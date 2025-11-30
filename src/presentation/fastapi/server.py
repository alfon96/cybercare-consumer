"""FastAPI application factory and server startup."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.application.ports.db_provider import DbProvider
from src.application.ports.http_server import HttpServer
from src.presentation.fastapi.routes.event_routes import event_router
from src.presentation.fastapi.routes.health_routes import health_router

__all__ = ["create_app", "start_fast_api_server"]

logger = logging.getLogger(__name__)


def create_app(
    db_provider: DbProvider,
) -> FastAPI:
    """Create and configure FastAPI application.

    Wires infrastructure (database, routes, error handlers).

    Returns:
        Configured FastAPI application instance.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Manage application lifecycle (startup/shutdown).

        Startup: Initialize database engine and session maker.
        Shutdown: Dispose of connections.
        """
        logger.info("Starting up application...")
        async with db_provider:
            app.state.db_provider = db_provider
            yield
        logger.info("Shutting down application...")

    app = FastAPI(
        title="Event Consumer API",
        description="Consumes and persists events from the propagator service",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(event_router)
    app.include_router(health_router)

    @app.get("/", include_in_schema=False)
    async def _() -> RedirectResponse:
        """Redirect root to OpenAPI docs."""
        return RedirectResponse(url="/docs")

    return app


def start_fast_api_server(params: HttpServer, db_provider: DbProvider) -> None:
    """Start the FastAPI server.

    Args:
        port: Port number to bind to.
    """
    logger.info(f"Starting FastAPI server on port {params.port}...")
    app = create_app(db_provider=db_provider)
    uvicorn.run(app, host="0.0.0.0", port=params.port, access_log=True)
