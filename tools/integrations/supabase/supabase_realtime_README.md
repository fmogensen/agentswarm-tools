# SupabaseRealtime

Subscribe to realtime database changes using Supabase Realtime.

## Overview

Listen to INSERT, UPDATE, and DELETE events on database tables in realtime. Perfect for collaborative apps, live notifications, and data synchronization.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | str | Yes | subscribe, unsubscribe, list_subscriptions |
| `table_name` | str | Optional | Table to subscribe to |
| `events` | List[str] | No | Events to listen for (INSERT, UPDATE, DELETE, ALL) |
| `filter` | str | Optional | Filter expression (e.g., "column=eq.value") |
| `schema` | str | No | Database schema (default: "public") |
| `callback_url` | str | Optional | Webhook URL to call on events |
| `duration` | int | No | Listen duration in seconds (default: 10) |
| `max_events` | int | No | Max events to capture (default: 100) |
| `subscription_id` | str | Optional | ID for unsubscribe action |

## Examples

### Basic Subscription

```python
from tools.integrations.supabase import SupabaseRealtime

# Listen for new messages
tool = SupabaseRealtime(
    action="subscribe",
    table_name="messages",
    events=["INSERT"],
    duration=30  # Listen for 30 seconds
)
result = tool.run()

for event in result['events_captured']:
    print(f"New message: {event['record']}")
```

### Filtered Subscription

```python
# Listen for specific room
tool = SupabaseRealtime(
    action="subscribe",
    table_name="messages",
    events=["INSERT", "UPDATE"],
    filter="room_id=eq.123",
    duration=60
)
result = tool.run()
```

### Webhook Integration

```python
# Send events to webhook
tool = SupabaseRealtime(
    action="subscribe",
    table_name="orders",
    events=["INSERT"],
    callback_url="https://yourapp.com/webhook",
    duration=300  # 5 minutes
)
result = tool.run()

# Your webhook receives:
# {
#     "type": "INSERT",
#     "table": "orders",
#     "record": {...},
#     "timestamp": "2025-11-23T10:00:00Z"
# }
```

## Use Cases

### Live Chat

```python
# Subscribe to chat messages
chat_sub = SupabaseRealtime(
    action="subscribe",
    table_name="messages",
    events=["INSERT"],
    filter="channel_id=eq.general",
    duration=3600  # 1 hour
)
result = chat_sub.run()
```

### Collaborative Editing

```python
# Track document changes
doc_sub = SupabaseRealtime(
    action="subscribe",
    table_name="documents",
    events=["UPDATE"],
    filter="document_id=eq.doc_123",
    duration=1800  # 30 minutes
)
result = doc_sub.run()
```

### Notifications

```python
# Listen for new notifications
notif_sub = SupabaseRealtime(
    action="subscribe",
    table_name="notifications",
    events=["INSERT"],
    filter="user_id=eq.user_456",
    callback_url="https://app.com/notify",
    duration=86400  # 24 hours
)
result = notif_sub.run()
```

---

**Version:** 1.0.0
