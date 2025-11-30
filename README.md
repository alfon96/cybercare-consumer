# Cybercare Consumer

[![CI](https://github.com/alfon96/cybercare-consumer/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/alfon96/cybercare-consumer/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python)
![Poetry](https://img.shields.io/badge/deps-poetry-60A5FA?logo=poetry)
![License](https://img.shields.io/badge/license-MIT-green)
![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20async%20SQLAlchemy-bc63bc)

FastAPI-based event consumer that receives, validates, and persists events to a database.

## Prerequisites

Choose one of the following:

- **Poetry**: Python 3.12+, [Poetry 1.8.4](https://python-poetry.org/docs/#installation)
- **Docker**: [Docker](https://docs.docker.com/get-docker/)

## Full Stack Setup

> **Recommended**: For a fast setup of the complete stack (Consumer + Propagator + PostgreSQL with Docker Compose), visit the [cybercare-stack](https://github.com/alfon96/cybercare-stack) repository.
>
> The sections below cover running this service individually.

## Getting Started

### Poetry

```bash
git clone https://github.com/alfon96/cybercare-consumer.git
cd cybercare-consumer

make install
make run
```

### Docker

```bash
git clone https://github.com/alfon96/cybercare-consumer.git
cd cybercare-consumer

docker build -t event-consumer .
docker run -p 8000:8000 \
  -e APP_PORT=8000 \
  event-consumer
```

> If you do have PostgreSQL, you can add:
>
> ```bash
> -e DATABASE_URL="postgresql+asyncpg://user:password@host:5432/db"
> ```

### DockerHub

```bash
docker run -p 8000:8000 \
  -e APP_PORT=8000 \
  alfo96/af-consumer:latest
```

> Optional PostgreSQL config (only if you already have a DB):
>
> ```bash
> -e DATABASE_URL="postgresql+asyncpg://user:password@host:5432/db"
> ```

## Configuration

This service needs the following environment variables:

| Variable       | Default | Optional | Description                                                                                                                                  |
| -------------- | ------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `APP_PORT`     | `8000`  | Yes      | Port the FastAPI application listens on                                                                                                      |
| `DATABASE_URL` | SQLite  | Yes      | If provided, must be an async PostgreSQL URL (`postgresql+asyncpg://user:password@host:port/db`). If omitted, the service uses async SQLite. |

## API

**Health Check**

```bash
curl http://localhost:8000/health
```

**Create Event**

```bash
curl -X POST http://localhost:8000/event \
  -H "Content-Type: application/json" \
  -d '{"event_type":"user_joined","event_payload":"Alice"}'
```

## Development

### Commands

```bash
make help         # Show all available commands
make install      # Install dependencies with dev tools
make run          # Start the service
make test         # Run pytest
make coverage     # Run tests with coverage report
make lint         # Check code with ruff
make typecheck    # Run mypy type checking
make format       # Auto-format code (isort, black, ruff)
make deps         # Check for dependency issues
make docs         # Generate documentation
make check        # Run all checks: format, lint, typecheck, deps, coverage
```

### Database Commands (Optional)

To query the SQLite database locally, install `sqlite3`:

```bash
# macOS
brew install sqlite3

# Linux (Ubuntu/Debian)
sudo apt install sqlite3

# Then use:
make db-count    # Count total events
make db-events   # Show last 10 events
make db-clear    # Clear all events
```

### CI/CD

Tests and code quality checks run automatically on every commit. Docker images are built and pushed to [alfo96/af-consumer](https://hub.docker.com/r/alfo96/af-consumer) on merge to main.

## Architecture

Clean architecture with separation of concerns: presentation → application → domain → infrastructure. Fully tested with pytest.
