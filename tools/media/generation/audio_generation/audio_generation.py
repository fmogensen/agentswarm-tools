"""
Generate audio: TTS, sound effects, music, voice cloning, songs
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os
import uuid

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class AudioGeneration(BaseTool):
    """
    Generate audio: TTS, sound effects, music, voice cloning, songs

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = AudioGeneration(prompt="example", params={"voice": "female"})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "audio_generation"
    tool_category: str = "media"
    tool_description: str = (
        "Generate audio: TTS, sound effects, music, voice cloning, songs"
    )

    # Parameters
    prompt: str = Field(
        ..., description="Description of what to generate", min_length=1
    )
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the audio_generation tool.

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
                "metadata": {"tool_name": self.tool_name, "params_used": self.params},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If prompt or params are invalid
        """
        if not self.prompt or not isinstance(self.prompt, str):
            raise ValidationError(
                "Prompt must be a non-empty string",
                tool_name=self.tool_name,
                details={"prompt": self.prompt},
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be a dictionary",
                tool_name=self.tool_name,
                details={"params": self.params},
            )

        # Optional additional checks
        allowed_keys = {"voice", "duration", "style", "format", "seed", "model"}
        for key in self.params.keys():
            if key not in allowed_keys:
                raise ValidationError(
                    f"Invalid parameter key: {key}",
                    tool_name=self.tool_name,
                    details={"invalid_key": key},
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        fake_audio_id = str(uuid.uuid4())
        fake_url = f"https://mock-audio.example.com/{fake_audio_id}.wav"

        return {
            "success": True,
            "result": {
                "audio_url": fake_url,
                "audio_id": fake_audio_id,
                "mock": True,
                "prompt_used": self.prompt,
                "parameters_used": self.params,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "params_used": self.params,
            },
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Simulates an audio-generation API call.

        Returns:
            Dict with generated audio metadata

        Raises:
            APIError: When audio generation fails
        """
        try:
            # Simulated generation process
            audio_id = str(uuid.uuid4())
            audio_url = f"https://audio.example.com/generated/{audio_id}.wav"

            return {
                "audio_id": audio_id,
                "audio_url": audio_url,
                "prompt_used": self.prompt,
                "parameters_used": self.params,
            }

        except Exception as e:
            raise APIError(f"Audio generation failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the audio_generation tool
    print("Testing AudioGeneration tool...")

    # Test with mock mode
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = AudioGeneration(
        prompt="calm piano music",
        params={"voice": "female", "duration": 30}
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Audio URL: {result.get('result', {}).get('audio_url')}")
    print(f"Audio ID: {result.get('result', {}).get('audio_id')}")
