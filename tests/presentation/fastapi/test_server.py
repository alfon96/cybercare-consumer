from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.application.ports.db_provider import DbProvider
from src.presentation.fastapi.server import create_app


@pytest.fixture
def mock_db_provider() -> Any:
    """Mock DbProvider that implements async context manager interface."""
    mock_provider = AsyncMock(spec=DbProvider)
    mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
    mock_provider.__aexit__ = AsyncMock(return_value=None)
    mock_provider.__call__ = MagicMock(return_value=AsyncMock())
    return mock_provider


@pytest.mark.asyncio
async def test_app_lifespan_and_routes(mock_db_provider: Any) -> None:
    """Test app startup, shutdown, and route availability."""
    app = create_app(db_provider=mock_db_provider)

    # Verify app structure
    assert app.title == "Event Consumer API"
    assert app.version == "1.0.0"

    async with app.router.lifespan_context(app):
        # Verify context manager was entered
        mock_db_provider.__aenter__.assert_called_once()
        assert app.state.db_provider is mock_db_provider

        # Test routes
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Health check
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json() == {"status": "healthy"}

            # Root redirects to docs
            resp = await client.get("/", follow_redirects=True)
            assert resp.status_code == 200

    # Verify context manager was exited
    mock_db_provider.__aexit__.assert_called_once()
