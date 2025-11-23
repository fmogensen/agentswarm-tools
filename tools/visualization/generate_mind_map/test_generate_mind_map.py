"""Tests for generate_mind_map tool."""

import os
from typing import Any, Dict
from unittest.mock import patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.visualization.generate_mind_map import GenerateMindMap


class TestGenerateMindMap:
    """Test suite for GenerateMindMap."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_prompt(self) -> str:
        return "Root\nBranch1: A, B\nBranch2: C"

    @pytest.fixture
    def tool(self, valid_prompt: str) -> GenerateMindMap:
        return GenerateMindMap(prompt=valid_prompt, params={"depth": 3})

    @pytest.fixture
    def simple_tool(self) -> GenerateMindMap:
        return GenerateMindMap(prompt="Root", params={})

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_prompt: str):
        tool = GenerateMindMap(prompt=valid_prompt, params={})
        assert tool.prompt == valid_prompt
        assert tool.params == {}

    def test_metadata_values(self, tool: GenerateMindMap):
        assert tool.tool_name == "generate_mind_map"
        assert tool.tool_category == "visualization"
        assert tool.tool_description.startswith("Generate mind map")

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool: GenerateMindMap):
        """Test successful execution."""
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result
        assert result["result"]["root"] == "Root"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_process_simple(self, simple_tool: GenerateMindMap):
        result = simple_tool.run()
        assert result["success"] is True
        assert result["result"]["root"] == "Root"
        assert result["result"]["branches"] == []

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GenerateMindMap):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["root"] == tool.prompt

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: GenerateMindMap):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["params_used"] is True

    # ========== VALIDATION ERRORS ==========

    def test_empty_prompt_raises(self):
        """Empty prompt raises PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateMindMap(prompt="", params={})

    def test_non_string_prompt_raises(self):
        """Non-string prompt raises PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateMindMap(prompt=123, params={})

    def test_invalid_params_type(self):
        """Non-dict params raise PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateMindMap(prompt="valid", params="not a dict")

    # ========== API ERROR HANDLING ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_api_error_wrapped(self, tool: GenerateMindMap):
        """Process failure returns error dict."""
        with patch.object(tool, "_process", side_effect=Exception("Boom")):
            result = tool.run()
            assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_process_validation_error_passthrough(self, tool: GenerateMindMap):
        """ValidationError from process returns error dict."""
        with patch.object(tool, "_process", side_effect=ValidationError("Bad", tool_name="x")):
            result = tool.run()
            assert result["success"] is False

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,valid,pydantic_error",
        [
            ("Valid prompt", True, False),
            ("A" * 5000, True, False),
            ("", False, True),
            ("   ", False, False),
        ],
    )
    def test_prompt_validation(self, prompt: str, valid: bool, pydantic_error: bool):
        if pydantic_error:
            with pytest.raises(PydanticValidationError):
                GenerateMindMap(prompt=prompt, params={})
        else:
            tool = GenerateMindMap(prompt=prompt, params={})
            result = tool.run()
            if valid:
                assert result["success"] is True
            else:
                assert result["success"] is False

    # ========== EDGE CASES ==========

    def test_unicode_prompt(self):
        tool = GenerateMindMap(prompt="Root\n分支: 一, 二", params={})
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_prompt(self):
        tool = GenerateMindMap(prompt="Root\nBranch@!$: A, B", params={})
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_single_line_prompt(self):
        tool = GenerateMindMap(prompt="OnlyRoot", params={})
        result = tool.run()
        assert result["result"]["branches"] == []

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_missing_colon_in_branches(self):
        tool = GenerateMindMap(prompt="Root\nBranchWithoutColon", params={})
        result = tool.run()
        assert result["result"]["branches"][0]["children"] == []

    # ========== INTEGRATION TESTS ==========

    def test_integration_runs(self, tool: GenerateMindMap):
        result = tool.run()
        assert result["success"] is True

    def test_environment_flag_behavior(self, tool: GenerateMindMap):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            r1 = tool.run()
        with patch.dict("os.environ", {"USE_MOCK_APIS": "false"}):
            r2 = tool.run()
        assert r1["metadata"]["mock_mode"] is True
        assert "mock_mode" not in r2["metadata"]
