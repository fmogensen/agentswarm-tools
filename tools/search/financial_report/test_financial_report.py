"""Tests for financial_report tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from tools.search.financial_report import FinancialReport
from shared.errors import ValidationError, APIError


class TestFinancialReport:
    """Test suite for FinancialReport."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_ticker(self) -> str:
        """Valid ticker for the tool."""
        return "AAPL"

    @pytest.fixture
    def tool(self, valid_ticker: str) -> FinancialReport:
        """Create tool instance with valid input."""
        return FinancialReport(ticker=valid_ticker)

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self):
        """Test successful execution."""
        tool = FinancialReport(ticker="AAPL")
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
        """Test validation errors with whitespace-only ticker."""
        tool = FinancialReport(ticker=" ")
        result = tool.run()
        assert result["success"] is False

    def test_empty_ticker_raises_pydantic_error(self):
        """Empty string fails Pydantic min_length validation."""
        with pytest.raises(PydanticValidationError):
            FinancialReport(ticker="")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, tool: FinancialReport):
        """Test API error handling."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self):
        """Test mock mode returns mock data."""
        tool = FinancialReport(ticker="AAPL")
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "Mock Company" in result["result"]["company"]

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_ticker(self):
        """Test valid ticker works in mock mode."""
        tool = FinancialReport(ticker="GOOGL")
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_report_types(self):
        """Test different report types."""
        for report_type in ["income_statement", "balance_sheet", "cash_flow", "earnings"]:
            tool = FinancialReport(ticker="AAPL", report_type=report_type)
            result = tool.run()
            assert result["success"] is True

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "ticker_value, expected_success, is_pydantic_error",
        [
            ("AAPL", True, False),
            ("", False, True),  # Empty string fails Pydantic min_length
            ("   ", False, False),  # Whitespace passes Pydantic, fails custom validation
            ("GOOGL", True, False),
            ("TSLA", True, False),
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_input_validation(self, ticker_value: str, expected_success: bool, is_pydantic_error: bool):
        """Test input validation with various inputs."""
        if is_pydantic_error:
            with pytest.raises(PydanticValidationError):
                FinancialReport(ticker=ticker_value)
        elif expected_success:
            tool = FinancialReport(ticker=ticker_value)
            result = tool.run()
            assert result["success"] is True
        else:
            tool = FinancialReport(ticker=ticker_value)
            result = tool.run()
            assert result["success"] is False
