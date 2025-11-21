# google_calendar_create_event_draft



## Category

Communication & Productivity

## Parameters

- **input**: Primary input parameter. Must be a JSON string containing event draft details.


## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.google_calendar_create_event_draft import GoogleCalendarCreateEventDraft

# Initialize the tool
tool = GoogleCalendarCreateEventDraft(
    input="example_value"
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
pytest tools/communication/google_calendar_create_event_draft/test_google_calendar_create_event_draft.py -v
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../TOOLS_DOCUMENTATION.md)
- [Examples](../../../TOOL_EXAMPLES.md)
- [Category Overview](../README.md)
