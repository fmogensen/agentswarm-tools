"""Tests for generate_dual_axes_chart tool."""

import pytest
from unittest.mock import patch
import base64

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
        """Prompt must be non-empty string."""
        with pytest.raises(ValidationError):
            GenerateDualAxesChart(prompt="", params={"data": valid_data}).run()

    def test_invalid_params_not_dict(self):
        with pytest.raises(ValidationError):
            GenerateDualAxesChart(prompt="test", params="not a dict").run()

    def test_missing_data_field(self):
        with pytest.raises(ValidationError):
            GenerateDualAxesChart(prompt="test", params={}).run()

    @pytest.mark.parametrize("missing", ["x", "column_values", "line_values"])
    def test_missing_required_data_fields(self, valid_data, missing):
        bad = valid_data.copy()
        del bad[missing]
        with pytest.raises(ValidationError):
            GenerateDualAxesChart(prompt="test", params={"data": bad}).run()

    @pytest.mark.parametrize("field", ["x", "column_values", "line_values"])
    def test_non_list_fields(self, valid_data, field):
        bad = valid_data.copy()
        bad[field] = "not a list"
        with pytest.raises(ValidationError):
            GenerateDualAxesChart(prompt="test", params={"data": bad}).run()

    def test_data_length_mismatch(self, valid_data):
        valid_data["x"] = [1]
        with pytest.raises(ValidationError):
            GenerateDualAxesChart(prompt="test", params={"data": valid_data}).run()

    # ========== API ERROR TESTS ==========

    def test_api_error_propagates(self, tool: GenerateDualAxesChart):
        """Process failure should raise APIError."""
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

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
            (None, False),
        ],
    )
    def test_prompt_validation(self, prompt, valid, valid_data):
        if valid:
            tool = GenerateDualAxesChart(prompt=prompt, params={"data": valid_data})
            assert tool.prompt == prompt
        else:
            with pytest.raises(Exception):
                GenerateDualAxesChart(prompt=prompt, params={"data": valid_data}).run()

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
        if valid:
            tool = GenerateDualAxesChart(prompt="test", params=params)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(ValidationError):
                GenerateDualAxesChart(prompt="test", params=params).run()

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
