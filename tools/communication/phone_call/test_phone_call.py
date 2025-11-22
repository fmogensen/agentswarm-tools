"""Tests for phone_call tool."""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any
import os
from pydantic import ValidationError as PydanticValidationError

from tools.communication.phone_call import PhoneCall
from shared.errors import ValidationError, APIError, AuthenticationError


class TestPhoneCall:
    """Test suite for PhoneCall."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_phone_number(self) -> str:
        return "+15551234567"

    @pytest.fixture
    def valid_message(self) -> str:
        return "Hello, this is a reminder about your appointment."

    @pytest.fixture
    def tool(self, valid_phone_number: str, valid_message: str) -> PhoneCall:
        return PhoneCall(phone_number=valid_phone_number, message=valid_message)

    @pytest.fixture
    def mock_twilio_call(self):
        """Mock Twilio call response."""
        mock_call = MagicMock()
        mock_call.sid = "CA1234567890abcdef1234567890abcdef"
        mock_call.status = "queued"
        mock_call.direction = "outbound-api"
        mock_call.to = "+15551234567"
        mock_call.from_ = "+15559876543"
        mock_call.date_created = None
        mock_call.price = None
        mock_call.price_unit = "USD"
        return mock_call

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self, valid_phone_number: str, valid_message: str):
        tool = PhoneCall(phone_number=valid_phone_number, message=valid_message)
        assert tool.phone_number == valid_phone_number
        assert tool.message == valid_message
        assert tool.language == "en-US"
        assert tool.wait_for_response == False
        assert tool.voice is None
        assert tool.tool_name == "phone_call"
        assert tool.tool_category == "communication"

    def test_tool_initialization_with_optional_params(self):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Test message",
            voice="female",
            language="es-ES",
            wait_for_response=True
        )
        assert tool.voice == "female"
        assert tool.language == "es-ES"
        assert tool.wait_for_response == True

    # ========== HAPPY PATH TESTS ==========

    @patch.dict("os.environ", {
        "USE_MOCK_APIS": "false",
        "TWILIO_ACCOUNT_SID": "AC1234567890",
        "TWILIO_AUTH_TOKEN": "fake_token",
        "TWILIO_PHONE_NUMBER": "+15559876543"
    })
    @patch("tools.communication.phone_call.phone_call.TWILIO_AVAILABLE", True)
    @patch("twilio.rest.Client")
    def test_execute_success(self, mock_client_class, tool, mock_twilio_call):
        mock_client = MagicMock()
        mock_client.calls.create.return_value = mock_twilio_call
        mock_client_class.return_value = mock_client

        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["result"]["call_sid"] == mock_twilio_call.sid
        assert result["result"]["status"] == "queued"
        assert result["metadata"]["mock_mode"] is False
        mock_client.calls.create.assert_called_once()

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: PhoneCall):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "call_sid" in result["result"]
        assert result["result"]["status"] == "completed"
        assert result["result"]["to"] == tool.phone_number
        assert result["result"]["message_delivered"] == tool.message

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_with_voice(self):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Test",
            voice="male"
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["voice_used"] == "male"

    # ========== VALIDATION TESTS ==========

    def test_empty_phone_number_raises_error(self):
        with pytest.raises(PydanticValidationError):
            PhoneCall(phone_number="", message="Test message")

    def test_empty_message_raises_error(self):
        with pytest.raises(PydanticValidationError):
            PhoneCall(phone_number="+15551234567", message="")

    def test_invalid_phone_format_no_plus(self):
        tool = PhoneCall(phone_number="15551234567", message="Test")
        result = tool.run()
        assert result["success"] is False
        error_msg = result.get("error", {}).get("message", "") if isinstance(result.get("error"), dict) else str(result.get("error", ""))
        assert "international format" in error_msg

    def test_invalid_phone_format_too_short(self):
        # Pydantic validates min_length before runtime validation
        with pytest.raises(PydanticValidationError):
            tool = PhoneCall(phone_number="+1555", message="Test")

    def test_invalid_phone_format_letters(self):
        tool = PhoneCall(phone_number="+1555abc1234", message="Test")
        result = tool.run()
        assert result["success"] is False

    def test_whitespace_phone_number(self):
        tool = PhoneCall(phone_number="   +15551234567   ", message="Test")
        # Should pass validation after strip
        result = tool.run()
        # In mock mode, should succeed
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            result = tool.run()
            assert result["success"] is True

    def test_whitespace_message(self):
        tool = PhoneCall(phone_number="+15551234567", message="   ")
        result = tool.run()
        assert result["success"] is False
        error_msg = result.get("error", {}).get("message", "") if isinstance(result.get("error"), dict) else str(result.get("error", ""))
        assert "message cannot be empty" in error_msg

    def test_invalid_voice_type(self):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Test",
            voice="robot"  # Invalid voice
        )
        result = tool.run()
        assert result["success"] is False
        error_msg = result.get("error", {}).get("message", "") if isinstance(result.get("error"), dict) else str(result.get("error", ""))
        assert "voice must be one of" in error_msg

    def test_invalid_language_format(self):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Test",
            language="english"  # Invalid format
        )
        result = tool.run()
        assert result["success"] is False
        error_msg = result.get("error", {}).get("message", "") if isinstance(result.get("error"), dict) else str(result.get("error", ""))
        assert "language must be in format" in error_msg

    def test_message_too_long(self):
        long_message = "a" * 2001
        with pytest.raises(PydanticValidationError):
            PhoneCall(phone_number="+15551234567", message=long_message)

    # ========== ERROR HANDLING TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("shared.base.get_rate_limiter")
    def test_missing_twilio_credentials(self, mock_rate_limiter, tool: PhoneCall):
        # Mock rate limiter to avoid interference
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit.return_value = None
        mock_rate_limiter.return_value = mock_limiter

        # Remove all Twilio env vars
        env_clean = os.environ.copy()
        for key in ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]:
            env_clean.pop(key, None)

        with patch.dict("os.environ", env_clean, clear=True):
            with patch("tools.communication.phone_call.phone_call.TWILIO_AVAILABLE", True):
                result = tool.run()
                assert result["success"] is False
                error = result.get("error", {})
                assert "TWILIO_ACCOUNT_SID" in str(error) or "AUTH_ERROR" in str(error)

    @patch.dict("os.environ", {
        "USE_MOCK_APIS": "false",
        "TWILIO_ACCOUNT_SID": "AC1234567890",
        "TWILIO_AUTH_TOKEN": "fake_token"
    })
    @patch("tools.communication.phone_call.phone_call.TWILIO_AVAILABLE", True)
    @patch("shared.base.get_rate_limiter")
    def test_missing_from_number(self, mock_rate_limiter, tool: PhoneCall):
        # Mock rate limiter to avoid interference
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit.return_value = None
        mock_rate_limiter.return_value = mock_limiter

        result = tool.run()
        assert result["success"] is False
        error_msg = result.get("error", {}).get("message", "") if isinstance(result.get("error"), dict) else str(result.get("error", ""))
        assert "TWILIO_PHONE_NUMBER" in error_msg

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("tools.communication.phone_call.phone_call.TWILIO_AVAILABLE", False)
    @patch("shared.base.get_rate_limiter")
    def test_twilio_not_installed(self, mock_rate_limiter, tool: PhoneCall):
        # Mock rate limiter to avoid interference
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit.return_value = None
        mock_rate_limiter.return_value = mock_limiter

        result = tool.run()
        assert result["success"] is False
        error_msg = result.get("error", {}).get("message", "") if isinstance(result.get("error"), dict) else str(result.get("error", ""))
        assert "twilio package not installed" in error_msg

    @patch.dict("os.environ", {
        "USE_MOCK_APIS": "false",
        "TWILIO_ACCOUNT_SID": "AC1234567890",
        "TWILIO_AUTH_TOKEN": "fake_token",
        "TWILIO_PHONE_NUMBER": "+15559876543"
    })
    @patch("tools.communication.phone_call.phone_call.TWILIO_AVAILABLE", True)
    @patch("twilio.rest.Client")
    @patch("shared.base.get_rate_limiter")
    def test_twilio_api_error(self, mock_rate_limiter, mock_client_class, tool):
        from twilio.base.exceptions import TwilioRestException

        # Mock rate limiter to avoid interference
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit.return_value = None
        mock_rate_limiter.return_value = mock_limiter

        mock_client = MagicMock()
        mock_error = TwilioRestException(
            status=400,
            uri="/mock/uri",
            msg="Invalid phone number",
            code=21211
        )
        mock_client.calls.create.side_effect = mock_error
        mock_client_class.return_value = mock_client

        result = tool.run()
        assert result["success"] is False
        error_msg = result.get("error", {}).get("message", "") if isinstance(result.get("error"), dict) else str(result.get("error", ""))
        assert "Invalid phone number" in error_msg

    @patch.dict("os.environ", {
        "USE_MOCK_APIS": "false",
        "TWILIO_ACCOUNT_SID": "AC1234567890",
        "TWILIO_AUTH_TOKEN": "fake_token",
        "TWILIO_PHONE_NUMBER": "+15559876543"
    })
    @patch("tools.communication.phone_call.phone_call.TWILIO_AVAILABLE", True)
    @patch("twilio.rest.Client")
    @patch("shared.base.get_rate_limiter")
    def test_twilio_auth_error(self, mock_rate_limiter, mock_client_class, tool):
        from twilio.base.exceptions import TwilioRestException

        # Mock rate limiter to avoid interference
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit.return_value = None
        mock_rate_limiter.return_value = mock_limiter

        mock_client = MagicMock()
        mock_error = TwilioRestException(
            status=401,
            uri="/mock/uri",
            msg="Authentication failed",
            code=20003
        )
        mock_client.calls.create.side_effect = mock_error
        mock_client_class.return_value = mock_client

        result = tool.run()
        assert result["success"] is False
        error = result.get("error", {})
        assert error.get("code") == "AUTH_ERROR"

    # ========== EDGE CASE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_message(self):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="你好，这是一个测试电话。"
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["message_delivered"] == "你好，这是一个测试电话。"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_special_characters_in_message(self):
        message = "Hello! <>&'\" @#$%"
        tool = PhoneCall(phone_number="+15551234567", message=message)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_international_phone_numbers(self):
        test_numbers = [
            "+442012345678",  # UK
            "+34612345678",   # Spain
            "+81312345678",   # Japan
            "+61212345678",   # Australia
        ]
        for number in test_numbers:
            tool = PhoneCall(phone_number=number, message="Test")
            result = tool.run()
            assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_phone_number_masking(self):
        tool = PhoneCall(phone_number="+15551234567", message="Test")
        result = tool.run()
        masked = result["metadata"]["phone_number"]
        assert "***" in masked
        assert masked.startswith("+15")
        assert masked.endswith("234567")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_twiml_generation_simple(self, tool: PhoneCall):
        twiml = tool._generate_twiml()
        assert '<?xml version="1.0" encoding="UTF-8"?>' in twiml
        assert '<Response>' in twiml
        assert '<Say' in twiml
        assert tool.message in twiml or '&' in twiml  # May be escaped

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_twiml_generation_with_response(self):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Test",
            wait_for_response=True
        )
        twiml = tool._generate_twiml()
        assert '<Gather' in twiml
        assert 'input="speech"' in twiml

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_twiml_xml_escaping(self):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Test <>&'\" message"
        )
        twiml = tool._generate_twiml()
        assert '&lt;' in twiml  # < escaped
        assert '&gt;' in twiml  # > escaped
        assert '&amp;' in twiml  # & escaped

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize("phone,valid", [
        ("+15551234567", True),
        ("+442012345678", True),
        ("+34612345678", True),
        ("15551234567", False),  # No +
        ("+1555", False),  # Too short - Pydantic error
        ("+155512345678901234", False),  # Too long
        ("+1555abc1234", False),  # Contains letters
    ])
    def test_phone_number_validation(self, phone, valid):
        if phone == "+1555":
            # Too short - caught by Pydantic validation
            with pytest.raises(PydanticValidationError):
                tool = PhoneCall(phone_number=phone, message="Test")
        elif valid:
            tool = PhoneCall(phone_number=phone, message="Test")
            with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
                result = tool.run()
                assert result["success"] is True
        else:
            tool = PhoneCall(phone_number=phone, message="Test")
            result = tool.run()
            assert result["success"] is False

    @pytest.mark.parametrize("voice,valid", [
        ("male", True),
        ("female", True),
        ("neutral", True),
        ("Male", True),  # Case insensitive
        ("FEMALE", True),
        (None, True),  # Optional
        ("robot", False),
        ("british", False),
    ])
    def test_voice_validation(self, voice, valid):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Test",
            voice=voice
        )
        if valid:
            with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
                result = tool.run()
                assert result["success"] is True
        else:
            result = tool.run()
            assert result["success"] is False

    @pytest.mark.parametrize("language,valid", [
        ("en-US", True),
        ("es-ES", True),
        ("fr-FR", True),
        ("de-DE", True),
        ("en", False),  # Missing country
        ("english", False),
        ("en-us", False),  # Wrong case
        ("EN-US", False),
    ])
    def test_language_validation(self, language, valid):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Test",
            language=language
        )
        if valid:
            with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
                result = tool.run()
                assert result["success"] is True
        else:
            result = tool.run()
            assert result["success"] is False


class TestPhoneCallIntegration:
    """Integration tests with shared components."""

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_basic_run_integration(self):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Integration test message"
        )
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_integration(self):
        tool = PhoneCall(
            phone_number="+15551234567",
            message="Test",
            voice="female",
            language="es-ES",
            wait_for_response=True
        )
        result = tool.run()
        metadata = result["metadata"]

        assert metadata["tool_name"] == "phone_call"
        assert metadata["language"] == "es-ES"
        assert metadata["wait_for_response"] is True
        assert metadata["mock_mode"] is True
        assert "***" in metadata["phone_number"]  # Phone masked

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_error_handling_integration(self):
        # "invalid" is too short (< 10 chars), caught by Pydantic
        # Use a longer invalid number that passes Pydantic but fails runtime validation
        tool = PhoneCall(
            phone_number="invalid12345",  # 13 chars, passes Pydantic min_length
            message="Test"
        )
        result = tool.run()
        assert result["success"] is False
        assert "error" in result
        error = result["error"]
        assert "code" in error
        assert "message" in error
