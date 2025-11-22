"""
Comprehensive test suite for UnifiedGoogleCalendar tool.
Tests all 4 actions (list, create, update, delete) with various scenarios.
"""

import os
import pytest
from datetime import datetime

os.environ["USE_MOCK_APIS"] = "true"

from tools.communication.unified_google_calendar import UnifiedGoogleCalendar
from shared.errors import ValidationError


class TestUnifiedGoogleCalendarList:
    """Test suite for list action."""

    def test_list_basic(self):
        """Test basic event listing."""
        tool = UnifiedGoogleCalendar(action="list", query="team meeting")
        result = tool.run()

        assert result.get("success") == True
        assert isinstance(result.get("result"), list)
        assert len(result.get("result")) > 0
        assert result.get("metadata", {}).get("action") == "list"

    def test_list_different_query(self):
        """Test listing with different query."""
        tool = UnifiedGoogleCalendar(action="list", query="project review")
        result = tool.run()

        assert result.get("success") == True
        assert result.get("metadata", {}).get("action") == "list"

    def test_list_missing_query(self):
        """Test list validation - missing query."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(action="list", query="")
            tool.run()

        assert "query is required" in str(exc_info.value)

    def test_list_whitespace_query(self):
        """Test list validation - whitespace query."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(action="list", query="   ")
            tool.run()

        assert "query is required" in str(exc_info.value)

    def test_list_result_structure(self):
        """Test list result structure."""
        tool = UnifiedGoogleCalendar(action="list", query="meeting")
        result = tool.run()

        first_event = result.get("result", [])[0]
        assert "id" in first_event
        assert "summary" in first_event
        assert "start" in first_event
        assert "end" in first_event


class TestUnifiedGoogleCalendarCreate:
    """Test suite for create action."""

    def test_create_basic(self):
        """Test basic event creation."""
        tool = UnifiedGoogleCalendar(
            action="create",
            summary="Team Standup",
            start_time="2025-01-20T10:00:00",
            end_time="2025-01-20T10:30:00",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("summary") == "Team Standup"
        assert result.get("metadata", {}).get("action") == "create"

    def test_create_with_all_fields(self):
        """Test creating event with all optional fields."""
        tool = UnifiedGoogleCalendar(
            action="create",
            summary="Project Meeting",
            start_time="2025-01-25T14:00:00",
            end_time="2025-01-25T15:30:00",
            description="Quarterly project review",
            location="Conference Room A",
            attendees="alice@example.com,bob@example.com",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("summary") == "Project Meeting"
        assert result.get("result", {}).get("description") == "Quarterly project review"
        assert result.get("result", {}).get("location") == "Conference Room A"
        assert len(result.get("result", {}).get("attendees", [])) == 2

    def test_create_missing_summary(self):
        """Test create validation - missing summary."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(
                action="create", start_time="2025-01-20T10:00:00", end_time="2025-01-20T10:30:00"
            )
            tool.run()

        assert "Missing required fields" in str(exc_info.value)
        assert "summary" in str(exc_info.value)

    def test_create_missing_start_time(self):
        """Test create validation - missing start_time."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(
                action="create", summary="Meeting", end_time="2025-01-20T10:30:00"
            )
            tool.run()

        assert "Missing required fields" in str(exc_info.value)
        assert "start_time" in str(exc_info.value)

    def test_create_missing_end_time(self):
        """Test create validation - missing end_time."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(
                action="create", summary="Meeting", start_time="2025-01-20T10:00:00"
            )
            tool.run()

        assert "Missing required fields" in str(exc_info.value)
        assert "end_time" in str(exc_info.value)

    def test_create_invalid_start_time_format(self):
        """Test create validation - invalid start_time format."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(
                action="create",
                summary="Meeting",
                start_time="invalid-datetime",
                end_time="2025-01-20T10:30:00",
            )
            tool.run()

        assert "Invalid start_time format" in str(exc_info.value)

    def test_create_invalid_end_time_format(self):
        """Test create validation - invalid end_time format."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(
                action="create",
                summary="Meeting",
                start_time="2025-01-20T10:00:00",
                end_time="not-a-date",
            )
            tool.run()

        assert "Invalid end_time format" in str(exc_info.value)

    def test_create_invalid_attendee_email(self):
        """Test create validation - invalid attendee email."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(
                action="create",
                summary="Meeting",
                start_time="2025-01-20T10:00:00",
                end_time="2025-01-20T10:30:00",
                attendees="invalid-email,bob@example.com",
            )
            tool.run()

        assert "Invalid attendee email" in str(exc_info.value)


class TestUnifiedGoogleCalendarUpdate:
    """Test suite for update action."""

    def test_update_summary(self):
        """Test updating event summary."""
        tool = UnifiedGoogleCalendar(
            action="update", event_id="test-event-123", summary="Updated Meeting Title"
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("summary") == "Updated Meeting Title"
        assert result.get("metadata", {}).get("action") == "update"

    def test_update_multiple_fields(self):
        """Test updating multiple fields."""
        tool = UnifiedGoogleCalendar(
            action="update",
            event_id="test-event-456",
            summary="Updated Title",
            start_time="2025-01-20T14:00:00",
            end_time="2025-01-20T15:00:00",
            location="New Location",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("summary") == "Updated Title"
        assert result.get("result", {}).get("location") == "New Location"

    def test_update_description_only(self):
        """Test updating only description."""
        tool = UnifiedGoogleCalendar(
            action="update", event_id="test-event-789", description="Updated description only"
        )
        result = tool.run()

        assert result.get("success") == True

    def test_update_attendees(self):
        """Test updating attendees."""
        tool = UnifiedGoogleCalendar(
            action="update",
            event_id="test-event-101",
            attendees="charlie@example.com,dave@example.com,eve@example.com",
        )
        result = tool.run()

        assert result.get("success") == True
        assert len(result.get("result", {}).get("attendees", [])) == 3

    def test_update_missing_event_id(self):
        """Test update validation - missing event_id."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(action="update", summary="Updated Title")
            tool.run()

        assert "event_id is required" in str(exc_info.value)

    def test_update_empty_event_id(self):
        """Test update validation - empty event_id."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(action="update", event_id="", summary="Updated Title")
            tool.run()

        assert "event_id is required" in str(exc_info.value)

    def test_update_no_fields(self):
        """Test update validation - no fields to update."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(action="update", event_id="test-event-123")
            tool.run()

        assert "At least one field must be provided" in str(exc_info.value)

    def test_update_invalid_datetime(self):
        """Test update validation - invalid datetime."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(
                action="update", event_id="test-event-123", start_time="not-a-valid-date"
            )
            tool.run()

        assert "Invalid start_time format" in str(exc_info.value)


class TestUnifiedGoogleCalendarDelete:
    """Test suite for delete action."""

    def test_delete_basic(self):
        """Test basic event deletion."""
        tool = UnifiedGoogleCalendar(action="delete", event_id="test-event-123")
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("status") == "deleted"
        assert result.get("metadata", {}).get("action") == "delete"

    def test_delete_with_notifications_all(self):
        """Test delete with notifications to all attendees."""
        tool = UnifiedGoogleCalendar(action="delete", event_id="test-event-456", send_updates="all")
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("notifications_sent") == True

    def test_delete_with_notifications_none(self):
        """Test delete without notifications."""
        tool = UnifiedGoogleCalendar(
            action="delete", event_id="test-event-789", send_updates="none"
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("notifications_sent") == False

    def test_delete_with_notifications_external_only(self):
        """Test delete with external only notifications."""
        tool = UnifiedGoogleCalendar(
            action="delete", event_id="test-event-999", send_updates="externalOnly"
        )
        result = tool.run()

        assert result.get("success") == True

    def test_delete_missing_event_id(self):
        """Test delete validation - missing event_id."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(action="delete")
            tool.run()

        assert "event_id is required" in str(exc_info.value)

    def test_delete_invalid_send_updates(self):
        """Test delete validation - invalid send_updates."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleCalendar(
                action="delete", event_id="test-event-123", send_updates="invalid"
            )
            tool.run()

        assert "send_updates must be one of" in str(exc_info.value)


class TestUnifiedGoogleCalendarIntegration:
    """Integration tests for multiple operations."""

    def test_create_then_update(self):
        """Test creating an event then updating it."""
        # Create
        create_tool = UnifiedGoogleCalendar(
            action="create",
            summary="New Meeting",
            start_time="2025-02-01T10:00:00",
            end_time="2025-02-01T11:00:00",
        )
        create_result = create_tool.run()

        assert create_result.get("success") == True
        event_id = create_result.get("result", {}).get("id")

        # Update
        update_tool = UnifiedGoogleCalendar(
            action="update", event_id=event_id, summary="Updated Meeting Title"
        )
        update_result = update_tool.run()

        assert update_result.get("success") == True
        assert update_result.get("result", {}).get("summary") == "Updated Meeting Title"

    def test_create_then_delete(self):
        """Test creating an event then deleting it."""
        # Create
        create_tool = UnifiedGoogleCalendar(
            action="create",
            summary="Temporary Meeting",
            start_time="2025-02-05T14:00:00",
            end_time="2025-02-05T15:00:00",
        )
        create_result = create_tool.run()

        assert create_result.get("success") == True
        event_id = create_result.get("result", {}).get("id")

        # Delete
        delete_tool = UnifiedGoogleCalendar(action="delete", event_id=event_id, send_updates="none")
        delete_result = delete_tool.run()

        assert delete_result.get("success") == True
        assert delete_result.get("result", {}).get("status") == "deleted"

    def test_metadata_includes_action(self):
        """Test that metadata includes action for all operations."""
        actions = [
            ("list", {"query": "test"}),
            (
                "create",
                {
                    "summary": "Test",
                    "start_time": "2025-01-20T10:00:00",
                    "end_time": "2025-01-20T11:00:00",
                },
            ),
            ("update", {"event_id": "test-123", "summary": "Updated"}),
            ("delete", {"event_id": "test-456"}),
        ]

        for action, params in actions:
            tool = UnifiedGoogleCalendar(action=action, **params)
            result = tool.run()

            assert result.get("metadata", {}).get("action") == action


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
