"""Tests for url_metadata tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from tools.web_content.url_metadata import UrlMetadata
from shared.errors import ValidationError, APIError


class TestUrlMetadata:
    """Test suite for UrlMetadata."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_url(self) -> str:
        """Valid test URL."""
        return "http://example.com/file"

    @pytest.fixture
    def tool(self, valid_url: str) -> UrlMetadata:
        """Create tool instance with valid parameters."""
        return UrlMetadata(input=valid_url)

    # ========== HAPPY PATH ==========

    @patch("requests.head")
    def test_execute_success(self, mock_head, tool: UrlMetadata):
        """Test successful execution."""
        mock_response = MagicMock()
        mock_response.headers = {
            "Content-Type": "text/html",
            "Content-Length": "2048",
            "Content-Disposition": 'attachment; filename="example.html"',
        }
        mock_response.raise_for_status = MagicMock()
        mock_head.return_value = mock_response

        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["content_type"] == "text/html"
        assert result["result"]["size"] == 2048
        assert result["result"]["filename"] == "example.html"

    def test_metadata_correct(self, tool: UrlMetadata):
        """Test tool metadata."""
        assert tool.tool_name == "url_metadata"
        assert tool.tool_category == "web"

    # ========== ERROR CASES ==========

    def test_validation_error(self):
        """Test validation errors."""
        with pytest.raises(ValidationError):
            tool = UrlMetadata(input="invalid_url")
            tool.run()

    @patch("requests.head", side_effect=Exception("API failed"))
    def test_api_error_handled(self, mock_head, tool: UrlMetadata):
        """Test API error handling."""
        with pytest.raises(APIError):
            tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: UrlMetadata):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["content_type"] == "text/html"
        assert result["result"]["size"] == 1024
        assert result["result"]["filename"] == "mock_file.html"

    # ========== EDGE CASES ==========

    @patch("requests.head")
    def test_no_content_disposition(self, mock_head, tool: UrlMetadata):
        """Test when Content-Disposition header is missing."""
        mock_response = MagicMock()
        mock_response.headers = {
            "Content-Type": "application/json",
            "Content-Length": "512",
        }
        mock_response.raise_for_status = MagicMock()
        mock_head.return_value = mock_response

        result = tool.run()
        assert result["result"]["filename"] == "file"

    @patch("requests.head")
    def test_unknown_content_length(self, mock_head, tool: UrlMetadata):
        """Test when Content-Length is unknown."""
        mock_response = MagicMock()
        mock_response.headers = {
            "Content-Type": "application/json",
            "Content-Length": "unknown",
        }
        mock_response.raise_for_status = MagicMock()
        mock_head.return_value = mock_response

        result = tool.run()
        assert result["result"]["size"] == "unknown"

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "url,expected_filename",
        [
            ("http://example.com/file", "file"),
            ("http://example.com/", "unknown"),
            ("http://example.com/path/to/file.txt", "file.txt"),
        ],
    )
    @patch("requests.head")
    def test_filename_extraction(self, mock_head, url, expected_filename):
        """Test filename extraction from URL."""
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "text/plain", "Content-Length": "1024"}
        mock_response.raise_for_status = MagicMock()
        mock_head.return_value = mock_response

        tool = UrlMetadata(input=url)
        result = tool.run()
        assert result["result"]["filename"] == expected_filename
