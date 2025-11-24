"""
Extract specific clips from videos based on exact timestamps.

This tool extracts video segments from a source video file using precise start and end timestamps.
Unlike VideoClipperTool which uses AI to automatically detect highlights, this tool extracts
clips at exact user-specified timestamps.
"""

import os
import subprocess
import tempfile
import uuid
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import urlparse

import requests
from pydantic import Field, field_validator

from shared.base import BaseTool
from shared.errors import MediaError, ValidationError


class VideoClipExtractor(BaseTool):
    """
    Extract specific clips from videos based on exact timestamps.

    This tool extracts video segments from a source video using precise start and end timestamps.
    Useful when you know exactly which parts of a video you want to extract, without needing
    AI-powered scene detection.

    Args:
        video_url: URL to source video (supports http/https or file:// paths)
        clips: List of clip specifications with start_time and end_time in seconds
        output_format: Output video format (mp4, mov, webm)
        preserve_quality: Whether to preserve original quality (true) or optimize for size (false)
        add_fade: Whether to add fade in/out transitions to each clip
        aspect_ratio: Optional aspect ratio to apply (16:9, 9:16, 1:1, 4:5, or null for original)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - clips: List of extracted clip dictionaries with URLs and metadata
        - total_clips: Number of clips successfully extracted
        - total_duration: Combined duration of all clips
        - metadata: Processing metadata

    Example:
        >>> tool = VideoClipExtractor(
        ...     video_url="https://example.com/full_video.mp4",
        ...     clips=[
        ...         {"start_time": 30.5, "end_time": 60.0, "label": "intro"},
        ...         {"start_time": 120.0, "end_time": 180.5, "label": "main_segment"}
        ...     ],
        ...     output_format="mp4",
        ...     preserve_quality=True
        ... )
        >>> result = tool.run()
        >>> print(f"Extracted {result['total_clips']} clips")
    """

    # Tool metadata
    tool_name: str = "video_clip_extractor"
    tool_category: str = "media"

    # Parameters
    video_url: str = Field(..., description="URL to source video (http/https or file://)")
    clips: List[Dict[str, Any]] = Field(
        ...,
        description="List of clip specs: [{'start_time': float, 'end_time': float, 'label': str}]",
        min_length=1,
    )
    output_format: Literal["mp4", "mov", "webm"] = Field("mp4", description="Output video format")
    preserve_quality: bool = Field(
        True, description="Preserve original quality (true) or optimize for size (false)"
    )
    add_fade: bool = Field(False, description="Add fade in/out transitions to each clip")
    aspect_ratio: Optional[Literal["16:9", "9:16", "1:1", "4:5"]] = Field(
        None, description="Optional aspect ratio (null preserves original)"
    )

    # Aspect ratio mappings
    ASPECT_RATIOS: Dict[str, tuple] = {
        "16:9": (1920, 1080),
        "9:16": (1080, 1920),
        "1:1": (1080, 1080),
        "4:5": (1080, 1350),
    }

    @field_validator("video_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate video URL format."""
        try:
            parsed = urlparse(v)
            if not parsed.scheme in ["http", "https", "file"]:
                raise ValueError("URL must use http, https, or file:// protocol")
            if parsed.scheme in ["http", "https"] and not parsed.netloc:
                raise ValueError("Invalid URL format")
            return v
        except Exception as e:
            raise ValueError(f"Invalid video URL: {e}")

    @field_validator("clips")
    @classmethod
    def validate_clips(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate clip specifications."""
        if not v:
            raise ValueError("At least one clip specification is required")

        for i, clip in enumerate(v):
            if "start_time" not in clip:
                raise ValueError(f"Clip {i+1} missing 'start_time'")
            if "end_time" not in clip:
                raise ValueError(f"Clip {i+1} missing 'end_time'")

            start = clip["start_time"]
            end = clip["end_time"]

            if not isinstance(start, (int, float)) or start < 0:
                raise ValueError(f"Clip {i+1} start_time must be non-negative number")
            if not isinstance(end, (int, float)) or end <= 0:
                raise ValueError(f"Clip {i+1} end_time must be positive number")
            if end <= start:
                raise ValueError(f"Clip {i+1} end_time must be greater than start_time")

        return v

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the video_clip_extractor tool.

        Returns:
            Dict with results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "clips": result["clips"],
                "total_clips": len(result["clips"]),
                "total_duration": result["total_duration"],
                "metadata": result["metadata"],
            }
        except Exception as e:
            raise MediaError(
                f"Video clip extraction failed: {e}",
                media_type="video",
                tool_name=self.tool_name,
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate aspect ratio if provided
        if self.aspect_ratio and self.aspect_ratio not in self.ASPECT_RATIOS:
            raise ValidationError(
                f"Invalid aspect_ratio. Must be one of {list(self.ASPECT_RATIOS.keys())} or null",
                field="aspect_ratio",
                tool_name=self.tool_name,
            )

        # Additional validation for clip overlaps or ordering (optional)
        sorted_clips = sorted(self.clips, key=lambda x: x["start_time"])
        for i in range(len(sorted_clips) - 1):
            current_end = sorted_clips[i]["end_time"]
            next_start = sorted_clips[i + 1]["start_time"]
            if current_end > next_start:
                self._logger.warning(
                    f"Clips {i+1} and {i+2} overlap (ends at {current_end}, next starts at {next_start})"
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        extracted_clips = []
        total_duration = 0.0

        for i, clip_spec in enumerate(self.clips):
            start_time = clip_spec["start_time"]
            end_time = clip_spec["end_time"]
            duration = end_time - start_time
            total_duration += duration

            clip_id = uuid.uuid4().hex[:8]
            label = clip_spec.get("label", f"clip_{i+1}")

            extracted_clips.append(
                {
                    "clip_id": f"{label}_{clip_id}",
                    "label": label,
                    "url": f"https://mock.example.com/clips/{label}_{clip_id}.{self.output_format}",
                    "start_time": self._format_timestamp(start_time),
                    "end_time": self._format_timestamp(end_time),
                    "start_seconds": start_time,
                    "end_seconds": end_time,
                    "duration": f"{duration:.1f}s",
                    "duration_seconds": duration,
                    "format": self.output_format,
                    "resolution": (
                        f"{self.ASPECT_RATIOS[self.aspect_ratio][0]}x{self.ASPECT_RATIOS[self.aspect_ratio][1]}"
                        if self.aspect_ratio
                        else "1920x1080"
                    ),
                    "file_size": f"{int(duration * 2.5)}MB",  # Mock size estimation
                }
            )

        return {
            "success": True,
            "clips": extracted_clips,
            "total_clips": len(extracted_clips),
            "total_duration": f"{total_duration:.1f}s",
            "metadata": {
                "mock_mode": True,
                "source_url": self.video_url,
                "output_format": self.output_format,
                "preserve_quality": self.preserve_quality,
                "aspect_ratio_applied": self.aspect_ratio or "original",
                "fade_transitions": self.add_fade,
                "processing_time": "1.2s",
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        try:
            # Check dependencies
            self._check_ffmpeg()

            # Download or access source video
            self._logger.info(f"Accessing video from {self.video_url}")
            video_file = self._get_video_file(self.video_url)

            # Extract clips
            extracted_clips = []
            total_duration = 0.0

            for i, clip_spec in enumerate(self.clips):
                self._logger.info(
                    f"Extracting clip {i+1}/{len(self.clips)}: {clip_spec.get('label', 'unnamed')}"
                )
                clip = self._extract_clip(video_file, clip_spec, i)
                extracted_clips.append(clip)
                total_duration += clip["duration_seconds"]

            # Clean up source video if it was downloaded
            if self.video_url.startswith(("http://", "https://")):
                if os.path.exists(video_file):
                    os.unlink(video_file)

            return {
                "clips": extracted_clips,
                "total_duration": f"{total_duration:.1f}s",
                "metadata": {
                    "source_url": self.video_url,
                    "output_format": self.output_format,
                    "preserve_quality": self.preserve_quality,
                    "aspect_ratio_applied": self.aspect_ratio or "original",
                    "fade_transitions": self.add_fade,
                },
            }

        except subprocess.CalledProcessError as e:
            raise MediaError(
                f"FFmpeg command failed: {e.stderr.decode() if e.stderr else str(e)}",
                media_type="video",
                tool_name=self.tool_name,
            )
        except requests.RequestException as e:
            raise MediaError(
                f"Failed to download video: {e}",
                media_type="video",
                tool_name=self.tool_name,
            )

    def _check_ffmpeg(self) -> None:
        """Check if FFmpeg is available."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise MediaError(
                "FFmpeg not found. Please install FFmpeg to use video extraction features.",
                media_type="video",
                tool_name=self.tool_name,
            )

    def _get_video_file(self, url: str) -> str:
        """
        Get video file path (download if URL, return path if file://).

        Args:
            url: Video URL

        Returns:
            Path to video file
        """
        if url.startswith("file://"):
            # Local file path
            file_path = url[7:]  # Remove 'file://'
            if not os.path.exists(file_path):
                raise MediaError(
                    f"Video file not found: {file_path}",
                    media_type="video",
                    tool_name=self.tool_name,
                )
            return file_path
        else:
            # Download from URL
            return self._download_video(url)

    def _download_video(self, url: str) -> str:
        """Download video from URL."""
        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode="wb", suffix=".mp4", delete=False)

        # Download with chunks
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)

        temp_file.close()
        return temp_file.name

    def _extract_clip(
        self, video_file: str, clip_spec: Dict[str, Any], index: int
    ) -> Dict[str, Any]:
        """Extract a single clip from the source video."""
        start_time = clip_spec["start_time"]
        end_time = clip_spec["end_time"]
        duration = end_time - start_time
        label = clip_spec.get("label", f"clip_{index+1}")

        # Create output file
        clip_id = uuid.uuid4().hex[:8]
        output_file = tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=f".{self.output_format}",
            delete=False,
        ).name

        # Build FFmpeg command
        cmd = ["ffmpeg", "-ss", str(start_time), "-i", video_file, "-t", str(duration)]

        # Add video filters
        filters = []

        # Apply aspect ratio if specified
        if self.aspect_ratio:
            width, height = self.ASPECT_RATIOS[self.aspect_ratio]
            filters.append(f"scale={width}:{height}:force_original_aspect_ratio=increase")
            filters.append(f"crop={width}:{height}")

        # Add fade transitions if requested
        if self.add_fade:
            fade_duration = min(0.5, duration / 4)  # Fade is 0.5s or 25% of clip, whichever is shorter
            fade_frames = int(fade_duration * 30)  # Assuming 30fps
            filters.append(f"fade=in:0:{fade_frames}")
            filters.append(f"fade=out:st={duration-fade_duration}:d={fade_duration}")

        # Apply filters if any
        if filters:
            cmd.extend(["-vf", ",".join(filters)])

        # Quality settings
        if self.preserve_quality:
            cmd.extend(["-c:v", "libx264", "-preset", "slow", "-crf", "18"])
        else:
            cmd.extend(["-c:v", "libx264", "-preset", "fast", "-crf", "23"])

        # Audio codec
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])

        # Output file
        cmd.extend([output_file, "-y"])

        # Execute FFmpeg
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Get file size
        file_size = os.path.getsize(output_file)

        # In production, upload to storage and get URL
        # For now, return file:// URL
        file_url = f"file://{output_file}"

        return {
            "clip_id": f"{label}_{clip_id}",
            "label": label,
            "url": file_url,
            "start_time": self._format_timestamp(start_time),
            "end_time": self._format_timestamp(end_time),
            "start_seconds": start_time,
            "end_seconds": end_time,
            "duration": f"{duration:.1f}s",
            "duration_seconds": duration,
            "format": self.output_format,
            "resolution": (
                f"{self.ASPECT_RATIOS[self.aspect_ratio][0]}x{self.ASPECT_RATIOS[self.aspect_ratio][1]}"
                if self.aspect_ratio
                else "original"
            ),
            "file_size": self._format_file_size(file_size),
            "file_path": output_file,
        }

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS.mmm."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


if __name__ == "__main__":
    # Test the video_clip_extractor tool
    print("Testing VideoClipExtractor...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic clip extraction
    print("\n1. Testing basic clip extraction...")
    tool1 = VideoClipExtractor(
        video_url="https://example.com/full_video.mp4",
        clips=[
            {"start_time": 30.0, "end_time": 60.0, "label": "intro"},
            {"start_time": 120.0, "end_time": 180.0, "label": "main_segment"},
        ],
        output_format="mp4",
    )
    result1 = tool1.run()
    assert result1.get("success") == True
    assert result1["total_clips"] == 2
    assert len(result1["clips"]) == 2
    assert result1["clips"][0]["label"] == "intro"
    assert result1["clips"][0]["duration_seconds"] == 30.0
    print(f"   Extracted {result1['total_clips']} clips")
    print("   Basic extraction test passed")

    # Test 2: Single clip extraction
    print("\n2. Testing single clip extraction...")
    tool2 = VideoClipExtractor(
        video_url="https://example.com/video.mp4",
        clips=[{"start_time": 10.5, "end_time": 25.75, "label": "highlight"}],
        output_format="mp4",
        preserve_quality=True,
    )
    result2 = tool2.run()
    assert result2.get("success") == True
    assert result2["total_clips"] == 1
    assert result2["clips"][0]["duration_seconds"] == 15.25
    print("   Single clip extraction test passed")

    # Test 3: With aspect ratio and fade
    print("\n3. Testing with aspect ratio and fade...")
    tool3 = VideoClipExtractor(
        video_url="https://example.com/video.mp4",
        clips=[
            {"start_time": 0, "end_time": 30, "label": "vertical_clip"},
        ],
        output_format="mp4",
        aspect_ratio="9:16",
        add_fade=True,
    )
    result3 = tool3.run()
    assert result3.get("success") == True
    assert result3["metadata"]["aspect_ratio_applied"] == "9:16"
    assert result3["metadata"]["fade_transitions"] == True
    print("   Aspect ratio and fade test passed")

    # Test 4: Multiple clips with different formats
    print("\n4. Testing multiple clips with webm format...")
    tool4 = VideoClipExtractor(
        video_url="https://example.com/long_video.mp4",
        clips=[
            {"start_time": 10, "end_time": 20, "label": "clip1"},
            {"start_time": 50, "end_time": 70, "label": "clip2"},
            {"start_time": 100, "end_time": 130, "label": "clip3"},
        ],
        output_format="webm",
        preserve_quality=False,
    )
    result4 = tool4.run()
    assert result4.get("success") == True
    assert result4["total_clips"] == 3
    assert all(clip["format"] == "webm" for clip in result4["clips"])
    print("   Multiple clips with webm format test passed")

    # Test 5: Square aspect ratio
    print("\n5. Testing square aspect ratio (1:1)...")
    tool5 = VideoClipExtractor(
        video_url="https://example.com/video.mp4",
        clips=[{"start_time": 5, "end_time": 15, "label": "square"}],
        output_format="mp4",
        aspect_ratio="1:1",
    )
    result5 = tool5.run()
    assert result5.get("success") == True
    assert "1080x1080" in result5["clips"][0]["resolution"]
    print("   Square aspect ratio test passed")

    # Test 6: Validation error - invalid clip times
    print("\n6. Testing validation error (end_time <= start_time)...")
    try:
        tool6 = VideoClipExtractor(
            video_url="https://example.com/video.mp4",
            clips=[{"start_time": 60, "end_time": 30, "label": "invalid"}],
        )
        result6 = tool6.run()
        assert False, "Should have raised validation error"
    except Exception as e:
        print(f"   Validation error caught: {type(e).__name__}")

    # Test 7: Validation error - negative start time
    print("\n7. Testing validation error (negative start_time)...")
    try:
        tool7 = VideoClipExtractor(
            video_url="https://example.com/video.mp4",
            clips=[{"start_time": -10, "end_time": 20, "label": "negative"}],
        )
        result7 = tool7.run()
        assert False, "Should have raised validation error"
    except Exception as e:
        print(f"   Validation error caught: {type(e).__name__}")

    # Test 8: Validation error - empty clips list
    print("\n8. Testing validation error (empty clips list)...")
    try:
        tool8 = VideoClipExtractor(
            video_url="https://example.com/video.mp4",
            clips=[],
        )
        result8 = tool8.run()
        assert False, "Should have raised validation error"
    except Exception as e:
        print(f"   Validation error caught: {type(e).__name__}")

    # Test 9: Precision timestamps
    print("\n9. Testing precision timestamps...")
    tool9 = VideoClipExtractor(
        video_url="https://example.com/video.mp4",
        clips=[{"start_time": 12.345, "end_time": 23.678, "label": "precise"}],
        output_format="mp4",
    )
    result9 = tool9.run()
    assert result9.get("success") == True
    assert result9["clips"][0]["start_seconds"] == 12.345
    assert result9["clips"][0]["end_seconds"] == 23.678
    print("   Precision timestamps test passed")

    # Test 10: File URL protocol
    print("\n10. Testing file:// URL protocol...")
    tool10 = VideoClipExtractor(
        video_url="file:///path/to/local/video.mp4",
        clips=[{"start_time": 0, "end_time": 10, "label": "local"}],
        output_format="mp4",
    )
    result10 = tool10.run()
    assert result10.get("success") == True
    assert result10["metadata"]["source_url"] == "file:///path/to/local/video.mp4"
    print("   File URL protocol test passed")

    print("\nAll tests passed!")
    print("\nSample clip output:")
    import json

    print(json.dumps(result1["clips"][0], indent=2))
