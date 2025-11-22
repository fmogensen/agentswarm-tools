"""Tests for GoogleCalendarUpdateEvent tool."""

import pytest
import os
from google_calendar_update_event import GoogleCalendarUpdateEvent
from shared.errors import ValidationError


class TestGoogleCalendarUpdateEvent:
    """Test cases for GoogleCalendarUpdateEvent tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_update_summary(self):
        """Test updating event summary."""
        tool = GoogleCalendarUpdateEvent(
            event_id="test-123",
            summary="New Meeting Title"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["summary"] == "New Meeting Title"
        assert "summary" in result["metadata"]["updated_fields"]

    def test_update_time(self):
        """Test updating event times."""
        tool = GoogleCalendarUpdateEvent(
            event_id="test-123",
            start_time="2025-01-15T10:00:00",
            end_time="2025-01-15T11:00:00"
        )
        result = tool.run()

        assert result["success"] == True
        assert "start_time" in result["metadata"]["updated_fields"]
        assert "end_time" in result["metadata"]["updated_fields"]

    def test_update_location(self):
        """Test updating event location."""
        tool = GoogleCalendarUpdateEvent(
            event_id="test-123",
            location="Conference Room A"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["location"] == "Conference Room A"

    def test_update_attendees(self):
        """Test updating event attendees."""
        tool = GoogleCalendarUpdateEvent(
            event_id="test-123",
            attendees="user1@example.com,user2@example.com"
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["result"]["attendees"]) == 2

    def test_update_multiple_fields(self):
        """Test updating multiple fields at once."""
        tool = GoogleCalendarUpdateEvent(
            event_id="test-123",
            summary="Updated Meeting",
            location="New Location",
            description="Updated description"
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["metadata"]["updated_fields"]) == 3

    def test_validation_empty_event_id(self):
        """Test validation for empty event ID."""
        with pytest.raises(ValidationError):
            tool = GoogleCalendarUpdateEvent(
                event_id="",
                summary="Test"
            )
            tool.run()

    def test_validation_no_updates(self):
        """Test validation when no fields to update."""
        with pytest.raises(ValidationError):
            tool = GoogleCalendarUpdateEvent(
                event_id="test-123"
            )
            tool.run()

    def test_validation_invalid_datetime(self):
        """Test validation for invalid datetime format."""
        with pytest.raises(ValidationError):
            tool = GoogleCalendarUpdateEvent(
                event_id="test-123",
                start_time="invalid-date"
            )
            tool.run()

    def test_validation_invalid_attendee_email(self):
        """Test validation for invalid attendee email."""
        with pytest.raises(ValidationError):
            tool = GoogleCalendarUpdateEvent(
                event_id="test-123",
                attendees="not-an-email,another-invalid"
            )
            tool.run()

    def test_mock_mode(self):
        """Test mock mode returns expected structure."""
        tool = GoogleCalendarUpdateEvent(
            event_id="test-123",
            summary="Test Meeting"
        )
        result = tool.run()

        assert result["metadata"]["mock_mode"] == True
        assert "htmlLink" in result["result"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
