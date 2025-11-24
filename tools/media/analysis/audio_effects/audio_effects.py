"""
Apply various audio effects like reverb, echo, EQ, compression, normalization
"""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class AudioEffects(BaseTool):
    """
    Apply various audio effects to audio files.

    Supports multiple effects:
    - reverb: Add reverb/echo effect
    - echo: Add echo/delay effect
    - eq: Equalization (bass, treble, mid adjustment)
    - normalize: Volume normalization
    - compress: Dynamic range compression
    - pitch_shift: Change pitch without affecting tempo
    - tempo_change: Change tempo without affecting pitch
    - fade_in: Fade in at the beginning
    - fade_out: Fade out at the end
    - noise_reduction: Reduce background noise

    Args:
        input_path: Path to input audio file
        effects: List of effect configurations, each containing:
            - type: Effect type (reverb, echo, eq, normalize, etc.)
            - parameters: Dict of effect-specific parameters
        output_path: Optional output file path (defaults to input_path with _processed suffix)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Output file path and effect details
        - metadata: Processing information

    Example:
        >>> tool = AudioEffects(
        ...     input_path="/path/to/audio.wav",
        ...     effects=[
        ...         {"type": "normalize", "parameters": {"target_level": -3}},
        ...         {"type": "reverb", "parameters": {"room_size": 0.5, "damping": 0.3}},
        ...         {"type": "eq", "parameters": {"bass": 2, "treble": -1}}
        ...     ]
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "audio_effects"
    tool_category: str = "media"

    # Parameters
    input_path: str = Field(..., description="Path to input audio file", min_length=1)
    effects: List[Dict[str, Any]] = Field(
        ..., description="List of effect configurations to apply", min_length=1
    )
    output_path: Optional[str] = Field(default=None, description="Output file path (optional)")

    def _execute(self) -> Dict[str, Any]:
        """Execute audio effects processing."""

        self._logger.info(f"Executing {self.tool_name} with input_path={self.input_path}, effects={self.effects}, output_path={self.output_path}")
        self._validate_parameters()

        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        try:
            result = self._process()
            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "effects_applied": len(self.effects),
                    "input_path": self.input_path,
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Audio effects processing failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.input_path or not isinstance(self.input_path, str):
            raise ValidationError(
                "input_path must be a non-empty string",
                tool_name=self.tool_name,
                field="input_path",
            )

        # Check if file exists (skip for mock mode)
        if not os.getenv("USE_MOCK_APIS", "false").lower() == "true":
            if not os.path.isfile(self.input_path):
                raise ValidationError(
                    f"Input audio file not found: {self.input_path}",
                    tool_name=self.tool_name,
                    field="input_path",
                )

        # Validate audio file extension
        valid_extensions = [".wav", ".mp3", ".flac", ".aac", ".m4a", ".ogg", ".wma"]
        if not any(self.input_path.lower().endswith(ext) for ext in valid_extensions):
            raise ValidationError(
                f"Unsupported audio format. Supported: {valid_extensions}",
                tool_name=self.tool_name,
                field="input_path",
            )

        # Validate effects list
        if not self.effects or not isinstance(self.effects, list):
            raise ValidationError(
                "effects must be a non-empty list", tool_name=self.tool_name, field="effects"
            )

        # Validate each effect
        valid_effect_types = {
            "reverb",
            "echo",
            "eq",
            "normalize",
            "compress",
            "pitch_shift",
            "tempo_change",
            "fade_in",
            "fade_out",
            "noise_reduction",
        }

        for i, effect in enumerate(self.effects):
            if not isinstance(effect, dict):
                raise ValidationError(
                    f"Effect at index {i} must be a dictionary",
                    tool_name=self.tool_name,
                    field="effects",
                )

            if "type" not in effect:
                raise ValidationError(
                    f"Effect at index {i} missing 'type' field",
                    tool_name=self.tool_name,
                    field="effects",
                )

            if effect["type"] not in valid_effect_types:
                raise ValidationError(
                    f"Invalid effect type '{effect['type']}'. Valid types: {valid_effect_types}",
                    tool_name=self.tool_name,
                    field="effects",
                )

            if "parameters" not in effect:
                raise ValidationError(
                    f"Effect at index {i} missing 'parameters' field",
                    tool_name=self.tool_name,
                    field="effects",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        output_file = self.output_path or self._generate_output_path()

        effects_applied = []
        for effect in self.effects:
            effects_applied.append(
                {
                    "type": effect["type"],
                    "parameters": effect.get("parameters", {}),
                    "status": "applied",
                    "mock": True,
                }
            )

        return {
            "success": True,
            "result": {
                "input_path": self.input_path,
                "output_path": output_file,
                "effects_applied": effects_applied,
                "processing_time_seconds": 2.5,
                "mock": True,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "total_effects": len(self.effects),
            },
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
                "-i",
                self.input_path,
                "-af",
                filter_chain,
                output_file,
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                raise APIError(
                    f"ffmpeg processing failed: {result.stderr}", tool_name=self.tool_name
                )

            effects_applied = [
                {
                    "type": effect["type"],
                    "parameters": effect.get("parameters", {}),
                    "status": "applied",
                }
                for effect in self.effects
            ]

            return {
                "input_path": self.input_path,
                "output_path": output_file,
                "effects_applied": effects_applied,
            }

        except FileNotFoundError:
            raise APIError(
                "ffmpeg is not installed. Please install ffmpeg.", tool_name=self.tool_name
            )
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Audio effects processing failed: {e}", tool_name=self.tool_name)

    def _build_filter_chain(self) -> str:
        """Build ffmpeg audio filter chain from effects list."""
        filters = []

        for effect in self.effects:
            effect_type = effect["type"]
            params = effect.get("parameters", {})

            if effect_type == "reverb":
                # Simple reverb using aecho
                filters.append(
                    f"aecho=0.8:0.9:{params.get('delay', 60)}:{params.get('decay', 0.5)}"
                )

            elif effect_type == "echo":
                delay = params.get("delay", 500)
                decay = params.get("decay", 0.6)
                filters.append(f"aecho=0.8:0.88:{delay}:{decay}")

            elif effect_type == "eq":
                # Bass, mid, treble adjustment
                bass = params.get("bass", 0)
                mid = params.get("mid", 0)
                treble = params.get("treble", 0)
                filters.append(f"equalizer=f=100:t=h:width=200:g={bass}")
                filters.append(f"equalizer=f=1000:t=h:width=200:g={mid}")
                filters.append(f"equalizer=f=10000:t=h:width=200:g={treble}")

            elif effect_type == "normalize":
                target_level = params.get("target_level", -3)
                filters.append(f"loudnorm=I={target_level}")

            elif effect_type == "compress":
                threshold = params.get("threshold", -20)
                ratio = params.get("ratio", 4)
                filters.append(f"acompressor=threshold={threshold}dB:ratio={ratio}")

            elif effect_type == "pitch_shift":
                semitones = params.get("semitones", 0)
                if semitones != 0:
                    filters.append(f"asetrate=44100*2^({semitones}/12),aresample=44100")

            elif effect_type == "tempo_change":
                tempo = params.get("tempo", 1.0)
                filters.append(f"atempo={tempo}")

            elif effect_type == "fade_in":
                duration = params.get("duration", 2)
                filters.append(f"afade=t=in:st=0:d={duration}")

            elif effect_type == "fade_out":
                duration = params.get("duration", 2)
                start_time = params.get("start_time", 0)
                filters.append(f"afade=t=out:st={start_time}:d={duration}")

            elif effect_type == "noise_reduction":
                # Simple high-pass filter for noise reduction
                cutoff = params.get("cutoff_frequency", 100)
                filters.append(f"highpass=f={cutoff}")

        # Join all filters with comma
        return ",".join(filters) if filters else "anull"

    def _generate_output_path(self) -> str:
        """Generate output path from input path."""
        base, ext = os.path.splitext(self.input_path)
        return f"{base}_processed{ext}"


if __name__ == "__main__":
    print("Testing AudioEffects...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test with mock data
    tool = AudioEffects(
        input_path="/path/to/test_audio.wav",
        effects=[
            {"type": "normalize", "parameters": {"target_level": -3}},
            {"type": "reverb", "parameters": {"delay": 60, "decay": 0.5}},
            {"type": "eq", "parameters": {"bass": 2, "mid": 0, "treble": -1}},
        ],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Output path: {result.get('result', {}).get('output_path')}")
    print(f"Effects applied: {len(result.get('result', {}).get('effects_applied', []))}")

    assert result.get("success") == True
    assert "output_path" in result.get("result", {})
    assert len(result.get("result", {}).get("effects_applied", [])) == 3

    print("AudioEffects test passed!")
