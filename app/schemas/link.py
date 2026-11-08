from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, HttpUrl, Field, ConfigDict


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = Field(None, min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    expires_at: datetime | None = None


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    short_code: str
    original_url: str
    clicks: int
    created_at: datetime
    expires_at: datetime | None