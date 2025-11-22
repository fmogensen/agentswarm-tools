# google_product_search



## Category

Search & Information Retrieval

## Parameters

- **query**: Product search query
- **num**: Number of results to return
- **page**: Page number for pagination


## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.search.google_product_search import GoogleProductSearch

# Initialize the tool
tool = GoogleProductSearch(
    query="example_value",
    num="example_value"
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
pytest tools/search/google_product_search/test_google_product_search.py -v
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../TOOLS_DOCUMENTATION.md)
- [Examples](../../../TOOL_EXAMPLES.md)
- [Category Overview](../README.md)
