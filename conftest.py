"""
Shared pytest fixtures for AgentSwarm Tools.

This file provides common fixtures used across all tests.
"""

import os
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, Mock

import pytest
import redis

# ========== PYTEST CONFIGURATION ==========


def pytest_configure(config):
    """Register custom markers for test categorization."""
    config.addinivalue_line("markers", "unit: mark test as unit test (uses mocks)")
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (uses live APIs)"
    )
    config.addinivalue_line("markers", "slow: mark test as slow-running")


# ========== ENVIRONMENT ==========


@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """Set up test environment variables."""
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("USE_MOCK_APIS", "true")
    os.environ.setdefault("ANALYTICS_ENABLED", "false")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")


# ========== MOCK SERVICES ==========


@pytest.fixture
def mock_redis() -> Mock:
    """Mock Redis client for testing."""
    mock = Mock(spec=redis.Redis)
    mock.get.return_value = None
    mock.set.return_value = True
    mock.hget.return_value = None
    mock.hset.return_value = True
    mock.hgetall.return_value = {}
    mock.incr.return_value = 1
    mock.lpush.return_value = 1
    mock.rpush.return_value = 1
    mock.lpop.return_value = None
    mock.publish.return_value = 1
    return mock


# ========== API RESPONSES ==========


@pytest.fixture
def mock_api_success_response() -> Dict[str, Any]:
    """Standard successful API response."""
    return {
        "status": "success",
        "data": {"result": "test_data"},
        "metadata": {"timestamp": "2025-11-20T10:00:00Z", "request_id": "test-request-123"},
    }


@pytest.fixture
def mock_api_error_response() -> Dict[str, Any]:
    """Standard API error response."""
    return {
        "status": "error",
        "error": {"code": "API_ERROR", "message": "API request failed", "details": {}},
    }


@pytest.fixture
def api_response_factory():
    """Factory for creating custom API responses."""

    def create_response(
        status: str = "success", data: Any = None, error_message: str = None
    ) -> Dict[str, Any]:
        if status == "success":
            return {
                "status": status,
                "data": data or {"result": "test_data"},
                "metadata": {"timestamp": "2025-11-20T10:00:00Z"},
            }
        else:
            return {
                "status": status,
                "error": {"code": "TEST_ERROR", "message": error_message or "Test error"},
            }

    return create_response


# ========== TOOL CONFIGURATION ==========


@pytest.fixture
def sample_tool_config() -> Dict[str, Any]:
    """Sample tool configuration for testing."""
    return {
        "api_key": "test_api_key_12345",
        "timeout": 30,
        "max_retries": 3,
        "rate_limit": {"calls": 10, "period": 60},
        "environment": "test",
    }


@pytest.fixture
def mock_tool_params() -> Dict[str, Any]:
    """Common tool parameters for testing."""
    return {"query": "test query", "max_results": 10, "timeout": 30}


# ========== FILE SYSTEM ==========


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    return str(file_path)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for testing."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    return str(test_dir)


# ========== ASYNC SUPPORT ==========


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ========== TEST DATA ==========


@pytest.fixture
def sample_email_data() -> Dict[str, Any]:
    """Sample email data for testing."""
    return {
        "to": "test@example.com",
        "subject": "Test Email",
        "body": "This is a test email body",
        "from": "sender@example.com",
        "cc": [],
        "bcc": [],
    }


@pytest.fixture
def sample_file_metadata() -> Dict[str, Any]:
    """Sample file metadata for testing."""
    return {
        "filename": "test_document.pdf",
        "size": 1024000,
        "mime_type": "application/pdf",
        "created_at": "2025-11-20T10:00:00Z",
        "modified_at": "2025-11-20T11:00:00Z",
    }


# ========== ERROR SCENARIOS ==========


@pytest.fixture
def api_validation_error():
    """Simulate validation error."""
    from shared.errors import ValidationError

    return ValidationError(
        "Invalid parameter", tool_name="test_tool", details={"param": "test_param"}
    )


# ========== MONITORING ==========


@pytest.fixture
def capture_analytics_events(monkeypatch):
    """Capture analytics events during tests."""
    events = []

    def mock_record_event(event_type, tool_name, **kwargs):
        events.append({"event_type": event_type, "tool_name": tool_name, **kwargs})

    monkeypatch.setattr("shared.analytics.record_event", mock_record_event)
    return events


# ========== CLEANUP ==========


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter between tests."""
    from shared.security import _rate_limiter_instance

    if _rate_limiter_instance:
        _rate_limiter_instance.reset()
    yield
