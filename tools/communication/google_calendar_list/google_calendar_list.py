"""
Search and retrieve Google Calendar events
"""

from typing import Any, Dict, List
from pydantic import Field
import os
import datetime

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GoogleCalendarList(BaseTool):
    """
    Search and retrieve Google Calendar events

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GoogleCalendarList(input="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "google_calendar_list"
    tool_category: str = "communication"

    # Parameters
    input: str = Field(..., description="Primary input parameter", min_length=1)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the google_calendar_list tool.

        Returns:
            Dict with results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "query": self.input},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input is empty or invalid
        """
        if not self.input or not self.input.strip():
            raise ValidationError(
                "Input cannot be empty",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_events = [
            {
                "id": f"mock-{i}",
                "summary": f"Mock Event {i}",
                "start": {"dateTime": f"2025-01-0{i}T09:00:00Z"},
                "end": {"dateTime": f"2025-01-0{i}T10:00:00Z"},
                "source": "mock",
            }
            for i in range(1, 4)
        ]

        return {
            "success": True,
            "result": mock_events,
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Returns:
            List of calendar events

        Raises:
            APIError: If Google API call fails
        """
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except Exception as e:
            raise APIError(
                f"Failed to import Google API dependencies: {e}",
                tool_name=self.tool_name,
            )

        try:
            credentials_path = os.getenv("GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE")

            if not credentials_path:
                raise APIError(
                    "Missing GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE environment variable",
                    tool_name=self.tool_name,
                )

            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/calendar.readonly"],
            )

            service = build("calendar", "v3", credentials=credentials)

            now = datetime.datetime.utcnow().isoformat() + "Z"

            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    q=self.input,
                    timeMin=now,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events: List[Dict[str, Any]] = events_result.get("items", [])

            return events

        except Exception as e:
            raise APIError(
                f"Google Calendar API request failed: {e}", tool_name=self.tool_name
            )


if __name__ == "__main__":
    print("Testing GoogleCalendarList...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: List calendar events with search query
    print("\nTest 1: List calendar events")
    tool = GoogleCalendarList(input="team meeting")
    result = tool.run()

    assert result.get('success') == True
    assert isinstance(result.get('result', []), list)
    assert len(result.get('result', [])) > 0
    print(f"✅ Test 1 passed: Found {len(result.get('result', []))} events")
    print(f"   First event: {result.get('result', [])[0].get('summary')}")

    # Test 2: Different search query
    print("\nTest 2: Different search query")
    tool = GoogleCalendarList(input="project review")
    result = tool.run()

    assert result.get('success') == True
    assert result.get('metadata', {}).get('query') == "project review"
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

    first_event = result.get('result', [])[0]
    assert 'id' in first_event
    assert 'summary' in first_event
    assert 'start' in first_event
    print(f"✅ Test 4 passed: Event structure correct")

    print("\n✅ All tests passed!")
