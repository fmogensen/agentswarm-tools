"""
Create or overwrite files in sandboxed environment
"""

from typing import Any, Dict
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class WriteTool(BaseTool):
    """
    Create or overwrite files in sandboxed environment

    Args:
        file_path: Path where the file should be created/written
        content: Content to write to the file

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (path, size, etc.)
        - metadata: Additional information

    Example:
        >>> tool = WriteTool(file_path="/tmp/example.txt", content="hello world")
        >>> result = tool.run()
    """

    tool_name: str = "write_tool"
    tool_category: str = "code_execution"

    file_path: str = Field(..., description="Path where the file should be created/written")
    content: str = Field(..., description="Content to write to the file")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the write_tool tool.

        Returns:
            Dict with results
        """
        self._validate_parameters()

        if self._should_use_mock():
            return self._generate_mock_results()

        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters.

        Raises:
            ValidationError: If file_path or content is invalid.
        """
        if not self.file_path or not self.file_path.strip():
            raise ValidationError(
                "File path cannot be empty",
                tool_name=self.tool_name,
                details={"file_path": self.file_path},
            )

        if not isinstance(self.content, str):
            raise ValidationError(
                "Content must be a string",
                tool_name=self.tool_name,
                details={"content_type": type(self.content).__name__},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "mock": True,
                "written": False,
                "path": self.file_path,
                "content_preview": self.content[:100],
                "bytes_written": len(self.content),
            },
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """Main processing logic: Create or overwrite a file.

        Returns:
            Dict with write result.

        Raises:
            APIError: If file write fails.
        """
        try:
            # Ensure directory exists
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.content)

            return {
                "written": True,
                "path": self.file_path,
                "bytes_written": len(self.content)
            }
        except Exception as e:
            raise APIError(f"Failed to write file: {e}", tool_name=self.tool_name)
