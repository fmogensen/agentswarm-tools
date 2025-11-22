"""
Delete Google Calendar events
"""

from typing import Any, Dict
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError, ResourceNotFoundError

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarDeleteEvent(BaseTool):
    """
    Delete Google Calendar events.

    Args:
        event_id: The ID of the event to delete
        send_updates: Whether to send cancellation notifications to attendees
                     Options: 'all', 'externalOnly', 'none' (default: 'all')

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Deletion confirmation
        - metadata: Additional information

    Example:
        >>> tool = GoogleCalendarDeleteEvent(
        ...     event_id="abc123",
        ...     send_updates="all"
        ... )
        >>> result = tool.run()
        >>> print(result["result"]["status"])  # "deleted"
    """

    # Tool metadata
    tool_name: str = "google_calendar_delete_event"
    tool_category: str = "communication"

    # Parameters
    event_id: str = Field(
        ...,
        description="The ID of the event to delete",
        min_length=1
    )
    send_updates: str = Field(
        "all",
        description="Send notifications: 'all', 'externalOnly', or 'none'"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute calendar event deletion."""
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
                    "send_updates": self.send_updates
                }
            }
        except HttpError as e:
            if e.resp.status == 404:
                raise ResourceNotFoundError(
                    f"Event not found: {self.event_id}",
                    tool_name=self.tool_name,
                    resource_type="calendar_event"
                )
            elif e.resp.status == 410:
                # Event already deleted
                return {
                    "success": True,
                    "result": {
                        "status": "already_deleted",
                        "event_id": self.event_id,
                        "message": "Event was already deleted"
                    },
                    "metadata": {
                        "tool_name": self.tool_name,
                        "event_id": self.event_id
                    }
                }
            raise APIError(
                f"Google Calendar API error: {e}",
                tool_name=self.tool_name,
                api_name="Google Calendar API"
            )
        except Exception as e:
            raise APIError(
                f"Failed to delete event: {e}",
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

        valid_updates = ['all', 'externalOnly', 'none']
        if self.send_updates not in valid_updates:
            raise ValidationError(
                f"send_updates must be one of: {', '.join(valid_updates)}",
                tool_name=self.tool_name,
                field="send_updates"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        from datetime import datetime

        return {
            "success": True,
            "result": {
                "status": "deleted",
                "event_id": self.event_id,
                "deleted_at": datetime.utcnow().isoformat() + "Z",
                "notifications_sent": self.send_updates != "none"
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "event_id": self.event_id,
                "send_updates": self.send_updates
            }
        }

    def _process(self) -> Dict[str, Any]:
        """Delete calendar event via Google Calendar API."""
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

        # Delete the event
        service.events().delete(
            calendarId='primary',
            eventId=self.event_id,
            sendUpdates=self.send_updates
        ).execute()

        from datetime import datetime

        return {
            "status": "deleted",
            "event_id": self.event_id,
            "deleted_at": datetime.utcnow().isoformat() + "Z",
            "notifications_sent": self.send_updates != "none"
        }


if __name__ == "__main__":
    print("Testing GoogleCalendarDeleteEvent...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic deletion
    tool = GoogleCalendarDeleteEvent(
        event_id="test-event-123"
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('result', {}).get('status')}")
    assert result.get('success') == True
    assert result.get('result', {}).get('status') == 'deleted'
    assert result.get('result', {}).get('event_id') == 'test-event-123'

    # Test deletion without notifications
    tool2 = GoogleCalendarDeleteEvent(
        event_id="test-event-456",
        send_updates="none"
    )
    result2 = tool2.run()

    print(f"No Notifications Success: {result2.get('success')}")
    assert result2.get('success') == True
    assert result2.get('result', {}).get('notifications_sent') == False

    # Test deletion with external only notifications
    tool3 = GoogleCalendarDeleteEvent(
        event_id="test-event-789",
        send_updates="externalOnly"
    )
    result3 = tool3.run()

    print(f"External Only Success: {result3.get('success')}")
    assert result3.get('success') == True
    assert result3.get('metadata', {}).get('send_updates') == 'externalOnly'

    print("GoogleCalendarDeleteEvent tests passed!")
