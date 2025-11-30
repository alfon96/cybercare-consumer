"""Use case: create and persist a domain event."""

import logging

from src.application.ports.event_repository import EventRepository
from src.core.event import DomainEvent

__all__ = ["create_event_uc"]

logger = logging.getLogger("usecase.create_event")


async def create_event_uc(
    event_type: str,
    event_payload: str,
    repo: EventRepository,
) -> None:
    """Create and persist an event.

    Orchestrates domain logic (validation) with infrastructure (persistence).

    Args:
        event_type: Event type.
        event_payload: Event content.
        repo: Event repository for persistence.

    Raises:
        DomainValidationError: If event is invalid.
        Exception: If persistence fails.
    """
    logger.debug(f"Creating domain event: type={event_type}")
    event = DomainEvent.create(event_type=event_type, event_payload=event_payload)
    await repo.save(event)
    logger.debug(f"Event persisted: id={id(event)}, type={event.event_type}")
