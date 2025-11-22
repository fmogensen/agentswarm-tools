"""Tests for scholar_search tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from tools.search.scholar_search import ScholarSearch
from shared.errors import ValidationError, APIError


class TestScholarSearch:
    """Test suite for ScholarSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        """Valid test query."""
        return "test query"

    @pytest.fixture
    def tool(self, valid_query: str) -> ScholarSearch:
        """Create ScholarSearch instance with valid parameters."""
        return ScholarSearch(query=valid_query, max_results=5)

    @pytest.fixture
    def mock_results(self) -> list:
        """Mock API results."""
        return [
            {
                "id": i,
                "title": f"Mock Article {i}",
                "abstract": f"This is a mock abstract for article {i}.",
                "authors": ["Author A", "Author B"],
                "source": "mock",
            }
            for i in range(1, 6)
        ]

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: ScholarSearch):
        """Test successful execution."""
        with patch.object(tool, "_process", return_value=[]):
            result = tool.run()
            assert result["success"] is True
            assert "result" in result

    def test_metadata_correct(self, tool: ScholarSearch):
        """Test tool metadata."""
        assert tool.tool_name == "scholar_search"
        assert tool.tool_category == "search"

    # ========== ERROR CASES ==========

    def test_validation_error(self):
        """Test validation errors."""
        with pytest.raises(PydanticValidationError):
            ScholarSearch(query="", max_results=10)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, tool: ScholarSearch):
        """Test API error handling."""
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            result = tool.run()
            assert result["success"] is False
            error_msg = result.get("error", {}).get("message", "") if isinstance(result.get("error"), dict) else str(result.get("error", ""))
            assert "API failed" in error_msg

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: ScholarSearch, mock_results: list):
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
        tool = ScholarSearch(query="Python编程", max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["query"] == "Python编程"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_special_characters_in_query(self):
        """Test special characters in query."""
        special_query = "query with @#$%^&* special chars"
        tool = ScholarSearch(query=special_query, max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["query"] == special_query

    def test_very_long_query(self):
        """Test query at maximum length."""
        long_query = "a" * 500  # Max length from Field definition
        tool = ScholarSearch(query=long_query, max_results=5)
        with patch.object(tool, "_process", return_value=[]):
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
            tool = ScholarSearch(query=query, max_results=max_results)
            assert tool.query == query
            assert tool.max_results == max_results
        else:
            with pytest.raises(Exception):  # Could be ValidationError or Pydantic error
                tool = ScholarSearch(query=query, max_results=max_results)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow(self, tool: ScholarSearch):
        """Test complete workflow."""
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["query"] == "test query"
