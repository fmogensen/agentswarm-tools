#!/usr/bin/env python3
"""Test visualization tools (15 chart generation tools)"""

import os
import sys
sys.path.insert(0, '/app')

# Bypass rate limiting
from shared import security
security.RateLimiter.check_rate_limit = lambda *args, **kwargs: None

results = {"passed": [], "failed": []}

def test(name, func):
    try:
        print(f"\n{'='*60}\n{name}\n{'='*60}")
        func()
        results["passed"].append(name)
        print(f"✅ {name} PASSED")
        return True
    except Exception as e:
        results["failed"].append(f"{name}: {str(e)[:100]}")
        print(f"❌ {name} FAILED: {e}")
        return False

# Sample data for charts
sample_data_dict = {"A": 30, "B": 50, "C": 40}  # For bar chart
sample_labels = ["A", "B", "C"]
sample_values = [30, 50, 40]
sample_number_list = [100, 120, 110, 105, 130]  # For line chart

# Test 1: Line Chart - expects list of numbers
def test_line_chart():
    from tools.visualization.generate_line_chart.generate_line_chart import GenerateLineChart
    tool = GenerateLineChart(
        prompt="Generate a line chart showing trends over time",
        params={
            "data": sample_number_list,
            "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
            "title": "Test Line Chart"
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated line chart")

# Test 2: Bar Chart - expects dict of category:value
def test_bar_chart():
    from tools.visualization.generate_bar_chart.generate_bar_chart import GenerateBarChart
    tool = GenerateBarChart(
        prompt="Generate a bar chart",
        params={
            "data": sample_data_dict,
            "title": "Test Bar Chart"
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated bar chart")

# Test 3: Pie Chart - expects labels and values as separate lists
def test_pie_chart():
    from tools.visualization.generate_pie_chart.generate_pie_chart import GeneratePieChart
    tool = GeneratePieChart(
        prompt="Generate a pie chart",
        params={
            "labels": sample_labels,
            "values": sample_values,
            "title": "Test Pie Chart"
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated pie chart")

# Test 4: Scatter Chart - expects x and y as separate lists
def test_scatter_chart():
    from tools.visualization.generate_scatter_chart.generate_scatter_chart import GenerateScatterChart
    tool = GenerateScatterChart(
        prompt="Generate a scatter chart",
        params={
            "x": [10, 20, 30, 40],
            "y": [20, 30, 25, 35],
            "title": "Test Scatter Chart"
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated scatter chart")

# Test 5: Area Chart - expects x and y as separate lists
def test_area_chart():
    from tools.visualization.generate_area_chart.generate_area_chart import GenerateAreaChart
    tool = GenerateAreaChart(
        prompt="Generate an area chart",
        params={
            "x": [1, 2, 3, 4, 5],
            "y": [100, 120, 110, 105, 130],
            "title": "Test Area Chart"
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated area chart")

# Test 6: Column Chart - expects categories and values as separate lists
def test_column_chart():
    from tools.visualization.generate_column_chart.generate_column_chart import GenerateColumnChart
    tool = GenerateColumnChart(
        prompt="Generate a column chart",
        params={
            "categories": sample_labels,
            "values": sample_values,
            "title": "Test Column Chart"
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated column chart")

# Test 7: Histogram
def test_histogram():
    from tools.visualization.generate_histogram_chart.generate_histogram_chart import GenerateHistogramChart
    tool = GenerateHistogramChart(
        prompt="Generate a histogram",
        params={"data": [1, 2, 2, 3, 3, 3, 4, 4, 5], "title": "Test Histogram"}
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated histogram")

# Test 8: Word Cloud
def test_word_cloud():
    from tools.visualization.generate_word_cloud_chart.generate_word_cloud_chart import GenerateWordCloudChart
    word_data = [
        {"text": "Python", "value": 100},
        {"text": "JavaScript", "value": 80},
        {"text": "Java", "value": 60}
    ]
    tool = GenerateWordCloudChart(
        prompt="Generate a word cloud",
        params={"data": word_data, "title": "Test Word Cloud"}
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated word cloud")

if __name__ == "__main__":
    print("\n🧪 TESTING VISUALIZATION TOOLS (8 of 15)\n")

    test("1. Line Chart", test_line_chart)
    test("2. Bar Chart", test_bar_chart)
    test("3. Pie Chart", test_pie_chart)
    test("4. Scatter Chart", test_scatter_chart)
    test("5. Area Chart", test_area_chart)
    test("6. Column Chart", test_column_chart)
    test("7. Histogram", test_histogram)
    test("8. Word Cloud", test_word_cloud)

    print(f"\n\n{'='*60}")
    print(f"RESULTS: {len(results['passed'])}/8 passed")
    print(f"{'='*60}")
    for p in results["passed"]:
        print(f"✅ {p}")
    for f in results["failed"]:
        print(f"❌ {f}")
