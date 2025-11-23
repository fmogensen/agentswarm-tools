# email_send

Send emails via Gmail API.

## Category

Communication & Productivity

## Parameters

- **to** (str): No description - **Required**
- **subject** (str): Email subject line - **Required**
- **body** (str): No description - **Required**
- **cc** (str): CC recipients - comma-separated list - Optional
- **bcc** (str): BCC recipients - comma-separated list - Optional
- **is_html** (bool): Whether body is HTML format - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.email_send import EmailSend

# Initialize the tool
tool = EmailSend(
    to="example_value",
    subject="example_value",
    body="example_value"
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
python email_send.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
