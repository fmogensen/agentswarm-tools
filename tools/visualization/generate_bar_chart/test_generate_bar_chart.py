"""Tests for generate_bar_chart tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
import os

from tools.visualization.generate_bar_chart import GenerateBarChart
from shared.errors import ValidationError, APIError


class TestGenerateBarChart:
    """Test suite for GenerateBarChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_data(self) -> Dict[str, Any]:
        return {"A": 1, "B": 2, "C": 3}

    @pytest.fixture
    def tool(self, valid_data: Dict[str, Any]) -> GenerateBarChart:
        return GenerateBarChart(prompt="Test Chart", params={"data": valid_data})

    @pytest.fixture
    def mock_chart_data(self):
        return {"A": 5, "B": 3, "C": 8}

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_data):
        tool = GenerateBarChart(prompt="Hello", params={"data": valid_data})
        assert tool.prompt == "Hello"
        assert tool.params["data"] == valid_data
        assert tool.tool_name == "generate_bar_chart"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool: GenerateBarChart):
        result = tool.run()
        assert result["success"] is True
        assert "image_base64" in result["result"]
        assert result["result"]["data"] == tool.params["data"]
        assert result["metadata"]["tool_name"] == "generate_bar_chart"

    def test_metadata_correct(self, tool):
        assert tool.tool_name == "generate_bar_chart"
        assert tool.tool_category == "visualization"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock(self, tool: GenerateBarChart):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: GenerateBarChart):
        result = tool.run()
        assert result["success"] is True
        assert "image_base64" in result["result"]

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("prompt", ["", None, 123])
    def test_invalid_prompt(self, prompt, valid_data):
        with pytest.raises(ValidationError):
            tool = GenerateBarChart(prompt=prompt, params={"data": valid_data})
            tool.run()

    def test_invalid_params_not_dict(self):
        with pytest.raises(ValidationError):
            tool = GenerateBarChart(prompt="Test", params="not a dict")
            tool.run()

    def test_missing_data_param(self):
        with pytest.raises(ValidationError):
            tool = GenerateBarChart(prompt="Test", params={})
            tool.run()

    def test_invalid_data_not_dict(self):
        with pytest.raises(ValidationError):
            tool = GenerateBarChart(prompt="Test", params={"data": "string"})
            tool.run()

    def test_invalid_data_keys(self):
        with pytest.raises(ValidationError):
            tool = GenerateBarChart(prompt="Test", params={"data": {1: 10}})
            tool.run()

    def test_invalid_data_values(self):
        with pytest.raises(ValidationError):
            tool = GenerateBarChart(
                prompt="Test", params={"data": {"A": "not numeric"}}
            )
            tool.run()

    # ========== ERROR HANDLING TESTS ==========

    def test_api_error_propagates(self, tool: GenerateBarChart):
        with patch.object(tool, "_process", side_effect=Exception("explode")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASE TESTS ==========

    def test_unicode_prompt(self, valid_data):
        tool = GenerateBarChart(prompt="测试图表", params={"data": valid_data})
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_prompt(self, valid_data):
        prompt = "@#$%^&*() Special !!!"
        tool = GenerateBarChart(prompt=prompt, params={"data": valid_data})
        result = tool.run()
        assert result["success"] is True

    def test_empty_data_dict(self):
        tool = GenerateBarChart(prompt="Empty Data", params={"data": {}})
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["data"] == {}

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "data,expected_valid",
        [
            ({"A": 1}, True),
            ({"A": 0}, True),
            ({"A": -5}, True),
            ({"A": None}, False),
            ({1: 5}, False),
            ("not a dict", False),
        ],
    )
    def test_data_validation(self, data, expected_valid):
        if expected_valid:
            tool = GenerateBarChart(prompt="Test", params={"data": data})
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = GenerateBarChart(prompt="Test", params={"data": data})
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_integration_flow(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert "image_base64" in result["result"]
        assert result["metadata"]["tool_name"] == "generate_bar_chart"

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert result["success"] is False or "error" in result

    def test_environment_variable_handling(self, tool, monkeypatch):
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        result = tool.run()
        assert result["result"]["mock"] is True
