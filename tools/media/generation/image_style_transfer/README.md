# image_style_transfer

Apply artistic styles to images using neural style transfer.

## Category

Media Generation & Analysis

## Parameters

- **input_image** (str): URL or path to the input image - **Required**
- **style** (str): Style name or type to apply - **Required**
- **style_image_url** (str): Optional URL to custom style reference image - Optional
- **style_strength** (float): No description - Optional
- **preserve_color** (bool): Whether to preserve original image colors - Optional
- **output_size** (str): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.media.generation.image_style_transfer import ImageStyleTransfer

# Initialize the tool
tool = ImageStyleTransfer(
    input_image="example_value",
    style="example_value",
    style_image_url="example_value"  # Optional
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
python image_style_transfer.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
