import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.link import Link
from app.repositories.link import LinkRepository


class LinkService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = LinkRepository(session)

    async def create_link(self, original_url: str, custom_alias: str | None = None) -> Link:
        short_code = custom_alias if custom_alias else secrets.token_urlsafe(settings.short_code_length)[
                                                       :settings.short_code_length]

        link = Link(
            short_code=short_code,
            original_url=str(original_url),
        )
        await self.repo.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        return link