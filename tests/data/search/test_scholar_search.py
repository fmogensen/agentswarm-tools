"""Comprehensive tests for scholar_search tool."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.data.search.scholar_search.scholar_search import ScholarSearch


class TestScholarSearch:
    """Test suite for ScholarSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        """Valid test query."""
        return "machine learning"

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

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, valid_query: str):
        """Test successful execution."""
        tool = ScholarSearch(query=valid_query, max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert len(result["result"]) == 5

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_correct(self, valid_query: str):
        """Test tool metadata."""
        tool = ScholarSearch(query=valid_query, max_results=5)
        result = tool.run()
        assert result["metadata"]["tool_name"] == "scholar_search"
        assert result["metadata"]["query"] == valid_query

    # ========== QUERY VALIDATION ==========

    def test_empty_query_rejected(self):
        """Test that empty query is rejected."""
        with pytest.raises(PydanticValidationError):
            ScholarSearch(query="", max_results=10)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_whitespace_query_rejected(self):
        """Test that whitespace-only query is rejected."""
        tool = ScholarSearch(query="   ", max_results=10)
        with pytest.raises(ValidationError, match="Query cannot be empty"):
            tool.run()

    def test_query_max_length(self):
        """Test query maximum length validation."""
        # 500 chars should work
        long_query = "a" * 500
        tool = ScholarSearch(query=long_query, max_results=5)
        assert tool.query == long_query

        # 501 chars should fail
        with pytest.raises(PydanticValidationError):
            ScholarSearch(query="a" * 501, max_results=5)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_academic_query_formats(self):
        """Test various academic query formats."""
        queries = [
            "machine learning algorithms",
            "deep learning neural networks",
            "natural language processing",
            "computer vision transformers",
            "reinforcement learning Q-learning",
            "author:Smith",  # Author search
            "title:optimization",  # Title search
        ]
        for query in queries:
            tool = ScholarSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    # ========== RESULT LIMIT BOUNDARIES ==========

    def test_min_results_boundary(self):
        """Test minimum results limit (1)."""
        tool = ScholarSearch(query="test", max_results=1)
        assert tool.max_results == 1

    def test_max_results_boundary(self):
        """Test maximum results limit (100)."""
        tool = ScholarSearch(query="test", max_results=100)
        assert tool.max_results == 100

    def test_zero_results_rejected(self):
        """Test that 0 results is rejected."""
        with pytest.raises(PydanticValidationError):
            ScholarSearch(query="test", max_results=0)

    def test_negative_results_rejected(self):
        """Test that negative results is rejected."""
        with pytest.raises(PydanticValidationError):
            ScholarSearch(query="test", max_results=-5)

    def test_exceeds_max_results_rejected(self):
        """Test that results > 100 is rejected."""
        with pytest.raises(PydanticValidationError):
            ScholarSearch(query="test", max_results=101)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_results_count_matches_limit(self):
        """Test that returned results match requested limit."""
        for limit in [1, 5, 10, 20, 50]:
            tool = ScholarSearch(query="test", max_results=limit)
            result = tool.run()
            assert len(result["result"]) == limit

    # ========== ERROR HANDLING ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_request_failure(self, valid_query: str):
        """Test handling of API request failures."""
        tool = ScholarSearch(query=valid_query, max_results=5)
        with patch("requests.get", side_effect=Exception("Network error")):
            with pytest.raises(APIError):
                tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_timeout(self, valid_query: str):
        """Test handling of API timeout."""
        tool = ScholarSearch(query=valid_query, max_results=5)
        with patch("requests.get", side_effect=TimeoutError("Request timeout")):
            with pytest.raises(APIError):
                tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_rate_limit_error(self, valid_query: str):
        """Test handling of rate limit errors."""
        tool = ScholarSearch(query=valid_query, max_results=5)
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")

        with patch("requests.get", return_value=mock_response):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_enabled(self, valid_query: str):
        """Test that mock mode returns mock data."""
        tool = ScholarSearch(query=valid_query, max_results=5)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_mock_mode_disabled(self, valid_query: str):
        """Test that mock mode can be disabled."""
        tool = ScholarSearch(query=valid_query, max_results=5)
        assert not tool._should_use_mock()

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_unicode_scientific_terms(self):
        """Test Unicode characters in scientific queries."""
        queries = [
            "Schrödinger equation",
            "Bézier curves",
            "naïve Bayes",
            "α-helix protein structure",
            "β-diversity in ecology",
        ]
        for query in queries:
            tool = ScholarSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mathematical_notation(self):
        """Test mathematical notation in queries."""
        queries = [
            "O(n log n) algorithms",
            "f(x) = x^2 + 1",
            "∫ x dx integration",
            "∑ series summation",
        ]
        for query in queries:
            tool = ScholarSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_year_filters_in_query(self):
        """Test queries with year filters."""
        queries = [
            "machine learning 2024",
            "research 2020-2023",
            "papers before:2020",
        ]
        for query in queries:
            tool = ScholarSearch(query=query, max_results=5)
            result = tool.run()
            assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "query,max_results,expected_valid",
        [
            ("valid research query", 10, True),
            ("a" * 500, 10, True),  # Max length
            ("short", 1, True),  # Min results
            ("test", 100, True),  # Max results
            ("", 10, False),  # Empty query
            ("a" * 501, 10, False),  # Exceeds max length
            ("test", 0, False),  # Zero results
            ("test", 101, False),  # Exceeds max results
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_parameter_combinations(self, query: str, max_results: int, expected_valid: bool):
        """Test various parameter combinations."""
        if expected_valid:
            tool = ScholarSearch(query=query, max_results=max_results)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = ScholarSearch(query=query, max_results=max_results)
                tool.run()

    # ========== CACHING TESTS ==========

    def test_cache_configuration(self, valid_query: str):
        """Test that caching is properly configured."""
        tool = ScholarSearch(query=valid_query, max_results=5)
        assert tool.enable_cache is True
        assert tool.cache_ttl == 3600
        assert "query" in tool.cache_key_params
        assert "max_results" in tool.cache_key_params

    # ========== RESULT FORMAT VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_result_format(self, valid_query: str):
        """Test that results have correct academic paper format."""
        tool = ScholarSearch(query=valid_query, max_results=5)
        result = tool.run()

        assert "success" in result
        assert "result" in result
        assert "metadata" in result
        assert isinstance(result["result"], list)

        # Check individual paper format
        for paper in result["result"]:
            assert "id" in paper
            assert "title" in paper
            assert "abstract" in paper
            assert "authors" in paper
            assert isinstance(paper["authors"], list)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_format(self, valid_query: str):
        """Test metadata format."""
        tool = ScholarSearch(query=valid_query, max_results=10)
        result = tool.run()

        metadata = result["metadata"]
        assert "tool_name" in metadata
        assert metadata["tool_name"] == "scholar_search"
        assert "query" in metadata
        assert "max_results" in metadata
        assert metadata["max_results"] == 10

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow(self):
        """Test complete workflow for academic search."""
        # Create tool
        tool = ScholarSearch(query="deep learning", max_results=10)

        # Verify parameters
        assert tool.query == "deep learning"
        assert tool.max_results == 10
        assert tool.tool_name == "scholar_search"
        assert tool.tool_category == "data"

        # Execute
        result = tool.run()

        # Verify results
        assert result["success"] is True
        assert len(result["result"]) == 10
        assert all("title" in paper for paper in result["result"])
        assert all("authors" in paper for paper in result["result"])

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_multiple_research_topics(self):
        """Test searching multiple research topics."""
        topics = [
            "quantum computing",
            "blockchain consensus",
            "climate modeling",
            "gene therapy",
            "renewable energy",
        ]

        for topic in topics:
            tool = ScholarSearch(query=topic, max_results=5)
            result = tool.run()
            assert result["success"] is True
            assert len(result["result"]) == 5

    # ========== TOOL METADATA TESTS ==========

    def test_tool_category(self, tool: ScholarSearch):
        """Test tool category is correct."""
        assert tool.tool_category == "data"

    def test_tool_name(self, tool: ScholarSearch):
        """Test tool name is correct."""
        assert tool.tool_name == "scholar_search"
