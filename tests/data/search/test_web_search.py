"""Comprehensive tests for web_search tool."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.data.search.web_search.web_search import WebSearch


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

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, valid_query: str):
        """Test successful execution."""
        tool = WebSearch(query=valid_query, max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert len(result["result"]) == 5

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_correct(self, valid_query: str):
        """Test tool metadata."""
        tool = WebSearch(query=valid_query, max_results=5)
        result = tool.run()
        assert result["metadata"]["tool_name"] == "web_search"

    # ========== QUERY VALIDATION ==========

    def test_empty_query_validation(self):
        """Test that empty query is rejected."""
        with pytest.raises(PydanticValidationError):
            WebSearch(query="", max_results=10)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_whitespace_query_validation(self):
        """Test that whitespace-only query is rejected."""
        tool = WebSearch(query="   ", max_results=10)
        with pytest.raises(ValidationError, match="Query cannot be empty"):
            tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_valid_query_formats(self):
        """Test various valid query formats."""
        queries = [
            "simple query",
            "query with numbers 123",
            "query-with-dashes",
            "query_with_underscores",
            "query with @#$%",
            "very " * 50 + "long query",  # Long query
        ]
        for query in queries:
            tool = WebSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    # ========== RESULT LIMIT BOUNDARIES ==========

    def test_min_results_boundary(self):
        """Test minimum results limit (1)."""
        tool = WebSearch(query="test", max_results=1)
        assert tool.max_results == 1

    def test_max_results_boundary(self):
        """Test maximum results limit (100)."""
        tool = WebSearch(query="test", max_results=100)
        assert tool.max_results == 100

    def test_zero_results_rejected(self):
        """Test that 0 results is rejected."""
        with pytest.raises(PydanticValidationError):
            WebSearch(query="test", max_results=0)

    def test_negative_results_rejected(self):
        """Test that negative results is rejected."""
        with pytest.raises(PydanticValidationError):
            WebSearch(query="test", max_results=-5)

    def test_exceeds_max_results_rejected(self):
        """Test that results > 100 is rejected."""
        with pytest.raises(PydanticValidationError):
            WebSearch(query="test", max_results=101)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_results_count_matches_limit(self):
        """Test that returned results match requested limit."""
        for limit in [1, 5, 10, 25, 50]:
            tool = WebSearch(query="test", max_results=limit)
            result = tool.run()
            assert len(result["result"]) == limit

    # ========== ERROR HANDLING ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_missing_api_credentials(self, valid_query: str):
        """Test error when API credentials are missing."""
        tool = WebSearch(query=valid_query, max_results=5)
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(APIError, match="Missing API credentials"):
                tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_request_failure(self, valid_query: str):
        """Test handling of API request failures."""
        tool = WebSearch(query=valid_query, max_results=5)
        with patch("requests.get", side_effect=Exception("Network error")):
            with pytest.raises(APIError):
                tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_timeout(self, valid_query: str):
        """Test handling of API timeout."""
        tool = WebSearch(query=valid_query, max_results=5)
        with patch("requests.get", side_effect=TimeoutError("Request timeout")):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_enabled(self, valid_query: str):
        """Test that mock mode returns mock data."""
        tool = WebSearch(query=valid_query, max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_mock_mode_disabled(self, valid_query: str):
        """Test that mock mode can be disabled."""
        tool = WebSearch(query=valid_query, max_results=5)
        assert not tool._should_use_mock()

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_query(self):
        """Test Unicode characters in query."""
        queries = [
            "Python编程",
            "Привет мир",
            "مرحبا",
            "🚀 rockets",
            "café résumé",
        ]
        for query in queries:
            tool = WebSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_special_characters_in_query(self):
        """Test special characters in query."""
        special_queries = [
            "query with @#$%^&* special chars",
            "query with 'single quotes'",
            'query with "double quotes"',
            "query with <html> tags",
            "query with [brackets]",
            "C++ programming",
            "AT&T corporation",
        ]
        for query in special_queries:
            tool = WebSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_sql_injection_attempt(self):
        """Test that SQL injection attempts are handled safely."""
        tool = WebSearch(query="'; DROP TABLE users; --", max_results=5)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_very_long_query(self):
        """Test handling of very long queries."""
        long_query = "a" * 1000
        tool = WebSearch(query=long_query, max_results=5)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "query,max_results,expected_valid",
        [
            ("valid query", 10, True),
            ("a" * 500, 10, True),  # Long query
            ("single", 1, True),  # Min results
            ("test", 100, True),  # Max results
            ("", 10, False),  # Empty query
            ("test", 0, False),  # Zero results
            ("test", -1, False),  # Negative results
            ("test", 101, False),  # Exceeds max
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_parameter_combinations(self, query: str, max_results: int, expected_valid: bool):
        """Test various parameter combinations."""
        if expected_valid:
            tool = WebSearch(query=query, max_results=max_results)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = WebSearch(query=query, max_results=max_results)
                tool.run()

    # ========== CACHING TESTS ==========

    def test_cache_configuration(self, valid_query: str):
        """Test that caching is properly configured."""
        tool = WebSearch(query=valid_query, max_results=5)
        assert tool.enable_cache is True
        assert tool.cache_ttl == 3600
        assert "query" in tool.cache_key_params
        assert "max_results" in tool.cache_key_params

    # ========== RESULT FORMAT VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_result_format(self, valid_query: str):
        """Test that results have correct format."""
        tool = WebSearch(query=valid_query, max_results=5)
        result = tool.run()

        assert "success" in result
        assert "result" in result
        assert "metadata" in result
        assert isinstance(result["result"], list)

        # Check individual result format
        for item in result["result"]:
            assert "title" in item
            assert "link" in item
            assert "snippet" in item

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_format(self, valid_query: str):
        """Test metadata format."""
        tool = WebSearch(query=valid_query, max_results=5)
        result = tool.run()

        metadata = result["metadata"]
        assert "tool_name" in metadata
        assert metadata["tool_name"] == "web_search"
        assert "mock_mode" in metadata

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow(self):
        """Test complete workflow from creation to execution."""
        # Create tool
        tool = WebSearch(query="python programming", max_results=10)

        # Verify parameters
        assert tool.query == "python programming"
        assert tool.max_results == 10
        assert tool.tool_name == "web_search"
        assert tool.tool_category == "data"

        # Execute
        result = tool.run()

        # Verify results
        assert result["success"] is True
        assert len(result["result"]) == 10
        assert all("title" in item for item in result["result"])
        assert all("link" in item for item in result["result"])

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_multiple_consecutive_searches(self):
        """Test multiple searches with same tool instance."""
        queries = ["python", "javascript", "rust", "go", "java"]

        for query in queries:
            tool = WebSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True
            assert len(result["result"]) == 5

    # ========== PERFORMANCE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_large_result_set(self):
        """Test handling of large result sets."""
        tool = WebSearch(query="test", max_results=100)
        result = tool.run()
        assert result["success"] is True
        assert len(result["result"]) == 100

    # ========== TOOL METADATA TESTS ==========

    def test_tool_category(self, tool: WebSearch):
        """Test tool category is correct."""
        assert tool.tool_category == "data"

    def test_tool_name(self, tool: WebSearch):
        """Test tool name is correct."""
        assert tool.tool_name == "web_search"
