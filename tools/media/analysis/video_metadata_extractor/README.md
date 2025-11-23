# video_metadata_extractor

Extract comprehensive metadata from video files.

## Category

Media Generation & Analysis

## Parameters

- **video_path** (str): Path or URL to the video file - **Required**
- **extract_thumbnails** (bool): Extract thumbnail images at key frames - Optional
- **include_streams** (bool): Include detailed stream information - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.media.analysis.video_metadata_extractor import VideoMetadataExtractor

# Initialize the tool
tool = VideoMetadataExtractor(
    video_path="example_value",
    extract_thumbnails="example_value",  # Optional
    include_streams="example_value"  # Optional
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
python video_metadata_extractor.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
