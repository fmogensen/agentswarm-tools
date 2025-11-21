# google_calendar_list



## Category

Communication & Productivity

## Parameters

- **input**: Primary input parameter


## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.google_calendar_list import GoogleCalendarList

# Initialize the tool
tool = GoogleCalendarList(
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
pytest tools/communication/google_calendar_list/test_google_calendar_list.py -v
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../TOOLS_DOCUMENTATION.md)
- [Examples](../../../TOOL_EXAMPLES.md)
- [Category Overview](../README.md)
