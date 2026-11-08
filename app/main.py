from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.redis import close_redis, get_redis
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    # warm Redis pool
    await get_redis()
    yield
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,  # tiny perf win on the hot path
)

app.add_middleware(RequestIdMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(api_router)
app.mount("/metrics", make_asgi_app())  # Prometheus