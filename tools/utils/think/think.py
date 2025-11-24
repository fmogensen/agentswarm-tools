"""
Internal reasoning and memory (no external effects)
"""

import os
from typing import Any, Dict

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


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
    thought: str = Field(..., description="Internal reasoning or thought to record", min_length=1)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the think tool.

        Returns:
            Dict with results
        """

        self._logger.info(f"Executing {self.tool_name} with thought={self.thought}")
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
                "metadata": {"tool_name": self.tool_name, "tool_version": "1.0.0"},
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


if __name__ == "__main__":
    print("Testing Think...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic thought recording
    print("\nTest 1: Basic thought recording")
    tool = Think(thought="I need to analyze the user's requirements before proceeding")
    result = tool.run()

    assert result.get("success") == True
    assert "stored" in result.get("result", {})
    print(f"✅ Test 1 passed: {result.get('result', {}).get('message')}")
    print(f"   Thought stored: {result.get('result', {}).get('stored')[:50]}...")

    # Test 2: Long thought
    print("\nTest 2: Long thought recording")
    long_thought = "This is a complex reasoning process that involves multiple steps: " * 5
    tool = Think(thought=long_thought)
    result = tool.run()

    assert result.get("success") == True
    print(f"✅ Test 2 passed: Long thought stored ({len(long_thought)} chars)")

    # Test 3: Validation - empty thought
    print("\nTest 3: Validation - empty thought")
    try:
        bad_tool = Think(thought="   ")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Validation - non-string thought
    print("\nTest 4: Validation - non-string thought")
    try:
        bad_tool = Think(thought="")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 4 passed: Validation working - {type(e).__name__}")

    print("\n✅ All tests passed!")
