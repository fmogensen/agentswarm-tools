"""Tests for query_call_logs tool."""

import pytest
from unittest.mock import patch, MagicMock
import os
from datetime import datetime

from tools.communication.query_call_logs import QueryCallLogs
from shared.errors import ValidationError, APIError, AuthenticationError


class TestQueryCallLogs:
    """Test suite for QueryCallLogs."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def basic_tool(self) -> QueryCallLogs:
        return QueryCallLogs(limit=10)

    @pytest.fixture
    def mock_call_data(self):
        """Mock Twilio call object."""
        call = MagicMock()
        call.sid = "CA1234567890abcdef1234567890abcdef"
        call.from_ = "+14155551234"
        call.to = "+14155559999"
        call.status = "completed"
        call.duration = 120
        call.start_time = datetime(2024, 1, 15, 10, 0, 0)
        call.end_time = datetime(2024, 1, 15, 10, 2, 0)
        call.direction = "outbound-api"
        call.price = "-0.015"
        call.price_unit = "USD"
        return call

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self):
        tool = QueryCallLogs(
            phone_number="+14155551234",
            start_date="2024-01-01",
            end_date="2024-01-31",
            status="completed",
            limit=50,
        )
        assert tool.phone_number == "+14155551234"
        assert tool.start_date == "2024-01-01"
        assert tool.end_date == "2024-01-31"
        assert tool.status == "completed"
        assert tool.limit == 50
        assert tool.tool_name == "query_call_logs"
        assert tool.tool_category == "communication"

    def test_default_parameters(self):
        tool = QueryCallLogs()
        assert tool.phone_number is None
        assert tool.start_date is None
        assert tool.end_date is None
        assert tool.status is None
        assert tool.limit == 50

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, basic_tool: QueryCallLogs):
        result = basic_tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert len(result["result"]) <= basic_tool.limit
        assert len(result["result"]) > 0

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_with_status_filter(self):
        tool = QueryCallLogs(status="completed", limit=5)
        result = tool.run()
        assert result["success"] is True
        # All mock results should have the specified status
        for call in result["result"]:
            assert call["status"] == "completed"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_with_phone_number_filter(self):
        tool = QueryCallLogs(phone_number="+14155551234", limit=5)
        result = tool.run()
        assert result["success"] is True
        # All mock results should have the specified phone number
        for call in result["result"]:
            assert call["from"] == "+14155551234"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_respects_limit(self):
        tool = QueryCallLogs(limit=3)
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]) <= 3

    # ========== VALIDATION TESTS ==========

    def test_invalid_limit_zero(self):
        # Pydantic validation should catch this at initialization
        with pytest.raises(Exception):  # ValidationError from Pydantic
            tool = QueryCallLogs(limit=0)

    def test_invalid_limit_negative(self):
        # Pydantic validation should catch this at initialization
        with pytest.raises(Exception):  # ValidationError from Pydantic
            tool = QueryCallLogs(limit=-5)

    def test_invalid_limit_exceeds_max(self):
        # Pydantic validation should catch this at initialization
        with pytest.raises(Exception):  # ValidationError from Pydantic
            tool = QueryCallLogs(limit=2000)

    def test_invalid_start_date_format(self):
        tool = QueryCallLogs(start_date="2024/01/01")
        result = tool.run()
        assert result["success"] is False
        error_msg = (
            result.get("error", {}).get("message", "")
            if isinstance(result.get("error"), dict)
            else str(result.get("error", ""))
        )
        assert "start_date must be in ISO format" in error_msg

    def test_invalid_end_date_format(self):
        tool = QueryCallLogs(end_date="01-31-2024")
        result = tool.run()
        assert result["success"] is False
        error_msg = (
            result.get("error", {}).get("message", "")
            if isinstance(result.get("error"), dict)
            else str(result.get("error", ""))
        )
        assert "end_date must be in ISO format" in error_msg

    def test_start_date_after_end_date(self):
        tool = QueryCallLogs(start_date="2024-01-31", end_date="2024-01-01")
        result = tool.run()
        assert result["success"] is False
        error_msg = (
            result.get("error", {}).get("message", "")
            if isinstance(result.get("error"), dict)
            else str(result.get("error", ""))
        )
        assert "start_date must be before or equal to end_date" in error_msg

    def test_invalid_status(self):
        tool = QueryCallLogs(status="invalid-status")
        result = tool.run()
        assert result["success"] is False
        error_msg = (
            result.get("error", {}).get("message", "")
            if isinstance(result.get("error"), dict)
            else str(result.get("error", ""))
        )
        assert "status must be one of" in error_msg

    def test_valid_status_values(self):
        valid_statuses = ["completed", "busy", "failed", "no-answer"]
        for status in valid_statuses:
            tool = QueryCallLogs(status=status, limit=5)
            # Should not raise validation error
            os.environ["USE_MOCK_APIS"] = "true"
            result = tool.run()
            assert result["success"] is True

    # ========== REAL API TESTS (Mocked) ==========
    # Note: These tests are skipped if Twilio is not installed (optional dependency)

    @pytest.mark.skipif(
        not os.getenv("TWILIO_ACCOUNT_SID") or not os.getenv("TWILIO_AUTH_TOKEN"),
        reason="Twilio credentials not set - optional dependency test",
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})  # Use mock mode for testing
    def test_real_api_success_simulation(self, basic_tool):
        # This test uses mock mode to simulate a successful API call
        result = basic_tool.run()

        assert result["success"] is True
        assert len(result["result"]) <= basic_tool.limit
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_validation_in_mock_mode(self):
        # Test that validation works even in mock mode
        tool = QueryCallLogs(start_date="invalid-date")
        result = tool.run()
        assert result["success"] is False

    @pytest.mark.skipif(
        True,  # Always skip this test - requires actual Twilio setup
        reason="Requires real Twilio credentials and API quota - skip in CI/CD",
    )
    def test_twilio_authentication_error(self):
        # Skip if twilio not installed (it's an optional dependency)
        pytest.importorskip("twilio")

        # This test would require real Twilio API interaction
        # Left as placeholder for manual testing with real credentials
        pass

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_phone_number_filter_in_mock_mode(self):
        # Test phone number filtering with mock data
        tool = QueryCallLogs(phone_number="+14155551234", limit=10)
        result = tool.run()

        assert result["success"] is True
        # All results should have the specified phone number as 'from'
        for call in result["result"]:
            assert call["from"] == "+14155551234"

    # ========== EDGE CASE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_valid_date_range(self):
        tool = QueryCallLogs(start_date="2024-01-01", end_date="2024-01-01", limit=5)  # Same day
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_limit_boundary_values(self):
        # Test minimum limit
        tool = QueryCallLogs(limit=1)
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]) <= 1

        # Test maximum limit
        tool = QueryCallLogs(limit=1000)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "status,valid",
        [
            ("completed", True),
            ("busy", True),
            ("failed", True),
            ("no-answer", True),
            ("invalid", False),
            ("pending", False),
        ],
    )
    def test_status_validation(self, status, valid):
        tool = QueryCallLogs(status=status, limit=5)
        if valid:
            os.environ["USE_MOCK_APIS"] = "true"
            result = tool.run()
            assert result["success"] is True
        else:
            result = tool.run()
            assert result["success"] is False

    @pytest.mark.parametrize(
        "start_date,end_date,valid",
        [
            ("2024-01-01", "2024-01-31", True),
            ("2024-01-01", "2024-01-01", True),
            ("2024-12-31", "2024-01-01", False),
            ("2024/01/01", "2024-01-31", False),
            ("2024-01-01", "01-31-2024", False),
        ],
    )
    def test_date_range_validation(self, start_date, end_date, valid):
        tool = QueryCallLogs(start_date=start_date, end_date=end_date, limit=5)
        if valid:
            os.environ["USE_MOCK_APIS"] = "true"
            result = tool.run()
            assert result["success"] is True
        else:
            result = tool.run()
            assert result["success"] is False


class TestQueryCallLogsIntegration:
    """Integration tests with shared components."""

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_basic_run_integration(self):
        tool = QueryCallLogs(limit=5)
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_integration(self):
        tool = QueryCallLogs(
            phone_number="+14155551234",
            start_date="2024-01-01",
            end_date="2024-01-31",
            status="completed",
            limit=10,
        )
        result = tool.run()
        metadata = result["metadata"]

        assert metadata["phone_number"] == "+14155551234"
        assert metadata["start_date"] == "2024-01-01"
        assert metadata["end_date"] == "2024-01-31"
        assert metadata["status"] == "completed"
        assert metadata["limit"] == 10
        assert metadata["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_call_record_structure(self):
        tool = QueryCallLogs(limit=1)
        result = tool.run()

        assert len(result["result"]) > 0
        call = result["result"][0]

        # Verify all required fields are present
        required_fields = [
            "sid",
            "from",
            "to",
            "status",
            "duration",
            "start_time",
            "direction",
            "price",
            "price_unit",
        ]
        for field in required_fields:
            assert field in call, f"Missing required field: {field}"
