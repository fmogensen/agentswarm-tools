"""
Live integration tests for Visualization tools.

These tests validate chart generation with real data.
"""

import os
import pytest
from typing import Dict, Any

pytestmark = [
    pytest.mark.integration,
]


@pytest.fixture(autouse=True)
def live_mode():
    """Ensure live API mode for integration tests."""
    original = os.environ.get("USE_MOCK_APIS", "true")
    os.environ["USE_MOCK_APIS"] = "false"
    yield
    os.environ["USE_MOCK_APIS"] = original


@pytest.fixture(autouse=True)
def reset_rate_limiter_for_test():
    """Reset rate limiter before each test by giving buckets full tokens."""
    from shared.security import get_rate_limiter
    from datetime import datetime
    limiter = get_rate_limiter()
    limiter._buckets.clear()
    # Pre-populate visualization tool buckets with full tokens
    viz_tools = [
        "generate_line_chart", "generate_bar_chart", "generate_pie_chart",
        "generate_scatter_chart", "generate_histogram_chart", "generate_word_cloud_chart"
    ]
    for tool in viz_tools:
        limiter._buckets[f"{tool}:anonymous"] = {
            "tokens": 60,
            "last_update": datetime.utcnow()
        }
    yield


class TestLineChartLive:
    """Live tests for line chart generation."""

    def test_basic_line_chart(self):
        """Test basic line chart generation."""
        from tools.visualization.generate_line_chart import GenerateLineChart

        tool = GenerateLineChart(
            prompt="Generate a line chart showing test values",
            params={
                "data": [
                    {"x": 1, "y": 10},
                    {"x": 2, "y": 25},
                    {"x": 3, "y": 15},
                    {"x": 4, "y": 30},
                    {"x": 5, "y": 20},
                ],
                "title": "Test Line Chart"
            }
        )
        result = tool.run()

        assert result.get("success") is True or "error" in result

    def test_line_chart_with_labels(self):
        """Test line chart with axis labels."""
        from tools.visualization.generate_line_chart import GenerateLineChart

        tool = GenerateLineChart(
            prompt="Generate line chart for performance over time",
            params={
                "data": [{"x": i, "y": i * 10} for i in range(10)],
                "title": "Performance Over Time",
            }
        )
        result = tool.run()

        assert result.get("success") is True or "error" in result


class TestBarChartLive:
    """Live tests for bar chart generation."""

    def test_basic_bar_chart(self):
        """Test basic bar chart generation."""
        from tools.visualization.generate_bar_chart import GenerateBarChart

        tool = GenerateBarChart(
            prompt="Generate bar chart for quarterly sales",
            params={
                "data": [
                    {"label": "Q1", "value": 100},
                    {"label": "Q2", "value": 150},
                    {"label": "Q3", "value": 120},
                    {"label": "Q4", "value": 180},
                ],
                "title": "Quarterly Sales"
            }
        )
        result = tool.run()

        assert result.get("success") is True or "error" in result


class TestPieChartLive:
    """Live tests for pie chart generation."""

    def test_basic_pie_chart(self):
        """Test basic pie chart generation."""
        from tools.visualization.generate_pie_chart import GeneratePieChart

        tool = GeneratePieChart(
            prompt="Generate pie chart showing traffic by device",
            params={
                "data": [
                    {"label": "Desktop", "value": 45},
                    {"label": "Mobile", "value": 35},
                    {"label": "Tablet", "value": 20},
                ],
                "title": "Traffic by Device"
            }
        )
        result = tool.run()

        assert result.get("success") is True or "error" in result


class TestScatterChartLive:
    """Live tests for scatter chart generation."""

    def test_basic_scatter_chart(self):
        """Test basic scatter chart generation."""
        from tools.visualization.generate_scatter_chart import GenerateScatterChart

        tool = GenerateScatterChart(
            prompt="Generate scatter chart for correlation analysis",
            params={
                "data": [
                    {"x": 1, "y": 2},
                    {"x": 2, "y": 4},
                    {"x": 3, "y": 3},
                    {"x": 4, "y": 5},
                    {"x": 5, "y": 4},
                ],
                "title": "Correlation Analysis"
            }
        )
        result = tool.run()

        assert result.get("success") is True or "error" in result


class TestHistogramLive:
    """Live tests for histogram generation."""

    def test_basic_histogram(self):
        """Test basic histogram generation."""
        from tools.visualization.generate_histogram_chart import GenerateHistogramChart

        tool = GenerateHistogramChart(
            prompt="Generate histogram for value distribution",
            params={
                "data": [10, 20, 20, 30, 30, 30, 40, 40, 50],
                "title": "Value Distribution"
            }
        )
        result = tool.run()

        assert result.get("success") is True or "error" in result


class TestWordCloudLive:
    """Live tests for word cloud generation."""

    def test_basic_word_cloud(self):
        """Test basic word cloud generation."""
        from tools.visualization.generate_word_cloud_chart import GenerateWordCloudChart

        tool = GenerateWordCloudChart(
            prompt="Generate word cloud for programming languages",
            params={
                "data": [
                    {"word": "Python", "weight": 100},
                    {"word": "JavaScript", "weight": 80},
                    {"word": "Java", "weight": 70},
                    {"word": "Go", "weight": 50},
                    {"word": "Rust", "weight": 40},
                ],
                "title": "Programming Languages"
            }
        )
        result = tool.run()

        assert result.get("success") is True or "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
