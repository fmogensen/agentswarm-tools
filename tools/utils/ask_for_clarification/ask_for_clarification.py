"""
Request additional information from user when needed
"""

import os
from typing import Any, Dict

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


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


if __name__ == "__main__":
    print("Testing AskForClarification...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic clarification request
    print("\nTest 1: Basic clarification request")
    tool = AskForClarification(question="What file format would you like for the output?")
    result = tool.run()

    assert result.get("success") == True
    assert "question" in result.get("result", {})
    print(f"✅ Test 1 passed: {result.get('result', {}).get('message')}")
    print(f"   Question: {result.get('result', {}).get('question')}")

    # Test 2: Multiple choice clarification
    print("\nTest 2: Multiple choice clarification")
    tool = AskForClarification(
        question="Which option do you prefer? A) Export to PDF B) Export to CSV C) Export to JSON"
    )
    result = tool.run()

    assert result.get("success") == True
    print(f"✅ Test 2 passed: Multi-option question created")

    # Test 3: Validation - empty question
    print("\nTest 3: Validation - empty question")
    try:
        bad_tool = AskForClarification(question="   ")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Specific clarification about parameters
    print("\nTest 4: Parameter clarification")
    tool = AskForClarification(
        question="Could you specify the date range for the data you need? (Format: YYYY-MM-DD to YYYY-MM-DD)"
    )
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("awaiting_user_response") == True
    print(f"✅ Test 4 passed: Parameter clarification created")

    print("\n✅ All tests passed!")
