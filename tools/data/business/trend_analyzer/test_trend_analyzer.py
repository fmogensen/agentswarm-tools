"""Test cases for TrendAnalyzer tool."""

import os

import pytest

from shared.errors import ValidationError

from .trend_analyzer import TrendAnalyzer


class TestTrendAnalyzer:
    """Test suite for TrendAnalyzer tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_trend_analysis(self):
        """Test trend analysis."""
        tool = TrendAnalyzer(data_points=[10, 12, 15, 18, 20], analysis_type="trend")
        result = tool.run()

        assert result["success"] == True
        assert "trend_analysis" in result["result"]

    def test_volatility_analysis(self):
        """Test volatility analysis."""
        tool = TrendAnalyzer(data_points=[10, 20, 15, 25, 18], analysis_type="volatility")
        result = tool.run()

        assert result["success"] == True
        assert "volatility_analysis" in result["result"]

    def test_seasonality_analysis(self):
        """Test seasonality analysis."""
        tool = TrendAnalyzer(data_points=[10, 20, 10, 20, 10, 20], analysis_type="seasonality")
        result = tool.run()

        assert result["success"] == True
        assert "seasonality_analysis" in result["result"]

    def test_all_analysis(self):
        """Test all analysis types."""
        tool = TrendAnalyzer(data_points=[10, 12, 15, 14, 18, 20], analysis_type="all")
        result = tool.run()

        assert result["success"] == True
        assert "trend_analysis" in result["result"]
        assert "volatility_analysis" in result["result"]
        assert "seasonality_analysis" in result["result"]
        assert "statistics" in result["result"]

    def test_with_time_labels(self):
        """Test with time labels."""
        tool = TrendAnalyzer(
            data_points=[10, 20, 30],
            time_labels=["2024-01", "2024-02", "2024-03"],
            analysis_type="trend",
        )
        result = tool.run()

        assert result["success"] == True

    def test_moving_average(self):
        """Test moving average calculation."""
        tool = TrendAnalyzer(data_points=[10, 20, 30, 40, 50], analysis_type="trend", window_size=3)
        result = tool.run()

        assert result["success"] == True
        assert "moving_average" in result["result"]
        assert len(result["result"]["moving_average"]) > 0

    def test_statistics(self):
        """Test statistics calculation."""
        tool = TrendAnalyzer(data_points=[10, 20, 30], analysis_type="trend")
        result = tool.run()

        assert result["success"] == True
        assert "statistics" in result["result"]
        stats = result["result"]["statistics"]
        assert "mean" in stats
        assert "median" in stats
        assert "std_dev" in stats

    def test_invalid_analysis_type(self):
        """Test invalid analysis type."""
        with pytest.raises(ValidationError):
            tool = TrendAnalyzer(data_points=[10, 20], analysis_type="invalid")
            tool._validate_parameters()

    def test_insufficient_data_points(self):
        """Test insufficient data points."""
        with pytest.raises(Exception):  # Pydantic will catch min_items=2
            tool = TrendAnalyzer(data_points=[10], analysis_type="trend")

    def test_mismatched_time_labels(self):
        """Test mismatched time labels."""
        with pytest.raises(ValidationError):
            tool = TrendAnalyzer(
                data_points=[10, 20, 30],
                time_labels=["2024-01", "2024-02"],  # Only 2 labels for 3 points
                analysis_type="trend",
            )
            tool._validate_parameters()

    def test_window_size_too_large(self):
        """Test window size larger than data points."""
        with pytest.raises(ValidationError):
            tool = TrendAnalyzer(data_points=[10, 20], window_size=5, analysis_type="trend")
            tool._validate_parameters()

    def test_mock_mode(self):
        """Test mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = TrendAnalyzer(data_points=[10, 20, 30], analysis_type="trend")
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
