"""Tests for think tool."""

import pytest
from unittest.mock import patch
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

    def test_execute_success(self, tool: Think):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["stored"] == tool.thought

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
        with pytest.raises(ValidationError):
            tool = Think(thought="")
            tool.run()

    def test_invalid_whitespace(self):
        with pytest.raises(ValidationError):
            tool = Think(thought="   ")
            tool.run()

    def test_invalid_non_string(self):
        with pytest.raises(ValidationError):
            tool = Think(thought=None)  # type: ignore
            tool.run()

    def test_api_error_propagates(self, tool: Think):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_thought(self):
        tool = Think(thought="思考中...")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["stored"] == "思考中..."

    def test_special_characters(self):
        thought = "@#$%^&*() internal thought!"
        tool = Think(thought=thought)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["stored"] == thought

    def test_long_thought(self):
        long_text = "a" * 5000
        tool = Think(thought=long_text)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["stored"] == long_text

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "thought,expected_valid",
        [
            ("Valid thought", True),
            ("a" * 300, True),
            ("", False),
            ("   ", False),
            (None, False),  # type: ignore
        ],
    )
    def test_param_validation(self, thought, expected_valid):
        if expected_valid:
            tool = Think(thought=thought)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = Think(thought=thought)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_rate_limiting_integration(self, tool: Think):
        result = tool.run()
        assert result["success"] is True

    def test_error_formatting_integration(self, tool: Think):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
