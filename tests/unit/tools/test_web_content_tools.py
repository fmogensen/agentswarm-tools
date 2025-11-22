"""
Comprehensive unit tests for Web Content Tools category.

Tests all web content tools:
- crawler
- summarize_large_document
- url_metadata
- webpage_capture_screen
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from tools.content.web.crawler.crawler import Crawler
from tools.content.web.summarize_large_document.summarize_large_document import (
    SummarizeLargeDocument,
)
from tools.content.web.url_metadata.url_metadata import UrlMetadata
from tools.content.web.webpage_capture_screen.webpage_capture_screen import WebpageCaptureScreen

from shared.errors import ValidationError, APIError


# ========== Crawler Tests ==========


class TestCrawler:
    """Comprehensive tests for Crawler tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = Crawler(url="https://example.com", max_depth=2)
        assert tool.url == "https://example.com"
        assert tool.max_depth == 2
        assert tool.tool_name == "crawler"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters"""
        tool = Crawler(url="https://example.com")
        assert tool.url == "https://example.com"
        assert tool.max_depth == 0  # Default value

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = Crawler(url="https://example.com", max_depth=1)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty URL"""
        tool = Crawler(url="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = Crawler(url="not-a-valid-url")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_max_depth(self):
        """Test validation with invalid max_depth (out of range)"""
        with pytest.raises(PydanticValidationError):
            Crawler(url="https://example.com", max_depth=-1)

        with pytest.raises(PydanticValidationError):
            Crawler(url="https://example.com", max_depth=5)  # Max is 3

    @patch("shared.base.get_rate_limiter")
    @patch("tools.content.web.crawler.crawler.requests.get")
    def test_execute_live_mode_success(self, mock_get, mock_rate_limiter, monkeypatch):
        """Test execution with mocked HTTP requests"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        # Mock rate limiter to allow requests
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit = MagicMock()  # No-op
        mock_rate_limiter.return_value = mock_limiter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><a href='/page1'>Link</a></body></html>"  # BeautifulSoup needs content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        tool = Crawler(url="https://example.com", max_depth=1)
        result = tool.run()

        assert result["success"] is True

    @patch("shared.base.get_rate_limiter")
    @patch("tools.content.web.crawler.crawler.requests.get")
    def test_api_error_handling_network_failure(self, mock_get, mock_rate_limiter, monkeypatch):
        """Test handling of network failures"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        # Mock rate limiter to allow requests
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit = MagicMock()
        mock_rate_limiter.return_value = mock_limiter

        mock_get.side_effect = Exception("Connection error")

        tool = Crawler(url="https://example.com")
        result = tool.run()

        # Tool returns error response instead of raising after retries
        assert result["success"] is False
        assert "error" in result

    def test_edge_case_https_and_http(self, monkeypatch):
        """Test handling of both HTTP and HTTPS URLs"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        urls = ["https://example.com", "http://example.com", "https://subdomain.example.com"]

        for url in urls:
            tool = Crawler(url=url, max_depth=1)
            result = tool.run()
            assert result["success"] is True


# ========== SummarizeLargeDocument Tests ==========


class TestSummarizeLargeDocument:
    """Comprehensive tests for SummarizeLargeDocument tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = SummarizeLargeDocument(
            input="https://example.com/document.pdf"
        )
        assert tool.input == "https://example.com/document.pdf"
        assert tool.tool_name == "summarize_large_document"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = SummarizeLargeDocument(
            input="https://example.com/doc.pdf"
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty document URL"""
        tool = SummarizeLargeDocument(input="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = SummarizeLargeDocument(input="invalid-url")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("shared.base.get_rate_limiter")
    @patch("tools.content.web.summarize_large_document.summarize_large_document.requests.get")
    def test_execute_live_mode_success(self, mock_get, mock_rate_limiter, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        # Mock rate limiter to allow requests
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit = MagicMock()
        mock_rate_limiter.return_value = mock_limiter

        # Mock document download
        mock_get_response = MagicMock()
        mock_get_response.text = "Long document content here..."
        mock_get_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_get_response

        tool = SummarizeLargeDocument(
            input="https://example.com/doc.pdf"
        )
        result = tool.run()

        assert result["success"] is True


# ========== UrlMetadata Tests ==========


class TestUrlMetadata:
    """Comprehensive tests for UrlMetadata tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = UrlMetadata(url="https://example.com")
        assert tool.url == "https://example.com"
        assert tool.tool_name == "url_metadata"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = UrlMetadata(url="https://example.com/page")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty URL"""
        tool = UrlMetadata(url="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = UrlMetadata(url="not-a-url")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("shared.base.get_rate_limiter")
    @patch("tools.content.web.url_metadata.url_metadata.requests.head")
    def test_execute_live_mode_success(self, mock_head, mock_rate_limiter, monkeypatch):
        """Test execution with mocked HTTP request"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        # Mock rate limiter to allow requests
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit = MagicMock()
        mock_rate_limiter.return_value = mock_limiter

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "Content-Type": "text/html",
            "Content-Length": "1024",
            "Content-Disposition": 'attachment; filename="example.html"'
        }
        mock_response.raise_for_status = MagicMock()
        mock_head.return_value = mock_response

        tool = UrlMetadata(url="https://example.com")
        result = tool.run()

        assert result["success"] is True

    @patch("shared.base.get_rate_limiter")
    @patch("tools.content.web.url_metadata.url_metadata.requests.head")
    def test_api_error_handling_not_found(self, mock_head, mock_rate_limiter, monkeypatch):
        """Test handling of 404 errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        # Mock rate limiter to allow requests
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit = MagicMock()
        mock_rate_limiter.return_value = mock_limiter

        import requests
        mock_head.side_effect = requests.RequestException("Not found")

        tool = UrlMetadata(url="https://example.com/nonexistent")
        result = tool.run()

        # Tool returns error response instead of raising after retries
        assert result["success"] is False
        assert "error" in result

    def test_edge_case_urls_with_parameters(self, monkeypatch):
        """Test URLs with query parameters"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        urls = [
            "https://example.com?param=value",
            "https://example.com?a=1&b=2",
            "https://example.com/page?search=test#section",
        ]

        for url in urls:
            tool = UrlMetadata(url=url)
            result = tool.run()
            assert result["success"] is True


# ========== WebpageCaptureScreen Tests ==========


class TestWebpageCaptureScreen:
    """Comprehensive tests for WebpageCaptureScreen tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = WebpageCaptureScreen(
            input="https://example.com"
        )
        assert str(tool.input) == "https://example.com/"  # HttpUrl adds trailing slash
        assert tool.tool_name == "webpage_capture_screen"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = WebpageCaptureScreen(input="https://example.com")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty URL - Pydantic validates at init"""
        with pytest.raises(PydanticValidationError):
            WebpageCaptureScreen(input="")

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        with pytest.raises(PydanticValidationError):
            WebpageCaptureScreen(input="not-a-url")

    @patch("shared.base.get_rate_limiter")
    @patch("tools.content.web.webpage_capture_screen.webpage_capture_screen.webdriver.Chrome")
    def test_execute_live_mode_success(self, mock_chrome, mock_rate_limiter, monkeypatch):
        """Test execution with mocked Chrome webdriver"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        # Mock rate limiter to allow requests
        mock_limiter = MagicMock()
        mock_limiter.check_rate_limit = MagicMock()
        mock_rate_limiter.return_value = mock_limiter

        mock_driver = MagicMock()
        mock_driver.save_screenshot = MagicMock()
        mock_driver.quit = MagicMock()
        mock_chrome.return_value = mock_driver

        tool = WebpageCaptureScreen(input="https://example.com")
        result = tool.run()

        assert result["success"] is True
