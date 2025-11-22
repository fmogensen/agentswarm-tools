"""
Extract comprehensive metadata from video files including codec, resolution, duration, bitrate, etc.
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os
import subprocess
import json
import re

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class VideoMetadataExtractor(BaseTool):
    """
    Extract comprehensive metadata from video files.

    This tool extracts detailed technical metadata from video files including:
    - Resolution, frame rate, aspect ratio
    - Video/audio codecs and bitrates
    - Duration and file size
    - Color space and profile information
    - Embedded metadata tags

    Args:
        video_path: Path or URL to the video file
        extract_thumbnails: Whether to extract thumbnail images at key frames
        include_streams: Include detailed stream information

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Comprehensive metadata dictionary
        - metadata: Tool execution information

    Example:
        >>> tool = VideoMetadataExtractor(
        ...     video_path="/path/to/video.mp4",
        ...     extract_thumbnails=True,
        ...     include_streams=True
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "video_metadata_extractor"
    tool_category: str = "media"

    # Parameters
    video_path: str = Field(
        ...,
        description="Path or URL to the video file",
        min_length=1
    )
    extract_thumbnails: bool = Field(
        default=False,
        description="Extract thumbnail images at key frames"
    )
    include_streams: bool = Field(
        default=True,
        description="Include detailed stream information"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the video metadata extraction."""
        self._validate_parameters()

        if self._should_use_mock():
            return self._generate_mock_results()

        try:
            result = self._process()
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "video_path": self.video_path
                }
            }
        except Exception as e:
            raise APIError(f"Metadata extraction failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.video_path or not isinstance(self.video_path, str):
            raise ValidationError(
                "video_path must be a non-empty string",
                tool_name=self.tool_name,
                field="video_path"
            )

        # Check if it's a URL or local file path
        if not self.video_path.startswith(("http://", "https://", "/")):
            # For relative paths, check if file exists
            if not os.path.isfile(self.video_path):
                raise ValidationError(
                    f"Video file not found: {self.video_path}",
                    tool_name=self.tool_name,
                    field="video_path"
                )

        # Validate video file extension
        valid_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm", ".m4v"]
        if not any(self.video_path.lower().endswith(ext) for ext in valid_extensions):
            # Only raise warning for local files, URLs might have different patterns
            if not self.video_path.startswith(("http://", "https://")):
                raise ValidationError(
                    f"Unsupported video format. Supported: {valid_extensions}",
                    tool_name=self.tool_name,
                    field="video_path"
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        metadata = {
            "file": {
                "path": self.video_path,
                "size_bytes": 15728640,
                "size_mb": 15.0,
                "format": "mp4",
                "created": "2024-01-15T10:30:00Z",
                "modified": "2024-01-15T10:30:00Z"
            },
            "video": {
                "codec": "h264",
                "codec_long": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
                "profile": "High",
                "level": "4.0",
                "width": 1920,
                "height": 1080,
                "resolution": "1920x1080",
                "aspect_ratio": "16:9",
                "frame_rate": 30.0,
                "bitrate": 2500000,
                "bitrate_mode": "VBR",
                "duration_seconds": 125.5,
                "duration_formatted": "00:02:05.5",
                "total_frames": 3765,
                "color_space": "yuv420p",
                "pixel_format": "yuv420p",
                "has_b_frames": True
            },
            "audio": {
                "codec": "aac",
                "codec_long": "AAC (Advanced Audio Coding)",
                "sample_rate": 48000,
                "channels": 2,
                "channel_layout": "stereo",
                "bitrate": 128000,
                "bits_per_sample": 16,
                "duration_seconds": 125.5
            },
            "container": {
                "format": "QuickTime / MOV",
                "major_brand": "isom",
                "compatible_brands": ["isom", "iso2", "avc1", "mp41"],
                "has_video": True,
                "has_audio": True,
                "has_subtitles": False
            },
            "mock": True
        }

        if self.extract_thumbnails:
            metadata["thumbnails"] = [
                {
                    "timestamp": 0.0,
                    "path": f"{self.video_path}_thumb_00.jpg",
                    "mock": True
                },
                {
                    "timestamp": 62.75,
                    "path": f"{self.video_path}_thumb_50.jpg",
                    "mock": True
                },
                {
                    "timestamp": 125.5,
                    "path": f"{self.video_path}_thumb_100.jpg",
                    "mock": True
                }
            ]

        if self.include_streams:
            metadata["streams"] = [
                {
                    "index": 0,
                    "type": "video",
                    "codec": "h264",
                    "width": 1920,
                    "height": 1080,
                    "fps": 30.0,
                    "bitrate": 2500000
                },
                {
                    "index": 1,
                    "type": "audio",
                    "codec": "aac",
                    "sample_rate": 48000,
                    "channels": 2,
                    "bitrate": 128000
                }
            ]

        return {
            "success": True,
            "result": metadata,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "video_path": self.video_path
            }
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic using ffprobe."""
        try:
            # Use ffprobe to extract metadata
            metadata = self._extract_with_ffprobe()

            if self.extract_thumbnails:
                metadata["thumbnails"] = self._extract_thumbnails()

            return metadata

        except FileNotFoundError:
            raise APIError(
                "ffprobe/ffmpeg is not installed. Please install ffmpeg.",
                tool_name=self.tool_name
            )
        except Exception as e:
            raise APIError(
                f"Failed to extract metadata: {e}",
                tool_name=self.tool_name
            )

    def _extract_with_ffprobe(self) -> Dict[str, Any]:
        """Extract metadata using ffprobe."""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            self.video_path
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise APIError(
                f"ffprobe failed: {result.stderr}",
                tool_name=self.tool_name
            )

        probe_data = json.loads(result.stdout)

        # Parse and structure the metadata
        metadata = self._parse_ffprobe_output(probe_data)

        if self.include_streams:
            metadata["streams"] = probe_data.get("streams", [])

        return metadata

    def _parse_ffprobe_output(self, probe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ffprobe output into structured metadata."""
        format_info = probe_data.get("format", {})
        streams = probe_data.get("streams", [])

        # Find video and audio streams
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

        metadata = {
            "file": {
                "path": self.video_path,
                "size_bytes": int(format_info.get("size", 0)),
                "size_mb": round(int(format_info.get("size", 0)) / (1024 * 1024), 2),
                "format": format_info.get("format_name", "unknown"),
                "duration": float(format_info.get("duration", 0))
            }
        }

        if video_stream:
            metadata["video"] = {
                "codec": video_stream.get("codec_name"),
                "codec_long": video_stream.get("codec_long_name"),
                "profile": video_stream.get("profile"),
                "width": video_stream.get("width"),
                "height": video_stream.get("height"),
                "resolution": f"{video_stream.get('width')}x{video_stream.get('height')}",
                "frame_rate": self._parse_frame_rate(video_stream.get("r_frame_rate")),
                "bitrate": int(video_stream.get("bit_rate", 0)),
                "pixel_format": video_stream.get("pix_fmt"),
                "color_space": video_stream.get("color_space")
            }

        if audio_stream:
            metadata["audio"] = {
                "codec": audio_stream.get("codec_name"),
                "codec_long": audio_stream.get("codec_long_name"),
                "sample_rate": int(audio_stream.get("sample_rate", 0)),
                "channels": audio_stream.get("channels"),
                "channel_layout": audio_stream.get("channel_layout"),
                "bitrate": int(audio_stream.get("bit_rate", 0))
            }

        return metadata

    def _parse_frame_rate(self, fps_str: Optional[str]) -> Optional[float]:
        """Parse frame rate string like '30/1' to float."""
        if not fps_str:
            return None
        try:
            if "/" in fps_str:
                num, den = fps_str.split("/")
                return round(float(num) / float(den), 2)
            return float(fps_str)
        except:
            return None

    def _extract_thumbnails(self) -> list:
        """Extract thumbnail images at key frames."""
        thumbnails = []
        # Placeholder for thumbnail extraction logic
        # In production, would use ffmpeg to extract frames
        return thumbnails


if __name__ == "__main__":
    print("Testing VideoMetadataExtractor...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test with mock data
    tool = VideoMetadataExtractor(
        video_path="/path/to/test_video.mp4",
        extract_thumbnails=True,
        include_streams=True
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Video resolution: {result.get('result', {}).get('video', {}).get('resolution')}")
    print(f"Duration: {result.get('result', {}).get('video', {}).get('duration_seconds')} seconds")

    assert result.get("success") == True
    assert "video" in result.get("result", {})
    assert "audio" in result.get("result", {})
    assert result.get("result", {}).get("video", {}).get("resolution") == "1920x1080"

    print("VideoMetadataExtractor test passed!")
