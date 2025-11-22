# Video Clipper Tool - Quick Start Guide

## Installation

```bash
# Install FFmpeg
brew install ffmpeg  # macOS
# or
sudo apt-get install ffmpeg  # Ubuntu

# Set API key
export OPENAI_API_KEY="sk-your-key-here"
```

## Basic Usage

```python
from tools.media_processing.video_clipper import VideoClipperTool

# Create 3 clips for TikTok
tool = VideoClipperTool(
    video_url="https://example.com/video.mp4",
    clip_duration=30,
    num_clips=3,
    detection_mode="highlights",
    aspect_ratio="9:16",
    add_captions=True,
    optimize_for="tiktok"
)

result = tool.run()
print(f"Created {len(result['clips'])} clips!")
```

## Common Presets

### TikTok
```python
VideoClipperTool(
    video_url="https://example.com/video.mp4",
    aspect_ratio="9:16",
    clip_duration=30,
    optimize_for="tiktok"
)
```

### Instagram Reels
```python
VideoClipperTool(
    video_url="https://example.com/video.mp4",
    aspect_ratio="9:16",
    clip_duration=30,
    optimize_for="instagram"
)
```

### YouTube Shorts
```python
VideoClipperTool(
    video_url="https://example.com/video.mp4",
    aspect_ratio="9:16",
    clip_duration=60,
    optimize_for="youtube_shorts"
)
```

## Detection Modes

- `auto` - Balanced (default)
- `action` - Sports, gaming
- `dialogue` - Podcasts, interviews
- `highlights` - Peak moments
- `topics` - Educational content

## Aspect Ratios

- `16:9` - Landscape (YouTube)
- `9:16` - Vertical (TikTok, Instagram Reels)
- `1:1` - Square (Instagram feed)
- `4:5` - Portrait (Instagram Stories)

## Output Format

```python
{
  "success": True,
  "clips": [
    {
      "clip_id": "clip_1_abc12345",
      "url": "https://...",
      "start_time": "00:02:30",
      "end_time": "00:03:00",
      "duration": 30,
      "score": 0.95,
      "highlight_type": "peak_moment"
    }
  ],
  "highlights_detected": 15,
  "total_duration": "90s",
  "aspect_ratio": "9:16"
}
```

## Testing

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = VideoClipperTool(video_url="https://example.com/test.mp4")
result = tool.run()  # Returns mock data
```

## Error Handling

```python
try:
    result = tool.run()
except ValidationError as e:
    print(f"Invalid parameters: {e.message}")
except AuthenticationError as e:
    print("Set OPENAI_API_KEY environment variable")
except MediaError as e:
    print(f"Processing failed: {e.message}")
```

## Full Documentation

- `README.md` - Complete reference
- `EXAMPLES.md` - 20 usage examples
- `test_video_clipper.py` - Test suite
