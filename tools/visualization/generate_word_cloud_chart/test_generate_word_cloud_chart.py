"""Tests for generate_word_cloud_chart tool."""

import pytest
from unittest.mock import patch, MagicMock
import os

from tools.visualization.generate_word_cloud_chart import GenerateWordCloudChart
from shared.errors import ValidationError, APIError


class TestGenerateWordCloudChart:
    """Test suite for GenerateWordCloudChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_params(self):
        return {"width": 300, "height": 200, "background_color": "white"}

    @pytest.fixture
    def tool(self, valid_params) -> GenerateWordCloudChart:
        """Create tool instance."""
        return GenerateWordCloudChart(prompt="valid prompt", params=valid_params)

    @pytest.fixture
    def mock_wc_instance(self):
        mock_wc = MagicMock()
        mock_wc.generate.return_value = mock_wc
        mock_img = MagicMock()
        mock_img.save = MagicMock()
        mock_wc.to_image.return_value = mock_img
        return mock_wc

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization_success(self, valid_params):
        tool = GenerateWordCloudChart(prompt="hello", params=valid_params)
        assert tool.prompt == "hello"
        assert tool.params == valid_params
        assert tool.tool_name == "generate_word_cloud_chart"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH ==========

    @patch("tools.visualization.generate_word_cloud_chart.WordCloud")
    def test_execute_success(self, mock_wc, tool, mock_wc_instance):
        mock_wc.return_value = mock_wc_instance
        result = tool.run()
        assert result["success"] is True
        assert "image_base64" in result["result"]
        assert result["metadata"]["tool_name"] == "generate_word_cloud_chart"

    def test_metadata_correct(self, tool):
        assert tool.tool_name == "generate_word_cloud_chart"
        assert tool.tool_category == "visualization"

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    # ========== ERROR CASES ==========

    def test_prompt_empty_raises_validation_error(self):
        with pytest.raises(ValidationError):
            tool = GenerateWordCloudChart(prompt="", params={})
            tool.run()

    def test_params_not_dict_raises_validation_error(self):
        with pytest.raises(ValidationError):
            tool = GenerateWordCloudChart(prompt="valid", params="not a dict")
            tool.run()

    @patch("tools.visualization.generate_word_cloud_chart.WordCloud", None)
    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_missing_library_raises_api_error(self):
        with pytest.raises(APIError):
            tool = GenerateWordCloudChart(prompt="test", params={})
            tool.run()

    @patch("tools.visualization.generate_word_cloud_chart.WordCloud")
    def test_api_error_handled(self, mock_wc, tool):
        mock_wc.side_effect = Exception("API failed")
        with pytest.raises(APIError):
            tool.run()

    # ========== EDGE CASES ==========

    @patch("tools.visualization.generate_word_cloud_chart.WordCloud")
    def test_unicode_prompt(self, mock_wc, tool, mock_wc_instance):
        mock_wc.return_value = mock_wc_instance
        tool.prompt = "你好 世界"
        result = tool.run()
        assert result["success"] is True

    @patch("tools.visualization.generate_word_cloud_chart.WordCloud")
    def test_special_characters_prompt(self, mock_wc, tool, mock_wc_instance):
        mock_wc.return_value = mock_wc_instance
        tool.prompt = "@#$%^&*()!"
        result = tool.run()
        assert result["success"] is True

    @patch("tools.visualization.generate_word_cloud_chart.WordCloud")
    def test_large_dimensions(self, mock_wc, mock_wc_instance):
        mock_wc.return_value = mock_wc_instance
        params = {"width": 5000, "height": 5000}
        tool = GenerateWordCloudChart(prompt="test", params=params)
        result = tool.run()
        assert result["result"]["width"] == 5000
        assert result["result"]["height"] == 5000

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,valid",
        [
            ("normal text", True),
            ("   spaces   ", True),
            ("", False),
            (" ", False),
        ],
    )
    def test_prompt_validation(self, prompt, valid):
        if valid:
            tool = GenerateWordCloudChart(prompt=prompt, params={})
            assert tool.prompt.strip() != ""
        else:
            with pytest.raises(ValidationError):
                tool = GenerateWordCloudChart(prompt=prompt, params={})
                tool.run()

    @pytest.mark.parametrize(
        "params,valid",
        [
            ({"width": 100, "height": 100}, True),
            ({}, True),
            (None, False),
            ("string", False),
            (123, False),
        ],
    )
    def test_params_validation(self, params, valid):
        if valid:
            tool = GenerateWordCloudChart(prompt="test", params=params)
            assert isinstance(tool.params, dict)
        else:
            with pytest.raises(ValidationError):
                tool = GenerateWordCloudChart(prompt="test", params=params)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch("tools.visualization.generate_word_cloud_chart.WordCloud")
    def test_integration_full_run(self, mock_wc, mock_wc_instance):
        mock_wc.return_value = mock_wc_instance
        tool = GenerateWordCloudChart(prompt="integration", params={"width": 200})
        result = tool.run()
        assert result["success"] is True

    @patch("tools.visualization.generate_word_cloud_chart.WordCloud")
    def test_error_formatting_integration(self, mock_wc):
        tool = GenerateWordCloudChart(prompt="test", params={})
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
