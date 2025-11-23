"""
Precisely transcribe audio to text with word-level timestamps
"""

import json
import os
from typing import Any, Dict, List

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class AudioTranscribe(BaseTool):
    """
    Precisely transcribe audio to text with word-level timestamps

    Args:
        input: Primary input parameter (audio file path or URL)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Transcription data with word-level timestamps
        - metadata: Additional information

    Example:
        >>> tool = AudioTranscribe(input="audio.wav")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "audio_transcribe"
    tool_category: str = "media"

    # Parameters
    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the audio_transcribe tool.

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
                "Input must be a non-empty string representing an audio file path or URL",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        if len(self.input.strip()) == 0:
            raise ValidationError(
                "Input cannot be an empty string",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_words = [
            {"word": "Hello", "start": 0.00, "end": 0.32},
            {"word": "world", "start": 0.33, "end": 0.62},
            {"word": "this", "start": 0.63, "end": 0.81},
            {"word": "is", "start": 0.82, "end": 0.93},
            {"word": "mock", "start": 0.94, "end": 1.13},
            {"word": "audio", "start": 1.14, "end": 1.52},
        ]

        return {
            "success": True,
            "result": {
                "text": "Hello world this is mock audio",
                "words": mock_words,
                "mock": True,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "tool_version": "1.0.0",
            },
        }

    def _process(self) -> Any:
        """Main processing logic."""
        try:
            # Lazy import to avoid dependency cost if unused
            import speech_recognition as sr

            recognizer = sr.Recognizer()

            if self.input.startswith("http://") or self.input.startswith("https://"):
                raise APIError(
                    "URL audio sources are not supported in this implementation",
                    tool_name=self.tool_name,
                )

            if not os.path.exists(self.input):
                raise ValidationError(
                    "Audio file does not exist",
                    tool_name=self.tool_name,
                    details={"input": self.input},
                )

            with sr.AudioFile(self.input) as source:
                audio_data = recognizer.record(source)

            try:
                raw_result = recognizer.recognize_whisper(
                    audio_data, show_dict=True, word_timestamps=True
                )
            except Exception as e:
                raise APIError(
                    f"Speech recognition failed: {e}",
                    tool_name=self.tool_name,
                )

            if isinstance(raw_result, str):
                return {"text": raw_result, "words": []}

            text = raw_result.get("text", "")
            segments = raw_result.get("segments", [])

            words: List[Dict[str, Any]] = []
            for seg in segments:
                for w in seg.get("words", []):
                    words.append(
                        {
                            "word": w.get("word", ""),
                            "start": float(w.get("start", 0.0)),
                            "end": float(w.get("end", 0.0)),
                        }
                    )

            return {
                "text": text,
                "words": words,
            }

        except FileNotFoundError:
            raise ValidationError(
                "Audio file could not be loaded",
                tool_name=self.tool_name,
                details={"input": self.input},
            )
        except Exception as e:
            raise APIError(
                f"Unexpected processing failure: {e}",
                tool_name=self.tool_name,
            )


if __name__ == "__main__":
    print("Testing AudioTranscribe...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test with mock data
    tool = AudioTranscribe(input="https://example.com/audio.mp3")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Text: {result.get('result', {}).get('text')}")
    print(f"Words count: {len(result.get('result', {}).get('words', []))}")
    assert result.get("success") == True
    assert "text" in result.get("result", {})
    print("AudioTranscribe test passed!")
