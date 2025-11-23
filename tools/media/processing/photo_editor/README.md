# photo_editor

Perform advanced photo editing operations on existing images.

## Category

Media Generation & Analysis

## Parameters

- **image_url** (str): URL to source image - **Required**
- **operations** (List[Dict[str, Any): List of editing operations - **Required**
- **output_format** (str): Output format: png, jpg, webp - Optional
- **quality** (int): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.media.processing.photo_editor import PhotoEditorTool

# Initialize the tool
tool = PhotoEditorTool(
    image_url="example_value",
    operations="example_value",
    output_format="example_value"  # Optional
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
python photo_editor.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
