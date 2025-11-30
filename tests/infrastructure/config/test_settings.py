"""Tests for configuration settings."""

from unittest.mock import patch

import pytest

from src.infrastructure.config.settings import load_params


def test_load_params_defaults() -> None:
    """Test load_params returns sqlite and default port."""
    with patch.dict("os.environ", {}, clear=True):
        uri, port = load_params()
        assert "sqlite+aiosqlite" in uri
        assert port == 8000


def test_load_params_postgres() -> None:
    """Test load_params validates postgres URI."""
    with patch.dict(
        "os.environ",
        {"DATABASE_URL": "postgresql+asyncpg://user:pass@localhost/db", "APP_PORT": "9000"},
        clear=True,
    ):
        uri, port = load_params()
        assert uri == "postgresql+asyncpg://user:pass@localhost/db"
        assert port == 9000


def test_load_params_invalid_postgres() -> None:
    """Test load_params rejects invalid postgres URI."""
    with (
        patch.dict("os.environ", {"DATABASE_URL": "postgresql://localhost/db"}, clear=True),
        pytest.raises(RuntimeError, match="postgresql\\+asyncpg"),
    ):
        load_params()
