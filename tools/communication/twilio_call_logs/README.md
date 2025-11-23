# twilio_call_logs

Retrieve and analyze Twilio call logs with filtering and optional transcript support.

## Category

Communication & Productivity

## Parameters

- **time_range_hours** (int): Hours to look back from current time - Optional
- **limit** (int): Maximum number of calls to return - Optional
- **include_transcript** (bool): Whether to include call transcripts in results - Optional
- **filter_status** (Literal["completed", "failed", "busy"): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.twilio_call_logs import TwilioCallLogs

# Initialize the tool
tool = TwilioCallLogs(
    time_range_hours="example_value",  # Optional
    limit="example_value",  # Optional
    include_transcript="example_value"  # Optional
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
python twilio_call_logs.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
