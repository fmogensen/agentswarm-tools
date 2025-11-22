"""Tests for webpage_capture_screen tool."""

import pytest
from unittest.mock import patch, MagicMock
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from typing import Dict, Any

from pydantic import ValidationError as PydanticValidationError

from tools.web_content.webpage_capture_screen import WebpageCaptureScreen
from shared.errors import ValidationError, APIError


class TestWebpageCaptureScreen:
    """Test suite for WebpageCaptureScreen."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_url(self) -> str:
        """Valid test URL."""
        return "https://example.com"

    @pytest.fixture
    def tool(self, valid_url: str) -> WebpageCaptureScreen:
        """Create tool instance."""
        return WebpageCaptureScreen(input=valid_url)

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("selenium.webdriver.Chrome")
    def test_execute_success(self, mock_chrome: MagicMock, tool: WebpageCaptureScreen):
        """Test successful execution."""
        mock_driver = MagicMock(spec=WebDriver)
        mock_chrome.return_value = mock_driver
        mock_driver.save_screenshot.return_value = True

        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert "screenshot_path" in result["result"]

    def test_metadata_correct(self, tool: WebpageCaptureScreen):
        """Test tool metadata."""
        assert tool.tool_name == "webpage_capture_screen"
        assert tool.tool_category == "web"

    # ========== ERROR CASES ==========

    def test_validation_error(self):
        """Test validation errors - Pydantic validates HttpUrl before tool validation."""
        with pytest.raises(PydanticValidationError):
            tool = WebpageCaptureScreen(input="invalid-url")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("selenium.webdriver.Chrome")
    def test_api_error_handled(self, mock_chrome: MagicMock, tool: WebpageCaptureScreen):
        """Test API error handling."""
        mock_chrome.side_effect = Exception("API failed")

        result = tool.run()
        assert result["success"] is False

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: WebpageCaptureScreen):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    # ========== EDGE CASES ==========

    def test_empty_input_raises_validation_error(self):
        """Test empty input raises ValidationError - Pydantic validates HttpUrl."""
        with pytest.raises(PydanticValidationError):
            tool = WebpageCaptureScreen(input="")

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "url,expected_valid",
        [
            ("https://validurl.com", True),
            ("http://anothervalidurl.com", True),
            ("invalid-url", False),
            ("ftp://invalidprotocol.com", False),
            ("", False),
        ],
    )
    @patch("selenium.webdriver.Chrome")
    def test_url_validation(self, mock_chrome: MagicMock, url: str, expected_valid: bool):
        """Test URL validation with various inputs - Pydantic validates HttpUrl."""
        if expected_valid:
            mock_driver = MagicMock(spec=WebDriver)
            mock_chrome.return_value = mock_driver
            mock_driver.save_screenshot.return_value = True
            tool = WebpageCaptureScreen(input=url)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(PydanticValidationError):
                tool = WebpageCaptureScreen(input=url)
