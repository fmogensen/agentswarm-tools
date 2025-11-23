# batch_video_analysis

Analyze multiple videos in batch with custom analysis criteria.

## Category

Media Generation & Analysis

## Parameters

- **video_urls** (str): Comma-separated video URLs or file paths - **Required**
- **analysis_types** (List[str): Types of analysis to perform on each video - Optional
- **custom_instruction** (str): Custom analysis instruction for specialized requirements - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.media.analysis.batch_video_analysis import BatchVideoAnalysis

# Initialize the tool
tool = BatchVideoAnalysis(
    video_urls="example_value",
    analysis_types="example_value",  # Optional
    custom_instruction="example_value"  # Optional
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
python batch_video_analysis.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
