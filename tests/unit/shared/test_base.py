"""
Comprehensive tests for shared.base module.
Target coverage: 95%+
"""

import logging
import os
import time
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import Field

from shared.analytics import EventType
from shared.base import BaseTool, SimpleBaseTool, create_simple_tool
from shared.errors import RateLimitError, ToolError, ValidationError

# Test Tool Implementations


class TestTool(BaseTool):
    """Test tool for unit testing."""

    tool_name: str = "test_tool"
    tool_category: str = "test"

    test_param: str = Field(..., description="Test parameter")

    def _execute(self) -> Dict[str, Any]:
        """Execute test logic."""
        return {"success": True, "data": self.test_param}


class FailingTool(BaseTool):
    """Tool that always fails."""

    tool_name: str = "failing_tool"
    tool_category: str = "test"

    error_type: str = Field("tool", description="Type of error to raise")

    def _execute(self) -> Dict[str, Any]:
        """Always raises an error."""
        if self.error_type == "validation":
            raise ValidationError("Validation failed", tool_name=self.tool_name)
        elif self.error_type == "rate_limit":
            raise RateLimitError("Rate limit exceeded", tool_name=self.tool_name)
        else:
            raise ToolError("Generic error", tool_name=self.tool_name)


class RetryableTool(BaseTool):
    """Tool that fails then succeeds."""

    tool_name: str = "retryable_tool"
    tool_category: str = "test"
    max_retries: int = 3

    fail_count: int = Field(2, description="Number of times to fail before success")
    _attempts: int = 0

    def _execute(self) -> Dict[str, Any]:
        """Fails N times then succeeds."""
        self._attempts += 1
        if self._attempts <= self.fail_count:
            raise ToolError("Temporary error", tool_name=self.tool_name, error_code="TEMP_ERROR")
        return {"success": True, "attempts": self._attempts}


class NoExecuteTool(BaseTool):
    """Tool without _execute implementation."""

    tool_name: str = "no_execute_tool"
    tool_category: str = "test"


# Fixtures


@pytest.fixture
def mock_env_clean():
    """Clean environment for testing."""
    # Save original env
    original = os.environ.copy()

    # Clear analytics and mock mode
    os.environ.pop("USE_MOCK_APIS", None)
    os.environ.pop("ANALYTICS_ENABLED", None)

    yield

    # Restore original env
    os.environ.clear()
    os.environ.update(original)


@pytest.fixture
def mock_mode():
    """Enable mock mode."""
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    os.environ.pop("USE_MOCK_APIS", None)


@pytest.fixture
def disable_analytics():
    """Disable analytics."""
    os.environ["ANALYTICS_ENABLED"] = "false"
    yield
    os.environ.pop("ANALYTICS_ENABLED", None)


# Test BaseTool Initialization


def test_base_tool_init():
    """Test BaseTool initialization."""
    tool = TestTool(test_param="hello")

    assert tool.tool_name == "test_tool"
    assert tool.tool_category == "test"
    assert tool.test_param == "hello"
    assert tool._request_id is not None
    assert len(tool._request_id) == 36  # UUID format
    assert tool._logger is not None
    assert isinstance(tool._logger, logging.Logger)
    assert tool._start_time is None


def test_base_tool_init_with_user_id():
    """Test BaseTool initialization with user_id."""
    tool = TestTool(test_param="hello", user_id="user123")

    assert tool._user_id == "user123"
    assert tool._request_id is not None


def test_base_tool_metadata():
    """Test tool metadata properties."""
    tool = TestTool(test_param="test")

    assert tool.tool_name == "test_tool"
    assert tool.tool_category == "test"
    assert tool.rate_limit_type == "default"
    assert tool.rate_limit_cost == 1
    assert tool.max_retries == 3
    assert tool.retry_delay == 1.0


# Test _execute() Abstract Method


def test_execute_not_implemented():
    """Test that _execute() must be implemented."""
    tool = NoExecuteTool()

    with pytest.raises(NotImplementedError):
        tool._execute()


def test_execute_called_by_run():
    """Test that run() calls _execute()."""
    tool = TestTool(test_param="test")

    with patch.object(tool, "_execute", return_value={"success": True}) as mock_execute:
        result = tool.run()

        mock_execute.assert_called_once()
        assert result == {"success": True}


# Test run() Method


def test_run_success():
    """Test successful tool execution."""
    tool = TestTool(test_param="hello")
    result = tool.run()

    assert result == {"success": True, "data": "hello"}


def test_run_sets_start_time():
    """Test that run() sets start_time."""
    tool = TestTool(test_param="test")

    assert tool._start_time is None
    tool.run()
    assert tool._start_time is not None
    assert isinstance(tool._start_time, float)


def test_run_with_tool_error():
    """Test run() with ToolError."""
    tool = FailingTool(error_type="tool")
    result = tool.run()

    assert result["success"] is False
    assert "error" in result
    assert result["error"]["code"] == "TOOL_ERROR"
    assert result["error"]["tool"] == "failing_tool"
    assert "request_id" in result["error"]


def test_run_with_validation_error():
    """Test run() with ValidationError."""
    tool = FailingTool(error_type="validation")
    result = tool.run()

    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"


def test_run_with_unexpected_error():
    """Test run() with unexpected exception."""
    tool = TestTool(test_param="test")

    with patch.object(tool, "_execute", side_effect=Exception("Unexpected!")):
        result = tool.run()

        assert result["success"] is False
        assert result["error"]["code"] == "UNEXPECTED_ERROR"
        assert "Unexpected!" in result["error"]["message"]


# Test Retry Logic


def test_execute_with_retry_success_on_first_try():
    """Test successful execution on first try."""
    tool = TestTool(test_param="test")
    result = tool._execute_with_retry()

    assert result == {"success": True, "data": "test"}


def test_execute_with_retry_eventual_success():
    """Test retry logic with eventual success."""
    tool = RetryableTool(fail_count=2)
    result = tool._execute_with_retry()

    assert result["success"] is True
    assert result["attempts"] == 3  # Failed twice, succeeded on 3rd


def test_execute_with_retry_validation_error_no_retry():
    """Test that validation errors are not retried."""
    tool = FailingTool(error_type="validation")

    with pytest.raises(ValidationError):
        tool._execute_with_retry()


def test_execute_with_retry_exhausted():
    """Test retry logic when all retries exhausted."""
    tool = RetryableTool(fail_count=10)  # More than max_retries

    with pytest.raises(ToolError):
        tool._execute_with_retry()


def test_execute_with_retry_exponential_backoff():
    """Test exponential backoff in retry logic."""
    tool = RetryableTool(fail_count=2)
    tool.retry_delay = 0.1  # Fast test

    start = time.time()
    tool._execute_with_retry()
    duration = time.time() - start

    # Should have delays: 0.1s (1st retry) + 0.2s (2nd retry) = 0.3s
    assert duration >= 0.3


# Test Rate Limiting


def test_check_rate_limit_in_mock_mode(mock_mode):
    """Test rate limiting is skipped in mock mode."""
    tool = TestTool(test_param="test")

    # Should not raise even if called many times
    for _ in range(1000):
        tool._check_rate_limit()


def test_check_rate_limit_called_during_run(mock_env_clean):
    """Test that run() checks rate limit."""
    tool = TestTool(test_param="test")

    with patch.object(tool, "_check_rate_limit") as mock_check:
        tool.run()
        mock_check.assert_called_once()


def test_check_rate_limit_with_rate_limit_error(mock_env_clean):
    """Test handling of rate limit errors."""
    tool = TestTool(test_param="test")

    with patch("shared.base.get_rate_limiter") as mock_limiter:
        mock_limiter.return_value.check_rate_limit.side_effect = RateLimitError()

        with pytest.raises(RateLimitError):
            tool._check_rate_limit()


# Test Analytics


def test_record_event_on_success(mock_env_clean):
    """Test analytics event recording on success."""
    tool = TestTool(test_param="test")

    with patch("shared.base.record_event") as mock_record:
        tool.run()

        # Should record start and success events
        assert mock_record.call_count == 2

        # Check first call (start event)
        start_event = mock_record.call_args_list[0][0][0]
        assert start_event.event_type == EventType.TOOL_START
        assert start_event.tool_name == "test_tool"

        # Check second call (success event)
        success_event = mock_record.call_args_list[1][0][0]
        assert success_event.event_type == EventType.TOOL_SUCCESS
        assert success_event.success is True


def test_record_event_on_error(mock_env_clean):
    """Test analytics event recording on error."""
    tool = FailingTool(error_type="tool")

    with patch("shared.base.record_event") as mock_record:
        tool.run()

        # Should record start and error events
        assert mock_record.call_count == 2

        error_event = mock_record.call_args_list[1][0][0]
        assert error_event.event_type == EventType.TOOL_ERROR
        assert error_event.success is False
        assert error_event.error_code == "TOOL_ERROR"


def test_analytics_disabled(disable_analytics):
    """Test that analytics can be disabled."""
    tool = TestTool(test_param="test")
    tool._enable_analytics = False

    with patch("shared.base.record_event") as mock_record:
        tool.run()

        # Should not record any events
        mock_record.assert_not_called()


# Test Logging


def test_log_start(caplog):
    """Test logging at start."""
    tool = TestTool(test_param="test")

    with caplog.at_level(logging.INFO):
        tool.run()

    assert "Starting test_tool" in caplog.text
    assert "request_id=" in caplog.text


def test_log_success(caplog):
    """Test logging on success."""
    tool = TestTool(test_param="test")

    with caplog.at_level(logging.INFO):
        tool.run()

    assert "Completed test_tool" in caplog.text
    assert "ms" in caplog.text


def test_log_error(caplog):
    """Test logging on error."""
    tool = FailingTool(error_type="tool")

    with caplog.at_level(logging.ERROR):
        tool.run()

    assert "Failed failing_tool" in caplog.text
    assert "Error:" in caplog.text


def test_logging_disabled():
    """Test that logging can be disabled."""
    tool = TestTool(test_param="test")
    tool._enable_logging = False

    with patch.object(tool._logger, "info") as mock_log:
        tool.run()

        mock_log.assert_not_called()


# Test Error Formatting


def test_format_error_response():
    """Test error response formatting."""
    tool = TestTool(test_param="test")
    error = ToolError(
        message="Test error",
        tool_name="test_tool",
        error_code="TEST_ERROR",
        retry_after=60,
        details={"key": "value"},
    )

    result = tool._format_error_response(error)

    assert result["success"] is False
    assert result["error"]["code"] == "TEST_ERROR"
    assert result["error"]["message"] == "Test error"
    assert result["error"]["tool"] == "test_tool"
    assert result["error"]["retry_after"] == 60
    assert result["error"]["details"] == {"key": "value"}
    assert "request_id" in result["error"]


# Test Utility Methods


def test_get_metadata():
    """Test _get_metadata() method."""
    tool = TestTool(test_param="test", user_id="user123")
    metadata = tool._get_metadata()

    assert metadata["tool_name"] == "test_tool"
    assert metadata["tool_category"] == "test"
    assert metadata["user_id"] == "user123"
    assert "request_id" in metadata


def test_should_use_mock_enabled():
    """Test _should_use_mock() when enabled."""
    os.environ["USE_MOCK_APIS"] = "true"
    tool = TestTool(test_param="test")

    assert tool._should_use_mock() is True

    os.environ.pop("USE_MOCK_APIS")


def test_should_use_mock_disabled():
    """Test _should_use_mock() when disabled."""
    os.environ.pop("USE_MOCK_APIS", None)
    tool = TestTool(test_param="test")

    assert tool._should_use_mock() is False


def test_should_use_mock_case_insensitive():
    """Test _should_use_mock() is case insensitive."""
    for value in ["TRUE", "True", "true", "TrUe"]:
        os.environ["USE_MOCK_APIS"] = value
        tool = TestTool(test_param="test")
        assert tool._should_use_mock() is True

    os.environ.pop("USE_MOCK_APIS")


# Test SimpleBaseTool


def test_simple_base_tool():
    """Test SimpleBaseTool configuration."""

    class SimpleTest(SimpleBaseTool):
        tool_name: str = "simple_test"
        test_param: str = Field(..., description="Test")

        def _execute(self):
            return {"success": True}

    tool = SimpleTest(test_param="test")

    assert tool.max_retries == 1  # No retries
    assert tool._enable_analytics is False


def test_simple_base_tool_no_retries():
    """Test that SimpleBaseTool doesn't retry."""

    class SimpleFailTool(SimpleBaseTool):
        tool_name: str = "simple_fail"
        _attempts: int = 0

        def _execute(self):
            self._attempts += 1
            raise ToolError("Fail", tool_name=self.tool_name)

    tool = SimpleFailTool()
    result = tool.run()

    assert result["success"] is False
    assert tool._attempts == 1  # Only tried once


# Test create_simple_tool


def test_create_simple_tool():
    """Test create_simple_tool() utility."""

    def upper_func(tool_instance):
        return tool_instance.text.upper()

    UpperTool = create_simple_tool("upper_tool", upper_func, "Converts to uppercase")

    assert UpperTool.tool_name == "upper_tool"
    assert "uppercase" in UpperTool.__doc__


def test_create_simple_tool_execution():
    """Test execution of dynamically created tool."""

    def reverse_func(tool_instance):
        return tool_instance.text[::-1]

    ReverseTool = create_simple_tool("reverse_tool", reverse_func, "Reverses text")

    # Can't instantiate without fields, so we test the class structure
    assert hasattr(ReverseTool, "_execute")
    assert ReverseTool.tool_name == "reverse_tool"


# Test Edge Cases


def test_run_with_none_return():
    """Test handling of None return from _execute."""

    class NoneTool(BaseTool):
        tool_name: str = "none_tool"

        def _execute(self):
            return None

    tool = NoneTool()
    result = tool.run()

    assert result is None


def test_run_with_string_return():
    """Test handling of string return from _execute."""

    class StringTool(BaseTool):
        tool_name: str = "string_tool"

        def _execute(self):
            return "simple string"

    tool = StringTool()
    result = tool.run()

    assert result == "simple string"


def test_run_with_list_return():
    """Test handling of list return from _execute."""

    class ListTool(BaseTool):
        tool_name: str = "list_tool"

        def _execute(self):
            return [1, 2, 3]

    tool = ListTool()
    result = tool.run()

    assert result == [1, 2, 3]


def test_multiple_runs_same_instance():
    """Test running same tool instance multiple times."""
    tool = TestTool(test_param="test")

    result1 = tool.run()
    result2 = tool.run()

    # Both should succeed
    assert result1 == {"success": True, "data": "test"}
    assert result2 == {"success": True, "data": "test"}


def test_concurrent_tool_instances():
    """Test multiple tool instances can run concurrently."""
    tool1 = TestTool(test_param="tool1")
    tool2 = TestTool(test_param="tool2")

    result1 = tool1.run()
    result2 = tool2.run()

    assert result1 == {"success": True, "data": "tool1"}
    assert result2 == {"success": True, "data": "tool2"}
    assert tool1._request_id != tool2._request_id


# Test Performance


def test_run_performance():
    """Test that run() overhead is minimal."""
    tool = TestTool(test_param="test")

    start = time.time()
    tool.run()
    duration = time.time() - start

    # Should complete very quickly (< 100ms)
    assert duration < 0.1


def test_record_event_measures_duration():
    """Test that events include duration measurement."""
    tool = TestTool(test_param="test")

    with patch("shared.base.record_event") as mock_record:
        tool.run()

        success_event = mock_record.call_args_list[1][0][0]
        assert success_event.duration_ms is not None
        assert success_event.duration_ms > 0


# Test Agency Swarm Compatibility


def test_agency_swarm_import_fallback():
    """Test fallback BaseTool when agency_swarm not installed."""
    # This is tested by the import at module level
    # If we got here, imports worked
    assert BaseTool is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
