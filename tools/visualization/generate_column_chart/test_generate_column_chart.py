"""Tests for generate_column_chart tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any

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

    @pytest.mark.parametrize(
        "prompt,params",
        [
            ("", {"categories": ["A"], "values": [1]}),  # Empty prompt
            ("  ", {"categories": ["A"], "values": [1]}),  # Whitespace prompt
            ("Hello", None),  # Params not dict
            ("Hello", {}),  # Missing categories / values
            ("Hello", {"categories": ["A"], "values": []}),  # Mismatched lengths
            ("Hello", {"categories": "A", "values": [1]}),  # Not lists
        ],
    )
    def test_validation_errors(self, prompt, params):
        with pytest.raises(ValidationError):
            tool = GenerateColumnChart(prompt=prompt, params=params)
            tool.run()

    def test_mismatched_length_validation(self):
        with pytest.raises(ValidationError):
            tool = GenerateColumnChart(
                prompt="Invalid", params={"categories": ["A", "B"], "values": [1]}
            )
            tool.run()

    # ========== API ERROR HANDLING ==========

    def test_api_error_handled(self, tool: GenerateColumnChart):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_prompt(self, valid_params: Dict[str, Any]):
        tool = GenerateColumnChart(prompt="标题", params=valid_params)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["prompt"] == "标题"

    def test_special_chars_prompt(self, valid_params: Dict[str, Any]):
        tool = GenerateColumnChart(prompt="@#$$% Chart!", params=valid_params)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["prompt"] == "@#$$% Chart!"

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

        if valid:
            tool = GenerateColumnChart(prompt="Test", params=params)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(ValidationError):
                tool = GenerateColumnChart(prompt="Test", params=params).run()

    # ========== INTEGRATION TESTS ==========

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
