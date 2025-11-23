# text_to_speech_advanced

Advanced text-to-speech with emotion, voice control, and prosody adjustment.

## Category

Media Generation & Analysis

## Parameters

- **text** (str): Text to convert to speech - **Required**
- **voice_id** (str): Specific voice identifier - Optional
- **gender** (str): Voice gender - Optional
- **age** (str): Voice age range - Optional
- **accent** (str): Voice accent/dialect - Optional
- **emotion** (str): Emotional expression - Optional
- **emotion_intensity** (float): No description - Optional
- **pitch** (float): No description - Optional
- **rate** (float): No description - Optional
- **volume** (float): No description - Optional
- **use_ssml** (bool): Whether text contains SSML markup - Optional
- **output_format** (str): Audio output format - Optional
- **sample_rate** (int): Audio sample rate in Hz - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.media.generation.text_to_speech_advanced import TextToSpeechAdvanced

# Initialize the tool
tool = TextToSpeechAdvanced(
    text="example_value",
    voice_id="example_value",  # Optional
    gender="example_value"  # Optional
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
python text_to_speech_advanced.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
