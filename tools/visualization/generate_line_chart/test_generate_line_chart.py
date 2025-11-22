"""Tests for generate_line_chart tool."""

import pytest
from unittest.mock import patch, MagicMock
import os

from pydantic import ValidationError as PydanticValidationError

from tools.visualization.generate_line_chart import GenerateLineChart
from shared.errors import ValidationError, APIError


class TestGenerateLineChart:
    """Test suite for GenerateLineChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_params(self):
        return {"data": [1, 2, 3], "labels": ["a", "b", "c"], "title": "Test Chart"}

    @pytest.fixture
    def tool(self, valid_params) -> GenerateLineChart:
        return GenerateLineChart(prompt="Test Prompt", params=valid_params)

    @pytest.fixture
    def mock_plot(self):
        with patch("matplotlib.pyplot.subplots") as mock_fig:
            fig = MagicMock()
            ax = MagicMock()
            mock_fig.return_value = (fig, ax)
            yield fig, ax

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_params):
        tool = GenerateLineChart(prompt="Test", params=valid_params)
        assert tool.prompt == "Test"
        assert tool.params == valid_params
        assert tool.tool_name == "generate_line_chart"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH TESTS ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool, mock_plot):
        result = tool.run()
        assert result["success"] is True
        assert "image_base64" in result["result"]
        assert result["metadata"]["tool_name"] == "generate_line_chart"

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_metadata_contains_prompt(self, tool, mock_plot):
        result = tool.run()
        assert result["metadata"]["prompt"] == tool.prompt

    # ========== MOCK MODE TESTS ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool, mock_plot):
        result = tool.run()
        assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    def test_invalid_prompt_empty(self):
        """Empty prompt fails custom validation and returns error dict."""
        tool = GenerateLineChart(prompt="", params={"data": [1, 2]})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_invalid_prompt_none(self):
        """None prompt raises PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateLineChart(prompt=None, params={"data": [1, 2]})

    def test_params_not_dict(self):
        """Non-dict params raise PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateLineChart(prompt="X", params="not a dict")

    @pytest.mark.parametrize(
        "data",
        [
            None,
            "not a list",
            [1, "x", 3],
        ],
    )
    def test_invalid_data(self, data):
        """Invalid data fails custom validation and returns error dict."""
        tool = GenerateLineChart(prompt="X", params={"data": data})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_labels_wrong_length(self):
        """Mismatched labels length fails custom validation and returns error dict."""
        tool = GenerateLineChart(prompt="X", params={"data": [1, 2], "labels": ["one"]})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    # ========== ERROR HANDLING TESTS ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_api_error(self, tool):
        """Process failure returns error dict."""
        with patch.object(tool, "_process", side_effect=Exception("Boom")):
            result = tool.run()
            assert result["success"] is False

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_process_chart_error(self, tool):
        """Chart processing failure returns error dict."""
        with patch("matplotlib.pyplot.subplots", side_effect=Exception("Plot fail")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_unicode_prompt(self, valid_params):
        tool = GenerateLineChart(prompt="Unicode 测试", params=valid_params)
        result = tool.run()
        assert result["success"] is True

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_special_chars_prompt(self, valid_params):
        tool = GenerateLineChart(prompt="Prompt @#&$*", params=valid_params)
        result = tool.run()
        assert result["success"] is True

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_minimal_data_list(self):
        tool = GenerateLineChart(prompt="Single", params={"data": [1]})
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "params,valid",
        [
            ({"data": [1, 2, 3]}, True),
            ({"data": []}, False),
            ({"data": [1, 2], "labels": ["a", "b"]}, True),
            ({"data": [1, 2], "labels": ["a", "b", "c"]}, False),
        ],
    )
    def test_parameter_validation(self, params, valid):
        tool = GenerateLineChart(prompt="OK", params=params)
        result = tool.run()
        if valid:
            assert result["success"] is True
        else:
            assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    def test_integration_normal_run(self, tool, mock_plot):
        result = tool.run()
        assert result["success"] is True
        assert "image_base64" in result["result"]

    def test_integration_error_formatting(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("Bad")):
            output = tool.run()
            assert output["success"] is False
            assert "error" in output
