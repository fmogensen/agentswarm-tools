# google_calendar_delete_event

Delete Google Calendar events.

## Category

Communication & Productivity

## Parameters

- **event_id** (str): The ID of the event to delete - **Required**
- **send_updates** (str): Send notifications: 'all', 'externalOnly', or 'none' - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.google_calendar_delete_event import GoogleCalendarDeleteEvent

# Initialize the tool
tool = GoogleCalendarDeleteEvent(
    event_id="example_value",
    send_updates="example_value"  # Optional
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
python google_calendar_delete_event.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
