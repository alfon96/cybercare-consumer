"""Structured logging setup for the application."""

import logging

__all__ = ["configure_logs"]


def configure_logs() -> None:
    """Configure console logging.

    Sets up:
    - Root logger at WARNING level.
    - Framework loggers (SQLAlchemy, FastAPI, Uvicorn) at appropriate levels.
    - Application loggers (src) at DEBUG level.
    - Structured format with timestamp, level, module, and line number.
    """
    log_format = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    date_format = "%d/%m/%y %H:%M:%S"

    formatter = logging.Formatter(log_format, date_format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    root.addHandler(handler)

    # Suppress verbose framework loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Application loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("src").setLevel(logging.DEBUG)
