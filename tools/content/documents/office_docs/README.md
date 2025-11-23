# office_docs

Generate or modify professional Word documents (.docx) from structured content.

## Category

Content Creation

## Parameters

- **mode** (str): Operation mode: create or modify - Optional
- **content** (str): No description - **Required**
- **template** (str): No description - Optional
- **title** (str): Document title - Optional
- **include_toc** (bool): Include table of contents - Optional
- **font_name** (str): Font family - Optional
- **font_size** (int): Base font size in points - Optional
- **output_format** (str): Output format: docx, pdf, both - Optional
- **existing_file_url** (str): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.content.documents.office_docs import OfficeDocsTool

# Initialize the tool
tool = OfficeDocsTool(
    mode="example_value",  # Optional
    content="example_value",
    template="example_value"  # Optional
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
python office_docs.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
