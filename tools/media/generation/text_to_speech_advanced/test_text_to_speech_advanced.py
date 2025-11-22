"""
Tests for TextToSpeechAdvanced tool
"""

import pytest
from unittest.mock import patch, MagicMock
import os

from tools.media_generation.text_to_speech_advanced import TextToSpeechAdvanced
from shared.errors import ValidationError, APIError


class TestTextToSpeechAdvanced:
    """Test suite for TextToSpeechAdvanced."""

    @pytest.fixture
    def tool(self):
        return TextToSpeechAdvanced(
            text="Hello, this is a test.", gender="female", age="adult", accent="american"
        )

    def test_initialization(self, tool):
        """Test tool initialization."""
        assert tool.tool_name == "text_to_speech_advanced"
        assert tool.tool_category == "media_generation"
        assert tool.text == "Hello, this is a test."

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        """Test mock mode execution."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "audio_url" in result["result"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_voice_genders(self):
        """Test with different voice genders."""
        genders = ["male", "female", "neutral"]

        for gender in genders:
            tool = TextToSpeechAdvanced(text="Testing voice gender", gender=gender)
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["voice_config"]["gender"] == gender

    def test_invalid_gender(self):
        """Test validation with invalid gender."""
        tool = TextToSpeechAdvanced(text="Test", gender="invalid")
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_voice_ages(self):
        """Test with different voice ages."""
        ages = ["child", "young_adult", "adult", "elderly"]

        for age in ages:
            tool = TextToSpeechAdvanced(text="Testing voice age", age=age)
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["voice_config"]["age"] == age

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_accents(self):
        """Test with different accents."""
        accents = ["american", "british", "australian", "indian", "scottish"]

        for accent in accents:
            tool = TextToSpeechAdvanced(text="Testing accent", accent=accent)
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["voice_config"]["accent"] == accent

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_emotions(self):
        """Test with different emotions."""
        emotions = ["neutral", "happy", "sad", "angry", "excited", "calm"]

        for emotion in emotions:
            tool = TextToSpeechAdvanced(
                text="Testing emotion", emotion=emotion, emotion_intensity=0.7
            )
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["voice_config"]["emotion"] == emotion

    def test_invalid_emotion(self):
        """Test validation with invalid emotion."""
        tool = TextToSpeechAdvanced(text="Test", emotion="invalid_emotion")
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_emotion_intensity(self):
        """Test emotion intensity parameter."""
        tool = TextToSpeechAdvanced(
            text="Testing emotion intensity", emotion="happy", emotion_intensity=0.9
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["voice_config"]["emotion_intensity"] == 0.9

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_prosody_controls(self):
        """Test prosody parameters."""
        tool = TextToSpeechAdvanced(text="Testing prosody", pitch=0.3, rate=1.2, volume=0.8)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["prosody"]["pitch"] == 0.3
        assert result["result"]["prosody"]["rate"] == 1.2
        assert result["result"]["prosody"]["volume"] == 0.8

    def test_invalid_pitch(self):
        """Test validation with invalid pitch."""
        tool = TextToSpeechAdvanced(text="Test", pitch=2.0)  # Out of range
        result = tool.run()
        assert result["success"] is False

    def test_invalid_rate(self):
        """Test validation with invalid rate."""
        tool = TextToSpeechAdvanced(text="Test", rate=3.0)  # Out of range
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_output_formats(self):
        """Test different output formats."""
        formats = ["mp3", "wav", "ogg", "flac"]

        for fmt in formats:
            tool = TextToSpeechAdvanced(text="Testing format", output_format=fmt)
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["format"] == fmt

    def test_invalid_output_format(self):
        """Test validation with invalid output format."""
        tool = TextToSpeechAdvanced(text="Test", output_format="invalid")
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_sample_rates(self):
        """Test different sample rates."""
        sample_rates = [8000, 16000, 22050, 44100, 48000]

        for rate in sample_rates:
            tool = TextToSpeechAdvanced(text="Testing sample rate", sample_rate=rate)
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["sample_rate"] == rate

    def test_invalid_sample_rate(self):
        """Test validation with invalid sample rate."""
        tool = TextToSpeechAdvanced(text="Test", sample_rate=99999)
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_long_text(self):
        """Test with longer text."""
        long_text = " ".join(["This is a test sentence."] * 100)
        tool = TextToSpeechAdvanced(text=long_text, rate=1.5)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["text_length"] == len(long_text)

    def test_empty_text(self):
        """Test validation with empty text."""
        tool = TextToSpeechAdvanced(text="   ")
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_custom_voice_id(self):
        """Test with custom voice ID."""
        tool = TextToSpeechAdvanced(text="Testing custom voice", voice_id="custom_voice_123")
        result = tool.run()
        assert result["success"] is True
        assert "custom_voice_123" in result["result"]["voice_config"]["voice_id"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_configuration(self):
        """Test with all parameters configured."""
        tool = TextToSpeechAdvanced(
            text="This is a comprehensive test of all parameters.",
            voice_id="test_voice_001",
            gender="female",
            age="young_adult",
            accent="british",
            emotion="excited",
            emotion_intensity=0.75,
            pitch=0.15,
            rate=1.05,
            volume=0.85,
            output_format="wav",
            sample_rate=44100,
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["voice_config"]["emotion"] == "excited"
        assert result["result"]["format"] == "wav"
        assert result["result"]["prosody"]["pitch"] == 0.15
