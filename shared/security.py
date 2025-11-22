"""
Security utilities for AgentSwarm Tools.
Handles API key management, input validation, and rate limiting.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import os
import re
import hashlib
from functools import wraps
from collections import defaultdict
import threading

from .errors import AuthenticationError, RateLimitError, SecurityError, ValidationError


# API Key Management


class APIKeyManager:
    """Secure API key management."""

    # Required API keys for different tool categories
    REQUIRED_KEYS = {
        "search": ["SERPAPI_KEY"],
        "media_generation": ["OPENAI_API_KEY"],
        "communication": ["GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET"],
        "storage": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
    }

    @staticmethod
    def get_key(key_name: str, required: bool = True) -> Optional[str]:
        """
        Get API key from environment.

        Args:
            key_name: Name of the environment variable
            required: Whether the key is required

        Returns:
            API key value or None

        Raises:
            AuthenticationError: If required key is missing
        """
        key = os.getenv(key_name)

        if required and not key:
            raise AuthenticationError(
                f"Missing required API key: {key_name}. "
                f"Please set the {key_name} environment variable."
            )

        return key

    @staticmethod
    def validate_keys(category: Optional[str] = None) -> List[str]:
        """
        Validate that required API keys are present.

        Args:
            category: Tool category to check (None for all)

        Returns:
            List of missing API keys
        """
        missing = []

        if category and category in APIKeyManager.REQUIRED_KEYS:
            keys_to_check = {category: APIKeyManager.REQUIRED_KEYS[category]}
        else:
            keys_to_check = APIKeyManager.REQUIRED_KEYS

        for cat, keys in keys_to_check.items():
            for key in keys:
                if not os.getenv(key):
                    missing.append(key)

        return missing

    @staticmethod
    def mask_key(key: str, visible_chars: int = 4) -> str:
        """
        Mask API key for logging.

        Args:
            key: API key to mask
            visible_chars: Number of characters to show at end

        Returns:
            Masked key (e.g., "sk-...abc123")
        """
        if not key or len(key) <= visible_chars:
            return "***"

        return f"{key[:3]}...{key[-visible_chars:]}"


# Input Validation


class InputValidator:
    """Input validation and sanitization."""

    # Patterns for common input types
    PATTERNS = {
        "email": re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$"),
        "url": re.compile(r"^https?://[\w\.-]+(?::\d+)?(?:/[\w\.-]*)*$"),
        "domain": re.compile(
            r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
        ),
        "phone": re.compile(r"^\+?1?\d{9,15}$"),
        "alpha": re.compile(r"^[a-zA-Z]+$"),
        "alphanumeric": re.compile(r"^[a-zA-Z0-9]+$"),
    }

    @staticmethod
    def validate_pattern(value: str, pattern_name: str) -> bool:
        """
        Validate value against a pattern.

        Args:
            value: Value to validate
            pattern_name: Name of pattern to use

        Returns:
            True if valid, False otherwise
        """
        if pattern_name not in InputValidator.PATTERNS:
            return False

        return bool(InputValidator.PATTERNS[pattern_name].match(value))

    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input.

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string

        Raises:
            ValidationError: If input is invalid
        """
        if not isinstance(value, str):
            raise ValidationError("Input must be a string")

        # Remove null bytes
        value = value.replace("\x00", "")

        # Trim whitespace
        value = value.strip()

        # Check length
        if max_length and len(value) > max_length:
            raise ValidationError(
                f"Input too long: {len(value)} > {max_length}", field="input_string"
            )

        return value

    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> str:
        """
        Validate and sanitize URL.

        Args:
            url: URL to validate
            allowed_schemes: Allowed URL schemes (default: http, https)

        Returns:
            Validated URL

        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError("URL cannot be empty", field="url")

        # Check scheme
        allowed_schemes = allowed_schemes or ["http", "https"]
        if not any(url.startswith(f"{scheme}://") for scheme in allowed_schemes):
            raise ValidationError(
                f"URL must start with one of: {', '.join(allowed_schemes)}", field="url"
            )

        # Basic URL validation
        if not InputValidator.validate_pattern(url, "url"):
            raise ValidationError("Invalid URL format", field="url")

        return url

    @staticmethod
    def validate_file_path(path: str, allowed_extensions: Optional[List[str]] = None) -> str:
        """
        Validate file path.

        Args:
            path: File path to validate
            allowed_extensions: Allowed file extensions

        Returns:
            Validated path

        Raises:
            SecurityError: If path contains suspicious patterns
            ValidationError: If extension not allowed
        """
        # Check for path traversal
        if ".." in path or path.startswith("/"):
            raise SecurityError("Path traversal detected", violation_type="path_traversal")

        # Check extension
        if allowed_extensions:
            ext = path.split(".")[-1].lower()
            if ext not in allowed_extensions:
                raise ValidationError(
                    f"File extension .{ext} not allowed. Allowed: {', '.join(allowed_extensions)}",
                    field="file_path",
                )

        return path


# Rate Limiting


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self):
        self._buckets: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"tokens": 0, "last_update": datetime.utcnow()}
        )
        self._lock = threading.Lock()

        # Default rate limits (requests per minute)
        self._limits = {
            "default": 60,
            "search": 100,
            "media_generation": 10,
            "media_analysis": 30,
            "api_call": 60,
        }

    def set_limit(self, key: str, limit: int) -> None:
        """Set rate limit for a key."""
        self._limits[key] = limit

    def check_rate_limit(self, key: str, limit_type: str = "default", cost: int = 1) -> None:
        """
        Check if request is within rate limit.

        Args:
            key: Unique identifier (user_id, tool_name, etc.)
            limit_type: Type of limit to apply
            cost: Token cost of this request

        Raises:
            RateLimitError: If rate limit exceeded
        """
        with self._lock:
            bucket = self._buckets[key]
            now = datetime.utcnow()

            # Refill tokens based on time passed
            time_passed = (now - bucket["last_update"]).total_seconds()
            limit = self._limits.get(limit_type, self._limits["default"])
            tokens_to_add = (time_passed / 60.0) * limit

            bucket["tokens"] = min(limit, bucket["tokens"] + tokens_to_add)
            bucket["last_update"] = now

            # Check if enough tokens
            if bucket["tokens"] < cost:
                retry_after = int((cost - bucket["tokens"]) / (limit / 60.0))
                raise RateLimitError(
                    f"Rate limit exceeded for {key}", retry_after=retry_after, limit=limit
                )

            # Consume tokens
            bucket["tokens"] -= cost

    def get_remaining(self, key: str, limit_type: str = "default") -> int:
        """Get remaining tokens for a key."""
        with self._lock:
            bucket = self._buckets.get(key)
            if not bucket:
                return self._limits.get(limit_type, self._limits["default"])

            now = datetime.utcnow()
            time_passed = (now - bucket["last_update"]).total_seconds()
            limit = self._limits.get(limit_type, self._limits["default"])
            tokens_to_add = (time_passed / 60.0) * limit

            current_tokens = min(limit, bucket["tokens"] + tokens_to_add)
            return int(current_tokens)


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    return _rate_limiter


# Decorators


def require_api_key(key_name: str):
    """Decorator to require an API key."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            APIKeyManager.get_key(key_name, required=True)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def rate_limit(limit_type: str = "default", cost: int = 1):
    """Decorator to apply rate limiting."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Use tool name as rate limit key
            key = getattr(self, "tool_name", self.__class__.__name__)
            limiter = get_rate_limiter()
            limiter.check_rate_limit(key, limit_type, cost)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


# Utility functions


def hash_user_id(user_id: str) -> str:
    """
    Hash user ID for privacy in logs.

    Args:
        user_id: User identifier

    Returns:
        Hashed user ID
    """
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]


def validate_api_keys(category: Optional[str] = None) -> List[str]:
    """
    Validate that required API keys are present.

    Args:
        category: Tool category to check (None for all)

    Returns:
        List of missing API keys
    """
    return APIKeyManager.validate_keys(category)


# Global rate limiter instance (for backward compatibility)
_rate_limiter_instance = None
