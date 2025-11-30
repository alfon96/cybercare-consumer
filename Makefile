.PHONY: install run test lint typecheck format deps docs check coverage db-count db-events db-reset

# Help
help:
	@echo "Available commands:"
	@echo "  install     - Install deps (incl. dev)"
	@echo "  run         - Run the service"
	@echo "  test        - Run tests"
	@echo "  coverage    - Run coverage report"
	@echo "  lint        - Ruff lint"
	@echo "  typecheck   - Mypy type checking"
	@echo "  format      - Auto-format code"
	@echo "  deps        - Dependency checks"
	@echo "  docs        - Build docs"
	@echo "  check       - Format + lint + typecheck + coverage"
	@echo "  db-count    - Show event count"
	@echo "  db-events   - Show last events"
	@echo "  db-clear    - Clear all events"

# Setup & run
install:
	poetry install --with dev

run:
	poetry run python -m src.main

# Tests & quality
test:
	poetry run pytest -q

coverage:
	poetry run pytest --cov=src --cov-report=term-missing --cov-config=pyproject.toml

lint:
	poetry run ruff check src tests

typecheck:
	poetry run mypy src

format:
	poetry run ruff check --select I --fix src tests
	poetry run black src tests

deps:
	poetry run deptry .

check: format lint typecheck deps coverage

# DB helpers
db-count:
	sqlite3 events.db "SELECT COUNT(*) as total FROM events;" 2>/dev/null || echo "No database yet"

db-events:
	sqlite3 events.db "SELECT * FROM events ORDER BY created_at DESC LIMIT 10;" 2>/dev/null || echo "No database yet"

db-clear:
	sqlite3 events.db "DELETE FROM events;" >/dev/null 2>&1 && echo "Events cleared" || echo "No database yet"
