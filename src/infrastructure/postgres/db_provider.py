from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.postgres.models.event import Base


class SqlAlchemyDbProvider:
    def __init__(self, database_uri: str) -> None:
        self._engine: AsyncEngine = create_async_engine(database_uri, echo=False, future=True)
        self._session_maker = async_sessionmaker(self._engine, expire_on_commit=False)

    async def __aenter__(self) -> "SqlAlchemyDbProvider":
        # init DB (works for Postgres or SQLite depending on URI)
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: BaseException | None,
    ) -> None:
        await self._engine.dispose()

    def __call__(self) -> AsyncSession:
        return self._session_maker()
