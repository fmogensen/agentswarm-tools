"""Tests for generate_scatter_chart tool."""

import base64
import os
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.visualization.generate_scatter_chart import GenerateScatterChart


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

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
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
        """None prompt raises PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateScatterChart(prompt=None, params=valid_params)

    def test_nonstring_prompt(self, valid_params):
        """Non-string prompt raises PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateScatterChart(prompt=123, params=valid_params)

    def test_params_not_dict(self):
        """Non-dict params raise PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateScatterChart(prompt="test", params="not a dict")

    def test_missing_x_or_y(self):
        """Missing x or y fails custom validation and returns error dict."""
        tool = GenerateScatterChart(prompt="test", params={"x": [1, 2]})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

        tool2 = GenerateScatterChart(prompt="test", params={"y": [1, 2]})
        result2 = tool2.run()
        assert result2["success"] is False
        assert result2["error"]["code"] == "VALIDATION_ERROR"

    def test_x_y_not_lists(self):
        """Non-list x/y fails custom validation and returns error dict."""
        tool = GenerateScatterChart(prompt="test", params={"x": "123", "y": [1, 2]})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

        tool2 = GenerateScatterChart(prompt="test", params={"x": [1, 2], "y": "abc"})
        result2 = tool2.run()
        assert result2["success"] is False
        assert result2["error"]["code"] == "VALIDATION_ERROR"

    def test_x_y_length_mismatch(self):
        """Mismatched x/y lengths fail custom validation and return error dict."""
        tool = GenerateScatterChart(prompt="test", params={"x": [1], "y": [1, 2]})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    # ========== API ERROR HANDLING ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, tool):
        """Process failure returns error dict with API_ERROR code."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False
            assert result["error"]["code"] == "API_ERROR"

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_empty_lists(self):
        """Empty lists may succeed with empty chart."""
        tool = GenerateScatterChart(prompt="test", params={"x": [], "y": []})
        result = tool.run()
        # Empty lists may be valid for some chart types
        assert result["success"] is True or (
            result["success"] is False and result["error"]["code"] == "VALIDATION_ERROR"
        )

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
            ([1], [1, 2], False),
            ("abc", [1, 2], False),
            ([1, 2], "xyz", False),
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_param_validation(self, x, y, valid):
        params = {"x": x, "y": y}
        tool = GenerateScatterChart(prompt="test", params=params)
        result = tool.run()
        if valid:
            assert result["success"] is True
        else:
            assert result["success"] is False
            assert result["error"]["code"] == "VALIDATION_ERROR"

    # ========== INTEGRATION TESTS ==========

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("test error")):
            result = tool.run()
            assert result["success"] is False or "error" in result

    def test_rate_limiting_integration(self, tool):
        result = tool.run()
        assert result["success"] is True
