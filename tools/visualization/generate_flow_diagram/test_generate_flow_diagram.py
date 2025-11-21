"""Tests for generate_flow_diagram tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any

from tools.visualization.generate_flow_diagram import GenerateFlowDiagram
from shared.errors import ValidationError, APIError


class TestGenerateFlowDiagram:
    """Test suite for GenerateFlowDiagram."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_prompt(self) -> str:
        return "Step A -> Step B -> Step C"

    @pytest.fixture
    def tool(self, valid_prompt: str) -> GenerateFlowDiagram:
        return GenerateFlowDiagram(prompt=valid_prompt, params={"level": "basic"})

    @pytest.fixture
    def mock_env_true(self):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            yield

    @pytest.fixture
    def mock_env_false(self):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "false"}):
            yield

    # ========== INITIALIZATION TESTS ==========

    def test_init_success(self, valid_prompt: str):
        tool = GenerateFlowDiagram(prompt=valid_prompt, params={})
        assert tool.prompt == valid_prompt
        assert tool.params == {}

    def test_metadata(self, tool: GenerateFlowDiagram):
        assert tool.tool_name == "generate_flow_diagram"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: GenerateFlowDiagram, mock_env_false):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "diagram_text" in result["result"]

    def test_step_extraction_multiple(self, tool: GenerateFlowDiagram):
        steps = tool._extract_steps_from_prompt(tool.prompt)
        assert steps == ["Step A", "Step B", "Step C"]

    # ========== MOCK MODE ==========

    def test_mock_mode_true(self, tool: GenerateFlowDiagram, mock_env_true):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "diagram_text" in result["result"]

    def test_mock_mode_false(self, tool: GenerateFlowDiagram, mock_env_false):
        result = tool.run()
        assert result["success"] is True
        assert "mock_mode" not in result["metadata"]

    # ========== VALIDATION TESTS ==========

    def test_empty_prompt_raises(self):
        with pytest.raises(ValidationError):
            tool = GenerateFlowDiagram(prompt="", params={})
            tool.run()

    def test_invalid_params_type(self, valid_prompt: str):
        with pytest.raises(ValidationError):
            tool = GenerateFlowDiagram(prompt=valid_prompt, params="not_dict")
            tool.run()

    def test_extract_steps_empty_failure(self):
        tool = GenerateFlowDiagram(prompt=" , , ", params={})
        with pytest.raises(ValidationError):
            tool._extract_steps_from_prompt(tool.prompt)

    # ========== ERROR HANDLING TESTS ==========

    def test_api_error_propagates(self, tool: GenerateFlowDiagram):
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            with pytest.raises(APIError):
                tool.run()

    def test_process_internal_error_wrapped(self, tool: GenerateFlowDiagram):
        with patch.object(
            tool, "_extract_steps_from_prompt", side_effect=Exception("fail")
        ):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_prompt(self):
        tool = GenerateFlowDiagram(prompt="開始 -> 終了", params={})
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_prompt(self):
        tool = GenerateFlowDiagram(prompt="A@1 -> B#2 -> C$3", params={})
        result = tool.run()
        assert result["success"] is True

    def test_single_word_prompt(self):
        tool = GenerateFlowDiagram(prompt="SingleStep", params={})
        result = tool.run()
        assert result["result"]["step_count"] == 1

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,expected_valid",
        [
            ("A -> B -> C", True),
            ("OneStep", True),
            ("", False),
            ("   ", False),
        ],
    )
    def test_prompt_validation(self, prompt: str, expected_valid: bool):
        if expected_valid:
            tool = GenerateFlowDiagram(prompt=prompt, params={})
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = GenerateFlowDiagram(prompt=prompt, params={})
                tool.run()

    @pytest.mark.parametrize(
        "params,expected_valid",
        [
            ({"a": 1}, True),
            ({}, True),
            ("string", False),
            (123, False),
        ],
    )
    def test_params_validation(self, valid_prompt: str, params, expected_valid: bool):
        if expected_valid:
            tool = GenerateFlowDiagram(prompt=valid_prompt, params=params)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = GenerateFlowDiagram(prompt=valid_prompt, params=params)
                tool.run()

    # ========== HELPER FUNCTION TESTS ==========

    def test_extract_steps_with_commas(self):
        tool = GenerateFlowDiagram(prompt="A, B, C", params={})
        steps = tool._extract_steps_from_prompt(tool.prompt)
        assert steps == ["A", "B", "C"]

    # ========== INTEGRATION TESTS ==========

    def test_full_workflow(self):
        tool = GenerateFlowDiagram(
            prompt="Start -> Middle -> End", params={"style": "modern"}
        )
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["tool_name"] == "generate_flow_diagram"

    def test_error_formatting(self, tool: GenerateFlowDiagram):
        with patch.object(tool, "_execute", side_effect=ValueError("TestErr")):
            output = tool.run()
            assert output.get("success") is False or "error" in output
