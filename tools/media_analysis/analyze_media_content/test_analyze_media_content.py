"""Tests for analyze_media_content tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any

from tools.media_analysis.analyze_media_content import AnalyzeMediaContent
from shared.errors import ValidationError, APIError


class TestAnalyzeMediaContent:
    """Test suite for AnalyzeMediaContent."""

    # ========= FIXTURES =========

    @pytest.fixture
    def valid_url(self) -> str:
        return "http://example.com/media.jpg"

    @pytest.fixture
    def instruction(self) -> str:
        return "Identify objects"

    @pytest.fixture
    def tool(self, valid_url: str, instruction: str) -> AnalyzeMediaContent:
        return AnalyzeMediaContent(media_url=valid_url, instruction=instruction)

    # ========= INITIALIZATION =========

    def test_tool_initialization(self, valid_url: str):
        tool = AnalyzeMediaContent(media_url=valid_url, instruction=None)
        assert tool.media_url == valid_url
        assert tool.instruction is None
        assert tool.tool_name == "analyze_media_content"

    def test_tool_metadata(self, tool: AnalyzeMediaContent):
        assert tool.tool_name == "analyze_media_content"
        assert tool.tool_category == "media_analysis"
        assert (
            tool.tool_description
            == "Deep analysis of images, audio, and video with custom requirements"
        )

    # ========= HAPPY PATH =========

    def test_execute_success(self, tool: AnalyzeMediaContent):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result
        assert result["metadata"]["media_url"] == tool.media_url

    def test_process_logic(self, tool: AnalyzeMediaContent):
        result = tool.run()
        features = result["result"]["detected_features"]
        assert isinstance(features, list)
        assert len(features) > 0

    # ========= MOCK MODE =========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: AnalyzeMediaContent):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["analysis"] == "This is a mock analysis result"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: AnalyzeMediaContent):
        result = tool.run()
        assert result["success"] is True
        assert "detected_features" in result["result"]

    # ========= VALIDATION TESTS =========

    @pytest.mark.parametrize("url", [None, "", 123, "ftp://invalid.com"])
    def test_invalid_media_url(self, url):
        with pytest.raises(ValidationError):
            tool = AnalyzeMediaContent(media_url=url, instruction="Test")
            tool.run()

    def test_invalid_instruction_type(self, valid_url):
        with pytest.raises(ValidationError):
            tool = AnalyzeMediaContent(media_url=valid_url, instruction=123)
            tool.run()

    # ========= API ERROR =========

    def test_api_error(self, tool: AnalyzeMediaContent):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError) as exc:
                tool.run()
            assert "API failed" in str(exc.value)

    # ========= EDGE CASES =========

    def test_instruction_none(self, valid_url):
        tool = AnalyzeMediaContent(media_url=valid_url, instruction=None)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["instruction"] == "Automatic analysis"

    def test_unicode_instruction(self, valid_url):
        tool = AnalyzeMediaContent(media_url=valid_url, instruction="分析内容")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["instruction"] == "分析内容"

    def test_special_characters_instruction(self, valid_url):
        text = "@#$%^&*()!"
        tool = AnalyzeMediaContent(media_url=valid_url, instruction=text)
        result = tool.run()
        assert result["success"] is True

    # ========= PARAMETRIZED TESTS =========

    @pytest.mark.parametrize(
        "media_url,instruction,valid",
        [
            ("http://example.com/a.jpg", "Test", True),
            ("https://example.com/a.mp4", None, True),
            ("badurl", "Test", False),
            ("ftp://site.com/file", None, False),
            ("", "Test", False),
        ],
    )
    def test_param_validation(self, media_url, instruction, valid):
        if valid:
            tool = AnalyzeMediaContent(media_url=media_url, instruction=instruction)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = AnalyzeMediaContent(media_url=media_url, instruction=instruction)
                tool.run()

    # ========= INTEGRATION TESTS =========

    def test_integration_basic_flow(self, tool: AnalyzeMediaContent):
        result = tool.run()
        assert result["success"] is True
        assert "media_url" in result["metadata"]

    def test_error_formatting(self, tool: AnalyzeMediaContent):
        with patch.object(tool, "_execute", side_effect=ValueError("Bad")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
