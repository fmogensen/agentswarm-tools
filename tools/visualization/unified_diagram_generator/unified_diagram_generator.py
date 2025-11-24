"""
Unified Diagram Generator - Consolidates 4 specialized diagram types into a single tool.

Replaces:
- generate_fishbone_diagram
- generate_flow_diagram
- generate_mind_map
- generate_organization_chart
"""

import os
from typing import Any, Dict, Literal

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError
from tools.visualization.renderers import DIAGRAM_RENDERERS

DiagramType = Literal["fishbone", "flow", "mindmap", "org_chart"]


class UnifiedDiagramGenerator(BaseTool):
    """
    Generate diagrams (fishbone, flow, mind maps, org charts).

    Consolidates 4 specialized diagram types into a single unified interface:
    - fishbone: Cause-effect analysis (Ishikawa diagrams)
    - flow: Process flow and workflow diagrams
    - mindmap: Hierarchical idea organization
    - org_chart: Organizational structure visualization

    Args:
        diagram_type: Type of diagram to generate
        data: Diagram structure (format varies by diagram type)
        title: Diagram title
        width: Diagram width in pixels
        height: Diagram height in pixels
        options: Additional diagram options (orientation, layout, etc.)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Diagram data/image and metadata
        - metadata: Tool information

    Example:
        >>> # Fishbone diagram
        >>> tool = UnifiedDiagramGenerator(
        ...     diagram_type="fishbone",
        ...     data={
        ...         "effect": "Customer Complaints",
        ...         "causes": {
        ...             "Methods": ["Cause A", "Cause B"],
        ...             "Materials": ["Cause C", "Cause D"]
        ...         }
        ...     },
        ...     title="Root Cause Analysis"
        ... )
        >>> result = tool.run()
        >>>
        >>> # Organization chart
        >>> tool = UnifiedDiagramGenerator(
        ...     diagram_type="org_chart",
        ...     data=[
        ...         {"id": "ceo", "name": "CEO"},
        ...         {"id": "cto", "name": "CTO", "parent": "ceo"}
        ...     ],
        ...     title="Company Structure"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "unified_diagram_generator"
    tool_category: str = "visualization"

    # Parameters
    diagram_type: DiagramType = Field(
        ..., description="Type of diagram to generate (fishbone, flow, mindmap, org_chart)"
    )

    data: Any = Field(
        ..., description="Diagram structure (format varies by diagram type - see documentation)"
    )

    title: str = Field("", description="Diagram title")

    width: int = Field(1200, description="Diagram width in pixels", ge=400, le=4000)

    height: int = Field(800, description="Diagram height in pixels", ge=300, le=3000)

    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional diagram options (orientation, layout, node_template, etc.)",
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the unified diagram generator.

        Returns:
            Dict with diagram data/image and metadata
        """

        self._logger.info(
            f"Executing {self.tool_name} with title={self.title}, width={self.width}, height={self.height}, options={self.options}"
        )
        self._validate_parameters()

        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "diagram_type": self.diagram_type,
                    "title": self.title,
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if self.diagram_type not in DIAGRAM_RENDERERS:
            raise ValidationError(
                f"Invalid diagram_type: {self.diagram_type}. Must be one of: {list(DIAGRAM_RENDERERS.keys())}",
                tool_name=self.tool_name,
                field="diagram_type",
            )

        if not isinstance(self.options, dict):
            raise ValidationError(
                "Options must be a dictionary", tool_name=self.tool_name, field="options"
            )

        # Validate data using renderer's validation
        renderer = DIAGRAM_RENDERERS[self.diagram_type]
        try:
            renderer.validate_data(self.data)
        except ValidationError as e:
            # Re-raise with tool context
            raise ValidationError(
                f"Invalid data for {self.diagram_type} diagram: {e.message}",
                tool_name=self.tool_name,
                field="data",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_diagrams = {
            "fishbone": {
                "effect": "Mock Problem",
                "causes": {
                    "Category 1": ["Cause A", "Cause B"],
                    "Category 2": ["Cause C", "Cause D"],
                },
            },
            "flow": {
                "nodes": [
                    {"id": "1", "label": "Start"},
                    {"id": "2", "label": "Process"},
                    {"id": "3", "label": "End"},
                ],
                "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}],
            },
            "mindmap": {
                "root": {
                    "name": "Central Idea",
                    "children": [{"name": "Branch 1"}, {"name": "Branch 2"}],
                }
            },
            "org_chart": [
                {"id": "ceo", "name": "CEO"},
                {"id": "cto", "name": "CTO", "parent": "ceo"},
                {"id": "cfo", "name": "CFO", "parent": "ceo"},
            ],
        }

        return {
            "success": True,
            "result": {
                "diagram_type": self.diagram_type,
                "data": mock_diagrams.get(self.diagram_type, {}),
                "title": self.title
                or f"Mock {self.diagram_type.replace('_', ' ').title()} Diagram",
                "width": self.width,
                "height": self.height,
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic.

        Uses the appropriate renderer for the diagram type.
        """
        renderer = DIAGRAM_RENDERERS[self.diagram_type]

        try:
            result = renderer.render(
                data=self.data,
                title=self.title,
                width=self.width,
                height=self.height,
                options=self.options,
            )

            # Add diagram type to result
            if isinstance(result, dict):
                result["diagram_type"] = self.diagram_type
            else:
                result = {"diagram_type": self.diagram_type, "data": result}

            return result

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(
                f"{self.diagram_type.replace('_', ' ').title()} diagram generation failed: {e}",
                tool_name=self.tool_name,
            )


if __name__ == "__main__":
    print("Testing UnifiedDiagramGenerator...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test fishbone diagram
    tool = UnifiedDiagramGenerator(
        diagram_type="fishbone",
        data={
            "effect": "Customer Complaints Increase",
            "causes": {
                "Methods": ["Poor training", "Inconsistent process"],
                "Materials": ["Low quality", "Supply issues"],
            },
        },
        title="Root Cause Analysis",
    )
    result = tool.run()
    print(f"Fishbone - Success: {result.get('success')}")
    assert result.get("success") == True

    # Test org chart
    tool = UnifiedDiagramGenerator(
        diagram_type="org_chart",
        data=[
            {"id": "ceo", "name": "CEO", "title": "Chief Executive Officer"},
            {"id": "cto", "name": "CTO", "title": "Chief Technology Officer", "parent": "ceo"},
            {"id": "cfo", "name": "CFO", "title": "Chief Financial Officer", "parent": "ceo"},
        ],
        title="Company Organization",
    )
    result = tool.run()
    print(f"Org Chart - Success: {result.get('success')}")
    assert result.get("success") == True

    # Test flow diagram
    tool = UnifiedDiagramGenerator(
        diagram_type="flow",
        data={
            "nodes": [
                {"id": "start", "label": "Start", "type": "start"},
                {"id": "process1", "label": "Process Data", "type": "process"},
                {"id": "decision", "label": "Valid?", "type": "decision"},
                {"id": "end", "label": "End", "type": "end"},
            ],
            "edges": [
                {"source": "start", "target": "process1"},
                {"source": "process1", "target": "decision"},
                {"source": "decision", "target": "end", "label": "Yes"},
            ],
        },
        title="Data Processing Flow",
    )
    result = tool.run()
    print(f"Flow - Success: {result.get('success')}")
    assert result.get("success") == True

    print("\nAll tests passed!")
