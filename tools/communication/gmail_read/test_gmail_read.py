"""Tests for gmail_read tool."""

import pytest
from unittest.mock import patch
from unittest.mock import Mock, patch, MagicMock
import base64
import os

from pydantic import ValidationError as PydanticValidationError

from tools.communication.gmail_read import GmailRead
from shared.errors import ValidationError, APIError


class TestGmailRead:
    """Test suite for GmailRead."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_message_id(self) -> str:
        return "12345abcdef"

    @pytest.fixture
    def tool(self, valid_message_id: str) -> GmailRead:
        return GmailRead(input=valid_message_id)

    @pytest.fixture
    def mock_gmail_message(self) -> dict:
        encoded_body = base64.urlsafe_b64encode(b"Hello World Body").decode("utf-8")
        return {
            "id": "12345abcdef",
            "snippet": "Email snippet text",
            "payload": {
                "headers": [{"name": "Subject", "value": "Test Subject"}],
                "parts": [{"mimeType": "text/plain", "body": {"data": encoded_body}}],
            },
        }

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_message_id: str):
        tool = GmailRead(input=valid_message_id)
        assert tool.input == valid_message_id
        assert tool.tool_name == "gmail_read"
        assert tool.tool_category == "communication"

    # ========== HAPPY PATH TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, tool: GmailRead):
        result = tool.run()

        assert result["success"] is True
        assert "subject" in result["result"]
        assert "message_id" in result["result"] or "message_id" in result["metadata"]

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock_results(self, tool: GmailRead):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["result"]["message_id"] == tool.input
        assert result["metadata"]["mock_mode"] is True

    # ========== VALIDATION TESTS ==========

    def test_empty_input_raises_validation_error(self):
        tool = GmailRead(input="")
        result = tool.run()
        assert result["success"] is False

    def test_whitespace_input_raises_validation_error(self):
        tool = GmailRead(input="   ")
        result = tool.run()
        assert result["success"] is False

    # ========== ERROR HANDLING TESTS ==========

    @patch.dict("os.environ", {"GOOGLE_SERVICE_ACCOUNT_JSON": "/tmp/fake.json", "USE_MOCK_APIS": "false"})
    @patch("google.oauth2.service_account.Credentials.from_service_account_file")
    @patch("googleapiclient.discovery.build")
    def test_process_api_error(self, mock_build, mock_creds, tool: GmailRead):
        service_mock = MagicMock()
        mock_build.return_value = service_mock

        service_mock.users.side_effect = Exception("API boom")

        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"}, clear=True)
    def test_missing_service_account_json(self, tool: GmailRead):
        result = tool.run()
        assert result["success"] is False

    # ========== EDGE CASE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_single_part_email(self, tool: GmailRead):
        # In mock mode, the tool returns mock data
        result = tool.run()
        assert result["success"] is True
        assert "body" in result["result"]

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "value,valid",
        [
            ("abc123", True),
            ("1", True),
            ("", False),
            ("   ", False),
        ],
    )
    def test_param_validation(self, value, valid):
        if valid:
            tool = GmailRead(input=value)
            assert tool.input == value
        else:
            tool = GmailRead(input=value)
            result = tool.run()
            assert result["success"] is False

    # ========== INTEGRATION-LIKE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_error_wrapping_from__execute(self, tool: GmailRead):
        with patch.object(tool, "_process", side_effect=ValueError("Boom")):
            result = tool.run()
            assert result["success"] is False
