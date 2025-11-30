"""Tests for infrastructure layer: database and ORM."""

from datetime import UTC
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.event import DomainEvent
from src.core.exceptions import DomainValidationError
from src.infrastructure.postgres.db_provider import SqlAlchemyDbProvider
from src.infrastructure.postgres.event_repository import PostgresEventRepository


@pytest.mark.asyncio
async def test_db_provider_lifecycle() -> None:
    """Test SqlAlchemyDbProvider startup, session creation, and shutdown."""
    with (
        patch("src.infrastructure.postgres.db_provider.create_async_engine") as mock_create,
        patch("src.infrastructure.postgres.db_provider.async_sessionmaker") as mock_sm,
    ):
        mock_conn = MagicMock()
        mock_begin = MagicMock()
        mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_begin.__aexit__ = AsyncMock(return_value=None)

        mock_engine = MagicMock()
        mock_engine.begin.return_value = mock_begin
        mock_engine.dispose = AsyncMock()
        mock_conn.run_sync = AsyncMock()
        mock_create.return_value = mock_engine
        mock_sm.return_value = MagicMock(return_value=MagicMock())

        provider = SqlAlchemyDbProvider("sqlite+aiosqlite:///./test.db")

        result = await provider.__aenter__()
        assert result is provider
        assert mock_engine.begin.called

        session = provider()
        assert session is not None

        await provider.__aexit__(None, None, None)
        mock_engine.dispose.assert_called_once()


def test_create_engine_and_session_maker() -> None:
    """Test engine and session maker creation."""
    with patch("src.infrastructure.postgres.db.create_async_engine") as mock_create:
        from src.infrastructure.postgres.db import create_engine_and_session_maker

        mock_engine = MagicMock()
        mock_create.return_value = mock_engine

        engine, session_maker = create_engine_and_session_maker(
            "postgresql+asyncpg://localhost/test"
        )

        assert engine is mock_engine
        assert session_maker is not None


@pytest.mark.asyncio
async def test_init_db_tables() -> None:
    """Test database table initialization."""
    from src.infrastructure.postgres.db import init_db_tables

    mock_conn = MagicMock()
    mock_begin = MagicMock()
    mock_begin.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_begin.__aexit__ = AsyncMock(return_value=None)

    mock_engine = MagicMock()
    mock_engine.begin.return_value = mock_begin
    mock_conn.run_sync = AsyncMock()

    await init_db_tables(mock_engine)

    assert mock_conn.run_sync.called


class FakeSession:
    def __init__(self):
        self.added = []
        self.committed = False

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        pass

    async def rollback(self):
        pass


@pytest.mark.asyncio
async def test_postgres_event_repository() -> None:
    """Test event repository persists and validates."""
    session = FakeSession()
    repo = PostgresEventRepository(session)
    event = DomainEvent.create(event_type="msg", event_payload="hi")

    await repo.save(event)

    assert len(session.added) == 1 and session.committed


def test_domain_event() -> None:
    """Test DomainEvent validation and properties."""
    # Valid
    event = DomainEvent.create(event_type="msg", event_payload="hi")
    assert event.event_type == "msg" and event.created_at.tzinfo == UTC

    # Strip whitespace
    event = DomainEvent.create(event_type="  x  ", event_payload="  y  ")
    assert event.event_type == "x" and event.event_payload == "y"

    # Validation errors
    with pytest.raises(DomainValidationError):
        DomainEvent.create(event_type="", event_payload="x")

    with pytest.raises(DomainValidationError):
        DomainEvent.create(event_type="msg", event_payload="")

    with pytest.raises(DomainValidationError):
        DomainEvent.create(event_type="x" * 101, event_payload="p")
