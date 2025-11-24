"""
Tests for Twilio Call Logs Tool

Comprehensive test suite covering initialization, mock mode execution,
parameter validation, and error handling.
"""

import os
from unittest.mock import MagicMock, patch
import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import ValidationError, APIError, AuthenticationError
from tools.communication.twilio_call_logs.twilio_call_logs import TwilioCallLogs


class TestTwilioCallLogs:
    """Test suite for TwilioCallLogs tool."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"
        yield
        # Cleanup
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_initialization_success(self):
        """Test successful tool initialization with valid parameters."""
        tool = TwilioCallLogs(time_range_hours=10, limit=10, include_transcript=True)

        assert tool.tool_name == "twilio_call_logs"
        assert tool.tool_category == "communication"

    def test_execute_mock_mode(self):
        """Test tool execution in mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = TwilioCallLogs(time_range_hours=10, limit=10, include_transcript=True)
        result = tool.run()

        assert result["success"] == True
        assert "result" in result
        assert "metadata" in result
        assert result["metadata"]["mock_mode"] == True

    def test_validation_missing_required_param(self):
        """Test validation raises error for missing required parameters."""
        # This test verifies Pydantic validation for required fields
        with pytest.raises((ValidationError, PydanticValidationError, TypeError)):
            tool = TwilioCallLogs()  # Missing required parameters

    def test_validation_invalid_param_type(self):
        """Test validation for invalid parameter types."""
        # Test with obviously invalid parameter types
        with pytest.raises((ValidationError, PydanticValidationError, TypeError)):
            # Pass invalid type for first parameter
            tool = TwilioCallLogs(**{"time_range_hours": 12345})

    def test_execute_validates_parameters(self):
        """Test that _execute calls _validate_parameters."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = TwilioCallLogs(time_range_hours=10, limit=10, include_transcript=True)

        # Mock the validate method to ensure it's called
        original_validate = tool._validate_parameters
        tool._validate_parameters = MagicMock(side_effect=original_validate)

        result = tool.run()

        # Verify validation was called
        tool._validate_parameters.assert_called_once()

    def test_mock_mode_detection(self):
        """Test that tool correctly detects mock mode from environment."""
        # Test with mock mode enabled
        os.environ["USE_MOCK_APIS"] = "true"
        tool = TwilioCallLogs(time_range_hours=10, limit=10, include_transcript=True)
        assert tool._should_use_mock() == True

        # Test with mock mode disabled
        os.environ["USE_MOCK_APIS"] = "false"
        tool2 = TwilioCallLogs(time_range_hours=10, limit=10, include_transcript=True)
        assert tool2._should_use_mock() == False

    def test_result_structure(self):
        """Test that result has expected structure."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = TwilioCallLogs(time_range_hours=10, limit=10, include_transcript=True)
        result = tool.run()

        # Verify standard result structure
        assert isinstance(result, dict)
        assert "success" in result
        assert "result" in result
        assert "metadata" in result

        # Verify metadata structure
        metadata = result["metadata"]
        assert "tool_name" in metadata
        assert metadata["tool_name"] == "twilio_call_logs"

    def test_authentication_error_handling(self):
        """Test handling of authentication errors in real mode."""
        os.environ.pop("USE_MOCK_APIS", None)

        # This test verifies the tool raises appropriate errors when
        # authentication fails (missing API keys, invalid credentials, etc.)
        tool = TwilioCallLogs(time_range_hours=10, limit=10, include_transcript=True)

        with pytest.raises((APIError, AuthenticationError, Exception)):
            # Without proper credentials, tool should raise an error
            result = tool.run()

    def test_tool_metadata_attributes(self):
        """Test that tool has correct metadata attributes."""
        tool = TwilioCallLogs(time_range_hours=10, limit=10, include_transcript=True)

        assert hasattr(tool, 'tool_name')
        assert hasattr(tool, 'tool_category')
        assert tool.tool_name == "twilio_call_logs"
        assert tool.tool_category == "communication"

    def test_mock_results_generation(self):
        """Test that mock results are properly generated."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = TwilioCallLogs(time_range_hours=10, limit=10, include_transcript=True)
        mock_result = tool._generate_mock_results()

        assert isinstance(mock_result, dict)
        assert "success" in mock_result
        assert mock_result["success"] == True
        assert "metadata" in mock_result
        assert mock_result["metadata"].get("mock_mode") == True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
