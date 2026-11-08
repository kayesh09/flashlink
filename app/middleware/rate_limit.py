from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# This is a stub for now. We will build the real Redis token bucket later.
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return await call_next(request)