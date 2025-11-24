"""
Delete Google Calendar events

DEPRECATED: This tool is deprecated. Use UnifiedGoogleCalendar with action="delete" instead.
This wrapper maintains backward compatibility and will be removed in a future version.
"""

import warnings
from typing import Any, Dict

from pydantic import Field

from shared.base import BaseTool


class GoogleCalendarDeleteEvent(BaseTool):
    """
    Delete Google Calendar events.

    DEPRECATED: Use UnifiedGoogleCalendar with action="delete" instead.
    This wrapper maintains backward compatibility.

    Args:
        event_id: The ID of the event to delete
        send_updates: Whether to send cancellation notifications to attendees
                     Options: 'all', 'externalOnly', 'none' (default: 'all')

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Deletion confirmation
        - metadata: Additional information (includes deprecated flag)

    Example:
        >>> # Deprecated usage (still works)
        >>> tool = GoogleCalendarDeleteEvent(
        ...     event_id="abc123",
        ...     send_updates="all"
        ... )
        >>> result = tool.run()
        >>>
        >>> # New recommended usage
        >>> from tools.communication.unified_google_calendar import UnifiedGoogleCalendar
        >>> tool = UnifiedGoogleCalendar(
        ...     action="delete",
        ...     event_id="abc123",
        ...     send_updates="all"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "google_calendar_delete_event"
    tool_category: str = "communication"

    # Parameters
    event_id: str = Field(..., description="The ID of the event to delete", min_length=1)
    send_updates: str = Field(
        "all", description="Send notifications: 'all', 'externalOnly', or 'none'"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute calendar event deletion (delegates to UnifiedGoogleCalendar)."""
        # Emit deprecation warning

        self._logger.info(
            f"Executing {self.tool_name} with event_id={self.event_id}, send_updates={self.send_updates}"
        )
        warnings.warn(
            "GoogleCalendarDeleteEvent is deprecated and will be removed in v3.0.0. "
            "Use UnifiedGoogleCalendar with action='delete' instead. "
            "See docs/guides/MIGRATION_GUIDE.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Import and delegate to unified tool
        from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

        unified_tool = UnifiedGoogleCalendar(
            action="delete", event_id=self.event_id, send_updates=self.send_updates
        )

        # Execute unified tool
        result = unified_tool._execute()

        # Update metadata to indicate this was called via deprecated wrapper
        if "metadata" not in result:
            result["metadata"] = {}

        result["metadata"]["original_tool"] = self.tool_name
        result["metadata"]["deprecated"] = True
        result["metadata"]["use_instead"] = "UnifiedGoogleCalendar with action='delete'"

        return result


if __name__ == "__main__":
    print("Testing GoogleCalendarDeleteEvent...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic deletion
    tool = GoogleCalendarDeleteEvent(event_id="test-event-123")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('result', {}).get('status')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("status") == "deleted"
    assert result.get("result", {}).get("event_id") == "test-event-123"

    # Test deletion without notifications
    tool2 = GoogleCalendarDeleteEvent(event_id="test-event-456", send_updates="none")
    result2 = tool2.run()

    print(f"No Notifications Success: {result2.get('success')}")
    assert result2.get("success") == True
    assert result2.get("result", {}).get("notifications_sent") == False

    # Test deletion with external only notifications
    tool3 = GoogleCalendarDeleteEvent(event_id="test-event-789", send_updates="externalOnly")
    result3 = tool3.run()

    print(f"External Only Success: {result3.get('success')}")
    assert result3.get("success") == True
    assert result3.get("metadata", {}).get("send_updates") == "externalOnly"

    print("GoogleCalendarDeleteEvent tests passed!")
