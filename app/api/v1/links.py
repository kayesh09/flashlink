from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_session
from app.schemas.link import LinkCreate, LinkOut
from app.services.link import LinkService

router = APIRouter()

@router.post("/links", response_model=LinkOut, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: LinkCreate,
    session: AsyncSession = Depends(get_session),
):
    service = LinkService(session)
    link = await service.create_link(payload.original_url, payload.custom_alias)
    return link