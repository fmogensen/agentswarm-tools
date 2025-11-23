"""
Tests for ImageStyleTransfer tool
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from shared.errors import APIError, ValidationError
from tools.media_generation.image_style_transfer import ImageStyleTransfer


class TestImageStyleTransfer:
    """Test suite for ImageStyleTransfer."""

    @pytest.fixture
    def tool(self):
        return ImageStyleTransfer(
            input_image="https://example.com/photo.jpg", style="starry_night", style_strength=0.7
        )

    def test_initialization(self, tool):
        """Test tool initialization."""
        assert tool.tool_name == "image_style_transfer"
        assert tool.tool_category == "media_generation"
        assert tool.style == "starry_night"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        """Test mock mode execution."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "styled_image_url" in result["result"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_predefined_styles(self):
        """Test with various predefined styles."""
        styles = ["monet", "van_gogh", "picasso", "oil_painting", "watercolor", "anime"]

        for style in styles:
            tool = ImageStyleTransfer(input_image="https://example.com/photo.jpg", style=style)
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["style_applied"] == style

    def test_invalid_style(self):
        """Test validation with invalid style."""
        tool = ImageStyleTransfer(
            input_image="https://example.com/photo.jpg", style="invalid_style_name"
        )
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_custom_style_image(self):
        """Test with custom style image URL."""
        tool = ImageStyleTransfer(
            input_image="https://example.com/photo.jpg",
            style="custom",
            style_image_url="https://example.com/style.jpg",
        )
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_style_strength_variations(self):
        """Test with different style strengths."""
        strengths = [0.0, 0.3, 0.5, 0.7, 1.0]

        for strength in strengths:
            tool = ImageStyleTransfer(
                input_image="https://example.com/photo.jpg",
                style="starry_night",
                style_strength=strength,
            )
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["style_strength"] == strength

    def test_invalid_style_strength(self):
        """Test validation with invalid style strength."""
        # Test value > 1.0
        tool = ImageStyleTransfer(
            input_image="https://example.com/photo.jpg", style="monet", style_strength=1.5
        )
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_preserve_color(self):
        """Test color preservation option."""
        tool = ImageStyleTransfer(
            input_image="https://example.com/photo.jpg", style="picasso", preserve_color=True
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["preserve_color"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_output_size(self):
        """Test with custom output size."""
        tool = ImageStyleTransfer(
            input_image="https://example.com/photo.jpg", style="monet", output_size="1024x1024"
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["output_size"] == "1024x1024"

    def test_invalid_output_size(self):
        """Test validation with invalid output size."""
        tool = ImageStyleTransfer(
            input_image="https://example.com/photo.jpg", style="monet", output_size="invalid"
        )
        result = tool.run()
        assert result["success"] is False

    def test_empty_input_image(self):
        """Test validation with empty input image."""
        tool = ImageStyleTransfer(input_image="   ", style="monet")
        result = tool.run()
        assert result["success"] is False
