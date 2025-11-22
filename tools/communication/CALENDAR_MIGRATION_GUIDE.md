# Google Calendar Tools Migration Guide

## Overview

The 4 separate Google Calendar tools have been consolidated into a single `UnifiedGoogleCalendar` tool with an action-based interface. This guide shows how to migrate from the deprecated tools to the new unified tool.

## Quick Reference

| Old Tool | New Equivalent |
|----------|---------------|
| `GoogleCalendarList` | `UnifiedGoogleCalendar(action="list", ...)` |
| `GoogleCalendarCreateEventDraft` | `UnifiedGoogleCalendar(action="create", ...)` |
| `GoogleCalendarUpdateEvent` | `UnifiedGoogleCalendar(action="update", ...)` |
| `GoogleCalendarDeleteEvent` | `UnifiedGoogleCalendar(action="delete", ...)` |

## Migration Examples

### 1. List Calendar Events

**Before (Deprecated):**
```python
from tools.communication.google_calendar_list import GoogleCalendarList

tool = GoogleCalendarList(input="team meeting")
result = tool.run()
```

**After (Recommended):**
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

tool = UnifiedGoogleCalendar(
    action="list",
    query="team meeting"
)
result = tool.run()
```

### 2. Create Calendar Event

**Before (Deprecated):**
```python
import json
from tools.communication.google_calendar_create_event_draft import GoogleCalendarCreateEventDraft

event_data = {
    "title": "Team Standup",
    "start_time": "2025-01-20T10:00:00",
    "end_time": "2025-01-20T10:30:00",
    "description": "Daily standup meeting",
    "location": "Conference Room A",
    "attendees": "alice@example.com,bob@example.com"
}

tool = GoogleCalendarCreateEventDraft(input=json.dumps(event_data))
result = tool.run()
```

**After (Recommended):**
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

tool = UnifiedGoogleCalendar(
    action="create",
    summary="Team Standup",  # Note: "title" is now "summary"
    start_time="2025-01-20T10:00:00",
    end_time="2025-01-20T10:30:00",
    description="Daily standup meeting",
    location="Conference Room A",
    attendees="alice@example.com,bob@example.com"
)
result = tool.run()
```

**Key Changes:**
- No need to JSON-encode the event data
- Field name changed: `title` → `summary` (matches Google Calendar API)
- Direct parameter passing instead of JSON string

### 3. Update Calendar Event

**Before (Deprecated):**
```python
from tools.communication.google_calendar_update_event import GoogleCalendarUpdateEvent

tool = GoogleCalendarUpdateEvent(
    event_id="abc123",
    summary="Updated Meeting Title",
    start_time="2025-01-20T14:00:00",
    end_time="2025-01-20T15:00:00",
    location="Conference Room B"
)
result = tool.run()
```

**After (Recommended):**
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

tool = UnifiedGoogleCalendar(
    action="update",
    event_id="abc123",
    summary="Updated Meeting Title",
    start_time="2025-01-20T14:00:00",
    end_time="2025-01-20T15:00:00",
    location="Conference Room B"
)
result = tool.run()
```

**Key Changes:**
- Add `action="update"` parameter
- All other parameters remain the same

### 4. Delete Calendar Event

**Before (Deprecated):**
```python
from tools.communication.google_calendar_delete_event import GoogleCalendarDeleteEvent

tool = GoogleCalendarDeleteEvent(
    event_id="abc123",
    send_updates="all"
)
result = tool.run()
```

**After (Recommended):**
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

tool = UnifiedGoogleCalendar(
    action="delete",
    event_id="abc123",
    send_updates="all"
)
result = tool.run()
```

**Key Changes:**
- Add `action="delete"` parameter
- All other parameters remain the same

## Parameter Mapping

### List Action
| Old (GoogleCalendarList) | New (UnifiedGoogleCalendar) |
|--------------------------|----------------------------|
| `input` | `query` |

### Create Action
| Old (GoogleCalendarCreateEventDraft) | New (UnifiedGoogleCalendar) |
|--------------------------------------|----------------------------|
| `input` (JSON with "title") | `summary` (direct parameter) |
| `input` (JSON with "start_time") | `start_time` (direct parameter) |
| `input` (JSON with "end_time") | `end_time` (direct parameter) |
| `input` (JSON with "description") | `description` (direct parameter) |
| `input` (JSON with "location") | `location` (direct parameter) |
| `input` (JSON with "attendees") | `attendees` (direct parameter) |

### Update Action
All parameters remain the same, just add `action="update"`.

### Delete Action
All parameters remain the same, just add `action="delete"`.

## Backward Compatibility

The old tools still work and automatically delegate to `UnifiedGoogleCalendar`. However:

1. A `DeprecationWarning` is emitted when using old tools
2. Response metadata includes `"deprecated": true` flag
3. Old tools will be removed in a future version

## Benefits of Migrating

1. **Reduced Code Duplication**: Single implementation for all calendar operations
2. **Consistent Error Handling**: Unified error messages and validation
3. **Easier Maintenance**: One tool to update instead of four
4. **Better Testing**: Comprehensive test suite for all actions
5. **Cleaner API**: No JSON encoding required for create action

## Common Patterns

### Creating Multiple Events
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

events = [
    {
        "summary": "Morning Standup",
        "start_time": "2025-01-20T09:00:00",
        "end_time": "2025-01-20T09:30:00"
    },
    {
        "summary": "Team Lunch",
        "start_time": "2025-01-20T12:00:00",
        "end_time": "2025-01-20T13:00:00"
    }
]

for event_data in events:
    tool = UnifiedGoogleCalendar(action="create", **event_data)
    result = tool.run()
    print(f"Created: {result['result']['id']}")
```

### Searching and Updating Events
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

# Search for events
list_tool = UnifiedGoogleCalendar(action="list", query="team meeting")
events = list_tool.run()

# Update the first matching event
if events['result']:
    event_id = events['result'][0]['id']

    update_tool = UnifiedGoogleCalendar(
        action="update",
        event_id=event_id,
        location="Updated Location"
    )
    update_tool.run()
```

## Testing Your Migration

Use mock mode to test your migration without hitting the actual API:

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

# Test list
tool = UnifiedGoogleCalendar(action="list", query="test")
result = tool.run()
assert result['success'] == True

# Test create
tool = UnifiedGoogleCalendar(
    action="create",
    summary="Test Event",
    start_time="2025-01-20T10:00:00",
    end_time="2025-01-20T11:00:00"
)
result = tool.run()
assert result['success'] == True

# Test update
tool = UnifiedGoogleCalendar(
    action="update",
    event_id="test-123",
    summary="Updated"
)
result = tool.run()
assert result['success'] == True

# Test delete
tool = UnifiedGoogleCalendar(
    action="delete",
    event_id="test-123"
)
result = tool.run()
assert result['success'] == True
```

## Timeline

- **Now**: Both old and new tools work (old tools delegate to new)
- **Q2 2025**: Deprecation warnings added to old tools
- **Q3 2025**: Old tools marked for removal
- **Q4 2025**: Old tools removed (breaking change)

## Questions?

For questions or issues with migration, please:
1. Check the comprehensive test suite in `test_unified_google_calendar.py`
2. Review the tool source code in `unified_google_calendar.py`
3. Consult the CALENDAR_CONSOLIDATION.md technical documentation
