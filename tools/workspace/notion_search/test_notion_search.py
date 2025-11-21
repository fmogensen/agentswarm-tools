"""Tests for notion_search tool."""

import pytest
from unittest.mock import patch, MagicMock
import os

from tools.workspace.notion_search import NotionSearch
from shared.errors import ValidationError, APIError


class TestNotionSearch:
    """Test suite for NotionSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        return "test query"

    @pytest.fixture
    def tool(self, valid_query: str) -> NotionSearch:
        return NotionSearch(query=valid_query, max_results=5)

    @pytest.fixture
    def mock_notion_response(self) -> dict:
        return {
            "results": [
                {
                    "id": "123",
                    "url": "https://notion.so/page123",
                    "object": "page",
                    "properties": {"title": {"title": [{"plain_text": "Sample Page"}]}},
                }
            ]
        }

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_query: str):
        tool = NotionSearch(query=valid_query, max_results=10)
        assert tool.query == valid_query
        assert tool.max_results == 10

    def test_metadata_fields(self, tool: NotionSearch):
        assert tool.tool_name == "notion_search"
        assert tool.tool_category == "workspace"
        assert tool.tool_description == "Search Notion workspace for pages and content"

    # ========== HAPPY PATH ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_mock_mode_success(self, tool: NotionSearch):
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]) <= tool.max_results
        assert result["metadata"]["mock_mode"] is True

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false", "NOTION_API_KEY": "abc123"})
    @patch("requests.post")
    def test_real_api_success(
        self, mock_post, tool: NotionSearch, mock_notion_response
    ):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_notion_response
        mock_post.return_value = mock_response

        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]) == 1
        assert result["result"][0]["title"] == "Sample Page"

    # ========== VALIDATION TESTS ==========

    def test_empty_query_raises(self):
        with pytest.raises(ValidationError):
            tool = NotionSearch(query="", max_results=5)
            tool.run()

    def test_whitespace_query_raises(self):
        with pytest.raises(ValidationError):
            tool = NotionSearch(query="   ", max_results=5)
            tool.run()

    def test_invalid_max_results(self):
        with pytest.raises(ValidationError):
            tool = NotionSearch(query="abc", max_results=0)
            tool.run()

    # ========== API ERROR HANDLING ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_no_api_key_raises(self, tool: NotionSearch):
        with pytest.raises(APIError):
            tool.run()

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false", "NOTION_API_KEY": "abc123"})
    @patch("requests.post", side_effect=Exception("Network failure"))
    def test_network_exception_raises(self, _, tool: NotionSearch):
        with pytest.raises(APIError):
            tool.run()

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false", "NOTION_API_KEY": "abc123"})
    @patch("requests.post")
    def test_non_200_status_error(self, mock_post, tool: NotionSearch):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_post.return_value = mock_response

        with pytest.raises(APIError):
            tool.run()

    # ========== EDGE CASE TESTS ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_unicode_query(self):
        tool = NotionSearch(query="こんにちは世界", max_results=3)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["query"] == "こんにちは世界"

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_special_characters_query(self):
        tool = NotionSearch(query="@#$%^&*()", max_results=3)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["query"] == "@#$%^&*()"

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_long_query(self):
        long_query = "a" * 500
        tool = NotionSearch(query=long_query, max_results=3)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "query,max_results,valid",
        [
            ("normal", 5, True),
            ("a" * 500, 5, True),
            ("", 5, False),
            ("query", 0, False),
            ("query", 101, False),
        ],
    )
    def test_param_validation(self, query, max_results, valid):
        if valid:
            tool = NotionSearch(query=query, max_results=max_results)
            assert tool.query == query
        else:
            with pytest.raises(Exception):
                NotionSearch(query=query, max_results=max_results)

    # ========== INTEGRATION TESTS ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_integration_mock_mode(self, tool: NotionSearch):
        r = tool.run()
        assert r["success"] is True

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_max_results_limit(self):
        tool = NotionSearch(query="test", max_results=2)
        result = tool.run()
        assert len(result["result"]) == 2
