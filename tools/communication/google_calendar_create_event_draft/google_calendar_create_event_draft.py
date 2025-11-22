"""
Create or modify calendar event draft (requires confirmation)

DEPRECATED: This tool is deprecated. Use UnifiedGoogleCalendar with action="create" instead.
This wrapper maintains backward compatibility and will be removed in a future version.
"""

from typing import Any, Dict
from pydantic import Field
import json
import warnings

from shared.base import BaseTool
from shared.errors import ValidationError


class GoogleCalendarCreateEventDraft(BaseTool):
    """
    Create or modify calendar event draft (requires confirmation)

    DEPRECATED: Use UnifiedGoogleCalendar with action="create" instead.
    This wrapper maintains backward compatibility.

    Args:
        input: JSON string containing event details (title, start_time, end_time, optional: description, location, attendees)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Created event data
        - metadata: Additional information (includes deprecated flag)

    Example:
        >>> # Deprecated usage (still works)
        >>> import json
        >>> event_data = {"title": "Meeting", "start_time": "2025-01-20T10:00:00", "end_time": "2025-01-20T11:00:00"}
        >>> tool = GoogleCalendarCreateEventDraft(input=json.dumps(event_data))
        >>> result = tool.run()
        >>>
        >>> # New recommended usage
        >>> from tools.communication.unified_google_calendar import UnifiedGoogleCalendar
        >>> tool = UnifiedGoogleCalendar(
        ...     action="create",
        ...     summary="Meeting",
        ...     start_time="2025-01-20T10:00:00",
        ...     end_time="2025-01-20T11:00:00"
        ... )
        >>> result = tool.run()
    """

    tool_name: str = "google_calendar_create_event_draft"
    tool_category: str = "communication"

    input: str = Field(
        ...,
        description="JSON string containing event details",
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the google_calendar_create_event_draft tool (delegates to UnifiedGoogleCalendar).

        Returns:
            Dict with results
        """
        # Emit deprecation warning
        warnings.warn(
            "GoogleCalendarCreateEventDraft is deprecated. Use UnifiedGoogleCalendar with action='create' instead. "
            "This wrapper will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Parse JSON input
        try:
            event_data = json.loads(self.input)
        except Exception:
            raise ValidationError(
                "Input must be valid JSON", tool_name=self.tool_name, details={"input": self.input}
            )

        if not isinstance(event_data, dict):
            raise ValidationError(
                "Input JSON must represent an object",
                tool_name=self.tool_name,
                details={"parsed": event_data},
            )

        # Map old field names to new field names
        # Old format uses "title", new format uses "summary"
        summary = event_data.get("title") or event_data.get("summary")
        start_time = event_data.get("start_time")
        end_time = event_data.get("end_time")
        description = event_data.get("description")
        location = event_data.get("location")
        attendees = event_data.get("attendees")

        # Import and delegate to unified tool
        from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

        unified_tool = UnifiedGoogleCalendar(
            action="create",
            summary=summary,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            attendees=attendees,
        )

        # Execute unified tool
        result = unified_tool._execute()

        # Update metadata to indicate this was called via deprecated wrapper
        if "metadata" not in result:
            result["metadata"] = {}

        result["metadata"]["original_tool"] = self.tool_name
        result["metadata"]["deprecated"] = True
        result["metadata"]["use_instead"] = "UnifiedGoogleCalendar with action='create'"

        return result


if __name__ == "__main__":
    print("Testing GoogleCalendarCreateEventDraft...")

    import os
    import json

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Create basic event draft
    print("\nTest 1: Create basic event draft")
    event_data = {
        "title": "Team Meeting",
        "start_time": "2025-01-15T10:00:00Z",
        "end_time": "2025-01-15T11:00:00Z",
    }
    tool = GoogleCalendarCreateEventDraft(input=json.dumps(event_data))
    result = tool.run()

    assert result.get("success") == True
    assert "event_id" in result.get("result", {})
    print(f"✅ Test 1 passed: Event draft created")
    print(f"   Event ID: {result.get('result', {}).get('event_id')}")

    # Test 2: Event with optional fields
    print("\nTest 2: Event with optional description")
    event_data = {
        "title": "Project Review",
        "start_time": "2025-01-20T14:00:00Z",
        "end_time": "2025-01-20T15:30:00Z",
        "description": "Quarterly project status review",
    }
    tool = GoogleCalendarCreateEventDraft(input=json.dumps(event_data))
    result = tool.run()

    assert result.get("success") == True
    print(f"✅ Test 2 passed: Event with description created")

    # Test 3: Validation - missing required field
    print("\nTest 3: Validation - missing required field")
    try:
        bad_event = {"title": "Meeting"}  # Missing start_time and end_time
        bad_tool = GoogleCalendarCreateEventDraft(input=json.dumps(bad_event))
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Validation - invalid JSON
    print("\nTest 4: Validation - invalid JSON")
    try:
        bad_tool = GoogleCalendarCreateEventDraft(input="not valid json")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 4 passed: JSON validation working - {type(e).__name__}")

    print("\n✅ All tests passed!")
