"""Tests for create_event use case."""

import pytest

from src.application.create_event import create_event_uc
from src.application.ports.event_repository import EventRepository
from src.core.event import DomainEvent
from src.core.exceptions import DomainValidationError


class InMemoryEventRepository(EventRepository):
    """In-memory repository for testing use cases."""

    def __init__(self) -> None:
        self.saved_events: list[DomainEvent] = []

    async def save(self, event: DomainEvent) -> DomainEvent:
        """Save event to memory.

        Args:
            event: Domain event to save.

        Returns:
            The saved event.
        """
        self.saved_events.append(event)
        return event


class FailingEventRepository(EventRepository):
    """Repository that always fails for error testing."""

    async def save(self, event: DomainEvent) -> None:
        """Raise error on save attempt.

        Args:
            event: Domain event (ignored).

        Raises:
            RuntimeError: Always.
        """
        raise RuntimeError("Repository failure")


@pytest.mark.asyncio
async def test_create_event_uc_saves_event() -> None:
    """Use case should save valid events to repository."""
    repo = InMemoryEventRepository()

    await create_event_uc(
        event_type="user_joined",
        event_payload="Alice",
        repo=repo,
    )

    assert len(repo.saved_events) == 1
    saved = repo.saved_events[0]
    assert saved.event_type == "user_joined"
    assert saved.event_payload == "Alice"


@pytest.mark.asyncio
async def test_create_event_uc_propagates_domain_validation_error() -> None:
    """Use case should propagate DomainValidationError from event creation."""
    repo = InMemoryEventRepository()

    with pytest.raises(DomainValidationError):
        await create_event_uc(
            event_type="   ",  # Invalid
            event_payload="Alice",
            repo=repo,
        )

    # Nothing should have been saved
    assert repo.saved_events == []


@pytest.mark.asyncio
async def test_create_event_uc_propagates_repository_error() -> None:
    """Use case should propagate repository errors."""
    repo = FailingEventRepository()

    with pytest.raises(RuntimeError):
        await create_event_uc(
            event_type="message",
            event_payload="hello",
            repo=repo,
        )
