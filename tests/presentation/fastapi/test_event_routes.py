"""Tests for event creation HTTP endpoints."""

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError

from src.application.ports.event_repository import EventRepository
from src.core.event import DomainEvent
from src.presentation.fastapi.dependencies import get_event_repository
from src.presentation.fastapi.models.event import (
    MAX_EVENT_PAYLOAD_LENGTH,
    MAX_EVENT_TYPE_LENGTH,
)
from src.presentation.fastapi.routes.event_routes import event_router
from src.presentation.fastapi.routes.health_routes import health_router


class DummyRepo(EventRepository):
    """Repository that stores events in memory."""

    def __init__(self) -> None:
        self.saved: list[DomainEvent] = []

    async def save(self, event: DomainEvent) -> DomainEvent:
        """Save event to memory."""
        self.saved.append(event)
        return event


class FailingRepo(EventRepository):
    """Repository that always raises RuntimeError."""

    async def save(self, event: DomainEvent) -> None:
        """Raise error on save attempt."""
        raise RuntimeError("DB down")


class IntegrityConstraintRepo(EventRepository):
    """Repository that simulates database constraint violation."""

    async def save(self, event: DomainEvent) -> None:
        """Raise IntegrityError to simulate constraint violation."""
        raise IntegrityError(
            statement="INSERT INTO events...",
            params={},
            orig=Exception("Duplicate key"),
        )


def create_test_app(repo: EventRepository) -> httpx.AsyncClient:
    """Create FastAPI test app with injected repository.

    Args:
        repo: Repository implementation to inject.

    Returns:
        AsyncClient configured for testing.
    """
    app = FastAPI()
    app.include_router(event_router)

    # Override dependency injection
    app.dependency_overrides[get_event_repository] = lambda: repo

    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.anyio
async def test_create_event_route_success() -> None:
    """POST /event should create event and return 201."""
    repo = DummyRepo()
    async with create_test_app(repo) as client:
        payload = {
            "event_type": "message",
            "event_payload": "hello",
        }

        resp = await client.post("/event", json=payload)

    assert resp.status_code == 201
    assert resp.json() == {"status": "created"}
    assert len(repo.saved) == 1
    saved = repo.saved[0]
    assert saved.event_type == "message"
    assert saved.event_payload == "hello"


@pytest.mark.anyio
async def test_create_event_route_validation_error_empty_type() -> None:
    """POST /event should reject empty event_type with 422."""
    repo = DummyRepo()
    async with create_test_app(repo) as client:
        payload = {
            "event_type": "   ",
            "event_payload": "hello",
        }

        resp = await client.post("/event", json=payload)

    assert resp.status_code == 422
    body = resp.json()
    assert "Event type cannot be empty" in body["detail"]


@pytest.mark.anyio
async def test_create_event_route_validation_error_empty_payload() -> None:
    """POST /event should reject empty event_payload with 422."""
    repo = DummyRepo()
    async with create_test_app(repo) as client:
        payload = {
            "event_type": "message",
            "event_payload": "   ",
        }

        resp = await client.post("/event", json=payload)

    assert resp.status_code == 422
    body = resp.json()
    assert "Event payload cannot be empty" in body["detail"]


@pytest.mark.anyio
async def test_create_event_route_pydantic_validation_error() -> None:
    """POST /event should reject missing fields with 422."""
    repo = DummyRepo()
    async with create_test_app(repo) as client:
        payload = {
            "event_type": "message",
            # Missing event_payload
        }

        resp = await client.post("/event", json=payload)

    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_event_route_extra_fields_rejected() -> None:
    """POST /event should reject extra fields with 422."""
    repo = DummyRepo()
    async with create_test_app(repo) as client:
        payload = {
            "event_type": "message",
            "event_payload": "hello",
            "extra_field": "not allowed",
        }

        resp = await client.post("/event", json=payload)

    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_event_route_integrity_error() -> None:
    """POST /event should return 409 on constraint violation."""
    repo = IntegrityConstraintRepo()
    async with create_test_app(repo) as client:
        payload = {
            "event_type": "message",
            "event_payload": "hello",
        }

        resp = await client.post("/event", json=payload)

    assert resp.status_code == 409
    body = resp.json()
    assert "constraint" in body["detail"].lower()


@pytest.mark.anyio
async def test_create_event_route_internal_error() -> None:
    """POST /event should return 500 on unexpected errors."""
    repo = FailingRepo()
    async with create_test_app(repo) as client:
        payload = {
            "event_type": "message",
            "event_payload": "hello",
        }

        resp = await client.post("/event", json=payload)

    assert resp.status_code == 500
    assert resp.json() == {"detail": "Internal server error"}


@pytest.mark.anyio
async def test_create_event_route_oversized_type() -> None:
    """POST /event should reject event_type exceeding 100 chars."""
    repo = DummyRepo()
    async with create_test_app(repo) as client:
        payload = {
            "event_type": "x" * (MAX_EVENT_TYPE_LENGTH + 1),
            "event_payload": "hello",
        }

        resp = await client.post("/event", json=payload)

    assert resp.status_code == 422


@pytest.mark.anyio
async def test_create_event_route_oversized_payload() -> None:
    """POST /event should reject event_payload exceeding 1000 chars."""
    repo = DummyRepo()
    async with create_test_app(repo) as client:
        payload = {
            "event_type": "message",
            "event_payload": "x" * (MAX_EVENT_PAYLOAD_LENGTH + 1),
        }

        resp = await client.post("/event", json=payload)

    assert resp.status_code == 422


@pytest.mark.anyio
async def test_health_check_endpoint() -> None:
    """GET /health should return 200 with healthy status."""
    app = FastAPI()
    app.include_router(health_router)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}
