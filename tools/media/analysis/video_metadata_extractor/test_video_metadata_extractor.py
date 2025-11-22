"""
Tests for VideoMetadataExtractor tool
"""

import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile

from tools.media_analysis.video_metadata_extractor import VideoMetadataExtractor
from shared.errors import ValidationError, APIError


class TestVideoMetadataExtractor:
    """Test suite for VideoMetadataExtractor."""

    @pytest.fixture
    def tool(self):
        return VideoMetadataExtractor(
            video_path="/path/to/test_video.mp4",
            extract_thumbnails=False,
            include_streams=True
        )

    def test_initialization(self, tool):
        """Test tool initialization."""
        assert tool.tool_name == "video_metadata_extractor"
        assert tool.tool_category == "media_analysis"
        assert tool.video_path == "/path/to/test_video.mp4"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        """Test mock mode execution."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "video" in result["result"]
        assert "audio" in result["result"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_structure(self, tool):
        """Test metadata structure."""
        result = tool.run()
        metadata = result["result"]

        # Check file info
        assert "file" in metadata
        assert metadata["file"]["size_mb"] == 15.0

        # Check video info
        assert "video" in metadata
        assert metadata["video"]["resolution"] == "1920x1080"
        assert metadata["video"]["codec"] == "h264"

        # Check audio info
        assert "audio" in metadata
        assert metadata["audio"]["codec"] == "aac"
        assert metadata["audio"]["channels"] == 2

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_extract_thumbnails(self):
        """Test thumbnail extraction."""
        tool = VideoMetadataExtractor(
            video_path="/path/to/test_video.mp4",
            extract_thumbnails=True
        )
        result = tool.run()
        assert "thumbnails" in result["result"]
        assert len(result["result"]["thumbnails"]) == 3

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_include_streams(self):
        """Test stream information inclusion."""
        tool = VideoMetadataExtractor(
            video_path="/path/to/test_video.mp4",
            include_streams=True
        )
        result = tool.run()
        assert "streams" in result["result"]
        assert len(result["result"]["streams"]) == 2

    def test_empty_path_validation(self):
        """Test validation with empty path."""
        tool = VideoMetadataExtractor(
            video_path="   "
        )
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_url_path(self):
        """Test with URL path."""
        tool = VideoMetadataExtractor(
            video_path="https://example.com/video.mp4"
        )
        result = tool.run()
        assert result["success"] is True
