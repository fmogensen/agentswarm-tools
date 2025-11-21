"""
Generate mind map for hierarchical information organization
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateMindMap(BaseTool):
    """
    Generate mind map for hierarchical information organization

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateMindMap(prompt="example", params={})
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_mind_map"
    tool_category: str = "visualization"
    tool_description: str = (
        "Generate mind map for hierarchical information organization"
    )

    # Parameters
    prompt: str = Field(
        ...,
        description="Description of what to generate",
        min_length=1,
        max_length=5000,
    )

    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_mind_map tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid parameters
            APIError: For external API failures
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
                "metadata": {
                    "tool_name": self.tool_name,
                    "prompt_length": len(self.prompt),
                    "params_used": bool(self.params),
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        if not isinstance(self.prompt, str) or not self.prompt.strip():
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

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """
        Generate mock results for testing.

        Returns:
            Dict with mock mind map
        """
        mock_map = {
            "root": self.prompt,
            "branches": [
                {"title": "Mock Branch 1", "children": ["A", "B", "C"]},
                {"title": "Mock Branch 2", "children": ["D", "E"]},
            ],
        }

        return {
            "success": True,
            "result": mock_map,
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Returns:
            Structured mind map data

        Raises:
            APIError: If generation fails
        """
        try:
            # Simple heuristic-based mind-map generator
            lines = [line.strip() for line in self.prompt.split("\n") if line.strip()]

            if not lines:
                raise ValidationError(
                    "Prompt does not contain any usable text", tool_name=self.tool_name
                )

            root = lines[0]
            branches: List[Dict[str, Any]] = []

            for line in lines[1:]:
                if ":" in line:
                    title, items = line.split(":", 1)
                    children = [i.strip() for i in items.split(",") if i.strip()]
                    branches.append({"title": title.strip(), "children": children})
                else:
                    branches.append({"title": line, "children": []})

            return {"root": root, "branches": branches, "params": self.params}

        except ValidationError:
            raise
        except Exception as e:
            raise APIError(f"Mind map generation failed: {e}", tool_name=self.tool_name)
