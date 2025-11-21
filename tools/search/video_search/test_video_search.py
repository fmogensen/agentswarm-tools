"""Tests for video_search tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List

from tools.search.video_search import VideoSearch
from shared.errors import ValidationError, APIError


class TestVideoSearch:
    """Test suite for VideoSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        """Valid test query."""
        return "Python tutorial"

    @pytest.fixture
    def tool(self, valid_query: str) -> VideoSearch:
        """Create VideoSearch instance with valid parameters."""
        return VideoSearch(query=valid_query, max_results=10)

    @pytest.fixture
    def mock_results(self) -> List[Dict[str, Any]]:
        """Mock API results."""
        return [
            {
                "video_id": f"mock_video_id_{i}",
                "title": f"Mock Video Title {i}",
                "channel": f"Mock Channel {i}",
                "views": 1000 * i,
                "duration": f"{i}:30",
                "upload_date": "2024-01-15",
                "thumbnails": {
                    "default": f"https://example.com/thumbnail_{i}_default.jpg",
                    "medium": f"https://example.com/thumbnail_{i}_medium.jpg",
                    "high": f"https://example.com/thumbnail_{i}_high.jpg",
                },
                "description": f"This is a mock description for video {i}.",
            }
            for i in range(1, 11)
        ]

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: VideoSearch, mock_results: List[Dict[str, Any]]):
        """Test successful execution."""
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert result["success"] is True
            assert "result" in result
            assert len(result["result"]) == 10

    def test_metadata_correct(self, tool: VideoSearch):
        """Test tool metadata."""
        assert tool.tool_name == "video_search"
        assert tool.tool_category == "search"

    # ========== ERROR CASES ==========

    def test_validation_error_empty_query(self):
        """Test validation error with empty query."""
        with pytest.raises(ValidationError):
            tool = VideoSearch(query="", max_results=10)
            tool.run()

    def test_validation_error_whitespace_query(self):
        """Test validation error with whitespace-only query."""
        with pytest.raises(ValidationError):
            tool = VideoSearch(query="   ", max_results=10)
            tool.run()

    def test_validation_error_max_results_too_low(self):
        """Test validation error with max_results too low."""
        with pytest.raises(ValidationError):
            tool = VideoSearch(query="test", max_results=0)
            tool.run()

    def test_validation_error_max_results_too_high(self):
        """Test validation error with max_results too high."""
        with pytest.raises(ValidationError):
            tool = VideoSearch(query="test", max_results=51)
            tool.run()

    def test_api_error_handled(self, tool: VideoSearch):
        """Test API error handling."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: VideoSearch):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert len(result["result"]) > 0

    # ========== EDGE CASES ==========

    def test_unicode_query(self, mock_results: List[Dict[str, Any]]):
        """Test Unicode characters in query."""
        tool = VideoSearch(query="Pythonチュートリアル", max_results=5)
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert result["success"] is True

    def test_special_characters_in_query(self, mock_results: List[Dict[str, Any]]):
        """Test special characters in query."""
        special_query = "query with @#$%^&* special chars"
        tool = VideoSearch(query=special_query, max_results=5)
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert result["success"] is True

    def test_max_results_boundary(self, mock_results: List[Dict[str, Any]]):
        """Test max_results boundary values."""
        # Test minimum
        tool = VideoSearch(query="test", max_results=1)
        with patch.object(tool, "_process", return_value=mock_results[:1]):
            result = tool.run()
            assert result["success"] is True

        # Test maximum
        tool = VideoSearch(query="test", max_results=50)
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert result["success"] is True

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "query,max_results,expected_valid",
        [
            ("valid query", 10, True),
            ("Python programming", 5, True),
            ("a" * 100, 10, True),
            ("", 10, False),  # Empty query
            ("   ", 10, False),  # Whitespace only
            ("test", 0, False),  # Invalid max_results
            ("test", 51, False),  # Max_results too high
            ("test", -1, False),  # Negative max_results
        ],
    )
    def test_parameter_validation(
        self, query: str, max_results: int, expected_valid: bool
    ):
        """Test parameter validation with various inputs."""
        if expected_valid:
            tool = VideoSearch(query=query, max_results=max_results)
            assert tool.query == query
            assert tool.max_results == max_results
        else:
            with pytest.raises(Exception):  # Could be ValidationError or Pydantic error
                tool = VideoSearch(query=query, max_results=max_results)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_full_workflow(self, mock_results: List[Dict[str, Any]]):
        """Test complete workflow."""
        tool = VideoSearch(query="python programming", max_results=5)
        with patch.object(tool, "_process", return_value=mock_results[:5]):
            result = tool.run()
            assert result["success"] is True
            assert len(result["result"]) == 5
            assert result["metadata"]["tool_name"] == "video_search"

    def test_result_structure(self, tool: VideoSearch, mock_results: List[Dict[str, Any]]):
        """Test that result structure matches expected format."""
        with patch.object(tool, "_process", return_value=mock_results):
            result = tool.run()
            assert "success" in result
            assert "result" in result
            assert "metadata" in result

            # Check first video structure
            if result["result"]:
                first_video = result["result"][0]
                assert "video_id" in first_video
                assert "title" in first_video
                assert "channel" in first_video
                assert "views" in first_video
                assert "duration" in first_video
                assert "upload_date" in first_video
                assert "thumbnails" in first_video
                assert "description" in first_video

                # Check thumbnails structure
                thumbnails = first_video["thumbnails"]
                assert "default" in thumbnails
                assert "medium" in thumbnails
                assert "high" in thumbnails

    def test_duration_parsing(self, tool: VideoSearch):
        """Test duration parsing functionality."""
        # Test various duration formats
        test_cases = [
            ("PT1H2M10S", "1:02:10"),
            ("PT10M30S", "10:30"),
            ("PT45S", "0:45"),
            ("PT1H0M0S", "1:00:00"),
            ("", "0:00"),
            ("PT0S", "0:00"),
        ]

        for input_duration, expected_output in test_cases:
            parsed = tool._parse_duration(input_duration)
            assert parsed == expected_output, f"Failed for {input_duration}"

    # ========== API INTEGRATION ==========

    @patch("tools.search.video_search.requests.get")
    def test_api_request_structure(self, mock_get: MagicMock, tool: VideoSearch):
        """Test that API requests are structured correctly."""
        # Mock the API responses
        mock_search_response = MagicMock()
        mock_search_response.json.return_value = {
            "items": [
                {
                    "id": {"videoId": "test_id_1"},
                    "snippet": {
                        "title": "Test Video",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2024-01-15T00:00:00Z",
                        "thumbnails": {
                            "default": {"url": "https://example.com/default.jpg"},
                            "medium": {"url": "https://example.com/medium.jpg"},
                            "high": {"url": "https://example.com/high.jpg"},
                        },
                        "description": "Test description"
                    }
                }
            ]
        }

        mock_details_response = MagicMock()
        mock_details_response.json.return_value = {
            "items": [
                {
                    "id": "test_id_1",
                    "statistics": {
                        "viewCount": "1000",
                        "likeCount": "100",
                        "commentCount": "50"
                    },
                    "contentDetails": {
                        "duration": "PT10M30S"
                    }
                }
            ]
        }

        mock_get.side_effect = [mock_search_response, mock_details_response]

        with patch.dict("os.environ", {"YOUTUBE_API_KEY": "test_key"}):
            result = tool.run()
            assert result["success"] is True
            assert len(result["result"]) == 1
            assert result["result"][0]["title"] == "Test Video"
            assert result["result"][0]["views"] == 1000

    def test_empty_results(self, tool: VideoSearch):
        """Test handling of empty API results."""
        with patch.object(tool, "_process", return_value=[]):
            result = tool.run()
            assert result["success"] is True
            assert len(result["result"]) == 0
