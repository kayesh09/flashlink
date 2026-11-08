from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.link import Link
from app.repositories.base import BaseRepository


class LinkRepository(BaseRepository[Link]):
    model = Link

    async def get_by_code(self, code: str) -> Link | None:
        stmt = select(Link).where(Link.short_code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()  # <--- FIXED THIS LINE

    async def increment_clicks(self, link_id) -> None:
        await self.session.execute(
            update(Link).where(Link.id == link_id).values(
                clicks=Link.clicks + 1
            )
        )