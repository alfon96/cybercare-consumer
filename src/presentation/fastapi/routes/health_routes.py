"""HTTP route handlers for health checks."""

import logging

from fastapi import APIRouter

__all__ = ["health_router"]

health_router = APIRouter(prefix="/health", tags=["Health"])
logger = logging.getLogger(__name__)


@health_router.get("", include_in_schema=True, response_model=dict)
async def health_check() -> dict[str, str]:
    """Health check endpoint for container orchestration.

    Returns:
        Status dictionary.
    """
    return {"status": "healthy"}
