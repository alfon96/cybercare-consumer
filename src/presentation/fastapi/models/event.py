"""Pydantic models for HTTP requests and responses."""

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["Event", "EventResponse", "MAX_EVENT_TYPE_LENGTH", "MAX_EVENT_PAYLOAD_LENGTH"]

MAX_EVENT_TYPE_LENGTH = 100
MAX_EVENT_PAYLOAD_LENGTH = 1000


class Event(BaseModel):
    """Request model for creating an event.

    Attributes:
        event_type: Type/category of the event (1-100 chars).
        event_payload: Event content (1-1000 chars).
    """

    event_type: str = Field(..., min_length=1, max_length=MAX_EVENT_TYPE_LENGTH)
    event_payload: str = Field(..., min_length=1, max_length=MAX_EVENT_PAYLOAD_LENGTH)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "event_type": "user_joined",
                "event_payload": "Alice",
            }
        },
    )


class EventResponse(BaseModel):
    """Response model for event creation.

    Attributes:
        status: Result status ("created" on success).
    """

    status: str = Field(..., pattern="^created$")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "created",
            }
        },
    )
