"""
Unified Chart Generator - Consolidates 9 common chart types into a single tool.

Replaces:
- generate_line_chart
- generate_bar_chart
- generate_column_chart
- generate_pie_chart
- generate_scatter_chart
- generate_area_chart
- generate_histogram_chart
- generate_dual_axes_chart
- generate_radar_chart
"""

import os
from typing import Any, Dict, Literal

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError
from tools.visualization.renderers import CHART_RENDERERS

ChartType = Literal[
    "line", "bar", "column", "pie", "scatter", "area", "histogram", "dual_axes", "radar"
]


class UnifiedChartGenerator(BaseTool):
    """
    Generate standard charts with multiple chart types.

    Consolidates 9 common chart types into a single unified interface:
    - line: Trends over time
    - bar: Horizontal categorical comparisons
    - column: Vertical categorical comparisons
    - pie: Proportions and parts of whole
    - scatter: Correlations and relationships
    - area: Cumulative trends
    - histogram: Distribution of values
    - dual_axes: Two metrics on different scales
    - radar: Multi-dimensional comparisons

    Args:
        chart_type: Type of chart to generate
        data: Chart data (format varies by chart type)
        title: Chart title
        width: Chart width in pixels
        height: Chart height in pixels
        options: Additional chart options (labels, colors, etc.)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Chart image as base64 and metadata
        - metadata: Tool information

    Example:
        >>> # Line chart
        >>> tool = UnifiedChartGenerator(
        ...     chart_type="line",
        ...     data=[1, 2, 3, 4, 5],
        ...     title="Sales Trend"
        ... )
        >>> result = tool.run()
        >>>
        >>> # Pie chart
        >>> tool = UnifiedChartGenerator(
        ...     chart_type="pie",
        ...     data=[
        ...         {"label": "A", "value": 30},
        ...         {"label": "B", "value": 70}
        ...     ],
        ...     title="Market Share"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "unified_chart_generator"
    tool_category: str = "visualization"

    # Parameters
    chart_type: ChartType = Field(
        ...,
        description="Type of chart to generate (line, bar, column, pie, scatter, area, histogram, dual_axes, radar)",
    )

    data: Any = Field(
        ..., description="Chart data (format varies by chart type - see documentation)"
    )

    title: str = Field("", description="Chart title")

    width: int = Field(800, description="Chart width in pixels", ge=200, le=4000)

    height: int = Field(600, description="Chart height in pixels", ge=200, le=3000)

    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional chart options (x_label, y_label, colors, grid, etc.)",
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the unified chart generator.

        Returns:
            Dict with chart image and metadata
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
                    "chart_type": self.chart_type,
                    "title": self.title,
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if self.chart_type not in CHART_RENDERERS:
            raise ValidationError(
                f"Invalid chart_type: {self.chart_type}. Must be one of: {list(CHART_RENDERERS.keys())}",
                tool_name=self.tool_name,
                field="chart_type",
            )

        if not isinstance(self.options, dict):
            raise ValidationError(
                "Options must be a dictionary", tool_name=self.tool_name, field="options"
            )

        # Validate data using renderer's validation
        renderer = CHART_RENDERERS[self.chart_type]
        try:
            renderer.validate_data(self.data)
        except ValidationError as e:
            # Re-raise with tool context
            raise ValidationError(
                f"Invalid data for {self.chart_type} chart: {e.message}",
                tool_name=self.tool_name,
                field="data",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="

        return {
            "success": True,
            "result": {
                "image_base64": mock_image,
                "chart_type": self.chart_type,
                "title": self.title or f"Mock {self.chart_type.title()} Chart",
                "width": self.width,
                "height": self.height,
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic.

        Uses the appropriate renderer for the chart type.
        """
        renderer = CHART_RENDERERS[self.chart_type]

        try:
            result = renderer.render(
                data=self.data,
                title=self.title,
                width=self.width,
                height=self.height,
                options=self.options,
            )

            result["chart_type"] = self.chart_type
            return result

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(
                f"{self.chart_type.title()} chart generation failed: {e}", tool_name=self.tool_name
            )


if __name__ == "__main__":
    print("Testing UnifiedChartGenerator...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test line chart
    tool = UnifiedChartGenerator(chart_type="line", data=[1, 2, 3, 4, 5], title="Sales Trend")
    result = tool.run()
    print(f"Line Chart - Success: {result.get('success')}")
    assert result.get("success") == True

    # Test pie chart
    tool = UnifiedChartGenerator(
        chart_type="pie",
        data=[
            {"label": "Product A", "value": 40},
            {"label": "Product B", "value": 35},
            {"label": "Product C", "value": 25},
        ],
        title="Market Share",
    )
    result = tool.run()
    print(f"Pie Chart - Success: {result.get('success')}")
    assert result.get("success") == True

    # Test bar chart
    tool = UnifiedChartGenerator(
        chart_type="bar",
        data={"North": 45, "South": 32, "East": 38, "West": 50},
        title="Sales by Region",
    )
    result = tool.run()
    print(f"Bar Chart - Success: {result.get('success')}")
    assert result.get("success") == True

    print("\nAll tests passed!")
