# onedrive_search



## Category

File & Storage Management

## Parameters

- **query**: Search query string
- **max_results**: Maximum number of results to return


## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.storage.onedrive_search import OnedriveSearch

# Initialize the tool
tool = OnedriveSearch(
    query="example_value",
    max_results="example_value"
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
pytest tools/storage/onedrive_search/test_onedrive_search.py -v
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../TOOLS_DOCUMENTATION.md)
- [Examples](../../../TOOL_EXAMPLES.md)
- [Category Overview](../README.md)
