from fastapi import APIRouter, Depends, Request, Response
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_redis, get_session
from app.core.exceptions import NotFoundError, ExpiredLinkError
from app.services.redirect import RedirectService

router = APIRouter()

@router.get("/{code}", status_code=301)
async def redirect(
    code: str,
    request: Request,
    redis: Redis = Depends(get_redis),
    session: AsyncSession = Depends(get_session),
):
    svc = RedirectService(redis, session)
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    try:
        target = await svc.resolve(code, ip, ua)
    except NotFoundError:
        return Response(status_code=404, content="Not found")
    except ExpiredLinkError:
        return Response(status_code=410, content="Link expired")

    # 301 so browsers and CDNs cache it client-side too.
    return Response(
        status_code=301,
        headers={"Location": target, "Cache-Control": "public, max-age=300"},
    )