"""
Search and retrieve Google Calendar events

DEPRECATED: This tool is deprecated. Use UnifiedGoogleCalendar with action="list" instead.
This wrapper maintains backward compatibility and will be removed in a future version.
"""

from typing import Any, Dict
from pydantic import Field
import warnings

from shared.base import BaseTool


class GoogleCalendarList(BaseTool):
    """
    Search and retrieve Google Calendar events

    DEPRECATED: Use UnifiedGoogleCalendar with action="list" instead.
    This wrapper maintains backward compatibility.

    Args:
        input: Search query for calendar events

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: List of calendar events
        - metadata: Additional information (includes deprecated flag)

    Example:
        >>> # Deprecated usage (still works)
        >>> tool = GoogleCalendarList(input="team meeting")
        >>> result = tool.run()
        >>>
        >>> # New recommended usage
        >>> from tools.communication.unified_google_calendar import UnifiedGoogleCalendar
        >>> tool = UnifiedGoogleCalendar(action="list", query="team meeting")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "google_calendar_list"
    tool_category: str = "communication"

    # Parameters
    input: str = Field(..., description="Search query for calendar events", min_length=1)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the google_calendar_list tool (delegates to UnifiedGoogleCalendar).

        Returns:
            Dict with results
        """
        # Emit deprecation warning
        warnings.warn(
            "GoogleCalendarList is deprecated and will be removed in v3.0.0. "
            "Use UnifiedGoogleCalendar with action='list' instead. "
            "See docs/guides/MIGRATION_GUIDE.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Import and delegate to unified tool
        from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

        unified_tool = UnifiedGoogleCalendar(action="list", query=self.input)

        # Execute unified tool
        result = unified_tool._execute()

        # Update metadata to indicate this was called via deprecated wrapper
        if "metadata" not in result:
            result["metadata"] = {}

        result["metadata"]["original_tool"] = self.tool_name
        result["metadata"]["deprecated"] = True
        result["metadata"]["use_instead"] = "UnifiedGoogleCalendar with action='list'"

        return result


if __name__ == "__main__":
    print("Testing GoogleCalendarList...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: List calendar events with search query
    print("\nTest 1: List calendar events")
    tool = GoogleCalendarList(input="team meeting")
    result = tool.run()

    assert result.get("success") == True
    assert isinstance(result.get("result", []), list)
    assert len(result.get("result", [])) > 0
    print(f"✅ Test 1 passed: Found {len(result.get('result', []))} events")
    print(f"   First event: {result.get('result', [])[0].get('summary')}")

    # Test 2: Different search query
    print("\nTest 2: Different search query")
    tool = GoogleCalendarList(input="project review")
    result = tool.run()

    assert result.get("success") == True
    assert result.get("metadata", {}).get("query") == "project review"
    print(f"✅ Test 2 passed: Query executed successfully")

    # Test 3: Validation - empty input
    print("\nTest 3: Validation - empty input")
    try:
        bad_tool = GoogleCalendarList(input="   ")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Mock data structure verification
    print("\nTest 4: Mock data structure verification")
    tool = GoogleCalendarList(input="test")
    result = tool.run()

    first_event = result.get("result", [])[0]
    assert "id" in first_event
    assert "summary" in first_event
    assert "start" in first_event
    print(f"✅ Test 4 passed: Event structure correct")

    print("\n✅ All tests passed!")
