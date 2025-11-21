"""Tests for financial_report tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any

from financial_report import FinancialReport
from shared.errors import ValidationError, APIError


class TestFinancialReport:
    """Test suite for FinancialReport."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        """Valid input for the tool."""
        return "Example Corp"

    @pytest.fixture
    def tool(self, valid_input: str) -> FinancialReport:
        """Create tool instance with valid input."""
        return FinancialReport(input=valid_input)

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: FinancialReport):
        """Test successful execution."""
        result = tool.run()
        assert result["success"] is True
        assert "result" in result

    def test_metadata_correct(self, tool: FinancialReport):
        """Test tool metadata."""
        assert tool.tool_name == "financial_report"
        assert tool.tool_category == "search"
        assert (
            tool.tool_description
            == "Search official financial reports, earnings, statements for public companies"
        )

    # ========== ERROR CASES ==========

    def test_validation_error(self):
        """Test validation errors."""
        with pytest.raises(ValidationError):
            tool = FinancialReport(input="")  # Invalid params
            tool.run()

    def test_api_error_handled(self, tool: FinancialReport):
        """Test API error handling."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: FinancialReport):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["company"] == "Mock Company"

    # ========== EDGE CASES ==========

    def test_unicode_input(self):
        """Test Unicode characters in input."""
        tool = FinancialReport(input="公司")
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_in_input(self):
        """Test special characters in input."""
        special_input = "query with @#$%^&* special chars"
        tool = FinancialReport(input=special_input)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "input_value, expected_success",
        [
            ("Valid Company", True),
            ("", False),  # Empty input should fail
            ("   ", False),  # Whitespace input should fail
            ("公司", True),  # Unicode input
            ("query with @#$%^&* special chars", True),  # Special characters
        ],
    )
    def test_input_validation(self, input_value: str, expected_success: bool):
        """Test input validation with various inputs."""
        if expected_success:
            tool = FinancialReport(input=input_value)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(ValidationError):
                tool = FinancialReport(input=input_value)
                tool.run()
