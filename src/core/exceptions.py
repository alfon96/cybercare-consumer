"""Domain exceptions."""

__all__ = ["DomainValidationError"]


class DomainValidationError(ValueError):
    """Raised when domain business rules are violated.

    This indicates data that doesn't meet domain invariants.
    """
