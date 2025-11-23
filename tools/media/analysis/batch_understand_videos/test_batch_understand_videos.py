"""Tests for batch_understand_videos tool."""

from typing import Any, Dict
from unittest.mock import patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.media_analysis.batch_understand_videos import BatchUnderstandVideos


class TestBatchUnderstandVideos:
    """Test suite for BatchUnderstandVideos."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_urls(self) -> str:
        return "https://youtube.com/watch?v=abc123, https://youtu.be/xyz789"

    @pytest.fixture
    def tool(self, valid_urls: str) -> BatchUnderstandVideos:
        return BatchUnderstandVideos(media_url=valid_urls, instruction="Summarize videos")

    @pytest.fixture
    def mock_env_off(self):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "false"}):
            yield

    @pytest.fixture
    def mock_env_on(self):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            yield

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_urls: str):
        tool = BatchUnderstandVideos(media_url=valid_urls, instruction="Test instruction")
        assert tool.media_url == valid_urls
        assert tool.instruction == "Test instruction"
        assert tool.tool_name == "batch_understand_videos"
        assert tool.tool_category == "media_analysis"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool: BatchUnderstandVideos, mock_env_off):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "videos" in result["result"]
        assert result["metadata"]["video_count"] == 2

    def test_execute_without_instruction(self, valid_urls: str, mock_env_off):
        tool = BatchUnderstandVideos(media_url=valid_urls)
        result = tool.run()
        videos = result["result"]["videos"]
        assert videos[0]["extracted_info"] == "No instruction provided"

    def test_metadata_correct(self, tool: BatchUnderstandVideos):
        assert tool.tool_name == "batch_understand_videos"
        assert tool.tool_category == "media_analysis"

    # ========== MOCK MODE TESTS ==========

    def test_mock_mode(self, tool: BatchUnderstandVideos, mock_env_on):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True
        assert len(result["result"]["videos"]) == 2

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_url", ["", "not-a-url", "http://example.com/video"])
    def test_invalid_media_url(self, bad_url: str):
        tool = BatchUnderstandVideos(media_url=bad_url)
        result = tool.run()
        assert result["success"] is False

    def test_instruction_invalid_type(self, valid_urls: str):
        with pytest.raises(PydanticValidationError):
            BatchUnderstandVideos(media_url=valid_urls, instruction=123)

    def test_empty_after_split(self):
        tool = BatchUnderstandVideos(media_url=" , , ")
        result = tool.run()
        assert result["success"] is False

    @pytest.mark.parametrize(
        "url",
        [
            "https://youtube.com/watch?v=validid",
            "https://youtu.be/validid",
        ],
    )
    def test_extract_video_id_valid(self, url: str):
        tool = BatchUnderstandVideos(media_url=url, instruction="test")
        assert tool._extract_video_id(url) == "validid"

    def test_extract_video_id_invalid(self):
        tool = BatchUnderstandVideos(media_url="https://youtube.com/noid", instruction="test")
        # _extract_video_id raises ValidationError directly when called internally
        try:
            tool._extract_video_id("https://youtube.com/noid")
            assert False, "Expected ValidationError"
        except ValidationError:
            pass

    # ========== ERROR HANDLING TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_from_process(self, tool: BatchUnderstandVideos, mock_env_off):
        with patch.object(tool, "_process", side_effect=Exception("failure")):
            result = tool.run()
            assert result["success"] is False

    def test_process_video_failure(self, tool: BatchUnderstandVideos, mock_env_off):
        with patch.object(tool, "_extract_video_id", side_effect=Exception("bad id")):
            result = tool.run()
            assert result["success"] is False

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "urls,expected_count",
        [
            ("https://youtube.com/watch?v=A", 1),
            (
                "https://youtu.be/A, https://youtu.be/B, https://youtube.com/watch?v=C",
                3,
            ),
        ],
    )
    def test_multiple_url_handling(self, urls: str, expected_count: int, mock_env_off):
        tool = BatchUnderstandVideos(media_url=urls, instruction="test")
        result = tool.run()
        assert len(result["result"]["videos"]) == expected_count

    # ========== EDGE CASE TESTS ==========

    def test_unicode_instruction(self, valid_urls: str, mock_env_off):
        tool = BatchUnderstandVideos(media_url=valid_urls, instruction="分析这些视频")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["instruction_used"] == "分析这些视频"

    def test_special_characters_instruction(self, valid_urls: str, mock_env_off):
        instruction = "@#$%^&* Extract!"
        tool = BatchUnderstandVideos(media_url=valid_urls, instruction=instruction)
        result = tool.run()
        assert result["result"]["instruction_used"] == instruction

    def test_long_instruction(self, valid_urls: str, mock_env_off):
        instruction = "a" * 500
        tool = BatchUnderstandVideos(media_url=valid_urls, instruction=instruction)
        result = tool.run()
        assert result["success"] is True

    # ========== INTEGRATION TESTS ==========

    def test_integration_real_mode(self, tool: BatchUnderstandVideos, mock_env_off):
        result = tool.run()
        assert result["success"] is True

    def test_error_formatting_integration(self, tool: BatchUnderstandVideos):
        with patch.object(tool, "_execute", side_effect=ValueError("boom")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
