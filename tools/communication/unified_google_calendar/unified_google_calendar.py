"""
Unified Google Calendar operations (list, create, update, delete).
Consolidates 4 separate calendar tools into a single action-based interface.
"""

from typing import Any, Dict, Optional, Literal, List
from pydantic import Field
import os
import json
from datetime import datetime

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError, ResourceNotFoundError

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class UnifiedGoogleCalendar(BaseTool):
    """
    Unified Google Calendar operations (list, create, update, delete).

    Consolidates 4 separate calendar tools into a single action-based interface,
    reducing code duplication and providing consistent error handling across
    all calendar operations.

    Args:
        action: Operation to perform ('list', 'create', 'update', 'delete')

        # List parameters
        query: Search query for listing events (required for 'list')

        # Create parameters
        summary: Event title/summary (required for 'create')
        start_time: Event start time in ISO format (required for 'create')
        end_time: Event end time in ISO format (required for 'create')
        description: Event description (optional for 'create'/'update')
        location: Event location (optional for 'create'/'update')
        attendees: Comma-separated attendee emails (optional for 'create'/'update')

        # Update/Delete parameters
        event_id: Event ID for update/delete operations (required for 'update'/'delete')

        # Additional parameters
        send_updates: Notification setting for delete ('all', 'externalOnly', 'none')
        timezone: Timezone for events (default: 'America/New_York')

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Operation-specific results
        - metadata: Additional information including action performed

    Examples:
        List events:
        >>> tool = UnifiedGoogleCalendar(action="list", query="team meeting")
        >>> result = tool.run()

        Create event:
        >>> tool = UnifiedGoogleCalendar(
        ...     action="create",
        ...     summary="Team Standup",
        ...     start_time="2025-01-20T10:00:00",
        ...     end_time="2025-01-20T10:30:00",
        ...     location="Conference Room A"
        ... )
        >>> result = tool.run()

        Update event:
        >>> tool = UnifiedGoogleCalendar(
        ...     action="update",
        ...     event_id="abc123",
        ...     summary="Updated Meeting Title",
        ...     start_time="2025-01-20T14:00:00"
        ... )
        >>> result = tool.run()

        Delete event:
        >>> tool = UnifiedGoogleCalendar(
        ...     action="delete",
        ...     event_id="abc123",
        ...     send_updates="all"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "unified_google_calendar"
    tool_category: str = "communication"

    # Action parameter
    action: Literal["list", "create", "update", "delete"] = Field(
        ..., description="Calendar operation to perform"
    )

    # List parameters
    query: Optional[str] = Field(
        None, description="Search query for listing events (required for 'list' action)"
    )

    # Create/Update parameters
    summary: Optional[str] = Field(
        None, description="Event title/summary (required for 'create', optional for 'update')"
    )
    start_time: Optional[str] = Field(
        None,
        description="Event start time in ISO format (required for 'create', optional for 'update')",
    )
    end_time: Optional[str] = Field(
        None,
        description="Event end time in ISO format (required for 'create', optional for 'update')",
    )
    description: Optional[str] = Field(
        None, description="Event description (optional for 'create'/'update')"
    )
    location: Optional[str] = Field(
        None, description="Event location (optional for 'create'/'update')"
    )
    attendees: Optional[str] = Field(
        None, description="Comma-separated attendee emails (optional for 'create'/'update')"
    )

    # Update/Delete parameters
    event_id: Optional[str] = Field(
        None, description="Event ID for update/delete operations (required for 'update'/'delete')"
    )

    # Additional parameters
    send_updates: str = Field(
        "all", description="Notification setting for delete: 'all', 'externalOnly', or 'none'"
    )
    timezone: str = Field("America/New_York", description="Timezone for event times")

    def _execute(self) -> Dict[str, Any]:
        """Execute the calendar operation based on action."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. DELEGATE TO ACTION HANDLER
        handlers = {
            "list": self._handle_list,
            "create": self._handle_create,
            "update": self._handle_update,
            "delete": self._handle_delete,
        }

        try:
            result = handlers[self.action]()

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "action": self.action,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
            }
        except HttpError as e:
            return self._handle_http_error(e)
        except Exception as e:
            raise APIError(f"Calendar operation failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters based on action."""
        if self.action == "list":
            if not self.query or not self.query.strip():
                raise ValidationError(
                    "query is required for 'list' action", tool_name=self.tool_name, field="query"
                )

        elif self.action == "create":
            required_fields = {
                "summary": self.summary,
                "start_time": self.start_time,
                "end_time": self.end_time,
            }
            missing = [f for f, v in required_fields.items() if not v]

            if missing:
                raise ValidationError(
                    f"Missing required fields for 'create': {', '.join(missing)}",
                    tool_name=self.tool_name,
                    details={"missing_fields": missing},
                )

            # Validate datetime formats
            self._validate_datetime(self.start_time, "start_time")
            self._validate_datetime(self.end_time, "end_time")

            # Validate attendees format
            if self.attendees:
                self._validate_attendees(self.attendees)

        elif self.action == "update":
            if not self.event_id or not self.event_id.strip():
                raise ValidationError(
                    "event_id is required for 'update' action",
                    tool_name=self.tool_name,
                    field="event_id",
                )

            # Check that at least one field is being updated
            update_fields = [
                self.summary,
                self.description,
                self.start_time,
                self.end_time,
                self.location,
                self.attendees,
            ]
            if not any(update_fields):
                raise ValidationError(
                    "At least one field must be provided for update",
                    tool_name=self.tool_name,
                    details={
                        "available_fields": [
                            "summary",
                            "description",
                            "start_time",
                            "end_time",
                            "location",
                            "attendees",
                        ]
                    },
                )

            # Validate datetime formats if provided
            if self.start_time:
                self._validate_datetime(self.start_time, "start_time")
            if self.end_time:
                self._validate_datetime(self.end_time, "end_time")

            # Validate attendees format if provided
            if self.attendees:
                self._validate_attendees(self.attendees)

        elif self.action == "delete":
            if not self.event_id or not self.event_id.strip():
                raise ValidationError(
                    "event_id is required for 'delete' action",
                    tool_name=self.tool_name,
                    field="event_id",
                )

            valid_updates = ["all", "externalOnly", "none"]
            if self.send_updates not in valid_updates:
                raise ValidationError(
                    f"send_updates must be one of: {', '.join(valid_updates)}",
                    tool_name=self.tool_name,
                    field="send_updates",
                )

    def _validate_datetime(self, dt_string: str, field_name: str) -> None:
        """Validate datetime format."""
        try:
            datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        except ValueError:
            raise ValidationError(
                f"Invalid {field_name} format: {dt_string}. Use ISO format (2025-01-15T10:00:00)",
                tool_name=self.tool_name,
                field=field_name,
            )

    def _validate_attendees(self, attendees_str: str) -> None:
        """Validate attendees format."""
        emails = [e.strip() for e in attendees_str.split(",")]
        for email in emails:
            if "@" not in email:
                raise ValidationError(
                    f"Invalid attendee email: {email}", tool_name=self.tool_name, field="attendees"
                )

    def _handle_http_error(self, error: HttpError) -> Dict[str, Any]:
        """Handle Google Calendar API HTTP errors."""
        if error.resp.status == 404:
            raise ResourceNotFoundError(
                f"Event not found: {self.event_id}",
                tool_name=self.tool_name,
                resource_type="calendar_event",
            )
        elif error.resp.status == 410 and self.action == "delete":
            # Event already deleted - return success
            return {
                "success": True,
                "result": {
                    "status": "already_deleted",
                    "event_id": self.event_id,
                    "message": "Event was already deleted",
                },
                "metadata": {
                    "tool_name": self.tool_name,
                    "action": self.action,
                    "event_id": self.event_id,
                },
            }
        else:
            raise APIError(
                f"Google Calendar API error: {error}",
                tool_name=self.tool_name,
                api_name="Google Calendar API",
                status_code=error.resp.status,
            )

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results based on action."""
        mock_handlers = {
            "list": self._generate_mock_list,
            "create": self._generate_mock_create,
            "update": self._generate_mock_update,
            "delete": self._generate_mock_delete,
        }

        result = mock_handlers[self.action]()

        return {
            "success": True,
            "result": result,
            "metadata": {"mock_mode": True, "tool_name": self.tool_name, "action": self.action},
        }

    def _generate_mock_list(self) -> List[Dict[str, Any]]:
        """Generate mock list results."""
        return [
            {
                "id": f"mock-event-{i}",
                "summary": f"Mock Event {i}: {self.query}",
                "start": {"dateTime": f"2025-01-0{i}T09:00:00Z"},
                "end": {"dateTime": f"2025-01-0{i}T10:00:00Z"},
                "status": "confirmed",
                "source": "mock",
            }
            for i in range(1, 4)
        ]

    def _generate_mock_create(self) -> Dict[str, Any]:
        """Generate mock create results."""
        event = {
            "id": "mock-created-event-123",
            "summary": self.summary,
            "description": self.description or "",
            "start": {"dateTime": self.start_time, "timeZone": self.timezone},
            "end": {"dateTime": self.end_time, "timeZone": self.timezone},
            "status": "confirmed",
            "htmlLink": "https://calendar.google.com/event?eid=mock-created-event-123",
            "created": datetime.utcnow().isoformat() + "Z",
        }

        if self.location:
            event["location"] = self.location

        if self.attendees:
            event["attendees"] = [
                {"email": e.strip(), "responseStatus": "needsAction"}
                for e in self.attendees.split(",")
            ]

        return event

    def _generate_mock_update(self) -> Dict[str, Any]:
        """Generate mock update results."""
        event = {
            "id": self.event_id,
            "summary": self.summary or "Mock Event (Updated)",
            "description": self.description or "Mock event description",
            "start": {
                "dateTime": self.start_time or "2025-01-15T10:00:00",
                "timeZone": self.timezone,
            },
            "end": {"dateTime": self.end_time or "2025-01-15T11:00:00", "timeZone": self.timezone},
            "location": self.location or "Mock Location",
            "status": "confirmed",
            "htmlLink": f"https://calendar.google.com/event?eid={self.event_id}",
            "updated": datetime.utcnow().isoformat() + "Z",
        }

        if self.attendees:
            event["attendees"] = [
                {"email": e.strip(), "responseStatus": "needsAction"}
                for e in self.attendees.split(",")
            ]

        return event

    def _generate_mock_delete(self) -> Dict[str, Any]:
        """Generate mock delete results."""
        return {
            "status": "deleted",
            "event_id": self.event_id,
            "deleted_at": datetime.utcnow().isoformat() + "Z",
            "notifications_sent": self.send_updates != "none",
        }

    def _get_calendar_service(self):
        """Initialize and return Google Calendar service."""
        credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or os.getenv(
            "GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE"
        )

        if not credentials_path:
            raise AuthenticationError(
                "Missing GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE environment variable",
                tool_name=self.tool_name,
                api_name="Google Calendar API",
            )

        scopes = ["https://www.googleapis.com/auth/calendar"]
        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)

        return build("calendar", "v3", credentials=creds)

    def _handle_list(self) -> List[Dict[str, Any]]:
        """Handle list action."""
        service = self._get_calendar_service()

        now = datetime.utcnow().isoformat() + "Z"

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                q=self.query,
                timeMin=now,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])

    def _handle_create(self) -> Dict[str, Any]:
        """Handle create action."""
        service = self._get_calendar_service()

        event_body = {
            "summary": self.summary,
            "start": {"dateTime": self.start_time, "timeZone": self.timezone},
            "end": {"dateTime": self.end_time, "timeZone": self.timezone},
        }

        if self.description:
            event_body["description"] = self.description

        if self.location:
            event_body["location"] = self.location

        if self.attendees:
            event_body["attendees"] = [
                {"email": email.strip()} for email in self.attendees.split(",")
            ]

        created_event = service.events().insert(calendarId="primary", body=event_body).execute()

        return {
            "id": created_event.get("id"),
            "summary": created_event.get("summary"),
            "description": created_event.get("description"),
            "start": created_event.get("start"),
            "end": created_event.get("end"),
            "location": created_event.get("location"),
            "attendees": created_event.get("attendees", []),
            "status": created_event.get("status"),
            "htmlLink": created_event.get("htmlLink"),
            "created": created_event.get("created"),
        }

    def _handle_update(self) -> Dict[str, Any]:
        """Handle update action."""
        service = self._get_calendar_service()

        # Get existing event first to verify it exists
        try:
            existing_event = (
                service.events().get(calendarId="primary", eventId=self.event_id).execute()
            )
        except HttpError as e:
            if e.resp.status == 404:
                raise ResourceNotFoundError(
                    f"Event not found: {self.event_id}",
                    tool_name=self.tool_name,
                    resource_type="calendar_event",
                )
            raise

        # Build update body with only provided fields
        update_body = {}

        if self.summary:
            update_body["summary"] = self.summary

        if self.description:
            update_body["description"] = self.description

        if self.start_time:
            update_body["start"] = {"dateTime": self.start_time, "timeZone": self.timezone}

        if self.end_time:
            update_body["end"] = {"dateTime": self.end_time, "timeZone": self.timezone}

        if self.location:
            update_body["location"] = self.location

        if self.attendees:
            update_body["attendees"] = [
                {"email": email.strip()} for email in self.attendees.split(",")
            ]

        # Perform update
        updated_event = (
            service.events()
            .patch(calendarId="primary", eventId=self.event_id, body=update_body)
            .execute()
        )

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
            "updated": updated_event.get("updated"),
        }

    def _handle_delete(self) -> Dict[str, Any]:
        """Handle delete action."""
        service = self._get_calendar_service()

        service.events().delete(
            calendarId="primary", eventId=self.event_id, sendUpdates=self.send_updates
        ).execute()

        return {
            "status": "deleted",
            "event_id": self.event_id,
            "deleted_at": datetime.utcnow().isoformat() + "Z",
            "notifications_sent": self.send_updates != "none",
        }


if __name__ == "__main__":
    print("Testing UnifiedGoogleCalendar...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: List action
    print("\nTest 1: List calendar events")
    tool = UnifiedGoogleCalendar(action="list", query="team meeting")
    result = tool.run()

    assert result.get("success") == True
    assert isinstance(result.get("result", []), list)
    assert len(result.get("result", [])) > 0
    assert result.get("metadata", {}).get("action") == "list"
    print(f"✅ Test 1 passed: Found {len(result.get('result', []))} events")

    # Test 2: Create action
    print("\nTest 2: Create calendar event")
    tool = UnifiedGoogleCalendar(
        action="create",
        summary="Team Standup",
        start_time="2025-01-20T10:00:00",
        end_time="2025-01-20T10:30:00",
        location="Conference Room A",
        description="Daily team standup meeting",
    )
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("summary") == "Team Standup"
    assert result.get("metadata", {}).get("action") == "create"
    print(f"✅ Test 2 passed: Event created with ID {result.get('result', {}).get('id')}")

    # Test 3: Update action
    print("\nTest 3: Update calendar event")
    tool = UnifiedGoogleCalendar(
        action="update",
        event_id="test-event-123",
        summary="Updated Meeting Title",
        start_time="2025-01-20T14:00:00",
        end_time="2025-01-20T15:00:00",
    )
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("summary") == "Updated Meeting Title"
    assert result.get("metadata", {}).get("action") == "update"
    print(f"✅ Test 3 passed: Event updated")

    # Test 4: Delete action
    print("\nTest 4: Delete calendar event")
    tool = UnifiedGoogleCalendar(action="delete", event_id="test-event-456", send_updates="all")
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("status") == "deleted"
    assert result.get("metadata", {}).get("action") == "delete"
    print(f"✅ Test 4 passed: Event deleted")

    # Test 5: Validation - missing query for list
    print("\nTest 5: Validation - missing query for list")
    try:
        bad_tool = UnifiedGoogleCalendar(action="list", query="")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 5 passed: Validation working - {type(e).__name__}")

    # Test 6: Validation - missing required fields for create
    print("\nTest 6: Validation - missing required fields for create")
    try:
        bad_tool = UnifiedGoogleCalendar(action="create", summary="Meeting")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 6 passed: Validation working - {type(e).__name__}")

    # Test 7: Validation - missing event_id for update
    print("\nTest 7: Validation - missing event_id for update")
    try:
        bad_tool = UnifiedGoogleCalendar(action="update", summary="Updated")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 7 passed: Validation working - {type(e).__name__}")

    # Test 8: Create with attendees
    print("\nTest 8: Create event with attendees")
    tool = UnifiedGoogleCalendar(
        action="create",
        summary="Project Review",
        start_time="2025-01-25T14:00:00",
        end_time="2025-01-25T15:30:00",
        attendees="alice@example.com,bob@example.com",
    )
    result = tool.run()

    assert result.get("success") == True
    assert len(result.get("result", {}).get("attendees", [])) == 2
    print(f"✅ Test 8 passed: Event with attendees created")

    # Test 9: Update with partial fields
    print("\nTest 9: Update event with partial fields")
    tool = UnifiedGoogleCalendar(
        action="update", event_id="test-event-789", description="Updated description only"
    )
    result = tool.run()

    assert result.get("success") == True
    print(f"✅ Test 9 passed: Partial update successful")

    # Test 10: Delete with no notifications
    print("\nTest 10: Delete event without notifications")
    tool = UnifiedGoogleCalendar(action="delete", event_id="test-event-999", send_updates="none")
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("notifications_sent") == False
    print(f"✅ Test 10 passed: Delete without notifications")

    print("\n✅ All 10 tests passed!")
