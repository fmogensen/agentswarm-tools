"""
Generate column chart for vertical categorical comparisons
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import json

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateColumnChart(BaseTool):
    """
    Generate column chart for vertical categorical comparisons

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateColumnChart(prompt="example", params={"values": [1,2,3]})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_column_chart"
    tool_category: str = "visualization"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional generation parameters (e.g., categories, values, title)",
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_column_chart tool.

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
                "metadata": {"tool_name": self.tool_name, "prompt": self.prompt},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are missing or invalid
        """
        if not self.prompt or not self.prompt.strip():
            raise ValidationError(
                "Prompt cannot be empty",
                tool_name=self.tool_name,
                field="prompt",
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be an object (dict)",
                tool_name=self.tool_name,
                field="params",
            )

        categories = self.params.get("categories")
        values = self.params.get("values")

        if categories is None or values is None:
            raise ValidationError(
                "Params must contain 'categories' and 'values'",
                tool_name=self.tool_name,
                field="params",
            )

        if not isinstance(categories, list) or not isinstance(values, list):
            raise ValidationError(
                "'categories' and 'values' must be lists",
                tool_name=self.tool_name,
                field="categories/values",
            )

        if len(categories) != len(values):
            raise ValidationError(
                "'categories' and 'values' must have the same length",
                tool_name=self.tool_name,
                field="categories/values",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_chart = {
            "type": "column",
            "title": f"Mock Chart for: {self.prompt}",
            "categories": ["A", "B", "C"],
            "values": [5, 10, 7],
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
            Dict representing a column chart specification
        """
        try:
            chart_spec = {
                "type": "column",
                "title": self.params.get("title", self.prompt),
                "categories": self.params["categories"],
                "values": self.params["values"],
                "style": self.params.get("style", {}),
                "config": self.params.get("config", {}),
            }
            return chart_spec
        except Exception as exc:
            raise APIError(f"Chart generation failed: {exc}", tool_name=self.tool_name)
