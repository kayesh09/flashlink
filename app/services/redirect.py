import orjson
from datetime import datetime, timezone
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError, ExpiredLinkError
from app.repositories.link import LinkRepository

CACHE_KEY = "link:{code}"
NEG_KEY = "neg:{code}"
CLICK_STREAM = "stream:clicks"


class RedirectService:
    def __init__(self, redis: Redis, session: AsyncSession) -> None:
        self.redis = redis
        self.repo = LinkRepository(session)

    async def resolve(self, code: str, ip: str | None,
                      user_agent: str | None) -> str:
        url = await self._lookup(code)
        # Fire-and-forget: push click event to Redis Stream
        await self._enqueue_click(code, ip, user_agent)
        return url

    async def _lookup(self, code: str) -> str:
        try:
            cached = await self.redis.get(CACHE_KEY.format(code=code))
            if cached:
                return cached
            neg = await self.redis.get(NEG_KEY.format(code=code))
            if neg:
                raise NotFoundError(code)
        except Exception:
            # Redis unavailable: don't kill the redirect, fall through.
            pass

        link = await self.repo.get_by_code(code)
        if link is None:
            await self._safe_set(
                NEG_KEY.format(code=code), "1",
                ex=settings.negative_cache_ttl_seconds,
            )
            raise NotFoundError(code)

        if link.expires_at and link.expires_at < datetime.now(timezone.utc):
            raise ExpiredLinkError(code)

        ttl = settings.redirect_cache_ttl_seconds
        if link.expires_at:
            ttl = max(10, int(
                (link.expires_at - datetime.now(timezone.utc)).total_seconds()
            ))
        await self._safe_set(
            CACHE_KEY.format(code=code), link.original_url, ex=ttl,
        )
        return link.original_url

    async def _enqueue_click(
        self, code: str, ip: str | None, user_agent: str | None
    ) -> None:
        payload = orjson.dumps({
            "code": code,
            "ip": ip,
            "ua": user_agent,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        try:
            await self.redis.xadd(CLICK_STREAM, {"d": payload},
                                  maxlen=100_000, approximate=True)
        except Exception:
            # Drop rather than block — analytics is best-effort on the hot path
            pass

    async def _safe_set(self, key: str, val: str, ex: int) -> None:
        try:
            await self.redis.set(key, val, ex=ex)
        except Exception:
            pass