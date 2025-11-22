"""
Generate flow diagram for processes and workflows
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateFlowDiagram(BaseTool):
    """
    Generate flow diagram for processes and workflows

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateFlowDiagram(prompt="example", params="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_flow_diagram"
    tool_category: str = "visualization"

    # Parameters
    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_flow_diagram tool.

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
                "metadata": {
                    "tool_name": self.tool_name,
                    "params_used": self.params,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters.

        Raises:
            ValidationError: If prompt is empty or params is invalid
        """
        if (
            not self.prompt
            or not isinstance(self.prompt, str)
            or not self.prompt.strip()
        ):
            raise ValidationError(
                "Prompt must be a non-empty string",
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
        """Generate mock results for testing."""
        mock_diagram = """
        [Start] --> [Mock Process A] --> [Mock Decision?]
                         | Yes                | No
                         v                    v
                   [Mock Path 1]         [Mock Path 2]
        """
        return {
            "success": True,
            "result": {
                "diagram_text": mock_diagram.strip(),
                "format": "text",
                "mock": True,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "tool_version": "1.0.0",
            },
        }

    def _process(self) -> Any:
        """Main processing logic.

        Returns:
            Dict containing flow diagram output
        """
        try:
            steps = self._extract_steps_from_prompt(self.prompt)

            diagram_lines = []
            for i, step in enumerate(steps):
                if i == 0:
                    diagram_lines.append(f"[Start] --> [{step}]")
                else:
                    diagram_lines.append(f"[{steps[i-1]}] --> [{step}]")

            diagram_text = "\n".join(diagram_lines)

            return {
                "diagram_text": diagram_text,
                "format": "text",
                "step_count": len(steps),
            }

        except Exception as e:
            raise APIError(
                f"Flow diagram generation failed: {e}", tool_name=self.tool_name
            )

    def _extract_steps_from_prompt(self, prompt: str) -> List[str]:
        """Extract workflow steps from the prompt.

        Args:
            prompt: Text describing the workflow

        Returns:
            List of step names

        Raises:
            ValidationError: If steps cannot be extracted
        """
        steps = [part.strip() for part in prompt.split("->") if part.strip()]

        if not steps:
            steps = [s.strip() for s in prompt.replace(",", " ").split() if s.strip()]

        if not steps:
            raise ValidationError(
                "Unable to extract steps from prompt",
                tool_name=self.tool_name,
                details={"prompt": prompt},
            )

        return steps


if __name__ == "__main__":
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateFlowDiagram(
        prompt="Order Processing -> Payment Verification -> Shipping -> Delivery",
        params={}
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get('success') == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
