"""Tests for understand_images tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Any, Dict
import os
from pydantic import ValidationError as PydanticValidationError

from tools.media_analysis.understand_images import UnderstandImages
from shared.errors import ValidationError, APIError


class TestUnderstandImages:
    """Test suite for UnderstandImages."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_url(self) -> str:
        return "https://example.com/image.png"

    @pytest.fixture
    def valid_instruction(self) -> str:
        return "Describe the image."

    @pytest.fixture
    def tool(self, valid_url: str, valid_instruction: str) -> UnderstandImages:
        return UnderstandImages(media_url=valid_url, instruction=valid_instruction)

    @pytest.fixture
    def fake_image_bytes(self) -> bytes:
        return b"FAKE_IMAGE_DATA"

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_url: str):
        tool = UnderstandImages(media_url=valid_url, instruction=None)
        assert tool.media_url == valid_url
        assert tool.instruction is None
        assert tool.tool_name == "understand_images"
        assert tool.tool_category == "media_analysis"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success_http(
        self, tool: UnderstandImages, fake_image_bytes: bytes
    ):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.content = fake_image_bytes
            mock_get.return_value = mock_resp

            result = tool.run()

        assert result["success"] is True
        assert result["result"]["image_size_bytes"] == len(fake_image_bytes)
        assert result["result"]["instruction"] == tool.instruction
        assert result["metadata"]["tool_name"] == "understand_images"

    def test_execute_success_aidrive(self, valid_instruction: str):
        tool = UnderstandImages(
            media_url="aidrive://my_image", instruction=valid_instruction
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["image_size_bytes"] == len(b"FAKE_AIDRIVE_IMAGE_DATA")

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: UnderstandImages):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_mock_disabled(self, tool: UnderstandImages):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.content = b"IMG"
            mock_get.return_value = mock_resp

            result = tool.run()
            assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    def test_invalid_media_url_empty(self):
        tool = UnderstandImages(media_url="", instruction=None)
        result = tool.run()
        assert result["success"] is False

    @pytest.mark.parametrize("url", ["ftp://invalid.com", "file://bad", "not_a_url"])
    def test_invalid_media_url_scheme(self, url: str):
        tool = UnderstandImages(media_url=url, instruction=None)
        result = tool.run()
        assert result["success"] is False

    def test_invalid_instruction_type(self, valid_url: str):
        with pytest.raises(PydanticValidationError):
            UnderstandImages(media_url=valid_url, instruction=123)

    # ========== API ERROR TESTS ==========

    def test_api_error_http_failure(self, tool: UnderstandImages):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_get.return_value = mock_resp

            result = tool.run()
            assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_process_exception(self, tool: UnderstandImages):
        with patch.object(tool, "_process", side_effect=Exception("Boom")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASE TESTS ==========

    def test_no_instruction(self, valid_url: str):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.content = b"IMGDATA"
            mock_get.return_value = mock_resp

            tool = UnderstandImages(media_url=valid_url, instruction=None)
            result = tool.run()

        assert result["result"]["instruction"] == "No instruction provided"
        assert result["result"]["instruction_applied"] is False

    def test_unicode_instruction(self, valid_url: str):
        instr = "描述图像内容"
        tool = UnderstandImages(media_url=valid_url, instruction=instr)

        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.content = b"DATA"
            mock_get.return_value = mock_resp

            result = tool.run()

        assert result["result"]["instruction"] == instr

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "media_url,valid",
        [
            ("https://valid.com/img.png", True),
            ("http://valid.com/img.png", True),
            ("aidrive://asset", True),
            ("ftp://invalid.com", False),
            ("", False),
        ],
    )
    def test_param_media_urls(self, media_url: str, valid: bool):
        tool = UnderstandImages(media_url=media_url, instruction=None)
        if valid:
            with patch("requests.get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.content = b"D"
                mock_get.return_value = mock_resp

                result = tool.run()
                assert result["success"] is True
        else:
            result = tool.run()
            assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    def test_error_wrapping_in_run(self, tool: UnderstandImages):
        with patch.object(tool, "_execute", side_effect=ValueError("Bad")):
            result = tool.run()
            assert result["success"] is False or "error" in result
