"""Tests for crawler tool."""

import pytest
from unittest.mock import patch, Mock
from typing import Dict, Any

from tools.web_content.crawler import Crawler
from shared.errors import ValidationError, APIError


class TestCrawler:
    """Test suite for Crawler."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_url(self) -> str:
        """Valid URL for testing."""
        return "https://example.com"

    @pytest.fixture
    def tool(self, valid_url: str) -> Crawler:
        """Create tool instance with valid parameters."""
        return Crawler(input=valid_url)

    @pytest.fixture
    def mock_response(self) -> Mock:
        """Mock requests response."""
        mock = Mock()
        mock.content = b"<html><body><p>Test content</p></body></html>"
        mock.raise_for_status = Mock()
        return mock

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: Crawler, mock_response: Mock):
        """Test successful execution."""
        with patch("requests.get", return_value=mock_response):
            result = tool.run()
            assert result["success"] is True
            assert "result" in result
            assert "content" in result["result"]
            assert "Test content" in result["result"]["content"]

    def test_metadata_correct(self, tool: Crawler):
        """Test tool metadata."""
        assert tool.tool_name == "crawler"
        assert tool.tool_category == "web"
        assert (
            tool.tool_description
            == "Retrieve and convert content from URLs into readable format"
        )

    # ========== ERROR CASES ==========

    def test_validation_error(self):
        """Test validation errors."""
        with pytest.raises(ValidationError):
            tool = Crawler(input="invalid-url")
            tool.run()

    def test_api_error_handled(self, tool: Crawler):
        """Test API error handling."""
        with patch("requests.get", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: Crawler):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "mock" in result["result"]

    # ========== EDGE CASES ==========

    def test_empty_content(self, tool: Crawler):
        """Test handling of empty content."""
        with patch("requests.get", return_value=Mock(content=b"")):
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["content"] == ""

    def test_unicode_content(self, tool: Crawler):
        """Test handling of Unicode content."""
        unicode_content = "<html><body><p>こんにちは世界</p></body></html>"
        with patch(
            "requests.get", return_value=Mock(content=unicode_content.encode("utf-8"))
        ):
            result = tool.run()
            assert result["success"] is True
            assert "こんにちは世界" in result["result"]["content"]

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "url,expected_valid",
        [
            ("https://valid-url.com", True),
            ("http://another-valid-url.com", True),
            ("ftp://invalid-url.com", False),
            ("", False),
            ("invalid-url", False),
        ],
    )
    def test_url_validation(self, url: str, expected_valid: bool):
        """Test URL validation with various inputs."""
        if expected_valid:
            tool = Crawler(input=url)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(ValidationError):
                tool = Crawler(input=url)
                tool.run()
