"""Tests for gmail_search tool."""

import pytest
from unittest.mock import patch
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from tools.communication.gmail_search import GmailSearch
from shared.errors import ValidationError, APIError


class TestGmailSearch:
    """Test suite for GmailSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        return "from:test@example.com"

    @pytest.fixture
    def tool(self, valid_query: str) -> GmailSearch:
        return GmailSearch(query=valid_query, max_results=5)

    @pytest.fixture
    def mock_messages(self):
        return [{"id": f"msg{i}"} for i in range(1, 4)]

    @pytest.fixture
    def mock_message_detail(self):
        return {
            "snippet": "Test snippet",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"},
                ]
            },
        }

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self, valid_query: str):
        tool = GmailSearch(query=valid_query, max_results=3)
        assert tool.query == valid_query
        assert tool.max_results == 3
        assert tool.tool_name == "gmail_search"
        assert tool.tool_category == "communication"

    # ========== HAPPY PATH TESTS ==========

    @patch.dict(
        "os.environ",
        {"USE_MOCK_APIS": "false", "GOOGLE_SERVICE_ACCOUNT_FILE": "/tmp/fake.json"},
    )
    @patch("tools.communication.gmail_search.gmail_search.Credentials")
    @patch("tools.communication.gmail_search.gmail_search.build")
    def test_execute_success(
        self, mock_build, mock_creds, tool, mock_messages, mock_message_detail
    ):
        service = MagicMock()
        users = service.users.return_value
        users.messages.return_value.list.return_value.execute.return_value = {
            "messages": mock_messages
        }
        users.messages.return_value.get.return_value.execute.return_value = mock_message_detail
        mock_build.return_value = service

        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]) == 3
        assert result["metadata"]["mock_mode"] is False

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GmailSearch):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert len(result["result"]) == tool.max_results

    # ========== VALIDATION TESTS ==========

    def test_empty_query_raises_validation_error(self):
        tool = GmailSearch(query="   ", max_results=5)
        result = tool.run()
        assert result["success"] is False
        error_msg = (
            result.get("error", {}).get("message", "")
            if isinstance(result.get("error"), dict)
            else str(result.get("error", ""))
        )
        assert "Query cannot be empty" in error_msg

    def test_invalid_max_results_raises_validation_error(self):
        tool = GmailSearch(query="test", max_results=0)
        result = tool.run()
        assert result["success"] is False
        error_msg = (
            result.get("error", {}).get("message", "")
            if isinstance(result.get("error"), dict)
            else str(result.get("error", ""))
        )
        assert "max_results must be a positive integer" in error_msg

    # ========== ERROR HANDLING TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_missing_env_var_raises_api_error(self, tool: GmailSearch):
        if "GOOGLE_SERVICE_ACCOUNT_FILE" in os.environ:
            del os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"]

        result = tool.run()
        assert result["success"] is False
        error_msg = (
            result.get("error", {}).get("message", "")
            if isinstance(result.get("error"), dict)
            else str(result.get("error", ""))
        )
        assert "GOOGLE_SERVICE_ACCOUNT_FILE" in error_msg

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch.object(GmailSearch, "_process", side_effect=Exception("API failed"))
    def test_api_error_propagates(self, mock_process, tool: GmailSearch):
        result = tool.run()
        assert result["success"] is False
        error_msg = (
            result.get("error", {}).get("message", "")
            if isinstance(result.get("error"), dict)
            else str(result.get("error", ""))
        )
        assert "API failed" in error_msg

    # ========== EDGE CASE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_query(self):
        tool = GmailSearch(query="测试查询", max_results=3)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_special_characters_query(self):
        tool = GmailSearch(query="@#$%&*()", max_results=3)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_long_query(self):
        long_query = "a" * 500
        tool = GmailSearch(query=long_query, max_results=3)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "query,max_results,valid",
        [
            ("hello", 5, True),
            ("a" * 300, 1, True),
            ("", 5, False),
            ("test", -1, False),
        ],
    )
    def test_param_validation(self, query, max_results, valid):
        if valid:
            tool = GmailSearch(query=query, max_results=max_results)
            assert tool.query == query
        else:
            tool = GmailSearch(query=query, max_results=max_results)
            result = tool.run()
            assert result["success"] is False


class TestGmailSearchIntegration:
    """Integration tests with shared components."""

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_basic_run_integration(self):
        tool = GmailSearch(query="integration", max_results=5)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_integration(self):
        tool = GmailSearch(query="integration-test", max_results=4)
        result = tool.run()
        metadata = result["metadata"]

        assert metadata["query"] == "integration-test"
        assert metadata["max_results"] == 4
        assert metadata["mock_mode"] is True
