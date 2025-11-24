"""
Generate area chart for trends under continuous variables
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


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

        self._logger.info(
            f"Executing {self.tool_name} with prompt={self.prompt}, params={self.params}"
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
                    "prompt": self.prompt,
                    "params": self.params,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
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
                    field="x/y",
                )

            if len(x) == 0:
                raise ValidationError("'x' and 'y' must not be empty", tool_name=self.tool_name)
        else:
            raise ValidationError(
                "Params must include either 'data' (list of {x, y}) or 'x' and 'y' arrays",
                tool_name=self.tool_name,
                field="params",
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
            # Handle both formats: data list or separate x/y arrays
            data = self.params.get("data")
            if data is not None:
                x = [item["x"] for item in data]
                y = [item["y"] for item in data]
            else:
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
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Error generating area chart: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateAreaChart(
        prompt="Revenue Growth Over Time",
        params={
            "data": [{"x": 1, "y": 100}, {"x": 2, "y": 150}, {"x": 3, "y": 180}, {"x": 4, "y": 220}]
        },
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
