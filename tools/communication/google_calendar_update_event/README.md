# google_calendar_update_event

Update existing Google Calendar events.

## Category

Communication & Productivity

## Parameters

- **event_id** (str): The ID of the event to update - **Required**
- **summary** (str): New event title/summary - Optional
- **description** (str): New event description - Optional
- **start_time** (str): No description - Optional
- **end_time** (str): No description - Optional
- **location** (str): New location - Optional
- **attendees** (str): No description - Optional
- **timezone** (str): Timezone for the event - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.google_calendar_update_event import GoogleCalendarUpdateEvent

# Initialize the tool
tool = GoogleCalendarUpdateEvent(
    event_id="example_value",
    summary="example_value",  # Optional
    description="example_value"  # Optional
)

# Run the tool
result = tool.run()

# Check result
if result["success"]:
    print(result["result"])
else:
    print(f"Error: {result.get('error')}")
```

## Testing

Run tests with:
```bash
python google_calendar_update_event.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
