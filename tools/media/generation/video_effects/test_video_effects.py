"""
Tests for VideoEffects tool
"""

import pytest
from unittest.mock import patch, MagicMock
import os

from tools.media_generation.video_effects import VideoEffects
from shared.errors import ValidationError, APIError


class TestVideoEffects:
    """Test suite for VideoEffects."""

    @pytest.fixture
    def tool(self):
        return VideoEffects(
            input_path="/path/to/test_video.mp4",
            effects=[{"type": "brightness", "parameters": {"value": 0.2}}],
            output_format="mp4",
        )

    def test_initialization(self, tool):
        """Test tool initialization."""
        assert tool.tool_name == "video_effects"
        assert tool.tool_category == "media_generation"
        assert tool.input_path == "/path/to/test_video.mp4"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        """Test mock mode execution."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "output_path" in result["result"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_multiple_effects(self):
        """Test with multiple effects."""
        tool = VideoEffects(
            input_path="/path/to/test_video.mp4",
            effects=[
                {"type": "brightness", "parameters": {"value": 0.2}},
                {"type": "saturation", "parameters": {"value": 0.3}},
                {"type": "blur", "parameters": {"strength": 5}},
                {"type": "vignette", "parameters": {"strength": 0.5}},
            ],
        )
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]["effects_applied"]) == 4

    def test_empty_effects_validation(self):
        """Test validation with empty effects list."""
        tool = VideoEffects(input_path="/path/to/test_video.mp4", effects=[])
        result = tool.run()
        assert result["success"] is False

    def test_invalid_effect_type(self):
        """Test validation with invalid effect type."""
        tool = VideoEffects(
            input_path="/path/to/test_video.mp4",
            effects=[{"type": "invalid_effect", "parameters": {}}],
        )
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_color_effects(self):
        """Test all color effects."""
        effects = [
            {"type": "brightness", "parameters": {"value": 0.2}},
            {"type": "contrast", "parameters": {"value": 0.3}},
            {"type": "saturation", "parameters": {"value": 0.4}},
            {"type": "hue", "parameters": {"degrees": 45}},
            {"type": "sepia", "parameters": {}},
            {"type": "grayscale", "parameters": {}},
            {"type": "invert", "parameters": {}},
        ]

        tool = VideoEffects(input_path="/path/to/test_video.mp4", effects=effects)
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]["effects_applied"]) == 7

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_blur_sharpen_effects(self):
        """Test blur and sharpen effects."""
        effects = [
            {"type": "blur", "parameters": {"strength": 5}},
            {"type": "sharpen", "parameters": {"strength": 7}},
            {"type": "motion_blur", "parameters": {}},
        ]

        tool = VideoEffects(input_path="/path/to/test_video.mp4", effects=effects)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_stylistic_effects(self):
        """Test stylistic effects."""
        effects = [
            {"type": "vignette", "parameters": {"strength": 0.5}},
            {"type": "vintage", "parameters": {}},
            {"type": "cinematic", "parameters": {}},
            {"type": "cartoon", "parameters": {}},
            {"type": "edge_detect", "parameters": {}},
        ]

        tool = VideoEffects(input_path="/path/to/test_video.mp4", effects=effects)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_time_effects(self):
        """Test time manipulation effects."""
        effects = [
            {"type": "slow_motion", "parameters": {"speed": 0.5}},
            {"type": "speed_up", "parameters": {"speed": 2.0}},
            {"type": "reverse", "parameters": {}},
        ]

        tool = VideoEffects(input_path="/path/to/test_video.mp4", effects=effects)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_output_formats(self):
        """Test different output formats."""
        formats = ["mp4", "mov", "avi", "webm"]

        for fmt in formats:
            tool = VideoEffects(
                input_path="/path/to/test_video.mp4",
                effects=[{"type": "brightness", "parameters": {"value": 0.1}}],
                output_format=fmt,
            )
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["output_format"] == fmt

    def test_invalid_output_format(self):
        """Test validation with invalid output format."""
        tool = VideoEffects(
            input_path="/path/to/test_video.mp4",
            effects=[{"type": "brightness", "parameters": {}}],
            output_format="invalid",
        )
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_custom_output_path(self):
        """Test with custom output path."""
        tool = VideoEffects(
            input_path="/path/to/test_video.mp4",
            effects=[{"type": "brightness", "parameters": {}}],
            output_path="/path/to/custom_output.mp4",
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["output_path"] == "/path/to/custom_output.mp4"
