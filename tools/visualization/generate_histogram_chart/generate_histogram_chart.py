"""
Generate histogram for frequency distribution
"""

import os
from typing import Any, Dict, List, Optional

import numpy as np
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class GenerateHistogramChart(BaseTool):
    """
    Generate histogram for frequency distribution

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateHistogramChart(prompt="example", params={"data": [1,2,3]})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_histogram_chart"
    tool_category: str = "visualization"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate", min_length=1)
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_histogram_chart tool.

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
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.prompt or not self.prompt.strip():
            raise ValidationError(
                "Prompt cannot be empty",
                tool_name=self.tool_name,
                details={"prompt": self.prompt},
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be a dictionary",
                tool_name=self.tool_name,
                details={"params": self.params},
            )

        data = self.params.get("data")
        if data is None:
            raise ValidationError(
                "Missing required parameter: data",
                tool_name=self.tool_name,
                details={"params": self.params},
            )

        if not isinstance(data, list) or not all(isinstance(x, (int, float)) for x in data):
            raise ValidationError(
                "Data must be a list of numbers",
                tool_name=self.tool_name,
                details={"data": data},
            )

        bins = self.params.get("bins")
        if bins is not None and (not isinstance(bins, int) or bins <= 0):
            raise ValidationError(
                "Bins must be a positive integer",
                tool_name=self.tool_name,
                details={"bins": bins},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_hist = {"bins": [0, 1, 2, 3], "counts": [5, 10, 3]}

        return {
            "success": True,
            "result": mock_hist,
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Generates histogram bins and counts.
        """
        data = self.params["data"]
        bins = self.params.get("bins", 10)

        try:
            counts, bin_edges = np.histogram(data, bins=bins)
        except Exception as e:
            raise APIError(f"Histogram generation failed: {e}", tool_name=self.tool_name)

        return {
            "bins": bin_edges.tolist(),
            "counts": counts.tolist(),
            "total_points": len(data),
        }


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateHistogramChart(
        prompt="Age Distribution Analysis",
        params={"data": [22, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50, 52, 55], "bins": 5},
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
