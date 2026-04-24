"""Custom exceptions."""


class AIProviderError(Exception):
    """Base exception for AI provider errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ConfigurationError(Exception):
    """Configuration error."""
    pass


class AuthenticationError(AIProviderError):
    """Authentication error."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class RateLimitError(AIProviderError):
    """Rate limit exceeded error."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


# Alias for consistency
AIServiceError = AIProviderError
