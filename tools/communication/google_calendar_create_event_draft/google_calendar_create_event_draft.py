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
