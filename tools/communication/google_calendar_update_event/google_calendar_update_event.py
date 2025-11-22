"""
Update existing Google Calendar events
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os
from datetime import datetime

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError, ResourceNotFoundError

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarUpdateEvent(BaseTool):
    """
    Update existing Google Calendar events.

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
        - metadata: Additional information

    Example:
        >>> tool = GoogleCalendarUpdateEvent(
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
    event_id: str = Field(
        ...,
        description="The ID of the event to update",
        min_length=1
    )
    summary: Optional[str] = Field(
        None,
        description="New event title/summary"
    )
    description: Optional[str] = Field(
        None,
        description="New event description"
    )
    start_time: Optional[str] = Field(
        None,
        description="New start time (ISO format: 2025-01-15T10:00:00)"
    )
    end_time: Optional[str] = Field(
        None,
        description="New end time (ISO format: 2025-01-15T11:00:00)"
    )
    location: Optional[str] = Field(
        None,
        description="New location"
    )
    attendees: Optional[str] = Field(
        None,
        description="New attendees (comma-separated emails)"
    )
    timezone: str = Field(
        "America/New_York",
        description="Timezone for the event"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute calendar event update."""
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
                "metadata": {
                    "tool_name": self.tool_name,
                    "event_id": self.event_id,
                    "updated_fields": self._get_updated_fields()
                }
            }
        except HttpError as e:
            if e.resp.status == 404:
                raise ResourceNotFoundError(
                    f"Event not found: {self.event_id}",
                    tool_name=self.tool_name,
                    resource_type="calendar_event"
                )
            raise APIError(
                f"Google Calendar API error: {e}",
                tool_name=self.tool_name,
                api_name="Google Calendar API"
            )
        except Exception as e:
            raise APIError(
                f"Failed to update event: {e}",
                tool_name=self.tool_name
            )

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        if not self.event_id.strip():
            raise ValidationError(
                "event_id cannot be empty",
                tool_name=self.tool_name,
                field="event_id"
            )

        # Check that at least one field is being updated
        if not any([
            self.summary, self.description, self.start_time,
            self.end_time, self.location, self.attendees
        ]):
            raise ValidationError(
                "At least one field must be provided for update",
                tool_name=self.tool_name,
                field="update_fields"
            )

        # Validate datetime formats if provided
        if self.start_time:
            try:
                datetime.fromisoformat(self.start_time.replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError(
                    f"Invalid start_time format: {self.start_time}. Use ISO format (2025-01-15T10:00:00)",
                    tool_name=self.tool_name,
                    field="start_time"
                )

        if self.end_time:
            try:
                datetime.fromisoformat(self.end_time.replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError(
                    f"Invalid end_time format: {self.end_time}. Use ISO format (2025-01-15T11:00:00)",
                    tool_name=self.tool_name,
                    field="end_time"
                )

        # Validate attendees format
        if self.attendees:
            emails = [e.strip() for e in self.attendees.split(',')]
            for email in emails:
                if '@' not in email:
                    raise ValidationError(
                        f"Invalid attendee email: {email}",
                        tool_name=self.tool_name,
                        field="attendees"
                    )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        mock_event = {
            "id": self.event_id,
            "summary": self.summary or "Mock Event (Updated)",
            "description": self.description or "Mock event description",
            "start": {
                "dateTime": self.start_time or "2025-01-15T10:00:00",
                "timeZone": self.timezone
            },
            "end": {
                "dateTime": self.end_time or "2025-01-15T11:00:00",
                "timeZone": self.timezone
            },
            "location": self.location or "Mock Location",
            "status": "confirmed",
            "htmlLink": f"https://calendar.google.com/event?eid={self.event_id}",
            "updated": datetime.utcnow().isoformat() + "Z"
        }

        if self.attendees:
            mock_event["attendees"] = [
                {"email": e.strip(), "responseStatus": "needsAction"}
                for e in self.attendees.split(',')
            ]

        return {
            "success": True,
            "result": mock_event,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "event_id": self.event_id,
                "updated_fields": self._get_updated_fields()
            }
        }

    def _process(self) -> Dict[str, Any]:
        """Update calendar event via Google Calendar API."""
        # Get credentials
        credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        if not credentials_path:
            raise AuthenticationError(
                "Missing GOOGLE_SERVICE_ACCOUNT_FILE environment variable",
                tool_name=self.tool_name,
                api_name="Google Calendar API"
            )

        # Create credentials
        scopes = ["https://www.googleapis.com/auth/calendar"]
        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=scopes
        )

        # Build Calendar service
        service = build("calendar", "v3", credentials=creds)

        # Get existing event first
        try:
            existing_event = service.events().get(
                calendarId='primary',
                eventId=self.event_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise ResourceNotFoundError(
                    f"Event not found: {self.event_id}",
                    tool_name=self.tool_name,
                    resource_type="calendar_event"
                )
            raise

        # Update only provided fields
        update_body = {}

        if self.summary:
            update_body['summary'] = self.summary

        if self.description:
            update_body['description'] = self.description

        if self.start_time:
            update_body['start'] = {
                'dateTime': self.start_time,
                'timeZone': self.timezone
            }

        if self.end_time:
            update_body['end'] = {
                'dateTime': self.end_time,
                'timeZone': self.timezone
            }

        if self.location:
            update_body['location'] = self.location

        if self.attendees:
            update_body['attendees'] = [
                {'email': email.strip()}
                for email in self.attendees.split(',')
            ]

        # Perform update
        updated_event = service.events().patch(
            calendarId='primary',
            eventId=self.event_id,
            body=update_body
        ).execute()

        return {
            "id": updated_event.get("id"),
            "summary": updated_event.get("summary"),
            "description": updated_event.get("description"),
            "start": updated_event.get("start"),
            "end": updated_event.get("end"),
            "location": updated_event.get("location"),
            "attendees": updated_event.get("attendees", []),
            "status": updated_event.get("status"),
            "htmlLink": updated_event.get("htmlLink"),
            "updated": updated_event.get("updated")
        }

    def _get_updated_fields(self) -> list:
        """Get list of fields being updated."""
        fields = []
        if self.summary:
            fields.append("summary")
        if self.description:
            fields.append("description")
        if self.start_time:
            fields.append("start_time")
        if self.end_time:
            fields.append("end_time")
        if self.location:
            fields.append("location")
        if self.attendees:
            fields.append("attendees")
        return fields


if __name__ == "__main__":
    print("Testing GoogleCalendarUpdateEvent...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test updating summary and time
    tool = GoogleCalendarUpdateEvent(
        event_id="test-event-123",
        summary="Updated Team Meeting",
        start_time="2025-01-20T14:00:00",
        end_time="2025-01-20T15:00:00"
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Event ID: {result.get('result', {}).get('id')}")
    print(f"Updated fields: {result.get('metadata', {}).get('updated_fields')}")
    assert result.get('success') == True
    assert result.get('result', {}).get('summary') == "Updated Team Meeting"

    # Test updating location and attendees
    tool2 = GoogleCalendarUpdateEvent(
        event_id="test-event-456",
        location="Conference Room B",
        attendees="user1@example.com,user2@example.com"
    )
    result2 = tool2.run()

    print(f"Location Update Success: {result2.get('success')}")
    assert result2.get('success') == True
    assert len(result2.get('result', {}).get('attendees', [])) == 2

    # Test updating description only
    tool3 = GoogleCalendarUpdateEvent(
        event_id="test-event-789",
        description="Updated meeting agenda: Q1 planning"
    )
    result3 = tool3.run()

    print(f"Description Update Success: {result3.get('success')}")
    assert result3.get('success') == True

    print("GoogleCalendarUpdateEvent tests passed!")
