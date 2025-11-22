"""Tests for summarize_large_document tool."""

import pytest
from unittest.mock import patch
from unittest.mock import Mock, patch
from typing import Dict, Any
from requests.exceptions import RequestException
from pydantic import ValidationError as PydanticValidationError

from tools.web_content.summarize_large_document import SummarizeLargeDocument
from shared.errors import ValidationError, APIError


class TestSummarizeLargeDocument:
    """Test suite for SummarizeLargeDocument."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_url(self) -> str:
        """Valid URL for testing."""
        return "http://example.com/document"

    @pytest.fixture
    def tool(self, valid_url: str) -> SummarizeLargeDocument:
        """Create tool instance with valid parameters."""
        return SummarizeLargeDocument(input=valid_url)

    @pytest.fixture
    def mock_response(self) -> Dict[str, Any]:
        """Mock response data."""
        return {
            "summary": "This is a summary of the document.",
            "questions": {
                "What is the main topic?": "Sample topic",
                "What are the key points?": ["Point 1", "Point 2"],
            },
        }

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(
        self, tool: SummarizeLargeDocument, mock_response: Dict[str, Any]
    ):
        """Test successful execution."""
        with patch.object(tool, "_process", return_value=mock_response):
            result = tool.run()
            assert result["success"] is True
            assert "result" in result
            assert result["result"] == mock_response

    def test_metadata_correct(self, tool: SummarizeLargeDocument):
        """Test tool metadata."""
        assert tool.tool_name == "summarize_large_document"
        assert tool.tool_category == "web"

    # ========== ERROR CASES ==========

    def test_validation_error(self):
        """Test validation errors."""
        tool = SummarizeLargeDocument(input="invalid-url")
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, tool: SummarizeLargeDocument):
        """Test API error handling."""
        with patch.object(tool, "_process", side_effect=RequestException("API failed")):
            result = tool.run()
            assert result["success"] is False

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: SummarizeLargeDocument):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "summary" in result["result"]
        assert "questions" in result["result"]

    # ========== EDGE CASES ==========

    def test_empty_url_raises_validation_error(self):
        """Test empty URL raises ValidationError."""
        tool = SummarizeLargeDocument(input="")
        result = tool.run()
        assert result["success"] is False

    def test_https_url(self):
        """Test HTTPS URL is accepted."""
        tool = SummarizeLargeDocument(input="https://example.com/document")
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "url,expected_valid",
        [
            ("http://example.com/document", True),
            ("https://example.com/document", True),
            ("ftp://example.com/document", False),
            ("invalid-url", False),
        ],
    )
    def test_url_validation(self, url: str, expected_valid: bool):
        """Test URL validation with various inputs."""
        tool = SummarizeLargeDocument(input=url)
        if expected_valid:
            with patch.object(tool, "_process", return_value={"summary": "test"}):
                result = tool.run()
                assert result["success"] is True
        else:
            result = tool.run()
            assert result["success"] is False
