"""
Chart renderers for standard chart types.
Consolidates rendering logic for line, bar, pie, scatter, area, column, histogram, dual_axes, and radar charts.
"""

from typing import Any, Dict, List, Optional, Union
import matplotlib.pyplot as plt
import numpy as np
from .base_renderer import BaseRenderer
from shared.errors import ValidationError


class LineChartRenderer(BaseRenderer):
    """Renderer for line charts (trends over time)."""

    def validate_data(self, data: Any) -> None:
        """Validate line chart data format."""
        if not isinstance(data, list) or len(data) == 0:
            raise ValidationError("Line chart data must be a non-empty list")

        first_item = data[0]
        if isinstance(first_item, dict):
            if not all(isinstance(item, dict) and "x" in item and "y" in item for item in data):
                raise ValidationError("Line chart data items must have 'x' and 'y' keys")
        elif not all(isinstance(x, (int, float)) for x in data):
            raise ValidationError("Line chart data must be numbers or {x, y} objects")

    def render(
        self,
        data: List[Union[float, Dict[str, Any]]],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render line chart."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            # Parse data format
            if isinstance(data[0], dict):
                x_vals = [item["x"] for item in data]
                y_vals = [item["y"] for item in data]
            else:
                x_vals = list(range(len(data)))
                y_vals = data

            fig, ax = self.create_figure(width, height)
            ax.plot(x_vals, y_vals, marker="o")

            labels = opts.get("labels")
            if labels:
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels)

            ax.set_title(title or "Line Chart")
            ax.set_xlabel(opts.get("x_label", "X"))
            ax.set_ylabel(opts.get("y_label", "Y"))
            ax.grid(opts.get("grid", True), alpha=0.3)

            return fig

        return self.safe_render(_render, data, title, width, height, options)


class BarChartRenderer(BaseRenderer):
    """Renderer for horizontal bar charts."""

    def validate_data(self, data: Any) -> None:
        """Validate bar chart data format."""
        if isinstance(data, dict):
            if len(data) == 0:
                raise ValidationError("Bar chart data cannot be empty")
            if not all(isinstance(v, (int, float)) for v in data.values()):
                raise ValidationError("Bar chart values must be numeric")
        elif isinstance(data, list):
            if len(data) == 0:
                raise ValidationError("Bar chart data cannot be empty")
            if not all(
                isinstance(item, dict) and "label" in item and "value" in item for item in data
            ):
                raise ValidationError("Bar chart items must have 'label' and 'value'")
        else:
            raise ValidationError("Bar chart data must be dict or list of {label, value}")

    def render(
        self,
        data: Union[Dict[str, float], List[Dict[str, Any]]],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render bar chart."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            # Normalize data format
            if isinstance(data, list):
                categories = [item["label"] for item in data]
                values = [item["value"] for item in data]
            else:
                categories = list(data.keys())
                values = list(data.values())

            fig, ax = self.create_figure(width, height)
            ax.barh(categories, values, color=opts.get("color", "#4285F4"))

            ax.set_xlabel(opts.get("x_label", "Value"))
            ax.set_ylabel(opts.get("y_label", "Category"))
            ax.set_title(title or "Bar Chart")

            return fig

        return self.safe_render(_render, data, title, width, height, options)


class ColumnChartRenderer(BaseRenderer):
    """Renderer for vertical column charts."""

    def validate_data(self, data: Any) -> None:
        """Validate column chart data format."""
        # Same as bar chart
        BarChartRenderer().validate_data(data)

    def render(
        self,
        data: Union[Dict[str, float], List[Dict[str, Any]]],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render column chart."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            # Normalize data format
            if isinstance(data, list):
                categories = [item["label"] for item in data]
                values = [item["value"] for item in data]
            else:
                categories = list(data.keys())
                values = list(data.values())

            fig, ax = self.create_figure(width, height)
            ax.bar(categories, values, color=opts.get("color", "#4285F4"))

            ax.set_xlabel(opts.get("x_label", "Category"))
            ax.set_ylabel(opts.get("y_label", "Value"))
            ax.set_title(title or "Column Chart")
            plt.xticks(rotation=opts.get("rotation", 45), ha="right")

            return fig

        return self.safe_render(_render, data, title, width, height, options)


class PieChartRenderer(BaseRenderer):
    """Renderer for pie charts."""

    def validate_data(self, data: Any) -> None:
        """Validate pie chart data format."""
        if isinstance(data, dict):
            if "labels" not in data or "values" not in data:
                raise ValidationError("Pie chart data dict must have 'labels' and 'values'")
            if len(data["labels"]) != len(data["values"]):
                raise ValidationError("Pie chart labels and values must have same length")
        elif isinstance(data, list):
            if len(data) == 0:
                raise ValidationError("Pie chart data cannot be empty")
            if not all(
                isinstance(item, dict) and "label" in item and "value" in item for item in data
            ):
                raise ValidationError("Pie chart items must have 'label' and 'value'")
        else:
            raise ValidationError("Pie chart data must be dict or list")

    def render(
        self,
        data: Union[Dict[str, List], List[Dict[str, Any]]],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render pie chart."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            # Normalize data format
            if isinstance(data, list):
                labels = [item["label"] for item in data]
                values = [item["value"] for item in data]
            else:
                labels = data["labels"]
                values = data["values"]

            fig, ax = self.create_figure(width, height)
            ax.pie(
                values,
                labels=labels,
                autopct=opts.get("autopct", "%1.1f%%"),
                colors=opts.get("colors"),
                startangle=opts.get("startangle", 90),
            )
            ax.set_title(title or "Pie Chart")

            return fig

        return self.safe_render(_render, data, title, width, height, options)


class ScatterChartRenderer(BaseRenderer):
    """Renderer for scatter charts."""

    def validate_data(self, data: Any) -> None:
        """Validate scatter chart data format."""
        if isinstance(data, dict):
            if "x" not in data or "y" not in data:
                raise ValidationError("Scatter chart data dict must have 'x' and 'y'")
            if len(data["x"]) != len(data["y"]):
                raise ValidationError("Scatter chart x and y must have same length")
        elif isinstance(data, list):
            if not all(isinstance(item, dict) and "x" in item and "y" in item for item in data):
                raise ValidationError("Scatter chart items must have 'x' and 'y'")
        else:
            raise ValidationError("Scatter chart data must be dict or list")

    def render(
        self,
        data: Union[Dict[str, List], List[Dict[str, Any]]],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render scatter chart."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            # Normalize data format
            if isinstance(data, list):
                x_vals = [item["x"] for item in data]
                y_vals = [item["y"] for item in data]
            else:
                x_vals = data["x"]
                y_vals = data["y"]

            fig, ax = self.create_figure(width, height)
            ax.scatter(
                x_vals,
                y_vals,
                c=opts.get("color", "#4285F4"),
                s=opts.get("size", 50),
                alpha=opts.get("alpha", 0.6),
            )

            ax.set_xlabel(opts.get("x_label", "X"))
            ax.set_ylabel(opts.get("y_label", "Y"))
            ax.set_title(title or "Scatter Chart")
            ax.grid(opts.get("grid", True), alpha=0.3)

            return fig

        return self.safe_render(_render, data, title, width, height, options)


class AreaChartRenderer(BaseRenderer):
    """Renderer for area charts."""

    def validate_data(self, data: Any) -> None:
        """Validate area chart data format."""
        LineChartRenderer().validate_data(data)  # Same as line chart

    def render(
        self,
        data: List[Union[float, Dict[str, Any]]],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render area chart."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            # Parse data format
            if isinstance(data[0], dict):
                x_vals = [item["x"] for item in data]
                y_vals = [item["y"] for item in data]
            else:
                x_vals = list(range(len(data)))
                y_vals = data

            fig, ax = self.create_figure(width, height)
            ax.fill_between(
                x_vals, y_vals, alpha=opts.get("alpha", 0.3), color=opts.get("color", "#4285F4")
            )
            ax.plot(x_vals, y_vals, color=opts.get("line_color", "#4285F4"))

            labels = opts.get("labels")
            if labels:
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels)

            ax.set_title(title or "Area Chart")
            ax.set_xlabel(opts.get("x_label", "X"))
            ax.set_ylabel(opts.get("y_label", "Y"))
            ax.grid(opts.get("grid", True), alpha=0.3)

            return fig

        return self.safe_render(_render, data, title, width, height, options)


class HistogramRenderer(BaseRenderer):
    """Renderer for histograms."""

    def validate_data(self, data: Any) -> None:
        """Validate histogram data format."""
        if not isinstance(data, list) or len(data) == 0:
            raise ValidationError("Histogram data must be a non-empty list")
        if not all(isinstance(x, (int, float)) for x in data):
            raise ValidationError("Histogram data must contain only numbers")

    def render(
        self,
        data: List[float],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render histogram."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            fig, ax = self.create_figure(width, height)

            bins = opts.get("bins", "auto")
            ax.hist(
                data,
                bins=bins,
                color=opts.get("color", "#4285F4"),
                alpha=opts.get("alpha", 0.7),
                edgecolor="black",
            )

            ax.set_xlabel(opts.get("x_label", "Value"))
            ax.set_ylabel(opts.get("y_label", "Frequency"))
            ax.set_title(title or "Histogram")
            ax.grid(opts.get("grid", True), alpha=0.3, axis="y")

            return fig

        return self.safe_render(_render, data, title, width, height, options)


class DualAxesChartRenderer(BaseRenderer):
    """Renderer for dual-axes charts."""

    def validate_data(self, data: Any) -> None:
        """Validate dual axes chart data format."""
        if not isinstance(data, dict):
            raise ValidationError("Dual axes data must be a dict")
        if "primary" not in data or "secondary" not in data:
            raise ValidationError("Dual axes data must have 'primary' and 'secondary'")
        if len(data["primary"]) != len(data["secondary"]):
            raise ValidationError("Primary and secondary data must have same length")

    def render(
        self,
        data: Dict[str, List],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render dual axes chart."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            primary_data = data["primary"]
            secondary_data = data["secondary"]
            x_vals = opts.get("x_values", list(range(len(primary_data))))

            fig, ax1 = self.create_figure(width, height)

            # Primary axis
            color1 = opts.get("primary_color", "#4285F4")
            ax1.set_xlabel(opts.get("x_label", "X"))
            ax1.set_ylabel(opts.get("primary_label", "Primary"), color=color1)
            ax1.plot(x_vals, primary_data, color=color1, marker="o")
            ax1.tick_params(axis="y", labelcolor=color1)

            # Secondary axis
            ax2 = ax1.twinx()
            color2 = opts.get("secondary_color", "#DB4437")
            ax2.set_ylabel(opts.get("secondary_label", "Secondary"), color=color2)
            ax2.plot(x_vals, secondary_data, color=color2, marker="s")
            ax2.tick_params(axis="y", labelcolor=color2)

            ax1.set_title(title or "Dual Axes Chart")
            fig.tight_layout()

            return fig

        return self.safe_render(_render, data, title, width, height, options)


class RadarChartRenderer(BaseRenderer):
    """Renderer for radar charts."""

    def validate_data(self, data: Any) -> None:
        """Validate radar chart data format."""
        if isinstance(data, dict):
            if "categories" not in data or "values" not in data:
                raise ValidationError("Radar chart data must have 'categories' and 'values'")
            if len(data["categories"]) != len(data["values"]):
                raise ValidationError("Categories and values must have same length")
        else:
            raise ValidationError("Radar chart data must be a dict")

    def render(
        self,
        data: Dict[str, List],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render radar chart."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            categories = data["categories"]
            values = data["values"]

            # Number of variables
            num_vars = len(categories)

            # Compute angle for each axis
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            values = values + [values[0]]  # Complete the circle
            angles += angles[:1]

            fig, ax = self.create_figure(width, height)
            ax = plt.subplot(111, projection="polar")

            ax.plot(angles, values, "o-", linewidth=2, color=opts.get("color", "#4285F4"))
            ax.fill(
                angles, values, alpha=opts.get("alpha", 0.25), color=opts.get("color", "#4285F4")
            )
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_title(title or "Radar Chart", pad=20)
            ax.grid(True)

            return fig

        return self.safe_render(_render, data, title, width, height, options)


# Renderer registry
CHART_RENDERERS = {
    "line": LineChartRenderer(),
    "bar": BarChartRenderer(),
    "column": ColumnChartRenderer(),
    "pie": PieChartRenderer(),
    "scatter": ScatterChartRenderer(),
    "area": AreaChartRenderer(),
    "histogram": HistogramRenderer(),
    "dual_axes": DualAxesChartRenderer(),
    "radar": RadarChartRenderer(),
}
