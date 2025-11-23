# slack_read_messages

Read messages from Slack channels via Slack API.

## Category

Communication & Productivity

## Parameters

- **channel** (str): No description - **Required**
- **limit** (int): Maximum number of messages to retrieve - Optional
- **oldest** (str): Timestamp to get messages after - Optional
- **latest** (str): Timestamp to get messages before - Optional
- **include_threads** (bool): Whether to include thread replies - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.slack_read_messages import SlackReadMessages

# Initialize the tool
tool = SlackReadMessages(
    channel="example_value",
    limit="example_value",  # Optional
    oldest="example_value"  # Optional
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
python slack_read_messages.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
