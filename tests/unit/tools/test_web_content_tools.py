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
        tool = Crawler(url="https://example.com", max_depth=2, max_pages=10)
        assert tool.url == "https://example.com"
        assert tool.max_depth == 2
        assert tool.max_pages == 10
        assert tool.tool_name == "crawler"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters"""
        tool = Crawler(url="https://example.com")
        assert tool.url == "https://example.com"
        assert tool.max_depth == 1  # Default value
        assert tool.max_pages == 50  # Default value

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = Crawler(url="https://example.com", max_depth=1, max_pages=5)
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
        """Test validation with invalid max_depth"""
        with pytest.raises(ValidationError):
            Crawler(url="https://example.com", max_depth=0)

    def test_validate_parameters_invalid_max_pages(self):
        """Test validation with invalid max_pages"""
        with pytest.raises(ValidationError):
            Crawler(url="https://example.com", max_pages=0)

    @patch("tools.content.web.crawler.crawler.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked HTTP requests"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><a href='/page1'>Link</a></body></html>"
        mock_get.return_value = mock_response

        tool = Crawler(url="https://example.com", max_depth=1, max_pages=2)
        result = tool.run()

        assert result["success"] is True

    @patch("tools.content.web.crawler.crawler.requests.get")
    def test_api_error_handling_network_failure(self, mock_get, monkeypatch):
        """Test handling of network failures"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        mock_get.side_effect = Exception("Connection error")

        tool = Crawler(url="https://example.com")
        with pytest.raises(APIError):
            tool.run()

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
            document_url="https://example.com/document.pdf", summary_length="medium"
        )
        assert tool.document_url == "https://example.com/document.pdf"
        assert tool.summary_length == "medium"
        assert tool.tool_name == "summarize_large_document"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = SummarizeLargeDocument(
            document_url="https://example.com/doc.pdf", summary_length="short"
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty document URL"""
        tool = SummarizeLargeDocument(document_url="", summary_length="medium")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = SummarizeLargeDocument(document_url="invalid-url", summary_length="medium")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_summary_length(self):
        """Test validation with invalid summary length"""
        tool = SummarizeLargeDocument(
            document_url="https://example.com/doc.pdf", summary_length="invalid"
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.content.web.summarize_large_document.summarize_large_document.requests.get")
    @patch("tools.content.web.summarize_large_document.summarize_large_document.requests.post")
    def test_execute_live_mode_success(self, mock_post, mock_get, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("SUMMARIZATION_API_KEY", "test_key")

        # Mock document download
        mock_get_response = MagicMock()
        mock_get_response.content = b"Long document content here..."
        mock_get.return_value = mock_get_response

        # Mock summarization API
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {"summary": "This is a summary of the document."}
        mock_post.return_value = mock_post_response

        tool = SummarizeLargeDocument(
            document_url="https://example.com/doc.pdf", summary_length="short"
        )
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_different_summary_lengths(self, monkeypatch):
        """Test different summary length options"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        lengths = ["short", "medium", "long"]

        for length in lengths:
            tool = SummarizeLargeDocument(
                document_url="https://example.com/doc.pdf", summary_length=length
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

    @patch("tools.content.web.url_metadata.url_metadata.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked HTTP request"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
        <head>
            <title>Example Page</title>
            <meta name="description" content="This is an example page">
            <meta property="og:image" content="https://example.com/image.jpg">
        </head>
        </html>
        """
        mock_get.return_value = mock_response

        tool = UrlMetadata(url="https://example.com")
        result = tool.run()

        assert result["success"] is True

    @patch("tools.content.web.url_metadata.url_metadata.requests.get")
    def test_api_error_handling_not_found(self, mock_get, monkeypatch):
        """Test handling of 404 errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not found")
        mock_get.return_value = mock_response

        tool = UrlMetadata(url="https://example.com/nonexistent")
        with pytest.raises(APIError):
            tool.run()

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
            url="https://example.com", width=1920, height=1080, task_summary="Capture homepage"
        )
        assert tool.url == "https://example.com"
        assert tool.width == 1920
        assert tool.height == 1080
        assert tool.tool_name == "webpage_capture_screen"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters"""
        tool = WebpageCaptureScreen(url="https://example.com", task_summary="Test")
        assert tool.url == "https://example.com"
        assert tool.width == 1280  # Default value
        assert tool.height == 720  # Default value

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = WebpageCaptureScreen(url="https://example.com", task_summary="Test capture")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty URL"""
        tool = WebpageCaptureScreen(url="", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = WebpageCaptureScreen(url="not-a-url", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_dimensions(self):
        """Test validation with invalid dimensions"""
        with pytest.raises(ValidationError):
            WebpageCaptureScreen(
                url="https://example.com", width=0, height=1080, task_summary="Test"
            )

        with pytest.raises(ValidationError):
            WebpageCaptureScreen(
                url="https://example.com", width=1920, height=0, task_summary="Test"
            )

    @patch("tools.content.web.webpage_capture_screen.webpage_capture_screen.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked screenshot API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("SCREENSHOT_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"screenshot_url": "https://example.com/screenshot.png"}
        mock_post.return_value = mock_response

        tool = WebpageCaptureScreen(url="https://example.com", task_summary="Test")
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_various_screen_sizes(self, monkeypatch):
        """Test various screen dimensions"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        dimensions = [
            (1920, 1080),  # Full HD
            (1366, 768),  # Common laptop
            (375, 667),  # Mobile (iPhone)
            (768, 1024),  # Tablet
            (3840, 2160),  # 4K
        ]

        for width, height in dimensions:
            tool = WebpageCaptureScreen(
                url="https://example.com", width=width, height=height, task_summary="Test"
            )
            result = tool.run()
            assert result["success"] is True

    def test_edge_case_full_page_capture(self, monkeypatch):
        """Test full page screenshot (scrolling capture)"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = WebpageCaptureScreen(
            url="https://example.com/long-page",
            width=1920,
            height=10000,  # Very tall for full page
            task_summary="Full page capture",
        )
        result = tool.run()

        assert result["success"] is True
