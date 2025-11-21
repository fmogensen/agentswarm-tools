"""Tests for generate_line_chart tool."""

import pytest
from unittest.mock import patch, MagicMock
import os

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

    def test_execute_success(self, tool, mock_plot):
        result = tool.run()
        assert result["success"] is True
        assert "image_base64" in result["result"]
        assert result["result"]["data_points"] == 3
        assert result["metadata"]["tool_name"] == "generate_line_chart"

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

    @pytest.mark.parametrize(
        "prompt,params",
        [
            ("", {"data": [1, 2]}),
            (None, {"data": [1, 2]}),
        ],
    )
    def test_invalid_prompt(self, prompt, params):
        with pytest.raises(ValidationError):
            tool = GenerateLineChart(prompt=prompt, params=params)
            tool.run()

    def test_params_not_dict(self):
        with pytest.raises(ValidationError):
            tool = GenerateLineChart(prompt="X", params="not a dict")
            tool.run()

    @pytest.mark.parametrize(
        "data",
        [
            None,
            "not a list",
            [1, "x", 3],
        ],
    )
    def test_invalid_data(self, data):
        with pytest.raises(ValidationError):
            tool = GenerateLineChart(prompt="X", params={"data": data})
            tool.run()

    def test_labels_wrong_length(self):
        with pytest.raises(ValidationError):
            tool = GenerateLineChart(
                prompt="X", params={"data": [1, 2], "labels": ["one"]}
            )
            tool.run()

    # ========== ERROR HANDLING TESTS ==========

    def test_api_error(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("Boom")):
            with pytest.raises(APIError):
                tool.run()

    def test_process_chart_error(self, tool):
        with patch("matplotlib.pyplot.subplots", side_effect=Exception("Plot fail")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_prompt(self, valid_params):
        tool = GenerateLineChart(prompt="Unicode 测试", params=valid_params)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["prompt"] == "Unicode 测试"

    def test_special_chars_prompt(self, valid_params):
        tool = GenerateLineChart(prompt="Prompt @#&$*", params=valid_params)
        result = tool.run()
        assert result["success"] is True

    def test_minimal_data_list(self):
        tool = GenerateLineChart(prompt="Single", params={"data": [1]})
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["data_points"] == 1

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
        if valid:
            tool = GenerateLineChart(prompt="OK", params=params)
            assert tool.run()["success"] is True
        else:
            with pytest.raises(Exception):
                tool = GenerateLineChart(prompt="Bad", params=params)
                tool.run()

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
