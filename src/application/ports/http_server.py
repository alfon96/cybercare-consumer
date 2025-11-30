"""Port definition for http server."""

from dataclasses import dataclass

__all__ = ["HttpServer"]


@dataclass
class HttpServer:
    """DTO for http server"""

    port: int
