"""
Configuration validators

Functions for validating configuration values.
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


def validate_api_key(api_key: str, key_name: str = "API key") -> bool:
    """
    Validate API key format.

    Args:
        api_key: API key to validate
        key_name: Name of the key for error messages

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    if not api_key:
        raise ValueError(f"{key_name} is required")

    if len(api_key) < 10:
        raise ValueError(f"{key_name} is too short")

    # Check for common placeholder values
    if api_key.lower() in ["your_key_here", "placeholder", "example", "test"]:
        raise ValueError(f"{key_name} appears to be a placeholder")

    return True


def validate_url(url: str, key_name: str = "URL") -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate
        key_name: Name of the URL for error messages

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    if not url:
        raise ValueError(f"{key_name} is required")

    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError(f"{key_name} must be a valid URL with scheme and netloc")
        if result.scheme not in ["http", "https"]:
            raise ValueError(f"{key_name} must use http or https scheme")
    except Exception as e:
        raise ValueError(f"Invalid {key_name}: {e}")

    return True


def validate_timeout(timeout: int, key_name: str = "Timeout") -> bool:
    """
    Validate timeout value.

    Args:
        timeout: Timeout value in seconds
        key_name: Name of the timeout for error messages

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(timeout, int):
        raise ValueError(f"{key_name} must be an integer")

    if timeout <= 0:
        raise ValueError(f"{key_name} must be positive")

    if timeout > 3600:
        raise ValueError(f"{key_name} must be less than 1 hour (3600 seconds)")

    return True


def validate_log_level(level: str, key_name: str = "Log level") -> bool:
    """
    Validate log level.

    Args:
        level: Log level to validate
        key_name: Name of the level for error messages

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    if level.upper() not in valid_levels:
        raise ValueError(f"{key_name} must be one of: {', '.join(valid_levels)}")

    return True


def validate_output_format(format: str, key_name: str = "Output format") -> bool:
    """
    Validate output format.

    Args:
        format: Format to validate
        key_name: Name of the format for error messages

    Returns:
        True if valid

    Raises:
        ValueError: If validation fails
    """
    valid_formats = ["json", "yaml", "text", "table"]

    if format.lower() not in valid_formats:
        raise ValueError(f"{key_name} must be one of: {', '.join(valid_formats)}")

    return True


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate entire configuration.

    Args:
        config: Configuration dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Validate API key
    if "GENSPARK_API_KEY" in config:
        try:
            validate_api_key(config["GENSPARK_API_KEY"], "GENSPARK_API_KEY")
        except ValueError as e:
            errors.append(str(e))

    # Validate API URL
    if "GENSPARK_API_URL" in config:
        try:
            validate_url(config["GENSPARK_API_URL"], "GENSPARK_API_URL")
        except ValueError as e:
            errors.append(str(e))

    # Validate timeout
    if "TOOL_TIMEOUT" in config:
        try:
            validate_timeout(config["TOOL_TIMEOUT"], "TOOL_TIMEOUT")
        except ValueError as e:
            errors.append(str(e))

    # Validate log level
    if "LOG_LEVEL" in config:
        try:
            validate_log_level(config["LOG_LEVEL"], "LOG_LEVEL")
        except ValueError as e:
            errors.append(str(e))

    # Validate output format
    if "DEFAULT_OUTPUT_FORMAT" in config:
        try:
            validate_output_format(config["DEFAULT_OUTPUT_FORMAT"], "DEFAULT_OUTPUT_FORMAT")
        except ValueError as e:
            errors.append(str(e))

    return errors
