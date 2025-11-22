"""Tests for GoogleCalendarDeleteEvent tool."""

import pytest
import os
from google_calendar_delete_event import GoogleCalendarDeleteEvent
from shared.errors import ValidationError


class TestGoogleCalendarDeleteEvent:
    """Test cases for GoogleCalendarDeleteEvent tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_delete_event_default(self):
        """Test deleting event with default settings."""
        tool = GoogleCalendarDeleteEvent(event_id="test-123")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["status"] == "deleted"
        assert result["result"]["event_id"] == "test-123"
        assert result["result"]["notifications_sent"] == True

    def test_delete_event_no_notifications(self):
        """Test deleting event without sending notifications."""
        tool = GoogleCalendarDeleteEvent(event_id="test-123", send_updates="none")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["notifications_sent"] == False

    def test_delete_event_external_only(self):
        """Test deleting event with external notifications only."""
        tool = GoogleCalendarDeleteEvent(event_id="test-123", send_updates="externalOnly")
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["send_updates"] == "externalOnly"

    def test_validation_empty_event_id(self):
        """Test validation for empty event ID."""
        with pytest.raises(ValidationError):
            tool = GoogleCalendarDeleteEvent(event_id="")
            tool.run()

    def test_validation_invalid_send_updates(self):
        """Test validation for invalid send_updates value."""
        with pytest.raises(ValidationError):
            tool = GoogleCalendarDeleteEvent(event_id="test-123", send_updates="invalid")
            tool.run()

    def test_mock_mode(self):
        """Test mock mode returns expected structure."""
        tool = GoogleCalendarDeleteEvent(event_id="test-123")
        result = tool.run()

        assert result["metadata"]["mock_mode"] == True
        assert "deleted_at" in result["result"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
