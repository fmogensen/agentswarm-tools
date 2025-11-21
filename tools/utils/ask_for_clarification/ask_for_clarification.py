"""
Request additional information from user when needed
"""

from typing import Any, Dict
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class AskForClarification(BaseTool):
    """
    Request additional information from user when needed

    Args:
        question: Question to ask the user for clarification

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = AskForClarification(question="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "ask_for_clarification"
    tool_category: str = "utils"
    tool_description: str = "Request additional information from user when needed"

    # Parameters
    question: str = Field(
        ..., description="Question to ask the user for clarification", min_length=1
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the ask_for_clarification tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: If parameters are invalid
            APIError: For unexpected failures
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
        """Validate input parameters.

        Raises:
            ValidationError: If question is empty or invalid
        """
        if not self.question or not self.question.strip():
            raise ValidationError(
                "Question cannot be empty",
                tool_name=self.tool_name,
                details={"question": self.question},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "message": "Mock clarification request",
                "question": self.question,
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """Main processing logic.

        Returns:
            Dict containing the clarification question for the user
        """
        return {
            "message": "Clarification required",
            "question": self.question,
            "awaiting_user_response": True,
        }
