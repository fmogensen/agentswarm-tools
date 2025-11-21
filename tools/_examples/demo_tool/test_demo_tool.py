"""
Tests for demo_tool - Reference Implementation

This test file demonstrates:
- Complete test coverage patterns
- Fixture usage
- Mocking external dependencies
- Parametrized tests
- Error case testing
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from tools._examples.demo_tool import DemoTool
from shared.errors import ValidationError, APIError


class TestDemoTool:
    """Test suite for DemoTool."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        """Valid test query."""
        return "test query"

    @pytest.fixture
    def demo_tool(self, valid_query: str) -> DemoTool:
        """Create DemoTool instance with valid parameters."""
        return DemoTool(
            query=valid_query,
            max_results=10,
            filter_type=None,
            use_cache=True
        )

    @pytest.fixture
    def mock_results(self) -> list:
        """Mock API results."""
        return [
            {
                "id": i,
                "title": f"Result {i}",
                "description": f"Description {i}",
                "score": 1.0 - (i * 0.1),
                "source": "test"
            }
            for i in range(1, 11)
        ]

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization_success(self, valid_query: str):
        """Test tool initializes with valid parameters."""
        tool = DemoTool(
            query=valid_query,
            max_results=5,
            filter_type="recent"
        )

        assert tool.query == valid_query
        assert tool.max_results == 5
        assert tool.filter_type == "recent"
        assert tool.use_cache is True  # Default value

    def test_tool_metadata_correct(self, demo_tool: DemoTool):
        """Test tool has correct metadata."""
        assert demo_tool.tool_name == "demo_tool"
        assert demo_tool.tool_category == "examples"
        assert demo_tool.tool_description == "Demo tool showing complete implementation pattern"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_returns_results(self, demo_tool: DemoTool):
        """Test successful execution returns results."""
        result = demo_tool.run()

        assert result is not None
        assert result["success"] is True
        assert "results" in result
        assert "total_count" in result
        assert "metadata" in result
        assert len(result["results"]) > 0

    def test_max_results_limit_enforced(self):
        """Test max_results parameter is enforced."""
        tool = DemoTool(query="test", max_results=3)
        result = tool.run()

        assert result["total_count"] <= 3
        assert len(result["results"]) <= 3

    def test_metadata_contains_query_info(self, demo_tool: DemoTool):
        """Test metadata contains query information."""
        result = demo_tool.run()

        metadata = result["metadata"]
        assert metadata["query"] == demo_tool.query
        assert metadata["max_results"] == demo_tool.max_results
        assert "tool_version" in metadata

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock_results(self, demo_tool: DemoTool):
        """Test mock mode returns mock data."""
        result = demo_tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert all(r["source"] == "mock" for r in result["results"])

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode_processes_query(self, demo_tool: DemoTool):
        """Test real mode processes actual query."""
        result = demo_tool.run()

        assert result["success"] is True
        # In demo tool, real mode still returns sample data
        # In actual tools, this would call real APIs

    # ========== VALIDATION TESTS ==========

    def test_empty_query_raises_validation_error(self):
        """Test empty query raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = DemoTool(query="", max_results=10)
            tool.run()

        assert "query" in str(exc_info.value).lower()

    def test_invalid_filter_type_raises_error(self):
        """Test invalid filter_type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = DemoTool(query="test", filter_type="invalid_filter")
            tool.run()

        assert "filter_type" in str(exc_info.value).lower()

    def test_max_results_boundary_values(self):
        """Test max_results at boundary values."""
        # Minimum (1)
        tool = DemoTool(query="test", max_results=1)
        assert tool.max_results == 1

        # Maximum (100)
        tool = DemoTool(query="test", max_results=100)
        assert tool.max_results == 100

        # Below minimum should fail Pydantic validation
        with pytest.raises(Exception):  # Pydantic ValidationError
            tool = DemoTool(query="test", max_results=0)

        # Above maximum should fail Pydantic validation
        with pytest.raises(Exception):
            tool = DemoTool(query="test", max_results=101)

    # ========== FILTER TESTS ==========

    @pytest.mark.parametrize("filter_type", ["recent", "popular", "relevant"])
    def test_valid_filter_types(self, filter_type: str):
        """Test all valid filter types work."""
        tool = DemoTool(query="test", filter_type=filter_type)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["filter_type"] == filter_type

    def test_filter_none_returns_all_results(self):
        """Test filter_type=None returns unfiltered results."""
        tool = DemoTool(query="test", filter_type=None, max_results=10)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["filter_type"] is None

    def test_filter_sorting_changes_order(self, demo_tool: DemoTool):
        """Test filters change result ordering."""
        # Get results with different filters
        with patch.object(demo_tool, '_process_query') as mock_process:
            mock_process.return_value = [
                {"id": 1, "score": 0.5},
                {"id": 2, "score": 0.9},
                {"id": 3, "score": 0.7}
            ]

            demo_tool.filter_type = "popular"
            result = demo_tool._apply_filters(mock_process.return_value)

            # Should be sorted by score descending
            assert result[0]["score"] == 0.9
            assert result[1]["score"] == 0.7
            assert result[2]["score"] == 0.5

    # ========== ERROR HANDLING TESTS ==========

    def test_api_error_propagates(self, demo_tool: DemoTool):
        """Test API errors are properly propagated."""
        with patch.object(demo_tool, '_process_query', side_effect=Exception("API failed")):
            with pytest.raises(APIError) as exc_info:
                demo_tool.run()

            assert "API failed" in str(exc_info.value)

    # ========== INTEGRATION TESTS ==========

    def test_full_workflow_with_filtering(self):
        """Test complete workflow with filtering."""
        tool = DemoTool(
            query="python programming",
            max_results=5,
            filter_type="relevant",
            use_cache=False
        )

        result = tool.run()

        assert result["success"] is True
        assert result["total_count"] <= 5
        assert result["metadata"]["query"] == "python programming"
        assert result["metadata"]["filter_type"] == "relevant"

    def test_caching_parameter_preserved(self):
        """Test use_cache parameter is preserved in metadata."""
        tool_with_cache = DemoTool(query="test", use_cache=True)
        tool_no_cache = DemoTool(query="test", use_cache=False)

        result_cached = tool_with_cache.run()
        result_no_cache = tool_no_cache.run()

        assert result_cached["metadata"]["used_cache"] is True
        assert result_no_cache["metadata"]["used_cache"] is False

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize("query,max_results,expected_valid", [
        ("valid query", 10, True),
        ("a" * 500, 10, True),  # Max length
        ("", 10, False),  # Empty query
        ("test", 0, False),  # Invalid max_results
        ("test", 101, False),  # Max_results too high
    ])
    def test_parameter_validation(self, query: str, max_results: int, expected_valid: bool):
        """Test parameter validation with various inputs."""
        if expected_valid:
            tool = DemoTool(query=query, max_results=max_results)
            assert tool.query == query
            assert tool.max_results == max_results
        else:
            with pytest.raises(Exception):  # Could be ValidationError or Pydantic error
                tool = DemoTool(query=query, max_results=max_results)
                tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_query(self):
        """Test Unicode characters in query."""
        tool = DemoTool(query="Python编程", max_results=5)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["query"] == "Python编程"

    def test_special_characters_in_query(self):
        """Test special characters in query."""
        special_query = "query with @#$%^&* special chars"
        tool = DemoTool(query=special_query)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["query"] == special_query

    def test_very_long_query(self):
        """Test query at maximum length."""
        long_query = "a" * 500  # Max length from Field definition
        tool = DemoTool(query=long_query, max_results=5)
        result = tool.run()

        assert result["success"] is True

    # ========== HELPER FUNCTION TESTS ==========

    def test_convenience_function(self):
        """Test run_demo_tool convenience function."""
        from tools._examples.demo_tool.demo_tool import run_demo_tool

        result = run_demo_tool("test query", max_results=5)

        assert result["success"] is True
        assert result["total_count"] <= 5


# ========== INTEGRATION TEST CLASS ==========

class TestDemoToolIntegration:
    """Integration tests with shared modules."""

    def test_analytics_tracking(self, demo_tool: DemoTool, capture_analytics_events):
        """Test analytics are tracked."""
        demo_tool.run()

        # Analytics events should be captured
        # (actual implementation depends on analytics backend)

    def test_rate_limiting_integration(self):
        """Test rate limiting integration."""
        # Rate limiting is handled by BaseTool.run()
        # This test verifies it doesn't break normal flow
        tool = DemoTool(query="test", max_results=5)
        result = tool.run()

        assert result["success"] is True

    def test_error_formatting_integration(self, demo_tool: DemoTool):
        """Test error formatting with shared.errors."""
        with patch.object(demo_tool, '_execute', side_effect=ValueError("Test error")):
            result = demo_tool.run()

            # BaseTool.run() catches and formats errors
            assert "error" in result or result.get("success") is False
