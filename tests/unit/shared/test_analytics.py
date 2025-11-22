"""
Comprehensive tests for shared.analytics module.
Target coverage: 90%+
"""

import pytest
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from shared.analytics import (
    EventType,
    AnalyticsEvent,
    ToolMetrics,
    AnalyticsBackend,
    InMemoryBackend,
    FileBackend,
    get_backend,
    record_event,
    get_metrics,
    get_all_metrics,
    print_metrics
)


# Fixtures

@pytest.fixture
def temp_analytics_dir():
    """Create temporary directory for analytics tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def clean_env():
    """Clean environment variables."""
    original = os.environ.copy()
    os.environ.pop("ANALYTICS_ENABLED", None)
    os.environ.pop("ANALYTICS_BACKEND", None)
    os.environ.pop("ANALYTICS_LOG_DIR", None)
    yield
    os.environ.clear()
    os.environ.update(original)


@pytest.fixture
def memory_backend():
    """Create in-memory backend for testing."""
    return InMemoryBackend()


@pytest.fixture
def file_backend(temp_analytics_dir):
    """Create file backend for testing."""
    return FileBackend(log_dir=temp_analytics_dir)


# Test EventType Enum

def test_event_type_values():
    """Test EventType enum values."""
    assert EventType.TOOL_START.value == "tool_start"
    assert EventType.TOOL_SUCCESS.value == "tool_success"
    assert EventType.TOOL_ERROR.value == "tool_error"
    assert EventType.API_CALL.value == "api_call"
    assert EventType.RATE_LIMIT.value == "rate_limit"
    assert EventType.VALIDATION_ERROR.value == "validation_error"


def test_event_type_members():
    """Test all EventType members exist."""
    expected = {
        "TOOL_START",
        "TOOL_SUCCESS",
        "TOOL_ERROR",
        "API_CALL",
        "RATE_LIMIT",
        "VALIDATION_ERROR"
    }
    actual = {e.name for e in EventType}
    assert actual == expected


# Test AnalyticsEvent

def test_analytics_event_creation():
    """Test AnalyticsEvent creation with required fields."""
    event = AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool"
    )

    assert event.event_type == EventType.TOOL_SUCCESS
    assert event.tool_name == "test_tool"
    assert isinstance(event.timestamp, datetime)
    assert event.duration_ms is None
    assert event.success is True
    assert event.error_code is None
    assert event.error_message is None
    assert event.metadata == {}
    assert event.user_id is None
    assert event.request_id is None


def test_analytics_event_with_all_fields():
    """Test AnalyticsEvent with all optional fields."""
    event = AnalyticsEvent(
        event_type=EventType.TOOL_ERROR,
        tool_name="test_tool",
        duration_ms=123.45,
        success=False,
        error_code="TEST_ERROR",
        error_message="Test error message",
        metadata={"key": "value"},
        user_id="user123",
        request_id="req123"
    )

    assert event.duration_ms == 123.45
    assert event.success is False
    assert event.error_code == "TEST_ERROR"
    assert event.error_message == "Test error message"
    assert event.metadata == {"key": "value"}
    assert event.user_id == "user123"
    assert event.request_id == "req123"


def test_analytics_event_to_dict():
    """Test AnalyticsEvent.to_dict() conversion."""
    event = AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool",
        duration_ms=100.0
    )

    result = event.to_dict()

    assert result["event_type"] == "tool_success"
    assert result["tool_name"] == "test_tool"
    assert result["duration_ms"] == 100.0
    assert "timestamp" in result
    assert isinstance(result["timestamp"], str)  # ISO format


# Test ToolMetrics

def test_tool_metrics_defaults():
    """Test ToolMetrics default values."""
    metrics = ToolMetrics(tool_name="test_tool")

    assert metrics.tool_name == "test_tool"
    assert metrics.total_requests == 0
    assert metrics.successful_requests == 0
    assert metrics.failed_requests == 0
    assert metrics.total_duration_ms == 0.0
    assert metrics.min_duration_ms is None
    assert metrics.max_duration_ms is None
    assert metrics.error_count_by_code == {}
    assert metrics.last_success is None
    assert metrics.last_error is None


def test_tool_metrics_avg_duration():
    """Test avg_duration_ms property."""
    metrics = ToolMetrics(tool_name="test")
    metrics.total_requests = 5
    metrics.total_duration_ms = 500.0

    assert metrics.avg_duration_ms == 100.0


def test_tool_metrics_avg_duration_no_requests():
    """Test avg_duration_ms with no requests."""
    metrics = ToolMetrics(tool_name="test")

    assert metrics.avg_duration_ms == 0.0


def test_tool_metrics_success_rate():
    """Test success_rate property."""
    metrics = ToolMetrics(tool_name="test")
    metrics.total_requests = 100
    metrics.successful_requests = 90

    assert metrics.success_rate == 90.0


def test_tool_metrics_success_rate_no_requests():
    """Test success_rate with no requests."""
    metrics = ToolMetrics(tool_name="test")

    assert metrics.success_rate == 0.0


def test_tool_metrics_error_rate():
    """Test error_rate property."""
    metrics = ToolMetrics(tool_name="test")
    metrics.total_requests = 100
    metrics.successful_requests = 90

    assert metrics.error_rate == 10.0


def test_tool_metrics_to_dict():
    """Test ToolMetrics.to_dict() conversion."""
    metrics = ToolMetrics(tool_name="test")
    metrics.total_requests = 10
    metrics.successful_requests = 8
    metrics.failed_requests = 2
    metrics.total_duration_ms = 1000.0
    metrics.min_duration_ms = 50.0
    metrics.max_duration_ms = 200.0
    metrics.error_count_by_code = {"ERROR_1": 1, "ERROR_2": 1}
    metrics.last_success = datetime.utcnow()
    metrics.last_error = datetime.utcnow()

    result = metrics.to_dict()

    assert result["tool_name"] == "test"
    assert result["total_requests"] == 10
    assert result["successful_requests"] == 8
    assert result["failed_requests"] == 2
    assert result["avg_duration_ms"] == 100.0
    assert result["min_duration_ms"] == 50.0
    assert result["max_duration_ms"] == 200.0
    assert result["success_rate"] == 80.0
    assert result["error_rate"] == 20.0
    assert result["error_count_by_code"] == {"ERROR_1": 1, "ERROR_2": 1}
    assert isinstance(result["last_success"], str)
    assert isinstance(result["last_error"], str)


# Test InMemoryBackend

def test_inmemory_backend_init(memory_backend):
    """Test InMemoryBackend initialization."""
    assert memory_backend.events == []
    assert hasattr(memory_backend, '_lock')


def test_inmemory_backend_record_event(memory_backend):
    """Test recording events in memory."""
    event = AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool"
    )

    memory_backend.record_event(event)

    assert len(memory_backend.events) == 1
    assert memory_backend.events[0] == event


def test_inmemory_backend_multiple_events(memory_backend):
    """Test recording multiple events."""
    for i in range(5):
        event = AnalyticsEvent(
            event_type=EventType.TOOL_SUCCESS,
            tool_name=f"tool_{i}"
        )
        memory_backend.record_event(event)

    assert len(memory_backend.events) == 5


def test_inmemory_backend_get_metrics_empty(memory_backend):
    """Test get_metrics with no events."""
    metrics = memory_backend.get_metrics("test_tool")

    assert metrics.tool_name == "test_tool"
    assert metrics.total_requests == 0


def test_inmemory_backend_get_metrics_success(memory_backend):
    """Test get_metrics with success events."""
    # Add success events
    for i in range(3):
        event = AnalyticsEvent(
            event_type=EventType.TOOL_SUCCESS,
            tool_name="test_tool",
            duration_ms=100.0 + i * 10
        )
        memory_backend.record_event(event)

    metrics = memory_backend.get_metrics("test_tool")

    assert metrics.total_requests == 3
    assert metrics.successful_requests == 3
    assert metrics.failed_requests == 0
    assert metrics.min_duration_ms == 100.0
    assert metrics.max_duration_ms == 120.0
    assert metrics.success_rate == 100.0


def test_inmemory_backend_get_metrics_errors(memory_backend):
    """Test get_metrics with error events."""
    for i in range(2):
        event = AnalyticsEvent(
            event_type=EventType.TOOL_ERROR,
            tool_name="test_tool",
            success=False,
            error_code="ERROR_1"
        )
        memory_backend.record_event(event)

    metrics = memory_backend.get_metrics("test_tool")

    assert metrics.total_requests == 2
    assert metrics.successful_requests == 0
    assert metrics.failed_requests == 2
    assert metrics.error_count_by_code["ERROR_1"] == 2
    assert metrics.success_rate == 0.0


def test_inmemory_backend_get_metrics_mixed(memory_backend):
    """Test get_metrics with mixed success/error events."""
    # 3 successes
    for _ in range(3):
        memory_backend.record_event(AnalyticsEvent(
            event_type=EventType.TOOL_SUCCESS,
            tool_name="test_tool"
        ))

    # 2 errors
    for _ in range(2):
        memory_backend.record_event(AnalyticsEvent(
            event_type=EventType.TOOL_ERROR,
            tool_name="test_tool",
            success=False,
            error_code="ERROR"
        ))

    metrics = memory_backend.get_metrics("test_tool")

    assert metrics.total_requests == 5
    assert metrics.successful_requests == 3
    assert metrics.failed_requests == 2
    assert metrics.success_rate == 60.0
    assert metrics.error_rate == 40.0


def test_inmemory_backend_get_metrics_with_days_filter(memory_backend):
    """Test get_metrics with days filter."""
    # Old event (10 days ago)
    old_event = AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool"
    )
    old_event.timestamp = datetime.utcnow() - timedelta(days=10)
    memory_backend.record_event(old_event)

    # Recent event
    recent_event = AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool"
    )
    memory_backend.record_event(recent_event)

    # Get metrics for last 7 days
    metrics = memory_backend.get_metrics("test_tool", days=7)

    assert metrics.total_requests == 1  # Only recent event


def test_inmemory_backend_get_all_metrics(memory_backend):
    """Test get_all_metrics."""
    # Add events for multiple tools
    memory_backend.record_event(AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="tool_a"
    ))
    memory_backend.record_event(AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="tool_b"
    ))

    all_metrics = memory_backend.get_all_metrics()

    assert "tool_a" in all_metrics
    assert "tool_b" in all_metrics
    assert all_metrics["tool_a"].total_requests == 1
    assert all_metrics["tool_b"].total_requests == 1


# Test FileBackend

def test_file_backend_init(file_backend, temp_analytics_dir):
    """Test FileBackend initialization."""
    assert file_backend.log_dir == Path(temp_analytics_dir)
    assert file_backend.log_dir.exists()


def test_file_backend_get_log_file(file_backend):
    """Test _get_log_file method."""
    date = datetime(2024, 1, 15)
    log_file = file_backend._get_log_file(date)

    assert log_file.name == "2024-01-15.jsonl"
    assert log_file.parent == file_backend.log_dir


def test_file_backend_record_event(file_backend):
    """Test recording event to file."""
    event = AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool"
    )

    file_backend.record_event(event)

    # Check file was created
    log_file = file_backend._get_log_file(event.timestamp)
    assert log_file.exists()

    # Check content
    with open(log_file, 'r') as f:
        line = f.readline()
        data = json.loads(line)
        assert data["tool_name"] == "test_tool"


def test_file_backend_record_multiple_events(file_backend):
    """Test recording multiple events to file."""
    for i in range(3):
        event = AnalyticsEvent(
            event_type=EventType.TOOL_SUCCESS,
            tool_name=f"tool_{i}"
        )
        file_backend.record_event(event)

    log_file = file_backend._get_log_file(datetime.utcnow())

    # Check all events were written
    with open(log_file, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 3


def test_file_backend_get_metrics_from_file(file_backend):
    """Test get_metrics reading from file."""
    # Record events
    for i in range(3):
        event = AnalyticsEvent(
            event_type=EventType.TOOL_SUCCESS,
            tool_name="test_tool",
            duration_ms=100.0 + i * 10
        )
        file_backend.record_event(event)

    # Get metrics
    metrics = file_backend.get_metrics("test_tool")

    assert metrics.total_requests == 3
    assert metrics.successful_requests == 3
    assert metrics.min_duration_ms == 100.0
    assert metrics.max_duration_ms == 120.0


def test_file_backend_get_metrics_nonexistent_file(file_backend):
    """Test get_metrics when log file doesn't exist."""
    metrics = file_backend.get_metrics("nonexistent_tool")

    assert metrics.total_requests == 0


def test_file_backend_get_all_metrics(file_backend):
    """Test get_all_metrics from files."""
    # Record events for multiple tools
    file_backend.record_event(AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="tool_a"
    ))
    file_backend.record_event(AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="tool_b"
    ))

    all_metrics = file_backend.get_all_metrics()

    assert "tool_a" in all_metrics
    assert "tool_b" in all_metrics


def test_file_backend_handles_malformed_json(file_backend):
    """Test FileBackend handles malformed JSON gracefully."""
    # Write malformed JSON
    log_file = file_backend._get_log_file(datetime.utcnow())
    with open(log_file, 'w') as f:
        f.write("not valid json\n")
        f.write('{"valid": "json"}\n')  # But wrong format

    # Should not crash
    metrics = file_backend.get_metrics("test_tool")
    assert metrics.total_requests == 0


# Test Global Functions

def test_get_backend_default(clean_env, temp_analytics_dir):
    """Test get_backend with default (file) backend."""
    os.environ["ANALYTICS_LOG_DIR"] = temp_analytics_dir

    # Reset global backend
    import shared.analytics
    shared.analytics._backend = None

    backend = get_backend()

    assert isinstance(backend, FileBackend)


def test_get_backend_memory(clean_env):
    """Test get_backend with memory backend."""
    os.environ["ANALYTICS_BACKEND"] = "memory"

    # Reset global backend
    import shared.analytics
    shared.analytics._backend = None

    backend = get_backend()

    assert isinstance(backend, InMemoryBackend)


def test_get_backend_cached():
    """Test that get_backend returns cached instance."""
    backend1 = get_backend()
    backend2 = get_backend()

    assert backend1 is backend2


def test_record_event_global(clean_env):
    """Test global record_event function."""
    os.environ["ANALYTICS_ENABLED"] = "true"
    os.environ["ANALYTICS_BACKEND"] = "memory"

    # Reset backend
    import shared.analytics
    shared.analytics._backend = None

    event = AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool"
    )

    record_event(event)

    # Verify event was recorded
    backend = get_backend()
    assert len(backend.events) >= 1


def test_record_event_disabled(clean_env):
    """Test record_event when analytics disabled."""
    os.environ["ANALYTICS_ENABLED"] = "false"

    # Reset backend
    import shared.analytics
    shared.analytics._backend = None
    shared.analytics._enabled = False

    event = AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool"
    )

    record_event(event)

    # Should not have created backend
    assert shared.analytics._backend is None


def test_record_event_exception_handling(clean_env):
    """Test that record_event handles exceptions gracefully."""
    os.environ["ANALYTICS_BACKEND"] = "memory"

    # Reset backend
    import shared.analytics
    shared.analytics._backend = None

    event = AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool"
    )

    with patch('shared.analytics.get_backend', side_effect=Exception("Backend error")):
        # Should not raise exception
        record_event(event)


def test_get_metrics_global(clean_env):
    """Test global get_metrics function."""
    os.environ["ANALYTICS_BACKEND"] = "memory"

    # Reset and setup
    import shared.analytics
    shared.analytics._backend = None

    record_event(AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool"
    ))

    metrics = get_metrics("test_tool")

    assert metrics.tool_name == "test_tool"
    assert metrics.total_requests >= 1


def test_get_all_metrics_global(clean_env):
    """Test global get_all_metrics function."""
    os.environ["ANALYTICS_BACKEND"] = "memory"

    # Reset
    import shared.analytics
    shared.analytics._backend = None

    record_event(AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="tool_a"
    ))

    all_metrics = get_all_metrics()

    assert isinstance(all_metrics, dict)
    assert "tool_a" in all_metrics


def test_print_metrics_single_tool(clean_env, capsys):
    """Test print_metrics for single tool."""
    os.environ["ANALYTICS_BACKEND"] = "memory"

    # Reset
    import shared.analytics
    shared.analytics._backend = None

    record_event(AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="test_tool",
        duration_ms=100.0
    ))

    print_metrics("test_tool")

    captured = capsys.readouterr()
    assert "test_tool" in captured.out
    assert "Total Requests" in captured.out


def test_print_metrics_all_tools(clean_env, capsys):
    """Test print_metrics for all tools."""
    os.environ["ANALYTICS_BACKEND"] = "memory"

    # Reset
    import shared.analytics
    shared.analytics._backend = None

    record_event(AnalyticsEvent(
        event_type=EventType.TOOL_SUCCESS,
        tool_name="tool_a"
    ))

    print_metrics()

    captured = capsys.readouterr()
    assert "All Tools" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
