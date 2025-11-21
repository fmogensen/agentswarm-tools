"""Tests for phone_call tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any
import os

from tools.communication.phone_call import PhoneCall
from shared.errors import ValidationError, APIError


class TestPhoneCall:
    """Test suite for PhoneCall."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        return "Call John about the meeting."

    @pytest.fixture
    def tool(self, valid_input: str) -> PhoneCall:
        return PhoneCall(input=valid_input)

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self, valid_input: str):
        tool = PhoneCall(input=valid_input)
        assert tool.input == valid_input
        assert tool.tool_name == "phone_call"
        assert tool.tool_category == "communication"

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool: PhoneCall):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "call_card" in result["result"]
        assert result["result"]["call_card"]["type"] == "ai_phone_call"
        assert result["metadata"]["mock_mode"] is False

    def test_metadata_correct(self, tool: PhoneCall):
        assert tool.tool_name == "phone_call"
        assert tool.tool_category == "communication"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: PhoneCall):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["call_card"]["type"] == "mock_phone_call"

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_input", ["", "   ", None])
    def test_input_empty_raises_error(self, bad_input):
        with pytest.raises(ValidationError):
            tool = PhoneCall(input=bad_input)
            tool.run()

    def test_input_too_long_raises_error(self):
        too_long = "a" * 2001
        with pytest.raises(ValidationError):
            tool = PhoneCall(input=too_long)
            tool.run()

    # ========== ERROR CASE TESTS ==========

    def test_api_error_raised(self, tool: PhoneCall):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_input(self):
        tool = PhoneCall(input="讨论一下项目进展")
        result = tool.run()
        assert result["success"] is True

    def test_special_characters(self):
        text = "@#$%^&*() important call!"
        tool = PhoneCall(input=text)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["call_card"]["text"] == text

    def test_min_length_valid(self):
        tool = PhoneCall(input="a")
        result = tool.run()
        assert result["success"] is True

    def test_call_id_generation(self, tool: PhoneCall):
        cid = tool._generate_call_id()
        assert isinstance(cid, str)
        assert len(cid) > 0

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "text, expected_valid",
        [
            ("Valid call text", True),
            ("x" * 2000, True),
            ("", False),
            ("   ", False),
            ("x" * 2001, False),
        ],
    )
    def test_parameter_validation(self, text, expected_valid):
        if expected_valid:
            tool = PhoneCall(input=text)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = PhoneCall(input=text)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_error_formatting_integration(self, tool: PhoneCall):
        with patch.object(tool, "_execute", side_effect=ValueError("Boom")):
            result = tool.run()
            assert result.get("success") is False or "error" in result

    def test_environment_mock_toggle(self, tool: PhoneCall):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            r1 = tool.run()
        with patch.dict("os.environ", {"USE_MOCK_APIS": "false"}):
            r2 = tool.run()

        assert r1["metadata"]["mock_mode"] is True
        assert r2["metadata"]["mock_mode"] is False
