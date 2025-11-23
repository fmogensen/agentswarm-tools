"""Tests for google_product_search tool."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.search.google_product_search import GoogleProductSearch


class TestGoogleProductSearch:
    """Test suite for GoogleProductSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        """Valid test query."""
        return "wireless headphones"

    @pytest.fixture
    def tool(self, valid_query: str) -> GoogleProductSearch:
        """Create GoogleProductSearch instance with valid parameters."""
        return GoogleProductSearch(query=valid_query, num=5, page=0)

    @pytest.fixture
    def mock_products(self) -> list:
        """Mock product results."""
        return [
            {
                "product_name": f"Mock Product {i}",
                "price": f"${99 + i}.99",
                "merchant": f"Mock Store {i % 3 + 1}",
                "product_url": f"https://example.com/product/{i}",
                "image": f"https://example.com/images/product{i}.jpg",
                "shipping": "Free shipping" if i % 2 == 0 else "$5.99",
                "rating": round(4.0 + (i % 10) / 10, 1),
                "review_count": (i + 1) * 100,
            }
            for i in range(1, 6)
        ]

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: GoogleProductSearch):
        """Test successful execution."""
        with patch.object(tool, "_process", return_value=tool._generate_mock_results()["result"]):
            result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "products" in result["result"]

    def test_metadata_correct(self, tool: GoogleProductSearch):
        """Test tool metadata."""
        assert tool.tool_name == "google_product_search"
        assert tool.tool_category == "search"

    def test_default_parameters(self):
        """Test default parameter values."""
        tool = GoogleProductSearch(query="laptop")
        assert tool.num == 100
        assert tool.page == 0

    # ========== ERROR CASES ==========

    def test_validation_error_empty_query(self):
        """Test validation error for empty query."""
        with pytest.raises(PydanticValidationError):
            GoogleProductSearch(query="", num=10)

    def test_validation_error_invalid_num(self):
        """Test validation error for invalid num parameter."""
        with pytest.raises(PydanticValidationError):
            GoogleProductSearch(query="laptop", num=101)

        with pytest.raises(PydanticValidationError):
            GoogleProductSearch(query="laptop", num=0)

    def test_validation_error_invalid_page(self):
        """Test validation error for invalid page parameter."""
        with pytest.raises(PydanticValidationError):
            GoogleProductSearch(query="laptop", page=-1)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, tool: GoogleProductSearch):
        """Test API error handling."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
        assert result["success"] is False
        error_msg = (
            result.get("error", {}).get("message", "")
            if isinstance(result.get("error"), dict)
            else str(result.get("error", ""))
        )
        assert len(error_msg) > 0

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GoogleProductSearch, mock_products: list):
        """Test mock mode returns mock data."""
        with patch.object(
            tool,
            "_generate_mock_results",
            return_value={
                "success": True,
                "result": {"products": mock_products, "total_results": 5},
                "metadata": {"mock_mode": True, "page": 0},
            },
        ):
            result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert len(result["result"]["products"]) == 5

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_query(self):
        """Test Unicode characters in query."""
        tool = GoogleProductSearch(query="笔记本电脑", num=5)
        with patch.object(tool, "_process", return_value=tool._generate_mock_results()["result"]):
            result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["tool_name"] == "google_product_search"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_special_characters_in_query(self):
        """Test special characters in query."""
        special_query = "laptop @#$%^&* special"
        tool = GoogleProductSearch(query=special_query, num=5)
        with patch.object(tool, "_process", return_value=tool._generate_mock_results()["result"]):
            result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["tool_name"] == "google_product_search"

    def test_pagination(self):
        """Test pagination with different page numbers."""
        for page in [0, 1, 2, 5, 10]:
            tool = GoogleProductSearch(query="laptop", num=10, page=page)
            with patch.object(
                tool, "_process", return_value=tool._generate_mock_results()["result"]
            ):
                result = tool.run()
                assert result["success"] is True
                assert result["metadata"]["page"] == page

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "query,num,page,expected_valid",
        [
            ("valid query", 10, 0, True),
            ("laptop", 100, 0, True),  # Max num
            ("", 10, 0, False),  # Empty query
            ("test", 0, 0, False),  # Invalid num
            ("test", 101, 0, False),  # Num too high
            ("test", 10, -1, False),  # Invalid page
            ("test", 50, 5, True),  # Valid pagination
        ],
    )
    def test_parameter_validation(self, query: str, num: int, page: int, expected_valid: bool):
        """Test parameter validation with various inputs."""
        if expected_valid:
            tool = GoogleProductSearch(query=query, num=num, page=page)
            assert tool.query == query
            assert tool.num == num
            assert tool.page == page
        else:
            with pytest.raises(Exception):  # Could be ValidationError or Pydantic error
                tool = GoogleProductSearch(query=query, num=num, page=page)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow(self):
        """Test complete workflow."""
        tool = GoogleProductSearch(query="gaming mouse", num=10, page=0)
        with patch.object(tool, "_process", return_value=tool._generate_mock_results()["result"]):
            result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "products" in result["result"]
        assert result["metadata"]["tool_name"] == "google_product_search"
        assert result["metadata"]["page"] == 0

    def test_multiple_pages_workflow(self):
        """Test workflow with multiple pages."""
        query = "laptop"
        for page in range(3):
            tool = GoogleProductSearch(query=query, num=10, page=page)
            with patch.object(
                tool, "_process", return_value=tool._generate_mock_results()["result"]
            ):
                result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["page"] == page
