"""
Update existing Google Calendar events

DEPRECATED: This tool is deprecated. Use UnifiedGoogleCalendar with action="update" instead.
This wrapper maintains backward compatibility and will be removed in a future version.
"""

import warnings
from typing import Any, Dict, Optional

from pydantic import Field

from shared.base import BaseTool


class GoogleCalendarUpdateEvent(BaseTool):
    """
    Update existing Google Calendar events.

    DEPRECATED: Use UnifiedGoogleCalendar with action="update" instead.
    This wrapper maintains backward compatibility.

    Args:
        event_id: The ID of the event to update
        summary: Optional new event title/summary
        description: Optional new event description
        start_time: Optional new start time (ISO format: 2025-01-15T10:00:00)
        end_time: Optional new end time (ISO format: 2025-01-15T11:00:00)
        location: Optional new location
        attendees: Optional new attendees (comma-separated emails)
        timezone: Timezone for the event (default: America/New_York)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Updated event details
        - metadata: Additional information (includes deprecated flag)

    Example:
        >>> # Deprecated usage (still works)
        >>> tool = GoogleCalendarUpdateEvent(
        ...     event_id="abc123",
        ...     summary="Updated Meeting Title",
        ...     start_time="2025-01-15T14:00:00"
        ... )
        >>> result = tool.run()
        >>>
        >>> # New recommended usage
        >>> from tools.communication.unified_google_calendar import UnifiedGoogleCalendar
        >>> tool = UnifiedGoogleCalendar(
        ...     action="update",
        ...     event_id="abc123",
        ...     summary="Updated Meeting Title",
        ...     start_time="2025-01-15T14:00:00"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "google_calendar_update_event"
    tool_category: str = "communication"

    # Parameters
    event_id: str = Field(..., description="The ID of the event to update", min_length=1)
    summary: Optional[str] = Field(None, description="New event title/summary")
    description: Optional[str] = Field(None, description="New event description")
    start_time: Optional[str] = Field(
        None, description="New start time (ISO format: 2025-01-15T10:00:00)"
    )
    end_time: Optional[str] = Field(
        None, description="New end time (ISO format: 2025-01-15T11:00:00)"
    )
    location: Optional[str] = Field(None, description="New location")
    attendees: Optional[str] = Field(None, description="New attendees (comma-separated emails)")
    timezone: str = Field("America/New_York", description="Timezone for the event")

    def _execute(self) -> Dict[str, Any]:
        """Execute calendar event update (delegates to UnifiedGoogleCalendar)."""
        # Emit deprecation warning

        self._logger.info(f"Executing {self.tool_name} with event_id={self.event_id}, summary={self.summary}, description={self.description}, ...")
        warnings.warn(
            "GoogleCalendarUpdateEvent is deprecated and will be removed in v3.0.0. "
            "Use UnifiedGoogleCalendar with action='update' instead. "
            "See docs/guides/MIGRATION_GUIDE.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Import and delegate to unified tool
        from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

        unified_tool = UnifiedGoogleCalendar(
            action="update",
            event_id=self.event_id,
            summary=self.summary,
            description=self.description,
            start_time=self.start_time,
            end_time=self.end_time,
            location=self.location,
            attendees=self.attendees,
            timezone=self.timezone,
        )

        # Execute unified tool
        result = unified_tool._execute()

        # Update metadata to indicate this was called via deprecated wrapper
        if "metadata" not in result:
            result["metadata"] = {}

        result["metadata"]["original_tool"] = self.tool_name
        result["metadata"]["deprecated"] = True
        result["metadata"]["use_instead"] = "UnifiedGoogleCalendar with action='update'"

        return result


if __name__ == "__main__":
    print("Testing GoogleCalendarUpdateEvent...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test updating summary and time
    tool = GoogleCalendarUpdateEvent(
        event_id="test-event-123",
        summary="Updated Team Meeting",
        start_time="2025-01-20T14:00:00",
        end_time="2025-01-20T15:00:00",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Event ID: {result.get('result', {}).get('id')}")
    print(f"Updated fields: {result.get('metadata', {}).get('updated_fields')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("summary") == "Updated Team Meeting"

    # Test updating location and attendees
    tool2 = GoogleCalendarUpdateEvent(
        event_id="test-event-456",
        location="Conference Room B",
        attendees="user1@example.com,user2@example.com",
    )
    result2 = tool2.run()

    print(f"Location Update Success: {result2.get('success')}")
    assert result2.get("success") == True
    assert len(result2.get("result", {}).get("attendees", [])) == 2

    # Test updating description only
    tool3 = GoogleCalendarUpdateEvent(
        event_id="test-event-789", description="Updated meeting agenda: Q1 planning"
    )
    result3 = tool3.run()

    print(f"Description Update Success: {result3.get('success')}")
    assert result3.get("success") == True

    print("GoogleCalendarUpdateEvent tests passed!")
