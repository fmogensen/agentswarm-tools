"""Tests for notion_read tool."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import os

from tools.workspace.notion_read import NotionRead
from shared.errors import ValidationError, APIError


class TestNotionRead:
    """Test suite for NotionRead."""

    # ========== FIXTURES ==========

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

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key"})
    @patch("requests.get")
    def test_execute_success(
        self, mock_get: Mock, tool: NotionRead, mock_blocks: Dict[str, Any]
    ):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocks
        mock_get.return_value = mock_response

        result = tool.run()

        assert result["success"] is True
        assert "page_id" in result["result"]
        assert "content" in result["result"]
        assert "summary" in result["result"]
        assert result["metadata"]["tool_name"] == "notion_read"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: NotionRead):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_input", [None, "", " ", 123])
    def test_invalid_input_raises_validation_error(self, bad_input):
        with pytest.raises(ValidationError):
            tool = NotionRead(input=bad_input)
            tool.run()

    # ========== API ERROR TESTS ==========

    @patch.dict("os.environ", {"NOTION_API_KEY": ""})
    def test_missing_api_key_raises_error(self, tool: NotionRead):
        with pytest.raises(APIError) as exc:
            tool.run()
        assert "NOTION_API_KEY missing" in str(exc.value)

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key"})
    @patch("requests.get", side_effect=Exception("Network fail"))
    def test_request_failure(self, mock_get, tool: NotionRead):
        with pytest.raises(APIError):
            tool.run()

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key"})
    @patch("requests.get")
    def test_api_non_200_response(self, mock_get, tool: NotionRead):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "server error"
        mock_get.return_value = mock_response

        with pytest.raises(APIError):
            tool.run()

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key"})
    @patch("requests.get")
    def test_no_text_content(self, mock_get, tool: NotionRead):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{}]}
        mock_get.return_value = mock_response

        result = tool.run()
        assert result["result"]["content"] == "(No text content found in page.)"

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key"})
    @patch("requests.get")
    def test_long_content_summary(self, mock_get, tool: NotionRead):
        long_text = [{"plain_text": "x" * 500}]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"paragraph": {"rich_text": long_text}}]
        }
        mock_get.return_value = mock_response

        result = tool.run()
        assert len(result["result"]["summary"]) < 210

    def test_unicode_input(self):
        tool = NotionRead(input="页面123")
        assert tool.input == "页面123"

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "input_value,valid",
        [
            ("page1", True),
            ("   page2   ", True),
            ("", False),
            ("   ", False),
            (None, False),
            (123, False),
        ],
    )
    def test_parameter_validation(self, input_value, valid):
        if valid:
            tool = NotionRead(input=input_value)
            assert isinstance(tool.input, str)
        else:
            with pytest.raises(Exception):
                NotionRead(input=input_value).run()

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"NOTION_API_KEY": "test_key"})
    @patch("requests.get")
    def test_full_integration(self, mock_get, tool: NotionRead, mock_blocks):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_blocks
        mock_get.return_value = mock_response

        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["tool_name"] == "notion_read"

    def test_error_formatting_integration(self, tool: NotionRead):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
