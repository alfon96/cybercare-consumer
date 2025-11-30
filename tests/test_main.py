import pytest

import src.main as main
from src.infrastructure.postgres.db_provider import SqlAlchemyDbProvider


def test_main_starts_server_with_db_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main should load params and start server with SqlAlchemyDbProvider."""
    called: dict[str, object] = {}

    def fake_load_params() -> tuple[str, int]:
        return ("sqlite+aiosqlite:///./events.db", 8000)

    def fake_start_fast_api_server(params, db_provider) -> None:
        called["params"] = params
        called["db_provider"] = db_provider

    monkeypatch.setattr("src.main.load_params", fake_load_params)
    monkeypatch.setattr("src.main.start_fast_api_server", fake_start_fast_api_server)

    main.main()

    assert called["params"].port == 8000
    assert isinstance(called["db_provider"], SqlAlchemyDbProvider)
