# teams_send_message

Send messages to Microsoft Teams channels via Microsoft Graph API.

## Category

Communication & Productivity

## Parameters

- **team_id** (str): The ID of the Microsoft Teams team - **Required**
- **channel_id** (str): The ID of the channel within the team - **Required**
- **message** (str): No description - **Required**
- **subject** (str): Message subject/title - Optional
- **content_type** (str): Content type - 'text' or 'html' - Optional
- **importance** (str): Message importance - 'normal', 'high', or 'low' - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.teams_send_message import TeamsSendMessage

# Initialize the tool
tool = TeamsSendMessage(
    team_id="example_value",
    channel_id="example_value",
    message="example_value"
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
python teams_send_message.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
