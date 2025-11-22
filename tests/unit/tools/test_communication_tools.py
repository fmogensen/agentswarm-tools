"""
Comprehensive unit tests for Communication Tools category.

Tests all communication tools:
- gmail_search, gmail_read, read_email_attachments, email_draft, email_send
- google_calendar_list, google_calendar_create_event_draft, google_calendar_update_event, google_calendar_delete_event
- phone_call, query_call_logs, twilio_phone_call, twilio_call_logs
- slack_send_message, slack_read_messages, teams_send_message
- google_docs, google_sheets, google_slides, meeting_notes
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any
from datetime import datetime

from tools.communication.gmail_search.gmail_search import GmailSearch
from tools.communication.gmail_read.gmail_read import GmailRead
from tools.communication.read_email_attachments.read_email_attachments import ReadEmailAttachments
from tools.communication.email_draft.email_draft import EmailDraft
from tools.communication.email_send.email_send import EmailSend
from tools.communication.google_calendar_list.google_calendar_list import GoogleCalendarList
from tools.communication.google_calendar_create_event_draft.google_calendar_create_event_draft import (
    GoogleCalendarCreateEventDraft,
)
from tools.communication.google_calendar_update_event.google_calendar_update_event import (
    GoogleCalendarUpdateEvent,
)
from tools.communication.google_calendar_delete_event.google_calendar_delete_event import (
    GoogleCalendarDeleteEvent,
)
from tools.communication.phone_call.phone_call import PhoneCall
from tools.communication.query_call_logs.query_call_logs import QueryCallLogs
from tools.communication.twilio_phone_call.twilio_phone_call import TwilioPhoneCall
from tools.communication.twilio_call_logs.twilio_call_logs import TwilioCallLogs
from tools.communication.slack_send_message.slack_send_message import SlackSendMessage
from tools.communication.slack_read_messages.slack_read_messages import SlackReadMessages
from tools.communication.teams_send_message.teams_send_message import TeamsSendMessage
from tools.communication.meeting_notes.meeting_notes import MeetingNotes

from shared.errors import ValidationError, APIError, AuthenticationError


# ========== GmailSearch Tests ==========


class TestGmailSearch:
    """Comprehensive tests for GmailSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = GmailSearch(query="from:test@example.com", max_results=10)
        assert tool.query == "from:test@example.com"
        assert tool.max_results == 10
        assert tool.tool_name == "gmail_search"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = GmailSearch(query="subject:meeting", max_results=5)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = GmailSearch(query="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.communication.gmail_search.gmail_search.build")
    def test_execute_live_mode_success(self, mock_build, monkeypatch):
        """Test execution with mocked Gmail API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("GMAIL_CLIENT_ID", "test_id")
        monkeypatch.setenv("GMAIL_CLIENT_SECRET", "test_secret")

        mock_service = MagicMock()
        mock_service.users().messages().list().execute.return_value = {
            "messages": [
                {"id": "msg1", "threadId": "thread1"},
                {"id": "msg2", "threadId": "thread2"},
            ]
        }
        mock_build.return_value = mock_service

        tool = GmailSearch(query="test", max_results=2)
        result = tool.run()

        assert result["success"] is True


# ========== GmailRead Tests ==========


class TestGmailRead:
    """Comprehensive tests for GmailRead tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = GmailRead(message_id="12345")
        assert tool.message_id == "12345"
        assert tool.tool_name == "gmail_read"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = GmailRead(message_id="test123")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_message_id(self):
        """Test validation with empty message ID"""
        tool = GmailRead(message_id="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== ReadEmailAttachments Tests ==========


class TestReadEmailAttachments:
    """Comprehensive tests for ReadEmailAttachments tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ReadEmailAttachments(message_id="12345")
        assert tool.message_id == "12345"
        assert tool.tool_name == "read_email_attachments"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ReadEmailAttachments(message_id="test123")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True


# ========== EmailDraft Tests ==========


class TestEmailDraft:
    """Comprehensive tests for EmailDraft tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = EmailDraft(
            to="recipient@example.com", subject="Test Email", body="This is a test email."
        )
        assert tool.to == "recipient@example.com"
        assert tool.subject == "Test Email"
        assert tool.body == "This is a test email."
        assert tool.tool_name == "email_draft"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = EmailDraft(to="test@example.com", subject="Meeting", body="Let's meet tomorrow.")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_invalid_email(self):
        """Test validation with invalid email address"""
        tool = EmailDraft(to="invalid-email", subject="Test", body="Body")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_empty_subject(self):
        """Test validation with empty subject"""
        tool = EmailDraft(to="test@example.com", subject="", body="Body")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== EmailSend Tests ==========


class TestEmailSend:
    """Comprehensive tests for EmailSend tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = EmailSend(
            to="recipient@example.com",
            subject="Test Email",
            body="This is a test email.",
            from_email="sender@example.com",
        )
        assert tool.to == "recipient@example.com"
        assert tool.subject == "Test Email"
        assert tool.tool_name == "email_send"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = EmailSend(to="test@example.com", subject="Test", body="Test body")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GoogleCalendarList Tests ==========


class TestGoogleCalendarList:
    """Comprehensive tests for GoogleCalendarList tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = GoogleCalendarList(max_results=10, time_min="2025-01-01T00:00:00Z")
        assert tool.max_results == 10
        assert tool.tool_name == "google_calendar_list"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = GoogleCalendarList(max_results=5)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    @patch("tools.communication.google_calendar_list.google_calendar_list.build")
    def test_execute_live_mode_success(self, mock_build, monkeypatch):
        """Test execution with mocked Calendar API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("GOOGLE_CALENDAR_CLIENT_ID", "test_id")
        monkeypatch.setenv("GOOGLE_CALENDAR_CLIENT_SECRET", "test_secret")

        mock_service = MagicMock()
        mock_service.events().list().execute.return_value = {
            "items": [
                {"id": "event1", "summary": "Meeting 1"},
                {"id": "event2", "summary": "Meeting 2"},
            ]
        }
        mock_build.return_value = mock_service

        tool = GoogleCalendarList(max_results=2)
        result = tool.run()

        assert result["success"] is True


# ========== GoogleCalendarCreateEventDraft Tests ==========


class TestGoogleCalendarCreateEventDraft:
    """Comprehensive tests for GoogleCalendarCreateEventDraft tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = GoogleCalendarCreateEventDraft(
            summary="Team Meeting",
            start_time="2025-01-15T10:00:00Z",
            end_time="2025-01-15T11:00:00Z",
            description="Weekly team sync",
        )
        assert tool.summary == "Team Meeting"
        assert tool.start_time == "2025-01-15T10:00:00Z"
        assert tool.tool_name == "google_calendar_create_event_draft"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = GoogleCalendarCreateEventDraft(
            summary="Meeting", start_time="2025-01-15T10:00:00Z", end_time="2025-01-15T11:00:00Z"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_summary(self):
        """Test validation with empty summary"""
        tool = GoogleCalendarCreateEventDraft(
            summary="", start_time="2025-01-15T10:00:00Z", end_time="2025-01-15T11:00:00Z"
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== GoogleCalendarUpdateEvent Tests ==========


class TestGoogleCalendarUpdateEvent:
    """Comprehensive tests for GoogleCalendarUpdateEvent tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = GoogleCalendarUpdateEvent(event_id="12345", summary="Updated Meeting")
        assert tool.event_id == "12345"
        assert tool.summary == "Updated Meeting"
        assert tool.tool_name == "google_calendar_update_event"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = GoogleCalendarUpdateEvent(event_id="test123", summary="Updated")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GoogleCalendarDeleteEvent Tests ==========


class TestGoogleCalendarDeleteEvent:
    """Comprehensive tests for GoogleCalendarDeleteEvent tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = GoogleCalendarDeleteEvent(event_id="12345")
        assert tool.event_id == "12345"
        assert tool.tool_name == "google_calendar_delete_event"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = GoogleCalendarDeleteEvent(event_id="test123")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== PhoneCall Tests ==========


class TestPhoneCall:
    """Comprehensive tests for PhoneCall tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = PhoneCall(to_number="+1234567890", message="This is a test call")
        assert tool.to_number == "+1234567890"
        assert tool.message == "This is a test call"
        assert tool.tool_name == "phone_call"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = PhoneCall(to_number="+1234567890", message="Test")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_invalid_number(self):
        """Test validation with invalid phone number"""
        tool = PhoneCall(to_number="invalid", message="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== QueryCallLogs Tests ==========


class TestQueryCallLogs:
    """Comprehensive tests for QueryCallLogs tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = QueryCallLogs(date_from="2025-01-01", date_to="2025-01-31")
        assert tool.date_from == "2025-01-01"
        assert tool.date_to == "2025-01-31"
        assert tool.tool_name == "query_call_logs"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = QueryCallLogs(date_from="2025-01-01")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== TwilioPhoneCall Tests ==========


class TestTwilioPhoneCall:
    """Comprehensive tests for TwilioPhoneCall tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = TwilioPhoneCall(
            to_number="+1234567890", from_number="+0987654321", message="Test call"
        )
        assert tool.to_number == "+1234567890"
        assert tool.from_number == "+0987654321"
        assert tool.tool_name == "twilio_phone_call"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = TwilioPhoneCall(to_number="+1234567890", from_number="+0987654321", message="Test")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== TwilioCallLogs Tests ==========


class TestTwilioCallLogs:
    """Comprehensive tests for TwilioCallLogs tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = TwilioCallLogs(date_from="2025-01-01", max_results=50)
        assert tool.date_from == "2025-01-01"
        assert tool.max_results == 50
        assert tool.tool_name == "twilio_call_logs"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = TwilioCallLogs(max_results=10)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== SlackSendMessage Tests ==========


class TestSlackSendMessage:
    """Comprehensive tests for SlackSendMessage tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = SlackSendMessage(channel="#general", message="Hello Slack!")
        assert tool.channel == "#general"
        assert tool.message == "Hello Slack!"
        assert tool.tool_name == "slack_send_message"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = SlackSendMessage(channel="#test", message="Test message")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_message(self):
        """Test validation with empty message"""
        tool = SlackSendMessage(channel="#general", message="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== SlackReadMessages Tests ==========


class TestSlackReadMessages:
    """Comprehensive tests for SlackReadMessages tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = SlackReadMessages(channel="#general", max_results=50)
        assert tool.channel == "#general"
        assert tool.max_results == 50
        assert tool.tool_name == "slack_read_messages"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = SlackReadMessages(channel="#test", max_results=10)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== TeamsSendMessage Tests ==========


class TestTeamsSendMessage:
    """Comprehensive tests for TeamsSendMessage tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = TeamsSendMessage(channel="General", message="Hello Teams!")
        assert tool.channel == "General"
        assert tool.message == "Hello Teams!"
        assert tool.tool_name == "teams_send_message"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = TeamsSendMessage(channel="Test", message="Test message")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== MeetingNotes Tests ==========


class TestMeetingNotes:
    """Comprehensive tests for MeetingNotes tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = MeetingNotes(
            meeting_id="12345", participants=["Alice", "Bob"], summary="Discussed project timeline"
        )
        assert tool.meeting_id == "12345"
        assert len(tool.participants) == 2
        assert tool.tool_name == "meeting_notes"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = MeetingNotes(meeting_id="test123", summary="Test meeting")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
