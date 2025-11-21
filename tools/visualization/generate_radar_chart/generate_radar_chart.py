"""
Generate radar chart for multidimensional data (4+ dimensions)
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import math

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateRadarChart(BaseTool):
    """
    Generate radar chart for multidimensional data (4+ dimensions)

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateRadarChart(prompt="example", params={"data": {...}})
        >>> result = tool.run()
    """

    tool_name: str = "generate_radar_chart"
    tool_category: str = "visualization"

    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_radar_chart tool.

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
        if not self.prompt or not self.prompt.strip():
            raise ValidationError(
                "Prompt cannot be empty",
                tool_name=self.tool_name,
                field="param",
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be a dictionary",
                tool_name=self.tool_name,
                field="param",
            )

        data = self.params.get("data")
        if data is None:
            raise ValidationError("params.data is required", tool_name=self.tool_name)

        if not isinstance(data, dict) or len(data) < 4:
            raise ValidationError(
                "params.data must be dict with at least 4 dimensions",
                tool_name=self.tool_name,
                details={
                    "dimension_count": len(data) if isinstance(data, dict) else None
                },
            )

        for key, value in data.items():
            if not isinstance(value, (int, float)):
                raise ValidationError(
                    "All dimension values must be numeric",
                    tool_name=self.tool_name,
                    field="param",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_points = [
            {"axis": f"dim{i}", "angle": i * 0.5, "radius": 0.8} for i in range(1, 6)
        ]
        return {
            "success": True,
            "result": {"mock": True, "points": mock_points},
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Converts multidimensional numeric data into radar-chart
        coordinates (angle + radius).
        """
        data: Dict[str, float] = self.params.get("data", {})

        keys = list(data.keys())
        values = list(data.values())

        max_val = max(values) or 1.0
        dim_count = len(keys)

        results = []
        for index, key in enumerate(keys):
            angle = (2 * math.pi * index) / dim_count
            radius = values[index] / max_val if max_val != 0 else 0

            results.append({"axis": key, "angle": angle, "radius": radius})

        return {"points": results, "dimension_count": dim_count, "normalized": True}
