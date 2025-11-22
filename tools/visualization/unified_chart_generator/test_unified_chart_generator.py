"""
Tests for UnifiedChartGenerator
"""

import os
import pytest
from unittest.mock import patch

# Set mock mode before importing
os.environ["USE_MOCK_APIS"] = "true"

from tools.visualization.unified_chart_generator import UnifiedChartGenerator
from shared.errors import ValidationError


class TestUnifiedChartGenerator:
    """Test suite for UnifiedChartGenerator."""

    def test_line_chart_simple(self):
        """Test line chart with simple numeric data."""
        tool = UnifiedChartGenerator(chart_type="line", data=[1, 2, 3, 4, 5], title="Sales Trend")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["chart_type"] == "line"
        assert result["result"]["mock"] == True

    def test_line_chart_with_xy(self):
        """Test line chart with x,y object data."""
        tool = UnifiedChartGenerator(
            chart_type="line",
            data=[{"x": 0, "y": 1}, {"x": 1, "y": 2}, {"x": 2, "y": 4}],
            title="Growth",
        )
        result = tool.run()

        assert result["success"] == True

    def test_bar_chart_dict(self):
        """Test bar chart with dict data."""
        tool = UnifiedChartGenerator(
            chart_type="bar", data={"North": 45, "South": 32, "East": 38}, title="Sales by Region"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["chart_type"] == "bar"

    def test_bar_chart_list(self):
        """Test bar chart with list data."""
        tool = UnifiedChartGenerator(
            chart_type="bar",
            data=[{"label": "Q1", "value": 100}, {"label": "Q2", "value": 150}],
            title="Quarterly Sales",
        )
        result = tool.run()

        assert result["success"] == True

    def test_pie_chart(self):
        """Test pie chart."""
        tool = UnifiedChartGenerator(
            chart_type="pie",
            data=[{"label": "A", "value": 30}, {"label": "B", "value": 70}],
            title="Market Share",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["chart_type"] == "pie"

    def test_scatter_chart(self):
        """Test scatter chart."""
        tool = UnifiedChartGenerator(
            chart_type="scatter", data={"x": [1, 2, 3], "y": [2, 4, 6]}, title="Correlation"
        )
        result = tool.run()

        assert result["success"] == True

    def test_area_chart(self):
        """Test area chart."""
        tool = UnifiedChartGenerator(
            chart_type="area", data=[10, 20, 15, 25, 30], title="Cumulative Sales"
        )
        result = tool.run()

        assert result["success"] == True

    def test_histogram(self):
        """Test histogram."""
        tool = UnifiedChartGenerator(
            chart_type="histogram",
            data=[1.2, 1.5, 1.8, 2.1, 2.3, 2.5, 2.8, 3.0],
            title="Distribution",
        )
        result = tool.run()

        assert result["success"] == True

    def test_dual_axes(self):
        """Test dual axes chart."""
        tool = UnifiedChartGenerator(
            chart_type="dual_axes",
            data={"primary": [10, 20, 30], "secondary": [100, 150, 200]},
            title="Revenue & Units",
        )
        result = tool.run()

        assert result["success"] == True

    def test_radar_chart(self):
        """Test radar chart."""
        tool = UnifiedChartGenerator(
            chart_type="radar",
            data={"categories": ["Speed", "Power", "Range"], "values": [8, 6, 9]},
            title="Product Comparison",
        )
        result = tool.run()

        assert result["success"] == True

    def test_invalid_chart_type(self):
        """Test invalid chart type raises error."""
        with pytest.raises(ValidationError):
            tool = UnifiedChartGenerator(chart_type="invalid", data=[1, 2, 3])
            tool.run()

    def test_options_passed_through(self):
        """Test that options are passed to renderer."""
        tool = UnifiedChartGenerator(
            chart_type="line",
            data=[1, 2, 3],
            title="Test",
            options={"x_label": "Time", "y_label": "Value", "grid": False},
        )
        result = tool.run()

        assert result["success"] == True

    def test_custom_dimensions(self):
        """Test custom width and height."""
        tool = UnifiedChartGenerator(
            chart_type="bar", data={"A": 10, "B": 20}, width=1200, height=800
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["width"] == 1200
        assert result["result"]["height"] == 800


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
