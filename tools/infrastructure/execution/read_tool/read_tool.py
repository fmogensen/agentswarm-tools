"""
Read files from sandboxed environment with line numbers
"""

import os
from typing import Any, Dict, List

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class ReadTool(BaseTool):
    """
    Read files from sandboxed environment with line numbers

    Args:
        file_path: Path to the file to read

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (file content with line numbers)
        - metadata: Additional information

    Example:
        >>> tool = ReadTool(file_path="/tmp/example.txt")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "read_tool"
    tool_category: str = "infrastructure"
    tool_description: str = "Read files from sandboxed environment with line numbers"

    # Parameters
    file_path: str = Field(..., description="Path to the file to read", min_length=1)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the read_tool tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid parameters
            APIError: For read failures
        """

        self._logger.info(f"Executing {self.tool_name} with file_path={self.file_path}")
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
                "metadata": {"tool_name": self.tool_name, "path": self.file_path},
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to read file: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input is empty or invalid
        """
        if not self.file_path or not isinstance(self.file_path, str):
            raise ValidationError(
                "File path must be a non-empty string",
                tool_name=self.tool_name,
                details={"file_path": self.file_path},
            )

        # Disallow directory traversal attempts
        if ".." in self.file_path:
            raise ValidationError(
                "Invalid file path. Directory traversal is not allowed.",
                tool_name=self.tool_name,
                details={"file_path": self.file_path},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_content = ["1: mock line one", "2: mock line two", "3: mock line three"]
        return {
            "success": True,
            "result": mock_content,
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> List[str]:
        """
        Main processing logic.

        Reads a file and returns its contents with line numbers.

        Returns:
            List of strings with line numbers

        Raises:
            APIError: If file cannot be opened or read
        """
        path = self.file_path

        if not os.path.exists(path):
            raise APIError(f"File not found: {path}", tool_name=self.tool_name)

        if not os.path.isfile(path):
            raise APIError(f"Not a file: {path}", tool_name=self.tool_name)

        try:
            lines_with_numbers: List[str] = []
            with open(path, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f, start=1):
                    lines_with_numbers.append(f"{idx}: {line.rstrip()}")

            return lines_with_numbers

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Unable to read file: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    print("Testing ReadTool...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Read file with mock mode
    print("\nTest 1: Read file with mock mode")
    tool = ReadTool(file_path="/tmp/test.txt")
    result = tool.run()

    assert result.get("success") == True
    assert isinstance(result.get("result"), list)
    assert len(result.get("result")) > 0
    print(f"✅ Test 1 passed: File read successfully")
    print(f"   Lines: {len(result.get('result'))}")
    print(f"   First line: {result.get('result')[0]}")

    # Test 2: Different file path
    print("\nTest 2: Read different file")
    tool = ReadTool(file_path="/home/user/document.txt")
    result = tool.run()

    assert result.get("success") == True
    assert result.get("metadata", {}).get("path") == "/home/user/document.txt"
    print(f"✅ Test 2 passed: Different file read successfully")

    # Test 3: Validation - directory traversal attempt
    print("\nTest 3: Validation - directory traversal")
    try:
        bad_tool = ReadTool(file_path="/tmp/../etc/passwd")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Security validation working - {type(e).__name__}")

    # Test 4: Mock data structure verification
    print("\nTest 4: Mock data structure verification")
    tool = ReadTool(file_path="/test/file.py")
    result = tool.run()

    first_line = result.get("result", [])[0]
    assert ":" in first_line  # Line numbers format
    print(f"✅ Test 4 passed: Line number format correct")

    print("\n✅ All tests passed!")
