"""
Internal reasoning and memory (no external effects)
"""

from typing import Any, Dict
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class Think(BaseTool):
    """
    Internal reasoning and memory (no external effects)

    Args:
        thought: Internal reasoning or thought to record

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = Think(thought="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "think"
    tool_category: str = "utils"

    # Parameters
    thought: str = Field(
        ..., description="Internal reasoning or thought to record", min_length=1
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the think tool.

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
                "metadata": {"tool_name": self.tool_name, "tool_version": "1.0.0"},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        if not self.thought or not isinstance(self.thought, str):
            raise ValidationError(
                "Thought must be a non-empty string",
                tool_name=self.tool_name,
                details={"thought": self.thought},
            )

        if not self.thought.strip():
            raise ValidationError(
                "Thought cannot be empty or whitespace",
                tool_name=self.tool_name,
                details={"thought": self.thought},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "stored": f"[MOCK] {self.thought}",
                "message": "Mock mode enabled; no real processing performed.",
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        This tool performs internal reasoning only; no external effects.

        Returns:
            Any: Result containing the processed thought
        """
        # For the think tool, the logic is simply to return the thought
        # as an internal memory record.
        return {"stored": self.thought, "message": "Thought recorded internally"}
