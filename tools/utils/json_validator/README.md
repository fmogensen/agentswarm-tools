# json_validator

Validate JSON data against a schema or check for well-formedness.

## Category

Utilities

## Parameters

- **json_data** (str): JSON data as a string or JSON string - **Required**
- **schema** (Dict[str, Any): Optional JSON schema to validate against - Optional
- **strict** (bool): Whether to enforce strict validation - Optional
- **validate_types** (bool): Whether to validate data types - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.utils.json_validator import JsonValidator

# Initialize the tool
tool = JsonValidator(
    json_data="example_value",
    schema="example_value",  # Optional
    strict="example_value"  # Optional
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
python json_validator.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
