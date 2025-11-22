# Video Clipper Tool - Usage Examples

## Quick Start

### Example 1: Basic TikTok Clip Generation

```python
from tools.media_processing.video_clipper import VideoClipperTool

# Create 3 viral-worthy clips optimized for TikTok
tool = VideoClipperTool(
    video_url="https://example.com/podcast_episode.mp4",
    clip_duration=30,
    num_clips=3,
    detection_mode="highlights",
    aspect_ratio="9:16",
    add_captions=True,
    optimize_for="tiktok"
)

result = tool.run()

print(f"Created {len(result['clips'])} clips from {result['highlights_detected']} detected highlights")

for clip in result['clips']:
    print(f"\nClip: {clip['clip_id']}")
    print(f"  URL: {clip['url']}")
    print(f"  Time: {clip['start_time']} - {clip['end_time']}")
    print(f"  Score: {clip['score']}")
    print(f"  Type: {clip['highlight_type']}")
    print(f"  Caption: {clip['caption_preview']}")
```

Output:
```
Created 3 clips from 15 detected highlights

Clip: clip_1_abc12345
  URL: https://storage.example.com/clips/clip_abc12345.mp4
  Time: 00:02:30 - 00:03:00
  Score: 0.95
  Type: peak_moment
  Caption: This is the most important point we need to understand...

Clip: clip_2_def67890
  URL: https://storage.example.com/clips/clip_def67890.mp4
  Time: 00:05:15 - 00:05:45
  Score: 0.89
  Type: emotional_high
  Caption: And that's why this approach works so well in practice...
```

---

## Platform-Specific Examples

### Example 2: Instagram Reels

```python
tool = VideoClipperTool(
    video_url="https://example.com/tutorial_video.mp4",
    clip_duration=30,
    num_clips=5,
    detection_mode="auto",
    aspect_ratio="9:16",
    add_captions=True,
    add_transitions=True,
    optimize_for="instagram",
    output_format="mp4"
)

result = tool.run()

# Instagram Reels specs:
# - Max 60 seconds
# - 9:16 aspect ratio preferred
# - 30 FPS
# - 3000k bitrate
```

### Example 3: YouTube Shorts

```python
tool = VideoClipperTool(
    video_url="https://example.com/educational_content.mp4",
    clip_duration=60,  # Max for Shorts
    num_clips=2,
    detection_mode="topics",
    aspect_ratio="9:16",
    add_captions=True,
    optimize_for="youtube_shorts"
)

result = tool.run()

# YouTube Shorts specs:
# - Max 60 seconds
# - 9:16 aspect ratio
# - 30 FPS
# - 4000k bitrate (higher quality)
```

### Example 4: Instagram Feed (Square)

```python
tool = VideoClipperTool(
    video_url="https://example.com/product_demo.mp4",
    clip_duration=45,
    num_clips=3,
    detection_mode="highlights",
    aspect_ratio="1:1",  # Square format
    add_captions=False,
    optimize_for="instagram"
)

result = tool.run()
```

---

## Detection Mode Examples

### Example 5: Action Detection for Sports Content

```python
# Best for: Sports, gaming, fast-paced action
tool = VideoClipperTool(
    video_url="https://example.com/basketball_game.mp4",
    clip_duration=15,  # Short, intense clips
    num_clips=10,
    detection_mode="action",  # Motion-based detection
    aspect_ratio="16:9",
    add_captions=False,
    optimize_for="youtube_shorts"
)

result = tool.run()

# Detected highlight types:
# - fast_motion
# - scene_change
# - intense_moment
# - dynamic_shot
```

### Example 6: Dialogue Detection for Podcasts

```python
# Best for: Podcasts, interviews, talk shows
tool = VideoClipperTool(
    video_url="https://example.com/podcast_interview.mp4",
    clip_duration=45,
    num_clips=5,
    detection_mode="dialogue",  # Speech-based detection
    aspect_ratio="9:16",
    add_captions=True,  # Important for dialogue
    optimize_for="tiktok"
)

result = tool.run()

# Detected highlight types:
# - key_quote
# - question
# - punchline
# - statement
```

### Example 7: Highlights Detection for Events

```python
# Best for: Events, performances, emotional content
tool = VideoClipperTool(
    video_url="https://example.com/concert_performance.mp4",
    clip_duration=30,
    num_clips=8,
    detection_mode="highlights",  # Peak moments
    aspect_ratio="9:16",
    add_captions=False,
    optimize_for="instagram"
)

result = tool.run()

# Detected highlight types:
# - peak_moment
# - emotional_high
# - climax
# - turning_point
```

### Example 8: Topics Detection for Educational Content

```python
# Best for: Lectures, tutorials, presentations
tool = VideoClipperTool(
    video_url="https://example.com/programming_tutorial.mp4",
    clip_duration=60,
    num_clips=5,
    detection_mode="topics",  # Theme-based detection
    aspect_ratio="16:9",
    add_captions=True,
    optimize_for="youtube_shorts"
)

result = tool.run()

# Detected highlight types:
# - topic_intro
# - main_point
# - conclusion
# - summary
```

---

## Advanced Usage Examples

### Example 9: Batch Processing Multiple Videos

```python
video_urls = [
    "https://example.com/video1.mp4",
    "https://example.com/video2.mp4",
    "https://example.com/video3.mp4",
]

all_clips = []

for url in video_urls:
    tool = VideoClipperTool(
        video_url=url,
        clip_duration=30,
        num_clips=3,
        detection_mode="auto",
        aspect_ratio="9:16",
        optimize_for="tiktok"
    )

    result = tool.run()
    all_clips.extend(result['clips'])

    print(f"Processed {url}: {len(result['clips'])} clips created")

print(f"\nTotal clips created: {len(all_clips)}")
```

### Example 10: Custom Clip Selection Based on Scores

```python
tool = VideoClipperTool(
    video_url="https://example.com/long_video.mp4",
    clip_duration=30,
    num_clips=10,  # Get more clips to filter
    detection_mode="highlights",
    aspect_ratio="9:16",
    optimize_for="tiktok"
)

result = tool.run()

# Filter only high-scoring clips (>0.85)
high_quality_clips = [
    clip for clip in result['clips']
    if clip['score'] > 0.85
]

print(f"High quality clips: {len(high_quality_clips)}/{len(result['clips'])}")

for clip in high_quality_clips:
    print(f"Clip {clip['clip_id']}: Score {clip['score']}")
```

### Example 11: Different Aspect Ratios for Multi-Platform

```python
video_url = "https://example.com/content.mp4"

platforms = {
    "TikTok": {"aspect": "9:16", "duration": 30, "platform": "tiktok"},
    "YouTube": {"aspect": "16:9", "duration": 60, "platform": "youtube_shorts"},
    "Instagram Feed": {"aspect": "1:1", "duration": 45, "platform": "instagram"},
    "Instagram Stories": {"aspect": "4:5", "duration": 30, "platform": "instagram"},
}

clips_by_platform = {}

for platform_name, config in platforms.items():
    tool = VideoClipperTool(
        video_url=video_url,
        clip_duration=config["duration"],
        num_clips=3,
        aspect_ratio=config["aspect"],
        optimize_for=config["platform"],
        detection_mode="highlights"
    )

    result = tool.run()
    clips_by_platform[platform_name] = result['clips']

    print(f"{platform_name}: {len(result['clips'])} clips at {config['aspect']}")
```

### Example 12: Long-Form Content Extraction

```python
# Extract longer clips for general use (not social media)
tool = VideoClipperTool(
    video_url="https://example.com/documentary.mp4",
    clip_duration=180,  # 3 minutes
    num_clips=5,
    detection_mode="topics",
    aspect_ratio="16:9",
    add_captions=True,
    add_transitions=False,
    optimize_for="general"  # No platform restrictions
)

result = tool.run()

print(f"Created {len(result['clips'])} long-form clips")
print(f"Total duration: {result['total_duration']}")
```

---

## Error Handling Examples

### Example 13: Robust Error Handling

```python
from shared.errors import ValidationError, MediaError, AuthenticationError

try:
    tool = VideoClipperTool(
        video_url="https://example.com/video.mp4",
        clip_duration=30,
        num_clips=5
    )
    result = tool.run()

    if result.get('success'):
        print(f"Success! Created {len(result['clips'])} clips")
        for clip in result['clips']:
            print(f"  - {clip['url']}")
    else:
        print(f"Error: {result.get('error', {}).get('message')}")

except ValidationError as e:
    print(f"Invalid parameters: {e.message}")
    print(f"Field: {e.details.get('field')}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print("Please set OPENAI_API_KEY environment variable")

except MediaError as e:
    print(f"Video processing failed: {e.message}")
    print(f"Details: {e.details}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

### Example 14: Validation Testing

```python
# Test invalid URL
try:
    tool = VideoClipperTool(
        video_url="ftp://invalid.url/video.mp4",
        clip_duration=30,
        num_clips=3
    )
except ValueError as e:
    print(f"URL validation failed: {e}")

# Test duration exceeds platform limit
try:
    tool = VideoClipperTool(
        video_url="https://example.com/video.mp4",
        clip_duration=90,  # Exceeds TikTok 60s limit
        num_clips=3,
        optimize_for="tiktok"
    )
    result = tool.run()
    if not result.get('success'):
        print(f"Platform limit exceeded: {result['error']['message']}")
except Exception as e:
    print(f"Validation error: {e}")
```

---

## Testing Examples

### Example 15: Mock Mode Testing

```python
import os

# Enable mock mode for testing without processing
os.environ["USE_MOCK_APIS"] = "true"

tool = VideoClipperTool(
    video_url="https://example.com/test_video.mp4",
    clip_duration=30,
    num_clips=5,
    detection_mode="highlights"
)

result = tool.run()

assert result['success'] == True
assert len(result['clips']) == 5
assert result['metadata']['mock_mode'] == True

print("Mock mode test passed!")
print(f"Mock clips: {len(result['clips'])}")
print(f"Mock highlights detected: {result['highlights_detected']}")

# Disable mock mode
del os.environ["USE_MOCK_APIS"]
```

### Example 16: Integration Testing

```python
def test_video_clipper_integration():
    """Test complete workflow"""

    # Step 1: Create clips
    tool = VideoClipperTool(
        video_url="https://example.com/test.mp4",
        clip_duration=30,
        num_clips=3,
        detection_mode="auto"
    )

    result = tool.run()

    # Step 2: Verify results
    assert result['success'] == True
    assert len(result['clips']) == 3

    # Step 3: Check clip properties
    for clip in result['clips']:
        assert 'url' in clip
        assert 'score' in clip
        assert 'duration' in clip
        assert clip['duration'] == 30

    # Step 4: Verify ordering (by score)
    scores = [clip['score'] for clip in result['clips']]
    assert scores == sorted(scores, reverse=True)

    print("Integration test passed!")
    return result

# Run test
result = test_video_clipper_integration()
```

---

## Production Examples

### Example 17: Production Workflow with Storage

```python
import os
from pathlib import Path

# Production configuration
os.environ["OPENAI_API_KEY"] = "sk-..."  # Your API key

tool = VideoClipperTool(
    video_url="https://storage.example.com/videos/source.mp4",
    clip_duration=30,
    num_clips=5,
    detection_mode="highlights",
    aspect_ratio="9:16",
    add_captions=True,
    optimize_for="tiktok"
)

result = tool.run()

if result['success']:
    # Save metadata
    import json

    metadata_path = Path("/mnt/user-data/outputs/clip_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Created {len(result['clips'])} clips")
    print(f"Metadata saved to {metadata_path}")

    # Upload to cloud storage (pseudo-code)
    for clip in result['clips']:
        # upload_to_cloud(clip['url'], destination)
        print(f"Uploaded: {clip['clip_id']}")
```

### Example 18: Monitoring and Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_clips_with_monitoring(video_url, num_clips):
    """Create clips with comprehensive monitoring"""

    logger.info(f"Starting clip creation for {video_url}")

    try:
        tool = VideoClipperTool(
            video_url=video_url,
            clip_duration=30,
            num_clips=num_clips,
            detection_mode="highlights"
        )

        result = tool.run()

        if result['success']:
            logger.info(f"Successfully created {len(result['clips'])} clips")
            logger.info(f"Detected {result['highlights_detected']} highlights")
            logger.info(f"Total duration: {result['total_duration']}")

            for i, clip in enumerate(result['clips'], 1):
                logger.info(f"Clip {i}: Score={clip['score']}, Type={clip['highlight_type']}")

            return result
        else:
            logger.error(f"Clip creation failed: {result.get('error')}")
            return None

    except Exception as e:
        logger.exception(f"Exception during clip creation: {e}")
        raise

# Run with monitoring
result = create_clips_with_monitoring(
    "https://example.com/video.mp4",
    num_clips=5
)
```

---

## Performance Optimization Examples

### Example 19: Efficient Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_video(video_data):
    """Process a single video"""
    url, config = video_data

    tool = VideoClipperTool(
        video_url=url,
        **config
    )

    return tool.run()

# Video queue
videos = [
    ("https://example.com/video1.mp4", {"num_clips": 3, "clip_duration": 30}),
    ("https://example.com/video2.mp4", {"num_clips": 5, "clip_duration": 45}),
    ("https://example.com/video3.mp4", {"num_clips": 2, "clip_duration": 60}),
]

# Process in parallel (be mindful of API rate limits)
results = []
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(process_video, video): video[0] for video in videos}

    for future in as_completed(futures):
        video_url = futures[future]
        try:
            result = future.result()
            results.append(result)
            print(f"Completed: {video_url}")
        except Exception as e:
            print(f"Failed {video_url}: {e}")

print(f"Total clips created: {sum(len(r['clips']) for r in results)}")
```

### Example 20: Adaptive Quality Based on Content

```python
def create_adaptive_clips(video_url, content_type):
    """Create clips with settings optimized for content type"""

    presets = {
        "sports": {
            "detection_mode": "action",
            "clip_duration": 15,
            "num_clips": 10,
            "add_captions": False,
            "aspect_ratio": "16:9"
        },
        "podcast": {
            "detection_mode": "dialogue",
            "clip_duration": 45,
            "num_clips": 5,
            "add_captions": True,
            "aspect_ratio": "9:16"
        },
        "tutorial": {
            "detection_mode": "topics",
            "clip_duration": 60,
            "num_clips": 8,
            "add_captions": True,
            "aspect_ratio": "16:9"
        },
        "entertainment": {
            "detection_mode": "highlights",
            "clip_duration": 30,
            "num_clips": 5,
            "add_captions": True,
            "aspect_ratio": "9:16"
        }
    }

    config = presets.get(content_type, presets["entertainment"])

    tool = VideoClipperTool(
        video_url=video_url,
        **config
    )

    result = tool.run()
    print(f"Created {len(result['clips'])} clips for {content_type} content")

    return result

# Usage
create_adaptive_clips("https://example.com/sports.mp4", "sports")
create_adaptive_clips("https://example.com/podcast.mp4", "podcast")
create_adaptive_clips("https://example.com/tutorial.mp4", "tutorial")
```

---

## Summary

The VideoClipperTool is highly versatile and can be adapted to many use cases:

- **Social Media**: TikTok, Instagram Reels, YouTube Shorts
- **Content Types**: Sports, podcasts, tutorials, entertainment
- **Detection Modes**: Action, dialogue, highlights, topics, auto
- **Aspect Ratios**: 16:9, 9:16, 1:1, 4:5
- **Features**: Captions, transitions, platform optimization

Choose the right combination of parameters for your specific needs!
