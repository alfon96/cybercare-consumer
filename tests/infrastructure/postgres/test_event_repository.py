"""Tests for PostgreSQL event repository."""

import pytest

from src.core.event import DomainEvent
from src.infrastructure.postgres.event_repository import PostgresEventRepository


class FakeSession:
    """Fake database session for testing repository methods.

    Simulates SQLAlchemy AsyncSession behavior without database.
    """

    def __init__(self, fail_on_commit: bool = False, fail_on_refresh: bool = False) -> None:
        """Initialize fake session with optional failure modes.

        Args:
            fail_on_commit: If True, raise error on commit().
            fail_on_refresh: If True, raise error on refresh().
        """
        self.added = []
        self.committed = False
        self.refreshed = []
        self.rolled_back = False
        self._fail_on_commit = fail_on_commit
        self._fail_on_refresh = fail_on_refresh

    def add(self, obj: object) -> None:
        """Add object to session.

        Args:
            obj: Object to add.
        """
        self.added.append(obj)

    async def commit(self) -> None:
        """Commit transaction (may fail based on initialization).

        Raises:
            RuntimeError: If fail_on_commit is True.
        """
        if self._fail_on_commit:
            raise RuntimeError("commit failed")
        self.committed = True

    async def refresh(self, obj: object) -> None:
        """Refresh object (may fail based on initialization).

        Args:
            obj: Object to refresh.

        Raises:
            RuntimeError: If fail_on_refresh is True.
        """
        if self._fail_on_refresh:
            raise RuntimeError("refresh failed")
        self.refreshed.append(obj)

    async def rollback(self) -> None:
        """Rollback transaction."""
        self.rolled_back = True


@pytest.mark.asyncio
async def test_postgres_event_repository_save_success() -> None:
    """Repository should commit event and refresh the object."""
    session = FakeSession()
    repo = PostgresEventRepository(session)

    event = DomainEvent.create(event_type="msg", event_payload="hi")
    db_obj = await repo.save(event)

    # Verify session interactions
    assert len(session.added) == 1
    assert session.committed is True
    assert db_obj in session.refreshed


@pytest.mark.asyncio
async def test_postgres_event_repository_rollback_on_commit_failure() -> None:
    """Repository should rollback on commit error."""
    session = FakeSession(fail_on_commit=True)
    repo = PostgresEventRepository(session)

    event = DomainEvent.create(event_type="msg", event_payload="hi")

    with pytest.raises(RuntimeError):
        await repo.save(event)

    assert session.rolled_back is True


@pytest.mark.asyncio
async def test_postgres_event_repository_rollback_on_refresh_failure() -> None:
    """Repository should rollback on refresh error."""
    session = FakeSession(fail_on_refresh=True)
    repo = PostgresEventRepository(session)

    event = DomainEvent.create(event_type="msg", event_payload="hi")

    with pytest.raises(RuntimeError):
        await repo.save(event)

    assert session.rolled_back is True
