"""
Convert files between different formats
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os
import base64

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class FileFormatConverter(BaseTool):
    """
    Convert files between different formats.

    This tool accepts an input string containing:
    - source_format: The current format of the file
    - target_format: The desired output format
    - file_data: Base64-encoded file contents

    Args:
        input: Primary input parameter containing conversion instructions

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Converted file data (base64 encoded)
        - metadata: Information about the conversion

    Example:
        >>> tool = FileFormatConverter(input="example")
        >>> result = tool.run()
    """

    tool_name: str = "file_format_converter"
    tool_category: str = "infrastructure"
    tool_description: str = "Convert files between different formats"

    input: str = Field(..., description="Primary input parameter", min_length=1)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the file_format_converter tool.

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
                "metadata": {
                    "tool_name": self.tool_name,
                    "conversion": "file_format_conversion",
                },
            }

        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError
        """
        if not self.input or not self.input.strip():
            raise ValidationError(
                "Input cannot be empty.",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        if "|" not in self.input:
            raise ValidationError(
                "Input must contain source_format|target_format|base64_data",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        parts = self.input.split("|")
        if len(parts) != 3:
            raise ValidationError(
                "Input must have exactly 3 parts: source_format|target_format|file_data",
                tool_name=self.tool_name,
                details={"input_parts": parts},
            )

        src, tgt, data = parts

        if not src or not tgt:
            raise ValidationError(
                "Source and target format cannot be empty.",
                tool_name=self.tool_name,
                details={"src": src, "tgt": tgt},
            )

        if not data:
            raise ValidationError(
                "File data cannot be empty.",
                tool_name=self.tool_name,
                details={"data": data},
            )

        try:
            base64.b64decode(data)
        except Exception:
            raise ValidationError("File data must be valid Base64.", tool_name=self.tool_name)

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "mock": True,
                "converted_data": base64.b64encode(b"mock data").decode(),
            },
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        The real implementation performs a placeholder 'conversion':
        - decodes the input
        - performs no real format transformation
        - re-encodes the data

        Returns:
            dict with converted file data
        """
        src, tgt, data = self.input.split("|")

        try:
            file_bytes = base64.b64decode(data)
        except Exception:
            raise ValidationError("Invalid Base64 in file data.", tool_name=self.tool_name)

        converted_bytes = file_bytes  # Placeholder for real conversion logic
        converted_base64 = base64.b64encode(converted_bytes).decode()

        return {
            "source_format": src,
            "target_format": tgt,
            "converted_data": converted_base64,
        }


if __name__ == "__main__":
    # Test the tool
    print("Testing FileFormatConverter...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test with mock input
    tool = FileFormatConverter(input="pdf|docx|SGVsbG8gV29ybGQ=")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Result: {result.get('result')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("mock") == True
    print("All tests passed!")
