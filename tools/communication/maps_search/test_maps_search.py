"""Tests for maps_search tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from tools.location.maps_search import MapsSearch
from shared.errors import ValidationError, APIError


class TestMapsSearch:
    """Test suite for MapsSearch."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_tool(self) -> MapsSearch:
        """Create tool instance with valid parameters."""
        return MapsSearch(query="test location", max_results=5)

    @pytest.fixture
    def mock_results(self) -> list:
        """Mock API results."""
        return [
            {
                "name": f"Mock Place {i}",
                "address": f"Mock Address {i}",
                "type": "mock",
                "rating": 4.5,
            }
            for i in range(1, 6)
        ]

    # ========== HAPPY PATH ==========

    def test_execute_success(self, valid_tool: MapsSearch):
        """Test successful execution."""
        with patch.object(
            valid_tool,
            "_process",
            return_value=valid_tool._generate_mock_results()["result"],
        ):
            result = valid_tool.run()
            assert result["success"] is True
            assert "result" in result
            assert len(result["result"]) == 5

    def test_metadata_correct(self, valid_tool: MapsSearch):
        """Test tool metadata."""
        assert valid_tool.tool_name == "maps_search"
        assert valid_tool.tool_category == "location"

    # ========== ERROR CASES ==========

    def test_validation_error_empty_query(self):
        """Test validation errors for empty query - fails Pydantic min_length=1."""
        with pytest.raises(PydanticValidationError):
            MapsSearch(query="", max_results=5)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, valid_tool: MapsSearch):
        """Test API error handling."""
        with patch.object(valid_tool, "_process", side_effect=Exception("API failed")):
            result = valid_tool.run()
            assert result["success"] is False

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, valid_tool: MapsSearch):
        """Test mock mode returns mock data."""
        result = valid_tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert len(result["result"]) == 5

    # ========== EDGE CASES ==========

    def test_max_results_boundary_values(self):
        """Test max_results at boundary values."""
        # Minimum (1)
        tool = MapsSearch(query="test", max_results=1)
        assert tool.max_results == 1

        # Maximum (50)
        tool = MapsSearch(query="test", max_results=50)
        assert tool.max_results == 50

        # Below minimum should fail Pydantic validation
        with pytest.raises(PydanticValidationError):
            MapsSearch(query="test", max_results=0)

        # Above maximum should fail Pydantic validation
        with pytest.raises(PydanticValidationError):
            MapsSearch(query="test", max_results=51)

    def test_unicode_query(self):
        """Test Unicode characters in query."""
        tool = MapsSearch(query="日本", max_results=5)
        with patch.object(tool, "_process", return_value=tool._generate_mock_results()["result"]):
            result = tool.run()
            assert result["success"] is True

    def test_special_characters_in_query(self):
        """Test special characters in query."""
        special_query = "query with @#$%^&* special chars"
        tool = MapsSearch(query=special_query, max_results=5)
        with patch.object(tool, "_process", return_value=tool._generate_mock_results()["result"]):
            result = tool.run()
            assert result["success"] is True

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "query,max_results,expected_valid,is_pydantic_error",
        [
            ("valid query", 10, True, False),
            ("a" * 500, 10, True, False),  # Max length
            ("", 10, False, True),  # Empty query - Pydantic min_length=1
            ("test", 0, False, True),  # Invalid max_results - Pydantic
            ("test", 51, False, True),  # Max_results too high - Pydantic
        ],
    )
    def test_parameter_validation(
        self, query: str, max_results: int, expected_valid: bool, is_pydantic_error: bool
    ):
        """Test parameter validation with various inputs."""
        if expected_valid:
            tool = MapsSearch(query=query, max_results=max_results)
            assert tool.query == query
            assert tool.max_results == max_results
        elif is_pydantic_error:
            with pytest.raises(PydanticValidationError):
                MapsSearch(query=query, max_results=max_results)
        else:
            tool = MapsSearch(query=query, max_results=max_results)
            result = tool.run()
            assert result["success"] is False
