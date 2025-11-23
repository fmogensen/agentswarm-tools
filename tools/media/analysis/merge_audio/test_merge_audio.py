"""Tests for merge_audio tool."""

import json
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pytest

from shared.errors import APIError, ValidationError
from tools.media_analysis.merge_audio import MergeAudio


class TestMergeAudio:
    """Test suite for MergeAudio."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input_json(self) -> str:
        return json.dumps(
            {
                "clips": [
                    {"path": "audio1.mp3", "start": 0, "gain": -3},
                    {"path": "audio2.wav", "start": 1000},
                ],
                "output_format": "mp3",
            }
        )

    @pytest.fixture
    def tool(self, valid_input_json: str) -> MergeAudio:
        return MergeAudio(input=valid_input_json)

    @pytest.fixture
    def mock_audio(self):
        seg = MagicMock()
        seg.__len__.return_value = 1000
        seg.apply_gain.return_value = seg
        return seg

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self, valid_input_json: str):
        tool = MergeAudio(input=valid_input_json)
        assert tool.input == valid_input_json
        assert tool.tool_name == "merge_audio"
        assert tool.tool_category == "media_analysis"

    # ========== HAPPY PATH TESTS ==========

    @patch("tools.media_analysis.merge_audio.AudioSegment")
    def test_execute_success(self, mock_audio_seg, tool, mock_audio):
        mock_audio_seg.from_file.return_value = mock_audio
        mock_audio_seg.silent.return_value = mock_audio
        mock_audio.overlay.return_value = mock_audio
        mock_audio.export.return_value = None

        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result
        assert result["result"]["format"] == "mp3"

    @patch("tools.media_analysis.merge_audio.AudioSegment")
    def test_metadata_correct(self, mock_audio_seg, tool, mock_audio):
        mock_audio_seg.from_file.return_value = mock_audio
        mock_audio_seg.silent.return_value = mock_audio
        mock_audio.overlay.return_value = mock_audio
        mock_audio.export.return_value = None

        result = tool.run()
        assert result["metadata"]["tool_name"] == "merge_audio"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["metadata"]["mock_mode"] is True

    # ========== ERROR CASES ==========

    def test_invalid_json_validation_error(self):
        with pytest.raises(ValidationError):
            tool = MergeAudio(input="not-json")
            tool.run()

    def test_missing_clips_validation_error(self):
        with pytest.raises(ValidationError):
            tool = MergeAudio(input=json.dumps({"wrong": []}))
            tool.run()

    def test_clip_missing_path_error(self):
        bad = json.dumps({"clips": [{"start": 0}]})
        with pytest.raises(ValidationError):
            MergeAudio(input=bad).run()

    def test_invalid_start_type(self):
        bad = json.dumps({"clips": [{"path": "a.mp3", "start": "wrong"}]})
        with pytest.raises(ValidationError):
            MergeAudio(input=bad).run()

    def test_invalid_gain_type(self):
        bad = json.dumps({"clips": [{"path": "a.mp3", "gain": "bad"}]})
        with pytest.raises(ValidationError):
            MergeAudio(input=bad).run()

    @patch(
        "tools.media_analysis.merge_audio.AudioSegment.from_file",
        side_effect=Exception("Load failed"),
    )
    def test_audio_load_error(self, mock_seg, tool):
        with pytest.raises(APIError):
            tool.run()

    def test_no_clips_error(self):
        with pytest.raises(ValidationError):
            MergeAudio(input=json.dumps({"clips": []})).run()

    @patch.object(MergeAudio, "_process", side_effect=Exception("API failure"))
    def test_api_error_handled(self, mock_proc, tool):
        with pytest.raises(APIError):
            tool.run()

    # ========== EDGE CASE TESTS ==========

    @patch("tools.media_analysis.merge_audio.AudioSegment")
    def test_single_clip(self, mock_audio_seg, mock_audio):
        input_json = json.dumps({"clips": [{"path": "a.mp3", "start": 0}], "output_format": "wav"})
        mock_audio_seg.from_file.return_value = mock_audio
        mock_audio_seg.silent.return_value = mock_audio
        mock_audio.overlay.return_value = mock_audio

        tool = MergeAudio(input=input_json)
        result = tool.run()
        assert result["result"]["format"] == "wav"

    @patch("tools.media_analysis.merge_audio.AudioSegment")
    def test_large_start_time(self, mock_audio_seg, mock_audio):
        mock_audio_seg.from_file.return_value = mock_audio
        mock_audio_seg.silent.return_value = mock_audio
        mock_audio.overlay.return_value = mock_audio

        inp = json.dumps({"clips": [{"path": "a.mp3", "start": 999999}], "output_format": "mp3"})

        tool = MergeAudio(input=inp)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "field_value,valid",
        [
            ("{}", False),
            (json.dumps({"clips": "not-a-list"}), False),
            (json.dumps({"clips": [{"path": 123}]}), False),
            (json.dumps({"clips": [{"path": "a.mp3", "gain": None}]}), True),
        ],
    )
    def test_param_validation(self, field_value, valid):
        if valid:
            tool = MergeAudio(input=field_value)
            with patch("tools.media_analysis.merge_audio.AudioSegment.from_file") as m:
                seg = MagicMock()
                seg.__len__.return_value = 1
                m.return_value = seg
                MergeAudio(input=field_value).run()
        else:
            with pytest.raises(Exception):
                MergeAudio(input=field_value).run()

    # ========== INTEGRATION TESTS ==========

    @patch("tools.media_analysis.merge_audio.AudioSegment")
    def test_integration_processing(self, mock_audio_seg, mock_audio, tool):
        mock_audio_seg.from_file.return_value = mock_audio
        mock_audio_seg.silent.return_value = mock_audio
        mock_audio.overlay.return_value = mock_audio

        result = tool.run()
        assert result["success"] is True
        assert "duration_ms" in result["result"]

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("boom")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
