# office_sheets

Generate or modify Excel spreadsheets (.xlsx) from structured data.

## Category

Content Creation

## Parameters

- **mode** (str): Operation mode: create or modify - Optional
- **data** (List[List[Any): Data as list of rows - **Required**
- **headers** (List[str): Column headers - Optional
- **formulas** (Dict[str, str): No description - Optional
- **charts** (List[Dict[str, Any): Chart definitions - Optional
- **formatting** (Dict[str, Any): Cell formatting rules - Optional
- **worksheets** (Dict[str, List[List[Any): No description - Optional
- **output_format** (str): Output format: xlsx, csv, both - Optional
- **existing_file_url** (str): No description - Optional
- **worksheet_name** (str): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.content.documents.office_sheets import OfficeSheetsTool

# Initialize the tool
tool = OfficeSheetsTool(
    mode="example_value",  # Optional
    data="example_value",
    headers="example_value"  # Optional
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
python office_sheets.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
