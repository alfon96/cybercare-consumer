"""Domain model for events."""

from dataclasses import dataclass
from datetime import UTC, datetime

from src.core.exceptions import DomainValidationError

__all__ = ["DomainEvent", "MAX_EVENT_TYPE_LENGTH", "MAX_EVENT_PAYLOAD_LENGTH"]

MAX_EVENT_TYPE_LENGTH = 100
MAX_EVENT_PAYLOAD_LENGTH = 1000


@dataclass(frozen=True)
class DomainEvent:
    """Domain model representing an event.

    Immutable once created. Enforces business rules through factory method.

    Attributes:
        event_type: Event type/category.
        event_payload: Event content.
        created_at: Creation timestamp (always UTC).
    """

    event_type: str
    event_payload: str
    created_at: datetime

    @classmethod
    def create(cls, event_type: str, event_payload: str) -> "DomainEvent":
        """Create and validate a domain event.

        Enforces:
        - Non-empty, non-whitespace event_type (1-100 chars).
        - Non-empty, non-whitespace event_payload (1-1000 chars).
        - UTC timestamp set to current time.

        Args:
            event_type: Event type (will be stripped).
            event_payload: Event content (will be stripped).

        Returns:
            Valid DomainEvent instance.

        Raises:
            DomainValidationError: If validation fails.
        """
        event_type = event_type.strip()
        event_payload = event_payload.strip()

        if not event_type:
            raise DomainValidationError("Event type cannot be empty")

        if not event_payload:
            raise DomainValidationError("Event payload cannot be empty")

        if len(event_type) > MAX_EVENT_TYPE_LENGTH:
            raise DomainValidationError(
                f"Event type exceeds {MAX_EVENT_TYPE_LENGTH} chars (got {len(event_type)})"
            )

        if len(event_payload) > MAX_EVENT_PAYLOAD_LENGTH:
            raise DomainValidationError(
                f"Event payload exceeds {MAX_EVENT_PAYLOAD_LENGTH} chars (got {len(event_payload)})"
            )

        return cls(
            event_type=event_type,
            event_payload=event_payload,
            created_at=datetime.now(UTC),
        )
