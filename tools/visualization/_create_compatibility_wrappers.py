"""
Script to create backward compatibility wrappers for deprecated chart tools.
Run this to update all old chart tools to delegate to UnifiedChartGenerator or UnifiedDiagramGenerator.
"""

from shared.logging import get_logger

logger = get_logger(__name__)

CHART_TOOL_MAPPINGS = {
    # Chart tools -> UnifiedChartGenerator
    "generate_bar_chart": {
        "chart_type": "bar",
        "unified_class": "UnifiedChartGenerator",
        "unified_import": "tools.visualization.unified_chart_generator",
    },
    "generate_column_chart": {
        "chart_type": "column",
        "unified_class": "UnifiedChartGenerator",
        "unified_import": "tools.visualization.unified_chart_generator",
    },
    "generate_pie_chart": {
        "chart_type": "pie",
        "unified_class": "UnifiedChartGenerator",
        "unified_import": "tools.visualization.unified_chart_generator",
    },
    "generate_scatter_chart": {
        "chart_type": "scatter",
        "unified_class": "UnifiedChartGenerator",
        "unified_import": "tools.visualization.unified_chart_generator",
    },
    "generate_area_chart": {
        "chart_type": "area",
        "unified_class": "UnifiedChartGenerator",
        "unified_import": "tools.visualization.unified_chart_generator",
    },
    "generate_histogram_chart": {
        "chart_type": "histogram",
        "unified_class": "UnifiedChartGenerator",
        "unified_import": "tools.visualization.unified_chart_generator",
    },
    "generate_dual_axes_chart": {
        "chart_type": "dual_axes",
        "unified_class": "UnifiedChartGenerator",
        "unified_import": "tools.visualization.unified_chart_generator",
    },
    "generate_radar_chart": {
        "chart_type": "radar",
        "unified_class": "UnifiedChartGenerator",
        "unified_import": "tools.visualization.unified_chart_generator",
    },
    # Diagram tools -> UnifiedDiagramGenerator
    "generate_fishbone_diagram": {
        "chart_type": "fishbone",
        "unified_class": "UnifiedDiagramGenerator",
        "unified_import": "tools.visualization.unified_diagram_generator",
    },
    "generate_flow_diagram": {
        "chart_type": "flow",
        "unified_class": "UnifiedDiagramGenerator",
        "unified_import": "tools.visualization.unified_diagram_generator",
    },
    "generate_mind_map": {
        "chart_type": "mindmap",
        "unified_class": "UnifiedDiagramGenerator",
        "unified_import": "tools.visualization.unified_diagram_generator",
    },
    "generate_organization_chart": {
        "chart_type": "org_chart",
        "unified_class": "UnifiedDiagramGenerator",
        "unified_import": "tools.visualization.unified_diagram_generator",
    },
}

WRAPPER_TEMPLATE_CHART = '''"""
{description}

DEPRECATED: This tool is now a compatibility wrapper.
Use {unified_class} with {param_type}="{chart_type}" instead.
"""

from typing import Any, Dict
from pydantic import Field
import os
import warnings

from shared.base import BaseTool


class {class_name}(BaseTool):
    """
    {description}

    DEPRECATED: Use {unified_class} with {param_type}="{chart_type}" instead.
    This wrapper will be removed in a future version.
    """

    tool_name: str = "{tool_name}"
    tool_category: str = "visualization"

    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """Delegates to {unified_class}."""
        warnings.warn(
            "{class_name} is deprecated and will be removed in v3.0.0. "
            "Use {unified_class} with {param_type}='{chart_type}' instead. "
            "See tools/visualization/MIGRATION_GUIDE.md for migration examples.",
            DeprecationWarning,
            stacklevel=2
        )

        from {unified_import} import {unified_class}

        data = self.params.get("data")
        title = self.params.get("title", self.prompt)
        width = self.params.get("width", {default_width})
        height = self.params.get("height", {default_height})

        options = {{k: v for k, v in self.params.items() if k not in ["data", "title", "width", "height"]}}

        unified_tool = {unified_class}(
            {param_type}="{chart_type}",
            data=data,
            title=title,
            width=width,
            height=height,
            options=options
        )

        result = unified_tool._execute()

        if "metadata" in result:
            result["metadata"]["tool_name"] = self.tool_name
            result["metadata"]["deprecated"] = True
            result["metadata"]["prompt"] = self.prompt

        return result

    def _validate_parameters(self) -> None:
        """Validation is handled by {unified_class}."""
        pass

    def _should_use_mock(self) -> bool:
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        return {{
            "success": True,
            "result": {{"mock": True}},
            "metadata": {{"mock_mode": True, "tool_name": self.tool_name}},
        }}

    def _process(self) -> Any:
        pass


if __name__ == "__main__":
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = {class_name}(prompt="Test", params={{"data": []}})
    result = tool.run()
    print(f"Success: {{result.get('success')}}")
'''


def to_class_name(tool_name):
    """Convert snake_case to CamelCase."""
    return "".join(word.capitalize() for word in tool_name.split("_"))


def get_description(tool_name, chart_type):
    """Generate tool description."""
    descriptions = {
        "line": "Generate line chart for trends over time",
        "bar": "Generate bar chart for horizontal categorical comparisons",
        "column": "Generate column chart for vertical categorical comparisons",
        "pie": "Generate pie chart for proportions and parts of whole",
        "scatter": "Generate scatter chart for correlations and relationships",
        "area": "Generate area chart for cumulative trends",
        "histogram": "Generate histogram for distribution of values",
        "dual_axes": "Generate dual-axes chart for two metrics on different scales",
        "radar": "Generate radar chart for multi-dimensional comparisons",
        "fishbone": "Generate fishbone diagram for cause-effect analysis",
        "flow": "Generate flow diagram for process visualization",
        "mindmap": "Generate mind map for hierarchical idea organization",
        "org_chart": "Generate organization chart for hierarchical structure",
    }
    return descriptions.get(chart_type, f"Generate {chart_type} visualization")


logger.info("Backward Compatibility Wrapper Mappings:")
logger.info("=" * 80)
for tool_name, config in CHART_TOOL_MAPPINGS.items():
    class_name = to_class_name(tool_name)
    chart_type = config["chart_type"]
    unified_class = config["unified_class"]
    unified_import = config["unified_import"]

    param_type = "diagram_type" if "Diagram" in unified_class else "chart_type"
    default_width = 1200 if "Diagram" in unified_class else 800
    default_height = 800 if "Diagram" in unified_class else 600

    description = get_description(tool_name, chart_type)

    logger.info(f"\n{tool_name}:")
    logger.info(f"  Class: {class_name}")
    logger.info(f"  Delegates to: {unified_class}({param_type}='{chart_type}')")
    logger.info(f"  Import: from {unified_import} import {unified_class}")

logger.info("\n" + "=" * 80)
logger.info("\nTo apply wrappers, manually update each tool file using the template above.")
logger.info("The template is available in WRAPPER_TEMPLATE_CHART variable.")
