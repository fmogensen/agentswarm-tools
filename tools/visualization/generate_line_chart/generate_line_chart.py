"""
Generate line chart for trends over time
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import base64
import io
import matplotlib.pyplot as plt

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateLineChart(BaseTool):
    """
    Generate line chart for trends over time

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

        Returns:
            Dict with results
        """
        self._validate_parameters()

        if self._should_use_mock():
            return self._generate_mock_results()

        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "prompt": self.prompt},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.prompt or not isinstance(self.prompt, str):
            raise ValidationError(
                "Prompt must be a non-empty string",
                tool_name=self.tool_name,
                field="prompt"
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be a dictionary",
                tool_name=self.tool_name,
                field="params"
            )

        data = self.params.get("data")
        if data is None or not isinstance(data, list):
            raise ValidationError(
                "Params must include 'data' as a list",
                tool_name=self.tool_name,
                field="data"
            )

        if len(data) == 0:
            raise ValidationError(
                "'data' must not be empty",
                tool_name=self.tool_name,
                field="data"
            )

        # Accept either list of numbers OR list of {x, y} objects
        first_item = data[0]
        if isinstance(first_item, dict):
            # Validate list of {x, y} objects
            if not all(isinstance(item, dict) and "x" in item and "y" in item for item in data):
                raise ValidationError(
                    "When 'data' contains objects, each must have 'x' and 'y' keys",
                    tool_name=self.tool_name,
                    field="data"
                )
        elif not all(isinstance(x, (int, float)) for x in data):
            raise ValidationError(
                "Params 'data' must be a list of numbers or list of {x, y} objects",
                tool_name=self.tool_name,
                field="data"
            )

        labels = self.params.get("labels")
        if labels is not None and (
            not isinstance(labels, list) or len(labels) != len(data)
        ):
            raise ValidationError(
                "If provided, 'labels' must be a list with same length as 'data'",
                tool_name=self.tool_name,
                field="labels"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB"  # Truncated fake base64
        return {
            "success": True,
            "result": {"image_base64": mock_image, "mock": True},
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        raw_data = self.params.get("data")
        labels = self.params.get("labels")
        title = self.params.get("title", self.prompt)

        # Handle both formats: list of numbers or list of {x, y} objects
        if isinstance(raw_data[0], dict):
            x_vals = [item["x"] for item in raw_data]
            y_vals = [item["y"] for item in raw_data]
        else:
            x_vals = list(range(len(raw_data)))
            y_vals = raw_data

        fig = None
        try:
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, marker="o")

            if labels:
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels)

            ax.set_title(title)
            ax.set_xlabel(self.params.get("x_label", "Time"))
            ax.set_ylabel(self.params.get("y_label", "Value"))

            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)

            encoded = base64.b64encode(buffer.read()).decode("utf-8")

            return {"image_base64": encoded, "data_points": len(raw_data)}

        except Exception as e:
            raise APIError(f"Chart generation failed: {e}", tool_name=self.tool_name)
        finally:
            if fig is not None:
                plt.close(fig)


if __name__ == "__main__":
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateLineChart(prompt="Sales trend", params={"data": [1, 2, 3, 4, 5]})
    result = tool.run()
    print(f"Success: {result.get('success')}")
