"""FastAPI dependency injection for database access."""

from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.event_repository import EventRepository
from src.infrastructure.postgres.event_repository import PostgresEventRepository

__all__ = ["get_db_session"]


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    provider = request.app.state.db_provider
    session: AsyncSession = provider()
    try:
        yield session
    finally:
        await session.close()


def get_event_repository(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> EventRepository:
    """Return the event repository implementation.

    Args:
        session: Database session (auto-injected).

    Returns:
        An EventRepository instance.
    """
    return PostgresEventRepository(session)
