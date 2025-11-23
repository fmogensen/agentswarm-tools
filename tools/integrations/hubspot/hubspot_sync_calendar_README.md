# HubSpot Sync Calendar Tool

Sync HubSpot meetings with Google Calendar for seamless schedule management.

## Overview

Features:
- Create/update/delete meetings
- Bidirectional sync
- Google Calendar integration
- Attendee management
- Automated reminders
- Meeting outcome tracking

## Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `operation` | str | Operation (hubspot_to_google, google_to_hubspot, bidirectional, create_meeting, update_meeting, delete_meeting) |

### Meeting Details (for create/update)

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | str | Meeting title (required for create) |
| `start_time` | str | ISO 8601 start time (required for create) |
| `end_time` | str | ISO 8601 end time (required for create) |
| `description` | str | Meeting description |
| `location` | str | Location or video link |

### Attendees

| Parameter | Type | Description |
|-----------|------|-------------|
| `attendee_emails` | List[str] | Email addresses |
| `contact_ids` | List[str] | HubSpot contact IDs |
| `owner_id` | str | HubSpot owner ID |

### Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `meeting_type` | str | None | Type (sales_call, demo, consultation, followup) |
| `outcome` | str | None | Outcome (scheduled, completed, cancelled, no_show) |
| `send_notifications` | bool | True | Send notifications |
| `reminder_minutes` | int | None | Reminder time |

### Sync Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sync_interval` | int | None | Auto-sync interval (hours) |
| `date_range_days` | int | 30 | Days to sync |
| `include_past_events` | bool | False | Include past events |

## Examples

### Create Meeting

```python
from tools.integrations.hubspot import HubSpotSyncCalendar

tool = HubSpotSyncCalendar(
    operation="create_meeting",
    title="Sales Demo - Acme Corp",
    start_time="2024-03-15T14:00:00Z",
    end_time="2024-03-15T15:00:00Z",
    description="Product demo and Q&A",
    location="https://zoom.us/j/123456789",
    attendee_emails=["john@acme.com"],
    contact_ids=["12345"],
    meeting_type="demo",
    send_notifications=True,
    reminder_minutes=15
)

result = tool.run()
print(f"Meeting created: {result['meeting_id']}")
```

### Update Meeting Outcome

```python
tool = HubSpotSyncCalendar(
    operation="update_meeting",
    meeting_id="meeting_123",
    outcome="completed",
    description="Demo completed. Next steps: proposal"
)

result = tool.run()
```

### Bidirectional Sync

```python
tool = HubSpotSyncCalendar(
    operation="bidirectional",
    date_range_days=30,
    sync_interval=24  # Sync every 24 hours
)

result = tool.run()
print(f"Synced {result['meetings_synced']} meetings")
print(f"Next sync: {result['next_sync']}")
```

## Best Practices

### 1. Automated Meeting Creation

```python
def schedule_demo(contact_id, preferred_time):
    """Automatically schedule demo meeting."""
    tool = HubSpotSyncCalendar(
        operation="create_meeting",
        title=f"Product Demo - Contact {contact_id}",
        start_time=preferred_time,
        end_time=(datetime.fromisoformat(preferred_time) + timedelta(hours=1)).isoformat(),
        contact_ids=[contact_id],
        meeting_type="demo",
        send_notifications=True
    )
    return tool.run()
```

### 2. Meeting Follow-up

```python
def complete_meeting_with_followup(meeting_id, outcome, next_steps):
    """Update meeting and create follow-up task."""
    # Update meeting outcome
    tool = HubSpotSyncCalendar(
        operation="update_meeting",
        meeting_id=meeting_id,
        outcome=outcome,
        description=f"Outcome: {outcome}. Next steps: {next_steps}"
    )
    result = tool.run()

    # Create follow-up if successful
    if outcome == "completed":
        # Create task or next meeting
        pass

    return result
```

## Related Tools

- **HubSpotCreateContact**: Create meeting attendees
- **HubSpotTrackDeal**: Link meetings to deals
- **HubSpotSendEmail**: Send meeting invites

## API Reference

HubSpot Meetings API: https://developers.hubspot.com/docs/api/crm/meetings
