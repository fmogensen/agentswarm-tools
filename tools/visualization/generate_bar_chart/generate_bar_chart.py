"""
Generate bar chart for horizontal categorical comparisons
"""

import base64
import io
import os
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class GenerateBarChart(BaseTool):
    """
    Generate bar chart for horizontal categorical comparisons

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateBarChart(prompt="example", params={"data": {"A": 3}})
        >>> result = tool.run()
    """

    tool_name: str = "generate_bar_chart"
    tool_category: str = "visualization"

    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_bar_chart tool.

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
                "metadata": {"tool_name": self.tool_name, "prompt": self.prompt},
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        if not self.prompt or not isinstance(self.prompt, str):
            raise ValidationError(
                "Prompt must be a non-empty string", tool_name=self.tool_name, field="prompt"
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be a dictionary", tool_name=self.tool_name, field="params"
            )

        data = self.params.get("data")
        if data is None:
            raise ValidationError(
                "Params must include 'data'", tool_name=self.tool_name, field="data"
            )

        # Accept either dict of category/value pairs OR list of {label, value} objects
        if isinstance(data, list):
            if len(data) == 0:
                raise ValidationError(
                    "'data' must not be empty", tool_name=self.tool_name, field="data"
                )
            if not all(
                isinstance(item, dict) and "label" in item and "value" in item for item in data
            ):
                raise ValidationError(
                    "When 'data' is a list, each item must have 'label' and 'value' keys",
                    tool_name=self.tool_name,
                    field="data",
                )
        elif isinstance(data, dict):
            if len(data) == 0:
                raise ValidationError(
                    "'data' must not be empty", tool_name=self.tool_name, field="data"
                )
            if not all(isinstance(k, str) for k in data.keys()):
                raise ValidationError(
                    "All category names (keys in data) must be strings",
                    tool_name=self.tool_name,
                    field="data",
                )
            if not all(isinstance(v, (int, float)) for v in data.values()):
                raise ValidationError(
                    "All values in data must be numeric", tool_name=self.tool_name, field="data"
                )
        else:
            raise ValidationError(
                "Params 'data' must be a dict or list of {label, value} objects",
                tool_name=self.tool_name,
                field="data",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_data = {"A": 5, "B": 3, "C": 8}
        return {
            "success": True,
            "result": {
                "mock": True,
                "description": f"Mock bar chart for: {self.prompt}",
                "data": mock_data,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Generates a horizontal bar chart and returns it as a base64 image.
        """
        raw_data = self.params["data"]

        # Handle both formats: dict or list of {label, value} objects
        if isinstance(raw_data, list):
            categories = [item["label"] for item in raw_data]
            values = [item["value"] for item in raw_data]
            data = {item["label"]: item["value"] for item in raw_data}
        else:
            data = raw_data
            categories = list(data.keys())
            values = list(data.values())

        fig = None
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.barh(categories, values)
            ax.set_xlabel("Value")
            ax.set_ylabel("Category")
            ax.set_title(self.prompt)

            buffer = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            img_b64 = base64.b64encode(buffer.read()).decode("utf-8")

            return {"image_base64": img_b64, "data": data, "description": self.prompt}
        finally:
            if fig is not None:
                plt.close(fig)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateBarChart(
        prompt="Sales by Region",
        params={"data": {"North": 45, "South": 32, "East": 38, "West": 50}},
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
