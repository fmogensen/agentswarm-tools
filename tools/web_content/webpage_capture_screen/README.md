# webpage_capture_screen



## Category

Web Content & Data Access

## Parameters

- **input**: Primary input parameter


## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.web_content.webpage_capture_screen import WebpageCaptureScreen

# Initialize the tool
tool = WebpageCaptureScreen(
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
pytest tools/web_content/webpage_capture_screen/test_webpage_capture_screen.py -v
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../TOOLS_DOCUMENTATION.md)
- [Examples](../../../TOOL_EXAMPLES.md)
- [Category Overview](../README.md)
