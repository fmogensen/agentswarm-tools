"""
Comprehensive tests for shared.errors module.
Target coverage: 100%
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from shared.errors import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    MediaError,
    QuotaExceededError,
    RateLimitError,
    ResourceNotFoundError,
    SecurityError,
    TimeoutError,
    ToolError,
    ValidationError,
    handle_api_response,
)

# Test ToolError Base Class


def test_tool_error_basic():
    """Test basic ToolError creation."""
    error = ToolError("Something went wrong")

    assert error.message == "Something went wrong"
    assert error.error_code == "TOOL_ERROR"
    assert error.tool_name is None
    assert error.details == {}
    assert error.retry_after is None
    assert isinstance(error.timestamp, datetime)


def test_tool_error_with_all_params():
    """Test ToolError with all parameters."""
    details = {"key": "value", "count": 42}
    error = ToolError(
        message="Error message",
        tool_name="test_tool",
        error_code="CUSTOM_ERROR",
        details=details,
        retry_after=120,
    )

    assert error.message == "Error message"
    assert error.tool_name == "test_tool"
    assert error.error_code == "CUSTOM_ERROR"
    assert error.details == details
    assert error.retry_after == 120


def test_tool_error_to_dict():
    """Test ToolError.to_dict() method."""
    error = ToolError(
        message="Test error",
        tool_name="test_tool",
        error_code="TEST_ERROR",
        details={"info": "extra"},
        retry_after=60,
    )

    result = error.to_dict()

    assert result["error_type"] == "ToolError"
    assert result["error_code"] == "TEST_ERROR"
    assert result["message"] == "Test error"
    assert result["tool_name"] == "test_tool"
    assert result["details"] == {"info": "extra"}
    assert result["retry_after"] == 60
    assert "timestamp" in result
    assert isinstance(result["timestamp"], str)  # ISO format


def test_tool_error_str():
    """Test ToolError string representation."""
    error = ToolError(message="Error occurred", error_code="ERR_CODE")

    assert str(error) == "[ERR_CODE] Error occurred"


def test_tool_error_str_with_tool_name():
    """Test ToolError string with tool name."""
    error = ToolError(message="Error occurred", tool_name="my_tool", error_code="ERR_CODE")

    assert str(error) == "my_tool: [ERR_CODE] Error occurred"


def test_tool_error_str_with_retry_after():
    """Test ToolError string with retry_after."""
    error = ToolError(message="Error occurred", error_code="ERR_CODE", retry_after=30)

    assert str(error) == "[ERR_CODE] Error occurred (retry after 30s)"


def test_tool_error_str_complete():
    """Test ToolError string with all components."""
    error = ToolError(
        message="Error occurred", tool_name="my_tool", error_code="ERR_CODE", retry_after=60
    )

    assert str(error) == "my_tool: [ERR_CODE] Error occurred (retry after 60s)"


def test_tool_error_is_exception():
    """Test that ToolError is a proper Exception."""
    error = ToolError("Test")

    assert isinstance(error, Exception)
    with pytest.raises(ToolError):
        raise error


# Test ValidationError


def test_validation_error_basic():
    """Test basic ValidationError."""
    error = ValidationError("Invalid input")

    assert error.message == "Invalid input"
    assert error.error_code == "VALIDATION_ERROR"
    assert error.details == {}


def test_validation_error_with_field():
    """Test ValidationError with field name."""
    error = ValidationError("Invalid email", field="email")

    assert error.message == "Invalid email"
    assert error.error_code == "VALIDATION_ERROR"
    assert error.details == {"field": "email"}


def test_validation_error_with_field_and_tool():
    """Test ValidationError with field and tool name."""
    error = ValidationError("Invalid input", field="username", tool_name="login_tool")

    assert error.tool_name == "login_tool"
    assert error.details["field"] == "username"


def test_validation_error_with_existing_details():
    """Test ValidationError merging field with existing details."""
    error = ValidationError(
        "Invalid input", field="email", details={"reason": "format"}, tool_name="test_tool"
    )

    assert error.details["field"] == "email"
    assert error.details["reason"] == "format"


# Test APIError


def test_api_error_basic():
    """Test basic APIError."""
    error = APIError("API call failed")

    assert error.message == "API call failed"
    assert error.error_code == "API_ERROR"
    assert error.details["api_name"] is None
    assert error.details["status_code"] is None


def test_api_error_with_details():
    """Test APIError with API name and status code."""
    error = APIError("Request failed", api_name="OpenAI", status_code=500)

    assert error.message == "Request failed"
    assert error.error_code == "API_ERROR"
    assert error.details["api_name"] == "OpenAI"
    assert error.details["status_code"] == 500


def test_api_error_with_tool_name():
    """Test APIError with tool name."""
    error = APIError("API error", api_name="Google", tool_name="search_tool")

    assert error.tool_name == "search_tool"
    assert error.details["api_name"] == "Google"


# Test RateLimitError


def test_rate_limit_error_basic():
    """Test basic RateLimitError with defaults."""
    error = RateLimitError()

    assert error.message == "Rate limit exceeded"
    assert error.error_code == "RATE_LIMIT"
    assert error.retry_after == 60
    assert error.details == {}


def test_rate_limit_error_with_params():
    """Test RateLimitError with custom parameters."""
    error = RateLimitError(message="Too many requests", retry_after=120, limit=100)

    assert error.message == "Too many requests"
    assert error.retry_after == 120
    assert error.details["limit"] == 100


def test_rate_limit_error_with_tool_name():
    """Test RateLimitError with tool name."""
    error = RateLimitError(tool_name="search_tool", limit=50)

    assert error.tool_name == "search_tool"
    assert error.details["limit"] == 50


# Test AuthenticationError


def test_authentication_error_basic():
    """Test basic AuthenticationError."""
    error = AuthenticationError("Auth failed")

    assert error.message == "Auth failed"
    assert error.error_code == "AUTH_ERROR"
    assert error.details == {}


def test_authentication_error_with_api():
    """Test AuthenticationError with API name."""
    error = AuthenticationError("Invalid token", api_name="Gmail")

    assert error.message == "Invalid token"
    assert error.details["api_name"] == "Gmail"


def test_authentication_error_with_tool():
    """Test AuthenticationError with tool name."""
    error = AuthenticationError("Auth failed", api_name="Gmail", tool_name="gmail_read")

    assert error.tool_name == "gmail_read"
    assert error.details["api_name"] == "Gmail"


# Test TimeoutError


def test_timeout_error_basic():
    """Test basic TimeoutError with default message."""
    error = TimeoutError()

    assert error.message == "Operation timed out"
    assert error.error_code == "TIMEOUT"
    assert error.details == {}


def test_timeout_error_with_timeout():
    """Test TimeoutError with timeout value."""
    error = TimeoutError(message="Request timed out", timeout=30)

    assert error.message == "Request timed out"
    assert error.details["timeout"] == 30


def test_timeout_error_with_tool():
    """Test TimeoutError with tool name."""
    error = TimeoutError(timeout=60, tool_name="slow_tool")

    assert error.tool_name == "slow_tool"
    assert error.details["timeout"] == 60


# Test ResourceNotFoundError


def test_resource_not_found_error_basic():
    """Test basic ResourceNotFoundError."""
    error = ResourceNotFoundError("Resource not found")

    assert error.message == "Resource not found"
    assert error.error_code == "NOT_FOUND"
    assert error.details == {}


def test_resource_not_found_error_with_type():
    """Test ResourceNotFoundError with resource type."""
    error = ResourceNotFoundError("File not found", resource_type="file")

    assert error.message == "File not found"
    assert error.details["resource_type"] == "file"


def test_resource_not_found_error_with_tool():
    """Test ResourceNotFoundError with tool name."""
    error = ResourceNotFoundError("Not found", resource_type="document", tool_name="doc_tool")

    assert error.tool_name == "doc_tool"
    assert error.details["resource_type"] == "document"


# Test ConfigurationError


def test_configuration_error_basic():
    """Test basic ConfigurationError."""
    error = ConfigurationError("Config error")

    assert error.message == "Config error"
    assert error.error_code == "CONFIG_ERROR"
    assert error.details == {}


def test_configuration_error_with_key():
    """Test ConfigurationError with config key."""
    error = ConfigurationError("Missing config", config_key="api_key")

    assert error.message == "Missing config"
    assert error.details["config_key"] == "api_key"


def test_configuration_error_with_tool():
    """Test ConfigurationError with tool name."""
    error = ConfigurationError("Invalid config", config_key="timeout", tool_name="my_tool")

    assert error.tool_name == "my_tool"
    assert error.details["config_key"] == "timeout"


# Test QuotaExceededError


def test_quota_exceeded_error_basic():
    """Test basic QuotaExceededError with defaults."""
    error = QuotaExceededError()

    assert error.message == "Quota exceeded"
    assert error.error_code == "QUOTA_EXCEEDED"
    assert error.details["quota_type"] is None
    assert error.details["limit"] is None
    assert error.details["used"] is None


def test_quota_exceeded_error_with_params():
    """Test QuotaExceededError with all parameters."""
    error = QuotaExceededError(
        message="Daily quota exceeded", quota_type="daily_requests", limit=1000, used=1005
    )

    assert error.message == "Daily quota exceeded"
    assert error.details["quota_type"] == "daily_requests"
    assert error.details["limit"] == 1000
    assert error.details["used"] == 1005


def test_quota_exceeded_error_with_tool():
    """Test QuotaExceededError with tool name."""
    error = QuotaExceededError(quota_type="api_calls", limit=100, used=100, tool_name="api_tool")

    assert error.tool_name == "api_tool"
    assert error.details["quota_type"] == "api_calls"


# Test SecurityError


def test_security_error_basic():
    """Test basic SecurityError."""
    error = SecurityError("Security violation")

    assert error.message == "Security violation"
    assert error.error_code == "SECURITY_ERROR"
    assert error.details == {}


def test_security_error_with_violation():
    """Test SecurityError with violation type."""
    error = SecurityError("Path traversal detected", violation_type="path_traversal")

    assert error.message == "Path traversal detected"
    assert error.details["violation_type"] == "path_traversal"


def test_security_error_with_tool():
    """Test SecurityError with tool name."""
    error = SecurityError(
        "SQL injection attempt", violation_type="sql_injection", tool_name="db_tool"
    )

    assert error.tool_name == "db_tool"
    assert error.details["violation_type"] == "sql_injection"


# Test MediaError


def test_media_error_basic():
    """Test basic MediaError."""
    error = MediaError("Media processing failed")

    assert error.message == "Media processing failed"
    assert error.error_code == "MEDIA_ERROR"
    assert error.details == {}


def test_media_error_with_type():
    """Test MediaError with media type."""
    error = MediaError("Invalid format", media_type="video")

    assert error.message == "Invalid format"
    assert error.details["media_type"] == "video"


def test_media_error_with_tool():
    """Test MediaError with tool name."""
    error = MediaError("Processing error", media_type="image", tool_name="image_tool")

    assert error.tool_name == "image_tool"
    assert error.details["media_type"] == "image"


# Test handle_api_response Utility


def test_handle_api_response_401():
    """Test handle_api_response with 401 status."""
    response = Mock()
    response.status_code = 401

    with pytest.raises(AuthenticationError) as exc_info:
        handle_api_response(response, "TestAPI")

    assert "Authentication failed for TestAPI" in str(exc_info.value)
    assert exc_info.value.details["api_name"] == "TestAPI"


def test_handle_api_response_403():
    """Test handle_api_response with 403 status."""
    response = Mock()
    response.status_code = 403

    with pytest.raises(AuthenticationError) as exc_info:
        handle_api_response(response, "TestAPI")

    assert "Access forbidden for TestAPI" in str(exc_info.value)


def test_handle_api_response_404():
    """Test handle_api_response with 404 status."""
    response = Mock()
    response.status_code = 404

    with pytest.raises(ResourceNotFoundError) as exc_info:
        handle_api_response(response, "TestAPI")

    assert "Resource not found on TestAPI" in str(exc_info.value)
    assert exc_info.value.details["resource_type"] == "TestAPI"


def test_handle_api_response_429():
    """Test handle_api_response with 429 status."""
    response = Mock()
    response.status_code = 429
    response.headers = {"Retry-After": "90"}

    with pytest.raises(RateLimitError) as exc_info:
        handle_api_response(response, "TestAPI")

    assert "Rate limit exceeded for TestAPI" in str(exc_info.value)
    assert exc_info.value.retry_after == 90


def test_handle_api_response_429_no_retry_header():
    """Test handle_api_response with 429 but no Retry-After header."""
    response = Mock()
    response.status_code = 429
    response.headers = {}

    with pytest.raises(RateLimitError) as exc_info:
        handle_api_response(response, "TestAPI")

    assert exc_info.value.retry_after == 60  # Default value


def test_handle_api_response_500():
    """Test handle_api_response with 500 status."""
    response = Mock()
    response.status_code = 500

    with pytest.raises(APIError) as exc_info:
        handle_api_response(response, "TestAPI")

    assert "TestAPI server error" in str(exc_info.value)
    assert exc_info.value.details["status_code"] == 500


def test_handle_api_response_503():
    """Test handle_api_response with 503 status."""
    response = Mock()
    response.status_code = 503

    with pytest.raises(APIError) as exc_info:
        handle_api_response(response, "TestAPI")

    assert "TestAPI server error" in str(exc_info.value)
    assert exc_info.value.details["status_code"] == 503


def test_handle_api_response_400():
    """Test handle_api_response with 400 status."""
    response = Mock()
    response.status_code = 400

    with pytest.raises(APIError) as exc_info:
        handle_api_response(response, "TestAPI")

    assert "TestAPI request failed" in str(exc_info.value)
    assert exc_info.value.details["status_code"] == 400


def test_handle_api_response_422():
    """Test handle_api_response with 422 status."""
    response = Mock()
    response.status_code = 422

    with pytest.raises(APIError) as exc_info:
        handle_api_response(response, "TestAPI")

    assert "TestAPI request failed" in str(exc_info.value)


def test_handle_api_response_200():
    """Test handle_api_response with success status (200)."""
    response = Mock()
    response.status_code = 200

    # Should not raise any exception
    handle_api_response(response, "TestAPI")


def test_handle_api_response_201():
    """Test handle_api_response with success status (201)."""
    response = Mock()
    response.status_code = 201

    # Should not raise any exception
    handle_api_response(response, "TestAPI")


def test_handle_api_response_no_status_code():
    """Test handle_api_response with object without status_code."""
    response = Mock(spec=[])  # No attributes

    # Should not raise any exception
    handle_api_response(response, "TestAPI")


# Test Error Inheritance


def test_all_errors_inherit_from_tool_error():
    """Test that all custom errors inherit from ToolError."""
    error_classes = [
        ValidationError,
        APIError,
        RateLimitError,
        AuthenticationError,
        TimeoutError,
        ResourceNotFoundError,
        ConfigurationError,
        QuotaExceededError,
        SecurityError,
        MediaError,
    ]

    for error_class in error_classes:
        error = error_class("Test message")
        assert isinstance(error, ToolError)
        assert isinstance(error, Exception)


def test_error_code_uniqueness():
    """Test that each error type has a unique error code."""
    errors = {
        "ToolError": ToolError("msg"),
        "ValidationError": ValidationError("msg"),
        "APIError": APIError("msg"),
        "RateLimitError": RateLimitError(),
        "AuthenticationError": AuthenticationError("msg"),
        "TimeoutError": TimeoutError(),
        "ResourceNotFoundError": ResourceNotFoundError("msg"),
        "ConfigurationError": ConfigurationError("msg"),
        "QuotaExceededError": QuotaExceededError(),
        "SecurityError": SecurityError("msg"),
        "MediaError": MediaError("msg"),
    }

    error_codes = set()
    for name, error in errors.items():
        assert error.error_code not in error_codes, f"{name} has duplicate error_code"
        error_codes.add(error.error_code)


# Test Edge Cases


def test_tool_error_empty_message():
    """Test ToolError with empty message."""
    error = ToolError("")

    assert error.message == ""
    assert str(error) == "[TOOL_ERROR] "


def test_tool_error_none_details():
    """Test ToolError explicitly with None details."""
    error = ToolError("Test", details=None)

    assert error.details == {}


def test_validation_error_none_field():
    """Test ValidationError with None field."""
    error = ValidationError("Test", field=None)

    assert "field" not in error.details or error.details.get("field") is None


def test_timestamp_is_datetime():
    """Test that timestamp is a datetime object."""
    error = ToolError("Test")

    assert isinstance(error.timestamp, datetime)
    # Timestamp should be recent (within last second)
    now = datetime.utcnow()
    assert (now - error.timestamp).total_seconds() < 1


def test_to_dict_iso_timestamp():
    """Test that to_dict() produces ISO format timestamp."""
    error = ToolError("Test")
    result = error.to_dict()

    # Should be ISO format string
    assert isinstance(result["timestamp"], str)
    # Should be parseable back to datetime
    parsed = datetime.fromisoformat(result["timestamp"])
    assert isinstance(parsed, datetime)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
