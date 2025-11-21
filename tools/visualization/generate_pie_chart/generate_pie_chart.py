"""
Generate pie chart for proportions and parts of whole
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import json
from io import BytesIO
import base64
import matplotlib.pyplot as plt

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GeneratePieChart(BaseTool):
    """
    Generate pie chart for proportions and parts of whole

    Args:
        prompt: Description of what to generate (must describe labels and values)
        params: Additional generation parameters (e.g., title, colors)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Dict with base64 image data
        - metadata: Additional information

    Example:
        >>> tool = GeneratePieChart(prompt="example", params={"title":"My chart"})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_pie_chart"
    tool_category: str = "visualization"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default={}, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_pie_chart tool.

        Returns:
            Dict with results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "prompt": self.prompt,
                    "params": self.params,
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if (
            not self.prompt
            or not isinstance(self.prompt, str)
            or not self.prompt.strip()
        ):
            raise ValidationError(
                "prompt must be a non-empty string",
                tool_name=self.tool_name,
                field="prompt"
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "params must be an object (dict)",
                tool_name=self.tool_name,
                field="params"
            )

        # Must include labels and values
        labels = self.params.get("labels")
        values = self.params.get("values")

        if labels is None or values is None:
            raise ValidationError(
                "params must include 'labels' and 'values'",
                tool_name=self.tool_name,
                field="params"
            )

        if not isinstance(labels, list) or not isinstance(values, list):
            raise ValidationError(
                "'labels' and 'values' must be lists",
                tool_name=self.tool_name,
                field="labels/values"
            )

        if len(labels) != len(values):
            raise ValidationError(
                "'labels' and 'values' must have the same length",
                tool_name=self.tool_name,
                field="labels/values"
            )

        if not all(isinstance(x, (int, float)) for x in values):
            raise ValidationError(
                "All values must be numeric",
                tool_name=self.tool_name,
                field="values"
            )

        if sum(values) <= 0:
            raise ValidationError(
                "Sum of values must be greater than zero",
                tool_name=self.tool_name,
                field="values"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {"mock": True, "image_base64": "MOCK_IMAGE_DATA"},
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        labels = self.params["labels"]
        values = self.params["values"]
        title = self.params.get("title", "Pie Chart")
        colors = self.params.get("colors")

        try:
            fig, ax = plt.subplots()
            ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors)
            ax.set_title(title)

            buffer = BytesIO()
            plt.savefig(buffer, format="png", bbox_inches="tight")
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode("utf-8")
            plt.close(fig)

            return {
                "image_base64": encoded,
                "labels": labels,
                "values": values,
                "title": title,
            }
        except Exception as e:
            raise APIError(
                f"Pie chart generation failed: {e}", tool_name=self.tool_name
            )
