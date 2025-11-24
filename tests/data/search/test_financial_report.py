"""Comprehensive tests for financial_report tool."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.data.search.financial_report.financial_report import FinancialReport


class TestFinancialReport:
    """Test suite for FinancialReport."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_ticker(self) -> str:
        """Valid test ticker."""
        return "AAPL"

    @pytest.fixture
    def tool(self, valid_ticker: str) -> FinancialReport:
        """Create FinancialReport instance with valid parameters."""
        return FinancialReport(ticker=valid_ticker, report_type="income_statement")

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, valid_ticker: str):
        """Test successful execution."""
        tool = FinancialReport(ticker=valid_ticker, report_type="income_statement")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["ticker"] == valid_ticker

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_all_report_types(self, valid_ticker: str):
        """Test all valid report types."""
        report_types = ["income_statement", "balance_sheet", "cash_flow", "earnings"]
        for report_type in report_types:
            tool = FinancialReport(ticker=valid_ticker, report_type=report_type)
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["report_type"] == report_type

    # ========== TICKER VALIDATION ==========

    def test_empty_ticker_rejected(self):
        """Test that empty ticker is rejected."""
        with pytest.raises(PydanticValidationError):
            FinancialReport(ticker="", report_type="income_statement")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_whitespace_ticker_rejected(self):
        """Test that whitespace-only ticker is rejected."""
        tool = FinancialReport(ticker="   ", report_type="income_statement")
        with pytest.raises(ValidationError, match="Ticker cannot be empty"):
            tool.run()

    def test_ticker_max_length(self):
        """Test ticker maximum length validation."""
        # 10 chars should work
        tool = FinancialReport(ticker="A" * 10, report_type="income_statement")
        assert tool.ticker == "A" * 10

        # 11 chars should fail
        with pytest.raises(PydanticValidationError):
            FinancialReport(ticker="A" * 11, report_type="income_statement")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_common_tickers(self):
        """Test common stock tickers."""
        tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"]
        for ticker in tickers:
            tool = FinancialReport(ticker=ticker, report_type="income_statement")
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["ticker"] == ticker

    # ========== REPORT TYPE VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_invalid_report_type_rejected(self, valid_ticker: str):
        """Test that invalid report type is rejected."""
        tool = FinancialReport(ticker=valid_ticker, report_type="invalid_type")
        with pytest.raises(ValidationError, match="Report type must be one of"):
            tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_default_report_type(self, valid_ticker: str):
        """Test default report type."""
        tool = FinancialReport(ticker=valid_ticker)
        assert tool.report_type == "income_statement"

    # ========== ERROR HANDLING ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_handling(self, valid_ticker: str):
        """Test handling of API errors."""
        tool = FinancialReport(ticker=valid_ticker, report_type="income_statement")
        with patch.object(tool, "_process", side_effect=Exception("API error")):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_enabled(self, valid_ticker: str):
        """Test that mock mode returns mock data."""
        tool = FinancialReport(ticker=valid_ticker, report_type="income_statement")
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    # ========== RESULT FORMAT VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_result_format(self, valid_ticker: str):
        """Test that results have correct format."""
        tool = FinancialReport(ticker=valid_ticker, report_type="income_statement")
        result = tool.run()

        assert "success" in result
        assert "result" in result
        assert "metadata" in result

        # Check result data structure
        data = result["result"]
        assert "ticker" in data
        assert "company" in data
        assert "report_type" in data
        assert "year" in data
        assert "data" in data

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_financial_data_structure(self, valid_ticker: str):
        """Test financial data structure."""
        tool = FinancialReport(ticker=valid_ticker, report_type="income_statement")
        result = tool.run()

        financial_data = result["result"]["data"]
        assert "revenue" in financial_data
        assert "expenses" in financial_data
        assert "net_income" in financial_data

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "ticker,report_type,expected_valid",
        [
            ("AAPL", "income_statement", True),
            ("GOOGL", "balance_sheet", True),
            ("MSFT", "cash_flow", True),
            ("AMZN", "earnings", True),
            ("", "income_statement", False),  # Empty ticker
            ("AAPL", "invalid_report", False),  # Invalid report type
            ("A" * 11, "income_statement", False),  # Ticker too long
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_parameter_combinations(self, ticker: str, report_type: str, expected_valid: bool):
        """Test various parameter combinations."""
        if expected_valid:
            tool = FinancialReport(ticker=ticker, report_type=report_type)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = FinancialReport(ticker=ticker, report_type=report_type)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow(self):
        """Test complete workflow for financial report."""
        # Create tool
        tool = FinancialReport(ticker="AAPL", report_type="income_statement")

        # Verify parameters
        assert tool.ticker == "AAPL"
        assert tool.report_type == "income_statement"
        assert tool.tool_name == "financial_report"
        assert tool.tool_category == "data"

        # Execute
        result = tool.run()

        # Verify results
        assert result["success"] is True
        assert result["result"]["ticker"] == "AAPL"
        assert result["result"]["report_type"] == "income_statement"

    # ========== TOOL METADATA TESTS ==========

    def test_tool_category(self, tool: FinancialReport):
        """Test tool category is correct."""
        assert tool.tool_category == "data"

    def test_tool_name(self, tool: FinancialReport):
        """Test tool name is correct."""
        assert tool.tool_name == "financial_report"
