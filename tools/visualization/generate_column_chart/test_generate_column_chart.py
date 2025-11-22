"""Tests for generate_column_chart tool."""

import pytest
import os
from unittest.mock import patch
from typing import Dict, Any

from pydantic import ValidationError as PydanticValidationError

from tools.visualization.generate_column_chart import GenerateColumnChart
from shared.errors import ValidationError, APIError


class TestGenerateColumnChart:
    """Test suite for GenerateColumnChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_params(self) -> Dict[str, Any]:
        return {
            "categories": ["A", "B", "C"],
            "values": [1, 2, 3],
            "title": "Test Chart",
            "style": {"color": "blue"},
            "config": {"width": 400},
        }

    @pytest.fixture
    def tool(self, valid_params: Dict[str, Any]) -> GenerateColumnChart:
        return GenerateColumnChart(prompt="Test prompt", params=valid_params)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_params: Dict[str, Any]):
        tool = GenerateColumnChart(prompt="Hello", params=valid_params)
        assert tool.prompt == "Hello"
        assert tool.params == valid_params

    def test_metadata(self, tool: GenerateColumnChart):
        assert tool.tool_name == "generate_column_chart"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: GenerateColumnChart):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["type"] == "column"
        assert result["metadata"]["tool_name"] == "generate_column_chart"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GenerateColumnChart):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["type"] == "column"
        assert result["result"]["categories"] == ["A", "B", "C"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: GenerateColumnChart):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["categories"] == ["A", "B", "C"]

    # ========== VALIDATION ERROR CASES ==========

    def test_validation_error_empty_prompt(self):
        """Empty prompt fails custom validation and returns error dict."""
        tool = GenerateColumnChart(prompt="", params={"categories": ["A"], "values": [1]})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_validation_error_whitespace_prompt(self):
        """Whitespace prompt fails custom validation and returns error dict."""
        tool = GenerateColumnChart(prompt="  ", params={"categories": ["A"], "values": [1]})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_validation_error_params_none(self):
        """None params raise PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateColumnChart(prompt="Hello", params=None)

    def test_validation_error_missing_categories_values(self):
        """Missing categories/values fails custom validation and returns error dict."""
        tool = GenerateColumnChart(prompt="Hello", params={})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_validation_error_mismatched_lengths(self):
        """Mismatched lengths fails custom validation and returns error dict."""
        tool = GenerateColumnChart(prompt="Hello", params={"categories": ["A"], "values": []})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_validation_error_not_lists(self):
        """Non-list categories fails custom validation and returns error dict."""
        tool = GenerateColumnChart(prompt="Hello", params={"categories": "A", "values": [1]})
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_mismatched_length_validation(self):
        """Mismatched lengths fails custom validation and returns error dict."""
        tool = GenerateColumnChart(
            prompt="Invalid", params={"categories": ["A", "B"], "values": [1]}
        )
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    # ========== API ERROR HANDLING ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, tool: GenerateColumnChart):
        """Process failure returns error dict with API_ERROR code."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False
            assert result["error"]["code"] == "API_ERROR"

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_unicode_prompt(self, valid_params: Dict[str, Any]):
        tool = GenerateColumnChart(prompt="标题", params=valid_params)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["prompt"] == "标题"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_special_chars_prompt(self, valid_params: Dict[str, Any]):
        tool = GenerateColumnChart(prompt="@#$$% Chart!", params=valid_params)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["prompt"] == "@#$$% Chart!"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_empty_style_and_config(self):
        tool = GenerateColumnChart(
            prompt="Test", params={"categories": ["A"], "values": [1], "title": "X"}
        )
        result = tool.run()
        assert result["result"]["style"] == {}
        assert result["result"]["config"] == {}

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "categories,values,valid",
        [
            (["A"], [1], True),
            (["A", "B"], [1, 2], True),
            ([], [], True),
            (["A"], [], False),
            (["A", "B"], [1], False),
        ],
    )
    def test_categories_values_validation(self, categories, values, valid):
        params = {"categories": categories, "values": values}
        tool = GenerateColumnChart(prompt="Test", params=params)
        result = tool.run()
        if valid:
            assert result["success"] is True
        else:
            assert result["success"] is False
            assert result["error"]["code"] == "VALIDATION_ERROR"

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_integration_full_workflow(self, valid_params: Dict[str, Any]):
        tool = GenerateColumnChart(prompt="Full Workflow", params=valid_params)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["title"] == "Test Chart"
        assert result["metadata"]["tool_name"] == "generate_column_chart"

    def test_error_formatting_integration(self, tool: GenerateColumnChart):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
