"""
Apply various visual effects and filters to videos
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import subprocess
import uuid

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class VideoEffects(BaseTool):
    """
    Apply various visual effects and filters to videos.

    Supports multiple effect categories:

    Color Effects:
    - brightness: Adjust brightness (-1.0 to 1.0)
    - contrast: Adjust contrast (-1.0 to 1.0)
    - saturation: Adjust color saturation (-1.0 to 1.0)
    - hue: Shift hue (0-360 degrees)
    - sepia: Apply sepia tone effect
    - grayscale: Convert to black and white
    - invert: Invert colors

    Blur/Sharpen:
    - blur: Apply blur effect (strength: 1-10)
    - sharpen: Sharpen the video (strength: 1-10)
    - motion_blur: Motion blur effect

    Stylistic:
    - vignette: Add vignette darkening around edges
    - vintage: Vintage film look
    - cinematic: Cinematic color grading
    - cartoon: Cartoon/anime style effect
    - edge_detect: Edge detection filter

    Distortion:
    - fisheye: Fisheye lens effect
    - lens_distortion: Lens distortion correction
    - glitch: Digital glitch effect

    Time Effects:
    - slow_motion: Slow down video (0.1-1.0)
    - speed_up: Speed up video (1.0-10.0)
    - reverse: Reverse video playback

    Transitions:
    - fade_in: Fade in from black
    - fade_out: Fade out to black
    - crossfade: Crossfade between clips

    Args:
        input_path: Path to input video file
        effects: List of effect configurations, each containing:
            - type: Effect type
            - parameters: Effect-specific parameters
        output_path: Optional output file path
        output_format: Output format (mp4, mov, avi, webm)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Output file path and effect details
        - metadata: Processing information

    Example:
        >>> tool = VideoEffects(
        ...     input_path="/path/to/video.mp4",
        ...     effects=[
        ...         {"type": "brightness", "parameters": {"value": 0.2}},
        ...         {"type": "saturation", "parameters": {"value": 0.3}},
        ...         {"type": "vignette", "parameters": {"strength": 0.5}}
        ...     ],
        ...     output_format="mp4"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "video_effects"
    tool_category: str = "media"

    # Parameters
    input_path: str = Field(
        ...,
        description="Path to input video file",
        min_length=1
    )
    effects: List[Dict[str, Any]] = Field(
        ...,
        description="List of effect configurations to apply",
        min_length=1
    )
    output_path: Optional[str] = Field(
        default=None,
        description="Output file path (optional)"
    )
    output_format: str = Field(
        default="mp4",
        description="Output format (mp4, mov, avi, webm)"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute video effects processing."""
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
                    "effects_applied": len(self.effects),
                    "input_path": self.input_path,
                    "output_format": self.output_format
                }
            }
        except Exception as e:
            raise APIError(f"Video effects processing failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.input_path or not isinstance(self.input_path, str):
            raise ValidationError(
                "input_path must be a non-empty string",
                tool_name=self.tool_name,
                field="input_path"
            )

        # Check if file exists (skip for mock mode)
        if not os.getenv("USE_MOCK_APIS", "false").lower() == "true":
            if not os.path.isfile(self.input_path):
                raise ValidationError(
                    f"Input video file not found: {self.input_path}",
                    tool_name=self.tool_name,
                    field="input_path"
                )

        # Validate video file extension
        valid_extensions = [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"]
        if not any(self.input_path.lower().endswith(ext) for ext in valid_extensions):
            raise ValidationError(
                f"Unsupported video format. Supported: {valid_extensions}",
                tool_name=self.tool_name,
                field="input_path"
            )

        # Validate effects list
        if not self.effects or not isinstance(self.effects, list):
            raise ValidationError(
                "effects must be a non-empty list",
                tool_name=self.tool_name,
                field="effects"
            )

        # Validate each effect
        valid_effect_types = {
            # Color effects
            "brightness", "contrast", "saturation", "hue", "sepia",
            "grayscale", "invert",
            # Blur/Sharpen
            "blur", "sharpen", "motion_blur",
            # Stylistic
            "vignette", "vintage", "cinematic", "cartoon", "edge_detect",
            # Distortion
            "fisheye", "lens_distortion", "glitch",
            # Time effects
            "slow_motion", "speed_up", "reverse",
            # Transitions
            "fade_in", "fade_out", "crossfade"
        }

        for i, effect in enumerate(self.effects):
            if not isinstance(effect, dict):
                raise ValidationError(
                    f"Effect at index {i} must be a dictionary",
                    tool_name=self.tool_name,
                    field="effects"
                )

            if "type" not in effect:
                raise ValidationError(
                    f"Effect at index {i} missing 'type' field",
                    tool_name=self.tool_name,
                    field="effects"
                )

            if effect["type"] not in valid_effect_types:
                raise ValidationError(
                    f"Invalid effect type '{effect['type']}'. Valid types: {valid_effect_types}",
                    tool_name=self.tool_name,
                    field="effects"
                )

            if "parameters" not in effect:
                effect["parameters"] = {}  # Allow empty parameters

        # Validate output format
        valid_formats = ["mp4", "mov", "avi", "webm"]
        if self.output_format not in valid_formats:
            raise ValidationError(
                f"Invalid output format '{self.output_format}'. Valid formats: {valid_formats}",
                tool_name=self.tool_name,
                field="output_format"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        output_file = self.output_path or self._generate_output_path()

        effects_applied = []
        for effect in self.effects:
            effects_applied.append({
                "type": effect["type"],
                "parameters": effect.get("parameters", {}),
                "status": "applied",
                "mock": True
            })

        return {
            "success": True,
            "result": {
                "input_path": self.input_path,
                "output_path": output_file,
                "output_format": self.output_format,
                "effects_applied": effects_applied,
                "processing_time_seconds": 12.5,
                "mock": True
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "total_effects": len(self.effects)
            }
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic using ffmpeg."""
        try:
            output_file = self.output_path or self._generate_output_path()

            # Build ffmpeg filter chain
            filter_chain = self._build_filter_chain()

            # Execute ffmpeg with filter chain
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output file
                "-i", self.input_path,
                "-vf", filter_chain,
                "-c:a", "copy",  # Copy audio stream
                output_file
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                raise APIError(
                    f"ffmpeg processing failed: {result.stderr}",
                    tool_name=self.tool_name
                )

            effects_applied = [
                {
                    "type": effect["type"],
                    "parameters": effect.get("parameters", {}),
                    "status": "applied"
                }
                for effect in self.effects
            ]

            return {
                "input_path": self.input_path,
                "output_path": output_file,
                "output_format": self.output_format,
                "effects_applied": effects_applied
            }

        except FileNotFoundError:
            raise APIError(
                "ffmpeg is not installed. Please install ffmpeg.",
                tool_name=self.tool_name
            )
        except Exception as e:
            raise APIError(
                f"Video effects processing failed: {e}",
                tool_name=self.tool_name
            )

    def _build_filter_chain(self) -> str:
        """Build ffmpeg video filter chain from effects list."""
        filters = []

        for effect in self.effects:
            effect_type = effect["type"]
            params = effect.get("parameters", {})

            # Color effects
            if effect_type == "brightness":
                value = params.get("value", 0)
                filters.append(f"eq=brightness={value}")

            elif effect_type == "contrast":
                value = params.get("value", 0)
                filters.append(f"eq=contrast={1 + value}")

            elif effect_type == "saturation":
                value = params.get("value", 0)
                filters.append(f"eq=saturation={1 + value}")

            elif effect_type == "hue":
                degrees = params.get("degrees", 0)
                filters.append(f"hue=h={degrees}")

            elif effect_type == "sepia":
                filters.append("colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131")

            elif effect_type == "grayscale":
                filters.append("hue=s=0")

            elif effect_type == "invert":
                filters.append("negate")

            # Blur/Sharpen
            elif effect_type == "blur":
                strength = params.get("strength", 5)
                filters.append(f"boxblur={strength}:{strength}")

            elif effect_type == "sharpen":
                strength = params.get("strength", 5)
                luma = strength / 10
                filters.append(f"unsharp=5:5:{luma}:5:5:0")

            elif effect_type == "motion_blur":
                filters.append("tblend=all_mode=average")

            # Stylistic
            elif effect_type == "vignette":
                strength = params.get("strength", 0.5)
                filters.append(f"vignette=PI/4:{strength}")

            elif effect_type == "vintage":
                filters.append("curves=vintage")

            elif effect_type == "cinematic":
                filters.append("eq=contrast=1.1:brightness=-0.05:saturation=1.2")

            elif effect_type == "cartoon":
                filters.append("edgedetect=low=0.1:high=0.4,negate")

            elif effect_type == "edge_detect":
                filters.append("edgedetect")

            # Distortion
            elif effect_type == "fisheye":
                filters.append("lenscorrection=k1=-0.227:k2=-0.022")

            elif effect_type == "lens_distortion":
                k1 = params.get("k1", 0)
                k2 = params.get("k2", 0)
                filters.append(f"lenscorrection=k1={k1}:k2={k2}")

            elif effect_type == "glitch":
                filters.append("noise=alls=20:allf=t+u")

            # Time effects (handled separately in setpts)
            elif effect_type == "slow_motion":
                speed = params.get("speed", 0.5)
                filters.append(f"setpts={1/speed}*PTS")

            elif effect_type == "speed_up":
                speed = params.get("speed", 2.0)
                filters.append(f"setpts={1/speed}*PTS")

            elif effect_type == "reverse":
                filters.append("reverse")

            # Transitions
            elif effect_type == "fade_in":
                duration = params.get("duration", 1)
                filters.append(f"fade=t=in:st=0:d={duration}")

            elif effect_type == "fade_out":
                duration = params.get("duration", 1)
                start_time = params.get("start_time", 0)
                filters.append(f"fade=t=out:st={start_time}:d={duration}")

        # Join all filters with comma
        return ",".join(filters) if filters else "null"

    def _generate_output_path(self) -> str:
        """Generate output path from input path."""
        base, _ = os.path.splitext(self.input_path)
        return f"{base}_effects.{self.output_format}"


if __name__ == "__main__":
    print("Testing VideoEffects...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test with multiple effects
    tool = VideoEffects(
        input_path="/path/to/test_video.mp4",
        effects=[
            {"type": "brightness", "parameters": {"value": 0.2}},
            {"type": "saturation", "parameters": {"value": 0.3}},
            {"type": "vignette", "parameters": {"strength": 0.5}},
            {"type": "blur", "parameters": {"strength": 3}}
        ],
        output_format="mp4"
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Output path: {result.get('result', {}).get('output_path')}")
    print(f"Effects applied: {len(result.get('result', {}).get('effects_applied', []))}")

    assert result.get("success") == True
    assert "output_path" in result.get("result", {})
    assert len(result.get("result", {}).get("effects_applied", [])) == 4

    print("VideoEffects test passed!")
