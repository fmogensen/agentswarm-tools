"""Tests for product_search tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from tools.search.product_search import ProductSearch
from shared.errors import ValidationError, APIError


class TestProductSearch:
    """Test suite for ProductSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_search_query(self) -> str:
        """Valid test search query."""
        return "wireless headphones"

    @pytest.fixture
    def valid_asin(self) -> str:
        """Valid test ASIN."""
        return "B08N5WRWNW"

    @pytest.fixture
    def search_tool(self, valid_search_query: str) -> ProductSearch:
        """Create ProductSearch instance for product search."""
        return ProductSearch(type="product_search", query=valid_search_query)

    @pytest.fixture
    def detail_tool(self, valid_asin: str) -> ProductSearch:
        """Create ProductSearch instance for product detail."""
        return ProductSearch(type="product_detail", ASIN=valid_asin)

    @pytest.fixture
    def mock_search_results(self) -> Dict[str, Any]:
        """Mock product search results."""
        return {
            "search_query": "wireless headphones",
            "products": [
                {
                    "ASIN": f"B08MOCK{i:03d}",
                    "title": f"Mock Product {i}",
                    "price": f"${29.99 + i * 10}",
                    "rating": 4.5,
                    "review_count": 1000 + i * 100,
                    "images": [f"https://example.com/image{i}.jpg"],
                    "availability": "In Stock",
                    "prime": True
                }
                for i in range(1, 6)
            ],
            "total_results": 5
        }

    @pytest.fixture
    def mock_detail_results(self) -> Dict[str, Any]:
        """Mock product detail results."""
        return {
            "ASIN": "B08N5WRWNW",
            "title": "Mock Product Detail",
            "price": "$49.99",
            "rating": 4.5,
            "review_count": 2500,
            "images": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg"
            ],
            "availability": "In Stock",
            "prime": True,
            "description": "This is a detailed mock product description.",
            "specifications": {
                "Brand": "Mock Brand",
                "Color": "Black",
                "Weight": "1.5 pounds"
            },
            "customer_reviews": [
                {
                    "rating": 5,
                    "title": "Great product!",
                    "text": "Mock review text.",
                    "verified": True
                }
            ],
            "related_products": [
                {
                    "ASIN": "B08RELATED1",
                    "title": "Related Product 1",
                    "price": "$39.99"
                }
            ]
        }

    # ========== HAPPY PATH ==========

    def test_execute_product_search_success(
        self, search_tool: ProductSearch, mock_search_results: Dict[str, Any]
    ):
        """Test successful product search execution."""
        with patch.object(search_tool, "_process", return_value=mock_search_results):
            result = search_tool.run()
            assert result["success"] is True
            assert "result" in result
            assert "products" in result["result"]
            assert len(result["result"]["products"]) == 5

    def test_execute_product_detail_success(
        self, detail_tool: ProductSearch, mock_detail_results: Dict[str, Any]
    ):
        """Test successful product detail execution."""
        with patch.object(detail_tool, "_process", return_value=mock_detail_results):
            result = detail_tool.run()
            assert result["success"] is True
            assert "result" in result
            assert result["result"]["ASIN"] == "B08N5WRWNW"
            assert "specifications" in result["result"]

    def test_metadata_correct(self, search_tool: ProductSearch):
        """Test tool metadata."""
        assert search_tool.tool_name == "product_search"
        assert search_tool.tool_category == "search"

    # ========== ERROR CASES ==========

    def test_validation_error_invalid_type(self):
        """Test validation error with invalid type."""
        with pytest.raises(ValidationError):
            tool = ProductSearch(type="invalid_type", query="test")
            tool.run()

    def test_validation_error_search_missing_query(self):
        """Test validation error when query missing for product_search."""
        with pytest.raises(ValidationError):
            tool = ProductSearch(type="product_search")
            tool.run()

    def test_validation_error_detail_missing_asin(self):
        """Test validation error when ASIN missing for product_detail."""
        with pytest.raises(ValidationError):
            tool = ProductSearch(type="product_detail")
            tool.run()

    def test_api_error_handled(self, search_tool: ProductSearch):
        """Test API error handling."""
        with patch.object(search_tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                search_tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_product_search(self, search_tool: ProductSearch):
        """Test mock mode for product search."""
        result = search_tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "products" in result["result"]
        assert len(result["result"]["products"]) > 0

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_product_detail(self, detail_tool: ProductSearch):
        """Test mock mode for product detail."""
        result = detail_tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "ASIN" in result["result"]
        assert "specifications" in result["result"]

    # ========== EDGE CASES ==========

    def test_unicode_query(self, mock_search_results: Dict[str, Any]):
        """Test Unicode characters in query."""
        tool = ProductSearch(type="product_search", query="无线耳机")
        with patch.object(tool, "_process", return_value=mock_search_results):
            result = tool.run()
            assert result["success"] is True

    def test_special_characters_in_query(self, mock_search_results: Dict[str, Any]):
        """Test special characters in query."""
        special_query = "headphones @#$% special"
        tool = ProductSearch(type="product_search", query=special_query)
        with patch.object(tool, "_process", return_value=mock_search_results):
            result = tool.run()
            assert result["success"] is True

    def test_location_domain_parameter(self, mock_search_results: Dict[str, Any]):
        """Test location_domain parameter."""
        tool = ProductSearch(
            type="product_search",
            query="test",
            location_domain="co.uk"
        )
        with patch.object(tool, "_process", return_value=mock_search_results):
            result = tool.run()
            assert result["success"] is True
            assert tool.location_domain == "co.uk"

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "type_value,query,asin,expected_valid",
        [
            ("product_search", "valid query", None, True),
            ("product_detail", None, "B08N5WRWNW", True),
            ("invalid_type", "query", None, False),
            ("product_search", None, None, False),  # Missing query
            ("product_detail", None, None, False),  # Missing ASIN
        ],
    )
    def test_parameter_validation(
        self, type_value: str, query: str, asin: str, expected_valid: bool
    ):
        """Test parameter validation with various inputs."""
        if expected_valid:
            tool = ProductSearch(type=type_value, query=query, ASIN=asin)
            assert tool.type == type_value
        else:
            with pytest.raises(Exception):  # Could be ValidationError or Pydantic error
                tool = ProductSearch(type=type_value, query=query, ASIN=asin)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_full_workflow_search(self, mock_search_results: Dict[str, Any]):
        """Test complete workflow for product search."""
        tool = ProductSearch(
            type="product_search",
            query="bluetooth speaker",
            location_domain="com"
        )
        with patch.object(tool, "_process", return_value=mock_search_results):
            result = tool.run()
            assert result["success"] is True
            assert "products" in result["result"]
            assert result["metadata"]["tool_name"] == "product_search"

    def test_full_workflow_detail(self, mock_detail_results: Dict[str, Any]):
        """Test complete workflow for product detail."""
        tool = ProductSearch(
            type="product_detail",
            ASIN="B08N5WRWNW",
            location_domain="com"
        )
        with patch.object(tool, "_process", return_value=mock_detail_results):
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["ASIN"] == "B08N5WRWNW"
            assert result["metadata"]["tool_name"] == "product_search"

    def test_search_result_structure(
        self, search_tool: ProductSearch, mock_search_results: Dict[str, Any]
    ):
        """Test that search result structure matches expected format."""
        with patch.object(search_tool, "_process", return_value=mock_search_results):
            result = search_tool.run()
            assert "success" in result
            assert "result" in result
            assert "metadata" in result

            # Check result structure
            assert "products" in result["result"]

            # Check first product structure
            if result["result"]["products"]:
                first_product = result["result"]["products"][0]
                assert "ASIN" in first_product
                assert "title" in first_product
                assert "price" in first_product
                assert "rating" in first_product
                assert "review_count" in first_product
                assert "images" in first_product
                assert "availability" in first_product
                assert "prime" in first_product

    def test_detail_result_structure(
        self, detail_tool: ProductSearch, mock_detail_results: Dict[str, Any]
    ):
        """Test that detail result structure matches expected format."""
        with patch.object(detail_tool, "_process", return_value=mock_detail_results):
            result = detail_tool.run()

            # Check extended detail fields
            assert "description" in result["result"]
            assert "specifications" in result["result"]
            assert "customer_reviews" in result["result"]
            assert "related_products" in result["result"]
