"""SQLAlchemy ORM models for events."""

from sqlalchemy import Column, DateTime, Index, Integer, String, func
from sqlalchemy.orm import DeclarativeBase

__all__ = ["Base", "Event"]

MAX_EVENT_TYPE_LENGTH = 100
MAX_EVENT_PAYLOAD_LENGTH = 1000


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""


class Event(Base):
    """ORM model for events table.

    Attributes:
        id: Unique identifier (auto-increment).
        type: Event type/category (indexed for queries).
        message: Event payload content.
        created_at: Timestamp in UTC (indexed, server default).
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(MAX_EVENT_TYPE_LENGTH), nullable=False, index=True)
    message = Column(String(MAX_EVENT_PAYLOAD_LENGTH), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )

    __table_args__ = (Index("idx_type_created_at", "type", "created_at"),)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Event(id={self.id}, type={self.type}, created_at={self.created_at})"
