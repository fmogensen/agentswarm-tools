"""
Generate area chart for trends under continuous variables
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateAreaChart(BaseTool):
    """
    Generate area chart for trends under continuous variables

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateAreaChart(prompt="example", params={"x":[1,2], "y":[3,4]})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_area_chart"
    tool_category: str = "visualization"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_area_chart tool.

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
                "metadata": {
                    "tool_name": self.tool_name,
                    "prompt": self.prompt,
                    "params": self.params,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: For invalid inputs
        """
        if not isinstance(self.prompt, str) or not self.prompt.strip():
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

        # Expected keys: x and y arrays for area chart
        if "x" not in self.params or "y" not in self.params:
            raise ValidationError(
                "Params must include 'x' and 'y' arrays",
                tool_name=self.tool_name,
                field="params",
            )

        x = self.params.get("x")
        y = self.params.get("y")

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
                field="x/y",
            )

        if len(x) == 0:
            raise ValidationError(
                "'x' and 'y' must not be empty", tool_name=self.tool_name
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_chart = {
            "chart_type": "area",
            "x": self.params.get("x", [1, 2, 3]),
            "y": self.params.get("y", [3, 6, 9]),
            "mock": True,
        }
        return {
            "success": True,
            "result": mock_chart,
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Returns:
            Dict containing chart data
        """
        try:
            x = self.params["x"]
            y = self.params["y"]

            chart_data = {
                "chart_type": "area",
                "description": self.prompt,
                "x": x,
                "y": y,
                "points": [{"x": xv, "y": yv} for xv, yv in zip(x, y)],
            }

            return chart_data

        except Exception as e:
            raise APIError(
                f"Error generating area chart: {e}", tool_name=self.tool_name
            )
