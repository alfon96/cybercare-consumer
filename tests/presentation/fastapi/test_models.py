"""Tests for Pydantic request/response models."""

import pytest
from pydantic import ValidationError

from src.presentation.fastapi.models.event import (
    MAX_EVENT_PAYLOAD_LENGTH,
    MAX_EVENT_TYPE_LENGTH,
    Event,
    EventResponse,
)


def test_event_model_valid() -> None:
    """Event model should accept valid data."""
    event = Event(event_type="message", event_payload="hello")
    assert event.event_type == "message"
    assert event.event_payload == "hello"


def test_event_model_rejects_extra_fields() -> None:
    """Event model should reject extra fields (forbid=True)."""
    with pytest.raises(ValidationError):
        Event(
            event_type="message",
            event_payload="hello",
            extra_field="not allowed",
        )


def test_event_model_rejects_empty_type() -> None:
    """Event model should reject empty event_type."""
    with pytest.raises(ValidationError):
        Event(event_type="", event_payload="hello")


def test_event_model_rejects_oversized_type() -> None:
    """Event model should reject event_type > 100 chars."""
    with pytest.raises(ValidationError):
        Event(event_type="x" * (MAX_EVENT_TYPE_LENGTH + 1), event_payload="hello")


def test_event_model_rejects_oversized_payload() -> None:
    """Event model should reject event_payload > 1000 chars."""
    with pytest.raises(ValidationError):
        Event(event_type="message", event_payload="x" * (MAX_EVENT_PAYLOAD_LENGTH + 1))


def test_event_response_model() -> None:
    """EventResponse model should accept valid status."""
    resp = EventResponse(status="created")
    assert resp.status == "created"
