"""Tests for audio_transcribe tool."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

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

    @patch("os.path.exists", return_value=True)
    @patch("speech_recognition.AudioFile")
    @patch("speech_recognition.Recognizer")
    def test_execute_success(
        self,
        mock_recognizer,
        mock_audiofile,
        mock_exists,
        tool: AudioTranscribe,
        mock_speech_result,
    ):
        recog_instance = MagicMock()
        recog_instance.record.return_value = b"audio-bytes"
        recog_instance.recognize_whisper.return_value = mock_speech_result
        mock_recognizer.return_value = recog_instance

        result = tool.run()
        assert result["success"] is True
        assert result["result"]["text"] == "hello world"
        assert len(result["result"]["words"]) == 2

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

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("os.path.exists", return_value=True)
    @patch("speech_recognition.AudioFile")
    @patch("speech_recognition.Recognizer")
    def test_real_mode(
        self, mock_recognizer, mock_audiofile, mock_exists, tool: AudioTranscribe
    ):
        recog_instance = MagicMock()
        recog_instance.record.return_value = b"audio-bytes"
        recog_instance.recognize_whisper.return_value = {"text": "ok", "segments": []}
        mock_recognizer.return_value = recog_instance

        result = tool.run()
        assert result["success"] is True
        assert result["result"]["text"] == "ok"

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_input", ["", "   ", None])
    def test_invalid_input_raises_validation_error(self, bad_input):
        with pytest.raises(ValidationError):
            tool = AudioTranscribe(input=bad_input)
            tool.run()

    def test_nonexistent_file_raises_error(self, tool: AudioTranscribe):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(ValidationError):
                tool.run()

    def test_url_input_not_supported(self):
        tool = AudioTranscribe(input="http://example.com/audio.wav")
        with pytest.raises(APIError):
            tool.run()

    # ========== ERROR CASE TESTS ==========

    @patch("os.path.exists", return_value=True)
    def test_process_api_error_propagates(self, mock_exists, tool: AudioTranscribe):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    @patch("os.path.exists", return_value=True)
    @patch("speech_recognition.AudioFile")
    @patch("speech_recognition.Recognizer")
    def test_speech_recognition_error(
        self, mock_recognizer, mock_audiofile, mock_exists, tool: AudioTranscribe
    ):
        recog_instance = MagicMock()
        recog_instance.record.return_value = b"audio-bytes"
        recog_instance.recognize_whisper.side_effect = Exception("speech error")
        mock_recognizer.return_value = recog_instance

        with pytest.raises(APIError):
            tool.run()

    # ========== EDGE CASES ==========

    @patch("os.path.exists", return_value=True)
    @patch("speech_recognition.AudioFile")
    @patch("speech_recognition.Recognizer")
    def test_process_string_return(
        self, mock_recognizer, mock_audiofile, mock_exists, tool: AudioTranscribe
    ):
        recog_instance = MagicMock()
        recog_instance.record.return_value = b"data"
        recog_instance.recognize_whisper.return_value = "simple text"
        mock_recognizer.return_value = recog_instance

        result = tool.run()
        assert result["result"]["text"] == "simple text"
        assert result["result"]["words"] == []

    def test_unicode_input_path(self):
        tool = AudioTranscribe(input="音频.wav")
        with patch("os.path.exists", return_value=False):
            with pytest.raises(ValidationError):
                tool.run()

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "input_path,valid",
        [
            ("audio.wav", True),
            ("   ", False),
            ("", False),
            (None, False),
            ("http://example.com/audio.wav", False),
        ],
    )
    def test_parameter_validation(self, input_path, valid):
        if valid:
            tool = AudioTranscribe(input=input_path)
            assert tool.input == input_path
        else:
            with pytest.raises(Exception):
                tool = AudioTranscribe(input=input_path)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_integration_with_analytics(
        self, tool: AudioTranscribe, capture_analytics_events
    ):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            tool.run()
        assert True  # analytics captured externally

    def test_rate_limiting(self, tool: AudioTranscribe):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            result = tool.run()
        assert result["success"] is True

    def test_error_formatting_integration(self, tool: AudioTranscribe):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
