"""Custom exceptions for EC2 TUI."""


class EC2TUIError(Exception):
    """Base exception for EC2 TUI."""

    pass


class ConfigurationError(EC2TUIError):
    """Configuration error."""

    pass


class AWSError(EC2TUIError):
    """AWS API error."""

    pass


class InsufficientCapacityError(AWSError):
    """Insufficient instance capacity error."""

    pass


class ValidationError(EC2TUIError):
    """Input validation error."""

    pass
