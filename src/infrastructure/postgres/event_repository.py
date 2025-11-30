"""PostgreSQL implementation of EventRepository port."""

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.event_repository import EventRepository
from src.core.event import DomainEvent
from src.infrastructure.postgres.models.event import Event as DBEvent

__all__ = ["PostgresEventRepository"]

logger = logging.getLogger(__name__)


class PostgresEventRepository(EventRepository):
    """Persist events to PostgreSQL using SQLAlchemy.

    Implements the EventRepository port for database persistence.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with database session.

        Args:
            session: Active AsyncSession instance.
        """
        self._session = session

    async def save(self, event: DomainEvent) -> DBEvent:
        """Persist an event to database.

        Args:
            event: Domain event to persist.

        Returns:
            Persisted DBEvent object with database-assigned values.

        Raises:
            IntegrityError: If database constraints are violated.
            Exception: For other database errors.
        """
        db_obj = DBEvent(
            type=event.event_type,
            message=event.event_payload,
            created_at=event.created_at,
        )
        self._session.add(db_obj)
        try:
            await self._session.commit()
            await self._session.refresh(db_obj)
            logger.debug(f"Event persisted: id={db_obj.id}, type={event.event_type}")
            return db_obj
        except IntegrityError as exc:
            logger.warning(f"Constraint violation: {exc}")
            await self._session.rollback()
            raise
        except Exception as exc:
            logger.error("Error persisting event", exc_info=exc)
            await self._session.rollback()
            raise
