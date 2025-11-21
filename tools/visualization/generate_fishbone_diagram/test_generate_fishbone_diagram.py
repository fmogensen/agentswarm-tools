"""Tests for generate_fishbone_diagram tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any
import os

from tools.visualization.generate_fishbone_diagram import GenerateFishboneDiagram
from shared.errors import ValidationError, APIError


class TestGenerateFishboneDiagram:
    """Test suite for GenerateFishboneDiagram."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_prompt(self) -> str:
        return "Increase customer satisfaction"

    @pytest.fixture
    def valid_params(self) -> Dict[str, Any]:
        return {"format": "text", "max_branches": 4}

    @pytest.fixture
    def tool(self, valid_prompt, valid_params) -> GenerateFishboneDiagram:
        return GenerateFishboneDiagram(prompt=valid_prompt, params=valid_params)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization_success(self, valid_prompt, valid_params):
        tool = GenerateFishboneDiagram(prompt=valid_prompt, params=valid_params)
        assert tool.prompt == valid_prompt
        assert tool.params == valid_params
        assert tool.tool_name == "generate_fishbone_diagram"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool: GenerateFishboneDiagram):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result
        assert result["metadata"]["prompt"] == tool.prompt

    def test_process_generates_correct_categories(self):
        tool = GenerateFishboneDiagram(prompt="test", params={"max_branches": 3})
        result = tool.run()
        causes = result["result"]["causes"]
        assert len(causes) == 3

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock_results(self, tool: GenerateFishboneDiagram):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "Mock Category 1" in result["result"]["causes"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode_processes(self, tool: GenerateFishboneDiagram):
        result = tool.run()
        assert result["success"] is True
        assert "effect" in result["result"]

    # ========== VALIDATION TESTS ==========

    def test_invalid_prompt_raises_validation_error(self):
        with pytest.raises(ValidationError):
            tool = GenerateFishboneDiagram(prompt="", params={})
            tool.run()

    def test_invalid_params_type_raises_error(self, valid_prompt):
        with pytest.raises(ValidationError):
            tool = GenerateFishboneDiagram(prompt=valid_prompt, params="not a dict")
            tool.run()

    def test_invalid_param_key_raises_error(self, valid_prompt):
        with pytest.raises(ValidationError):
            tool = GenerateFishboneDiagram(prompt=valid_prompt, params={"unknown": 123})
            tool.run()

    def test_invalid_max_branches_value(self, valid_prompt):
        with pytest.raises(ValidationError):
            tool = GenerateFishboneDiagram(
                prompt=valid_prompt, params={"max_branches": 0}
            )
            tool.run()

    # ========== API ERROR TESTS ==========

    def test_api_error_propagates(self, tool: GenerateFishboneDiagram):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError) as exc:
                tool.run()
            assert "API failed" in str(exc.value)

    # ========== EDGE CASE TESTS ==========

    def test_unicode_prompt(self):
        tool = GenerateFishboneDiagram(prompt="质量问题分析", params={})
        result = tool.run()
        assert result["success"] is True

    def test_special_character_prompt(self):
        tool = GenerateFishboneDiagram(prompt="failure @#$%^&*()", params={})
        result = tool.run()
        assert result["success"] is True

    def test_max_branches_greater_than_default(self):
        tool = GenerateFishboneDiagram(prompt="test", params={"max_branches": 10})
        result = tool.run()
        assert len(result["result"]["causes"]) == 6  # max categories available

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,params,valid",
        [
            ("valid", {}, True),
            ("analysis", {"format": "text"}, True),
            ("root cause", {"max_branches": 3}, True),
            ("", {}, False),
            ("test", {"invalid": 123}, False),
            ("test", {"max_branches": -1}, False),
        ],
    )
    def test_parameter_validation(self, prompt, params, valid):
        if valid:
            tool = GenerateFishboneDiagram(prompt=prompt, params=params)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = GenerateFishboneDiagram(prompt=prompt, params=params)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_environment_integration(self, tool: GenerateFishboneDiagram):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            result = tool.run()
        assert result["success"] is True

    def test_full_workflow(self):
        tool = GenerateFishboneDiagram(
            prompt="workflow test", params={"max_branches": 5}
        )
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]["causes"]) <= 5
