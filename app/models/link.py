import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, BigInteger, String, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class Link(Base, TimestampMixin):
    __tablename__ = "links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    short_code: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    clicks: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_links_short_code", "short_code"),
    )