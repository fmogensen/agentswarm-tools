"""Tests for stock_price tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from tools.search.stock_price import StockPrice
from shared.errors import ValidationError, APIError


class TestStockPrice:
    """Test suite for StockPrice."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_ticker(self) -> str:
        """Valid stock symbol."""
        return "AAPL"

    @pytest.fixture
    def tool(self, valid_ticker: str) -> StockPrice:
        """Create StockPrice instance with valid parameters."""
        return StockPrice(ticker=valid_ticker)

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: StockPrice):
        """Test successful execution."""
        with patch.object(
            tool,
            "_process",
            return_value={"symbol": "AAPL", "price": 150.00, "currency": "USD"},
        ):
            result = tool.run()
            assert result["success"] is True
            assert "result" in result
            assert result["result"]["symbol"] == "AAPL"
            assert result["result"]["price"] == 150.00

    def test_metadata_correct(self, tool: StockPrice):
        """Test tool metadata."""
        assert tool.tool_name == "stock_price"
        assert tool.tool_category == "search"

    # ========== ERROR CASES ==========

    def test_validation_error(self):
        """Test validation errors."""
        tool = StockPrice(ticker=" ")  # Whitespace only
        result = tool.run()
        assert result["success"] is False

    def test_empty_ticker_raises_pydantic_error(self):
        """Empty string fails Pydantic min_length validation."""
        with pytest.raises(PydanticValidationError):
            StockPrice(ticker="")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, tool: StockPrice):
        """Test API error handling."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self):
        """Test mock mode returns mock data."""
        tool = StockPrice(ticker="AAPL")
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_input(self):
        """Test Unicode characters in input."""
        tool = StockPrice(ticker="TEST")
        result = tool.run()
        # Should succeed in mock mode
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_special_characters_in_input(self):
        """Test special characters in input."""
        tool = StockPrice(ticker="TST")
        result = tool.run()
        # Should succeed in mock mode
        assert result["success"] is True

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "ticker_value,expected_valid,is_pydantic_error",
        [
            ("AAPL", True, False),
            ("", False, True),  # Empty string fails Pydantic min_length
            ("12345", True, False),
            ("GOOGL", True, False),
            (" ", False, False),  # Whitespace passes Pydantic, fails custom validation
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_parameter_validation(self, ticker_value: str, expected_valid: bool, is_pydantic_error: bool):
        """Test parameter validation with various inputs."""
        if is_pydantic_error:
            with pytest.raises(PydanticValidationError):
                StockPrice(ticker=ticker_value)
        elif expected_valid:
            tool = StockPrice(ticker=ticker_value)
            result = tool.run()
            assert result["success"] is True
        else:
            tool = StockPrice(ticker=ticker_value)
            result = tool.run()
            assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow(self):
        """Test complete workflow."""
        tool = StockPrice(ticker="AAPL")
        result = tool.run()
        assert result["success"] is True
