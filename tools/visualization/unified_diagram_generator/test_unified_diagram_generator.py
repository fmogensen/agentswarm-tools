"""
Tests for UnifiedDiagramGenerator
"""

import os
import pytest

# Set mock mode before importing
os.environ["USE_MOCK_APIS"] = "true"

from tools.visualization.unified_diagram_generator import UnifiedDiagramGenerator
from shared.errors import ValidationError


class TestUnifiedDiagramGenerator:
    """Test suite for UnifiedDiagramGenerator."""

    def test_fishbone_diagram(self):
        """Test fishbone diagram generation."""
        tool = UnifiedDiagramGenerator(
            diagram_type="fishbone",
            data={
                "effect": "Customer Complaints",
                "causes": {
                    "Methods": ["Poor training", "Inconsistent process"],
                    "Materials": ["Low quality"],
                },
            },
            title="Root Cause Analysis",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["diagram_type"] == "fishbone"

    def test_flow_diagram(self):
        """Test flow diagram generation."""
        tool = UnifiedDiagramGenerator(
            diagram_type="flow",
            data={
                "nodes": [
                    {"id": "1", "label": "Start"},
                    {"id": "2", "label": "Process"},
                    {"id": "3", "label": "End"},
                ],
                "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}],
            },
            title="Process Flow",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["diagram_type"] == "flow"

    def test_mindmap(self):
        """Test mind map generation."""
        tool = UnifiedDiagramGenerator(
            diagram_type="mindmap",
            data={
                "root": {
                    "name": "Central Idea",
                    "children": [{"name": "Branch 1"}, {"name": "Branch 2"}],
                }
            },
            title="Project Planning",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["diagram_type"] == "mindmap"

    def test_org_chart(self):
        """Test organization chart generation."""
        tool = UnifiedDiagramGenerator(
            diagram_type="org_chart",
            data=[
                {"id": "ceo", "name": "CEO"},
                {"id": "cto", "name": "CTO", "parent": "ceo"},
                {"id": "cfo", "name": "CFO", "parent": "ceo"},
            ],
            title="Company Structure",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["diagram_type"] == "org_chart"

    def test_invalid_diagram_type(self):
        """Test invalid diagram type raises error."""
        with pytest.raises(ValidationError):
            tool = UnifiedDiagramGenerator(diagram_type="invalid", data={})
            tool.run()

    def test_custom_dimensions(self):
        """Test custom width and height."""
        tool = UnifiedDiagramGenerator(
            diagram_type="org_chart", data=[{"id": "root", "name": "Root"}], width=1600, height=1000
        )
        result = tool.run()

        assert result["success"] == True

    def test_options_passed_through(self):
        """Test that options are passed to renderer."""
        tool = UnifiedDiagramGenerator(
            diagram_type="flow",
            data={"nodes": [{"id": "1", "label": "Start"}], "edges": []},
            options={"orientation": "LR"},
        )
        result = tool.run()

        assert result["success"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
