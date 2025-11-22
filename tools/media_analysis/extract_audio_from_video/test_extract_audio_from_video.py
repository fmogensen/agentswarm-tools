"""Tests for extract_audio_from_video tool."""

import pytest
from unittest.mock import patch, MagicMock
import os
from pydantic import ValidationError as PydanticValidationError

from tools.media_analysis.extract_audio_from_video import ExtractAudioFromVideo
from shared.errors import ValidationError, APIError


class TestExtractAudioFromVideo:
    """Test suite for ExtractAudioFromVideo."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def fake_video_path(self, tmp_path):
        """Create a fake valid video file."""
        path = tmp_path / "video.mp4"
        path.write_text("fake data")
        return str(path)

    @pytest.fixture
    def tool(self, fake_video_path) -> ExtractAudioFromVideo:
        """Create tool instance."""
        return ExtractAudioFromVideo(input=fake_video_path)

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization_success(self, fake_video_path):
        tool = ExtractAudioFromVideo(input=fake_video_path)
        assert tool.input == fake_video_path
        assert tool.tool_name == "extract_audio_from_video"
        assert tool.tool_category == "media_analysis"

    def test_metadata_correct(self, tool):
        assert tool.tool_name == "extract_audio_from_video"
        assert tool.tool_category == "media_analysis"
        assert tool.tool_description == "Extract audio track from video files to MP3"

    # ========== VALIDATION TESTS ==========

    def test_invalid_input_empty(self):
        tool = ExtractAudioFromVideo(input="")
        result = tool.run()
        assert result["success"] is False

    @pytest.mark.parametrize("invalid_input", [None, 123, [], {}])
    def test_invalid_input_wrong_type(self, invalid_input):
        with pytest.raises(PydanticValidationError):
            ExtractAudioFromVideo(input=invalid_input)

    def test_input_file_missing(self, tmp_path):
        nonexistent = str(tmp_path / "missing.mp4")
        tool = ExtractAudioFromVideo(input=nonexistent)
        result = tool.run()
        assert result["success"] is False

    def test_invalid_extension(self, tmp_path):
        bad_file = tmp_path / "not_video.txt"
        bad_file.write_text("data")
        tool = ExtractAudioFromVideo(input=str(bad_file))
        result = tool.run()
        assert result["success"] is False

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock_results(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True
        assert result["result"]["output_file"].endswith(".mock_audio.mp3")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_mock_off_falls_back_to_real_process(self, tool):
        with patch.object(tool, "_process", return_value={"output_file": "x.mp3"}):
            result = tool.run()
        assert result["success"] is True
        assert result["result"]["output_file"] == "x.mp3"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            mock_run.return_value.stdout = "ok"

            result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["result"]["output_file"].endswith(".mp3")
        assert "metadata" in result

    # ========== PROCESS TESTS ==========

    def test_process_ffmpeg_failure(self, tool):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = "ffmpeg error"

        with patch("subprocess.run", return_value=mock_proc):
            result = tool.run()
            assert result["success"] is False

    def test_process_ffmpeg_not_found(self, tool):
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            result = tool.run()
            assert result["success"] is False

    def test_process_unexpected_exception(self, tool):
        with patch("subprocess.run", side_effect=RuntimeError("boom")):
            result = tool.run()
            assert result["success"] is False

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize("ext", [".mp4", ".mov", ".mkv", ".avi", ".webm"])
    def test_valid_extensions(self, tmp_path, ext):
        f = tmp_path / ("file" + ext)
        f.write_text("x")
        tool = ExtractAudioFromVideo(input=str(f))

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_filename(self, tmp_path):
        f = tmp_path / "测试视频.mp4"
        f.write_text("x")
        tool = ExtractAudioFromVideo(input=str(f))

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            result = tool.run()

        assert result["success"] is True

    def test_special_characters_in_filename(self, tmp_path):
        f = tmp_path / "video @#$%.mp4"
        f.write_text("x")
        tool = ExtractAudioFromVideo(input=str(f))

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            result = tool.run()

        assert result["success"] is True

    # ========== INTEGRATION TESTS ==========

    def test_integration_error_formatting(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("error")):
            result = tool.run()
            assert isinstance(result, dict)
            assert result.get("success") is False or "error" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_process_integration(self, fake_video_path):
        tool = ExtractAudioFromVideo(input=fake_video_path)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stderr = ""
            r = tool.run()

        assert r["success"] is True
