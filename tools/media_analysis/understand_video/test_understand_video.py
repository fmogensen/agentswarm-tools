"""Tests for understand_video tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Any, Dict

from tools.media_analysis.understand_video import UnderstandVideo
from shared.errors import ValidationError, APIError


class TestUnderstandVideo:
    """Test suite for UnderstandVideo."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_url(self) -> str:
        return "https://www.youtube.com/watch?v=ABCDEFGHIJK"

    @pytest.fixture
    def tool(self, valid_url: str) -> UnderstandVideo:
        return UnderstandVideo(media_url=valid_url, instruction="full transcript")

    @pytest.fixture
    def mock_api_response(self) -> list:
        return [{"start": 0, "text": "Hello world"}, {"start": 5, "text": "More text"}]

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization_success(self, valid_url: str):
        tool = UnderstandVideo(media_url=valid_url, instruction="test")
        assert tool.media_url == valid_url
        assert tool.instruction == "test"
        assert tool.tool_name == "understand_video"

    # ========== HAPPY PATH TESTS ==========

    @patch("requests.get")
    def test_execute_success(
        self, mock_get, tool: UnderstandVideo, mock_api_response: list
    ):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_api_response
        mock_get.return_value = mock_resp

        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert len(result["result"]["transcript"]) == 2
        assert result["metadata"]["tool_name"] == "understand_video"

    def test_metadata_correct(self, tool: UnderstandVideo):
        assert tool.tool_name == "understand_video"
        assert tool.tool_category == "media_analysis"
        assert "Extract transcript" in tool.tool_description

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: UnderstandVideo):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_url", ["", None, 123, "http://notyoutube.com"])
    def test_invalid_media_url_raises(self, bad_url: Any):
        with pytest.raises(ValidationError):
            tool = UnderstandVideo(media_url=bad_url, instruction="x")
            tool.run()

    def test_invalid_instruction_type(self, valid_url: str):
        with pytest.raises(ValidationError):
            tool = UnderstandVideo(media_url=valid_url, instruction=123)
            tool.run()

    # ========== _extract_video_id TESTS ==========

    @pytest.mark.parametrize(
        "url,vid",
        [
            ("https://youtube.com/watch?v=ABCDEFGHIJK", "ABCDEFGHIJK"),
            ("https://youtu.be/ABCDEFGHIJK", "ABCDEFGHIJK"),
        ],
    )
    def test_extract_video_id_valid(self, tool: UnderstandVideo, url: str, vid: str):
        assert tool._extract_video_id(url) == vid

    def test_extract_video_id_invalid(self, tool: UnderstandVideo):
        with pytest.raises(ValidationError):
            tool._extract_video_id("https://youtube.com/watch?v=BAD")

    # ========== _format_timestamp TESTS ==========

    @pytest.mark.parametrize(
        "seconds,expected", [(0, "00:00"), (5, "00:05"), (65, "01:05"), (600, "10:00")]
    )
    def test_format_timestamp(
        self, tool: UnderstandVideo, seconds: float, expected: str
    ):
        assert tool._format_timestamp(seconds) == expected

    # ========== ERROR HANDLING TESTS ==========

    @patch.object(UnderstandVideo, "_process", side_effect=Exception("API failed"))
    def test_api_error_wrapped(self, _, tool: UnderstandVideo):
        with pytest.raises(APIError):
            tool.run()

    @patch("requests.get")
    def test_api_status_error(self, mock_get, tool: UnderstandVideo):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.json.return_value = {}
        mock_get.return_value = mock_resp

        with pytest.raises(APIError):
            tool.run()

    # ========== EDGE CASE TESTS ==========

    def test_unicode_instruction(self, valid_url: str):
        tool = UnderstandVideo(media_url=valid_url, instruction="分析视频内容")
        assert tool.instruction == "分析视频内容"

    @patch("requests.get")
    def test_empty_transcript_return(self, mock_get, tool: UnderstandVideo):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp

        result = tool.run()
        assert result["success"] is True
        assert result["result"]["transcript"] == []

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "url,is_valid",
        [
            ("https://www.youtube.com/watch?v=ABCDEFGHIJK", True),
            ("https://youtu.be/ABCDEFGHIJK", True),
            ("not a url", False),
            ("https://google.com", False),
        ],
    )
    def test_url_validation(self, url: str, is_valid: bool):
        if is_valid:
            tool = UnderstandVideo(media_url=url)
            assert tool.media_url == url
        else:
            with pytest.raises(Exception):
                UnderstandVideo(media_url=url).run()

    # ========== INTEGRATION TESTS ==========

    def test_error_formatting_integration(self, tool: UnderstandVideo):
        with patch.object(tool, "_execute", side_effect=ValueError("bad")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
