"""Tests for web_search tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from tools.search.web_search import WebSearch
from shared.errors import ValidationError, APIError


class TestWebSearch:
    """Test suite for WebSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        """Valid test query."""
        return "test query"

    @pytest.fixture
    def tool(self, valid_query: str) -> WebSearch:
        """Create WebSearch instance with valid parameters."""
        return WebSearch(query=valid_query, max_results=5)

    @pytest.fixture
    def mock_results(self) -> list:
        """Mock API results."""
        return [
            {
                "title": f"Mock Result {i}",
                "link": f"https://example.com/mock/{i}",
                "snippet": f"This is a mock snippet for result {i}.",
            }
            for i in range(1, 6)
        ]

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: WebSearch):
        """Test successful execution."""
        with patch.object(
            tool, "_process", return_value=tool._generate_mock_results()["result"]
        ):
            result = tool.run()
            assert result["success"] is True
            assert "result" in result
            assert len(result["result"]) == 5

    def test_metadata_correct(self, tool: WebSearch):
        """Test tool metadata."""
        assert tool.tool_name == "web_search"
        assert tool.tool_category == "search"

    # ========== ERROR CASES ==========

    def test_validation_error(self):
        """Test validation errors."""
        # Pydantic validates min_length=1 before tool runs
        with pytest.raises(PydanticValidationError):
            WebSearch(query="", max_results=10)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, valid_query: str):
        """Test API error handling."""
        tool = WebSearch(query=valid_query, max_results=5)
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: WebSearch, mock_results: list):
        """Test mock mode returns mock data."""
        with patch.object(
            tool,
            "_generate_mock_results",
            return_value={
                "success": True,
                "result": mock_results,
                "metadata": {"mock_mode": True},
            },
        ):
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["mock_mode"] is True
            assert len(result["result"]) == 5

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_query(self):
        """Test Unicode characters in query."""
        tool = WebSearch(query="Python编程", max_results=5)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_special_characters_in_query(self):
        """Test special characters in query."""
        special_query = "query with @#$%^&* special chars"
        tool = WebSearch(query=special_query, max_results=5)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "query,max_results,expected_valid",
        [
            ("valid query", 10, True),
            ("a" * 500, 10, True),  # Max length
            ("", 10, False),  # Empty query
            ("test", 0, False),  # Invalid max_results
            ("test", 101, False),  # Max_results too high
        ],
    )
    def test_parameter_validation(
        self, query: str, max_results: int, expected_valid: bool
    ):
        """Test parameter validation with various inputs."""
        if expected_valid:
            tool = WebSearch(query=query, max_results=max_results)
            assert tool.query == query
            assert tool.max_results == max_results
        else:
            with pytest.raises(Exception):  # Could be ValidationError or Pydantic error
                tool = WebSearch(query=query, max_results=max_results)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow(self):
        """Test complete workflow."""
        tool = WebSearch(query="python programming", max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]) == 5
