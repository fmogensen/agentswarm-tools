"""
Comprehensive unit tests for Workspace Tools category.

Tests all workspace integration tools:
- notion_search
- notion_read
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any

from tools.communication.notion_search.notion_search import NotionSearch
from tools.communication.notion_read.notion_read import NotionRead

from shared.errors import ValidationError, APIError, AuthenticationError


# ========== NotionSearch Tests ==========


class TestNotionSearch:
    """Comprehensive tests for NotionSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = NotionSearch(query="project notes", max_results=10)
        assert tool.query == "project notes"
        assert tool.max_results == 10
        assert tool.tool_name == "notion_search"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters"""
        tool = NotionSearch(query="test")
        assert tool.query == "test"
        assert tool.max_results == 10  # Default value

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = NotionSearch(query="meeting notes", max_results=5)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True
        assert isinstance(result["result"], list)

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = NotionSearch(query="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_whitespace_query(self):
        """Test validation with whitespace only query"""
        tool = NotionSearch(query="   ")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_max_results(self):
        """Test validation with invalid max_results"""
        with pytest.raises(ValidationError):
            NotionSearch(query="test", max_results=0)

    def test_validate_parameters_max_results_too_high(self):
        """Test validation with max_results exceeding limit"""
        with pytest.raises(ValidationError):
            NotionSearch(query="test", max_results=1000)

    @patch("tools.communication.notion_search.notion_search.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked Notion API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("NOTION_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "page1",
                    "properties": {"title": {"title": [{"text": {"content": "Page 1"}}]}},
                },
                {
                    "id": "page2",
                    "properties": {"title": {"title": [{"text": {"content": "Page 2"}}]}},
                },
            ]
        }
        mock_post.return_value = mock_response

        tool = NotionSearch(query="test", max_results=2)
        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]) == 2
        mock_post.assert_called_once()

    @patch("tools.communication.notion_search.notion_search.requests.post")
    def test_api_error_handling_missing_api_key(self, mock_post, monkeypatch):
        """Test handling of missing API key"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.delenv("NOTION_API_KEY", raising=False)

        tool = NotionSearch(query="test")
        with pytest.raises(APIError) as exc_info:
            tool.run()
        assert "api" in str(exc_info.value).lower() or "key" in str(exc_info.value).lower()

    @patch("tools.communication.notion_search.notion_search.requests.post")
    def test_api_error_handling_network_failure(self, mock_post, monkeypatch):
        """Test handling of network failures"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("NOTION_API_KEY", "test_key")

        mock_post.side_effect = Exception("Network error")
        tool = NotionSearch(query="test")

        with pytest.raises(APIError):
            tool.run()

    @patch("tools.communication.notion_search.notion_search.requests.post")
    def test_edge_case_empty_results(self, mock_post, monkeypatch):
        """Test handling of empty search results"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("NOTION_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_post.return_value = mock_response

        tool = NotionSearch(query="nonexistent")
        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]) == 0

    def test_edge_case_special_characters_in_query(self, monkeypatch):
        """Test handling of special characters in search query"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        special_queries = [
            "query with @mention",
            "query with #hashtag",
            "query/with/slashes",
            "query & ampersand",
        ]

        for query in special_queries:
            tool = NotionSearch(query=query)
            result = tool.run()
            assert result["success"] is True

    @patch("tools.communication.notion_search.notion_search.requests.post")
    def test_rate_limit_handling(self, mock_post, monkeypatch):
        """Test handling of rate limit errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("NOTION_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
        mock_post.return_value = mock_response

        tool = NotionSearch(query="test")
        with pytest.raises(APIError):
            tool.run()


# ========== NotionRead Tests ==========


class TestNotionRead:
    """Comprehensive tests for NotionRead tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = NotionRead(page_id="abc123def456")
        assert tool.page_id == "abc123def456"
        assert tool.tool_name == "notion_read"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = NotionRead(page_id="test123")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True
        assert "content" in result["result"]

    def test_validate_parameters_empty_page_id(self):
        """Test validation with empty page ID"""
        tool = NotionRead(page_id="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_whitespace_page_id(self):
        """Test validation with whitespace page ID"""
        tool = NotionRead(page_id="   ")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_page_id_format(self):
        """Test validation with invalid page ID format"""
        # Notion page IDs should be UUID format
        tool = NotionRead(page_id="invalid-id")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.communication.notion_read.notion_read.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked Notion API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("NOTION_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "page123",
            "properties": {"title": {"title": [{"text": {"content": "Test Page"}}]}},
            "content": "This is the page content",
        }
        mock_get.return_value = mock_response

        tool = NotionRead(page_id="page123")
        result = tool.run()

        assert result["success"] is True
        mock_get.assert_called_once()

    @patch("tools.communication.notion_read.notion_read.requests.get")
    def test_api_error_handling_missing_api_key(self, mock_get, monkeypatch):
        """Test handling of missing API key"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.delenv("NOTION_API_KEY", raising=False)

        tool = NotionRead(page_id="page123")
        with pytest.raises(APIError) as exc_info:
            tool.run()
        assert "api" in str(exc_info.value).lower() or "key" in str(exc_info.value).lower()

    @patch("tools.communication.notion_read.notion_read.requests.get")
    def test_api_error_handling_page_not_found(self, mock_get, monkeypatch):
        """Test handling of page not found errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("NOTION_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Page not found")
        mock_get.return_value = mock_response

        tool = NotionRead(page_id="nonexistent")
        with pytest.raises(APIError):
            tool.run()

    @patch("tools.communication.notion_read.notion_read.requests.get")
    def test_api_error_handling_permission_denied(self, mock_get, monkeypatch):
        """Test handling of permission denied errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("NOTION_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = Exception("Permission denied")
        mock_get.return_value = mock_response

        tool = NotionRead(page_id="restricted")
        with pytest.raises(APIError):
            tool.run()

    @patch("tools.communication.notion_read.notion_read.requests.get")
    def test_edge_case_large_page_content(self, mock_get, monkeypatch):
        """Test reading large page content"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("NOTION_API_KEY", "test_key")

        large_content = "x" * 1000000  # 1MB of content
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "page123",
            "properties": {},
            "content": large_content,
        }
        mock_get.return_value = mock_response

        tool = NotionRead(page_id="page123")
        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]["content"]) == 1000000

    def test_edge_case_uuid_formats(self, monkeypatch):
        """Test various UUID formats for page IDs"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        valid_uuids = [
            "123e4567-e89b-12d3-a456-426614174000",
            "123e4567e89b12d3a456426614174000",  # Without dashes
            "123E4567-E89B-12D3-A456-426614174000",  # Uppercase
        ]

        for uuid in valid_uuids:
            tool = NotionRead(page_id=uuid)
            result = tool.run()
            assert result["success"] is True
