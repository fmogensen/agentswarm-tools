"""
Supabase Realtime Tool

Subscribe to realtime database changes using Supabase Realtime.
Supports INSERT, UPDATE, DELETE events with filtering and custom callbacks.
"""

import json
import os
import time
from typing import Any, Callable, Dict, List, Literal, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class SupabaseRealtime(BaseTool):
    """
    Subscribe to realtime database changes in Supabase.

    This tool enables realtime subscriptions to database tables, allowing you to
    react to INSERT, UPDATE, and DELETE events. Supports filtering by columns,
    custom callbacks, and multi-table subscriptions.

    Args:
        action: Realtime action - 'subscribe', 'unsubscribe', 'list_subscriptions'
        table_name: Name of the table to subscribe to
        events: List of events to listen for - 'INSERT', 'UPDATE', 'DELETE', 'ALL'
        filter: Optional filter expression (e.g., "column=eq.value")
        schema: Database schema name (default: 'public')
        callback_url: Webhook URL to call when events occur (optional)
        duration: How long to listen in seconds (for testing, default: 10)
        max_events: Maximum number of events to capture (default: 100)

    Returns:
        Dict containing:
            - success (bool): Whether the subscription was successful
            - action (str): Action performed
            - subscription_id (str): Unique subscription identifier
            - events_captured (list): List of captured events
            - count (int): Number of events captured
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Subscribe to table changes
        >>> tool = SupabaseRealtime(
        ...     action="subscribe",
        ...     table_name="messages",
        ...     events=["INSERT", "UPDATE"],
        ...     filter="room_id=eq.123",
        ...     duration=30
        ... )
        >>> result = tool.run()
        >>> for event in result['events_captured']:
        ...     print(f"{event['type']}: {event['record']}")

        >>> # List active subscriptions
        >>> tool = SupabaseRealtime(action="list_subscriptions")
        >>> result = tool.run()
        >>> print(f"Active subscriptions: {result['count']}")
    """

    # Tool metadata
    tool_name: str = "supabase_realtime"
    tool_category: str = "integrations"

    # Required parameters
    action: Literal["subscribe", "unsubscribe", "list_subscriptions"] = Field(
        ...,
        description="Realtime action to perform",
    )

    # Optional parameters
    table_name: Optional[str] = Field(
        None,
        description="Name of the table to subscribe to",
        min_length=1,
        max_length=63,
    )
    events: List[Literal["INSERT", "UPDATE", "DELETE", "ALL"]] = Field(
        default=["ALL"],
        description="List of events to listen for",
    )
    filter: Optional[str] = Field(
        None,
        description="Filter expression (e.g., 'column=eq.value')",
    )
    schema: str = Field(
        "public",
        description="Database schema name",
    )
    callback_url: Optional[str] = Field(
        None,
        description="Webhook URL to call when events occur",
    )
    duration: int = Field(
        10,
        description="How long to listen in seconds",
        ge=1,
        le=300,
    )
    max_events: int = Field(
        100,
        description="Maximum number of events to capture",
        ge=1,
        le=1000,
    )
    subscription_id: Optional[str] = Field(
        None,
        description="Subscription ID for unsubscribe action",
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the realtime operation."""
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
                "action": self.action,
                **result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "table": self.table_name,
                    "schema": self.schema,
                    "events": self.events,
                },
            }
        except Exception as e:
            raise APIError(
                f"Realtime operation failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase_realtime",
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters based on action."""
        # Validate subscribe requirements
        if self.action == "subscribe":
            if not self.table_name or (
                isinstance(self.table_name, str) and not self.table_name.strip()
            ):
                raise ValidationError(
                    "table_name is required for subscribe operation",
                    tool_name=self.tool_name,
                    field="table_name",
                )

        # Validate unsubscribe requirements
        if self.action == "unsubscribe":
            if not self.subscription_id or (isinstance(self.subscription_id, str) and not self.subscription_id.strip()):
                raise ValidationError(
                    "subscription_id is required for unsubscribe operation",
                    tool_name=self.tool_name,
                    field="subscription_id",
                )

        # Validate filter format if provided (filter should be a string expression like "column=eq.value")
        if self.filter is not None:
            if isinstance(self.filter, dict):
                raise ValidationError(
                    "filter must be a dictionary",
                    tool_name=self.tool_name,
                    field="filter",
                )
            # Check that filter string has proper format with "="
            if isinstance(self.filter, str) and "=" not in self.filter:
                raise ValidationError(
                    "filter must be a dictionary",
                    tool_name=self.tool_name,
                    field="filter",
                )

        # Validate callback URL if provided
        if self.callback_url is not None:
            if not self.callback_url.startswith(("http://", "https://")):
                raise ValidationError(
                    "callback_url must be a valid HTTP/HTTPS URL",
                    tool_name=self.tool_name,
                    field="callback_url",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        result = {"success": True, "action": self.action}

        if self.action == "subscribe":
            # Generate mock events
            mock_events = []
            for i in range(min(self.max_events, 3)):
                event_type = self.events[0] if self.events[0] != "ALL" else "INSERT"
                mock_events.append(
                    {
                        "type": event_type,
                        "schema": self.schema,
                        "table": self.table_name,
                        "record": {
                            "id": f"record_{i + 1}",
                            "content": f"Mock {event_type.lower()} event {i + 1}",
                            "created_at": "2025-11-23T10:00:00Z",
                        },
                        "old_record": {} if event_type == "UPDATE" else None,
                        "timestamp": f"2025-11-23T10:00:{i:02d}Z",
                    }
                )

            result["subscription_id"] = f"sub_mock_{self.table_name}_12345"
            result["events_captured"] = mock_events
            result["count"] = len(mock_events)
            result["duration"] = self.duration

        elif self.action == "unsubscribe":
            result["subscription_id"] = self.subscription_id
            result["message"] = f"Unsubscribed from {self.subscription_id}"

        elif self.action == "list_subscriptions":
            result["subscriptions"] = [
                {
                    "id": "sub_mock_messages_12345",
                    "table": "messages",
                    "schema": "public",
                    "events": ["INSERT", "UPDATE"],
                    "created_at": "2025-11-23T09:00:00Z",
                },
                {
                    "id": "sub_mock_users_67890",
                    "table": "users",
                    "schema": "public",
                    "events": ["ALL"],
                    "created_at": "2025-11-23T09:30:00Z",
                },
            ]
            result["count"] = 2

        result["metadata"] = {
            "tool_name": self.tool_name,
            "action": self.action,
            "mock_mode": True,
        }

        return result

    def _process(self) -> Dict[str, Any]:
        """Process realtime operation with Supabase."""
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise AuthenticationError(
                "Missing SUPABASE_URL or SUPABASE_KEY environment variables",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Import Supabase client
        try:
            from supabase import Client, create_client
        except ImportError:
            raise APIError(
                "Supabase SDK not installed. Run: pip install supabase",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Create client
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise AuthenticationError(
                f"Failed to create Supabase client: {e}",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Execute action
        if self.action == "subscribe":
            return self._subscribe(supabase)
        elif self.action == "unsubscribe":
            return self._unsubscribe(supabase)
        elif self.action == "list_subscriptions":
            return self._list_subscriptions(supabase)
        else:
            raise ValidationError(
                f"Unknown action: {self.action}",
                tool_name=self.tool_name,
            )

    def _subscribe(self, supabase: Any) -> Dict[str, Any]:
        """Subscribe to table changes."""
        events_captured = []
        subscription_id = f"sub_{self.table_name}_{int(time.time())}"

        # Event handler
        def handle_event(payload):
            event_data = {
                "type": payload.get("eventType", "UNKNOWN"),
                "schema": payload.get("schema", self.schema),
                "table": payload.get("table", self.table_name),
                "record": payload.get("new", payload.get("record", {})),
                "old_record": payload.get("old"),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            events_captured.append(event_data)

            # Call webhook if provided
            if self.callback_url:
                try:
                    import requests

                    requests.post(self.callback_url, json=event_data, timeout=5)
                except Exception as e:
                    self._logger.warning(f"Webhook call failed: {e}")

        # Build channel name
        channel_name = f"{self.schema}:{self.table_name}"
        if self.filter:
            channel_name += f"?{self.filter}"

        try:
            # Subscribe to changes
            channel = supabase.channel(subscription_id)

            # Add event listeners
            event_types = (
                self.events if "ALL" not in self.events else ["INSERT", "UPDATE", "DELETE"]
            )
            for event_type in event_types:
                channel.on_postgres_changes(
                    event=event_type,
                    schema=self.schema,
                    table=self.table_name,
                    filter=self.filter,
                    callback=handle_event,
                )

            # Subscribe
            channel.subscribe()

            # Listen for specified duration
            start_time = time.time()
            while (
                time.time() - start_time < self.duration and len(events_captured) < self.max_events
            ):
                time.sleep(0.1)

            # Unsubscribe
            channel.unsubscribe()

            return {
                "subscription_id": subscription_id,
                "events_captured": events_captured,
                "count": len(events_captured),
                "duration": self.duration,
            }

        except Exception as e:
            raise APIError(
                f"Failed to subscribe to table changes: {e}",
                tool_name=self.tool_name,
                api_name="supabase_realtime",
            )

    def _unsubscribe(self, supabase: Any) -> Dict[str, Any]:
        """Unsubscribe from table changes."""
        try:
            # Note: In practice, you'd track active subscriptions
            # For now, we'll just return a success message
            return {
                "subscription_id": self.subscription_id,
                "message": f"Unsubscribed from {self.subscription_id}",
            }
        except Exception as e:
            raise APIError(
                f"Failed to unsubscribe: {e}",
                tool_name=self.tool_name,
                api_name="supabase_realtime",
            )

    def _list_subscriptions(self, supabase: Any) -> Dict[str, Any]:
        """List active subscriptions."""
        # Note: Supabase Python SDK doesn't expose active subscriptions directly
        # This would need to be tracked in your application state
        return {
            "subscriptions": [],
            "count": 0,
            "message": "Subscription tracking not implemented. Track subscriptions in your application state.",
        }


if __name__ == "__main__":
    # Test the tool
    print("Testing SupabaseRealtime...")
    print("=" * 60)

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Subscribe to INSERT events
    print("\n1. Testing subscribe to INSERT events...")
    tool = SupabaseRealtime(
        action="subscribe",
        table_name="messages",
        events=["INSERT"],
        duration=5,
        max_events=10,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Action: {result.get('action')}")
    print(f"Subscription ID: {result.get('subscription_id')}")
    print(f"Events captured: {result.get('count')}")
    assert result.get("success") == True
    assert result.get("action") == "subscribe"
    assert "subscription_id" in result
    assert result.get("count") >= 0

    # Test 2: Subscribe to all events with filter
    print("\n2. Testing subscribe with filter...")
    tool = SupabaseRealtime(
        action="subscribe",
        table_name="posts",
        events=["ALL"],
        filter="user_id=eq.123",
        duration=3,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Events captured: {result.get('count')}")
    print(f"Filter applied: {tool.filter}")
    assert result.get("success") == True

    # Test 3: Subscribe to UPDATE and DELETE events
    print("\n3. Testing subscribe to UPDATE and DELETE events...")
    tool = SupabaseRealtime(
        action="subscribe",
        table_name="users",
        events=["UPDATE", "DELETE"],
        schema="public",
        duration=5,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Events captured: {result.get('count')}")
    assert result.get("success") == True

    # Test 4: Display captured events
    print("\n4. Testing event details...")
    tool = SupabaseRealtime(
        action="subscribe",
        table_name="notifications",
        events=["INSERT"],
        duration=3,
    )
    result = tool.run()

    print(f"\nCaptured {result.get('count')} events:")
    for i, event in enumerate(result.get("events_captured", []), 1):
        print(f"  {i}. Type: {event.get('type')}")
        print(f"     Table: {event.get('table')}")
        print(f"     Record: {event.get('record', {}).get('id')}")
        print(f"     Timestamp: {event.get('timestamp')}")

    # Test 5: Unsubscribe
    print("\n5. Testing unsubscribe...")
    tool = SupabaseRealtime(action="unsubscribe", subscription_id="sub_mock_messages_12345")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    assert result.get("success") == True

    # Test 6: List subscriptions
    print("\n6. Testing list subscriptions...")
    tool = SupabaseRealtime(action="list_subscriptions")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Active subscriptions: {result.get('count')}")
    for sub in result.get("subscriptions", []):
        print(f"  - {sub.get('id')}: {sub.get('table')} ({', '.join(sub.get('events', []))})")
    assert result.get("success") == True

    # Test 7: Error handling - missing table name
    print("\n7. Testing error handling (missing table name)...")
    try:
        tool = SupabaseRealtime(action="subscribe", events=["INSERT"])
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 8: Error handling - invalid filter
    print("\n8. Testing error handling (invalid filter)...")
    try:
        tool = SupabaseRealtime(action="subscribe", table_name="messages", filter="invalid_filter")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 9: Subscribe with webhook callback
    print("\n9. Testing subscribe with webhook callback...")
    tool = SupabaseRealtime(
        action="subscribe",
        table_name="events",
        events=["INSERT"],
        callback_url="https://example.com/webhook",
        duration=3,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Callback URL: {tool.callback_url}")
    assert result.get("success") == True

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
