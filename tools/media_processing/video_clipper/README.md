# Video Clipper Tool

Automatically extract engaging clips from long-form videos using AI-powered scene detection.

## Overview

The VideoClipperTool analyzes videos to identify the most engaging segments based on various detection modes (action, dialogue, highlights, topics) and creates optimized short clips suitable for social media platforms like Instagram, TikTok, and YouTube Shorts.

## Features

- **AI-Powered Scene Detection**: Uses GPT-4 Vision for intelligent scene analysis
- **Speech Transcription**: OpenAI Whisper for accurate caption generation
- **Multiple Detection Modes**: Action, dialogue, highlights, topics, or auto-balanced
- **Platform Optimization**: Presets for Instagram, TikTok, YouTube Shorts
- **Flexible Aspect Ratios**: 16:9, 9:16, 1:1, 4:5 support
- **Auto Captions**: Burned-in subtitles from transcription
- **Smooth Transitions**: Optional fade transitions between scenes
- **FFmpeg Processing**: Professional-grade video processing

## Requirements

### System Dependencies
- FFmpeg (required for video processing)
- Python 3.9+

### Python Dependencies
- pydantic
- requests
- agency-swarm (BaseTool)

### API Keys
- `OPENAI_API_KEY`: For Whisper transcription and GPT-4 Vision scene analysis

## Installation

```bash
# Install FFmpeg (macOS)
brew install ffmpeg

# Install FFmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Install Python dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-openai-api-key"
```

## Usage

### Basic Example

```python
from tools.media_processing.video_clipper import VideoClipperTool

# Create tool instance
tool = VideoClipperTool(
    video_url="https://example.com/long_video.mp4",
    clip_duration=30,
    num_clips=5,
    detection_mode="highlights",
    aspect_ratio="9:16",
    add_captions=True,
    optimize_for="tiktok"
)

# Execute
result = tool.run()

# Access results
for clip in result["clips"]:
    print(f"Clip: {clip['url']}")
    print(f"Score: {clip['score']}")
    print(f"Time: {clip['start_time']} - {clip['end_time']}")
    print(f"Type: {clip['highlight_type']}")
```

### Detection Modes

#### Auto (Balanced)
```python
tool = VideoClipperTool(
    video_url="https://example.com/video.mp4",
    detection_mode="auto",  # Balanced detection
    num_clips=3
)
```

#### Action Detection
Best for sports, gaming, fast-paced content:
```python
tool = VideoClipperTool(
    video_url="https://example.com/sports.mp4",
    detection_mode="action",  # Motion-based detection
    aspect_ratio="16:9"
)
```

#### Dialogue Detection
Best for podcasts, interviews, talk shows:
```python
tool = VideoClipperTool(
    video_url="https://example.com/podcast.mp4",
    detection_mode="dialogue",  # Speech-based detection
    add_captions=True
)
```

#### Highlights Detection
Best for peak moments, emotional content:
```python
tool = VideoClipperTool(
    video_url="https://example.com/event.mp4",
    detection_mode="highlights",  # Peak moments
    clip_duration=15
)
```

#### Topics Detection
Best for educational content, presentations:
```python
tool = VideoClipperTool(
    video_url="https://example.com/lecture.mp4",
    detection_mode="topics",  # Theme-based detection
    clip_duration=60
)
```

### Platform Optimization

#### TikTok
```python
tool = VideoClipperTool(
    video_url="https://example.com/video.mp4",
    optimize_for="tiktok",
    aspect_ratio="9:16",
    clip_duration=30,  # Max 60s for TikTok
    add_captions=True,
    add_transitions=True
)
```

#### Instagram Reels
```python
tool = VideoClipperTool(
    video_url="https://example.com/video.mp4",
    optimize_for="instagram",
    aspect_ratio="9:16",
    clip_duration=30,
    output_format="mp4"
)
```

#### YouTube Shorts
```python
tool = VideoClipperTool(
    video_url="https://example.com/video.mp4",
    optimize_for="youtube_shorts",
    aspect_ratio="9:16",
    clip_duration=60,
    add_captions=True
)
```

#### General (No Platform Restrictions)
```python
tool = VideoClipperTool(
    video_url="https://example.com/video.mp4",
    optimize_for="general",
    clip_duration=120,  # Up to 300s
    aspect_ratio="16:9"
)
```

### Aspect Ratios

```python
# Landscape (YouTube, traditional)
aspect_ratio="16:9"  # 1920x1080

# Vertical (TikTok, Instagram Reels)
aspect_ratio="9:16"  # 1080x1920

# Square (Instagram feed)
aspect_ratio="1:1"   # 1080x1080

# Portrait (Instagram Stories)
aspect_ratio="4:5"   # 1080x1350
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_url` | str | Required | URL to source video (http/https) |
| `clip_duration` | int | 30 | Duration of each clip in seconds (10-300) |
| `num_clips` | int | 3 | Number of clips to extract (1-10) |
| `detection_mode` | str | "auto" | Algorithm for selecting clips |
| `aspect_ratio` | str | "9:16" | Output aspect ratio |
| `add_captions` | bool | True | Add auto-generated captions |
| `add_transitions` | bool | True | Add transitions between scenes |
| `optimize_for` | str | "general" | Platform optimization preset |
| `include_branding` | bool | False | Include branding watermark |
| `output_format` | str | "mp4" | Output video format |

### Detection Modes
- `auto`: Balanced detection (motion + speech + emotion)
- `action`: Motion-based detection (sports, gaming)
- `dialogue`: Speech-based detection (podcasts, interviews)
- `highlights`: Peak moments (events, climaxes)
- `topics`: Theme-based detection (education, presentations)

### Platform Settings

| Platform | Max Duration | Bitrate | FPS | Audio Bitrate |
|----------|-------------|---------|-----|---------------|
| TikTok | 60s | 2500k | 30 | 128k |
| Instagram | 60s | 3000k | 30 | 128k |
| YouTube Shorts | 60s | 4000k | 30 | 192k |
| General | 300s | 3500k | 30 | 192k |

## Return Value

```python
{
    "success": True,
    "clips": [
        {
            "clip_id": "clip_1_abc12345",
            "url": "https://storage.example.com/clips/clip_abc12345.mp4",
            "start_time": "00:02:30",
            "end_time": "00:03:00",
            "duration": 30,
            "score": 0.95,
            "highlight_type": "peak_moment",
            "caption_preview": "This is the most important point...",
            "resolution": "1080x1920",
            "format": "mp4",
            "file_size": "2.3 MB"
        },
        # ... more clips
    ],
    "highlights_detected": 15,
    "total_duration": "90s",
    "aspect_ratio": "9:16",
    "metadata": {
        "detection_mode": "highlights",
        "transcription_available": True,
        "platform_optimized": "tiktok",
        "source_duration": "600s",
        "source_resolution": "1920x1080",
        "source_fps": 30
    }
}
```

## How It Works

1. **Download Video**: Fetch source video from URL
2. **Extract Audio**: Extract audio track for transcription
3. **Transcribe**: Use OpenAI Whisper for speech-to-text
4. **Scene Analysis**:
   - Extract frames at regular intervals
   - Analyze with GPT-4 Vision
   - Score scenes based on detection mode
5. **Clip Selection**:
   - Rank scenes by score
   - Ensure no overlap between clips
   - Select top N clips
6. **Video Processing**:
   - Extract clip segments with FFmpeg
   - Resize/crop to aspect ratio
   - Apply transitions
   - Burn in captions
   - Optimize for platform
7. **Output**: Return clip URLs and metadata

## Testing

### Mock Mode

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = VideoClipperTool(
    video_url="https://example.com/video.mp4",
    clip_duration=30,
    num_clips=3
)
result = tool.run()
# Returns mock data without processing
```

### Run Tests

```bash
# Run all tests
pytest tools/media_processing/video_clipper/test_video_clipper.py -v

# Run specific test
pytest tools/media_processing/video_clipper/test_video_clipper.py::TestVideoClipperTool::test_basic_clipping -v

# Run with coverage
pytest tools/media_processing/video_clipper/test_video_clipper.py --cov=tools.media_processing.video_clipper
```

### Run Built-in Tests

```bash
python tools/media_processing/video_clipper/video_clipper.py
```

## Error Handling

The tool provides comprehensive error handling:

```python
from shared.errors import ValidationError, MediaError, AuthenticationError

try:
    tool = VideoClipperTool(
        video_url="https://example.com/video.mp4",
        clip_duration=30,
        num_clips=3
    )
    result = tool.run()
except ValidationError as e:
    # Invalid parameters
    print(f"Validation error: {e.message}")
except AuthenticationError as e:
    # Missing API key
    print(f"Auth error: {e.message}")
except MediaError as e:
    # FFmpeg or processing error
    print(f"Media error: {e.message}")
```

## Performance

- **Processing Time**: ~2-5 seconds per minute of source video
- **Memory Usage**: ~500MB-2GB depending on video resolution
- **Storage**: Clips are temporarily stored, then uploaded to persistent storage

## Best Practices

1. **Choose Detection Mode**: Match mode to content type
2. **Set Appropriate Duration**: Consider platform limits
3. **Use Captions**: Improves engagement for vertical videos
4. **Test Aspect Ratios**: Verify clips look good on target platform
5. **Monitor API Usage**: Whisper and GPT-4 Vision incur costs
6. **Optimize Quality**: Higher bitrates for important content

## Limitations

- Requires internet connection for video download
- OpenAI API costs for transcription and scene analysis
- FFmpeg must be installed on system
- Processing time scales with video length
- Generated URLs may expire (use persistent storage)

## Troubleshooting

### FFmpeg Not Found
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu
```

### Missing API Key
```bash
export OPENAI_API_KEY="sk-..."
```

### Video Download Fails
- Check URL is accessible
- Verify URL uses http/https protocol
- Ensure adequate disk space

### Poor Clip Selection
- Try different detection mode
- Adjust clip duration
- Increase num_clips to see more options

## Contributing

Follow Agency Swarm tool development standards:
1. Inherit from BaseTool
2. Implement all 5 required methods
3. Use environment variables for secrets
4. Include comprehensive test block
5. Add type hints and docstrings

## License

Part of the AgentSwarm Tools Framework.
