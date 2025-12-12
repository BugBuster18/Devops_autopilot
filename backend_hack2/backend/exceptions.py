"""Custom exception classes for better error categorization."""

from typing import Optional, Dict, Any


class AutopilotBaseException(Exception):
    """Base exception for all Autopilot-related errors."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(AutopilotBaseException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(AutopilotBaseException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Authorization failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class ValidationError(AutopilotBaseException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class ExternalAPIError(AutopilotBaseException):
    """Raised when external API calls fail."""

    def __init__(self, message: str = "External API call failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=502, details=details)


class DatabaseError(AutopilotBaseException):
    """Raised when database operations fail."""

    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class VideoGenerationError(AutopilotBaseException):
    """Raised when video generation fails."""

    def __init__(self, message: str = "Video generation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class ReportGenerationError(AutopilotBaseException):
    """Raised when report generation fails."""

    def __init__(self, message: str = "Report generation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class ResourceNotFoundError(AutopilotBaseException):
    """Raised when requested resource is not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class ConfigurationError(AutopilotBaseException):
    """Raised when configuration is missing or invalid."""

    def __init__(self, message: str = "Configuration error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)
