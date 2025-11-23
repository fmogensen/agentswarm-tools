# meeting_notes_agent

Transcribe meeting audio and generate structured notes with action items.

## Category

Communication & Productivity

## Parameters

- **audio_url** (str): URL to meeting audio file - **Required**
- **export_formats** (List[str): Export formats: notion, pdf, markdown - Optional
- **include_transcript** (bool): Include full transcript - Optional
- **extract_action_items** (bool): Extract action items - Optional
- **identify_speakers** (bool): Identify different speakers - Optional
- **meeting_title** (str): Meeting title - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.meeting_notes import MeetingNotesAgent

# Initialize the tool
tool = MeetingNotesAgent(
    audio_url="example_value",
    export_formats="example_value",  # Optional
    include_transcript="example_value"  # Optional
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
python meeting_notes_agent.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
