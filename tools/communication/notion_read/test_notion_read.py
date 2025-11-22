"""Tests for notion_read tool."""

import pytest
from unittest.mock import patch
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import os

from pydantic import ValidationError as PydanticValidationError

from tools.workspace.notion_read import NotionRead
from shared.errors import ValidationError, APIError


class TestNotionRead:
    """Test suite for NotionRead."""

    # ========== FIXTURES ==========

    @pytest.fixture(autouse=True)
    def mock_rate_limiter(self):
        """Mock rate limiter to avoid rate limit errors in tests."""
        with patch("shared.base.get_rate_limiter") as mock:
            mock_limiter = MagicMock()
            mock_limiter.check_rate_limit.return_value = None
            mock.return_value = mock_limiter
            yield mock_limiter

    @pytest.fixture
    def valid_input(self) -> str:
        return "abc123"

    @pytest.fixture
    def tool(self, valid_input: str) -> NotionRead:
        return NotionRead(input=valid_input)

    @pytest.fixture
    def mock_blocks(self) -> Dict[str, Any]:
        return {
            "results": [
                {
                    "paragraph": {
                        "rich_text": [
                            {"plain_text": "Hello"},
                            {"plain_text": "World"},
                        ]
                    }
                },
                {
                    "paragraph": {
                        "rich_text": [
                            {"plain_text": "Another"},
                            {"plain_text": "Block"},
                        ]
                    }
                },
            ]
        }

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self):
        tool = NotionRead(input="page123")
        assert tool.input == "page123"
        assert tool.tool_name == "notion_read"
        assert tool.tool_category == "workspace"

    # ========== HAPPY PATH TESTS ==========

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key", "USE_MOCK_APIS": "false"})
    @patch("requests.get")
    def test_execute_success(
        self, mock_get: Mock, mock_blocks: Dict[str, Any], valid_input: str
    ):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocks
        mock_get.return_value = mock_response

        tool = NotionRead(input=valid_input)
        result = tool.run()

        assert result["success"] is True
        assert "page_id" in result["result"]
        assert "content" in result["result"]
        assert "summary" in result["result"]
        assert result["metadata"]["tool_name"] == "notion_read"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, valid_input: str):
        tool = NotionRead(input=valid_input)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    # ========== VALIDATION TESTS ==========

    def test_none_input_raises_pydantic_error(self):
        # None type triggers Pydantic validation error
        with pytest.raises(PydanticValidationError):
            NotionRead(input=None)

    def test_int_input_raises_pydantic_error(self):
        # Integer type triggers Pydantic validation error
        with pytest.raises(PydanticValidationError):
            NotionRead(input=123)

    def test_empty_string_returns_validation_error(self):
        # Empty string passes Pydantic but fails our validation
        tool = NotionRead(input="")
        result = tool.run()
        assert result["success"] is False
        assert "error" in result

    def test_whitespace_returns_validation_error(self):
        # Whitespace passes Pydantic but fails our validation
        tool = NotionRead(input="   ")
        result = tool.run()
        assert result["success"] is False
        assert "error" in result

    # ========== API ERROR TESTS ==========

    @patch.dict("os.environ", {"NOTION_API_KEY": "", "USE_MOCK_APIS": "false"}, clear=True)
    def test_missing_api_key_returns_error(self, valid_input: str):
        tool = NotionRead(input=valid_input)
        result = tool.run()
        assert result["success"] is False
        assert "NOTION_API_KEY" in str(result["error"]["message"])

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key", "USE_MOCK_APIS": "false"})
    @patch("requests.get", side_effect=Exception("Network fail"))
    def test_request_failure(self, mock_get, valid_input: str):
        tool = NotionRead(input=valid_input)
        result = tool.run()
        assert result["success"] is False
        assert "error" in result

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key", "USE_MOCK_APIS": "false"})
    @patch("requests.get")
    def test_api_non_200_response(self, mock_get, valid_input: str):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "server error"
        mock_get.return_value = mock_response

        tool = NotionRead(input=valid_input)
        result = tool.run()
        assert result["success"] is False
        assert "error" in result

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key", "USE_MOCK_APIS": "false"})
    @patch("requests.get")
    def test_no_text_content(self, mock_get, valid_input: str):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{}]}
        mock_get.return_value = mock_response

        tool = NotionRead(input=valid_input)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["content"] == "(No text content found in page.)"

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key", "USE_MOCK_APIS": "false"})
    @patch("requests.get")
    def test_long_content_summary(self, mock_get, valid_input: str):
        long_text = [{"plain_text": "x" * 500}]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"paragraph": {"rich_text": long_text}}]
        }
        mock_get.return_value = mock_response

        tool = NotionRead(input=valid_input)
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]["summary"]) < 210

    def test_unicode_input(self):
        tool = NotionRead(input="页面123")
        assert tool.input == "页面123"

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "input_value,valid,pydantic_error",
        [
            ("page1", True, False),
            ("   page2   ", True, False),
            ("", False, False),  # Empty string - runtime validation error
            ("   ", False, False),  # Whitespace - runtime validation error
            (None, False, True),  # None - Pydantic error
            (123, False, True),  # Int - Pydantic error
        ],
    )
    def test_parameter_validation(self, input_value, valid, pydantic_error):
        if pydantic_error:
            with pytest.raises(PydanticValidationError):
                NotionRead(input=input_value)
        elif valid:
            tool = NotionRead(input=input_value)
            assert isinstance(tool.input, str)
        else:
            # Invalid but passes Pydantic - returns error response
            tool = NotionRead(input=input_value)
            result = tool.run()
            assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key", "USE_MOCK_APIS": "false"})
    @patch("requests.get")
    def test_full_integration(self, mock_get, mock_blocks, valid_input: str):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocks
        mock_get.return_value = mock_response

        tool = NotionRead(input=valid_input)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["tool_name"] == "notion_read"

    def test_error_formatting_integration(self, valid_input: str):
        tool = NotionRead(input=valid_input)
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert result["success"] is False
            assert "error" in result
