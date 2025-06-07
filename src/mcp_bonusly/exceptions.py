"""
Custom exceptions for the Bonusly MCP server.
"""


class BonuslyError(Exception):
    """Base exception for Bonusly-related errors."""
    pass


class BonuslyAuthenticationError(BonuslyError):
    """Raised when authentication with Bonusly API fails."""
    pass


class BonuslyAPIError(BonuslyError):
    """Raised when Bonusly API returns an error response."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class BonuslyNotFoundError(BonuslyError):
    """Raised when a requested resource is not found."""
    pass


class BonuslyValidationError(BonuslyError):
    """Raised when request validation fails."""
    pass


class BonuslyRateLimitError(BonuslyError):
    """Raised when API rate limit is exceeded."""
    pass


class BonuslyConfigurationError(BonuslyError):
    """Raised when there's a configuration issue."""
    pass 