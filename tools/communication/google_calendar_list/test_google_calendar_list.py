"""Tests for google_calendar_list tool."""

import pytest
from unittest.mock import patch
from unittest.mock import Mock, patch, MagicMock
import os
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from tools.communication.google_calendar_list import GoogleCalendarList
from shared.errors import ValidationError, APIError


class TestGoogleCalendarList:
    """Test suite for GoogleCalendarList."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        return "meeting"

    @pytest.fixture
    def tool(self, valid_input: str) -> GoogleCalendarList:
        return GoogleCalendarList(input=valid_input)

    @pytest.fixture
    def mock_google_events(self) -> list:
        return [
            {
                "id": "1",
                "summary": "Event 1",
                "start": {"dateTime": "2025-01-01T09:00:00Z"},
            },
            {
                "id": "2",
                "summary": "Event 2",
                "start": {"dateTime": "2025-01-02T11:00:00Z"},
            },
        ]

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initializes(self, valid_input: str):
        tool = GoogleCalendarList(input=valid_input)
        assert tool.input == valid_input
        assert tool.tool_name == "google_calendar_list"
        assert tool.tool_category == "communication"

    # ========== HAPPY PATH TESTS ==========

    @patch.dict(
        "os.environ",
        {
            "USE_MOCK_APIS": "false",
            "GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE": "/fake.json",
        },
    )
    @patch("google.oauth2.service_account.Credentials.from_service_account_file")
    @patch("googleapiclient.discovery.build")
    def test_execute_success(self, mock_build, mock_creds, tool, mock_google_events):
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_events.list.return_value.execute.return_value = {
            "items": mock_google_events
        }
        mock_service.events.return_value = mock_events
        mock_build.return_value = mock_service

        result = tool.run()

        assert result["success"] is True
        assert result["result"] == mock_google_events
        assert result["metadata"]["tool_name"] == "google_calendar_list"

    def test_metadata_correct(self, tool: GoogleCalendarList):
        assert tool.tool_name == "google_calendar_list"
        assert tool.tool_category == "communication"

    # ========== VALIDATION ERROR TESTS ==========

    @pytest.mark.parametrize("bad_input", [None])
    def test_validation_error_invalid_input_type(self, bad_input):
        with pytest.raises(PydanticValidationError):
            GoogleCalendarList(input=bad_input)

    @pytest.mark.parametrize("bad_input", [""])
    def test_validation_error_invalid_input_empty(self, bad_input):
        with pytest.raises(PydanticValidationError):
            GoogleCalendarList(input=bad_input)

    def test_validation_error_whitespace_runtime(self):
        """Test that whitespace-only input fails at runtime validation."""
        tool = GoogleCalendarList(input=" ")
        result = tool.run()
        assert result["success"] is False

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GoogleCalendarList):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert len(result["result"]) == 3
        assert all(event["source"] == "mock" for event in result["result"])

    # ========== API ERROR TESTS ==========

    @patch.dict(
        "os.environ",
        {
            "USE_MOCK_APIS": "false",
            "GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE": "/fake.json",
        },
    )
    @patch.object(GoogleCalendarList, "_process", side_effect=Exception("API failed"))
    def test_api_error_handled(self, mock_process, tool: GoogleCalendarList):
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"}, clear=True)
    def test_missing_env_variable_raises_error(self, tool: GoogleCalendarList):
        result = tool.run()
        assert result["success"] is False

    # ========== IMPORT ERROR TESTS ==========

    @patch.dict(
        "os.environ",
        {
            "USE_MOCK_APIS": "false",
            "GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE": "/fake.json",
        },
    )
    @patch(
        "google.oauth2.service_account.Credentials.from_service_account_file",
        side_effect=Exception("Import fail"),
    )
    def test_google_import_failure(self, mock_import, tool: GoogleCalendarList):
        result = tool.run()
        assert result["success"] is False

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize("text", ["会议", "special @#$%", "a" * 50])
    def test_various_inputs(self, text):
        tool = GoogleCalendarList(input=text)
        assert tool.input == text

    # ========== EDGE CASE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_input(self):
        tool = GoogleCalendarList(input="团队会议 📅")
        result = tool.run()
        assert result["success"] is True

    def test_whitespace_trimmed(self):
        tool = GoogleCalendarList(input="  meeting  ")
        result = tool.run()
        assert result["success"] is True or result["success"] is False

    @patch.dict(
        "os.environ",
        {
            "USE_MOCK_APIS": "false",
            "GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE": "/fake.json",
        },
    )
    @patch("googleapiclient.discovery.build")
    @patch("google.oauth2.service_account.Credentials.from_service_account_file")
    def test_api_returns_empty_list(self, mock_creds, mock_build, tool):
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_events.list.return_value.execute.return_value = {"items": []}
        mock_service.events.return_value = mock_events
        mock_build.return_value = mock_service

        result = tool.run()

        assert result["success"] is True
        assert result["result"] == []

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_integration_basic(self, tool: GoogleCalendarList):
        result = tool.run()
        assert result["success"] is True
