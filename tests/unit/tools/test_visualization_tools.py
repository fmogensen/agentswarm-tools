"""
Comprehensive unit tests for Visualization Tools category.

Tests all 16 visualization tools from Chart Server MCP:
- generate_line_chart, generate_bar_chart, generate_pie_chart, generate_scatter_chart
- generate_area_chart, generate_column_chart, generate_dual_axes_chart
- generate_fishbone_diagram, generate_flow_diagram, generate_histogram_chart
- generate_mind_map, generate_network_graph, generate_radar_chart
- generate_treemap_chart, generate_word_cloud_chart, generate_organization_chart
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any, List

from tools.visualization.generate_line_chart.generate_line_chart import GenerateLineChart
from tools.visualization.generate_bar_chart.generate_bar_chart import GenerateBarChart
from tools.visualization.generate_pie_chart.generate_pie_chart import GeneratePieChart
from tools.visualization.generate_scatter_chart.generate_scatter_chart import GenerateScatterChart
from tools.visualization.generate_area_chart.generate_area_chart import GenerateAreaChart
from tools.visualization.generate_column_chart.generate_column_chart import GenerateColumnChart
from tools.visualization.generate_dual_axes_chart.generate_dual_axes_chart import (
    GenerateDualAxesChart,
)
from tools.visualization.generate_fishbone_diagram.generate_fishbone_diagram import (
    GenerateFishboneDiagram,
)
from tools.visualization.generate_flow_diagram.generate_flow_diagram import GenerateFlowDiagram
from tools.visualization.generate_histogram_chart.generate_histogram_chart import (
    GenerateHistogramChart,
)
from tools.visualization.generate_mind_map.generate_mind_map import GenerateMindMap
from tools.visualization.generate_network_graph.generate_network_graph import GenerateNetworkGraph
from tools.visualization.generate_radar_chart.generate_radar_chart import GenerateRadarChart
from tools.visualization.generate_treemap_chart.generate_treemap_chart import GenerateTreemapChart
from tools.visualization.generate_word_cloud_chart.generate_word_cloud_chart import (
    GenerateWordCloudChart,
)
from tools.visualization.generate_organization_chart.generate_organization_chart import (
    GenerateOrganizationChart,
)

from shared.errors import ValidationError, APIError


# ========== GenerateLineChart Tests ==========


class TestGenerateLineChart:
    """Comprehensive tests for GenerateLineChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [{"x": 1, "y": 10}, {"x": 2, "y": 20}, {"x": 3, "y": 15}]
        tool = GenerateLineChart(
            prompt="Sales Over Time",
            params={
                "data": data,
                "title": "Sales Over Time",
                "width": 800,
                "height": 600
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Sales Over Time"
        assert tool.params.get("width") == 800
        assert tool.params.get("height") == 600
        assert tool.tool_name == "generate_line_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [{"x": 1, "y": 10}, {"x": 2, "y": 20}]
        tool = GenerateLineChart(
            prompt="Test Chart",
            params={
                "data": data,
                "title": "Test Chart"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_data(self):
        """Test validation with empty data"""
        tool = GenerateLineChart(
            prompt="Test",
            params={
                "data": [],
                "title": "Test"
            }
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_data_format(self):
        """Test validation with invalid data format"""
        tool = GenerateLineChart(
            prompt="Test",
            params={
                "data": [{"a": 1}],
                "title": "Test"
            }
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== GenerateBarChart Tests ==========


class TestGenerateBarChart:
    """Comprehensive tests for GenerateBarChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [{"category": "A", "value": 10}, {"category": "B", "value": 20}]
        tool = GenerateBarChart(
            prompt="Category Comparison",
            params={
                "data": data,
                "title": "Category Comparison"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Category Comparison"
        assert tool.tool_name == "generate_bar_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [{"category": "Q1", "value": 100}, {"category": "Q2", "value": 150}]
        tool = GenerateBarChart(
            prompt="Quarterly Results",
            params={
                "data": data,
                "title": "Quarterly Results"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GeneratePieChart Tests ==========


class TestGeneratePieChart:
    """Comprehensive tests for GeneratePieChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [{"label": "Category A", "value": 30}, {"label": "Category B", "value": 70}]
        tool = GeneratePieChart(
            prompt="Distribution",
            params={
                "data": data,
                "title": "Distribution"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Distribution"
        assert tool.tool_name == "generate_pie_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [{"label": "Apple", "value": 40}, {"label": "Orange", "value": 60}]
        tool = GeneratePieChart(
            prompt="Fruit Distribution",
            params={
                "data": data,
                "title": "Fruit Distribution"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_negative_values(self):
        """Test validation with negative values"""
        data = [{"label": "A", "value": -10}, {"label": "B", "value": 20}]
        tool = GeneratePieChart(
            prompt="Test",
            params={
                "data": data,
                "title": "Test"
            }
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== GenerateScatterChart Tests ==========


class TestGenerateScatterChart:
    """Comprehensive tests for GenerateScatterChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [{"x": 1, "y": 2}, {"x": 2, "y": 4}, {"x": 3, "y": 6}]
        tool = GenerateScatterChart(
            prompt="Correlation Plot",
            params={
                "data": data,
                "title": "Correlation Plot"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Correlation Plot"
        assert tool.tool_name == "generate_scatter_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [{"x": 10, "y": 20}, {"x": 15, "y": 25}]
        tool = GenerateScatterChart(
            prompt="Test Scatter",
            params={
                "data": data,
                "title": "Test Scatter"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateAreaChart Tests ==========


class TestGenerateAreaChart:
    """Comprehensive tests for GenerateAreaChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [{"x": 1, "y": 10}, {"x": 2, "y": 20}, {"x": 3, "y": 15}]
        tool = GenerateAreaChart(
            prompt="Area Trend",
            params={
                "data": data,
                "title": "Area Trend"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Area Trend"
        assert tool.tool_name == "generate_area_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [{"x": 1, "y": 5}, {"x": 2, "y": 10}]
        tool = GenerateAreaChart(
            prompt="Test Area",
            params={
                "data": data,
                "title": "Test Area"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateColumnChart Tests ==========


class TestGenerateColumnChart:
    """Comprehensive tests for GenerateColumnChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [{"category": "Jan", "value": 100}, {"category": "Feb", "value": 120}]
        tool = GenerateColumnChart(
            prompt="Monthly Sales",
            params={
                "data": data,
                "title": "Monthly Sales"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Monthly Sales"
        assert tool.tool_name == "generate_column_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [{"category": "A", "value": 50}, {"category": "B", "value": 75}]
        tool = GenerateColumnChart(
            prompt="Test Column",
            params={
                "data": data,
                "title": "Test Column"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateDualAxesChart Tests ==========


class TestGenerateDualAxesChart:
    """Comprehensive tests for GenerateDualAxesChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = {
            "primary": [{"x": 1, "y": 10}, {"x": 2, "y": 20}],
            "secondary": [{"x": 1, "y": 100}, {"x": 2, "y": 200}],
        }
        tool = GenerateDualAxesChart(
            prompt="Dual Axes Chart",
            params={
                "data": data,
                "title": "Dual Axes Chart"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Dual Axes Chart"
        assert tool.tool_name == "generate_dual_axes_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = {"primary": [{"x": 1, "y": 5}], "secondary": [{"x": 1, "y": 50}]}
        tool = GenerateDualAxesChart(
            prompt="Test Dual",
            params={
                "data": data,
                "title": "Test Dual"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateFishboneDiagram Tests ==========


class TestGenerateFishboneDiagram:
    """Comprehensive tests for GenerateFishboneDiagram tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = {
            "problem": "Low Sales",
            "causes": {
                "Marketing": ["Poor ads", "Low budget"],
                "Product": ["Quality issues", "High price"],
            },
        }
        tool = GenerateFishboneDiagram(
            prompt="Root Cause Analysis",
            params={
                "data": data,
                "title": "Root Cause Analysis"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Root Cause Analysis"
        assert tool.tool_name == "generate_fishbone_diagram"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = {"problem": "Test", "causes": {"Category1": ["Cause1"]}}
        tool = GenerateFishboneDiagram(
            prompt="Test Fishbone",
            params={
                "data": data,
                "title": "Test Fishbone"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateFlowDiagram Tests ==========


class TestGenerateFlowDiagram:
    """Comprehensive tests for GenerateFlowDiagram tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = {
            "nodes": [{"id": "1", "label": "Start"}, {"id": "2", "label": "Process"}],
            "edges": [{"from": "1", "to": "2"}],
        }
        tool = GenerateFlowDiagram(
            prompt="Process Flow",
            params={
                "data": data,
                "title": "Process Flow"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Process Flow"
        assert tool.tool_name == "generate_flow_diagram"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = {"nodes": [{"id": "A", "label": "Node A"}], "edges": []}
        tool = GenerateFlowDiagram(
            prompt="Test Flow",
            params={
                "data": data,
                "title": "Test Flow"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateHistogramChart Tests ==========


class TestGenerateHistogramChart:
    """Comprehensive tests for GenerateHistogramChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
        tool = GenerateHistogramChart(
            prompt="Distribution",
            params={
                "data": data,
                "title": "Distribution",
                "bins": 5
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Distribution"
        assert tool.params.get("bins") == 5
        assert tool.tool_name == "generate_histogram_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [1, 2, 3, 4, 5]
        tool = GenerateHistogramChart(
            prompt="Test Histogram",
            params={
                "data": data,
                "title": "Test Histogram"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateMindMap Tests ==========


class TestGenerateMindMap:
    """Comprehensive tests for GenerateMindMap tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = {
            "central": "Project",
            "branches": [
                {"label": "Planning", "children": ["Timeline", "Budget"]},
                {"label": "Execution", "children": ["Tasks", "Resources"]},
            ],
        }
        tool = GenerateMindMap(
            prompt="Project Mind Map",
            params={
                "data": data,
                "title": "Project Mind Map"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Project Mind Map"
        assert tool.tool_name == "generate_mind_map"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = {"central": "Main", "branches": [{"label": "Branch1", "children": []}]}
        tool = GenerateMindMap(
            prompt="Test Mind Map",
            params={
                "data": data,
                "title": "Test Mind Map"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateNetworkGraph Tests ==========


class TestGenerateNetworkGraph:
    """Comprehensive tests for GenerateNetworkGraph tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = {
            "nodes": [{"id": "1", "label": "Node 1"}, {"id": "2", "label": "Node 2"}],
            "edges": [{"source": "1", "target": "2", "weight": 1}],
        }
        tool = GenerateNetworkGraph(
            prompt="Network Diagram",
            params={
                "data": data,
                "title": "Network Diagram"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Network Diagram"
        assert tool.tool_name == "generate_network_graph"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = {"nodes": [{"id": "A", "label": "A"}], "edges": []}
        tool = GenerateNetworkGraph(
            prompt="Test Network",
            params={
                "data": data,
                "title": "Test Network"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateRadarChart Tests ==========


class TestGenerateRadarChart:
    """Comprehensive tests for GenerateRadarChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [
            {"axis": "Speed", "value": 80},
            {"axis": "Reliability", "value": 90},
            {"axis": "Cost", "value": 60},
        ]
        tool = GenerateRadarChart(
            prompt="Performance Metrics",
            params={
                "data": data,
                "title": "Performance Metrics"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Performance Metrics"
        assert tool.tool_name == "generate_radar_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [{"axis": "A", "value": 50}, {"axis": "B", "value": 75}]
        tool = GenerateRadarChart(
            prompt="Test Radar",
            params={
                "data": data,
                "title": "Test Radar"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateTreemapChart Tests ==========


class TestGenerateTreemapChart:
    """Comprehensive tests for GenerateTreemapChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [
            {"name": "Category A", "value": 100, "children": []},
            {"name": "Category B", "value": 200, "children": []},
        ]
        tool = GenerateTreemapChart(
            prompt="Hierarchy View",
            params={
                "data": data,
                "title": "Hierarchy View"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Hierarchy View"
        assert tool.tool_name == "generate_treemap_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [{"name": "A", "value": 50, "children": []}]
        tool = GenerateTreemapChart(
            prompt="Test Treemap",
            params={
                "data": data,
                "title": "Test Treemap"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateWordCloudChart Tests ==========


class TestGenerateWordCloudChart:
    """Comprehensive tests for GenerateWordCloudChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = [
            {"word": "Python", "frequency": 100},
            {"word": "JavaScript", "frequency": 80},
            {"word": "Java", "frequency": 60},
        ]
        tool = GenerateWordCloudChart(
            prompt="Programming Languages",
            params={
                "data": data,
                "title": "Programming Languages"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Programming Languages"
        assert tool.tool_name == "generate_word_cloud_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = [{"word": "Test", "frequency": 10}]
        tool = GenerateWordCloudChart(
            prompt="Test Word Cloud",
            params={
                "data": data,
                "title": "Test Word Cloud"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True


# ========== GenerateOrganizationChart Tests ==========


class TestGenerateOrganizationChart:
    """Comprehensive tests for GenerateOrganizationChart tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        data = {
            "name": "CEO",
            "children": [{"name": "CTO", "children": []}, {"name": "CFO", "children": []}],
        }
        tool = GenerateOrganizationChart(
            prompt="Company Structure",
            params={
                "data": data,
                "title": "Company Structure"
            }
        )
        assert tool.params.get("data") == data
        assert tool.params.get("title") == "Company Structure"
        assert tool.tool_name == "generate_organization_chart"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        data = {"name": "Root", "children": []}
        tool = GenerateOrganizationChart(
            prompt="Test Org Chart",
            params={
                "data": data,
                "title": "Test Org Chart"
            }
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_missing_name(self):
        """Test validation with missing name field"""
        data = {"children": []}
        tool = GenerateOrganizationChart(
            prompt="Test",
            params={
                "data": data,
                "title": "Test"
            }
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()
