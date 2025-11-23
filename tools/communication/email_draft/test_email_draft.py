"""Tests for email_draft tool."""

from typing import Any, Dict
from unittest.mock import patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.communication.email_draft import EmailDraft


class TestEmailDraft:
    """Test suite for EmailDraft."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        return "This is a test email draft input."

    @pytest.fixture
    def tool(self, valid_input: str) -> EmailDraft:
        return EmailDraft(input=valid_input)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_input: str):
        tool = EmailDraft(input=valid_input)
        assert tool.input == valid_input
        assert tool.tool_name == "email_draft"
        assert tool.tool_category == "communication"

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool: EmailDraft):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mode"] == "generated"
        assert "subject" in result["result"]
        assert "body_text" in result["result"]
        assert "body_html" in result["result"]
        assert "metadata" in result

    def test_metadata_correct(self, tool: EmailDraft):
        result = tool.run()
        metadata = result["metadata"]
        assert metadata["tool_name"] == "email_draft"
        assert metadata["tool_version"] == "1.0.0"

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: EmailDraft):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mode"] == "mock"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: EmailDraft):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mode"] == "generated"

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_input", [None])
    def test_invalid_input_raises_validation_error_type(self, bad_input):
        with pytest.raises(PydanticValidationError):
            EmailDraft(input=bad_input)

    @pytest.mark.parametrize("bad_input", ["", "   "])
    def test_invalid_input_raises_validation_error_empty(self, bad_input):
        with pytest.raises(ValidationError):
            tool = EmailDraft(input=bad_input)
            tool._execute()

    # ========== ERROR CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_from_process(self, tool: EmailDraft):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    def test_unicode_input(self):
        tool = EmailDraft(input="こんにちは世界")
        result = tool.run()
        assert result["success"] is True
        assert "こんにちは世界" in result["result"]["body_text"]

    def test_special_characters_input(self):
        special = "@#$%^&*()_+=-!~"
        tool = EmailDraft(input=special)
        result = tool.run()
        assert result["success"] is True
        assert special in result["result"]["body_text"]

    def test_very_long_input(self):
        long_input = "a" * 5000
        tool = EmailDraft(input=long_input)
        result = tool.run()
        assert result["success"] is True
        assert long_input[:60] in result["result"]["subject"]

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "input_value,valid",
        [
            ("valid text", True),
            (" another valid text ", True),
            ("", False),
            ("   ", False),
            (None, False),
        ],
    )
    def test_input_validation(self, input_value, valid):
        if valid:
            tool = EmailDraft(input=input_value)
            result = tool.run()
            assert result["success"] is True
        else:
            if input_value is None:
                with pytest.raises(PydanticValidationError):
                    EmailDraft(input=input_value)
            else:
                with pytest.raises(ValidationError):
                    tool = EmailDraft(input=input_value)
                    tool._execute()

    # ========== INTEGRATION TESTS ==========

    def test_integration_safe_run(self, tool: EmailDraft):
        result = tool.run()
        assert result["success"] is True

    def test_integration_error_formatting(self, tool: EmailDraft):
        with patch.object(tool, "_execute", side_effect=ValueError("Test err")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
