# text_formatter

Format and clean text data with various transformations.

## Category

Utilities

## Parameters

- **text** (str): Text to format - **Required**
- **operations** (List[str): List of operations: trim, lowercase, uppercase, title, remove_whitespace, remove_punctuation, normalize_spaces, remove_numbers, remove_special_chars - **Required**
- **custom_replacements** (Dict[str, str): Optional custom find/replace pairs - Optional
- **strip_html** (bool): Whether to strip HTML tags - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.utils.text_formatter import TextFormatter

# Initialize the tool
tool = TextFormatter(
    text="example_value",
    operations="example_value",
    custom_replacements="example_value"  # Optional
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
python text_formatter.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
