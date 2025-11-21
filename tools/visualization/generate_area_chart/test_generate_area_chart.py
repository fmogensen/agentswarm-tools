"""Tests for generate_area_chart tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any
import os

from tools.visualization.generate_area_chart import GenerateAreaChart
from shared.errors import ValidationError, APIError


class TestGenerateAreaChart:
    """Test suite for GenerateAreaChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_params(self) -> Dict[str, Any]:
        return {"x": [1, 2, 3], "y": [4, 5, 6]}

    @pytest.fixture
    def tool(self, valid_params: Dict[str, Any]) -> GenerateAreaChart:
        return GenerateAreaChart(prompt="Simple chart", params=valid_params)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_params):
        tool = GenerateAreaChart(prompt="Test", params=valid_params)
        assert tool.prompt == "Test"
        assert tool.params == valid_params
        assert tool.tool_name == "generate_area_chart"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: GenerateAreaChart):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result
        assert result["result"]["chart_type"] == "area"

    def test_metadata_contains_prompt_and_params(self, tool: GenerateAreaChart):
        result = tool.run()
        metadata = result["metadata"]
        assert metadata["prompt"] == tool.prompt
        assert metadata["params"] == tool.params
        assert metadata["tool_name"] == "generate_area_chart"

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GenerateAreaChart):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: GenerateAreaChart):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["chart_type"] == "area"

    # ========== ERROR CASES ==========

    @pytest.mark.parametrize("bad_prompt", ["", "   ", None, 123])
    def test_invalid_prompt(self, bad_prompt):
        with pytest.raises(ValidationError):
            tool = GenerateAreaChart(prompt=bad_prompt, params={"x": [1], "y": [1]})
            tool.run()

    @pytest.mark.parametrize(
        "bad_params",
        [
            None,
            [],
            "string",
            {"x": [1, 2]},
            {"y": [1, 2]},
            {"x": "notlist", "y": [1]},
            {"x": [1], "y": "notlist"},
        ],
    )
    def test_invalid_params_structure(self, bad_params):
        with pytest.raises(ValidationError):
            tool = GenerateAreaChart(prompt="test", params=bad_params)
            tool.run()

    def test_mismatched_x_y_lengths(self):
        with pytest.raises(ValidationError):
            tool = GenerateAreaChart(prompt="test", params={"x": [1, 2], "y": [1]})
            tool.run()

    def test_empty_x_y_lists(self):
        with pytest.raises(ValidationError):
            tool = GenerateAreaChart(prompt="test", params={"x": [], "y": []})
            tool.run()

    def test_api_error_propagates(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_prompt(self, valid_params):
        tool = GenerateAreaChart(prompt="测试中文", params=valid_params)
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_prompt(self, valid_params):
        tool = GenerateAreaChart(prompt="@#$% Chart &*()", params=valid_params)
        result = tool.run()
        assert result["success"] is True

    def test_long_prompt(self, valid_params):
        long_text = "a" * 500
        tool = GenerateAreaChart(prompt=long_text, params=valid_params)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "x,y,valid",
        [
            ([1, 2, 3], [4, 5, 6], True),
            ([1], [2], True),
            ([1, 2], [3], False),
            ([], [], False),
            ("bad", [1], False),
            ([1], "bad", False),
        ],
    )
    def test_params_validation(self, x, y, valid):
        if valid:
            tool = GenerateAreaChart(prompt="ok", params={"x": x, "y": y})
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = GenerateAreaChart(prompt="ok", params={"x": x, "y": y})
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_integration_environment_toggle(self, tool: GenerateAreaChart):
        with patch.dict(os.environ, {"USE_MOCK_APIS": "true"}):
            result = tool.run()
            assert result["metadata"]["mock_mode"] is True

        with patch.dict(os.environ, {"USE_MOCK_APIS": "false"}):
            result = tool.run()
            assert "mock_mode" not in result["metadata"]

    def test_error_formatting_integration(self, tool: GenerateAreaChart):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
