# Media Tools

Tools for generating, analyzing, and processing images, videos, and audio content.

## Subcategories

### Generation (`generation/`)
Create new media content from text descriptions or reference materials.

**Tools:**
- `image_generation` - Generate images from text descriptions
- `video_generation` - Generate video clips from prompts
- `audio_generation` - Generate audio, TTS, sound effects, music
- `podcast_generator` - Create multi-speaker podcast episodes
- `image_style_transfer` - Apply artistic styles to images
- `text_to_speech_advanced` - Advanced text-to-speech with voice control
- `video_effects` - Apply effects and filters to videos

### Analysis (`analysis/`)
Understand and extract information from media files.

**Tools:**
- `understand_images` - Analyze and describe image content
- `understand_video` - Extract transcripts and analyze videos
- `batch_understand_videos` - Analyze multiple videos in batch
- `analyze_media_content` - Deep analysis with custom requirements
- `audio_transcribe` - Convert speech to text
- `audio_effects` - Apply audio processing effects
- `batch_video_analysis` - Batch video analysis with custom parameters
- `extract_audio_from_video` - Extract audio tracks from video
- `merge_audio` - Combine multiple audio files
- `video_metadata_extractor` - Extract video metadata and properties

### Processing (`processing/`)
Edit and transform existing media files.

**Tools:**
- `photo_editor` - Edit and transform images
- `video_editor` - Edit and compose videos
- `video_clipper` - Extract and create clips from videos

## Category Identifier

All tools in this category have:
```python
tool_category: str = "media"
```

## Usage Examples

### Generate an image:
```python
from tools.media.generation.image_generation import ImageGeneration

tool = ImageGeneration(
    prompt="a futuristic city at sunset",
    params={"size": "1024x1024", "model": "flux-pro"}
)
result = tool.run()
```

### Analyze video content:
```python
from tools.media.analysis.understand_video import UnderstandVideo

tool = UnderstandVideo(
    media_url="https://youtube.com/watch?v=123",
    instruction="Extract full transcript with timestamps"
)
result = tool.run()
```

### Edit a photo:
```python
from tools.media.processing.photo_editor import PhotoEditor

tool = PhotoEditor(
    image_url="https://example.com/photo.jpg",
    operations=[
        {"type": "resize", "width": 800, "height": 600},
        {"type": "filter", "name": "sepia"}
    ]
)
result = tool.run()
```
