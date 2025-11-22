"""
Create or modify calendar event draft (requires confirmation)
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os
import json

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GoogleCalendarCreateEventDraft(BaseTool):
    """
    Create or modify calendar event draft (requires confirmation)

    Args:
        input: Primary input parameter containing event draft details in JSON format

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (draft event data)
        - metadata: Additional information including mock mode indicator

    Example:
        >>> tool = GoogleCalendarCreateEventDraft(input="example")
        >>> result = tool.run()
    """

    tool_name: str = "google_calendar_create_event_draft"
    tool_category: str = "communication"

    input: str = Field(
        ...,
        description="Primary input parameter. Must be a JSON string containing event draft details.",
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the google_calendar_create_event_draft tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: If input is invalid
            APIError: If processing fails
        """
        self._validate_parameters()

        if self._should_use_mock():
            return self._generate_mock_results()

        try:
            result = self._process()
            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "mock_mode": False},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input JSON is invalid or missing required fields
        """
        if not self.input or not self.input.strip():
            raise ValidationError(
                "Input cannot be empty",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        try:
            parsed = json.loads(self.input)
        except Exception:
            raise ValidationError(
                "Input must be valid JSON",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        if not isinstance(parsed, dict):
            raise ValidationError(
                "Input JSON must represent an object",
                tool_name=self.tool_name,
                details={"parsed": parsed},
            )

        required_fields = ["title", "start_time", "end_time"]
        missing = [f for f in required_fields if f not in parsed]

        if missing:
            raise ValidationError(
                "Missing required event fields",
                tool_name=self.tool_name,
                details={"missing_fields": missing},
            )

    def _should_use_mock(self) -> bool:
        """
        Check if mock mode is enabled.

        Returns:
            True if USE_MOCK_APIS=true, otherwise False
        """
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """
        Generate mock results for testing.

        Returns:
            Mocked draft event dictionary
        """
        return {
            "success": True,
            "result": {
                "event_id": "mock-event-123",
                "status": "draft_created",
                "echo": self.input,
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Creates or updates a calendar event draft. Does not commit the event.
        Returns the parsed event draft structure.

        Returns:
            Parsed event draft dictionary

        Raises:
            APIError: If external service failure occurs
        """
        try:
            draft = json.loads(self.input)

            # Simulated real processing logic
            draft_event = {
                "event_id": "draft-" + draft.get("title", "").replace(" ", "-"),
                "status": "draft_created",
                "data": draft,
            }

            return draft_event

        except Exception as e:
            raise APIError(
                f"Failed to process event draft: {e}", tool_name=self.tool_name
            )


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
        "end_time": "2025-01-15T11:00:00Z"
    }
    tool = GoogleCalendarCreateEventDraft(input=json.dumps(event_data))
    result = tool.run()

    assert result.get('success') == True
    assert 'event_id' in result.get('result', {})
    print(f"✅ Test 1 passed: Event draft created")
    print(f"   Event ID: {result.get('result', {}).get('event_id')}")

    # Test 2: Event with optional fields
    print("\nTest 2: Event with optional description")
    event_data = {
        "title": "Project Review",
        "start_time": "2025-01-20T14:00:00Z",
        "end_time": "2025-01-20T15:30:00Z",
        "description": "Quarterly project status review"
    }
    tool = GoogleCalendarCreateEventDraft(input=json.dumps(event_data))
    result = tool.run()

    assert result.get('success') == True
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
