"""Application entrypoint."""

import logging

import src.infrastructure.logging  # noqa: F401
from src.application.ports.http_server import HttpServer
from src.infrastructure.config.settings import load_params
from src.infrastructure.postgres.db_provider import SqlAlchemyDbProvider
from src.presentation.fastapi.server import start_fast_api_server

__all__ = ["main"]

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the Event Consumer service."""
    logger.info("Starting Event Consumer service...")
    database_uri, app_port = load_params()
    start_fast_api_server(
        params=HttpServer(port=app_port),
        db_provider=SqlAlchemyDbProvider(database_uri=database_uri),
    )


if __name__ == "__main__":
    main()
