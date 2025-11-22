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

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any

from tools.media.generation.image_generation.image_generation import ImageGeneration
from tools.media.generation.video_generation.video_generation import VideoGeneration
from tools.media.generation.audio_generation.audio_generation import AudioGeneration
from tools.media.generation.podcast_generator.podcast_generator import PodcastGenerator
from tools.media.generation.image_style_transfer.image_style_transfer import ImageStyleTransfer
from tools.media.generation.text_to_speech_advanced.text_to_speech_advanced import (
    TextToSpeechAdvanced,
)
from tools.media.generation.video_effects.video_effects import VideoEffects

from shared.errors import ValidationError, APIError, MediaError


# ========== ImageGeneration Tests ==========


class TestImageGeneration:
    """Comprehensive tests for ImageGeneration tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ImageGeneration(
            model="flux-pro",
            query="a beautiful sunset",
            aspect_ratio="16:9",
            task_summary="Generate sunset image",
        )
        assert tool.model == "flux-pro"
        assert tool.query == "a beautiful sunset"
        assert tool.aspect_ratio == "16:9"
        assert tool.tool_name == "image_generation"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters"""
        tool = ImageGeneration(model="flux-pro", query="test image", task_summary="Test")
        assert tool.model == "flux-pro"
        assert tool.query == "test image"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ImageGeneration(
            model="flux-pro", query="mountain landscape", task_summary="Generate landscape"
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = ImageGeneration(model="flux-pro", query="", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_empty_model(self):
        """Test validation with empty model"""
        tool = ImageGeneration(model="", query="test image", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.media.generation.image_generation.image_generation.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"url": "https://example.com/generated-image.png"}]
        }
        mock_post.return_value = mock_response

        tool = ImageGeneration(model="gpt-image-1", query="test image", task_summary="Test")
        result = tool.run()

        assert result["success"] is True

    @patch("tools.media.generation.image_generation.image_generation.requests.post")
    def test_api_error_handling(self, mock_post, monkeypatch):
        """Test handling of API errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")

        mock_post.side_effect = Exception("API failed")
        tool = ImageGeneration(model="gpt-image-1", query="test", task_summary="Test")

        with pytest.raises(APIError):
            tool.run()

    def test_aspect_ratio_validation(self):
        """Test aspect ratio validation"""
        valid_ratios = ["1:1", "16:9", "4:3", "9:16"]
        for ratio in valid_ratios:
            tool = ImageGeneration(
                model="flux-pro", query="test", aspect_ratio=ratio, task_summary="Test"
            )
            # Should not raise


# ========== VideoGeneration Tests ==========


class TestVideoGeneration:
    """Comprehensive tests for VideoGeneration tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = VideoGeneration(
            model="gemini/veo3",
            query="a cat playing piano",
            duration=5,
            task_summary="Generate cat video",
        )
        assert tool.model == "gemini/veo3"
        assert tool.query == "a cat playing piano"
        assert tool.duration == 5
        assert tool.tool_name == "video_generation"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = VideoGeneration(
            model="kling/v2.5-pro", query="dancing robot", task_summary="Generate robot video"
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = VideoGeneration(model="gemini/veo3", query="", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_duration(self):
        """Test validation with invalid duration"""
        with pytest.raises(ValidationError):
            VideoGeneration(model="gemini/veo3", query="test", duration=0, task_summary="Test")

    @patch("tools.media.generation.video_generation.video_generation.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"video_url": "https://example.com/generated-video.mp4"}
        mock_post.return_value = mock_response

        tool = VideoGeneration(model="sora-2", query="test video", task_summary="Test")
        result = tool.run()

        assert result["success"] is True


# ========== AudioGeneration Tests ==========


class TestAudioGeneration:
    """Comprehensive tests for AudioGeneration tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = AudioGeneration(
            model="google/gemini-2.5-pro-preview-tts",
            query="Hello world",
            voice="male",
            task_summary="Generate greeting",
        )
        assert tool.model == "google/gemini-2.5-pro-preview-tts"
        assert tool.query == "Hello world"
        assert tool.voice == "male"
        assert tool.tool_name == "audio_generation"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AudioGeneration(
            model="elevenlabs/v3-tts", query="Test speech", task_summary="Test TTS"
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = AudioGeneration(
            model="google/gemini-2.5-pro-preview-tts", query="", task_summary="Test"
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.media.generation.audio_generation.audio_generation.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("ELEVENLABS_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.content = b"fake_audio_data"
        mock_post.return_value = mock_response

        tool = AudioGeneration(model="elevenlabs/v3-tts", query="test audio", task_summary="Test")
        result = tool.run()

        assert result["success"] is True


# ========== PodcastGenerator Tests ==========


class TestPodcastGenerator:
    """Comprehensive tests for PodcastGenerator tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = PodcastGenerator(
            topic="AI in healthcare",
            duration=10,
            hosts=["Host 1", "Host 2"],
            task_summary="Generate podcast",
        )
        assert tool.topic == "AI in healthcare"
        assert tool.duration == 10
        assert len(tool.hosts) == 2
        assert tool.tool_name == "podcast_generator"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = PodcastGenerator(topic="Climate change", duration=5, task_summary="Test podcast")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_topic(self):
        """Test validation with empty topic"""
        tool = PodcastGenerator(topic="", duration=5, task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_duration(self):
        """Test validation with invalid duration"""
        with pytest.raises(ValidationError):
            PodcastGenerator(topic="test", duration=0, task_summary="Test")


# ========== ImageStyleTransfer Tests ==========


class TestImageStyleTransfer:
    """Comprehensive tests for ImageStyleTransfer tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ImageStyleTransfer(
            source_image_url="https://example.com/source.jpg",
            style="oil painting",
            task_summary="Apply style transfer",
        )
        assert tool.source_image_url == "https://example.com/source.jpg"
        assert tool.style == "oil painting"
        assert tool.tool_name == "image_style_transfer"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ImageStyleTransfer(
            source_image_url="https://example.com/image.jpg",
            style="watercolor",
            task_summary="Test style transfer",
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty URL"""
        tool = ImageStyleTransfer(source_image_url="", style="oil painting", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = ImageStyleTransfer(
            source_image_url="not-a-url", style="oil painting", task_summary="Test"
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.media.generation.image_style_transfer.image_style_transfer.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("STABILITY_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"artifacts": [{"base64": "fake_base64_data"}]}
        mock_post.return_value = mock_response

        tool = ImageStyleTransfer(
            source_image_url="https://example.com/test.jpg", style="cartoon", task_summary="Test"
        )
        result = tool.run()

        assert result["success"] is True


# ========== TextToSpeechAdvanced Tests ==========


class TestTextToSpeechAdvanced:
    """Comprehensive tests for TextToSpeechAdvanced tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = TextToSpeechAdvanced(
            text="Hello, this is a test.",
            voice="en-US-Neural2-A",
            speed=1.0,
            pitch=0,
            task_summary="Generate speech",
        )
        assert tool.text == "Hello, this is a test."
        assert tool.voice == "en-US-Neural2-A"
        assert tool.speed == 1.0
        assert tool.tool_name == "text_to_speech_advanced"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = TextToSpeechAdvanced(text="Test speech generation", task_summary="Test TTS")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_text(self):
        """Test validation with empty text"""
        tool = TextToSpeechAdvanced(text="", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_speed(self):
        """Test validation with invalid speed"""
        with pytest.raises(ValidationError):
            TextToSpeechAdvanced(text="test", speed=0, task_summary="Test")

    def test_validate_parameters_speed_range(self):
        """Test validation with speed out of range"""
        with pytest.raises(ValidationError):
            TextToSpeechAdvanced(text="test", speed=5.0, task_summary="Test")

    @patch("tools.media.generation.text_to_speech_advanced.text_to_speech_advanced.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("GOOGLE_CLOUD_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"audioContent": "base64_encoded_audio"}
        mock_post.return_value = mock_response

        tool = TextToSpeechAdvanced(text="test speech", task_summary="Test")
        result = tool.run()

        assert result["success"] is True


# ========== VideoEffects Tests ==========


class TestVideoEffects:
    """Comprehensive tests for VideoEffects tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = VideoEffects(
            video_url="https://example.com/video.mp4",
            effect_type="blur",
            intensity=0.5,
            task_summary="Apply video effects",
        )
        assert tool.video_url == "https://example.com/video.mp4"
        assert tool.effect_type == "blur"
        assert tool.intensity == 0.5
        assert tool.tool_name == "video_effects"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = VideoEffects(
            video_url="https://example.com/test.mp4",
            effect_type="sharpen",
            task_summary="Test effects",
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty URL"""
        tool = VideoEffects(video_url="", effect_type="blur", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_intensity(self):
        """Test validation with invalid intensity"""
        with pytest.raises(ValidationError):
            VideoEffects(
                video_url="https://example.com/video.mp4",
                effect_type="blur",
                intensity=2.0,
                task_summary="Test",
            )

    @patch("tools.media.generation.video_effects.video_effects.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("VIDEO_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "processed_video_url": "https://example.com/processed.mp4"
        }
        mock_post.return_value = mock_response

        tool = VideoEffects(
            video_url="https://example.com/test.mp4", effect_type="sepia", task_summary="Test"
        )
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_multiple_effects(self, monkeypatch):
        """Test applying multiple effects"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        effects = ["blur", "sharpen", "sepia", "grayscale"]

        for effect in effects:
            tool = VideoEffects(
                video_url="https://example.com/test.mp4",
                effect_type=effect,
                task_summary=f"Test {effect}",
            )
            result = tool.run()
            assert result["success"] is True
