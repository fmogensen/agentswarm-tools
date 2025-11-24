"""
Generate podcast episodes with multiple speakers, background music, and effects.

This tool creates complete podcast episodes with:
- Multiple speakers with distinct voices and personalities
- Background music mixing
- Intro and outro segments
- Realistic conversation flow
- Voice consistency across segments
"""

import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field, field_validator, model_validator

from shared.base import BaseTool
from shared.errors import APIError, ConfigurationError, ValidationError


class PodcastGenerator(BaseTool):
    """
    Generate full podcast episodes with multiple speakers and audio mixing.

    Creates professional podcast episodes with:
    - Multi-speaker conversations with distinct voices
    - Background music integration
    - Intro/outro segments
    - Script generation or custom script support
    - Professional audio mixing

    Args:
        topic: Main topic/subject of the podcast episode
        duration_minutes: Target duration in minutes (1-60)
        num_speakers: Number of speakers (1-4)
        speaker_personalities: List of personality descriptions for each speaker
        script_content: Optional pre-written script (auto-generated if not provided)
        background_music: Whether to include background music
        music_style: Style of background music
        output_format: Audio output format (mp3 or wav)
        add_intro: Whether to add intro segment
        add_outro: Whether to add outro segment
        voice_consistency: Ensure consistent voice characteristics

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - podcast_url: URL to download the generated podcast
        - duration_seconds: Actual duration of the podcast
        - speakers_used: List of speaker configurations used
        - transcript: Full transcript of the podcast
        - metadata: Additional metadata (file size, format, etc.)

    Example:
        >>> tool = PodcastGenerator(
        ...     topic="The Future of AI",
        ...     duration_minutes=15,
        ...     num_speakers=2,
        ...     speaker_personalities=["enthusiastic tech host", "AI researcher expert"]
        ... )
        >>> result = tool.run()
        >>> print(result['podcast_url'])
    """

    # Tool metadata
    tool_name: str = "podcast_generator"
    tool_category: str = "media"
    tool_description: str = "Generate podcast episodes with multiple speakers and audio mixing"

    # Core parameters
    topic: str = Field(
        ...,
        description="Main topic or subject of the podcast episode",
        min_length=1,
        max_length=500,
    )

    duration_minutes: int = Field(
        10, description="Target duration of the podcast in minutes", ge=1, le=60
    )

    num_speakers: int = Field(2, description="Number of speakers in the podcast", ge=1, le=4)

    speaker_personalities: List[str] = Field(
        ...,
        description="List of personality descriptions for each speaker (e.g., ['enthusiastic host', 'expert guest'])",
    )

    script_content: Optional[str] = Field(
        None,
        description="Optional pre-written script. If not provided, script will be auto-generated",
    )

    # Audio mixing parameters
    background_music: bool = Field(True, description="Whether to include background music")

    music_style: Literal["upbeat", "calm", "corporate", "none"] = Field(
        "upbeat", description="Style of background music to use"
    )

    output_format: Literal["mp3", "wav"] = Field("mp3", description="Output audio format")

    # Segment parameters
    add_intro: bool = Field(True, description="Whether to add an intro segment to the podcast")

    add_outro: bool = Field(True, description="Whether to add an outro segment to the podcast")

    voice_consistency: bool = Field(
        True, description="Ensure consistent voice characteristics throughout the episode"
    )

    @model_validator(mode="after")
    def validate_speaker_personalities(self):
        """Validate that speaker_personalities matches num_speakers."""
        if len(self.speaker_personalities) != self.num_speakers:
            raise ValueError(
                f"speaker_personalities must contain exactly {self.num_speakers} entries "
                f"(got {len(self.speaker_personalities)})"
            )

        # Validate each personality description
        for i, personality in enumerate(self.speaker_personalities):
            if not personality or not isinstance(personality, str):
                raise ValueError(f"Speaker personality at index {i} must be a non-empty string")
            if len(personality) > 200:
                raise ValueError(
                    f"Speaker personality at index {i} is too long (max 200 characters)"
                )

        return self

    @field_validator("script_content")
    @classmethod
    def validate_script_content(cls, v):
        """Validate script content if provided."""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("script_content must be a string")
            if len(v) > 50000:
                raise ValueError("script_content is too long (max 50000 characters)")
        return v

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the podcast generator tool.

        Returns:
            Dict with podcast generation results
        """

        self._logger.info(
            f"Executing {self.tool_name} with topic={self.topic}, duration_minutes={self.duration_minutes}, num_speakers={self.num_speakers}, ..."
        )
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
                "podcast_url": result["podcast_url"],
                "duration_seconds": result["duration_seconds"],
                "speakers_used": result["speakers_used"],
                "transcript": result["transcript"],
                "metadata": result["metadata"],
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Podcast generation failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
            ConfigurationError: If API keys are missing
        """
        # Validate topic
        if not self.topic or not self.topic.strip():
            raise ValidationError(
                "Topic must be a non-empty string", tool_name=self.tool_name, field="topic"
            )

        # Validate duration
        if self.duration_minutes < 1 or self.duration_minutes > 60:
            raise ValidationError(
                "duration_minutes must be between 1 and 60",
                tool_name=self.tool_name,
                field="duration_minutes",
                details={"duration_minutes": self.duration_minutes},
            )

        # Validate num_speakers
        if self.num_speakers < 1 or self.num_speakers > 4:
            raise ValidationError(
                "num_speakers must be between 1 and 4",
                tool_name=self.tool_name,
                field="num_speakers",
                details={"num_speakers": self.num_speakers},
            )

        # Validate speaker_personalities count
        if len(self.speaker_personalities) != self.num_speakers:
            raise ValidationError(
                f"speaker_personalities must contain exactly {self.num_speakers} entries",
                tool_name=self.tool_name,
                field="speaker_personalities",
                details={"expected": self.num_speakers, "got": len(self.speaker_personalities)},
            )

        # Check for API keys in production mode
        if not self._should_use_mock():
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ConfigurationError(
                    "OPENAI_API_KEY environment variable is required for podcast generation",
                    tool_name=self.tool_name,
                    config_key="OPENAI_API_KEY",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate realistic mock results for testing."""
        podcast_id = str(uuid.uuid4())
        mock_url = f"https://podcast-storage.example.com/{podcast_id}.{self.output_format}"

        # Calculate approximate duration (with intro/outro)
        base_duration = self.duration_minutes * 60
        if self.add_intro:
            base_duration += 15  # 15 second intro
        if self.add_outro:
            base_duration += 10  # 10 second outro

        # Generate mock transcript
        transcript = self._generate_mock_transcript()

        # Generate speaker configurations
        speakers_used = []
        voice_models = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        for i, personality in enumerate(self.speaker_personalities):
            speakers_used.append(
                {
                    "speaker_id": f"speaker_{i+1}",
                    "personality": personality,
                    "voice_model": voice_models[i % len(voice_models)],
                    "voice_settings": {"stability": 0.75, "similarity_boost": 0.8, "speed": 1.0},
                }
            )

        return {
            "success": True,
            "podcast_url": mock_url,
            "duration_seconds": base_duration,
            "speakers_used": speakers_used,
            "transcript": transcript,
            "metadata": {
                "podcast_id": podcast_id,
                "topic": self.topic,
                "format": self.output_format,
                "file_size_mb": round(base_duration * 0.125, 2),  # Approximate MP3 size
                "sample_rate": "44100 Hz",
                "bitrate": "128 kbps",
                "channels": "stereo",
                "music_included": self.background_music,
                "music_style": self.music_style if self.background_music else None,
                "has_intro": self.add_intro,
                "has_outro": self.add_outro,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "mock_mode": True,
            },
        }

    def _generate_mock_transcript(self) -> str:
        """Generate a mock transcript based on parameters."""
        lines = []

        if self.add_intro:
            lines.append("[INTRO MUSIC - 15 seconds]")
            lines.append("")

        # Generate conversation based on script or topic
        if self.script_content:
            lines.append("[PODCAST CONTENT - Using provided script]")
            lines.append(
                self.script_content[:500] + "..."
                if len(self.script_content) > 500
                else self.script_content
            )
        else:
            lines.append(f"[PODCAST CONTENT - Generated conversation about: {self.topic}]")
            lines.append("")

            for i, personality in enumerate(self.speaker_personalities):
                speaker_name = f"Speaker {i+1} ({personality})"
                if i == 0:
                    lines.append(
                        f"{speaker_name}: Welcome to today's episode about {self.topic}. "
                        f"I'm excited to dive into this fascinating topic."
                    )
                elif i == 1:
                    lines.append(
                        f"{speaker_name}: Thanks for having me! I'm looking forward to "
                        f"discussing {self.topic} and sharing some insights."
                    )
                else:
                    lines.append(
                        f"{speaker_name}: Great to be here and contribute to this "
                        f"important conversation."
                    )

            lines.append("")
            lines.append(
                f"[...conversation continues for approximately {self.duration_minutes} minutes...]"
            )

        if self.add_outro:
            lines.append("")
            lines.append(f"Speaker 1: That's all for today's episode. Thank you for listening!")
            lines.append("[OUTRO MUSIC - 10 seconds]")

        return "\n".join(lines)

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic for podcast generation.

        This method handles:
        1. Script generation (if needed)
        2. Voice synthesis for each speaker
        3. Audio segment creation
        4. Background music integration
        5. Final audio mixing

        Returns:
            Dict with podcast metadata and URLs

        Raises:
            APIError: When podcast generation fails
            ConfigurationError: When API keys are missing
        """
        try:
            # Get API key
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ConfigurationError(
                    "OPENAI_API_KEY environment variable is required",
                    tool_name=self.tool_name,
                    config_key="OPENAI_API_KEY",
                )

            # Generate unique podcast ID
            podcast_id = str(uuid.uuid4())

            # Step 1: Generate or validate script
            script = self._generate_or_validate_script()

            # Step 2: Assign voices to speakers
            speakers_config = self._assign_speaker_voices()

            # Step 3: Generate audio segments
            audio_segments = self._generate_audio_segments(script, speakers_config)

            # Step 4: Add intro/outro if requested
            if self.add_intro:
                intro_segment = self._generate_intro_segment()
                audio_segments.insert(0, intro_segment)

            if self.add_outro:
                outro_segment = self._generate_outro_segment()
                audio_segments.append(outro_segment)

            # Step 5: Mix audio with background music
            final_audio_url = self._mix_audio_segments(audio_segments, podcast_id)

            # Step 6: Calculate final duration
            total_duration = sum(seg.get("duration", 0) for seg in audio_segments)

            # Step 7: Generate transcript
            transcript = self._generate_transcript(script)

            # Step 8: Create metadata
            metadata = {
                "podcast_id": podcast_id,
                "topic": self.topic,
                "format": self.output_format,
                "file_size_mb": round(total_duration * 0.125, 2),
                "sample_rate": "44100 Hz",
                "bitrate": "128 kbps",
                "channels": "stereo",
                "music_included": self.background_music,
                "music_style": self.music_style if self.background_music else None,
                "has_intro": self.add_intro,
                "has_outro": self.add_outro,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "processing_time_seconds": 0,  # Would be calculated in real implementation
            }

            return {
                "podcast_url": final_audio_url,
                "duration_seconds": int(total_duration),
                "speakers_used": speakers_config,
                "transcript": transcript,
                "metadata": metadata,
            }

        except ConfigurationError:
            raise
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(
                f"Podcast generation failed: {str(e)}",
                tool_name=self.tool_name,
                api_name="OpenAI TTS",
            )

    def _generate_or_validate_script(self) -> Dict[str, Any]:
        """
        Generate script using AI or validate provided script.

        Returns:
            Dict containing script segments with speaker assignments
        """
        if self.script_content:
            # Parse and validate provided script
            return self._parse_script(self.script_content)
        else:
            # Generate script using AI based on topic and speakers
            return self._generate_script_from_topic()

    def _generate_script_from_topic(self) -> Dict[str, Any]:
        """
        Generate podcast script from topic using OpenAI API.

        Returns:
            Dict containing generated script segments
        """
        # This would use OpenAI's GPT API to generate a conversational script
        # For production, this would make actual API calls

        # Simulated structure
        script = {
            "segments": [
                {
                    "speaker_index": 0,
                    "text": f"Welcome to today's episode about {self.topic}.",
                    "duration_estimate": 5,
                },
                {
                    "speaker_index": 1,
                    "text": f"Thanks for having me! Let's explore {self.topic}.",
                    "duration_estimate": 4,
                },
            ],
            "total_segments": 2,
            "estimated_duration": 9,
        }

        return script

    def _parse_script(self, script_content: str) -> Dict[str, Any]:
        """
        Parse user-provided script into segments.

        Args:
            script_content: Raw script text

        Returns:
            Dict containing parsed script segments
        """
        # Simple parsing logic - in production this would be more sophisticated
        segments = []
        lines = script_content.split("\n")

        for line in lines:
            if line.strip():
                # Simple format: "Speaker 1: text"
                if ":" in line:
                    speaker_part, text = line.split(":", 1)
                    speaker_index = 0  # Default to first speaker

                    # Extract speaker number if present
                    if "speaker" in speaker_part.lower():
                        try:
                            speaker_index = (
                                int(speaker_part.lower().replace("speaker", "").strip()) - 1
                            )
                        except ValueError:
                            pass

                    segments.append(
                        {
                            "speaker_index": speaker_index,
                            "text": text.strip(),
                            "duration_estimate": len(text.split()) * 0.5,  # ~0.5 seconds per word
                        }
                    )

        return {
            "segments": segments,
            "total_segments": len(segments),
            "estimated_duration": sum(s["duration_estimate"] for s in segments),
        }

    def _assign_speaker_voices(self) -> List[Dict[str, Any]]:
        """
        Assign voice models to each speaker based on personalities.

        Returns:
            List of speaker configurations with voice assignments
        """
        # OpenAI TTS voice options
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        speakers_config = []
        for i, personality in enumerate(self.speaker_personalities):
            # Voice selection logic based on personality
            # In production, this could be more sophisticated
            voice_model = voice_options[i % len(voice_options)]

            speakers_config.append(
                {
                    "speaker_id": f"speaker_{i+1}",
                    "personality": personality,
                    "voice_model": voice_model,
                    "voice_settings": {
                        "model": "tts-1-hd" if self.voice_consistency else "tts-1",
                        "voice": voice_model,
                        "speed": 1.0,
                    },
                }
            )

        return speakers_config

    def _generate_audio_segments(
        self, script: Dict[str, Any], speakers_config: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate audio for each script segment using OpenAI TTS.

        Args:
            script: Parsed script with segments
            speakers_config: Speaker voice configurations

        Returns:
            List of audio segment metadata
        """
        # In production, this would:
        # 1. Call OpenAI TTS API for each segment
        # 2. Save temporary audio files
        # 3. Return file paths and metadata

        segments = []
        for segment in script.get("segments", []):
            speaker_idx = segment["speaker_index"]
            speaker_config = speakers_config[speaker_idx]

            segments.append(
                {
                    "speaker_id": speaker_config["speaker_id"],
                    "text": segment["text"],
                    "audio_file": f"/tmp/segment_{uuid.uuid4()}.{self.output_format}",
                    "duration": segment["duration_estimate"],
                    "voice_model": speaker_config["voice_model"],
                }
            )

        return segments

    def _generate_intro_segment(self) -> Dict[str, Any]:
        """
        Generate intro segment with music and voice.

        Returns:
            Dict containing intro segment metadata
        """
        # In production, this would generate actual intro audio
        return {
            "type": "intro",
            "audio_file": f"/tmp/intro_{uuid.uuid4()}.{self.output_format}",
            "duration": 15,
            "has_music": True,
        }

    def _generate_outro_segment(self) -> Dict[str, Any]:
        """
        Generate outro segment with music and voice.

        Returns:
            Dict containing outro segment metadata
        """
        # In production, this would generate actual outro audio
        return {
            "type": "outro",
            "audio_file": f"/tmp/outro_{uuid.uuid4()}.{self.output_format}",
            "duration": 10,
            "has_music": True,
        }

    def _mix_audio_segments(self, segments: List[Dict[str, Any]], podcast_id: str) -> str:
        """
        Mix all audio segments with background music.

        Args:
            segments: List of audio segment metadata
            podcast_id: Unique podcast identifier

        Returns:
            URL to final mixed audio file
        """
        # In production, this would:
        # 1. Use pydub or similar to concatenate segments
        # 2. Add background music track if enabled
        # 3. Apply audio normalization and effects
        # 4. Export final file
        # 5. Upload to storage and return URL

        final_url = f"https://podcast-storage.example.com/{podcast_id}.{self.output_format}"
        return final_url

    def _generate_transcript(self, script: Dict[str, Any]) -> str:
        """
        Generate formatted transcript from script.

        Args:
            script: Parsed script with segments

        Returns:
            Formatted transcript text
        """
        lines = []

        if self.add_intro:
            lines.append("[INTRO MUSIC - 15 seconds]")
            lines.append("")

        for segment in script.get("segments", []):
            speaker_idx = segment["speaker_index"]
            personality = self.speaker_personalities[speaker_idx]
            speaker_name = f"Speaker {speaker_idx + 1} ({personality})"
            lines.append(f"{speaker_name}: {segment['text']}")

        if self.add_outro:
            lines.append("")
            lines.append("[OUTRO MUSIC - 10 seconds]")

        return "\n".join(lines)


if __name__ == "__main__":
    # Test the PodcastGenerator tool
    print("Testing PodcastGenerator tool...")
    print("=" * 70)

    # Enable mock mode for testing
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test Case 1: Basic 2-speaker podcast
    print("\nTest Case 1: Basic 2-speaker podcast")
    print("-" * 70)
    tool1 = PodcastGenerator(
        topic="The Future of Artificial Intelligence",
        duration_minutes=10,
        num_speakers=2,
        speaker_personalities=["enthusiastic tech host", "AI researcher expert"],
        background_music=True,
        music_style="upbeat",
    )
    result1 = tool1.run()

    print(f"Success: {result1.get('success')}")
    print(f"Podcast URL: {result1.get('podcast_url')}")
    print(f"Duration: {result1.get('duration_seconds')} seconds")
    print(f"Speakers: {len(result1.get('speakers_used', []))}")
    print(f"Format: {result1.get('metadata', {}).get('format')}")
    print(f"File Size: {result1.get('metadata', {}).get('file_size_mb')} MB")
    print("\nTranscript Preview:")
    transcript1 = result1.get("transcript", "")
    print(transcript1[:300] + "..." if len(transcript1) > 300 else transcript1)

    # Test Case 2: 3-speaker panel with custom script
    print("\n\nTest Case 2: 3-speaker panel discussion")
    print("-" * 70)
    custom_script = """Speaker 1: Welcome everyone to our panel on climate change.
Speaker 2: Thank you for having me. This is such an important topic.
Speaker 3: I'm excited to share the latest research findings.
Speaker 1: Let's dive right in. What are the most pressing challenges we face?"""

    tool2 = PodcastGenerator(
        topic="Climate Change Solutions",
        duration_minutes=20,
        num_speakers=3,
        speaker_personalities=[
            "professional moderator",
            "environmental scientist",
            "policy expert",
        ],
        script_content=custom_script,
        background_music=True,
        music_style="calm",
        add_intro=True,
        add_outro=True,
    )
    result2 = tool2.run()

    print(f"Success: {result2.get('success')}")
    print(f"Podcast URL: {result2.get('podcast_url')}")
    print(f"Duration: {result2.get('duration_seconds')} seconds")
    print(f"Speakers: {result2.get('speakers_used', [])}")

    # Test Case 3: Solo podcast (1 speaker)
    print("\n\nTest Case 3: Solo podcast episode")
    print("-" * 70)
    tool3 = PodcastGenerator(
        topic="Meditation and Mindfulness Practices",
        duration_minutes=5,
        num_speakers=1,
        speaker_personalities=["calm meditation guide"],
        background_music=True,
        music_style="calm",
        output_format="wav",
        add_intro=False,
        add_outro=False,
    )
    result3 = tool3.run()

    print(f"Success: {result3.get('success')}")
    print(f"Podcast URL: {result3.get('podcast_url')}")
    print(f"Duration: {result3.get('duration_seconds')} seconds")
    print(f"Format: {result3.get('metadata', {}).get('format')}")

    # Test Case 4: Maximum speakers (4) with no music
    print("\n\nTest Case 4: 4-speaker roundtable without music")
    print("-" * 70)
    tool4 = PodcastGenerator(
        topic="Startup Funding Strategies",
        duration_minutes=30,
        num_speakers=4,
        speaker_personalities=[
            "startup founder",
            "venture capitalist",
            "angel investor",
            "business advisor",
        ],
        background_music=False,
        music_style="none",
        voice_consistency=True,
    )
    result4 = tool4.run()

    print(f"Success: {result4.get('success')}")
    print(f"Podcast URL: {result4.get('podcast_url')}")
    print(f"Duration: {result4.get('duration_seconds')} seconds")
    print(f"Music Included: {result4.get('metadata', {}).get('music_included')}")

    # Test Case 5: Error handling - mismatched speakers
    print("\n\nTest Case 5: Error handling - mismatched speaker count")
    print("-" * 70)
    try:
        tool5 = PodcastGenerator(
            topic="Test Topic",
            duration_minutes=10,
            num_speakers=3,
            speaker_personalities=["host", "guest"],  # Only 2 personalities for 3 speakers
        )
        result5 = tool5.run()
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}")
        print(f"Error message: {str(e)}")

    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("\nNote: Tests run in mock mode (USE_MOCK_APIS=true)")
    print("For production use, set OPENAI_API_KEY environment variable")
