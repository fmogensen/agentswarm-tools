"""Tests for generate_dual_axes_chart tool."""

import pytest
import os
from unittest.mock import patch
import base64

from pydantic import ValidationError as PydanticValidationError

from tools.visualization.generate_dual_axes_chart import GenerateDualAxesChart
from shared.errors import ValidationError, APIError


class TestGenerateDualAxesChart:
    """Test suite for GenerateDualAxesChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_data(self):
        """Valid test data dict."""
        return {
            "x": [1, 2, 3],
            "column_values": [10, 20, 30],
            "line_values": [5, 15, 25],
        }

    @pytest.fixture
    def tool(self, valid_data) -> GenerateDualAxesChart:
        """Create valid tool instance."""
        return GenerateDualAxesChart(prompt="Test Chart", params={"data": valid_data})

    # ========== INITIALIZATION TESTS ==========

    def test_tool_metadata(self, tool: GenerateDualAxesChart):
        """Test tool metadata is correct."""
        assert tool.tool_name == "generate_dual_axes_chart"
        assert tool.tool_category == "visualization"

    def test_initialization_success(self, valid_data):
        """Test valid tool initialization."""
        tool = GenerateDualAxesChart(prompt="Chart", params={"data": valid_data})
        assert tool.prompt == "Chart"
        assert tool.params["data"] == valid_data

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: GenerateDualAxesChart):
        """Test successful execution."""
        result = tool.run()
        assert result["success"] is True
        assert "chart_base64" in result["result"]
        assert result["metadata"]["tool_name"] == "generate_dual_axes_chart"

    def test_base64_output_valid(self, tool: GenerateDualAxesChart):
        """Ensure base64 output decodes."""
        result = tool.run()
        encoded = result["result"]["chart_base64"]
        decoded = base64.b64decode(encoded)
        assert isinstance(decoded, bytes)

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GenerateDualAxesChart):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: GenerateDualAxesChart):
        """Test real mode processes data."""
        result = tool.run()
        assert result["success"] is True
        assert "chart_base64" in result["result"]

    # ========== VALIDATION ERROR TESTS ==========

    def test_missing_prompt(self, valid_data):
        """Empty prompt fails custom validation and returns error dict."""
        tool = GenerateDualAxesChart(prompt="", params={"data": valid_data})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_invalid_params_not_dict(self):
        """Non-dict params raise PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateDualAxesChart(prompt="test", params="not a dict")

    def test_missing_data_field(self):
        """Missing data field fails custom validation and returns error dict."""
        tool = GenerateDualAxesChart(prompt="test", params={})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.parametrize("missing", ["x", "column_values", "line_values"])
    def test_missing_required_data_fields(self, valid_data, missing):
        """Missing required data fields fail custom validation and return error dict."""
        bad = valid_data.copy()
        del bad[missing]
        tool = GenerateDualAxesChart(prompt="test", params={"data": bad})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    @pytest.mark.parametrize("field", ["x", "column_values", "line_values"])
    def test_non_list_fields(self, valid_data, field):
        """Non-list fields fail custom validation and return error dict."""
        bad = valid_data.copy()
        bad[field] = "not a list"
        tool = GenerateDualAxesChart(prompt="test", params={"data": bad})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_data_length_mismatch(self, valid_data):
        """Mismatched data lengths fail custom validation and return error dict."""
        valid_data["x"] = [1]
        tool = GenerateDualAxesChart(prompt="test", params={"data": valid_data})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    # ========== API ERROR TESTS ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_api_error_propagates(self, tool: GenerateDualAxesChart):
        """Process failure returns error dict with API_ERROR code."""
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            result = tool.run()
            assert result["success"] is False
            assert result["error"]["code"] == "API_ERROR"

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_unicode_prompt(self, valid_data):
        tool = GenerateDualAxesChart(prompt="图表测试", params={"data": valid_data})
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["prompt"] == "图表测试"

    def test_special_characters_prompt(self, valid_data):
        prompt = "Chart @$%^&*()!"
        tool = GenerateDualAxesChart(prompt=prompt, params={"data": valid_data})
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,valid",
        [
            ("Valid prompt", True),
            ("a" * 500, True),
            ("", False),
        ],
    )
    def test_prompt_validation(self, prompt, valid, valid_data):
        tool = GenerateDualAxesChart(prompt=prompt, params={"data": valid_data})
        if valid:
            assert tool.prompt == prompt
            result = tool.run()
            assert result["success"] is True
        else:
            result = tool.run()
            assert result["success"] is False

    def test_prompt_none_raises(self, valid_data):
        """None prompt raises PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateDualAxesChart(prompt=None, params={"data": valid_data})

    @pytest.mark.parametrize(
        "x, col, line, valid",
        [
            ([1], [1], [1], True),
            ([1, 2], [1], [1], False),
            ([], [], [], True),
        ],
    )
    def test_data_length_parametrized(self, x, col, line, valid):
        params = {"data": {"x": x, "column_values": col, "line_values": line}}
        tool = GenerateDualAxesChart(prompt="test", params=params)
        result = tool.run()
        if valid:
            assert result["success"] is True
        else:
            assert result["success"] is False
            assert result["error"]["code"] == "VALIDATION_ERROR"

    # ========== INTEGRATION TESTS ==========

    def test_integration_runs(self, tool: GenerateDualAxesChart):
        """Full workflow integration test."""
        result = tool.run()
        assert result["success"] is True
        assert "chart_base64" in result["result"]

    def test_error_formatting_integration(self, tool: GenerateDualAxesChart):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
