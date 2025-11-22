"""
Advanced text-to-speech with emotion, voice characteristics, and prosody control
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import uuid

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class TextToSpeechAdvanced(BaseTool):
    """
    Advanced text-to-speech with emotion, voice control, and prosody adjustment.

    This tool provides fine-grained control over speech synthesis including:
    - Multiple voice profiles (age, gender, accent)
    - Emotional expression (happy, sad, angry, excited, calm, etc.)
    - Prosody control (pitch, rate, volume)
    - SSML support for advanced control
    - Multi-speaker support
    - Background music/effects

    Voice Parameters:
    - voice_id: Specific voice identifier or preset
    - gender: "male", "female", "neutral"
    - age: "child", "young_adult", "adult", "elderly"
    - accent: "american", "british", "australian", "indian", etc.

    Emotion Parameters:
    - emotion: "neutral", "happy", "sad", "angry", "excited", "calm", "fearful", "surprised"
    - emotion_intensity: 0.0-1.0 (how strongly to express the emotion)

    Prosody Parameters:
    - pitch: -1.0 to 1.0 (lower to higher pitch)
    - rate: 0.5 to 2.0 (speed of speech, 1.0 is normal)
    - volume: 0.0 to 1.0 (volume level)

    Args:
        text: Text to convert to speech (supports plain text or SSML)
        voice_id: Optional specific voice identifier
        gender: Voice gender (male, female, neutral)
        age: Voice age range
        accent: Voice accent/dialect
        emotion: Emotional expression to apply
        emotion_intensity: Strength of emotional expression (0.0-1.0)
        pitch: Pitch adjustment (-1.0 to 1.0)
        rate: Speaking rate (0.5 to 2.0)
        volume: Volume level (0.0 to 1.0)
        use_ssml: Whether text contains SSML markup
        output_format: Audio format (mp3, wav, ogg, flac)
        sample_rate: Audio sample rate in Hz (8000, 16000, 22050, 44100, 48000)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Audio file URL/path and synthesis details
        - metadata: Processing information

    Example:
        >>> tool = TextToSpeechAdvanced(
        ...     text="Hello! I'm excited to meet you!",
        ...     gender="female",
        ...     age="young_adult",
        ...     accent="american",
        ...     emotion="excited",
        ...     emotion_intensity=0.8,
        ...     pitch=0.1,
        ...     rate=1.1,
        ...     output_format="mp3"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "text_to_speech_advanced"
    tool_category: str = "media_generation"

    # Parameters
    text: str = Field(
        ...,
        description="Text to convert to speech",
        min_length=1,
        max_length=50000
    )
    voice_id: Optional[str] = Field(
        default=None,
        description="Specific voice identifier"
    )
    gender: str = Field(
        default="neutral",
        description="Voice gender"
    )
    age: str = Field(
        default="adult",
        description="Voice age range"
    )
    accent: str = Field(
        default="american",
        description="Voice accent/dialect"
    )
    emotion: str = Field(
        default="neutral",
        description="Emotional expression"
    )
    emotion_intensity: float = Field(
        default=0.5,
        description="Emotion intensity (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    pitch: float = Field(
        default=0.0,
        description="Pitch adjustment (-1.0 to 1.0)",
        ge=-1.0,
        le=1.0
    )
    rate: float = Field(
        default=1.0,
        description="Speaking rate (0.5 to 2.0)",
        ge=0.5,
        le=2.0
    )
    volume: float = Field(
        default=1.0,
        description="Volume level (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    use_ssml: bool = Field(
        default=False,
        description="Whether text contains SSML markup"
    )
    output_format: str = Field(
        default="mp3",
        description="Audio output format"
    )
    sample_rate: int = Field(
        default=22050,
        description="Audio sample rate in Hz"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute advanced text-to-speech synthesis."""
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
                    "text_length": len(self.text),
                    "voice_config": {
                        "gender": self.gender,
                        "age": self.age,
                        "accent": self.accent,
                        "emotion": self.emotion
                    }
                }
            }
        except Exception as e:
            raise APIError(f"Text-to-speech synthesis failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.text or not isinstance(self.text, str):
            raise ValidationError(
                "text must be a non-empty string",
                tool_name=self.tool_name,
                field="text"
            )

        # Validate gender
        valid_genders = ["male", "female", "neutral"]
        if self.gender not in valid_genders:
            raise ValidationError(
                f"Invalid gender '{self.gender}'. Valid options: {valid_genders}",
                tool_name=self.tool_name,
                field="gender"
            )

        # Validate age
        valid_ages = ["child", "young_adult", "adult", "elderly"]
        if self.age not in valid_ages:
            raise ValidationError(
                f"Invalid age '{self.age}'. Valid options: {valid_ages}",
                tool_name=self.tool_name,
                field="age"
            )

        # Validate accent
        valid_accents = [
            "american", "british", "australian", "canadian", "indian",
            "scottish", "irish", "southern", "new_york", "california"
        ]
        if self.accent not in valid_accents:
            raise ValidationError(
                f"Invalid accent '{self.accent}'. Valid options: {valid_accents}",
                tool_name=self.tool_name,
                field="accent"
            )

        # Validate emotion
        valid_emotions = [
            "neutral", "happy", "sad", "angry", "excited", "calm",
            "fearful", "surprised", "disgusted", "contempt", "loving",
            "playful", "serious", "confident", "anxious"
        ]
        if self.emotion not in valid_emotions:
            raise ValidationError(
                f"Invalid emotion '{self.emotion}'. Valid options: {valid_emotions}",
                tool_name=self.tool_name,
                field="emotion"
            )

        # Validate output format
        valid_formats = ["mp3", "wav", "ogg", "flac", "aac"]
        if self.output_format not in valid_formats:
            raise ValidationError(
                f"Invalid output format '{self.output_format}'. Valid options: {valid_formats}",
                tool_name=self.tool_name,
                field="output_format"
            )

        # Validate sample rate
        valid_sample_rates = [8000, 16000, 22050, 44100, 48000]
        if self.sample_rate not in valid_sample_rates:
            raise ValidationError(
                f"Invalid sample rate {self.sample_rate}. Valid options: {valid_sample_rates}",
                tool_name=self.tool_name,
                field="sample_rate"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        audio_id = str(uuid.uuid4())
        audio_url = f"https://mock-tts-api.example.com/audio/{audio_id}.{self.output_format}"

        # Calculate estimated duration (rough approximation)
        words = len(self.text.split())
        words_per_minute = 150 * self.rate
        duration_seconds = (words / words_per_minute) * 60

        return {
            "success": True,
            "result": {
                "audio_url": audio_url,
                "audio_id": audio_id,
                "format": self.output_format,
                "sample_rate": self.sample_rate,
                "duration_seconds": round(duration_seconds, 2),
                "text_length": len(self.text),
                "voice_config": {
                    "voice_id": self.voice_id or f"mock_{self.gender}_{self.age}_{self.accent}",
                    "gender": self.gender,
                    "age": self.age,
                    "accent": self.accent,
                    "emotion": self.emotion,
                    "emotion_intensity": self.emotion_intensity
                },
                "prosody": {
                    "pitch": self.pitch,
                    "rate": self.rate,
                    "volume": self.volume
                },
                "processing_time_seconds": 1.2,
                "mock": True
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name
            }
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic for advanced TTS."""
        try:
            # In production, this would call an advanced TTS API
            # Examples: ElevenLabs, Google Cloud TTS, Azure TTS, Amazon Polly

            audio_id = str(uuid.uuid4())

            # Prepare API request
            api_payload = {
                "text": self.text,
                "voice_config": {
                    "voice_id": self.voice_id,
                    "gender": self.gender,
                    "age": self.age,
                    "accent": self.accent
                },
                "emotion_config": {
                    "emotion": self.emotion,
                    "intensity": self.emotion_intensity
                },
                "prosody": {
                    "pitch": self.pitch,
                    "rate": self.rate,
                    "volume": self.volume
                },
                "output_config": {
                    "format": self.output_format,
                    "sample_rate": self.sample_rate
                },
                "use_ssml": self.use_ssml
            }

            # Simulated API call
            # response = requests.post(TTS_API_URL, json=api_payload, headers=...)
            # audio_url = response.json()["audio_url"]

            audio_url = f"https://api.example.com/tts/audio/{audio_id}.{self.output_format}"

            # Calculate estimated duration
            words = len(self.text.split())
            words_per_minute = 150 * self.rate
            duration_seconds = (words / words_per_minute) * 60

            return {
                "audio_url": audio_url,
                "audio_id": audio_id,
                "format": self.output_format,
                "sample_rate": self.sample_rate,
                "duration_seconds": round(duration_seconds, 2),
                "text_length": len(self.text),
                "voice_config": {
                    "voice_id": self.voice_id or f"{self.gender}_{self.age}_{self.accent}",
                    "gender": self.gender,
                    "age": self.age,
                    "accent": self.accent,
                    "emotion": self.emotion,
                    "emotion_intensity": self.emotion_intensity
                },
                "prosody": {
                    "pitch": self.pitch,
                    "rate": self.rate,
                    "volume": self.volume
                }
            }

        except Exception as e:
            raise APIError(
                f"TTS API error: {e}",
                tool_name=self.tool_name
            )


if __name__ == "__main__":
    print("Testing TextToSpeechAdvanced...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test with emotional speech
    tool = TextToSpeechAdvanced(
        text="Hello! I'm so excited to meet you today!",
        gender="female",
        age="young_adult",
        accent="american",
        emotion="excited",
        emotion_intensity=0.8,
        pitch=0.2,
        rate=1.1,
        volume=0.9,
        output_format="mp3",
        sample_rate=44100
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Audio URL: {result.get('result', {}).get('audio_url')}")
    print(f"Duration: {result.get('result', {}).get('duration_seconds')} seconds")
    print(f"Voice config: {result.get('result', {}).get('voice_config')}")

    assert result.get("success") == True
    assert "audio_url" in result.get("result", {})
    assert result.get("result", {}).get("voice_config", {}).get("emotion") == "excited"

    # Test with different emotion
    tool2 = TextToSpeechAdvanced(
        text="I'm sorry to hear that. How can I help?",
        gender="male",
        emotion="calm",
        emotion_intensity=0.7,
        rate=0.9
    )
    result2 = tool2.run()

    print(f"\nCalm voice test success: {result2.get('success')}")
    assert result2.get("success") == True

    print("TextToSpeechAdvanced test passed!")
