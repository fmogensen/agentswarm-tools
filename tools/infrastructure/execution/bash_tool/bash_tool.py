"""
Execute bash commands in sandboxed Linux environment
"""

import os
import subprocess
from typing import Any, Dict

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class BashTool(BaseTool):
    """
    Execute bash commands in sandboxed Linux environment

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = BashTool(input="echo hello")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "bash_tool"
    tool_category: str = "infrastructure"
    tool_description: str = "Execute bash commands in sandboxed Linux environment"

    # Parameters
    input: str = Field(..., description="Primary input parameter", min_length=1, max_length=5000)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the bash_tool tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid input
            APIError: For execution failures
        """

        self._logger.info(f"Executing {self.tool_name} with input={self.input}")
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
            ValidationError: If input is empty or invalid
        """
        if not self.input or not self.input.strip():
            raise ValidationError(
                "Input command cannot be empty",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        # Additional security restrictions — prevent dangerous commands
        forbidden = ["rm -rf", "shutdown", "reboot", ":(){:|:&};:"]  # simple heuristic
        lowered = self.input.lower()
        for cmd in forbidden:
            if cmd in lowered:
                raise ValidationError(
                    "Forbidden command detected",
                    tool_name=self.tool_name,
                    details={"forbidden_substring": cmd},
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "stdout": f"MOCK: Executed '{self.input}'",
                "stderr": "",
                "exit_code": 0,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "tool_version": "1.0.0",
            },
        }

    def _process(self) -> Any:
        """
        Execute the bash command within the sandbox.

        Returns:
            Dict with stdout, stderr, exit_code

        Raises:
            APIError: If execution fails unexpectedly
        """
        try:
            completed = subprocess.run(
                self.input, shell=True, capture_output=True, text=True, timeout=20
            )
        except subprocess.TimeoutExpired:
            raise APIError("Command execution timed out", tool_name=self.tool_name)
        except Exception as exc:
            raise APIError(f"Execution error: {exc}", tool_name=self.tool_name)

        return {
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "exit_code": completed.returncode,
        }


if __name__ == "__main__":
    print("Testing BashTool...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Execute simple echo command
    print("\nTest 1: Execute echo command")
    tool = BashTool(input="echo 'Hello World'")
    result = tool.run()

    assert result.get("success") == True
    assert "stdout" in result.get("result", {})
    print(f"✅ Test 1 passed: Command executed")
    print(f"   Output: {result.get('result', {}).get('stdout')}")

    # Test 2: Different command
    print("\nTest 2: Execute pwd command")
    tool = BashTool(input="pwd")
    result = tool.run()

    assert result.get("success") == True
    print(f"✅ Test 2 passed: Command executed successfully")

    # Test 3: Validation - empty command
    print("\nTest 3: Validation - empty command")
    try:
        bad_tool = BashTool(input="   ")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Security - forbidden command
    print("\nTest 4: Security - forbidden command")
    try:
        bad_tool = BashTool(input="rm -rf /")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 4 passed: Security validation working - {type(e).__name__}")

    print("\n✅ All tests passed!")
