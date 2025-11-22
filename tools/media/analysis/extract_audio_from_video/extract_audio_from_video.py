"""
Extract audio track from video files to MP3
"""

from typing import Any, Dict
from pydantic import Field
import os
import subprocess

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class ExtractAudioFromVideo(BaseTool):
    """
    Extract audio track from video files to MP3

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = ExtractAudioFromVideo(input="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "extract_audio_from_video"
    tool_category: str = "media"
    tool_description: str = "Extract audio track from video files to MP3"

    # Parameters
    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the extract_audio_from_video tool.

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
                "metadata": {"tool_name": self.tool_name, "tool_version": "1.0.0"},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.input or not isinstance(self.input, str):
            raise ValidationError(
                "Input must be a non-empty string",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        if not os.path.isfile(self.input):
            raise ValidationError(
                "Input video file does not exist",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        valid_ext = [".mp4", ".mov", ".mkv", ".avi", ".webm"]
        if not any(self.input.lower().endswith(ext) for ext in valid_ext):
            raise ValidationError(
                "Input must be a valid video file",
                tool_name=self.tool_name,
                details={"allowed_extensions": valid_ext},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        output_path = self.input + ".mock_audio.mp3"
        return {
            "success": True,
            "result": {"output_file": output_path, "mock": True},
            "metadata": {"mock_mode": True, "tool_version": "1.0.0"},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        try:
            base, _ = os.path.splitext(self.input)
            output_file = f"{base}.mp3"

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                self.input,
                "-vn",
                "-acodec",
                "mp3",
                output_file,
            ]

            process = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if process.returncode != 0:
                raise APIError(
                    f"FFmpeg failed: {process.stderr}", tool_name=self.tool_name
                )

            return {"output_file": output_file}

        except FileNotFoundError:
            raise APIError(
                "FFmpeg is not installed or not found in PATH", tool_name=self.tool_name
            )
        except Exception as e:
            raise APIError(f"Unexpected error: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    print("Testing ExtractAudioFromVideo...")

    import os
    import tempfile

    os.environ["USE_MOCK_APIS"] = "true"

    # Create a temporary test file for validation
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        tool = ExtractAudioFromVideo(input=tmp_path)
        result = tool.run()

        print(f"Success: {result.get('success')}")
        print(f"Result: {result.get('result')}")
        assert result.get("success") == True
        assert "output_file" in result.get("result", {})
        print("ExtractAudioFromVideo test passed!")
    finally:
        # Cleanup
        import os as os_mod
        if os_mod.path.exists(tmp_path):
            os_mod.remove(tmp_path)
