"""
Read files from sandboxed environment with line numbers
"""

from typing import Any, Dict, List
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


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
    tool_category: str = "code_execution"
    tool_description: str = "Read files from sandboxed environment with line numbers"

    # Parameters
    file_path: str = Field(..., description="Path to the file to read")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the read_tool tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid parameters
            APIError: For read failures
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
                "metadata": {"tool_name": self.tool_name, "path": self.file_path},
            }
        except Exception as e:
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
            raise APIError(f"Unable to read file: {e}", tool_name=self.tool_name)
