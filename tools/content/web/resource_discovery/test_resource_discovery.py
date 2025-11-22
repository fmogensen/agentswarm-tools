"""Tests for resource_discovery tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
import os
from pydantic import ValidationError as PydanticValidationError

from tools.web.resource_discovery import ResourceDiscovery
from shared.errors import ValidationError, APIError


class TestResourceDiscovery:
    """Test suite for ResourceDiscovery."""

    # ========== FIXTURES ==========

    @pytest.fixture(autouse=True)
    def disable_rate_limiting(self):
        """Disable rate limiting for all tests."""
        with patch("shared.base.get_rate_limiter") as mock_limiter:
            mock_limiter.return_value.check_rate_limit.return_value = None
            yield

    @pytest.fixture
    def valid_url(self) -> str:
        return "https://example.com"

    @pytest.fixture
    def tool(self, valid_url: str) -> ResourceDiscovery:
        return ResourceDiscovery(input=valid_url)

    @pytest.fixture
    def mock_html(self) -> str:
        return """
            <html>
                <body>
                    <a href="audio.mp3">Audio</a>
                    <a href="video.mp4">Video</a>
                    <img src="image.jpg" />
                    <source src="clip.mov" />
                    <a href="document.pdf">Document</a>
                </body>
            </html>
        """

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_url: str):
        tool = ResourceDiscovery(input=valid_url)
        assert tool.input == valid_url
        assert tool.tool_name == "resource_discovery"
        assert tool.tool_category == "web"

    # ========== HAPPY PATH ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"}, clear=False)
    @patch("tools.web.resource_discovery.resource_discovery.requests.get")
    def test_execute_success(self, mock_get, tool: ResourceDiscovery, mock_html: str):
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert "resources" in result["result"]
        assert len(result["result"]["resources"]) == 5

    # ========== MOCK MODE ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"}, clear=False)
    def test_mock_mode(self, tool: ResourceDiscovery):
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert len(result["result"]["resources"]) == 2

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"}, clear=False)
    @patch("tools.web.resource_discovery.resource_discovery.requests.get")
    def test_real_mode(self, mock_get, tool: ResourceDiscovery, mock_html: str):
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        result = tool.run()
        assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_input", [None, 123])
    def test_pydantic_validation_error(self, bad_input):
        """Test that Pydantic rejects invalid types."""
        with pytest.raises(PydanticValidationError):
            ResourceDiscovery(input=bad_input)

    def test_custom_validation_error_invalid_url(self):
        """Test that our custom validation rejects non-http URLs.

        BaseTool.run() catches ValidationError and returns error dict.
        """
        tool = ResourceDiscovery(input="ftp://invalid.com")
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_custom_validation_error_empty_input(self):
        """Test that our custom validation rejects empty input.

        BaseTool.run() catches ValidationError and returns error dict.
        """
        tool = ResourceDiscovery(input="")
        result = tool.run()
        assert result["success"] is False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    # ========== ERROR CASES ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"}, clear=False)
    @patch("tools.web.resource_discovery.resource_discovery.requests.get", side_effect=Exception("Network error"))
    def test_api_error(self, mock_get, tool: ResourceDiscovery):
        """Test that API errors are caught and returned in error format."""
        result = tool.run()
        assert result["success"] is False
        assert "error" in result
        assert result["error"]["code"] == "API_ERROR"

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"}, clear=False)
    def test_process_raises_api_error(self, tool: ResourceDiscovery):
        """Test that exceptions in _process are wrapped as API errors."""
        with patch.object(tool, "_process", side_effect=Exception("Failure")):
            result = tool.run()
            assert result["success"] is False
            assert result["error"]["code"] == "API_ERROR"

    # ========== EDGE CASES ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"}, clear=False)
    @patch("tools.web.resource_discovery.resource_discovery.requests.get")
    def test_no_media_links(self, mock_get, tool: ResourceDiscovery):
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>No media here</p></body></html>"
        mock_get.return_value = mock_response

        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]["resources"]) == 0

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"}, clear=False)
    @patch("tools.web.resource_discovery.resource_discovery.requests.get")
    def test_relative_urls_resolved(self, mock_get, tool: ResourceDiscovery):
        mock_response = MagicMock()
        mock_response.text = '<a href="/files/test.mp3">file</a>'
        mock_get.return_value = mock_response

        result = tool.run()
        res = result["result"]["resources"][0]
        assert res["url"] == "https://example.com/files/test.mp3"

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "extension,expected_type",
        [
            ("song.mp3", "audio"),
            ("track.wav", "audio"),
            ("movie.mp4", "video"),
            ("clip.mov", "video"),
            ("pic.jpg", "image"),
            ("file.zip", "archive"),
            ("doc.pdf", "document"),
        ],
    )
    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"}, clear=False)
    @patch("tools.web.resource_discovery.resource_discovery.requests.get")
    def test_media_type_detection(
        self, mock_get, tool: ResourceDiscovery, extension, expected_type
    ):
        mock_response = MagicMock()
        mock_response.text = f'<a href="{extension}">file</a>'
        mock_get.return_value = mock_response

        result = tool.run()
        res = result["result"]["resources"][0]

        assert res["type"] == expected_type
        assert res["filename"] == extension

    # ========== INTEGRATION TESTS ==========

    def test_error_formatting_integration(self, tool: ResourceDiscovery):
        """Test that unexpected errors are formatted correctly by BaseTool.run()."""
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert result["success"] is False
            assert "error" in result
            assert result["error"]["code"] == "UNEXPECTED_ERROR"
