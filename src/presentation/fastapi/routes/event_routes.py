"""HTTP route handlers for event creation."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.application.create_event import create_event_uc
from src.application.ports.event_repository import EventRepository
from src.core.exceptions import DomainValidationError
from src.presentation.fastapi.dependencies import get_event_repository
from src.presentation.fastapi.models.event import Event, EventResponse

__all__ = ["event_router"]

event_router = APIRouter(prefix="/event", tags=["Events"])
logger = logging.getLogger(__name__)


@event_router.post("", response_model=EventResponse, status_code=201)
async def create_event_route(
    event: Event,
    repo: EventRepository = Depends(get_event_repository),  # noqa: B008
) -> EventResponse:
    """Create and persist an event.

    Args:
        event: Event request payload.
        repo: Event repository (injected).

    Returns:
        EventResponse with status "created".

    Raises:
        HTTPException 422: Domain validation failed.
        HTTPException 409: Database constraint violated.
        HTTPException 503: Database timeout.
        HTTPException 500: Unexpected error.
    """
    try:
        await create_event_uc(
            event_type=event.event_type,
            event_payload=event.event_payload,
            repo=repo,
        )
        logger.info(f"Event created: type={event.event_type}")
        return EventResponse(status="created")

    except DomainValidationError as exc:
        logger.warning(f"Domain validation error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except IntegrityError as exc:
        logger.warning(f"Constraint violation: {exc}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event already exists or violates database constraints",
        ) from exc

    except TimeoutError as exc:
        logger.error(f"Database timeout: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database operation timed out",
        ) from exc

    except Exception as exc:
        logger.error("Unexpected error in create_event_route", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc
