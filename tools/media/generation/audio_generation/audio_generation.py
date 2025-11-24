"""
Generate audio: TTS, sound effects, music, voice cloning, songs using LiteLLM
"""

import os
import uuid
from typing import Any, Dict, Optional

from pydantic import Field

from shared.analytics import AnalyticsEvent, EventType, record_event
from shared.base import BaseTool
from shared.errors import APIError, ValidationError
from shared.llm_client import LLMResponse, get_llm_client


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
    tool_description: str = "Generate audio: TTS, sound effects, music, voice cloning, songs"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate", min_length=1)
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )
    model: Optional[str] = Field(
        None, description="TTS model to use (uses LiteLLM for text-to-speech)"
    )
    fallback_models: Optional[list] = Field(
        None, description="List of fallback TTS models if primary fails"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the audio_generation tool.

        Returns:
            Dict with results
        """

        self._logger.info(f"Executing {self.tool_name} with prompt={self.prompt}, params={self.params}, model={self.model}, fallback_models={self.fallback_models}")
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "params_used": self.params},
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
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
        Main processing logic using LiteLLM for TTS.

        Note: For TTS, we use chat completion to generate the text,
        then would integrate with a TTS provider. This is a simplified
        implementation showing the cost tracking pattern.

        Returns:
            Dict with generated audio metadata

        Raises:
            APIError: When audio generation fails
        """
        try:
            # Get LiteLLM client
            client = get_llm_client()

            # For TTS, we might first process the text with an LLM
            # to optimize it for speech synthesis
            model = self.model or "gpt-3.5-turbo"
            fallback = self.fallback_models or ["claude-3-haiku-20240307"]

            # Optimize text for TTS (optional preprocessing)
            messages = [
                {
                    "role": "user",
                    "content": f"Optimize this text for text-to-speech, ensuring it's clear and natural: {self.prompt}",
                }
            ]

            response: LLMResponse = client.chat_completion(
                messages=messages, model=model, fallback_models=fallback, max_tokens=500
            )

            # Record cost event for LLM preprocessing
            record_event(
                AnalyticsEvent(
                    event_type=EventType.LLM_COST,
                    tool_name=self.tool_name,
                    success=True,
                    metadata={
                        "model": response.model,
                        "provider": response.provider,
                        "cost": response.cost,
                        "total_tokens": response.usage.get("total_tokens", 0),
                        "task_type": "audio_generation_preprocessing",
                    },
                )
            )

            # Simulated TTS API call (in production, would call actual TTS service)
            audio_id = str(uuid.uuid4())
            audio_url = f"https://audio.example.com/generated/{audio_id}.wav"

            return {
                "audio_id": audio_id,
                "audio_url": audio_url,
                "prompt_used": self.prompt,
                "optimized_text": response.content,
                "preprocessing_model": response.model,
                "preprocessing_cost": response.cost,
                "parameters_used": self.params,
            }

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Audio generation failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the audio_generation tool
    print("Testing AudioGeneration tool...")

    # Test with mock mode
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = AudioGeneration(prompt="calm piano music", params={"voice": "female", "duration": 30})
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Audio URL: {result.get('result', {}).get('audio_url')}")
    print(f"Audio ID: {result.get('result', {}).get('audio_id')}")
