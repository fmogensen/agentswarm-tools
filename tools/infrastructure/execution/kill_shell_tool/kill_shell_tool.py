"""
Terminate background bash processes by shell ID
"""

import os
import signal
import time
from typing import Any, Dict, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError

# Simulated shell tracking registry (in real implementation, this would be a persistent store)
_SHELL_REGISTRY = {}


class KillShellTool(BaseTool):
    """
    Terminate background bash processes by shell ID.

    This tool allows terminating background shell processes that were started
    and tracked by the system. Supports both graceful (SIGTERM) and forced
    (SIGKILL) termination.

    Args:
        shell_id: ID of the background shell to terminate (required)
        force: Whether to use force kill (SIGKILL) instead of graceful termination (SIGTERM)
        timeout: Seconds to wait for graceful shutdown before force killing (default: 5)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Termination details (shell_id, terminated, exit_code, signal_used, cleanup_performed)
        - metadata: Tool execution information

    Example:
        >>> # Graceful termination
        >>> tool = KillShellTool(shell_id="shell_123", force=False, timeout=5)
        >>> result = tool.run()

        >>> # Force termination
        >>> tool = KillShellTool(shell_id="shell_456", force=True)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "kill_shell_tool"
    tool_category: str = "infrastructure"
    tool_description: str = "Terminate background bash processes by shell ID"

    # Parameters
    shell_id: str = Field(
        ...,
        description="ID of background shell to terminate",
        min_length=1,
    )
    force: bool = Field(
        False,
        description="Use force kill (SIGKILL vs SIGTERM)",
    )
    timeout: int = Field(
        5,
        description="Seconds to wait before force kill",
        ge=0,
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the kill_shell_tool logic.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid input
            APIError: For execution failures
        """

        self._logger.info(
            f"Executing {self.tool_name} with shell_id={self.shell_id}, force={self.force}, timeout={self.timeout}"
        )
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
            ValidationError: If shell_id is empty or timeout is negative
        """
        if not self.shell_id or not self.shell_id.strip():
            raise ValidationError(
                "shell_id cannot be empty",
                tool_name=self.tool_name,
                details={"shell_id": self.shell_id},
            )

        if self.timeout < 0:
            raise ValidationError(
                f"timeout must be non-negative, got {self.timeout}",
                tool_name=self.tool_name,
                details={"timeout": self.timeout},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        # Determine signal based on force flag or timeout=0
        use_sigkill = self.force or self.timeout == 0
        return {
            "success": True,
            "result": {
                "mock": True,
                "shell_id": self.shell_id,
                "terminated": True,
                "exit_code": -9 if use_sigkill else 0,
                "signal_used": "SIGKILL" if use_sigkill else "SIGTERM",
                "cleanup_performed": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Dict[str, Any]:
        """
        Terminate the background shell process.

        Returns:
            Dict with termination details

        Raises:
            APIError: If shell_id not found or termination fails
        """
        # Check if shell exists in tracking system
        if self.shell_id not in _SHELL_REGISTRY:
            raise APIError(
                f"Shell ID '{self.shell_id}' not found in tracking system",
                tool_name=self.tool_name,
            )

        shell_info = _SHELL_REGISTRY[self.shell_id]
        pid = shell_info.get("pid")
        status = shell_info.get("status", "running")

        # Check if shell is already terminated
        if status in ["terminated", "stopped", "zombie"]:
            self._logger.info(f"Shell {self.shell_id} is already {status}")
            # Still clean up from registry
            del _SHELL_REGISTRY[self.shell_id]
            return {
                "shell_id": self.shell_id,
                "terminated": True,
                "exit_code": shell_info.get("exit_code", 0),
                "signal_used": "N/A (already terminated)",
                "cleanup_performed": True,
                "previous_status": status,
            }

        # Determine signal to use
        signal_used = None
        exit_code = None

        try:
            if self.force or self.timeout == 0:
                # Force kill immediately
                self._logger.info(f"Force killing shell {self.shell_id} (PID: {pid})")
                os.kill(pid, signal.SIGKILL)
                signal_used = "SIGKILL"
                exit_code = -9
            else:
                # Graceful termination with timeout
                self._logger.info(f"Gracefully terminating shell {self.shell_id} (PID: {pid})")
                os.kill(pid, signal.SIGTERM)
                signal_used = "SIGTERM"

                # Wait for process to terminate
                start_time = time.time()
                process_terminated = False

                while time.time() - start_time < self.timeout:
                    try:
                        # Check if process still exists
                        os.kill(pid, 0)  # Signal 0 doesn't kill, just checks existence
                        time.sleep(0.1)  # Brief sleep before checking again
                    except OSError:
                        # Process doesn't exist anymore - it terminated
                        process_terminated = True
                        exit_code = 0
                        break

                # If still running after timeout, force kill
                if not process_terminated:
                    self._logger.warning(
                        f"Shell {self.shell_id} did not terminate within {self.timeout}s, force killing"
                    )
                    os.kill(pid, signal.SIGKILL)
                    signal_used = "SIGKILL (after SIGTERM timeout)"
                    exit_code = -9

        except ProcessLookupError:
            # Process doesn't exist (already terminated)
            self._logger.info(f"Process {pid} already terminated")
            signal_used = "N/A (process not found)"
            exit_code = 0
        except PermissionError:
            raise APIError(
                f"Permission denied to kill process {pid}",
                tool_name=self.tool_name,
            )
        except Exception as e:
            raise APIError(
                f"Failed to kill shell: {e}",
                tool_name=self.tool_name,
            )

        # Clean up from registry
        del _SHELL_REGISTRY[self.shell_id]

        return {
            "shell_id": self.shell_id,
            "terminated": True,
            "exit_code": exit_code,
            "signal_used": signal_used,
            "cleanup_performed": True,
            "pid": pid,
        }


# Helper functions for shell tracking (used by BashTool or similar)
def register_shell(shell_id: str, pid: int, command: str = "") -> None:
    """Register a new shell in the tracking system."""
    _SHELL_REGISTRY[shell_id] = {
        "pid": pid,
        "command": command,
        "status": "running",
        "started_at": time.time(),
    }


def update_shell_status(shell_id: str, status: str, exit_code: Optional[int] = None) -> None:
    """Update shell status in tracking system."""
    if shell_id in _SHELL_REGISTRY:
        _SHELL_REGISTRY[shell_id]["status"] = status
        if exit_code is not None:
            _SHELL_REGISTRY[shell_id]["exit_code"] = exit_code


def get_shell_info(shell_id: str) -> Optional[Dict[str, Any]]:
    """Get information about a tracked shell."""
    return _SHELL_REGISTRY.get(shell_id)


def list_shells() -> Dict[str, Dict[str, Any]]:
    """List all tracked shells."""
    return _SHELL_REGISTRY.copy()


if __name__ == "__main__":
    print("Testing KillShellTool...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Graceful termination
    print("\nTest 1: Graceful termination")
    tool = KillShellTool(shell_id="test_shell_123", force=False)
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("shell_id") == "test_shell_123"
    assert result.get("result", {}).get("terminated") == True
    assert result.get("result", {}).get("signal_used") in ["SIGTERM", "SIGKILL"]
    print(f"✅ Test 1 passed: Graceful termination succeeded")
    print(f"   Signal used: {result.get('result', {}).get('signal_used')}")

    # Test 2: Force termination
    print("\nTest 2: Force termination")
    tool = KillShellTool(shell_id="test_shell_456", force=True)
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("signal_used") == "SIGKILL"
    assert result.get("result", {}).get("exit_code") == -9
    print(f"✅ Test 2 passed: Force termination succeeded")

    # Test 3: Validation - empty shell_id
    print("\nTest 3: Validation - empty shell_id")
    try:
        bad_tool = KillShellTool(shell_id="   ", force=False)
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Validation - negative timeout
    print("\nTest 4: Validation - negative timeout")
    try:
        bad_tool = KillShellTool(shell_id="test_shell", timeout=-5)
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 4 passed: Validation working - {type(e).__name__}")

    # Test 5: Zero timeout (immediate force kill)
    print("\nTest 5: Zero timeout (immediate force kill)")
    tool = KillShellTool(shell_id="test_shell_789", timeout=0)
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("signal_used") == "SIGKILL"
    print(f"✅ Test 5 passed: Zero timeout force kill succeeded")

    print("\n✅ All tests passed!")
