"""
AgentSwarm Tools - Shared Utilities

This package contains shared utilities and base classes for all tools.
"""

from .base import BaseTool
from .errors import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    RateLimitError,
    ToolError,
    ValidationError,
)

# from .analytics import AnalyticsTracker, EventType
# from .security import APIKeyManager, InputValidator, RateLimiter

__version__ = "1.0.0"

__all__ = [
    "BaseTool",
    "ToolError",
    "ValidationError",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "ConfigurationError",
]
