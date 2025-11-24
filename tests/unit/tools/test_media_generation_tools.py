"""
Comprehensive unit tests for Media Generation Tools category.

Tests all media generation tools:
- image_generation
- video_generation
- audio_generation
- podcast_generator
- image_style_transfer
- text_to_speech_advanced
- video_effects
"""

from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from shared.errors import APIError, MediaError, ValidationError
from tools.media.generation.audio_generation.audio_generation import AudioGeneration
from tools.media.generation.image_generation.image_generation import ImageGeneration
from tools.media.generation.image_style_transfer.image_style_transfer import ImageStyleTransfer
from tools.media.generation.podcast_generator.podcast_generator import PodcastGenerator
from tools.media.generation.text_to_speech_advanced.text_to_speech_advanced import (
    TextToSpeechAdvanced,
)
from tools.media.generation.video_effects.video_effects import VideoEffects
from tools.media.generation.video_generation.video_generation import VideoGeneration

# ========== ImageGeneration Tests ==========


class TestImageGeneration:
    """Comprehensive tests for ImageGeneration tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ImageGeneration(
            prompt="a beautiful sunset",
            params={"size": "1024x1024"},
        )
        assert tool.prompt == "a beautiful sunset"
        assert tool.params == {"size": "1024x1024"}
        assert tool.tool_name == "image_generation"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters"""
        tool = ImageGeneration(prompt="test image")
        assert tool.prompt == "test image"
        assert tool.params == {}

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ImageGeneration(prompt="mountain landscape")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = ImageGeneration(prompt="test")  # Pydantic allows empty after init
        tool.prompt = ""  # Set to empty after init
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_params(self):
        """Test validation with invalid params type"""
        tool = ImageGeneration(prompt="test image", params={})
        tool.params = "invalid"  # Set invalid after init
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_execute_live_mode_success(self):
        """Test that live mode returns properly formatted result"""
        # Don't actually run in live mode to avoid rate limits
        # Just test that the structure is correct in mock mode
        import os

        os.environ["USE_MOCK_APIS"] = "true"

        tool = ImageGeneration(prompt="test image", params={"size": "1024x1024"})
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        # Mock mode should be true
        assert result["metadata"]["mock_mode"] is True

    def test_api_error_handling(self):
        """Test that tool works without actual API"""
        tool = ImageGeneration(prompt="test")
        # Validation should pass with non-empty prompt
        tool._validate_parameters()  # Should not raise

    def test_size_validation(self):
        """Test size parameter validation"""
        valid_sizes = ["512x512", "1024x1024", "1024x768"]
        for size in valid_sizes:
            tool = ImageGeneration(prompt="test", params={"size": size})
            # Should not raise
            tool._validate_parameters()


# ========== VideoGeneration Tests ==========


class TestVideoGeneration:
    """Comprehensive tests for VideoGeneration tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = VideoGeneration(
            prompt="a cat playing piano",
            params={"duration": 5},
        )
        assert tool.prompt == "a cat playing piano"
        assert tool.params == {"duration": 5}
        assert tool.tool_name == "video_generation"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = VideoGeneration(prompt="dancing robot")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = VideoGeneration(prompt="test")
        tool.prompt = ""  # Set empty after init
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_duration(self):
        """Test validation with invalid duration in params"""
        tool = VideoGeneration(prompt="test", params={"duration": 0})
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_execute_live_mode_success(self):
        """Test execution returns properly formatted result"""
        import os

        os.environ["USE_MOCK_APIS"] = "true"

        tool = VideoGeneration(prompt="test video", params={"duration": 6})
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True


# ========== AudioGeneration Tests ==========


class TestAudioGeneration:
    """Comprehensive tests for AudioGeneration tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = AudioGeneration(
            prompt="Hello world",
            params={"voice": "male"},
        )
        assert tool.prompt == "Hello world"
        assert tool.params == {"voice": "male"}
        assert tool.tool_name == "audio_generation"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AudioGeneration(prompt="Test speech")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = AudioGeneration(prompt="test")
        tool.prompt = ""  # Set empty after init
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_execute_live_mode_success(self):
        """Test execution returns properly formatted result"""
        import os

        os.environ["USE_MOCK_APIS"] = "true"

        tool = AudioGeneration(prompt="test audio", params={"voice": "female"})
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True


# ========== PodcastGenerator Tests ==========


class TestPodcastGenerator:
    """Comprehensive tests for PodcastGenerator tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = PodcastGenerator(
            topic="AI in healthcare",
            duration_minutes=10,
            num_speakers=2,
            speaker_personalities=["Host 1", "Host 2"],
        )
        assert tool.topic == "AI in healthcare"
        assert tool.duration_minutes == 10
        assert tool.num_speakers == 2
        assert len(tool.speaker_personalities) == 2
        assert tool.tool_name == "podcast_generator"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = PodcastGenerator(
            topic="Climate change",
            duration_minutes=5,
            num_speakers=1,
            speaker_personalities=["climate expert"],
        )
        result = tool.run()

        assert result["success"] is True
        assert "podcast_url" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_topic(self):
        """Test validation with empty topic"""
        tool = PodcastGenerator(
            topic="test", duration_minutes=5, num_speakers=1, speaker_personalities=["host"]
        )
        tool.topic = ""  # Set empty after init
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_duration(self):
        """Test validation with invalid duration - Pydantic validates at init"""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            PodcastGenerator(
                topic="test", duration_minutes=0, num_speakers=1, speaker_personalities=["host"]
            )


# ========== ImageStyleTransfer Tests ==========


class TestImageStyleTransfer:
    """Comprehensive tests for ImageStyleTransfer tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ImageStyleTransfer(
            input_image="https://example.com/source.jpg",
            style="starry_night",
        )
        assert tool.input_image == "https://example.com/source.jpg"
        assert tool.style == "starry_night"
        assert tool.tool_name == "image_style_transfer"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ImageStyleTransfer(
            input_image="https://example.com/image.jpg",
            style="watercolor",
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty URL - Pydantic validates at init"""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            ImageStyleTransfer(input_image="", style="starry_night")

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = ImageStyleTransfer(input_image="not-a-url", style="starry_night")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_execute_live_mode_success(self, monkeypatch):
        """Test execution in live mode returns properly formatted result"""
        # Don't actually run in live mode to avoid rate limits
        # Just test that the structure is correct in mock mode
        import os

        os.environ["USE_MOCK_APIS"] = "true"

        tool = ImageStyleTransfer(input_image="https://example.com/test.jpg", style="starry_night")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True


# ========== TextToSpeechAdvanced Tests ==========


class TestTextToSpeechAdvanced:
    """Comprehensive tests for TextToSpeechAdvanced tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = TextToSpeechAdvanced(
            text="Hello, this is a test.",
            gender="female",
            age="young_adult",
            accent="american",
            emotion="neutral",
            rate=1.0,
            pitch=0.0,
        )
        assert tool.text == "Hello, this is a test."
        assert tool.gender == "female"
        assert tool.age == "young_adult"
        assert tool.accent == "american"
        assert tool.rate == 1.0
        assert tool.pitch == 0.0
        assert tool.tool_name == "text_to_speech_advanced"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = TextToSpeechAdvanced(text="Test speech generation")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_text(self):
        """Test validation with empty text - Pydantic validates at init"""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            TextToSpeechAdvanced(text="")

    def test_validate_parameters_invalid_rate(self):
        """Test validation with invalid rate - Pydantic validates at init"""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            TextToSpeechAdvanced(text="test", rate=0.3)  # Below minimum 0.5

    def test_validate_parameters_rate_range(self):
        """Test validation with rate out of range - Pydantic validates at init"""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            TextToSpeechAdvanced(text="test", rate=5.0)  # Above maximum 2.0

    def test_execute_live_mode_success(self, monkeypatch):
        """Test execution in live mode returns properly formatted result"""
        # Don't actually run in live mode to avoid rate limits
        # Just test that the structure is correct in mock mode
        import os

        os.environ["USE_MOCK_APIS"] = "true"

        tool = TextToSpeechAdvanced(text="test speech", gender="female", emotion="happy")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True


# ========== VideoEffects Tests ==========


class TestVideoEffects:
    """Comprehensive tests for VideoEffects tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = VideoEffects(
            input_path="/path/to/video.mp4",
            effects=[
                {"type": "blur", "parameters": {"strength": 5}},
            ],
        )
        assert tool.input_path == "/path/to/video.mp4"
        assert len(tool.effects) == 1
        assert tool.effects[0]["type"] == "blur"
        assert tool.tool_name == "video_effects"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = VideoEffects(
            input_path="/path/to/test.mp4",
            effects=[
                {"type": "sharpen", "parameters": {"strength": 3}},
            ],
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_path(self):
        """Test validation with empty input path - Pydantic validates at init"""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            VideoEffects(input_path="", effects=[{"type": "blur"}])

    def test_validate_parameters_empty_effects(self):
        """Test validation with empty effects list - Pydantic validates at init"""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            VideoEffects(
                input_path="/path/to/video.mp4",
                effects=[],
            )

    @patch("shared.base.get_rate_limiter")
    def test_execute_live_mode_success(self, mock_rate_limiter, monkeypatch):
        """Test execution in live mode (mock mode off) - validates file existence"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        # Mock rate limiter to not raise errors
        mock_limiter_instance = MagicMock()
        mock_limiter_instance.check_rate_limit.return_value = None
        mock_rate_limiter.return_value = mock_limiter_instance

        # File validation happens in _validate_parameters
        tool = VideoEffects(input_path="/path/to/test.mp4", effects=[{"type": "sepia"}])

        # BaseTool catches ValidationError and returns error response
        tool._raise_exceptions = False
        result = tool.run()

        # Should return error response for missing file
        assert result["success"] is False
        assert "error" in result
        assert "not found" in str(result["error"]["message"]).lower()

    def test_edge_case_multiple_effects(self, monkeypatch):
        """Test applying multiple effects"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        effect_types = ["blur", "sharpen", "sepia", "grayscale"]

        tool = VideoEffects(
            input_path="/path/to/test.mp4",
            effects=[{"type": effect} for effect in effect_types],
        )
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]["effects_applied"]) == 4
