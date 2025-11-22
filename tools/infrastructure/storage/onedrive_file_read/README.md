# onedrive_file_read

Read and process OneDrive/SharePoint files, answer questions about content

    Args:
        input: Primary input parameter containing file descriptor or query

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

## Category

File & Storage Management

## Parameters

- **input**: Primary input parameter. Expected to be a JSON string with fields such as 'file_path', 'drive_id', 'item_id', or 'question'.


## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.storage.onedrive_file_read import OnedriveFileRead

# Initialize the tool
tool = OnedriveFileRead(
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
pytest tools/storage/onedrive_file_read/test_onedrive_file_read.py -v
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../TOOLS_DOCUMENTATION.md)
- [Examples](../../../TOOL_EXAMPLES.md)
- [Category Overview](../README.md)
