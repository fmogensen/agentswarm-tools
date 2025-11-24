"""
Generate pie chart for proportions and parts of whole
"""

import base64
import json
import os
from io import BytesIO
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


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
    params: Dict[str, Any] = Field(default={}, description="Additional generation parameters")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_pie_chart tool.

        Returns:
            Dict with results
        """

        self._logger.info(
            f"Executing {self.tool_name} with prompt={self.prompt}, params={self.params}"
        )
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
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
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.prompt or not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValidationError(
                "prompt must be a non-empty string", tool_name=self.tool_name, field="prompt"
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "params must be an object (dict)", tool_name=self.tool_name, field="params"
            )

        # Accept either labels/values arrays OR data as list of {label, value} objects
        data = self.params.get("data")
        labels = self.params.get("labels")
        values = self.params.get("values")

        if data is not None:
            # New format: list of {label, value} objects
            if not isinstance(data, list):
                raise ValidationError(
                    "'data' must be a list", tool_name=self.tool_name, field="data"
                )
            if len(data) == 0:
                raise ValidationError(
                    "'data' must not be empty", tool_name=self.tool_name, field="data"
                )
            if not all(
                isinstance(item, dict) and "label" in item and "value" in item for item in data
            ):
                raise ValidationError(
                    "When 'data' is provided, each item must have 'label' and 'value' keys",
                    tool_name=self.tool_name,
                    field="data",
                )
            extracted_values = [item["value"] for item in data]
            if not all(isinstance(x, (int, float)) for x in extracted_values):
                raise ValidationError(
                    "All values must be numeric", tool_name=self.tool_name, field="data"
                )
            if sum(extracted_values) <= 0:
                raise ValidationError(
                    "Sum of values must be greater than zero",
                    tool_name=self.tool_name,
                    field="data",
                )
        elif labels is not None and values is not None:
            # Original format: separate labels and values arrays
            if not isinstance(labels, list) or not isinstance(values, list):
                raise ValidationError(
                    "'labels' and 'values' must be lists",
                    tool_name=self.tool_name,
                    field="labels/values",
                )

            if len(labels) != len(values):
                raise ValidationError(
                    "'labels' and 'values' must have the same length",
                    tool_name=self.tool_name,
                    field="labels/values",
                )

            if not all(isinstance(x, (int, float)) for x in values):
                raise ValidationError(
                    "All values must be numeric", tool_name=self.tool_name, field="values"
                )

            if sum(values) <= 0:
                raise ValidationError(
                    "Sum of values must be greater than zero",
                    tool_name=self.tool_name,
                    field="values",
                )
        else:
            raise ValidationError(
                "params must include either 'data' (list of {label, value}) or 'labels' and 'values'",
                tool_name=self.tool_name,
                field="params",
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
        # Handle both formats: data list or separate labels/values
        data = self.params.get("data")
        if data is not None:
            labels = [item["label"] for item in data]
            values = [item["value"] for item in data]
        else:
            labels = self.params["labels"]
            values = self.params["values"]

        title = self.params.get("title", "Pie Chart")
        colors = self.params.get("colors")

        fig = None
        try:
            fig, ax = plt.subplots()
            ax.pie(values, labels=labels, autopct="%1.1f%%", colors=colors)
            ax.set_title(title)

            buffer = BytesIO()
            plt.savefig(buffer, format="png", bbox_inches="tight")
            buffer.seek(0)
            encoded = base64.b64encode(buffer.read()).decode("utf-8")

            return {
                "image_base64": encoded,
                "labels": labels,
                "values": values,
                "title": title,
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Pie chart generation failed: {e}", tool_name=self.tool_name)
        finally:
            if fig is not None:
                plt.close(fig)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GeneratePieChart(
        prompt="Market Share Distribution",
        params={
            "data": [
                {"label": "Product A", "value": 40},
                {"label": "Product B", "value": 35},
                {"label": "Product C", "value": 25},
            ]
        },
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
