"""
Unit tests for PodcastGenerator tool.

Tests cover:
- Basic podcast generation with different speaker counts
- Custom script parsing
- Background music integration
- Intro/outro segments
- Error handling and validation
- Mock mode operation
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from shared.errors import ConfigurationError, ValidationError

from .podcast_generator import PodcastGenerator


class TestPodcastGeneratorValidation:
    """Test input validation."""

    def test_valid_basic_podcast(self):
        """Test valid basic podcast configuration."""
        tool = PodcastGenerator(
            topic="Test Topic",
            duration_minutes=10,
            num_speakers=2,
            speaker_personalities=["host", "guest"],
        )
        assert tool.topic == "Test Topic"
        assert tool.duration_minutes == 10
        assert tool.num_speakers == 2

    def test_empty_topic_fails(self):
        """Test that empty topic raises ValidationError."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = PodcastGenerator(
            topic="   ",  # Empty/whitespace only
            duration_minutes=10,
            num_speakers=2,
            speaker_personalities=["host", "guest"],
        )
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_mismatched_speaker_count_fails(self):
        """Test that mismatched speaker personalities raises error."""
        with pytest.raises(ValueError) as exc_info:
            PodcastGenerator(
                topic="Test",
                duration_minutes=10,
                num_speakers=3,
                speaker_personalities=["host", "guest"],  # Only 2 for 3 speakers
            )
        assert "exactly 3 entries" in str(exc_info.value)

    def test_duration_out_of_range(self):
        """Test duration validation."""
        os.environ["USE_MOCK_APIS"] = "true"

        # Too short
        tool1 = PodcastGenerator(
            topic="Test", duration_minutes=0, num_speakers=1, speaker_personalities=["host"]
        )
        result1 = tool1.run()
        assert result1["success"] is False

        # Too long
        tool2 = PodcastGenerator(
            topic="Test", duration_minutes=100, num_speakers=1, speaker_personalities=["host"]
        )
        result2 = tool2.run()
        assert result2["success"] is False

    def test_invalid_num_speakers(self):
        """Test speaker count validation."""
        os.environ["USE_MOCK_APIS"] = "true"

        # Too few
        tool1 = PodcastGenerator(
            topic="Test", duration_minutes=10, num_speakers=0, speaker_personalities=[]
        )
        result1 = tool1.run()
        assert result1["success"] is False

        # Too many
        tool2 = PodcastGenerator(
            topic="Test",
            duration_minutes=10,
            num_speakers=5,
            speaker_personalities=["a", "b", "c", "d", "e"],
        )
        result2 = tool2.run()
        assert result2["success"] is False


class TestPodcastGeneratorMockMode:
    """Test mock mode operation."""

    def setup_method(self):
        """Enable mock mode for all tests."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_basic_two_speaker_podcast(self):
        """Test basic 2-speaker podcast generation."""
        tool = PodcastGenerator(
            topic="AI and Technology",
            duration_minutes=10,
            num_speakers=2,
            speaker_personalities=["tech host", "AI expert"],
        )
        result = tool.run()

        assert result["success"] is True
        assert "podcast_url" in result
        assert result["duration_seconds"] > 0
        assert len(result["speakers_used"]) == 2
        assert "transcript" in result
        assert result["metadata"]["mock_mode"] is True

    def test_single_speaker_podcast(self):
        """Test solo podcast generation."""
        tool = PodcastGenerator(
            topic="Meditation Guide",
            duration_minutes=5,
            num_speakers=1,
            speaker_personalities=["calm guide"],
        )
        result = tool.run()

        assert result["success"] is True
        assert len(result["speakers_used"]) == 1
        assert (
            "meditation" in result["transcript"].lower() or "guide" in result["transcript"].lower()
        )

    def test_four_speaker_panel(self):
        """Test maximum speaker count (4 speakers)."""
        tool = PodcastGenerator(
            topic="Business Discussion",
            duration_minutes=20,
            num_speakers=4,
            speaker_personalities=["moderator", "founder", "investor", "advisor"],
        )
        result = tool.run()

        assert result["success"] is True
        assert len(result["speakers_used"]) == 4
        assert all("speaker_id" in s for s in result["speakers_used"])
        assert all("personality" in s for s in result["speakers_used"])

    def test_with_custom_script(self):
        """Test podcast with custom script."""
        custom_script = """Speaker 1: Welcome to the show!
Speaker 2: Thanks for having me.
Speaker 1: Let's discuss the topic.
Speaker 2: Absolutely, I'm excited to share."""

        tool = PodcastGenerator(
            topic="Custom Script Test",
            duration_minutes=5,
            num_speakers=2,
            speaker_personalities=["host", "guest"],
            script_content=custom_script,
        )
        result = tool.run()

        assert result["success"] is True
        assert "script" in result["transcript"].lower() or "welcome" in result["transcript"].lower()

    def test_background_music_settings(self):
        """Test different background music settings."""
        # With upbeat music
        tool1 = PodcastGenerator(
            topic="Test",
            num_speakers=1,
            speaker_personalities=["host"],
            background_music=True,
            music_style="upbeat",
        )
        result1 = tool1.run()
        assert result1["metadata"]["music_included"] is True
        assert result1["metadata"]["music_style"] == "upbeat"

        # No music
        tool2 = PodcastGenerator(
            topic="Test",
            num_speakers=1,
            speaker_personalities=["host"],
            background_music=False,
            music_style="none",
        )
        result2 = tool2.run()
        assert result2["metadata"]["music_included"] is False

    def test_intro_outro_segments(self):
        """Test intro and outro segment inclusion."""
        # With intro and outro
        tool1 = PodcastGenerator(
            topic="Test",
            duration_minutes=5,
            num_speakers=1,
            speaker_personalities=["host"],
            add_intro=True,
            add_outro=True,
        )
        result1 = tool1.run()

        # Duration should include intro (15s) + outro (10s)
        assert result1["duration_seconds"] >= 5 * 60 + 25
        assert result1["metadata"]["has_intro"] is True
        assert result1["metadata"]["has_outro"] is True

        # Without intro and outro
        tool2 = PodcastGenerator(
            topic="Test",
            duration_minutes=5,
            num_speakers=1,
            speaker_personalities=["host"],
            add_intro=False,
            add_outro=False,
        )
        result2 = tool2.run()

        assert result2["metadata"]["has_intro"] is False
        assert result2["metadata"]["has_outro"] is False

    def test_output_formats(self):
        """Test different output formats."""
        # MP3 format
        tool1 = PodcastGenerator(
            topic="Test", num_speakers=1, speaker_personalities=["host"], output_format="mp3"
        )
        result1 = tool1.run()
        assert result1["metadata"]["format"] == "mp3"
        assert ".mp3" in result1["podcast_url"]

        # WAV format
        tool2 = PodcastGenerator(
            topic="Test", num_speakers=1, speaker_personalities=["host"], output_format="wav"
        )
        result2 = tool2.run()
        assert result2["metadata"]["format"] == "wav"
        assert ".wav" in result2["podcast_url"]

    def test_voice_consistency_setting(self):
        """Test voice consistency parameter."""
        tool = PodcastGenerator(
            topic="Test",
            num_speakers=2,
            speaker_personalities=["host", "guest"],
            voice_consistency=True,
        )
        result = tool.run()

        assert result["success"] is True
        # In mock mode, just verify the parameter is respected
        for speaker in result["speakers_used"]:
            assert "voice_model" in speaker

    def test_metadata_completeness(self):
        """Test that all expected metadata fields are present."""
        tool = PodcastGenerator(
            topic="Comprehensive Test",
            duration_minutes=15,
            num_speakers=2,
            speaker_personalities=["host", "expert"],
        )
        result = tool.run()

        metadata = result["metadata"]
        required_fields = [
            "podcast_id",
            "topic",
            "format",
            "file_size_mb",
            "sample_rate",
            "bitrate",
            "channels",
            "music_included",
            "has_intro",
            "has_outro",
            "generated_at",
            "mock_mode",
        ]

        for field in required_fields:
            assert field in metadata, f"Missing metadata field: {field}"

    def test_speaker_configuration_structure(self):
        """Test speaker configuration structure."""
        tool = PodcastGenerator(
            topic="Test", num_speakers=3, speaker_personalities=["host", "guest1", "guest2"]
        )
        result = tool.run()

        speakers = result["speakers_used"]
        assert len(speakers) == 3

        for i, speaker in enumerate(speakers):
            assert "speaker_id" in speaker
            assert "personality" in speaker
            assert "voice_model" in speaker
            assert "voice_settings" in speaker
            assert speaker["personality"] == ["host", "guest1", "guest2"][i]


class TestPodcastGeneratorProduction:
    """Test production mode behavior."""

    def setup_method(self):
        """Disable mock mode."""
        os.environ["USE_MOCK_APIS"] = "false"

    def teardown_method(self):
        """Re-enable mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_missing_api_key_fails(self):
        """Test that missing API key raises ConfigurationError."""
        # Temporarily remove API key
        original_key = os.environ.pop("OPENAI_API_KEY", None)

        try:
            tool = PodcastGenerator(topic="Test", num_speakers=1, speaker_personalities=["host"])
            result = tool.run()

            assert result["success"] is False
            assert result["error"]["code"] == "CONFIG_ERROR"

        finally:
            # Restore API key if it existed
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key


class TestPodcastGeneratorEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Enable mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_very_long_topic(self):
        """Test handling of very long topic."""
        long_topic = "A" * 500  # Maximum allowed length
        tool = PodcastGenerator(topic=long_topic, num_speakers=1, speaker_personalities=["host"])
        result = tool.run()
        assert result["success"] is True

    def test_topic_too_long_fails(self):
        """Test that topic over 500 chars fails."""
        with pytest.raises(ValueError):
            PodcastGenerator(
                topic="A" * 501, num_speakers=1, speaker_personalities=["host"]  # Over limit
            )

    def test_empty_personality_fails(self):
        """Test that empty personality string fails."""
        with pytest.raises(ValueError) as exc_info:
            PodcastGenerator(
                topic="Test",
                num_speakers=2,
                speaker_personalities=["host", ""],  # Empty personality
            )
        assert "non-empty string" in str(exc_info.value)

    def test_personality_too_long_fails(self):
        """Test that personality over 200 chars fails."""
        with pytest.raises(ValueError) as exc_info:
            PodcastGenerator(
                topic="Test", num_speakers=1, speaker_personalities=["A" * 201]  # Over limit
            )
        assert "too long" in str(exc_info.value)

    def test_script_content_too_long_fails(self):
        """Test that script over 50000 chars fails."""
        with pytest.raises(ValueError) as exc_info:
            PodcastGenerator(
                topic="Test",
                num_speakers=1,
                speaker_personalities=["host"],
                script_content="A" * 50001,  # Over limit
            )
        assert "too long" in str(exc_info.value)

    def test_minimum_duration(self):
        """Test minimum duration podcast."""
        tool = PodcastGenerator(
            topic="Quick Update",
            duration_minutes=1,  # Minimum
            num_speakers=1,
            speaker_personalities=["host"],
            add_intro=False,
            add_outro=False,
        )
        result = tool.run()
        assert result["success"] is True
        assert result["duration_seconds"] >= 60

    def test_maximum_duration(self):
        """Test maximum duration podcast."""
        tool = PodcastGenerator(
            topic="Long Form Discussion",
            duration_minutes=60,  # Maximum
            num_speakers=2,
            speaker_personalities=["host", "guest"],
        )
        result = tool.run()
        assert result["success"] is True
        assert result["duration_seconds"] >= 3600


class TestPodcastGeneratorTranscript:
    """Test transcript generation."""

    def setup_method(self):
        """Enable mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_transcript_includes_speakers(self):
        """Test that transcript includes speaker labels."""
        tool = PodcastGenerator(
            topic="Test", num_speakers=2, speaker_personalities=["tech host", "expert guest"]
        )
        result = tool.run()

        transcript = result["transcript"]
        assert "Speaker" in transcript or "speaker" in transcript.lower()

    def test_transcript_with_intro_outro(self):
        """Test transcript includes intro/outro markers."""
        tool = PodcastGenerator(
            topic="Test",
            num_speakers=1,
            speaker_personalities=["host"],
            add_intro=True,
            add_outro=True,
        )
        result = tool.run()

        transcript = result["transcript"]
        assert "INTRO" in transcript.upper() or "intro" in transcript.lower()
        assert "OUTRO" in transcript.upper() or "outro" in transcript.lower()

    def test_transcript_without_intro_outro(self):
        """Test transcript without intro/outro markers."""
        tool = PodcastGenerator(
            topic="Test",
            num_speakers=1,
            speaker_personalities=["host"],
            add_intro=False,
            add_outro=False,
        )
        result = tool.run()

        transcript = result["transcript"]
        # Transcript should still be generated, just without intro/outro
        assert len(transcript) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
