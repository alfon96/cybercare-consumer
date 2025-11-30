"""Port definition for event persistence."""

from typing import Protocol

from src.core.event import DomainEvent

__all__ = ["EventRepository"]


class EventRepository(Protocol):
    """Interface for event persistence.

    Any implementation (PostgreSQL, MongoDB, file system) must conform
    to this protocol.
    """

    async def save(self, event: DomainEvent) -> object:
        """Persist a domain event.

        Args:
            event: The domain event to persist.

        Returns:
            The persisted object.

        Raises:
            Exception: If persistence fails.
        """
        ...
