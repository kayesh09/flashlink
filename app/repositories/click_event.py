import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ClickEvent(Base):
    __tablename__ = "click_events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    link_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("links.id", ondelete="CASCADE"), nullable=False
    )
    ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(512))
    country: Mapped[str | None] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )

    __table_args__ = (
        Index("ix_clicks_link_created", "link_id", "created_at"),
    )