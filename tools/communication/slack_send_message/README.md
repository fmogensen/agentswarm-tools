# slack_send_message

Send messages to Slack channels via Slack API.

## Category

Communication & Productivity

## Parameters

- **channel** (str): No description - **Required**
- **text** (str): Message text content - **Required**
- **thread_ts** (str): Timestamp of parent message to reply in thread - Optional
- **blocks** (str): Structured blocks in JSON format for rich formatting - Optional
- **username** (str): Bot username override - Optional
- **icon_emoji** (str): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.slack_send_message import SlackSendMessage

# Initialize the tool
tool = SlackSendMessage(
    channel="example_value",
    text="example_value",
    thread_ts="example_value"  # Optional
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
python slack_send_message.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
