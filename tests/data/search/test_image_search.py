"""Comprehensive tests for image_search tool."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.data.search.image_search.image_search import ImageSearch


class TestImageSearch:
    """Test suite for ImageSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        """Valid test query."""
        return "sunset landscape"

    @pytest.fixture
    def tool(self, valid_query: str) -> ImageSearch:
        """Create ImageSearch instance with valid parameters."""
        return ImageSearch(query=valid_query, max_results=5)

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, valid_query: str):
        """Test successful execution."""
        tool = ImageSearch(query=valid_query, max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["total_count"] == 5

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_correct(self, valid_query: str):
        """Test tool metadata."""
        tool = ImageSearch(query=valid_query, max_results=5)
        result = tool.run()
        assert result["metadata"]["tool_name"] == "image_search"
        assert result["metadata"]["query"] == valid_query

    # ========== QUERY VALIDATION ==========

    def test_empty_query_rejected(self):
        """Test that empty query is rejected."""
        with pytest.raises(PydanticValidationError):
            ImageSearch(query="", max_results=10)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_whitespace_query_rejected(self):
        """Test that whitespace-only query is rejected."""
        tool = ImageSearch(query="   ", max_results=10)
        with pytest.raises(ValidationError, match="Query cannot be empty"):
            tool.run()

    def test_query_max_length(self):
        """Test query maximum length validation."""
        # 500 chars should work
        long_query = "a" * 500
        tool = ImageSearch(query=long_query, max_results=5)
        assert tool.query == long_query

        # 501 chars should fail
        with pytest.raises(PydanticValidationError):
            ImageSearch(query="a" * 501, max_results=5)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_visual_search_queries(self):
        """Test various visual/image search queries."""
        queries = [
            "sunset beach",
            "mountain landscape",
            "city skyline night",
            "abstract art",
            "product photography",
            "portrait photo",
        ]
        for query in queries:
            tool = ImageSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    # ========== RESULT LIMIT BOUNDARIES ==========

    def test_min_results_boundary(self):
        """Test minimum results limit (1)."""
        tool = ImageSearch(query="test", max_results=1)
        assert tool.max_results == 1

    def test_max_results_boundary(self):
        """Test maximum results limit (100)."""
        tool = ImageSearch(query="test", max_results=100)
        assert tool.max_results == 100

    def test_zero_results_rejected(self):
        """Test that 0 results is rejected."""
        with pytest.raises(PydanticValidationError):
            ImageSearch(query="test", max_results=0)

    def test_negative_results_rejected(self):
        """Test that negative results is rejected."""
        with pytest.raises(PydanticValidationError):
            ImageSearch(query="test", max_results=-5)

    def test_exceeds_max_results_rejected(self):
        """Test that results > 100 is rejected."""
        with pytest.raises(PydanticValidationError):
            ImageSearch(query="test", max_results=101)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_results_count_matches_limit(self):
        """Test that returned results match requested limit."""
        for limit in [1, 5, 10, 20]:
            tool = ImageSearch(query="test", max_results=limit)
            result = tool.run()
            assert result["result"]["total_count"] == limit

    # ========== ERROR HANDLING ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_missing_api_key(self, valid_query: str):
        """Test error when API key is missing."""
        tool = ImageSearch(query=valid_query, max_results=5)
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(APIError, match="SERPAPI_KEY"):
                tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_request_failure(self, valid_query: str):
        """Test handling of API request failures."""
        tool = ImageSearch(query=valid_query, max_results=5)
        with patch("requests.get", side_effect=Exception("Network error")):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_enabled(self, valid_query: str):
        """Test that mock mode returns mock data."""
        tool = ImageSearch(query=valid_query, max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_mock_mode_disabled(self, valid_query: str):
        """Test that mock mode can be disabled."""
        tool = ImageSearch(query=valid_query, max_results=5)
        assert not tool._should_use_mock()

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_query(self):
        """Test Unicode characters in query."""
        queries = [
            "café Paris",
            "日本 landscape",
            "Москва архитектура",
        ]
        for query in queries:
            tool = ImageSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_color_and_size_filters(self):
        """Test queries with color and size specifications."""
        queries = [
            "red car",
            "blue ocean",
            "large format landscape",
            "high resolution portrait",
        ]
        for query in queries:
            tool = ImageSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    # ========== RESULT FORMAT VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_result_format(self, valid_query: str):
        """Test that results have correct image format."""
        tool = ImageSearch(query=valid_query, max_results=5)
        result = tool.run()

        assert "success" in result
        assert "result" in result
        assert "images" in result["result"]
        assert "total_count" in result["result"]
        assert isinstance(result["result"]["images"], list)

        # Check individual image format
        for image in result["result"]["images"]:
            assert "position" in image
            assert "title" in image
            assert "image_url" in image
            assert "thumbnail_url" in image
            assert "dimensions" in image
            assert "width" in image["dimensions"]
            assert "height" in image["dimensions"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_image_urls_format(self, valid_query: str):
        """Test that image URLs are properly formatted."""
        tool = ImageSearch(query=valid_query, max_results=5)
        result = tool.run()

        for image in result["result"]["images"]:
            assert image["image_url"].startswith("http")
            assert image["thumbnail_url"].startswith("http")

    # ========== CACHING TESTS ==========

    def test_cache_configuration(self, valid_query: str):
        """Test that caching is properly configured."""
        tool = ImageSearch(query=valid_query, max_results=5)
        assert tool.enable_cache is True
        assert tool.cache_ttl == 3600
        assert "query" in tool.cache_key_params
        assert "max_results" in tool.cache_key_params

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow(self):
        """Test complete workflow for image search."""
        # Create tool
        tool = ImageSearch(query="nature photography", max_results=10)

        # Verify parameters
        assert tool.query == "nature photography"
        assert tool.max_results == 10
        assert tool.tool_name == "image_search"
        assert tool.tool_category == "data"

        # Execute
        result = tool.run()

        # Verify results
        assert result["success"] is True
        assert result["result"]["total_count"] == 10
        assert len(result["result"]["images"]) == 10

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "query,max_results,expected_valid",
        [
            ("valid query", 10, True),
            ("a" * 500, 10, True),  # Max length
            ("short", 1, True),  # Min results
            ("test", 100, True),  # Max results
            ("", 10, False),  # Empty query
            ("a" * 501, 10, False),  # Exceeds max length
            ("test", 0, False),  # Zero results
            ("test", 101, False),  # Exceeds max results
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_parameter_combinations(self, query: str, max_results: int, expected_valid: bool):
        """Test various parameter combinations."""
        if expected_valid:
            tool = ImageSearch(query=query, max_results=max_results)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = ImageSearch(query=query, max_results=max_results)
                tool.run()

    # ========== TOOL METADATA TESTS ==========

    def test_tool_category(self, tool: ImageSearch):
        """Test tool category is correct."""
        assert tool.tool_category == "data"

    def test_tool_name(self, tool: ImageSearch):
        """Test tool name is correct."""
        assert tool.tool_name == "image_search"
