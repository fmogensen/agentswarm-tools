"""Comprehensive tests for data_aggregator tool."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.data.business.data_aggregator.data_aggregator import DataAggregator


class TestDataAggregator:
    """Test suite for DataAggregator."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_sources(self) -> list:
        """Valid test data sources."""
        return ["10", "20", "30", "40", "50"]

    @pytest.fixture
    def tool(self, valid_sources: list) -> DataAggregator:
        """Create DataAggregator instance with valid parameters."""
        return DataAggregator(sources=valid_sources, aggregation_method="sum")

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, valid_sources: list):
        """Test successful execution."""
        tool = DataAggregator(sources=valid_sources, aggregation_method="sum")
        result = tool.run()
        assert result["success"] is True
        assert "result" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_all_aggregation_methods(self, valid_sources: list):
        """Test all valid aggregation methods."""
        methods = ["sum", "avg", "max", "min", "count", "median"]
        for method in methods:
            tool = DataAggregator(sources=valid_sources, aggregation_method=method)
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["method"] == method

    # ========== SOURCES VALIDATION ==========

    def test_empty_sources_rejected(self):
        """Test that empty sources list is rejected."""
        with pytest.raises(PydanticValidationError):
            DataAggregator(sources=[], aggregation_method="sum")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_single_source(self):
        """Test aggregation with single source."""
        tool = DataAggregator(sources=["100"], aggregation_method="sum")
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_many_sources(self):
        """Test aggregation with many sources."""
        sources = [str(i) for i in range(1, 101)]  # 100 sources
        tool = DataAggregator(sources=sources, aggregation_method="sum")
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["sources_count"] == 100

    # ========== AGGREGATION METHOD VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_invalid_method_rejected(self, valid_sources: list):
        """Test that invalid aggregation method is rejected."""
        tool = DataAggregator(sources=valid_sources, aggregation_method="invalid")
        with pytest.raises(ValidationError, match="aggregation_method must be one of"):
            tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_case_sensitive_method(self, valid_sources: list):
        """Test that method names are case sensitive."""
        tool = DataAggregator(sources=valid_sources, aggregation_method="SUM")
        with pytest.raises(ValidationError):
            tool.run()

    # ========== DATA TYPE HANDLING ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_numeric_strings(self):
        """Test handling of numeric strings."""
        sources = ["10.5", "20.3", "30.7"]
        tool = DataAggregator(sources=sources, aggregation_method="sum")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["valid_values"] == 3

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_mixed_valid_invalid_sources(self):
        """Test handling of mixed valid and invalid sources."""
        sources = ["10", "20", "invalid", "30", "not_a_number"]
        tool = DataAggregator(sources=sources, aggregation_method="sum")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["valid_values"] == 3

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_all_invalid_sources_rejected(self):
        """Test that all invalid sources is rejected."""
        sources = ["invalid", "not_a_number", "abc"]
        tool = DataAggregator(sources=sources, aggregation_method="sum")
        with pytest.raises(ValidationError, match="No valid numeric values"):
            tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_negative_numbers(self):
        """Test handling of negative numbers."""
        sources = ["-10", "-20", "30", "40"]
        tool = DataAggregator(sources=sources, aggregation_method="sum")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["valid_values"] == 4

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_floating_point_numbers(self):
        """Test handling of floating point numbers."""
        sources = ["10.5", "20.3", "30.7", "40.1"]
        tool = DataAggregator(sources=sources, aggregation_method="avg")
        result = tool.run()
        assert result["success"] is True

    # ========== FILTERS VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_min_value_filter(self):
        """Test minimum value filter."""
        sources = ["10", "20", "30", "40", "50"]
        filters = {"min_value": 25}
        tool = DataAggregator(sources=sources, aggregation_method="sum", filters=filters)
        result = tool.run()
        assert result["success"] is True
        # Only 30, 40, 50 should pass filter
        assert result["result"]["valid_values"] == 3

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_max_value_filter(self):
        """Test maximum value filter."""
        sources = ["10", "20", "30", "40", "50"]
        filters = {"max_value": 35}
        tool = DataAggregator(sources=sources, aggregation_method="count", filters=filters)
        result = tool.run()
        assert result["success"] is True
        # Only 10, 20, 30 should pass filter
        assert result["result"]["valid_values"] == 3

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_min_and_max_filter(self):
        """Test both min and max value filters."""
        sources = ["10", "20", "30", "40", "50"]
        filters = {"min_value": 20, "max_value": 40}
        tool = DataAggregator(sources=sources, aggregation_method="count", filters=filters)
        result = tool.run()
        assert result["success"] is True
        # Only 20, 30, 40 should pass filter
        assert result["result"]["valid_values"] == 3

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_filters_remove_all_values(self):
        """Test that filters removing all values is rejected."""
        sources = ["10", "20", "30"]
        filters = {"min_value": 100}
        tool = DataAggregator(sources=sources, aggregation_method="sum", filters=filters)
        with pytest.raises(ValidationError, match="No values remain after applying filters"):
            tool.run()

    # ========== AGGREGATION OPERATIONS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_sum_aggregation(self):
        """Test sum aggregation."""
        sources = ["10", "20", "30"]
        tool = DataAggregator(sources=sources, aggregation_method="sum")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["aggregated_value"] == 60

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_avg_aggregation(self):
        """Test average aggregation."""
        sources = ["10", "20", "30"]
        tool = DataAggregator(sources=sources, aggregation_method="avg")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["aggregated_value"] == 20

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_max_aggregation(self):
        """Test max aggregation."""
        sources = ["10", "50", "30"]
        tool = DataAggregator(sources=sources, aggregation_method="max")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["aggregated_value"] == 50

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_min_aggregation(self):
        """Test min aggregation."""
        sources = ["10", "50", "30"]
        tool = DataAggregator(sources=sources, aggregation_method="min")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["aggregated_value"] == 10

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_count_aggregation(self):
        """Test count aggregation."""
        sources = ["10", "20", "30", "40"]
        tool = DataAggregator(sources=sources, aggregation_method="count")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["aggregated_value"] == 4

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_median_aggregation(self):
        """Test median aggregation."""
        sources = ["10", "20", "30", "40", "50"]
        tool = DataAggregator(sources=sources, aggregation_method="median")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["aggregated_value"] == 30

    # ========== ERROR HANDLING ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_error_handling(self, valid_sources: list):
        """Test general error handling."""
        tool = DataAggregator(sources=valid_sources, aggregation_method="sum")
        with patch.object(tool, "_process", side_effect=Exception("Processing error")):
            with pytest.raises(APIError, match="Aggregation failed"):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_enabled(self, valid_sources: list):
        """Test that mock mode returns mock data."""
        tool = DataAggregator(sources=valid_sources, aggregation_method="sum")
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    # ========== RESULT FORMAT VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_result_format(self, valid_sources: list):
        """Test that results have correct format."""
        tool = DataAggregator(sources=valid_sources, aggregation_method="sum")
        result = tool.run()

        assert "success" in result
        assert "result" in result
        assert "metadata" in result

        # Check result data structure
        data = result["result"]
        assert "aggregated_value" in data
        assert "sources_processed" in data
        assert "valid_values" in data
        assert "method" in data
        assert "data_points" in data

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "sources,method,filters,expected_valid",
        [
            (["10", "20", "30"], "sum", None, True),
            (["10", "20", "30"], "avg", None, True),
            (["10", "20", "30"], "max", None, True),
            (["10", "20", "30"], "min", None, True),
            (["10", "20", "30"], "count", None, True),
            (["10", "20", "30"], "median", None, True),
            (["10", "20", "30"], "sum", {"min_value": 15}, True),
            ([], "sum", None, False),  # Empty sources
            (["10", "20"], "invalid", None, False),  # Invalid method
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_parameter_combinations(
        self, sources: list, method: str, filters: dict, expected_valid: bool
    ):
        """Test various parameter combinations."""
        if expected_valid:
            tool = DataAggregator(sources=sources, aggregation_method=method, filters=filters)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = DataAggregator(sources=sources, aggregation_method=method, filters=filters)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_full_workflow(self):
        """Test complete workflow for data aggregation."""
        # Create tool
        sources = ["100", "200", "300", "400", "500"]
        tool = DataAggregator(sources=sources, aggregation_method="avg")

        # Verify parameters
        assert tool.sources == sources
        assert tool.aggregation_method == "avg"
        assert tool.tool_name == "data_aggregator"
        assert tool.tool_category == "data"

        # Execute
        result = tool.run()

        # Verify results
        assert result["success"] is True
        assert result["result"]["aggregated_value"] == 300
        assert result["result"]["valid_values"] == 5

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_complex_filtering_workflow(self):
        """Test complex filtering workflow."""
        sources = [str(i * 10) for i in range(1, 11)]  # 10, 20, 30...100
        filters = {"min_value": 30, "max_value": 70}
        tool = DataAggregator(sources=sources, aggregation_method="sum", filters=filters)

        result = tool.run()

        # Should include 30, 40, 50, 60, 70 = 250
        assert result["success"] is True
        assert result["result"]["aggregated_value"] == 250
        assert result["result"]["valid_values"] == 5

    # ========== TOOL METADATA TESTS ==========

    def test_tool_category(self, tool: DataAggregator):
        """Test tool category is correct."""
        assert tool.tool_category == "data"

    def test_tool_name(self, tool: DataAggregator):
        """Test tool name is correct."""
        assert tool.tool_name == "data_aggregator"
