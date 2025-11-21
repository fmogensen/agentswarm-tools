"""Tests for generate_radar_chart tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any
import math

from tools.visualization.generate_radar_chart import GenerateRadarChart
from shared.errors import ValidationError, APIError


class TestGenerateRadarChart:
    """Test suite for GenerateRadarChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_data(self) -> Dict[str, float]:
        return {"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0}

    @pytest.fixture
    def tool(self, valid_data: Dict[str, float]) -> GenerateRadarChart:
        return GenerateRadarChart(prompt="Generate chart", params={"data": valid_data})

    # ========== INITIALIZATION TESTS ==========

    def test_tool_metadata(self, tool: GenerateRadarChart):
        assert tool.tool_name == "generate_radar_chart"
        assert tool.tool_category == "visualization"

    def test_initialization_stores_parameters(self, valid_data: Dict[str, float]):
        tool = GenerateRadarChart(prompt="Test", params={"data": valid_data})
        assert tool.prompt == "Test"
        assert tool.params["data"] == valid_data

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool: GenerateRadarChart):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "points" in result["result"]
        assert result["result"]["dimension_count"] == 4

    def test_process_generates_correct_angles(self, tool: GenerateRadarChart):
        out = tool._process()
        points = out["points"]
        assert points[0]["angle"] == 0
        assert math.isclose(points[1]["angle"], 2 * math.pi / 4, rel_tol=1e-6)

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GenerateRadarChart):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: GenerateRadarChart):
        result = tool.run()
        assert result["success"] is True
        assert "points" in result["result"]

    # ========== ERROR CASES ==========

    def test_missing_prompt_raises_error(self):
        with pytest.raises(ValidationError):
            GenerateRadarChart(
                prompt="", params={"data": {"a": 1, "b": 2, "c": 3, "d": 4}}
            ).run()

    def test_params_not_dict_raises_error(self):
        with pytest.raises(ValidationError):
            GenerateRadarChart(prompt="x", params="not a dict").run()

    def test_missing_data_key_raises_error(self):
        with pytest.raises(ValidationError):
            GenerateRadarChart(prompt="x", params={}).run()

    def test_not_enough_dimensions_raises_error(self):
        with pytest.raises(ValidationError):
            GenerateRadarChart(prompt="x", params={"data": {"a": 1, "b": 2}}).run()

    def test_non_numeric_values_raises_error(self):
        with pytest.raises(ValidationError):
            GenerateRadarChart(
                prompt="x", params={"data": {"a": 1, "b": "bad", "c": 3, "d": 4}}
            ).run()

    def test_api_error(self, tool: GenerateRadarChart):
        with patch.object(tool, "_process", side_effect=Exception("Fail")):
            with pytest.raises(APIError):
                tool.run()

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,params,valid",
        [
            ("ok", {"data": {"a": 1, "b": 2, "c": 3, "d": 4}}, True),
            ("", {"data": {"a": 1, "b": 2, "c": 3, "d": 4}}, False),
            ("ok", {"data": {"a": 1, "b": 2, "c": 3}}, False),
            ("ok", {"data": {"a": 1, "b": "bad", "c": 3, "d": 4}}, False),
        ],
    )
    def test_param_validation_matrix(self, prompt, params, valid):
        if valid:
            tool = GenerateRadarChart(prompt=prompt, params=params)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                GenerateRadarChart(prompt=prompt, params=params).run()

    # ========== EDGE CASES ==========

    def test_unicode_prompt(self, valid_data: Dict[str, float]):
        tool = GenerateRadarChart(prompt="生成雷达图", params={"data": valid_data})
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_in_prompt(self, valid_data: Dict[str, float]):
        tool = GenerateRadarChart(prompt="@#% Radar!", params={"data": valid_data})
        result = tool.run()
        assert result["success"] is True

    def test_zero_values(self):
        data = {"a": 0, "b": 0, "c": 0, "d": 0}
        tool = GenerateRadarChart(prompt="zero", params={"data": data})
        result = tool.run()
        assert all(p["radius"] == 0 for p in result["result"]["points"])

    # ========== INTEGRATION TESTS ==========

    def test_integration_basic(self, tool: GenerateRadarChart):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["tool_name"] == "generate_radar_chart"

    def test_error_formatting_integration(self, tool: GenerateRadarChart):
        with patch.object(tool, "_execute", side_effect=ValueError("Boom")):
            output = tool.run()
            assert output.get("success") is False or "error" in output
