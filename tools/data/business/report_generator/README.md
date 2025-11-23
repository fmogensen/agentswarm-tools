# report_generator

Generate business reports from structured data with various formats.

## Category

Data & Search

## Parameters

- **data** (Dict[str, Any): Data to include in the report - **Required**
- **report_type** (str): Type of report: summary, detailed, executive, analytics - **Required**
- **title** (str): Report title - **Required**
- **sections** (List[str): No description - Optional
- **format** (str): Output format: json, markdown, html - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.data.business.report_generator import ReportGenerator

# Initialize the tool
tool = ReportGenerator(
    data="example_value",
    report_type="example_value",
    title="example_value"
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
python report_generator.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
