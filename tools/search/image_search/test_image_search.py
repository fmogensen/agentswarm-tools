"""Tests for image_search tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from tools.search.image_search import ImageSearch
from shared.errors import ValidationError, APIError


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
        return ImageSearch(query=valid_query, max_results=10)

    @pytest.fixture
    def mock_results(self) -> Dict[str, Any]:
        """Mock API results."""
        return {
            "images": [
                {
                    "position": i,
                    "title": f"Mock Image {i}",
                    "image_url": f"https://example.com/images/mock_{i}.jpg",
                    "thumbnail_url": f"https://example.com/thumbnails/mock_{i}_thumb.jpg",
                    "source_page": f"https://example.com/page/{i}",
                    "dimensions": {"width": 1920, "height": 1080},
                    "format": "JPEG",
                    "file_size": "245 KB",
                }
                for i in range(1, 11)
            ],
            "total_count": 10
        }

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: ImageSearch, mock_results: Dict[str, Any]):
        """Test successful execution."""
        with patch.object(
            tool, "_process", return_value=mock_results
        ):
            result = tool.run()
            assert result["success"] is True
            assert "result" in result
            assert result["result"]["total_count"] == 10
            assert len(result["result"]["images"]) == 10

    def test_metadata_correct(self, tool: ImageSearch):
        """Test tool metadata."""
        assert tool.tool_name == "image_search"
        assert tool.tool_category == "search"

    # ========== ERROR CASES ==========

    def test_validation_error_empty_query(self):
        """Test validation error with empty query."""
        with pytest.raises(ValidationError):
            tool = ImageSearch(query="", max_results=10)
            tool.run()

    def test_validation_error_whitespace_query(self):
        """Test validation error with whitespace-only query."""
        with pytest.raises(ValidationError):
            tool = ImageSearch(query="   ", max_results=10)
            tool.run()

    def test_api_error_handled(self, tool: ImageSearch):
        """Test API error handling."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: ImageSearch):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "images" in result["result"]
        assert result["result"]["total_count"] > 0

    # ========== EDGE CASES ==========

    def test_unicode_query(self, mock_results: Dict[str, Any]):
        """Test Unicode characters in query."""
        tool = ImageSearch(query="日本の風景", max_results=5)
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["query"] == "日本の風景"

    def test_special_characters_in_query(self, mock_results: Dict[str, Any]):
        """Test special characters in query."""
        special_query = "query with @#$%^&* special chars"
        tool = ImageSearch(query=special_query, max_results=5)
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["query"] == special_query

    def test_max_results_boundary(self, mock_results: Dict[str, Any]):
        """Test max_results boundary values."""
        # Test minimum
        tool = ImageSearch(query="test", max_results=1)
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["max_results"] == 1

        # Test maximum
        tool = ImageSearch(query="test", max_results=100)
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["max_results"] == 100

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "query,max_results,expected_valid",
        [
            ("valid query", 10, True),
            ("a" * 500, 10, True),  # Max length
            ("", 10, False),  # Empty query
            ("   ", 10, False),  # Whitespace only
            ("test", 0, False),  # Invalid max_results
            ("test", 101, False),  # Max_results too high
            ("test", -1, False),  # Negative max_results
        ],
    )
    def test_parameter_validation(
        self, query: str, max_results: int, expected_valid: bool
    ):
        """Test parameter validation with various inputs."""
        if expected_valid:
            tool = ImageSearch(query=query, max_results=max_results)
            assert tool.query == query
            assert tool.max_results == max_results
        else:
            with pytest.raises(Exception):  # Could be ValidationError or Pydantic error
                tool = ImageSearch(query=query, max_results=max_results)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_full_workflow(self, mock_results: Dict[str, Any]):
        """Test complete workflow."""
        tool = ImageSearch(query="python programming", max_results=5)
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert result["success"] is True
            assert "images" in result["result"]
            assert result["metadata"]["tool_name"] == "image_search"
            assert result["metadata"]["query"] == "python programming"
            assert result["metadata"]["max_results"] == 5

    def test_result_structure(self, tool: ImageSearch, mock_results: Dict[str, Any]):
        """Test that result structure matches expected format."""
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert "success" in result
            assert "result" in result
            assert "metadata" in result

            # Check result structure
            assert "images" in result["result"]
            assert "total_count" in result["result"]

            # Check first image structure
            if result["result"]["images"]:
                first_image = result["result"]["images"][0]
                assert "position" in first_image
                assert "title" in first_image
                assert "image_url" in first_image
                assert "thumbnail_url" in first_image
                assert "source_page" in first_image
                assert "dimensions" in first_image
                assert "format" in first_image
