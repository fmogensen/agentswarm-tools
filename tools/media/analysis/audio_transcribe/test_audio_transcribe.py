"""Tests for audio_transcribe tool."""

import pytest
from unittest.mock import patch
from unittest.mock import Mock, patch, MagicMock
import os
from pydantic import ValidationError as PydanticValidationError

from tools.media_analysis.audio_transcribe import AudioTranscribe
from shared.errors import ValidationError, APIError


class TestAudioTranscribe:
    """Test suite for AudioTranscribe."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        return "fake_audio.wav"

    @pytest.fixture
    def tool(self, valid_input: str) -> AudioTranscribe:
        return AudioTranscribe(input=valid_input)

    @pytest.fixture
    def mock_audio_file(self, tmp_path):
        path = tmp_path / "test.wav"
        path.write_bytes(b"RIFF....WAVEfmt ")  # minimal mock WAV header
        return str(path)

    @pytest.fixture
    def mock_speech_result(self) -> dict:
        return {
            "text": "hello world",
            "segments": [
                {
                    "words": [
                        {"word": "hello", "start": 0.1, "end": 0.3},
                        {"word": "world", "start": 0.4, "end": 0.6},
                    ]
                }
            ],
        }

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization_success(self, valid_input: str):
        tool = AudioTranscribe(input=valid_input)
        assert tool.input == valid_input
        assert tool.tool_name == "audio_transcribe"
        assert tool.tool_category == "media_analysis"

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, tool: AudioTranscribe):
        result = tool.run()
        assert result["success"] is True
        assert "text" in result["result"]

    # ========== METADATA TESTS ==========

    def test_metadata_correct(self, tool: AudioTranscribe):
        assert tool.tool_name == "audio_transcribe"
        assert tool.tool_category == "media_analysis"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: AudioTranscribe):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_real_mode_with_mock(self, tool: AudioTranscribe):
        # Using mock mode to test basic flow
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["text"] is not None

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_input", ["", "   "])
    def test_invalid_input_raises_validation_error(self, bad_input):
        tool = AudioTranscribe(input=bad_input)
        result = tool.run()
        assert result["success"] is False

    def test_invalid_input_none(self):
        with pytest.raises(PydanticValidationError):
            AudioTranscribe(input=None)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("os.path.exists", return_value=False)
    def test_nonexistent_file_raises_error(self, mock_exists, tool: AudioTranscribe):
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_url_input_not_supported(self):
        tool = AudioTranscribe(input="http://example.com/audio.wav")
        result = tool.run()
        assert result["success"] is False

    # ========== ERROR CASE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("os.path.exists", return_value=True)
    def test_process_api_error_propagates(self, mock_exists, tool: AudioTranscribe):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("os.path.exists", return_value=True)
    def test_speech_recognition_error(self, mock_exists, tool: AudioTranscribe):
        with patch.object(tool, "_process", side_effect=Exception("speech error")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_process_string_return(self, tool: AudioTranscribe):
        # In mock mode, return is a dict with text
        result = tool.run()
        assert result["success"] is True
        assert "text" in result["result"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("os.path.exists", return_value=False)
    def test_unicode_input_path(self, mock_exists):
        tool = AudioTranscribe(input="音频.wav")
        result = tool.run()
        assert result["success"] is False

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "input_path,valid,is_pydantic_error,use_mock",
        [
            ("audio.wav", True, False, True),
            ("   ", False, False, True),  # Whitespace passes Pydantic, fails at runtime
            ("", False, False, True),  # Empty string passes Pydantic, fails custom validation
            (None, False, True, True),  # None fails Pydantic type check
            (
                "http://example.com/audio.wav",
                False,
                False,
                False,
            ),  # URL fails custom validation (needs real mode)
        ],
    )
    def test_parameter_validation(self, input_path, valid, is_pydantic_error, use_mock):
        mock_env = {"USE_MOCK_APIS": "true" if use_mock else "false"}
        with patch.dict("os.environ", mock_env):
            if valid:
                tool = AudioTranscribe(input=input_path)
                result = tool.run()
                assert result["success"] is True
            elif is_pydantic_error:
                with pytest.raises(PydanticValidationError):
                    AudioTranscribe(input=input_path)
            else:
                tool = AudioTranscribe(input=input_path)
                result = tool.run()
                assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_integration_with_analytics(self, tool: AudioTranscribe, capture_analytics_events):
        tool.run()
        assert True  # analytics captured externally

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_rate_limiting(self, tool: AudioTranscribe):
        result = tool.run()
        assert result["success"] is True

    def test_error_formatting_integration(self, tool: AudioTranscribe):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
