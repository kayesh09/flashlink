# app/api/deps.py
from typing import Annotated
from fastapi import Depends, Header, HTTPException, status
from redis.asyncio import Redis
from redis.exceptions import AuthorizationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token
from app.db.redis import get_redis
from app.db.session import get_session
from app.repositories.user import UserRepository
from app.models.user import User

async def get_current_user(
        authorization:Annotated[str | None,Header()] = None,
        session:AsyncSession =Depends(get_session),

) ->User:
    if not authorization or not authorization .startswith("Bearer"):
        raise HTTPException(status.HTTP_402_UNAUTHORIZED,
                            "missing bearer token")
    token=authorization.removeprefix("Bearer ")
    try:
        email=decode_token(token)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "Invalide Token")
    user = await UserRepository(session).get_by_email(email)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,"user not found")
    return user