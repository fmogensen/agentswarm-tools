"""
Custom exceptions for AgentSwarm Tools Framework.
Provides structured error handling with analytics integration.
"""

from datetime import datetime
from typing import Any, Dict, Optional


class ToolError(Exception):
    """Base exception for all tool errors."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ):
        self.message = message
        self.tool_name = tool_name
        self.error_code = error_code or "TOOL_ERROR"
        self.details = details or {}
        self.retry_after = retry_after
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/analytics."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "tool_name": self.tool_name,
            "details": self.details,
            "retry_after": self.retry_after,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self) -> str:
        """Human-readable error message."""
        base = f"[{self.error_code}] {self.message}"
        if self.tool_name:
            base = f"{self.tool_name}: {base}"
        if self.retry_after:
            base += f" (retry after {self.retry_after}s)"
        return base


class ValidationError(ToolError):
    """Input validation failed."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        # Extract details from kwargs if present to merge with field
        existing_details = kwargs.pop("details", {})
        merged_details = {**existing_details}
        if field:
            merged_details["field"] = field

        super().__init__(
            message=message, error_code="VALIDATION_ERROR", details=merged_details, **kwargs
        )


class APIError(ToolError):
    """External API call failed."""

    def __init__(
        self,
        message: str,
        api_name: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code="API_ERROR",
            details={"api_name": api_name, "status_code": status_code},
            **kwargs,
        )


class RateLimitError(ToolError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60,
        limit: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT",
            retry_after=retry_after,
            details={"limit": limit} if limit else {},
            **kwargs,
        )


class AuthenticationError(ToolError):
    """Authentication/authorization failed."""

    def __init__(self, message: str, api_name: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            details={"api_name": api_name} if api_name else {},
            **kwargs,
        )


class TimeoutError(ToolError):
    """Operation timed out."""

    def __init__(
        self, message: str = "Operation timed out", timeout: Optional[int] = None, **kwargs
    ):
        super().__init__(
            message=message,
            error_code="TIMEOUT",
            details={"timeout": timeout} if timeout else {},
            **kwargs,
        )


class ResourceNotFoundError(ToolError):
    """Requested resource not found."""

    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details={"resource_type": resource_type} if resource_type else {},
            **kwargs,
        )


class ConfigurationError(ToolError):
    """Tool configuration error."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details={"config_key": config_key} if config_key else {},
            **kwargs,
        )


class QuotaExceededError(ToolError):
    """User quota exceeded."""

    def __init__(
        self,
        message: str = "Quota exceeded",
        quota_type: Optional[str] = None,
        limit: Optional[int] = None,
        used: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code="QUOTA_EXCEEDED",
            details={"quota_type": quota_type, "limit": limit, "used": used},
            **kwargs,
        )


class SecurityError(ToolError):
    """Security violation detected."""

    def __init__(self, message: str, violation_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="SECURITY_ERROR",
            details={"violation_type": violation_type} if violation_type else {},
            **kwargs,
        )


class MediaError(ToolError):
    """Media processing error."""

    def __init__(self, message: str, media_type: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            error_code="MEDIA_ERROR",
            details={"media_type": media_type} if media_type else {},
            **kwargs,
        )


# Utility functions for error handling


def handle_api_response(response: Any, api_name: str) -> None:
    """
    Handle API response and raise appropriate exceptions.

    Args:
        response: HTTP response object
        api_name: Name of the API for error context

    Raises:
        Various ToolError subclasses based on response status
    """
    if hasattr(response, "status_code"):
        if response.status_code == 401:
            raise AuthenticationError(f"Authentication failed for {api_name}", api_name=api_name)
        elif response.status_code == 403:
            raise AuthenticationError(f"Access forbidden for {api_name}", api_name=api_name)
        elif response.status_code == 404:
            raise ResourceNotFoundError(f"Resource not found on {api_name}", resource_type=api_name)
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                f"Rate limit exceeded for {api_name}", retry_after=retry_after, api_name=api_name
            )
        elif response.status_code >= 500:
            raise APIError(
                f"{api_name} server error", api_name=api_name, status_code=response.status_code
            )
        elif response.status_code >= 400:
            raise APIError(
                f"{api_name} request failed", api_name=api_name, status_code=response.status_code
            )
