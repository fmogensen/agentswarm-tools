"""Tests for google_calendar_create_event_draft tool."""

import json
from typing import Any, Dict
from unittest.mock import patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.communication.google_calendar_create_event_draft import (
    GoogleCalendarCreateEventDraft,
)


class TestGoogleCalendarCreateEventDraft:
    """Test suite for GoogleCalendarCreateEventDraft."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        return json.dumps(
            {
                "title": "Test Event",
                "start_time": "2025-01-01T10:00:00",
                "end_time": "2025-01-01T11:00:00",
                "location": "Online",
            }
        )

    @pytest.fixture
    def tool(self, valid_input: str) -> GoogleCalendarCreateEventDraft:
        return GoogleCalendarCreateEventDraft(input=valid_input)

    # ========== INITIALIZATION ==========

    def test_initialization(self, valid_input: str):
        tool = GoogleCalendarCreateEventDraft(input=valid_input)
        assert tool.input == valid_input
        assert tool.tool_name == "google_calendar_create_event_draft"
        assert tool.tool_category == "communication"

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: GoogleCalendarCreateEventDraft):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["status"] == "draft_created"

    def test_metadata_correct(self, tool: GoogleCalendarCreateEventDraft):
        assert tool.tool_name == "google_calendar_create_event_draft"
        assert tool.tool_category == "communication"

    # ========== VALIDATION TESTS ==========

    def test_empty_input_raises_validation_error(self):
        tool = GoogleCalendarCreateEventDraft(input="")
        result = tool.run()
        assert result["success"] is False

    @pytest.mark.parametrize(
        "bad_input",
        [
            "not-json",
            "123",
            json.dumps([]),
            json.dumps({"title": "Missing times"}),
            json.dumps({"start_time": "t", "end_time": "t"}),
            json.dumps({"title": "x", "start_time": "t"}),
        ],
    )
    def test_invalid_inputs_raise(self, bad_input):
        tool = GoogleCalendarCreateEventDraft(input=bad_input)
        result = tool.run()
        assert result["success"] is False

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GoogleCalendarCreateEventDraft):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: GoogleCalendarCreateEventDraft):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is False

    # ========== ERROR CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_process_error_raises_api_error(self, tool: GoogleCalendarCreateEventDraft):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_wraps_api_error(self, tool: GoogleCalendarCreateEventDraft):
        with patch.object(tool, "_process", side_effect=ValueError("boom")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    def test_unicode_input(self):
        data = {
            "title": "会议",
            "start_time": "2025-01-01T10:00:00",
            "end_time": "2025-01-01T11:00:00",
        }
        tool = GoogleCalendarCreateEventDraft(input=json.dumps(data))
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_input(self):
        data = {
            "title": "@#$%^&* Event!",
            "start_time": "2025-01-01T10:00:00",
            "end_time": "2025-01-01T11:00:00",
        }
        tool = GoogleCalendarCreateEventDraft(input=json.dumps(data))
        result = tool.run()
        assert result["success"] is True
        assert "@" in result["result"]["data"]["title"]

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "input_data,expected_valid",
        [
            ({"title": "A", "start_time": "t", "end_time": "t"}, True),
            (
                {"title": "", "start_time": "t", "end_time": "t"},
                True,
            ),  # Empty title allowed
            ({}, False),
            ([], False),
            ("string", False),
        ],
    )
    def test_param_validation(self, input_data, expected_valid):
        input_str = json.dumps(input_data) if not isinstance(input_data, str) else input_data

        if expected_valid:
            tool = GoogleCalendarCreateEventDraft(input=input_str)
            result = tool.run()
            assert result["success"] is True
        else:
            tool = GoogleCalendarCreateEventDraft(input=input_str)
            result = tool.run()
            assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    def test_integration_basic_flow(self, tool: GoogleCalendarCreateEventDraft):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["status"] == "draft_created"

    def test_integration_error_formatting(self, tool: GoogleCalendarCreateEventDraft):
        with patch.object(tool, "_execute", side_effect=ValueError("x")):
            output = tool.run()
            assert isinstance(output, dict)
            assert "success" in output
            assert output.get("success") is False or "error" in output
