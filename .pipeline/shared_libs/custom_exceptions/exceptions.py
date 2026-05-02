"""Custom exception classes for the Fiverr Job Automation Tool."""

from typing import Optional


class AutomationError(Exception):
    """Base exception for automation-related errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """Initialize the automation error.
        
        Args:
            message: Error message.
            details: Optional additional error details.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class APIError(AutomationError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 endpoint: Optional[str] = None, details: Optional[dict] = None):
        """Initialize the API error.
        
        Args:
            message: Error message.
            status_code: HTTP status code if applicable.
            endpoint: API endpoint that caused the error.
            details: Optional additional error details.
        """
        super().__init__(message, details)
        self.status_code = status_code
        self.endpoint = endpoint
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " - ".join(parts)


class AuthenticationError(APIError):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed",
                 endpoint: Optional[str] = None, details: Optional[dict] = None):
        """Initialize the authentication error.
        
        Args:
            message: Error message.
            endpoint: API endpoint that caused the error.
            details: Optional additional error details.
        """
        super().__init__(message, status_code=401, endpoint=endpoint, details=details)


class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, message: str = "API rate limit exceeded",
                 retry_after: Optional[int] = None,
                 endpoint: Optional[str] = None,
                 details: Optional[dict] = None):
        """Initialize the rate limit error.
        
        Args:
            message: Error message.
            retry_after: Seconds to wait before retrying.
            endpoint: API endpoint that caused the error.
            details: Optional additional error details.
        """
        super().__init__(message, status_code=429, endpoint=endpoint, details=details)
        self.retry_after = retry_after
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]
        if self.retry_after:
            parts.append(f"Retry after: {self.retry_after}s")
        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " - ".join(parts)


class ConfigurationError(AutomationError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 details: Optional[dict] = None):
        """Initialize the configuration error.
        
        Args:
            message: Error message.
            config_key: Configuration key that caused the error.
            details: Optional additional error details.
        """
        super().__init__(message, details)
        self.config_key = config_key
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]
        if self.config_key:
            parts.append(f"Config key: {self.config_key}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " - ".join(parts)


class ValidationError(AutomationError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[str] = None, details: Optional[dict] = None):
        """Initialize the validation error.
        
        Args:
            message: Error message.
            field: Field that failed validation.
            value: Value that failed validation.
            details: Optional additional error details.
        """
        super().__init__(message, details)
        self.field = field
        self.value = value
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]
        if self.field:
            parts.append(f"Field: {self.field}")
        if self.value:
            parts.append(f"Value: {self.value}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " - ".join(parts)
