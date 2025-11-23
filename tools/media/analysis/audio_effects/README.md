# audio_effects

Apply various audio effects to audio files.

## Category

Media Generation & Analysis

## Parameters

- **input_path** (str): Path to input audio file - **Required**
- **effects** (List[Dict[str, Any): List of effect configurations to apply - **Required**
- **output_path** (str): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.media.analysis.audio_effects import AudioEffects

# Initialize the tool
tool = AudioEffects(
    input_path="example_value",
    effects="example_value",
    output_path="example_value"  # Optional
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
python audio_effects.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
