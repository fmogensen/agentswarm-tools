# batch_processor

Process multiple items in batch with various operations.

## Category

Utilities

## Parameters

- **items** (List[Any): List of items to process - **Required**
- **operation** (str): Operation to perform: transform, filter, validate, aggregate, count - **Required**
- **operation_config** (Dict[str, Any): No description - Optional
- **batch_size** (int): Number of items to process per batch - Optional
- **continue_on_error** (bool): Whether to continue processing if an item fails - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.utils.batch_processor import BatchProcessor

# Initialize the tool
tool = BatchProcessor(
    items="example_value",
    operation="example_value",
    operation_config="example_value"  # Optional
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
python batch_processor.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
