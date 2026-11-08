from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(p: str) -> str:
    return pwd.hash(p)


def verify_password(p: str, h: str) -> bool:
    return pwd.verify(p, h)


def create_access_token(sub: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_ttl_minutes
    )
    return jwt.encode(
        {"sub": sub, "exp": exp},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> str:
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    return payload["sub"]