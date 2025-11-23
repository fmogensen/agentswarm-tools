"""
Tests for AudioEffects tool
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from shared.errors import APIError, ValidationError
from tools.media_analysis.audio_effects import AudioEffects


class TestAudioEffects:
    """Test suite for AudioEffects."""

    @pytest.fixture
    def tool(self):
        return AudioEffects(
            input_path="/path/to/test_audio.wav",
            effects=[{"type": "normalize", "parameters": {"target_level": -3}}],
        )

    def test_initialization(self, tool):
        """Test tool initialization."""
        assert tool.tool_name == "audio_effects"
        assert tool.tool_category == "media_analysis"
        assert tool.input_path == "/path/to/test_audio.wav"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        """Test mock mode execution."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "output_path" in result["result"]
        assert len(result["result"]["effects_applied"]) == 1

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_multiple_effects(self):
        """Test with multiple effects."""
        tool = AudioEffects(
            input_path="/path/to/test_audio.wav",
            effects=[
                {"type": "normalize", "parameters": {"target_level": -3}},
                {"type": "reverb", "parameters": {"delay": 60, "decay": 0.5}},
                {"type": "eq", "parameters": {"bass": 2, "treble": -1}},
            ],
        )
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]["effects_applied"]) == 3

    def test_empty_effects_validation(self):
        """Test validation with empty effects list."""
        tool = AudioEffects(input_path="/path/to/test_audio.wav", effects=[])
        result = tool.run()
        assert result["success"] is False

    def test_invalid_effect_type(self):
        """Test validation with invalid effect type."""
        tool = AudioEffects(
            input_path="/path/to/test_audio.wav",
            effects=[{"type": "invalid_effect", "parameters": {}}],
        )
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_custom_output_path(self):
        """Test with custom output path."""
        tool = AudioEffects(
            input_path="/path/to/test_audio.wav",
            effects=[{"type": "normalize", "parameters": {}}],
            output_path="/path/to/custom_output.wav",
        )
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["output_path"] == "/path/to/custom_output.wav"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_all_effect_types(self):
        """Test all supported effect types."""
        effects = [
            {"type": "reverb", "parameters": {"delay": 60, "decay": 0.5}},
            {"type": "echo", "parameters": {"delay": 500, "decay": 0.6}},
            {"type": "eq", "parameters": {"bass": 2, "mid": 0, "treble": -1}},
            {"type": "normalize", "parameters": {"target_level": -3}},
            {"type": "compress", "parameters": {"threshold": -20, "ratio": 4}},
            {"type": "pitch_shift", "parameters": {"semitones": 2}},
            {"type": "tempo_change", "parameters": {"tempo": 1.1}},
            {"type": "fade_in", "parameters": {"duration": 2}},
            {"type": "fade_out", "parameters": {"duration": 2, "start_time": 10}},
            {"type": "noise_reduction", "parameters": {"cutoff_frequency": 100}},
        ]

        tool = AudioEffects(input_path="/path/to/test_audio.wav", effects=effects)
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]["effects_applied"]) == 10
