"""Tests for stock_price tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from tools.search.stock_price import StockPrice
from shared.errors import ValidationError, APIError


class TestStockPrice:
    """Test suite for StockPrice."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        """Valid stock symbol."""
        return "AAPL"

    @pytest.fixture
    def tool(self, valid_input: str) -> StockPrice:
        """Create StockPrice instance with valid parameters."""
        return StockPrice(input=valid_input)

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
        with pytest.raises(ValidationError):
            tool = StockPrice(input="")  # Invalid params
            tool.run()

    def test_api_error_handled(self, tool: StockPrice):
        """Test API error handling."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: StockPrice):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    # ========== EDGE CASES ==========

    def test_unicode_input(self):
        """Test Unicode characters in input."""
        tool = StockPrice(input="テスト")
        with pytest.raises(APIError):
            tool.run()

    def test_special_characters_in_input(self):
        """Test special characters in input."""
        tool = StockPrice(input="@#$%^&*")
        with pytest.raises(APIError):
            tool.run()

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "input_value,expected_valid",
        [
            ("AAPL", True),
            ("", False),
            ("12345", True),
            ("a" * 500, True),  # Max length
            (" ", False),  # Only spaces
        ],
    )
    def test_parameter_validation(self, input_value: str, expected_valid: bool):
        """Test parameter validation with various inputs."""
        if expected_valid:
            tool = StockPrice(input=input_value)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(ValidationError):
                tool = StockPrice(input=input_value)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_full_workflow(self, valid_input: str):
        """Test complete workflow."""
        tool = StockPrice(input=valid_input)
        with patch.object(
            tool,
            "_process",
            return_value={"symbol": "AAPL", "price": 150.00, "currency": "USD"},
        ):
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["symbol"] == "AAPL"
