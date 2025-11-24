"""
Generate fishbone diagram for cause-effect analysis
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class GenerateFishboneDiagram(BaseTool):
    """
    Generate fishbone diagram for cause-effect analysis

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateFishboneDiagram(prompt="example", params={"format": "text"})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_fishbone_diagram"
    tool_category: str = "visualization"
    tool_description: str = "Generate fishbone diagram for cause-effect analysis"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate", min_length=1)
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_fishbone_diagram tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid inputs
            APIError: For processing errors
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
                    "prompt": self.prompt,
                    "params": self.params,
                    "tool_name": self.tool_name,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters.

        Raises:
            ValidationError: If prompt or params are invalid
        """
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValidationError(
                "prompt must be a non-empty string",
                tool_name=self.tool_name,
                field="param",
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "params must be a dictionary",
                tool_name=self.tool_name,
                field="param",
            )

        allowed_keys = ["format", "max_branches"]
        for key in self.params:
            if key not in allowed_keys:
                raise ValidationError(
                    f"Invalid parameter key: {key}. Allowed keys: {allowed_keys}",
                    tool_name=self.tool_name,
                    field="param",
                )

        if "max_branches" in self.params:
            if not isinstance(self.params["max_branches"], int) or self.params["max_branches"] <= 0:
                raise ValidationError(
                    "max_branches must be a positive integer",
                    tool_name=self.tool_name,
                    field="param",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        fishbone = {
            "effect": self.prompt,
            "causes": {
                "Mock Category 1": ["Mock Cause A", "Mock Cause B"],
                "Mock Category 2": ["Mock Cause C", "Mock Cause D"],
            },
        }

        return {
            "success": True,
            "result": fishbone,
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Generates a simple structured fishbone diagram representation.

        Returns:
            Dict representing a fishbone diagram
        """
        max_branches = self.params.get("max_branches", 6)

        categories = [
            "Methods",
            "Machines",
            "Materials",
            "Measurements",
            "Environment",
            "People",
        ]

        selected_categories = categories[:max_branches]

        diagram = {"effect": self.prompt, "causes": {}}

        for cat in selected_categories:
            diagram["causes"][cat] = [
                f"Possible cause related to {cat} 1",
                f"Possible cause related to {cat} 2",
            ]

        return diagram


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateFishboneDiagram(
        prompt="Customer Complaints Increase", params={"format": "text", "max_branches": 4}
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
