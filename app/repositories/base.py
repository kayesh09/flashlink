from typing import Generic,TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base
from sqlalchemy.util import await_only

ModelT = TypeVar("ModelT",bound=Base)

class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self,session:AsyncSession) -> None:
        self.session = session

    async def get_by_id(self,id_:object) -> ModelT | None:
        return await self.session.get(self.model,id_)
    async def add(self,instance:ModelT)-> ModelT:
        self.session.add(instance)
        await self.session.flush()
        return instance