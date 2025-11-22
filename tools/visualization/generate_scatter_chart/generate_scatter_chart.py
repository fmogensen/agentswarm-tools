"""
Generate scatter chart for correlations and relationships
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os
import uuid
import base64
import io
import matplotlib.pyplot as plt

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateScatterChart(BaseTool):
    """
    Generate scatter chart for correlations and relationships

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateScatterChart(prompt="example", params="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_scatter_chart"
    tool_category: str = "visualization"
    tool_description: str = "Generate scatter chart for correlations and relationships"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_scatter_chart tool.

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
        """Validate input parameters.

        Raises:
            ValidationError: If inputs are missing or invalid
        """
        if not self.prompt or not isinstance(self.prompt, str):
            raise ValidationError(
                "Prompt must be a non-empty string",
                tool_name=self.tool_name,
                field="prompt",
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be a dictionary",
                tool_name=self.tool_name,
                field="params",
            )

        # Accept either x/y arrays OR data as list of {x, y} objects
        data = self.params.get("data")
        x = self.params.get("x")
        y = self.params.get("y")

        if data is not None:
            # New format: list of {x, y} objects
            if not isinstance(data, list):
                raise ValidationError(
                    "'data' must be a list",
                    tool_name=self.tool_name,
                    field="data",
                )
            if len(data) == 0:
                raise ValidationError(
                    "'data' must not be empty",
                    tool_name=self.tool_name,
                    field="data",
                )
            if not all(isinstance(item, dict) and "x" in item and "y" in item for item in data):
                raise ValidationError(
                    "When 'data' is provided, each item must have 'x' and 'y' keys",
                    tool_name=self.tool_name,
                    field="data",
                )
        elif x is not None and y is not None:
            # Original format: separate x and y arrays
            if not isinstance(x, list) or not isinstance(y, list):
                raise ValidationError(
                    "'x' and 'y' must be lists",
                    tool_name=self.tool_name,
                    field="x/y",
                )

            if len(x) != len(y):
                raise ValidationError(
                    "'x' and 'y' must be the same length",
                    tool_name=self.tool_name,
                    field="x/y"
                )
        else:
            raise ValidationError(
                "Params must include either 'data' (list of {x, y}) or 'x' and 'y' lists",
                tool_name=self.tool_name,
                field="params",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_id = str(uuid.uuid4())
        return {
            "success": True,
            "result": {
                "chart_id": mock_id,
                "image_base64": "mock_image_data",
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """Main processing logic.

        Returns:
            Dict containing chart ID and Base64 PNG data

        Raises:
            APIError: If chart generation fails
        """
        fig = None
        try:
            # Handle both formats: data list or separate x/y arrays
            data = self.params.get("data")
            if data is not None:
                x = [item["x"] for item in data]
                y = [item["y"] for item in data]
            else:
                x = self.params["x"]
                y = self.params["y"]

            # Create chart
            fig, ax = plt.subplots()
            ax.scatter(x, y)

            title = self.params.get("title", "Scatter Chart")
            ax.set_title(title)

            ax.set_xlabel(self.params.get("x_label", "X"))
            ax.set_ylabel(self.params.get("y_label", "Y"))

            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)

            image_base64 = base64.b64encode(buf.read()).decode("utf-8")

            chart_id = str(uuid.uuid4())

            return {"chart_id": chart_id, "image_base64": image_base64}

        except Exception as e:
            raise APIError(f"Chart generation failed: {e}", tool_name=self.tool_name)
        finally:
            if fig is not None:
                plt.close(fig)
