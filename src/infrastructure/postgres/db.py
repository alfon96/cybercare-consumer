"""SQLAlchemy engine and session creation."""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.postgres.models.event import Base

__all__ = ["create_engine_and_session_maker", "init_db_tables"]


def create_engine_and_session_maker(
    database_uri: str,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Create SQLAlchemy engine and session maker.

    Args:
        database_uri: Async PostgreSQL connection URI.

    Returns:
        Tuple of (AsyncEngine, async_sessionmaker).
    """
    engine = create_async_engine(
        database_uri,
        echo=False,  # Don't log all SQL statements
        future=True,  #  Use SQLAlchemy 2.0 behavior now
        pool_size=20,  #  Keep 20 connections ready
        max_overflow=10,  #  Allow up to 10 extra connections temporarily
        pool_pre_ping=True,  #  Check connections are alive before using
    )
    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return engine, session_maker


async def init_db_tables(engine: AsyncEngine) -> None:
    """Create all tables defined in models.

    Args:
        engine: SQLAlchemy AsyncEngine to use.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
