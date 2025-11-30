# src/application/ports/db.py
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class DbProvider(Protocol):
    """Port: async lifecycle + session factory."""

    async def __aenter__(self) -> "DbProvider":
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: BaseException | None,
    ) -> None:
        ...

    def __call__(self) -> AsyncSession:
        ...
