"""Tests for onedrive_search tool."""

import pytest
from unittest.mock import patch
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import os
from pydantic import ValidationError as PydanticValidationError

from tools.storage.onedrive_search import OnedriveSearch
from shared.errors import ValidationError, APIError


class TestOnedriveSearch:
    """Test suite for OnedriveSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        return "test query"

    @pytest.fixture
    def tool(self, valid_query: str) -> OnedriveSearch:
        return OnedriveSearch(query=valid_query, max_results=5)

    @pytest.fixture
    def mock_graph_response(self) -> Dict[str, Any]:
        return {
            "value": [
                {
                    "id": f"id-{i}",
                    "name": f"File {i}",
                    "size": 100 + i,
                    "webUrl": f"http://example.com/{i}",
                    "parentReference": {"path": f"/drive/root:/folder{i}"},
                }
                for i in range(10)
            ]
        }

    # ========== INITIALIZATION TESTS ==========

    def test_initialization_success(self, valid_query: str):
        tool = OnedriveSearch(query=valid_query, max_results=10)
        assert tool.query == valid_query
        assert tool.max_results == 10
        assert tool.tool_name == "onedrive_search"
        assert tool.tool_category == "storage"

    # ========== HAPPY PATH TESTS ==========

    @patch.dict("os.environ", {"MS_GRAPH_TOKEN": "token123"})
    @patch("requests.get")
    def test_execute_success(
        self, mock_get: Mock, tool: OnedriveSearch, mock_graph_response: Dict[str, Any]
    ):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_graph_response
        mock_get.return_value = mock_resp

        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]) <= tool.max_results
        assert "metadata" in result
        assert result["metadata"]["query"] == tool.query

    def test_metadata_correct(self, tool: OnedriveSearch):
        assert tool.tool_name == "onedrive_search"
        assert tool.tool_category == "storage"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: OnedriveSearch):
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert len(result["result"]) == tool.max_results

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch.dict("os.environ", {"MS_GRAPH_TOKEN": "abc"})
    @patch("requests.get")
    def test_real_mode(self, mock_get: Mock, tool: OnedriveSearch):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"value": []}
        mock_get.return_value = mock_resp

        result = tool.run()
        assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    def test_empty_query_raises_validation(self):
        with pytest.raises(PydanticValidationError):
            OnedriveSearch(query="", max_results=5)

    @pytest.mark.parametrize("max_results", [0, -1])
    def test_invalid_max_results_raises(self, max_results: int):
        with pytest.raises(PydanticValidationError):
            OnedriveSearch(query="test", max_results=max_results)

    def test_pydantic_field_validation(self):
        with pytest.raises(PydanticValidationError):
            OnedriveSearch(query="a" * 600, max_results=5)

    # ========== API ERROR TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_missing_token_raises_api_error(self, tool: OnedriveSearch):
        with patch.dict("os.environ", {}, clear=True):
            result = tool.run()
            assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false", "MS_GRAPH_TOKEN": "token"})
    @patch("requests.get")
    def test_http_error_raises_api_error(self, mock_get: Mock, tool: OnedriveSearch):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Server error"
        mock_get.return_value = mock_resp

        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false", "MS_GRAPH_TOKEN": "token"})
    @patch("requests.get", side_effect=Exception("network error"))
    def test_network_exception_wrapped(self, mock_get: Mock, tool: OnedriveSearch):
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_propagates(self, tool: OnedriveSearch):
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_query(self):
        tool = OnedriveSearch(query="测试中文", max_results=3)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_special_characters_query(self):
        tool = OnedriveSearch(query="@#$^&*( query", max_results=3)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_max_length_query(self):
        q = "a" * 500
        tool = OnedriveSearch(query=q, max_results=3)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "query,max_results,valid",
        [
            ("hello", 1, True),
            ("a" * 500, 10, True),
            ("", 5, False),
            ("test", -1, False),
            ("test", 201, False),
        ],
    )
    def test_parameter_validation(self, query: str, max_results: int, valid: bool):
        if valid:
            tool = OnedriveSearch(query=query, max_results=max_results)
            assert tool.query == query
        else:
            with pytest.raises(Exception):
                tool = OnedriveSearch(query=query, max_results=max_results)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_integration_full_run(self):
        tool = OnedriveSearch(query="integration test", max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["query"] == "integration test"

    def test_error_formatting_integration(self, tool: OnedriveSearch):
        with patch.object(tool, "_execute", side_effect=ValueError("bad value")):
            output = tool.run()
            assert "error" in output or output.get("success") is False
