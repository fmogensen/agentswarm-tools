"""
Generate dual axes chart combining column and line charts
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import base64
import io

import matplotlib.pyplot as plt

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateDualAxesChart(BaseTool):
    """
    Generate dual axes chart combining column and line charts

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateDualAxesChart(prompt="example", params={"data": {...}})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_dual_axes_chart"
    tool_category: str = "visualization"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_dual_axes_chart tool.

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
                field="prompt",
                tool_name=self.tool_name,
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be a dictionary",
                field="params",
                tool_name=self.tool_name,
            )

        required_fields = ["x", "column_values", "line_values"]
        data = self.params.get("data")

        if data is None or not isinstance(data, dict):
            raise ValidationError(
                "Params must include a 'data' dict",
                field="params",
                tool_name=self.tool_name,
            )

        for f in required_fields:
            if f not in data:
                raise ValidationError(
                    f"Missing required data field '{f}'",
                    field=f,
                    tool_name=self.tool_name,
                )

            if not isinstance(data[f], list):
                raise ValidationError(
                    f"'{f}' must be a list",
                    field=f,
                    tool_name=self.tool_name,
                )

        if not (len(data["x"]) == len(data["column_values"]) == len(data["line_values"])):
            raise ValidationError(
                "Data lists must have equal lengths",
                field="data",
                tool_name=self.tool_name,
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {"mock": True, "chart_base64": "dHVubmVsbW9jay1kYXRh"},
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        data = self.params["data"]
        x = data["x"]
        col = data["column_values"]
        line = data["line_values"]

        fig = None
        try:
            fig, ax1 = plt.subplots(figsize=(10, 6))

            ax1.bar(x, col, color="skyblue", label="Column Series")
            ax1.set_ylabel("Column Values")

            ax2 = ax1.twinx()
            ax2.plot(x, line, color="red", marker="o", label="Line Series")
            ax2.set_ylabel("Line Values")

            plt.title(self.prompt)

            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format="png", bbox_inches="tight")
            img_bytes.seek(0)

            encoded = base64.b64encode(img_bytes.read()).decode("utf-8")

            return {
                "chart_base64": encoded,
                "x": x,
                "column_values": col,
                "line_values": line,
            }
        finally:
            if fig is not None:
                plt.close(fig)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateDualAxesChart(
        prompt="Sales and Customer Count Analysis",
        params={
            "data": {
                "x": ["Jan", "Feb", "Mar", "Apr"],
                "column_values": [100, 120, 90, 150],
                "line_values": [50, 60, 55, 70],
            }
        },
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
