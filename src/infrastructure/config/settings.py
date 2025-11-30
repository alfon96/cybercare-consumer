import logging
import os
from typing import Final

from dotenv import load_dotenv

__all__ = ["load_params"]

load_dotenv()
logger = logging.getLogger(__name__)


def load_params() -> tuple[str, int]:
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    in_memory_alternative_db = "sqlite+aiosqlite:///./events.db"
    _raw_database_uri = os.getenv("DATABASE_URL")

    if _raw_database_uri is None:
        _raw_database_uri = in_memory_alternative_db
    elif not _raw_database_uri.startswith("postgresql+asyncpg"):
        raise RuntimeError(
            "POSTGRES_URI environment variable must be set and start with 'postgresql+asyncpg'\n"
            "Example: postgresql+asyncpg://user:password@localhost/dbname"
        )

    database_uri: Final[str] = _raw_database_uri

    logger.info(f"Consumer configured: port={app_port}, db_uri={database_uri.split('@')[0]}...")

    return (database_uri, app_port)
