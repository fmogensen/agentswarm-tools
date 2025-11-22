"""
Merge multiple audio clips into one file with positioning and effects
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import json
from io import BytesIO

from shared.base import BaseTool
from shared.errors import ValidationError, APIError

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None


class MergeAudio(BaseTool):
    """
    Merge multiple audio clips into one file with positioning and effects.

    The `input` parameter must be a JSON string containing:
    - clips: List of dict items, each containing:
        - path: Path to audio file
        - start: Start position in milliseconds
        - gain: Optional gain adjustment in dB

    Example input:
    {
        "clips": [
            {"path": "audio1.mp3", "start": 0, "gain": -2},
            {"path": "audio2.wav", "start": 5000}
        ],
        "output_format": "mp3"
    }

    Args:
        input: Primary input parameter (JSON string)

    Returns:
        Dict containing:
        - success: Boolean
        - result: Path or binary output
        - metadata: Dict with details
    """

    tool_name: str = "merge_audio"
    tool_category: str = "media"

    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the merge_audio tool.

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
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.input or not isinstance(self.input, str):
            raise ValidationError(
                "Parameter 'input' must be a non-empty JSON string",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        try:
            parsed = json.loads(self.input)
        except Exception:
            raise ValidationError(
                "Parameter 'input' must be valid JSON", tool_name=self.tool_name
            )

        if "clips" not in parsed or not isinstance(parsed["clips"], list):
            raise ValidationError(
                "Input JSON must contain a 'clips' list", tool_name=self.tool_name
            )

        for clip in parsed["clips"]:
            if "path" not in clip or not isinstance(clip["path"], str):
                raise ValidationError(
                    "Each clip must include a string 'path'",
                    tool_name=self.tool_name,
                    details={"clip": clip},
                )
            if "start" in clip and not isinstance(clip["start"], int):
                raise ValidationError(
                    "'start' must be an integer (milliseconds)",
                    tool_name=self.tool_name,
                    details={"clip": clip},
                )
            if "gain" in clip and not isinstance(clip["gain"], (int, float)):
                raise ValidationError(
                    "'gain' must be numeric (dB)",
                    tool_name=self.tool_name,
                    details={"clip": clip},
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {"mock": True, "message": "Audio merged successfully (mock)"},
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        if AudioSegment is None:
            raise APIError(
                "pydub library is required for audio merging. Install with: pip install pydub",
                tool_name=self.tool_name,
            )

        data = json.loads(self.input)
        clips = data.get("clips", [])
        output_format = data.get("output_format", "mp3")

        if not clips:
            raise ValidationError("No audio clips provided", tool_name=self.tool_name)

        # Determine the required total duration
        max_end = 0
        loaded = []

        for clip in clips:
            try:
                audio = AudioSegment.from_file(clip["path"])
            except Exception as e:
                raise APIError(
                    f"Failed to load audio file {clip['path']}: {e}",
                    tool_name=self.tool_name,
                )

            start = clip.get("start", 0)
            gain = clip.get("gain", None)

            if gain is not None:
                audio = audio.apply_gain(gain)

            end = start + len(audio)
            if end > max_end:
                max_end = end

            loaded.append((audio, start))

        # Create output container
        output = AudioSegment.silent(duration=max_end)

        # Overlay audio clips
        for audio, start in loaded:
            output = output.overlay(audio, position=start)

        # Export to bytes
        buffer = BytesIO()
        output.export(buffer, format=output_format)
        buffer.seek(0)

        return {
            "audio_bytes": buffer.read(),
            "format": output_format,
            "duration_ms": max_end,
        }


if __name__ == "__main__":
    print("Testing MergeAudio...")

    import os
    import json

    os.environ["USE_MOCK_APIS"] = "true"

    # Test with mock data
    test_input = json.dumps(
        {
            "clips": [
                {"path": "audio1.mp3", "start": 0, "gain": -2},
                {"path": "audio2.wav", "start": 5000},
            ],
            "output_format": "mp3",
        }
    )

    tool = MergeAudio(input=test_input)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Result: {result.get('result')}")
    assert result.get("success") == True
    assert "message" in result.get("result", {}) or "mock" in result.get("result", {})
    print("MergeAudio test passed!")
