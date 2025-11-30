"""Fixed dependency tests - aligned with actual implementation."""

from contextlib import suppress
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.event_repository import PostgresEventRepository
from src.presentation.fastapi.dependencies import get_db_session, get_event_repository


@pytest.mark.asyncio
async def test_get_db_session_dependency() -> None:
    """Test get_db_session yields database session and closes it."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_provider = MagicMock(return_value=mock_session)
    mock_request = MagicMock()
    mock_request.app.state.db_provider = mock_provider

    # Get yielded session
    gen = get_db_session(mock_request)
    session = await anext(gen)

    assert session is mock_session
    mock_session.close.assert_not_called()

    # Trigger finally block to verify cleanup
    with suppress(StopAsyncIteration):
        await gen.__anext__()

    mock_session.close.assert_called_once()


def test_get_event_repository_dependency() -> None:
    """Test get_event_repository returns PostgresEventRepository instance."""
    mock_session = MagicMock(spec=AsyncSession)

    repo = get_event_repository(session=mock_session)

    assert isinstance(repo, PostgresEventRepository)
    assert repo._session is mock_session
