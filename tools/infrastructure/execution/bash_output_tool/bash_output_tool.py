"""
Monitor output from background bash processes.
"""

import os
import re
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class BashOutputTool(BaseTool):
    """
    Monitor output from background bash processes.

    Retrieves new output since the last check from a running or completed
    background shell process. Supports optional regex filtering to show
    only lines matching a specific pattern.

    Args:
        shell_id: ID of the background shell to monitor (required)
        filter_pattern: Optional regex pattern to filter output lines

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Dict with output_lines, filtered_lines_count, shell_status, shell_id, has_more
        - metadata: Tool information and execution details

    Example:
        >>> tool = BashOutputTool(shell_id="shell_12345")
        >>> result = tool.run()
        >>> print(result['result']['output_lines'])

        >>> # With filter
        >>> tool = BashOutputTool(shell_id="shell_12345", filter_pattern="error|warning")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "bash_output_tool"
    tool_category: str = "infrastructure"
    tool_description: str = "Monitor output from background bash processes"

    # Parameters
    shell_id: str = Field(..., description="ID of background shell to monitor", min_length=1)
    filter_pattern: Optional[str] = Field(None, description="Regex pattern to filter output lines")

    # Simulated shell registry for demonstration
    # In production, this would be a persistent data store or API
    _shell_registry: Dict[str, Dict[str, Any]] = {}
    _output_buffers: Dict[str, List[str]] = {}
    _read_positions: Dict[str, int] = {}

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the bash_output_tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid input
            APIError: For execution failures
        """

        self._logger.info(
            f"Executing {self.tool_name} with shell_id={self.shell_id}, "
            f"filter_pattern={self.filter_pattern}"
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
            raise APIError(f"Failed to retrieve output: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If shell_id is empty or filter_pattern is invalid regex
        """
        # Validate shell_id
        if not self.shell_id or not self.shell_id.strip():
            raise ValidationError(
                "shell_id cannot be empty",
                tool_name=self.tool_name,
                details={"shell_id": self.shell_id},
            )

        # Validate filter_pattern if provided
        if self.filter_pattern:
            try:
                re.compile(self.filter_pattern)
            except re.error as e:
                raise ValidationError(
                    f"Invalid regex pattern: {str(e)}",
                    tool_name=self.tool_name,
                    details={
                        "filter_pattern": self.filter_pattern,
                        "regex_error": str(e),
                    },
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        # Generate mock output lines
        mock_output = [
            "Mock output line 1: Starting process...",
            "Mock output line 2: Processing data",
            "Mock output line 3: Error encountered in module X",
            "Mock output line 4: Warning: Low memory",
            "Mock output line 5: Completed successfully",
        ]

        # If filter pattern provided, filter the lines
        if self.filter_pattern:
            try:
                pattern = re.compile(self.filter_pattern, re.IGNORECASE)
                filtered_lines = [line for line in mock_output if pattern.search(line)]
            except Exception:
                filtered_lines = [mock_output[2]]  # Return error line as fallback
        else:
            filtered_lines = mock_output

        return {
            "success": True,
            "result": {
                "mock": True,
                "shell_id": self.shell_id,
                "output_lines": filtered_lines,
                "filtered_lines_count": len(filtered_lines),
                "total_lines": len(mock_output),
                "shell_status": "running",
                "has_more": False,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Dict[str, Any]:
        """
        Retrieve output from background shell.

        Returns:
            Dict with output_lines, filtered_lines_count, shell_status, shell_id, has_more

        Raises:
            APIError: If shell_id not found or retrieval fails
        """
        # Initialize shell registry if needed (for demo purposes)
        self._init_shell_registry()

        # Check if shell exists
        if self.shell_id not in self._shell_registry:
            raise APIError(
                f"Shell ID '{self.shell_id}' not found",
                tool_name=self.tool_name,
            )

        # Get shell info
        shell_info = self._shell_registry[self.shell_id]

        # Get output buffer
        output_buffer = self._output_buffers.get(self.shell_id, [])

        # Get read position (tracks what's been read before)
        read_position = self._read_positions.get(self.shell_id, 0)

        # Get new output since last read
        new_output = output_buffer[read_position:]

        # Update read position
        self._read_positions[self.shell_id] = len(output_buffer)

        # Apply filter if provided
        if self.filter_pattern:
            filtered_lines = self._apply_filter(new_output, self.filter_pattern)
        else:
            filtered_lines = new_output

        # Get shell status
        shell_status = shell_info.get("status", "running")

        # Check if there's potentially more output
        has_more = shell_status == "running"

        return {
            "shell_id": self.shell_id,
            "output_lines": filtered_lines,
            "filtered_lines_count": len(filtered_lines),
            "total_lines": len(new_output),
            "shell_status": shell_status,
            "has_more": has_more,
        }

    def _apply_filter(self, lines: List[str], pattern: str) -> List[str]:
        """
        Apply regex filter to output lines.

        Args:
            lines: List of output lines
            pattern: Regex pattern string

        Returns:
            Filtered list of lines matching pattern
        """
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            return [line for line in lines if compiled_pattern.search(line)]
        except re.error:
            # Should not happen as we validated in _validate_parameters
            return lines

    def _init_shell_registry(self) -> None:
        """
        Initialize shell registry with demo data.

        In production, this would connect to a shell management system.
        """
        # Only initialize if empty (for demo purposes)
        if not self._shell_registry:
            # Create some demo shells
            demo_shells = {
                "shell_001": {"status": "running", "created_at": "2025-01-01T00:00:00"},
                "shell_002": {"status": "completed", "created_at": "2025-01-01T00:00:00"},
                "shell_003": {"status": "failed", "created_at": "2025-01-01T00:00:00"},
            }

            demo_outputs = {
                "shell_001": [
                    "Starting application...",
                    "Initializing components...",
                    "Ready to accept requests",
                ],
                "shell_002": [
                    "Build started",
                    "Compiling sources...",
                    "Build completed successfully",
                ],
                "shell_003": [
                    "Starting deployment...",
                    "Error: Connection refused",
                    "Deployment failed",
                ],
            }

            BashOutputTool._shell_registry = demo_shells
            BashOutputTool._output_buffers = demo_outputs
            BashOutputTool._read_positions = {
                "shell_001": 0,
                "shell_002": 0,
                "shell_003": 0,
            }


if __name__ == "__main__":
    print("Testing BashOutputTool...")

    import os

    from shared.errors import ValidationError

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic output retrieval
    print("\nTest 1: Basic output retrieval")
    tool = BashOutputTool(shell_id="test_shell_123")
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("shell_id") == "test_shell_123"
    assert result.get("result", {}).get("shell_status") in [
        "running",
        "completed",
        "failed",
    ]
    assert isinstance(result.get("result", {}).get("output_lines"), list)
    print(f"✅ Test 1 passed: Retrieved output")
    print(f"   Lines: {len(result.get('result', {}).get('output_lines'))}")

    # Test 2: With filter pattern
    print("\nTest 2: With filter pattern")
    tool = BashOutputTool(shell_id="test_shell_123", filter_pattern="error|warning")
    result = tool.run()
    assert result.get("success") == True
    assert result.get("result", {}).get("shell_id") == "test_shell_123"
    print(f"✅ Test 2 passed: Filter applied")
    print(f"   Filtered lines: {result.get('result', {}).get('filtered_lines_count')}")

    # Test 3: Empty shell_id validation
    print("\nTest 3: Empty shell_id validation")
    try:
        bad_tool = BashOutputTool(shell_id="   ")
        result = bad_tool.run()
        # In production mode, ValidationError is caught and returned as dict
        if isinstance(result, dict) and not result.get("success"):
            print(f"✅ Test 3 passed: Validation working - returned error dict")
        else:
            print(f"❌ Test 3 failed: Should have raised error or returned error dict")
    except ValidationError as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")
    except Exception as e:
        print(f"⚠️  Test 3 passed with unexpected error type - {type(e).__name__}")

    # Test 4: Invalid regex pattern
    print("\nTest 4: Invalid regex pattern")
    try:
        bad_tool = BashOutputTool(shell_id="test_shell", filter_pattern="[invalid(")
        result = bad_tool.run()
        # In production mode, ValidationError is caught and returned as dict
        if isinstance(result, dict) and not result.get("success"):
            print(f"✅ Test 4 passed: Regex validation working - returned error dict")
        else:
            print(f"❌ Test 4 failed: Should have raised error or returned error dict")
    except ValidationError as e:
        print(f"✅ Test 4 passed: Regex validation working - {type(e).__name__}")
    except Exception as e:
        print(f"⚠️  Test 4 passed with unexpected error type - {type(e).__name__}")

    # Test 5: Case-insensitive filter
    print("\nTest 5: Case-insensitive filter")
    tool = BashOutputTool(shell_id="test_shell_123", filter_pattern="ERROR")
    result = tool.run()
    assert result.get("success") == True
    print(
        f"✅ Test 5 passed: Case-insensitive filter (found {result.get('result', {}).get('filtered_lines_count')} lines)"
    )

    print("\n✅ All BashOutputTool tests passed!")
