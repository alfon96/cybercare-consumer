"""Tests for DomainEvent model and validation."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta

import pytest

from src.core.event import MAX_EVENT_PAYLOAD_LENGTH, MAX_EVENT_TYPE_LENGTH, DomainEvent
from src.core.exceptions import DomainValidationError


def test_domain_event_create_sets_fields_correctly() -> None:
    """DomainEvent.create should set all fields with UTC timestamp."""
    event_type = "user_joined"
    payload = "Alice"

    event = DomainEvent.create(event_type=event_type, event_payload=payload)

    assert event.event_type == event_type
    assert event.event_payload == payload
    assert isinstance(event.created_at, datetime)
    assert event.created_at.tzinfo == UTC

    # Timestamp should be recent
    now = datetime.now(UTC)
    assert now - event.created_at < timedelta(seconds=2)


def test_domain_event_create_rejects_empty_type() -> None:
    """DomainEvent.create should reject empty event_type."""
    with pytest.raises(DomainValidationError) as exc:
        DomainEvent.create(event_type="", event_payload="x")
    assert "Event type cannot be empty" in str(exc.value)


def test_domain_event_create_rejects_whitespace_type() -> None:
    """DomainEvent.create should reject whitespace-only event_type."""
    with pytest.raises(DomainValidationError):
        DomainEvent.create(event_type="   ", event_payload="x")


def test_domain_event_create_rejects_empty_payload() -> None:
    """DomainEvent.create should reject empty event_payload."""
    with pytest.raises(DomainValidationError) as exc:
        DomainEvent.create(event_type="message", event_payload="")
    assert "Event payload cannot be empty" in str(exc.value)


def test_domain_event_create_rejects_whitespace_payload() -> None:
    """DomainEvent.create should reject whitespace-only event_payload."""
    with pytest.raises(DomainValidationError) as exc:
        DomainEvent.create(event_type="message", event_payload="   ")
    assert "Event payload cannot be empty" in str(exc.value)


def test_domain_event_create_rejects_oversized_type() -> None:
    """DomainEvent.create should reject event_type exceeding max length."""
    long_type = "x" * (MAX_EVENT_TYPE_LENGTH + 1)
    with pytest.raises(DomainValidationError) as exc:
        DomainEvent.create(event_type=long_type, event_payload="payload")
    assert "exceeds" in str(exc.value).lower()


def test_domain_event_create_rejects_oversized_payload() -> None:
    """DomainEvent.create should reject event_payload exceeding max length."""
    long_payload = "x" * (MAX_EVENT_PAYLOAD_LENGTH + 1)
    with pytest.raises(DomainValidationError) as exc:
        DomainEvent.create(event_type="message", event_payload=long_payload)
    assert "exceeds" in str(exc.value).lower()


def test_domain_event_create_strips_whitespace() -> None:
    """DomainEvent.create should strip leading/trailing whitespace."""
    event = DomainEvent.create(event_type="  user_joined  ", event_payload="  Alice  ")
    assert event.event_type == "user_joined"
    assert event.event_payload == "Alice"


def test_domain_event_is_frozen() -> None:
    """DomainEvent should be immutable after creation."""
    event = DomainEvent.create(event_type="message", event_payload="hello")
    with pytest.raises(FrozenInstanceError):
        event.event_type = "modified"
