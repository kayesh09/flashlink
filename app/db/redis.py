from redis.asyncio import Redis, from_url
from app.core.config import settings

_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:  # <--- FIXED THIS LINE (is instead of in)
        _redis = from_url(
            str(settings.redis_dsn),
            encoding="utf-8",
            decode_responses=True,
            max_connections=128,
            socket_timeout=1.0,
            socket_connect_timeout=1.0,
            health_check_interval=30,
        )
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None