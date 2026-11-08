from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)
from app.core.config import settings

engine = create_async_engine(
    settings.async_db_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_max_timeout,  # <--- FIXED THIS LINE
    pool_pre_ping=True,
    echo=settings.debug,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session