# Video Editor Tool

Advanced video editing tool using FFmpeg for comprehensive video manipulation operations.

## Overview

The VideoEditorTool provides powerful video editing capabilities including trimming, merging, resizing, rotating, speed adjustment, audio manipulation, subtitle addition, and transitions. It uses FFmpeg under the hood for professional-quality video processing.

## Features

- **Trim**: Cut videos to specific time ranges
- **Merge**: Combine multiple videos into one
- **Resize**: Change video dimensions
- **Rotate**: Rotate videos by 90, 180, or 270 degrees
- **Speed**: Adjust playback speed (slow motion or fast forward)
- **Add Audio**: Replace or add audio tracks
- **Add Subtitles**: Embed subtitle files
- **Transitions**: Add transition effects between clips
- **Multiple Formats**: Output to mp4, avi, mov, or webm

## Installation

### Prerequisites

FFmpeg must be installed on your system:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg
```

### Python Dependencies

```bash
pip install requests pydantic
```

## Usage

### Basic Example

```python
from tools.media_processing.video_editor import VideoEditorTool

# Trim a video
tool = VideoEditorTool(
    video_url="https://example.com/video.mp4",
    operations=[
        {"type": "trim", "start": "00:00:10", "end": "00:00:30"}
    ],
    output_format="mp4"
)
result = tool.run()
print(result["result"]["edited_video_url"])
```

### Complex Workflow

```python
# Multi-step editing workflow
tool = VideoEditorTool(
    video_url="https://example.com/video.mp4",
    operations=[
        # Trim to 20 seconds
        {"type": "trim", "start": "00:00:05", "end": "00:00:25"},
        # Resize to 1080p
        {"type": "resize", "width": 1920, "height": 1080},
        # Speed up 1.5x
        {"type": "speed", "factor": 1.5},
        # Rotate 90 degrees
        {"type": "rotate", "degrees": 90}
    ],
    output_format="mp4"
)
result = tool.run()
```

## Operations Reference

### 1. Trim

Cut video to specific time range.

```python
{
    "type": "trim",
    "start": "00:00:10",  # HH:MM:SS or numeric seconds
    "end": "00:00:30"     # HH:MM:SS or numeric seconds
}
```

**Time Formats:**
- `"00:01:30"` - One minute, thirty seconds
- `"90"` - 90 seconds
- `"90.5"` - 90.5 seconds

### 2. Merge

Combine multiple videos.

```python
{
    "type": "merge",
    "videos": [
        "https://example.com/video1.mp4",
        "https://example.com/video2.mp4",
        "https://example.com/video3.mp4"
    ]
}
```

**Note:** When using merge, `video_url` parameter can be omitted.

### 3. Resize

Change video dimensions.

```python
{
    "type": "resize",
    "width": 1920,
    "height": 1080
}
```

**Common Resolutions:**
- 4K: `3840 x 2160`
- 1080p: `1920 x 1080`
- 720p: `1280 x 720`
- 480p: `854 x 480`

### 4. Rotate

Rotate video by degrees.

```python
{
    "type": "rotate",
    "degrees": 90  # 90, 180, 270, or negative equivalents
}
```

**Valid Values:**
- `0`: No rotation
- `90` or `-270`: Rotate 90° clockwise
- `180` or `-180`: Rotate 180°
- `270` or `-90`: Rotate 270° clockwise (90° counter-clockwise)

### 5. Speed

Adjust playback speed.

```python
{
    "type": "speed",
    "factor": 2.0  # Positive number
}
```

**Examples:**
- `0.5`: Half speed (slow motion)
- `1.0`: Normal speed
- `2.0`: Double speed
- `4.0`: 4x speed

### 6. Add Audio

Add or replace audio track.

```python
{
    "type": "add_audio",
    "audio_url": "https://example.com/audio.mp3"
}
```

**Supported Audio Formats:**
- MP3
- WAV
- AAC
- M4A

### 7. Add Subtitles

Embed subtitle file.

```python
{
    "type": "add_subtitles",
    "subtitle_url": "https://example.com/subtitles.srt"
}
```

**Supported Subtitle Formats:**
- SRT (SubRip)
- VTT (WebVTT)
- ASS/SSA

### 8. Transition

Add transition effects (requires merge operation).

```python
{
    "type": "transition",
    "effect": "fade"  # fade, wipeleft, wiperight, wipeup, wipedown, dissolve
}
```

**Available Effects:**
- `fade`: Fade in/out
- `wipeleft`: Wipe left
- `wiperight`: Wipe right
- `wipeup`: Wipe up
- `wipedown`: Wipe down
- `dissolve`: Cross dissolve

## Parameters

### VideoEditorTool

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video_url` | str | Conditional | None | URL to source video (required except for merge-only) |
| `operations` | List[Dict] | Yes | - | List of editing operations to apply |
| `output_format` | str | No | "mp4" | Output format: mp4, avi, mov, webm |

## Return Value

```python
{
    "success": True,
    "result": {
        "edited_video_url": "file:///path/to/edited.mp4",
        "format": "mp4",
        "duration": "00:00:20",
        "resolution": "1920x1080",
        "file_size": "5.2 MB",
        "operations_applied": 4,
        "fps": 30
    },
    "metadata": {
        "tool_name": "video_editor"
    }
}
```

## Examples

### Example 1: Create Highlight Reel

```python
# Extract best moments and create highlight reel
tool = VideoEditorTool(
    operations=[
        {
            "type": "merge",
            "videos": [
                "https://example.com/clip1.mp4",  # 0-10s
                "https://example.com/clip2.mp4",  # 10-20s
                "https://example.com/clip3.mp4"   # 20-30s
            ]
        },
        {"type": "transition", "effect": "fade"},
        {"type": "resize", "width": 1920, "height": 1080},
        {"type": "add_audio", "audio_url": "https://example.com/music.mp3"}
    ],
    output_format="mp4"
)
```

### Example 2: Social Media Clip

```python
# Create vertical video for social media
tool = VideoEditorTool(
    video_url="https://example.com/landscape.mp4",
    operations=[
        {"type": "trim", "start": "00:00:15", "end": "00:00:45"},
        {"type": "resize", "width": 1080, "height": 1920},  # Vertical
        {"type": "speed", "factor": 1.2},  # Slightly faster
    ],
    output_format="mp4"
)
```

### Example 3: Tutorial Video

```python
# Process tutorial with subtitles
tool = VideoEditorTool(
    video_url="https://example.com/tutorial.mp4",
    operations=[
        {"type": "trim", "start": "00:00:00", "end": "00:05:00"},
        {"type": "resize", "width": 1280, "height": 720},
        {"type": "add_subtitles", "subtitle_url": "https://example.com/subs.srt"},
        {"type": "speed", "factor": 1.1}  # Slightly faster
    ],
    output_format="mp4"
)
```

### Example 4: Time-lapse

```python
# Create time-lapse from regular video
tool = VideoEditorTool(
    video_url="https://example.com/long_video.mp4",
    operations=[
        {"type": "trim", "start": "00:00:00", "end": "01:00:00"},
        {"type": "speed", "factor": 10.0},  # 10x speed
        {"type": "resize", "width": 1920, "height": 1080}
    ],
    output_format="mp4"
)
```

## Error Handling

### Common Errors

```python
# ValidationError: Invalid operation
try:
    tool = VideoEditorTool(
        video_url="https://example.com/video.mp4",
        operations=[{"type": "invalid_op"}]
    )
    result = tool.run()
except Exception as e:
    print(f"Error: {e}")
    # Error: Operation type 'invalid_op' not supported
```

### Error Types

- **ValidationError**: Invalid parameters or operation configuration
- **MediaError**: FFmpeg processing error or video corruption
- **APIError**: Failed to download video/audio/subtitle files

## Testing

### Run Tests

```bash
# Run all tests
pytest tools/media_processing/video_editor/test_video_editor.py -v

# Run specific test
pytest tools/media_processing/video_editor/test_video_editor.py::TestVideoEditorTool::test_trim_operation -v

# Run with mock mode
USE_MOCK_APIS=true python tools/media_processing/video_editor/video_editor.py
```

### Mock Mode

For testing without FFmpeg or actual video files:

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = VideoEditorTool(
    video_url="https://example.com/video.mp4",
    operations=[{"type": "trim", "start": "0", "end": "10"}]
)
result = tool.run()
# Returns mock data without processing
```

## Performance Considerations

### Processing Time

Operation processing times vary based on:
- Video length and resolution
- Number of operations
- Hardware capabilities
- Output format

**Estimates:**
- Trim (copy mode): Very fast (seconds)
- Resize: Moderate (1-2x video length)
- Speed: Moderate (1-2x video length)
- Add Audio/Subtitles: Fast-Moderate
- Merge: Fast if same codec, moderate otherwise

### Memory Usage

- Large videos (>1GB) may require significant RAM
- Operations are applied sequentially to manage memory
- Temporary files are created during processing

### Optimization Tips

1. **Use trim first**: Reduce video length before other operations
2. **Minimize transcoding**: Use compatible formats when possible
3. **Batch operations**: Apply multiple operations in one tool call
4. **Choose appropriate resolution**: Don't upscale unnecessarily

## Troubleshooting

### FFmpeg Not Found

```
Error: FFmpeg not found. Please install FFmpeg...
```

**Solution:** Install FFmpeg (see Installation section)

### Invalid Time Format

```
Error: trim operation 0 start must be in format 'HH:MM:SS' or numeric seconds
```

**Solution:** Use valid time format: `"00:01:30"` or `"90"`

### Rotation Degrees Invalid

```
Error: Rotate operation 0 degrees must be 0, 90, 180, or 270
```

**Solution:** Use only 90-degree increments: 0, 90, 180, 270

### Merge Requires Multiple Videos

```
Error: Merge operation 0 requires at least 2 videos
```

**Solution:** Provide at least 2 video URLs in the merge operation

## Advanced Usage

### Chaining with Other Tools

```python
# Download from AI Drive, edit, upload back
from tools.storage.aidrive_tool import AIDriveTool
from tools.media_processing.video_editor import VideoEditorTool

# 1. Get video from AI Drive
aidrive = AIDriveTool(action="get_readable_url", path="/videos/raw.mp4")
video_url = aidrive.run()["result"]["url"]

# 2. Edit video
editor = VideoEditorTool(
    video_url=video_url,
    operations=[
        {"type": "trim", "start": "0", "end": "30"},
        {"type": "resize", "width": 1920, "height": 1080}
    ]
)
result = editor.run()

# 3. Upload edited video
upload = AIDriveTool(
    action="upload",
    local_path=result["result"]["edited_video_url"].replace("file://", ""),
    remote_path="/videos/edited.mp4"
)
upload.run()
```

## Limitations

1. **FFmpeg Required**: Must have FFmpeg installed
2. **File Size**: Very large files (>5GB) may cause memory issues
3. **Format Support**: Limited to formats supported by FFmpeg
4. **Transition Effects**: Require multiple video clips to be effective
5. **Real-time Processing**: Not designed for live streaming

## Contributing

When contributing improvements:

1. Follow Agency Swarm tool development standards
2. Add tests for new operations
3. Update documentation
4. Ensure FFmpeg compatibility
5. Test with various video formats

## License

Part of the AgentSwarm Tools Framework.

## Support

For issues or questions:
- Check FFmpeg documentation: https://ffmpeg.org/documentation.html
- Review test cases in `test_video_editor.py`
- Consult tool documentation in main repository
