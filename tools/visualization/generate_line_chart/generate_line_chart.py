"""
Generate line chart for trends over time

DEPRECATED: This tool is now a compatibility wrapper.
Use UnifiedChartGenerator with chart_type="line" instead.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import warnings

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateLineChart(BaseTool):
    """
    Generate line chart for trends over time

    DEPRECATED: Use UnifiedChartGenerator with chart_type="line" instead.
    This wrapper will be removed in a future version.

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateLineChart(prompt="example", params={"data": [1,2,3]})
        >>> result = tool.run()
    """

    tool_name: str = "generate_line_chart"
    tool_category: str = "visualization"

    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_line_chart tool.

        Delegates to UnifiedChartGenerator for actual implementation.

        Returns:
            Dict with results
        """
        # Emit deprecation warning
        warnings.warn(
            "GenerateLineChart is deprecated and will be removed in v3.0.0. "
            "Use UnifiedChartGenerator with chart_type='line' instead. "
            "See tools/visualization/MIGRATION_GUIDE.md for migration examples.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Import here to avoid circular dependency
        from tools.visualization.unified_chart_generator import UnifiedChartGenerator

        # Extract parameters
        data = self.params.get("data")
        title = self.params.get("title", self.prompt)
        width = self.params.get("width", 800)
        height = self.params.get("height", 600)

        # Build options from params
        options = {
            "labels": self.params.get("labels"),
            "x_label": self.params.get("x_label", "Time"),
            "y_label": self.params.get("y_label", "Value"),
            "grid": self.params.get("grid", True),
        }

        # Remove None values
        options = {k: v for k, v in options.items() if v is not None}

        # Delegate to UnifiedChartGenerator
        unified_tool = UnifiedChartGenerator(
            chart_type="line", data=data, title=title, width=width, height=height, options=options
        )

        # Run the unified tool
        result = unified_tool._execute()

        # Adjust metadata to maintain backward compatibility
        if "metadata" in result:
            result["metadata"]["tool_name"] = self.tool_name
            result["metadata"]["deprecated"] = True
            result["metadata"]["prompt"] = self.prompt

        return result

    def _validate_parameters(self) -> None:
        """Validation is handled by UnifiedChartGenerator."""
        pass

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB"
        return {
            "success": True,
            "result": {"image_base64": mock_image, "mock": True},
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """Not used - delegated to UnifiedChartGenerator."""
        pass


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateLineChart(prompt="Sales trend", params={"data": [1, 2, 3, 4, 5]})
    result = tool.run()
    print(f"Success: {result.get('success')}")
