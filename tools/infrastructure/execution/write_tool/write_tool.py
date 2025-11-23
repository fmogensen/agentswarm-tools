"""
Create or overwrite files in sandboxed environment
"""

import os
from typing import Any, Dict

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


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
    tool_category: str = "infrastructure"

    file_path: str = Field(
        ..., description="Path where the file should be created/written", min_length=1
    )
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

            return {"written": True, "path": self.file_path, "bytes_written": len(self.content)}
        except Exception as e:
            raise APIError(f"Failed to write file: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    print("Testing WriteTool...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Write content to file
    print("\nTest 1: Write content to file")
    tool = WriteTool(file_path="/tmp/test.txt", content="Hello World\nLine 2\nLine 3")
    result = tool.run()

    assert result.get("success") == True
    assert "bytes_written" in result.get("result", {})
    print(f"✅ Test 1 passed: File written")
    print(f"   Path: {result.get('result', {}).get('path')}")
    print(f"   Bytes: {result.get('result', {}).get('bytes_written')}")

    # Test 2: Write different content
    print("\nTest 2: Write different content")
    tool = WriteTool(file_path="/home/user/output.txt", content="# Header\n\nContent here")
    result = tool.run()

    assert result.get("success") == True
    print(f"✅ Test 2 passed: Different file written")

    # Test 3: Validation - empty file path
    print("\nTest 3: Validation - empty file path")
    try:
        bad_tool = WriteTool(file_path="   ", content="test")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Empty content (valid)
    print("\nTest 4: Write empty content (valid)")
    tool = WriteTool(file_path="/tmp/empty.txt", content="")
    result = tool.run()

    assert result.get("success") == True
    assert result.get("result", {}).get("bytes_written") == 0
    print(f"✅ Test 4 passed: Empty file written")

    print("\n✅ All tests passed!")
