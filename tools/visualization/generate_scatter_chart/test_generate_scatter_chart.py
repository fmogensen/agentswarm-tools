"""Tests for generate_scatter_chart tool."""

import pytest
from unittest.mock import patch, MagicMock
import base64

from tools.visualization.generate_scatter_chart import GenerateScatterChart
from shared.errors import ValidationError, APIError


class TestGenerateScatterChart:
    """Test suite for GenerateScatterChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_params(self):
        return {
            "x": [1, 2, 3],
            "y": [4, 5, 6],
            "title": "Test Chart",
            "x_label": "X Axis",
            "y_label": "Y Axis",
        }

    @pytest.fixture
    def tool(self, valid_params):
        return GenerateScatterChart(prompt="valid prompt", params=valid_params)

    # ========== INITIALIZATION ==========

    def test_initialization(self, valid_params):
        tool = GenerateScatterChart(prompt="abc", params=valid_params)
        assert tool.prompt == "abc"
        assert tool.params == valid_params

    def test_metadata(self, tool):
        assert tool.tool_name == "generate_scatter_chart"
        assert tool.tool_category == "visualization"
        assert tool.tool_description is not None

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert "chart_id" in result["result"]
        assert "image_base64" in result["result"]
        assert len(result["result"]["image_base64"]) > 0

    def test_execute_metadata_contains_input(self, tool):
        result = tool.run()
        metadata = result["metadata"]
        assert metadata["tool_name"] == "generate_scatter_chart"
        assert metadata["prompt"] == "valid prompt"
        assert metadata["params"] == tool.params

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool):
        result = tool.run()
        assert result["success"] is True

    # ========== VALIDATION ERRORS ==========

    def test_missing_prompt(self, valid_params):
        with pytest.raises(ValidationError):
            tool = GenerateScatterChart(prompt=None, params=valid_params)
            tool.run()

    def test_nonstring_prompt(self, valid_params):
        with pytest.raises(ValidationError):
            tool = GenerateScatterChart(prompt=123, params=valid_params)
            tool.run()

    def test_params_not_dict(self):
        with pytest.raises(ValidationError):
            tool = GenerateScatterChart(prompt="test", params="not a dict")
            tool.run()

    def test_missing_x_or_y(self):
        with pytest.raises(ValidationError):
            tool = GenerateScatterChart(prompt="test", params={"x": [1, 2]})
            tool.run()
        with pytest.raises(ValidationError):
            tool = GenerateScatterChart(prompt="test", params={"y": [1, 2]})
            tool.run()

    def test_x_y_not_lists(self):
        with pytest.raises(ValidationError):
            tool = GenerateScatterChart(prompt="test", params={"x": "123", "y": [1, 2]})
            tool.run()
        with pytest.raises(ValidationError):
            tool = GenerateScatterChart(prompt="test", params={"x": [1, 2], "y": "abc"})
            tool.run()

    def test_x_y_length_mismatch(self):
        with pytest.raises(ValidationError):
            tool = GenerateScatterChart(prompt="test", params={"x": [1], "y": [1, 2]})
            tool.run()

    # ========== API ERROR HANDLING ==========

    def test_api_error_handled(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

    def test_empty_lists(self):
        with pytest.raises(ValidationError):
            tool = GenerateScatterChart(prompt="test", params={"x": [], "y": []})
            tool.run()

    def test_zero_values(self):
        tool = GenerateScatterChart(prompt="test", params={"x": [0, 0], "y": [0, 0]})
        result = tool.run()
        assert result["success"] is True

    def test_unicode_prompt(self, valid_params):
        tool = GenerateScatterChart(prompt="Unicode 测试", params=valid_params)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "x, y, valid",
        [
            ([1, 2, 3], [4, 5, 6], True),
            ([], [], False),
            ([1], [1, 2], False),
            ("abc", [1, 2], False),
            ([1, 2], "xyz", False),
        ],
    )
    def test_param_validation(self, x, y, valid):
        params = {"x": x, "y": y}
        if valid:
            tool = GenerateScatterChart(prompt="test", params=params)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(ValidationError):
                tool = GenerateScatterChart(prompt="test", params=params)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("test error")):
            result = tool.run()
            assert result["success"] is False or "error" in result

    def test_rate_limiting_integration(self, tool):
        result = tool.run()
        assert result["success"] is True
