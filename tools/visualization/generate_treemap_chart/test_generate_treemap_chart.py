"""Tests for generate_treemap_chart tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any

from tools.visualization.generate_treemap_chart import GenerateTreemapChart
from shared.errors import ValidationError, APIError


class TestGenerateTreemapChart:
    """Test suite for GenerateTreemapChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_data(self) -> Dict[str, Any]:
        return {
            "data": {
                "name": "root",
                "children": [
                    {"name": "A", "value": 10},
                    {"name": "B", "value": 20},
                ],
            }
        }

    @pytest.fixture
    def tool(self, valid_data: Dict[str, Any]) -> GenerateTreemapChart:
        return GenerateTreemapChart(prompt="Test treemap", params=valid_data)

    @pytest.fixture
    def list_data_tool(self) -> GenerateTreemapChart:
        return GenerateTreemapChart(
            prompt="List data",
            params={
                "data": [
                    {"name": "Item1", "value": 1},
                    {"name": "Item2", "value": 2},
                ]
            },
        )

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: GenerateTreemapChart):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["chart_type"] == "treemap"
        assert isinstance(result["result"]["nodes"], list)

    def test_metadata_correct(self, tool: GenerateTreemapChart):
        assert tool.tool_name == "generate_treemap_chart"
        assert tool.tool_category == "visualization"

    def test_list_data_success(self, list_data_tool: GenerateTreemapChart):
        result = list_data_tool.run()
        assert result["success"] is True
        assert len(result["result"]["nodes"]) == 2

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GenerateTreemapChart):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    # ========== ERROR CASES ==========

    def test_missing_prompt_raises(self, valid_data):
        with pytest.raises(ValidationError):
            tool = GenerateTreemapChart(prompt="", params=valid_data)
            tool.run()

    def test_params_not_dict(self):
        with pytest.raises(ValidationError):
            tool = GenerateTreemapChart(prompt="ok", params="not-a-dict")
            tool.run()

    def test_missing_data_field(self):
        with pytest.raises(ValidationError):
            tool = GenerateTreemapChart(prompt="ok", params={})
            tool.run()

    def test_data_wrong_type(self):
        with pytest.raises(ValidationError):
            tool = GenerateTreemapChart(prompt="ok", params={"data": 123})
            tool.run()

    def test_children_not_list(self):
        tool = GenerateTreemapChart(
            prompt="test", params={"data": {"name": "root", "children": "invalid"}}
        )
        with pytest.raises(APIError):
            tool.run()

    def test_api_error_from_process(self, tool: GenerateTreemapChart):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

    def test_node_without_name(self):
        tool = GenerateTreemapChart(prompt="test", params={"data": {"value": 10}})
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["nodes"][0]["name"] == "Unnamed"

    def test_empty_children_list(self):
        tool = GenerateTreemapChart(
            prompt="test", params={"data": {"name": "root", "children": []}}
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["nodes"][0]["name"] == "root"

    def test_unicode_prompt(self, valid_data):
        tool = GenerateTreemapChart(prompt="可视化", params=valid_data)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "data",
        [
            {"data": {"name": "x", "value": 1}},
            {"data": {"label": "y", "children": [{"name": "z"}]}},
            {"data": [{"name": "a"}, {"label": "b"}]},
        ],
    )
    def test_various_valid_data(self, data):
        tool = GenerateTreemapChart(prompt="test", params=data)
        result = tool.run()
        assert result["success"] is True

    @pytest.mark.parametrize(
        "prompt,expected_valid",
        [
            ("valid", True),
            ("   ", False),
            ("", False),
        ],
    )
    def test_prompt_validation(self, prompt, expected_valid, valid_data):
        if expected_valid:
            tool = GenerateTreemapChart(prompt=prompt, params=valid_data)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(ValidationError):
                tool = GenerateTreemapChart(prompt=prompt, params=valid_data)
                tool.run()


class TestGenerateTreemapChartIntegration:
    """Integration tests with shared modules."""

    def test_run_integration(self, tool: GenerateTreemapChart):
        result = tool.run()
        assert result["success"] is True
        assert "metadata" in result

    def test_error_formatting(self, tool: GenerateTreemapChart):
        with patch.object(tool, "_execute", side_effect=ValueError("boom")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
