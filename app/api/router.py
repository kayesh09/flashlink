from fastapi import APIRouter
from app.api.v1 import redirect, links

api_router = APIRouter()
api_router.include_router(redirect.router, tags=["Redirect"])
api_router.include_router(links.router, prefix="/api/v1", tags=["Links"])