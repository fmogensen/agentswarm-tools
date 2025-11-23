"""
Tests for HubSpot Sync Calendar Tool

Comprehensive test suite covering meeting creation, updates, deletion,
calendar synchronization, and bidirectional sync operations.
"""

import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from shared.errors import APIError, ValidationError
from tools.integrations.hubspot.hubspot_sync_calendar import HubSpotSyncCalendar


class TestHubSpotSyncCalendar:
    """Test suite for HubSpotSyncCalendar tool."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"
        yield
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_create_meeting(self):
        """Test creating a meeting."""
        tool = HubSpotSyncCalendar(
            operation="create_meeting",
            title="Sales Demo - Acme Corp",
            start_time="2024-03-15T14:00:00Z",
            end_time="2024-03-15T15:00:00Z",
            description="Product demo",
            location="https://zoom.us/j/123456789",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["operation"] == "create_meeting"
        assert result["sync_status"] == "synced"
        assert "meeting_id" in result
        assert "event_id" in result
        assert result["title"] == "Sales Demo - Acme Corp"

    def test_create_meeting_with_attendees(self):
        """Test creating meeting with attendees."""
        tool = HubSpotSyncCalendar(
            operation="create_meeting",
            title="Team Meeting",
            start_time="2024-03-20T10:00:00Z",
            end_time="2024-03-20T11:00:00Z",
            attendee_emails=["john@example.com", "jane@example.com"],
            contact_ids=["123", "456"],
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["attendees"]) == 2
        assert len(result["contact_ids"]) == 2

    def test_create_meeting_with_type(self):
        """Test creating meeting with specific type."""
        for meeting_type in ["sales_call", "demo", "consultation", "followup"]:
            tool = HubSpotSyncCalendar(
                operation="create_meeting",
                title=f"{meeting_type.title()} Meeting",
                start_time="2024-03-15T14:00:00Z",
                end_time="2024-03-15T15:00:00Z",
                meeting_type=meeting_type,
            )
            result = tool.run()
            assert result["success"] == True

    def test_update_meeting(self):
        """Test updating a meeting."""
        tool = HubSpotSyncCalendar(
            operation="update_meeting",
            meeting_id="meeting_12345",
            title="Updated Meeting Title",
            description="Updated description",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["operation"] == "update_meeting"
        assert result["meeting_id"] == "meeting_12345"
        assert "updated_fields" in result

    def test_update_meeting_outcome(self):
        """Test updating meeting outcome."""
        for outcome in ["scheduled", "completed", "cancelled", "no_show"]:
            tool = HubSpotSyncCalendar(
                operation="update_meeting",
                meeting_id="meeting_123",
                outcome=outcome,
            )
            result = tool.run()
            assert result["success"] == True
            assert result["outcome"] == outcome

    def test_delete_meeting(self):
        """Test deleting a meeting."""
        tool = HubSpotSyncCalendar(
            operation="delete_meeting",
            meeting_id="meeting_789",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["operation"] == "delete_meeting"
        assert result["sync_status"] == "deleted"

    def test_hubspot_to_google_sync(self):
        """Test syncing HubSpot meetings to Google Calendar."""
        tool = HubSpotSyncCalendar(
            operation="hubspot_to_google",
            date_range_days=7,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["operation"] == "hubspot_to_google"
        assert result["sync_status"] == "completed"
        assert "meetings_synced" in result
        assert "events_synced" in result

    def test_google_to_hubspot_sync(self):
        """Test syncing Google Calendar events to HubSpot."""
        tool = HubSpotSyncCalendar(
            operation="google_to_hubspot",
            date_range_days=14,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["operation"] == "google_to_hubspot"
        assert result["sync_status"] == "completed"

    def test_bidirectional_sync(self):
        """Test bidirectional calendar synchronization."""
        tool = HubSpotSyncCalendar(
            operation="bidirectional",
            date_range_days=30,
            sync_bidirectional=True,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["operation"] == "bidirectional"
        assert result["metadata"]["bidirectional"] == True

    def test_sync_with_interval(self):
        """Test sync with scheduled interval."""
        tool = HubSpotSyncCalendar(
            operation="hubspot_to_google",
            date_range_days=30,
            sync_interval=24,
        )
        result = tool.run()

        assert result["success"] == True
        assert "next_sync" in result
        assert result["next_sync"] is not None

    def test_sync_with_owner_filter(self):
        """Test sync filtered by owner."""
        tool = HubSpotSyncCalendar(
            operation="hubspot_to_google",
            date_range_days=7,
            owner_id="owner_123",
        )
        result = tool.run()

        assert result["success"] == True

    def test_sync_including_past_events(self):
        """Test sync including past events."""
        tool = HubSpotSyncCalendar(
            operation="bidirectional",
            date_range_days=30,
            include_past_events=True,
        )
        result = tool.run()

        assert result["success"] == True

    def test_meeting_with_notifications(self):
        """Test creating meeting with notifications."""
        tool = HubSpotSyncCalendar(
            operation="create_meeting",
            title="Important Meeting",
            start_time="2024-03-15T14:00:00Z",
            end_time="2024-03-15T15:00:00Z",
            send_notifications=True,
            reminder_minutes=15,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["notifications_sent"] == True

    def test_meeting_with_custom_calendar(self):
        """Test creating meeting in custom calendar."""
        tool = HubSpotSyncCalendar(
            operation="create_meeting",
            title="Custom Calendar Meeting",
            start_time="2024-03-15T14:00:00Z",
            end_time="2024-03-15T15:00:00Z",
            calendar_id="custom_calendar_123",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["calendar_id"] == "custom_calendar_123"

    def test_invalid_operation(self):
        """Test validation of operation parameter."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSyncCalendar(
                operation="invalid_operation",
            )
            tool.run()
        assert "Invalid operation" in str(exc_info.value)

    def test_create_meeting_missing_title(self):
        """Test that create_meeting requires title."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSyncCalendar(
                operation="create_meeting",
                start_time="2024-03-15T14:00:00Z",
                end_time="2024-03-15T15:00:00Z",
            )
            tool.run()
        assert "requires title" in str(exc_info.value)

    def test_create_meeting_missing_times(self):
        """Test that create_meeting requires start and end times."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSyncCalendar(
                operation="create_meeting",
                title="Test Meeting",
            )
            tool.run()
        assert "requires title, start_time, and end_time" in str(exc_info.value)

    def test_invalid_time_format(self):
        """Test validation of time format."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSyncCalendar(
                operation="create_meeting",
                title="Test Meeting",
                start_time="invalid-time",
                end_time="2024-03-15T15:00:00Z",
            )
            tool.run()
        assert "ISO 8601 format" in str(exc_info.value)

    def test_start_time_after_end_time(self):
        """Test validation that start_time must be before end_time."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSyncCalendar(
                operation="create_meeting",
                title="Test Meeting",
                start_time="2024-03-15T15:00:00Z",
                end_time="2024-03-15T14:00:00Z",
            )
            tool.run()
        assert "start_time must be before end_time" in str(exc_info.value)

    def test_update_meeting_requires_id(self):
        """Test that update_meeting requires meeting_id."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSyncCalendar(
                operation="update_meeting",
                title="Updated Title",
            )
            tool.run()
        assert "requires meeting_id" in str(exc_info.value)

    def test_delete_meeting_requires_id(self):
        """Test that delete_meeting requires meeting_id."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSyncCalendar(
                operation="delete_meeting",
            )
            tool.run()
        assert "requires meeting_id" in str(exc_info.value)

    def test_invalid_meeting_type(self):
        """Test validation of meeting type."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSyncCalendar(
                operation="create_meeting",
                title="Test Meeting",
                start_time="2024-03-15T14:00:00Z",
                end_time="2024-03-15T15:00:00Z",
                meeting_type="invalid_type",
            )
            tool.run()
        assert "Invalid meeting_type" in str(exc_info.value)

    def test_invalid_outcome(self):
        """Test validation of outcome parameter."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSyncCalendar(
                operation="update_meeting",
                meeting_id="meeting_123",
                outcome="invalid_outcome",
            )
            tool.run()
        assert "Invalid outcome" in str(exc_info.value)

    def test_sync_date_range(self):
        """Test sync with specific date range."""
        tool = HubSpotSyncCalendar(
            operation="hubspot_to_google",
            date_range_days=60,
        )
        result = tool.run()

        assert result["success"] == True
        assert "date_range" in result
        start = datetime.strptime(result["date_range"]["start"], "%Y-%m-%d")
        end = datetime.strptime(result["date_range"]["end"], "%Y-%m-%d")
        assert (end - start).days == 60

    def test_update_multiple_fields(self):
        """Test updating multiple meeting fields."""
        tool = HubSpotSyncCalendar(
            operation="update_meeting",
            meeting_id="meeting_456",
            title="New Title",
            description="New description",
            location="New location",
            outcome="completed",
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["updated_fields"]) >= 4

    def test_meeting_with_video_link(self):
        """Test creating meeting with video conference link."""
        tool = HubSpotSyncCalendar(
            operation="create_meeting",
            title="Video Call",
            start_time="2024-03-15T14:00:00Z",
            end_time="2024-03-15T15:00:00Z",
            location="https://meet.google.com/abc-defg-hij",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["location"] == "https://meet.google.com/abc-defg-hij"

    def test_tool_metadata(self):
        """Test tool metadata."""
        tool = HubSpotSyncCalendar(
            operation="create_meeting",
            title="Test",
            start_time="2024-03-15T14:00:00Z",
            end_time="2024-03-15T15:00:00Z",
        )

        assert tool.tool_name == "hubspot_sync_calendar"
        assert tool.tool_category == "integrations"
        assert tool.rate_limit_cost == 2

    def test_sync_interval_validation(self):
        """Test validation of sync interval."""
        # Valid intervals
        for interval in [1, 24, 48, 168]:
            tool = HubSpotSyncCalendar(
                operation="hubspot_to_google",
                date_range_days=7,
                sync_interval=interval,
            )
            result = tool.run()
            assert result["success"] == True

    def test_reminder_minutes_validation(self):
        """Test validation of reminder minutes."""
        # Valid reminder times
        for minutes in [0, 15, 30, 60, 1440]:
            tool = HubSpotSyncCalendar(
                operation="create_meeting",
                title="Test",
                start_time="2024-03-15T14:00:00Z",
                end_time="2024-03-15T15:00:00Z",
                reminder_minutes=minutes,
            )
            result = tool.run()
            assert result["success"] == True

    @patch("tools.integrations.hubspot.hubspot_sync_calendar.requests")
    def test_api_call_structure(self, mock_requests):
        """Test API call structure (mocked)."""
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ["HUBSPOT_API_KEY"] = "test_key"
        os.environ["GOOGLE_CALENDAR_CREDENTIALS"] = "test_creds"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "meeting123",
            "properties": {
                "hs_meeting_title": "Test Meeting",
            },
        }
        mock_requests.post.return_value = mock_response

        tool = HubSpotSyncCalendar(
            operation="create_meeting",
            title="Test Meeting",
            start_time="2024-03-15T14:00:00Z",
            end_time="2024-03-15T15:00:00Z",
        )
        result = tool.run()

        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        assert "https://api.hubapi.com/crm/v3/objects/meetings" in call_args[0][0]

        os.environ.pop("HUBSPOT_API_KEY")
        os.environ.pop("GOOGLE_CALENDAR_CREDENTIALS")

    def test_notifications_disabled(self):
        """Test creating meeting with notifications disabled."""
        tool = HubSpotSyncCalendar(
            operation="create_meeting",
            title="No Notifications",
            start_time="2024-03-15T14:00:00Z",
            end_time="2024-03-15T15:00:00Z",
            send_notifications=False,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["notifications_sent"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
