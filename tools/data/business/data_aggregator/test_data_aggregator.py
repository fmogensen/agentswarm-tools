"""Test cases for DataAggregator tool."""

import os

import pytest

from shared.errors import ValidationError

from .data_aggregator import DataAggregator


class TestDataAggregator:
    """Test suite for DataAggregator tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_sum_aggregation(self):
        """Test sum aggregation."""
        tool = DataAggregator(sources=["10", "20", "30"], aggregation_method="sum")
        result = tool.run()

        assert result["success"] == True
        assert "result" in result
        assert result["result"]["method"] == "sum"

    def test_avg_aggregation(self):
        """Test average aggregation."""
        tool = DataAggregator(sources=["10", "20", "30"], aggregation_method="avg")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["method"] == "avg"

    def test_max_aggregation(self):
        """Test max aggregation."""
        tool = DataAggregator(sources=["10", "20", "30"], aggregation_method="max")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["method"] == "max"

    def test_min_aggregation(self):
        """Test min aggregation."""
        tool = DataAggregator(sources=["10", "20", "30"], aggregation_method="min")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["method"] == "min"

    def test_count_aggregation(self):
        """Test count aggregation."""
        tool = DataAggregator(sources=["10", "20", "30"], aggregation_method="count")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["method"] == "count"

    def test_median_aggregation(self):
        """Test median aggregation."""
        tool = DataAggregator(sources=["10", "20", "30"], aggregation_method="median")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["method"] == "median"

    def test_invalid_method(self):
        """Test invalid aggregation method."""
        with pytest.raises(ValidationError):
            tool = DataAggregator(sources=["10", "20"], aggregation_method="invalid")
            tool._validate_parameters()

    def test_empty_sources(self):
        """Test empty sources."""
        with pytest.raises(Exception):  # Pydantic will catch min_items=1
            tool = DataAggregator(sources=[], aggregation_method="sum")

    def test_with_filters(self):
        """Test aggregation with filters."""
        tool = DataAggregator(
            sources=["10", "20", "30"], aggregation_method="sum", filters={"min_value": 15}
        )
        result = tool.run()

        assert result["success"] == True

    def test_mock_mode(self):
        """Test mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = DataAggregator(sources=["10", "20", "30"], aggregation_method="sum")
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
