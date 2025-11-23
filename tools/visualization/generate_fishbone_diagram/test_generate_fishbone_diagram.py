"""Tests for generate_fishbone_diagram tool."""

import os
from typing import Any, Dict
from unittest.mock import patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.visualization.generate_fishbone_diagram import GenerateFishboneDiagram


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

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool: GenerateFishboneDiagram):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result
        assert result["metadata"]["prompt"] == tool.prompt

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
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
        """Empty prompt raises PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateFishboneDiagram(prompt="", params={})

    def test_invalid_params_type_raises_error(self, valid_prompt):
        """Non-dict params raise PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateFishboneDiagram(prompt=valid_prompt, params="not a dict")

    def test_invalid_param_key_raises_error(self, valid_prompt):
        """Unknown param key fails custom validation and returns error dict."""
        tool = GenerateFishboneDiagram(prompt=valid_prompt, params={"unknown": 123})
        result = tool.run()
        assert result["success"] is False

    def test_invalid_max_branches_value(self, valid_prompt):
        """Invalid max_branches fails custom validation and returns error dict."""
        tool = GenerateFishboneDiagram(prompt=valid_prompt, params={"max_branches": 0})
        result = tool.run()
        assert result["success"] is False

    # ========== API ERROR TESTS ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_api_error_propagates(self, tool: GenerateFishboneDiagram):
        """Process failure returns error dict."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASE TESTS ==========

    def test_unicode_prompt(self):
        tool = GenerateFishboneDiagram(prompt="质量问题分析", params={})
        result = tool.run()
        assert result["success"] is True

    def test_special_character_prompt(self):
        tool = GenerateFishboneDiagram(prompt="failure @#$%^&*()", params={})
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_max_branches_greater_than_default(self):
        tool = GenerateFishboneDiagram(prompt="test", params={"max_branches": 10})
        result = tool.run()
        assert len(result["result"]["causes"]) == 6  # max categories available

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,params,valid,pydantic_error",
        [
            ("valid", {}, True, False),
            ("analysis", {"format": "text"}, True, False),
            ("root cause", {"max_branches": 3}, True, False),
            ("", {}, False, True),
            ("test", {"invalid": 123}, False, False),
            ("test", {"max_branches": -1}, False, False),
        ],
    )
    def test_parameter_validation(self, prompt, params, valid, pydantic_error):
        if pydantic_error:
            with pytest.raises(PydanticValidationError):
                GenerateFishboneDiagram(prompt=prompt, params=params)
        else:
            tool = GenerateFishboneDiagram(prompt=prompt, params=params)
            result = tool.run()
            if valid:
                assert result["success"] is True
            else:
                assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    def test_environment_integration(self, tool: GenerateFishboneDiagram):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            result = tool.run()
        assert result["success"] is True

    def test_full_workflow(self):
        tool = GenerateFishboneDiagram(prompt="workflow test", params={"max_branches": 5})
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]["causes"]) <= 5
