# unified_google_calendar

Unified Google Calendar operations (list, create, update, delete).

## Category

Communication & Productivity

## Parameters

- **action** (Literal["list", "create", "update", "delete"): Calendar operation to perform - **Required**
- **query** (str): No description - Optional
- **summary** (str): No description - Optional
- **start_time** (str): No description - Optional
- **end_time** (str): No description - Optional
- **description** (str): No description - Optional
- **location** (str): No description - Optional
- **attendees** (str): No description - Optional
- **event_id** (str): No description - Optional
- **send_updates** (str): Notification setting for delete: 'all', 'externalOnly', or 'none' - Optional
- **timezone** (str): Timezone for event times - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

# Initialize the tool
tool = UnifiedGoogleCalendar(
    action="example_value",
    query="example_value",  # Optional
    summary="example_value"  # Optional
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
python unified_google_calendar.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
