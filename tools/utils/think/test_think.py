"""Tests for think tool."""

import pytest
from unittest.mock import patch
from pydantic import ValidationError as PydanticValidationError
from tools.utils.think import Think
from shared.errors import ValidationError, APIError


class TestThink:
    """Test suite for Think."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_thought(self) -> str:
        return "I am thinking."

    @pytest.fixture
    def tool(self, valid_thought: str) -> Think:
        return Think(thought=valid_thought)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization_success(self, valid_thought: str):
        tool = Think(thought=valid_thought)
        assert tool.thought == valid_thought
        assert tool.tool_name == "think"
        assert tool.tool_category == "utils"

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool: Think):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["stored"] == tool.thought

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_metadata_correct(self, tool: Think):
        result = tool.run()
        metadata = result["metadata"]
        assert metadata["tool_name"] == "think"
        assert metadata["tool_version"] == "1.0.0"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: Think):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["stored"].startswith("[MOCK]")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: Think):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["stored"] == tool.thought

    # ========== ERROR CASES ==========

    def test_invalid_empty_string(self):
        # Empty string fails Pydantic min_length=1 validation at construction
        with pytest.raises(PydanticValidationError):
            Think(thought="")

    def test_invalid_whitespace(self):
        # Whitespace passes Pydantic but fails custom validation at runtime
        tool = Think(thought="   ")
        result = tool.run()
        assert result["success"] is False

    def test_invalid_non_string(self):
        with pytest.raises(PydanticValidationError):
            Think(thought=None)  # type: ignore

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_propagates(self, tool: Think):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_unicode_thought(self):
        tool = Think(thought="思考中...")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["stored"] == "思考中..."

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_special_characters(self):
        thought = "@#$%^&*() internal thought!"
        tool = Think(thought=thought)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["stored"] == thought

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_long_thought(self):
        long_text = "a" * 5000
        tool = Think(thought=long_text)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["stored"] == long_text

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "thought,expected_valid,is_pydantic_error",
        [
            ("Valid thought", True, False),
            ("a" * 300, True, False),
            ("", False, True),  # Empty string fails Pydantic min_length=1
            ("   ", False, False),  # Whitespace passes Pydantic, fails custom validation
            (None, False, True),  # None fails Pydantic type check
        ],
    )
    def test_param_validation(self, thought, expected_valid, is_pydantic_error):
        if expected_valid:
            tool = Think(thought=thought)
            result = tool.run()
            assert result["success"] is True
        elif is_pydantic_error:
            with pytest.raises(PydanticValidationError):
                Think(thought=thought)
        else:
            tool = Think(thought=thought)
            result = tool.run()
            assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    def test_rate_limiting_integration(self, tool: Think):
        result = tool.run()
        assert result["success"] is True

    def test_error_formatting_integration(self, tool: Think):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
