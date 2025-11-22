# Podcast Generator Tool

Generate professional podcast episodes with multiple speakers, background music, and audio mixing.

## Overview

The Podcast Generator tool creates complete podcast episodes with:
- **Multiple speakers** (1-4) with distinct voices and personalities
- **Background music** integration with customizable styles
- **Intro and outro** segments
- **Script generation** or custom script support
- **Professional audio mixing** with OpenAI TTS
- **Voice consistency** across segments

## Features

### Multi-Speaker Support
- Support for 1-4 speakers per episode
- Unique voice assignment for each speaker
- Personality-based voice selection
- Realistic conversation flow

### Audio Production
- High-quality TTS using OpenAI's latest models
- Background music mixing
- Automatic audio normalization
- Support for MP3 and WAV formats

### Flexible Scripting
- Auto-generate scripts from topics using AI
- Custom script support with speaker assignments
- Intelligent script parsing and segmentation

### Professional Polish
- Optional intro segments (15 seconds)
- Optional outro segments (10 seconds)
- Background music in multiple styles
- Voice consistency across all segments

## Installation

```bash
# Install required dependencies
pip install openai pydub requests

# Set environment variable
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Two-Speaker Podcast

```python
from tools.media_generation.podcast_generator import PodcastGenerator

# Create a basic podcast
tool = PodcastGenerator(
    topic="The Future of AI",
    duration_minutes=10,
    num_speakers=2,
    speaker_personalities=["enthusiastic tech host", "AI researcher expert"]
)

result = tool.run()
print(f"Podcast URL: {result['podcast_url']}")
print(f"Duration: {result['duration_seconds']} seconds")
```

### Solo Podcast (Meditation/Narrative)

```python
tool = PodcastGenerator(
    topic="Guided Meditation for Beginners",
    duration_minutes=5,
    num_speakers=1,
    speaker_personalities=["calm meditation guide"],
    background_music=True,
    music_style="calm",
    add_intro=False,
    add_outro=False
)

result = tool.run()
```

### Panel Discussion (4 Speakers)

```python
tool = PodcastGenerator(
    topic="Startup Funding Strategies",
    duration_minutes=30,
    num_speakers=4,
    speaker_personalities=[
        "professional moderator",
        "startup founder",
        "venture capitalist",
        "business advisor"
    ],
    background_music=True,
    music_style="corporate"
)

result = tool.run()
```

### Custom Script

```python
custom_script = """
Speaker 1: Welcome to Tech Talk Weekly!
Speaker 2: Thanks for having me on the show.
Speaker 1: Let's dive into today's topic about AI ethics.
Speaker 2: This is such an important discussion to have.
"""

tool = PodcastGenerator(
    topic="AI Ethics Discussion",
    duration_minutes=15,
    num_speakers=2,
    speaker_personalities=["tech host", "ethics expert"],
    script_content=custom_script
)

result = tool.run()
```

## Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `topic` | str | Main topic/subject of the podcast (1-500 chars) |
| `speaker_personalities` | List[str] | Personality descriptions for each speaker |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration_minutes` | int | 10 | Target duration in minutes (1-60) |
| `num_speakers` | int | 2 | Number of speakers (1-4) |
| `script_content` | str | None | Optional pre-written script |
| `background_music` | bool | True | Include background music |
| `music_style` | str | "upbeat" | Music style: upbeat, calm, corporate, none |
| `output_format` | str | "mp3" | Output format: mp3 or wav |
| `add_intro` | bool | True | Add 15-second intro segment |
| `add_outro` | bool | True | Add 10-second outro segment |
| `voice_consistency` | bool | True | Ensure consistent voice characteristics |

## Return Value

Returns a dictionary with:

```python
{
    "success": True,
    "podcast_url": "https://podcast-storage.example.com/abc123.mp3",
    "duration_seconds": 625,
    "speakers_used": [
        {
            "speaker_id": "speaker_1",
            "personality": "enthusiastic tech host",
            "voice_model": "alloy",
            "voice_settings": {
                "model": "tts-1-hd",
                "voice": "alloy",
                "speed": 1.0
            }
        },
        # ... more speakers
    ],
    "transcript": "Full transcript text...",
    "metadata": {
        "podcast_id": "abc123",
        "topic": "The Future of AI",
        "format": "mp3",
        "file_size_mb": 8.5,
        "sample_rate": "44100 Hz",
        "bitrate": "128 kbps",
        "channels": "stereo",
        "music_included": True,
        "music_style": "upbeat",
        "has_intro": True,
        "has_outro": True,
        "generated_at": "2025-11-22T10:30:00"
    }
}
```

## Voice Models

The tool uses OpenAI's TTS voices, automatically assigned based on speaker personalities:

- **alloy** - Neutral, balanced voice
- **echo** - Clear, male-presenting voice
- **fable** - Warm, expressive voice
- **onyx** - Deep, authoritative voice
- **nova** - Bright, female-presenting voice
- **shimmer** - Soft, gentle voice

## Music Styles

### Upbeat
High-energy background music suitable for:
- Tech podcasts
- Motivational content
- Business updates

### Calm
Relaxing background music suitable for:
- Meditation guides
- Educational content
- Storytelling

### Corporate
Professional background music suitable for:
- Business podcasts
- Industry discussions
- Training materials

### None
No background music (voice only)

## Script Format

When providing a custom script, use this format:

```
Speaker 1: First speaker's dialogue here.
Speaker 2: Second speaker's response.
Speaker 1: Continuing the conversation.
```

The tool will automatically:
- Parse speaker assignments
- Estimate segment durations
- Assign appropriate voices
- Generate audio for each segment

## Examples

### Example 1: Educational Podcast

```python
tool = PodcastGenerator(
    topic="Introduction to Python Programming",
    duration_minutes=20,
    num_speakers=2,
    speaker_personalities=["friendly instructor", "curious beginner"],
    background_music=True,
    music_style="calm"
)

result = tool.run()
```

### Example 2: News Podcast

```python
tool = PodcastGenerator(
    topic="Weekly Tech News Roundup",
    duration_minutes=15,
    num_speakers=3,
    speaker_personalities=[
        "news anchor",
        "tech reporter",
        "industry analyst"
    ],
    background_music=True,
    music_style="corporate",
    output_format="mp3"
)

result = tool.run()
```

### Example 3: Interview Podcast

```python
custom_interview = """
Speaker 1: Today we're joined by an amazing guest.
Speaker 2: Thanks for having me!
Speaker 1: Tell us about your journey into entrepreneurship.
Speaker 2: It all started when I was in college...
"""

tool = PodcastGenerator(
    topic="Founder Interview Series",
    duration_minutes=25,
    num_speakers=2,
    speaker_personalities=["experienced interviewer", "successful entrepreneur"],
    script_content=custom_interview,
    background_music=True,
    music_style="upbeat"
)

result = tool.run()
```

## Testing

### Mock Mode

For testing without API calls:

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = PodcastGenerator(
    topic="Test Podcast",
    num_speakers=2,
    speaker_personalities=["host", "guest"]
)

result = tool.run()
# Returns realistic mock data without API costs
```

### Run Tests

```bash
# Run all tests
pytest tools/media_generation/podcast_generator/test_podcast_generator.py

# Run specific test class
pytest tools/media_generation/podcast_generator/test_podcast_generator.py::TestPodcastGeneratorMockMode

# Run with verbose output
pytest tools/media_generation/podcast_generator/test_podcast_generator.py -v
```

## Error Handling

The tool provides detailed error messages for common issues:

### Validation Errors

```python
# Mismatched speaker count
try:
    tool = PodcastGenerator(
        topic="Test",
        num_speakers=3,
        speaker_personalities=["host", "guest"]  # Only 2
    )
except ValueError as e:
    print(f"Error: {e}")
    # Error: speaker_personalities must contain exactly 3 entries
```

### Configuration Errors

```python
# Missing API key in production mode
os.environ["USE_MOCK_APIS"] = "false"
os.environ.pop("OPENAI_API_KEY", None)

tool = PodcastGenerator(
    topic="Test",
    num_speakers=1,
    speaker_personalities=["host"]
)

result = tool.run()
# Returns: {"success": False, "error": {"code": "CONFIG_ERROR", ...}}
```

## Best Practices

### 1. Speaker Personalities

Be specific with personality descriptions:

```python
# Good
speaker_personalities=["enthusiastic tech host", "cautious security expert"]

# Less effective
speaker_personalities=["host", "guest"]
```

### 2. Duration Planning

Account for intro/outro when planning duration:

```python
# For a 10-minute podcast with intro/outro
duration_minutes=10  # Actual duration will be ~10:25
# (10 minutes content + 15s intro + 10s outro)
```

### 3. Script Length

When providing custom scripts, aim for natural conversation:

```python
# Good: Natural dialogue
script = """
Speaker 1: What's your take on the recent developments?
Speaker 2: I think it's fascinating. The technology has come so far.
Speaker 1: Absolutely. What excites you most?
"""

# Avoid: Long monologues
script = """
Speaker 1: [500 words of continuous speech without breaks]
"""
```

### 4. Music Selection

Match music style to content:

- **Tech/Business**: upbeat or corporate
- **Education/Meditation**: calm
- **Interviews**: upbeat or corporate
- **Narrative/Storytelling**: calm

## Performance

### Processing Time

Approximate processing times (varies by duration and speakers):

- 5-minute podcast (2 speakers): ~30-60 seconds
- 10-minute podcast (2 speakers): ~60-120 seconds
- 20-minute podcast (4 speakers): ~120-240 seconds

### File Sizes

Approximate file sizes (MP3 @ 128 kbps):

- 5-minute podcast: ~5 MB
- 10-minute podcast: ~10 MB
- 20-minute podcast: ~20 MB
- 30-minute podcast: ~30 MB

WAV files are approximately 10x larger than MP3.

## Limitations

1. **Maximum speakers**: 4 speakers per podcast
2. **Maximum duration**: 60 minutes per episode
3. **Topic length**: 500 characters maximum
4. **Script length**: 50,000 characters maximum
5. **Personality description**: 200 characters maximum per speaker

## Troubleshooting

### Issue: "Missing OPENAI_API_KEY"

**Solution**: Set the environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

### Issue: Mismatched speaker count error

**Solution**: Ensure `speaker_personalities` list length matches `num_speakers`:
```python
num_speakers=2
speaker_personalities=["host", "guest"]  # Must have exactly 2 entries
```

### Issue: Script not being used

**Solution**: Verify script format with "Speaker X:" prefix:
```python
script_content="Speaker 1: Hello\nSpeaker 2: Hi there"
```

## Technical Details

### Architecture

1. **Script Generation**: Uses OpenAI GPT API to generate conversational scripts
2. **Voice Synthesis**: Uses OpenAI TTS API for each speaker segment
3. **Audio Mixing**: Combines segments with pydub library
4. **Music Integration**: Overlays background music at appropriate levels
5. **Export**: Finalizes and exports to requested format

### Dependencies

- `openai`: OpenAI API client
- `pydub`: Audio manipulation and mixing
- `requests`: HTTP requests for API calls
- `pydantic`: Data validation

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test examples in `test_podcast_generator.py`
3. Enable mock mode to test without API costs
4. Consult OpenAI TTS documentation for voice details

## License

Part of the AgentSwarm Tools Framework.
