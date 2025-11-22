"""
Tests for BatchVideoAnalysis tool
"""

import pytest
from unittest.mock import patch, MagicMock
import os

from tools.media_analysis.batch_video_analysis import BatchVideoAnalysis
from shared.errors import ValidationError, APIError


class TestBatchVideoAnalysis:
    """Test suite for BatchVideoAnalysis."""

    @pytest.fixture
    def tool(self):
        return BatchVideoAnalysis(
            video_urls="https://example.com/video1.mp4,https://example.com/video2.mp4",
            analysis_types=["scene_detection", "object_recognition"]
        )

    def test_initialization(self, tool):
        """Test tool initialization."""
        assert tool.tool_name == "batch_video_analysis"
        assert tool.tool_category == "media_analysis"
        assert "video1.mp4" in tool.video_urls

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        """Test mock mode execution."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["total_videos"] == 2
        assert len(result["result"]["analyses"]) == 2

    def test_empty_video_urls_validation(self):
        """Test validation with empty video URLs."""
        tool = BatchVideoAnalysis(
            video_urls="   ",
            analysis_types=["scene_detection"]
        )
        result = tool.run()
        assert result["success"] is False
        assert "video_urls" in str(result.get("error", {}))

    def test_invalid_analysis_type(self):
        """Test validation with invalid analysis type."""
        tool = BatchVideoAnalysis(
            video_urls="https://example.com/video1.mp4",
            analysis_types=["invalid_type"]
        )
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_custom_instruction(self):
        """Test with custom instruction."""
        tool = BatchVideoAnalysis(
            video_urls="https://example.com/video1.mp4",
            analysis_types=["scene_detection"],
            custom_instruction="Focus on action scenes"
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["custom_instruction"] == "Focus on action scenes"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_multiple_analysis_types(self):
        """Test with multiple analysis types."""
        tool = BatchVideoAnalysis(
            video_urls="https://example.com/video1.mp4",
            analysis_types=["scene_detection", "object_recognition", "sentiment", "transcript"]
        )
        result = tool.run()
        assert result["success"] is True
        analyses = result["result"]["analyses"][0]["analyses"]
        assert "scene_detection" in analyses
        assert "object_recognition" in analyses
        assert "sentiment" in analyses
        assert "transcript" in analyses
