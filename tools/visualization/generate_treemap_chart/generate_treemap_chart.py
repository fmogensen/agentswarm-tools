"""
Generate treemap for hierarchical data visualization
"""

import json
import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class GenerateTreemapChart(BaseTool):
    """
    Generate treemap for hierarchical data visualization

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateTreemapChart(prompt="example", params={"data": {...}})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_treemap_chart"
    tool_category: str = "visualization"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional generation parameters (must include hierarchical source data)",
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_treemap_chart tool.

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
        if not self.prompt or not self.prompt.strip():
            raise ValidationError(
                "prompt cannot be empty",
                tool_name=self.tool_name,
                details={"prompt": self.prompt},
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "params must be a dictionary",
                tool_name=self.tool_name,
                details={"params_type": str(type(self.params))},
            )

        if "data" not in self.params:
            raise ValidationError(
                "params must include a 'data' field containing hierarchical input",
                tool_name=self.tool_name,
                details={"params": self.params},
            )

        data = self.params.get("data")
        if not isinstance(data, (dict, list)):
            raise ValidationError(
                "params['data'] must be a dictionary or list representing hierarchical data",
                tool_name=self.tool_name,
                details={"data_type": str(type(data))},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "mock": True,
                "chart_data": {
                    "type": "treemap",
                    "nodes": [
                        {"name": "Group A", "value": 100},
                        {"name": "Group B", "value": 60},
                        {"name": "Group C", "value": 40},
                    ],
                },
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Returns:
            Parsed hierarchical structure ready for treemap rendering.

        Raises:
            APIError: On unexpected processing failures
        """
        data = self.params.get("data")

        try:
            structured = self._normalize_treemap_data(data)

            return {"chart_type": "treemap", "nodes": structured}

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Treemap generation failed: {e}", tool_name=self.tool_name)

    def _normalize_treemap_data(self, data: Any) -> List[Dict[str, Any]]:
        """
        Convert raw hierarchical input into a normalized treemap node list.

        Args:
            data: Raw hierarchical structure

        Returns:
            List of treemap nodes (name, value, children)
        """
        if isinstance(data, dict):
            return self._normalize_dict_node(data)
        elif isinstance(data, list):
            return [self._normalize_dict_node(item) for item in data]
        else:
            raise ValueError("Invalid data format for treemap")

    def _normalize_dict_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a single hierarchical node.

        Args:
            node: Node dictionary

        Returns:
            Normalized node
        """
        name = node.get("name") or node.get("label") or "Unnamed"
        value = node.get("value", None)
        children = node.get("children", None)

        normalized = {"name": name}

        if value is not None:
            normalized["value"] = value

        if children:
            if not isinstance(children, list):
                raise ValueError("children must be a list")
            normalized["children"] = [self._normalize_dict_node(child) for child in children]

        return normalized


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateTreemapChart(
        prompt="Company Budget Breakdown",
        params={
            "data": {
                "name": "Total Budget",
                "value": 1000,
                "children": [
                    {"name": "Engineering", "value": 400},
                    {"name": "Marketing", "value": 300},
                    {"name": "Operations", "value": 200},
                    {"name": "Admin", "value": 100},
                ],
            }
        },
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
