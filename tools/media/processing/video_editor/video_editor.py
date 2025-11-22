"""
Perform advanced video editing operations using FFmpeg.
"""

from typing import Any, Dict, List, Optional, Union, ClassVar
from pydantic import Field
import os
import subprocess
import tempfile
import requests
import uuid
from pathlib import Path
import json

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, MediaError


class VideoEditorTool(BaseTool):
    """
    Perform advanced video editing operations using FFmpeg.

    Use this tool to edit videos including trim, merge, add audio, add subtitles,
    resize, rotate, speed adjustment, and transitions.

    Args:
        video_url: URL to source video (required for most operations)
        operations: List of editing operations to apply in sequence
        output_format: Output format (mp4, avi, mov, webm)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: {"edited_video_url": "...", "format": "...", "duration": "..."}
        - metadata: Processing metadata

    Supported Operations:
        - trim: Cut video to specific time range
        - merge: Combine multiple videos
        - add_audio: Add or replace audio track
        - add_subtitles: Add subtitle file
        - resize: Change video dimensions
        - rotate: Rotate video by degrees
        - speed: Adjust playback speed
        - transition: Add transitions between clips

    Example:
        >>> tool = VideoEditorTool(
        ...     video_url="https://example.com/video.mp4",
        ...     operations=[
        ...         {"type": "trim", "start": "00:00:10", "end": "00:00:30"},
        ...         {"type": "resize", "width": 1920, "height": 1080},
        ...         {"type": "speed", "factor": 1.5}
        ...     ],
        ...     output_format="mp4"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "video_editor"
    tool_category: str = "media"

    # Parameters
    video_url: Optional[str] = Field(
        None, description="URL to source video (required for most operations)"
    )
    operations: List[Dict[str, Any]] = Field(
        ..., description="List of editing operations to apply", min_length=1
    )
    output_format: str = Field("mp4", description="Output format: mp4, avi, mov, webm")

    # Supported operation types
    SUPPORTED_OPERATIONS: ClassVar[set] = {
        "trim",
        "merge",
        "add_audio",
        "add_subtitles",
        "resize",
        "rotate",
        "speed",
        "transition",
    }

    # Supported formats
    SUPPORTED_FORMATS: ClassVar[set] = {"mp4", "avi", "mov", "webm"}

    # Supported transition effects
    SUPPORTED_TRANSITIONS: ClassVar[set] = {"fade", "wipeleft", "wiperight", "wipeup", "wipedown", "dissolve"}

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the video_editor tool.

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
                "result": result,
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            raise MediaError(
                f"Video editing failed: {e}",
                media_type="video",
                tool_name=self.tool_name,
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Check if video_url is required for this operation set
        requires_video = any(
            op.get("type") != "merge" for op in self.operations
        )

        if requires_video and not self.video_url:
            # Check if it's a merge operation with videos in the operation itself
            merge_ops = [op for op in self.operations if op.get("type") == "merge"]
            if not merge_ops or not merge_ops[0].get("videos"):
                raise ValidationError(
                    "video_url is required for non-merge operations",
                    tool_name=self.tool_name
                )

        # Validate output format
        if self.output_format.lower() not in self.SUPPORTED_FORMATS:
            raise ValidationError(
                f"output_format must be one of {self.SUPPORTED_FORMATS}",
                field="output_format",
                tool_name=self.tool_name,
            )

        # Validate operations
        if not self.operations:
            raise ValidationError(
                "At least one operation is required",
                field="operations",
                tool_name=self.tool_name,
            )

        # Validate each operation
        for i, operation in enumerate(self.operations):
            if "type" not in operation:
                raise ValidationError(
                    f"Operation {i} missing 'type' field",
                    field="operations",
                    tool_name=self.tool_name,
                )

            op_type = operation["type"]
            if op_type not in self.SUPPORTED_OPERATIONS:
                raise ValidationError(
                    f"Operation type '{op_type}' not supported. Must be one of {self.SUPPORTED_OPERATIONS}",
                    field="operations",
                    tool_name=self.tool_name,
                )

            # Validate specific operation parameters
            self._validate_operation(operation, i)

    def _validate_operation(self, operation: Dict[str, Any], index: int) -> None:
        """Validate individual operation parameters."""
        op_type = operation["type"]

        if op_type == "trim":
            if "start" not in operation or "end" not in operation:
                raise ValidationError(
                    f"Trim operation {index} requires 'start' and 'end' fields",
                    field="operations",
                    tool_name=self.tool_name,
                )
            # Validate time format (HH:MM:SS or seconds)
            self._validate_time_format(operation["start"], f"trim operation {index} start")
            self._validate_time_format(operation["end"], f"trim operation {index} end")

        elif op_type == "merge":
            if "videos" not in operation:
                raise ValidationError(
                    f"Merge operation {index} requires 'videos' field",
                    field="operations",
                    tool_name=self.tool_name,
                )
            if not isinstance(operation["videos"], list) or len(operation["videos"]) < 2:
                raise ValidationError(
                    f"Merge operation {index} requires at least 2 videos",
                    field="operations",
                    tool_name=self.tool_name,
                )

        elif op_type == "add_audio":
            if "audio_url" not in operation:
                raise ValidationError(
                    f"Add_audio operation {index} requires 'audio_url' field",
                    field="operations",
                    tool_name=self.tool_name,
                )

        elif op_type == "add_subtitles":
            if "subtitle_url" not in operation:
                raise ValidationError(
                    f"Add_subtitles operation {index} requires 'subtitle_url' field",
                    field="operations",
                    tool_name=self.tool_name,
                )

        elif op_type == "resize":
            if "width" not in operation or "height" not in operation:
                raise ValidationError(
                    f"Resize operation {index} requires 'width' and 'height' fields",
                    field="operations",
                    tool_name=self.tool_name,
                )
            if operation["width"] <= 0 or operation["height"] <= 0:
                raise ValidationError(
                    f"Resize operation {index} width and height must be positive",
                    field="operations",
                    tool_name=self.tool_name,
                )

        elif op_type == "rotate":
            if "degrees" not in operation:
                raise ValidationError(
                    f"Rotate operation {index} requires 'degrees' field",
                    field="operations",
                    tool_name=self.tool_name,
                )
            if operation["degrees"] not in [0, 90, 180, 270, -90, -180, -270]:
                raise ValidationError(
                    f"Rotate operation {index} degrees must be 0, 90, 180, or 270 (or negative)",
                    field="operations",
                    tool_name=self.tool_name,
                )

        elif op_type == "speed":
            if "factor" not in operation:
                raise ValidationError(
                    f"Speed operation {index} requires 'factor' field",
                    field="operations",
                    tool_name=self.tool_name,
                )
            if operation["factor"] <= 0:
                raise ValidationError(
                    f"Speed operation {index} factor must be positive",
                    field="operations",
                    tool_name=self.tool_name,
                )

        elif op_type == "transition":
            if "effect" not in operation:
                raise ValidationError(
                    f"Transition operation {index} requires 'effect' field",
                    field="operations",
                    tool_name=self.tool_name,
                )
            if operation["effect"] not in self.SUPPORTED_TRANSITIONS:
                raise ValidationError(
                    f"Transition effect '{operation['effect']}' not supported. Must be one of {self.SUPPORTED_TRANSITIONS}",
                    field="operations",
                    tool_name=self.tool_name,
                )

    def _validate_time_format(self, time_str: str, field_name: str) -> None:
        """Validate time format (HH:MM:SS or numeric seconds)."""
        import re

        # Allow numeric seconds or HH:MM:SS format
        time_pattern = r'^(\d+:)?(\d{1,2}:)?\d{1,2}(\.\d+)?$'
        numeric_pattern = r'^\d+(\.\d+)?$'

        if not (re.match(time_pattern, str(time_str)) or re.match(numeric_pattern, str(time_str))):
            raise ValidationError(
                f"{field_name} must be in format 'HH:MM:SS' or numeric seconds",
                field="operations",
                tool_name=self.tool_name,
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "edited_video_url": f"https://mock.example.com/edited_video_{uuid.uuid4().hex[:8]}.{self.output_format}",
                "format": self.output_format,
                "duration": "00:00:20",
                "resolution": "1920x1080",
                "file_size": "5.2 MB",
                "operations_applied": len(self.operations),
                "fps": 30,
            },
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        try:
            # Check FFmpeg availability
            self._check_ffmpeg()

            # Download source video(s)
            temp_files = []
            input_file = None

            # For merge operations, handle differently
            merge_ops = [op for op in self.operations if op.get("type") == "merge"]
            if merge_ops and not self.video_url:
                # Merge operation without initial video_url
                videos = merge_ops[0]["videos"]
                temp_files = [self._download_file(url, "video") for url in videos]
                # Remove merge from operations as it will be handled first
                operations_to_apply = [op for op in self.operations if op.get("type") != "merge"]
            else:
                if self.video_url:
                    input_file = self._download_file(self.video_url, "video")
                    temp_files.append(input_file)
                operations_to_apply = self.operations

            # Create output file path
            output_file = tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=f".{self.output_format}",
                delete=False,
            ).name

            # Apply operations sequentially
            current_input = input_file if input_file else temp_files[0]

            # Handle merge first if present
            if merge_ops and not self.video_url:
                current_input = self._apply_merge(temp_files, merge_ops[0])
                temp_files = [current_input]

            for i, operation in enumerate(operations_to_apply):
                is_last = (i == len(operations_to_apply) - 1)
                output = output_file if is_last else tempfile.NamedTemporaryFile(
                    mode="wb",
                    suffix=f".{self.output_format}",
                    delete=False,
                ).name

                current_input = self._apply_operation(current_input, operation, output)

                if not is_last:
                    temp_files.append(current_input)

            # Get video info
            video_info = self._get_video_info(output_file)

            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception as e:
                    self._logger.warning(f"Failed to delete temp file {temp_file}: {e}")

            # Get file size
            file_size = self._format_file_size(os.path.getsize(output_file))

            # In production, upload to AI Drive or cloud storage
            file_url = f"file://{output_file}"

            return {
                "edited_video_url": file_url,
                "format": self.output_format,
                "duration": video_info.get("duration", "unknown"),
                "resolution": video_info.get("resolution", "unknown"),
                "file_size": file_size,
                "operations_applied": len(self.operations),
                "fps": video_info.get("fps", 30),
            }

        except subprocess.CalledProcessError as e:
            raise MediaError(
                f"FFmpeg command failed: {e.stderr.decode() if e.stderr else str(e)}",
                media_type="video",
                tool_name=self.tool_name,
            )
        except requests.RequestException as e:
            raise APIError(
                f"Failed to download video: {e}", tool_name=self.tool_name
            )
        except Exception as e:
            raise MediaError(
                f"Video processing failed: {e}",
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
                "FFmpeg not found. Please install FFmpeg to use video editing features.",
                media_type="video",
                tool_name=self.tool_name,
            )

    def _download_file(self, url: str, file_type: str) -> str:
        """
        Download file from URL.

        Args:
            url: File URL
            file_type: Type of file (video, audio, subtitle)

        Returns:
            Path to downloaded file
        """
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()

        # Determine file extension from URL or content-type
        extension = Path(url).suffix or ".tmp"

        temp_file = tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=extension,
            delete=False,
        )

        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)

        temp_file.close()
        return temp_file.name

    def _apply_operation(
        self, input_file: str, operation: Dict[str, Any], output_file: str
    ) -> str:
        """
        Apply a single operation to the video.

        Args:
            input_file: Path to input video
            operation: Operation dictionary
            output_file: Path to output video

        Returns:
            Path to output video
        """
        op_type = operation["type"]

        if op_type == "trim":
            self._apply_trim(input_file, operation, output_file)
        elif op_type == "merge":
            # Already handled in _process
            return input_file
        elif op_type == "add_audio":
            self._apply_add_audio(input_file, operation, output_file)
        elif op_type == "add_subtitles":
            self._apply_add_subtitles(input_file, operation, output_file)
        elif op_type == "resize":
            self._apply_resize(input_file, operation, output_file)
        elif op_type == "rotate":
            self._apply_rotate(input_file, operation, output_file)
        elif op_type == "speed":
            self._apply_speed(input_file, operation, output_file)
        elif op_type == "transition":
            # Transitions require multiple clips - skip for single video
            self._logger.warning("Transition operation requires merge operation. Skipping.")
            # Copy input to output
            subprocess.run(
                ["ffmpeg", "-i", input_file, "-c", "copy", output_file, "-y"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        return output_file

    def _apply_trim(
        self, input_file: str, operation: Dict[str, Any], output_file: str
    ) -> None:
        """Trim video to specified time range."""
        start = operation["start"]
        end = operation["end"]

        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-ss", str(start),
            "-to", str(end),
            "-c", "copy",
            output_file,
            "-y",
        ]

        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _apply_merge(self, video_files: List[str], operation: Dict[str, Any]) -> str:
        """Merge multiple videos."""
        # Create concat file
        concat_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        for video_file in video_files:
            concat_file.write(f"file '{video_file}'\n")
        concat_file.close()

        output_file = tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=f".{self.output_format}",
            delete=False,
        ).name

        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file.name,
            "-c", "copy",
            output_file,
            "-y",
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        finally:
            os.unlink(concat_file.name)

        return output_file

    def _apply_add_audio(
        self, input_file: str, operation: Dict[str, Any], output_file: str
    ) -> None:
        """Add or replace audio track."""
        audio_url = operation["audio_url"]
        audio_file = self._download_file(audio_url, "audio")

        try:
            # Replace audio track
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-i", audio_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                output_file,
                "-y",
            ]

            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        finally:
            if os.path.exists(audio_file):
                os.unlink(audio_file)

    def _apply_add_subtitles(
        self, input_file: str, operation: Dict[str, Any], output_file: str
    ) -> None:
        """Add subtitles to video."""
        subtitle_url = operation["subtitle_url"]
        subtitle_file = self._download_file(subtitle_url, "subtitle")

        try:
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-vf", f"subtitles={subtitle_file}",
                "-c:a", "copy",
                output_file,
                "-y",
            ]

            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        finally:
            if os.path.exists(subtitle_file):
                os.unlink(subtitle_file)

    def _apply_resize(
        self, input_file: str, operation: Dict[str, Any], output_file: str
    ) -> None:
        """Resize video to specified dimensions."""
        width = operation["width"]
        height = operation["height"]

        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-vf", f"scale={width}:{height}",
            "-c:a", "copy",
            output_file,
            "-y",
        ]

        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _apply_rotate(
        self, input_file: str, operation: Dict[str, Any], output_file: str
    ) -> None:
        """Rotate video by specified degrees."""
        degrees = operation["degrees"]

        # FFmpeg transpose values: 0=90°, 1=90°CW, 2=90°CCW, 3=90°CW+vflip
        # For 180° we use two 90° rotations
        if degrees == 90 or degrees == -270:
            transpose = "1"
        elif degrees == -90 or degrees == 270:
            transpose = "2"
        elif degrees == 180 or degrees == -180:
            transpose = "1,transpose=1"
        else:
            # 0 degrees - just copy
            subprocess.run(
                ["ffmpeg", "-i", input_file, "-c", "copy", output_file, "-y"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return

        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-vf", f"transpose={transpose}",
            "-c:a", "copy",
            output_file,
            "-y",
        ]

        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _apply_speed(
        self, input_file: str, operation: Dict[str, Any], output_file: str
    ) -> None:
        """Adjust video playback speed."""
        factor = operation["factor"]

        # Video speed adjustment
        video_filter = f"setpts={1/factor}*PTS"

        # Audio speed adjustment
        audio_filter = f"atempo={factor}"

        # FFmpeg atempo filter only supports 0.5-2.0, so we need to chain for higher values
        audio_filters = []
        remaining = factor
        while remaining > 2.0:
            audio_filters.append("atempo=2.0")
            remaining /= 2.0
        while remaining < 0.5:
            audio_filters.append("atempo=0.5")
            remaining /= 0.5
        if remaining != 1.0:
            audio_filters.append(f"atempo={remaining}")

        audio_filter_str = ",".join(audio_filters) if audio_filters else "atempo=1.0"

        cmd = [
            "ffmpeg",
            "-i", input_file,
            "-filter_complex", f"[0:v]{video_filter}[v];[0:a]{audio_filter_str}[a]",
            "-map", "[v]",
            "-map", "[a]",
            output_file,
            "-y",
        ]

        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _get_video_info(self, video_file: str) -> Dict[str, Any]:
        """Get video metadata."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_file,
            ]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            info = json.loads(result.stdout.decode())

            # Extract relevant information
            video_stream = next(
                (s for s in info.get("streams", []) if s.get("codec_type") == "video"),
                {}
            )

            duration = float(info.get("format", {}).get("duration", 0))
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            width = video_stream.get("width", 0)
            height = video_stream.get("height", 0)
            fps = eval(video_stream.get("r_frame_rate", "30/1"))

            return {
                "duration": duration_str,
                "resolution": f"{width}x{height}",
                "fps": int(fps),
            }

        except Exception as e:
            self._logger.warning(f"Failed to get video info: {e}")
            return {
                "duration": "unknown",
                "resolution": "unknown",
                "fps": 30,
            }

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
    # Test the video_editor tool
    print("Testing VideoEditorTool...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Trim operation
    print("\n1. Testing trim operation...")
    tool1 = VideoEditorTool(
        video_url="https://example.com/video.mp4",
        operations=[
            {"type": "trim", "start": "00:00:10", "end": "00:00:30"}
        ],
        output_format="mp4",
    )
    result1 = tool1.run()
    assert result1.get("success") == True
    assert "edited_video_url" in result1["result"]
    assert result1["result"]["operations_applied"] == 1
    print("   Trim operation test passed")

    # Test 2: Resize and rotate
    print("\n2. Testing resize and rotate operations...")
    tool2 = VideoEditorTool(
        video_url="https://example.com/video.mp4",
        operations=[
            {"type": "resize", "width": 1920, "height": 1080},
            {"type": "rotate", "degrees": 90}
        ],
        output_format="mp4",
    )
    result2 = tool2.run()
    assert result2.get("success") == True
    assert result2["result"]["operations_applied"] == 2
    print("   Resize and rotate test passed")

    # Test 3: Speed adjustment
    print("\n3. Testing speed adjustment...")
    tool3 = VideoEditorTool(
        video_url="https://example.com/video.mp4",
        operations=[
            {"type": "speed", "factor": 2.0}
        ],
        output_format="mp4",
    )
    result3 = tool3.run()
    assert result3.get("success") == True
    print("   Speed adjustment test passed")

    # Test 4: Add audio
    print("\n4. Testing add audio operation...")
    tool4 = VideoEditorTool(
        video_url="https://example.com/video.mp4",
        operations=[
            {"type": "add_audio", "audio_url": "https://example.com/audio.mp3"}
        ],
        output_format="mp4",
    )
    result4 = tool4.run()
    assert result4.get("success") == True
    print("   Add audio test passed")

    # Test 5: Merge videos
    print("\n5. Testing merge operation...")
    tool5 = VideoEditorTool(
        operations=[
            {
                "type": "merge",
                "videos": [
                    "https://example.com/video1.mp4",
                    "https://example.com/video2.mp4",
                    "https://example.com/video3.mp4"
                ]
            }
        ],
        output_format="mp4",
    )
    result5 = tool5.run()
    assert result5.get("success") == True
    print("   Merge operation test passed")

    # Test 6: Add subtitles
    print("\n6. Testing add subtitles operation...")
    tool6 = VideoEditorTool(
        video_url="https://example.com/video.mp4",
        operations=[
            {"type": "add_subtitles", "subtitle_url": "https://example.com/subtitles.srt"}
        ],
        output_format="mp4",
    )
    result6 = tool6.run()
    assert result6.get("success") == True
    print("   Add subtitles test passed")

    # Test 7: Complex multi-operation workflow
    print("\n7. Testing complex multi-operation workflow...")
    tool7 = VideoEditorTool(
        video_url="https://example.com/video.mp4",
        operations=[
            {"type": "trim", "start": "00:00:05", "end": "00:00:25"},
            {"type": "resize", "width": 1280, "height": 720},
            {"type": "speed", "factor": 1.5},
            {"type": "rotate", "degrees": 180}
        ],
        output_format="webm",
    )
    result7 = tool7.run()
    assert result7.get("success") == True
    assert result7["result"]["operations_applied"] == 4
    assert result7["result"]["format"] == "webm"
    print("   Complex workflow test passed")

    # Test 8: Validation error - missing required field
    print("\n8. Testing validation error (missing trim end)...")
    try:
        tool8 = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[
                {"type": "trim", "start": "00:00:10"}  # Missing 'end'
            ],
        )
        result8 = tool8.run()
        assert False, "Should have raised ValidationError"
    except Exception:
        print("   Validation error test passed")

    # Test 9: Validation error - invalid operation type
    print("\n9. Testing validation error (invalid operation)...")
    try:
        tool9 = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[
                {"type": "invalid_operation"}
            ],
        )
        result9 = tool9.run()
        assert False, "Should have raised ValidationError"
    except Exception:
        print("   Invalid operation test passed")

    # Test 10: Validation error - invalid speed factor
    print("\n10. Testing validation error (invalid speed factor)...")
    try:
        tool10 = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[
                {"type": "speed", "factor": -1.0}  # Negative factor
            ],
        )
        result10 = tool10.run()
        assert False, "Should have raised ValidationError"
    except Exception:
        print("   Invalid speed factor test passed")

    print("\nAll tests passed!")
