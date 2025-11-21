"""
Download file wrapper URLs to sandbox for processing
"""

from typing import Any, Dict
from pydantic import Field
import os
import uuid
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class DownloadfilewrapperTool(BaseTool):
    """
    Download file wrapper URLs to sandbox for processing.

    Args:
        input: Primary input parameter. Must be a valid HTTP/HTTPS URL.

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Dictionary containing downloaded file information
        - metadata: Additional information

    Example:
        >>> tool = DownloadfilewrapperTool(input="https://example.com/file.pdf")
        >>> result = tool.run()
    """

    tool_name: str = "downloadfilewrapper_tool"
    tool_category: str = "code_execution"

    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the downloadfilewrapper_tool tool.

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
                "metadata": {"tool_name": self.tool_name, "input_url": self.input},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters.

        Raises:
            ValidationError: If the input URL is missing or invalid.
        """
        if not self.input or not isinstance(self.input, str):
            raise ValidationError(
                "Input must be a non-empty string",
                tool_name=self.tool_name,
                field="param",
            )

        if not (self.input.startswith("http://") or self.input.startswith("https://")):
            raise ValidationError(
                "Input must be a valid HTTP/HTTPS URL",
                tool_name=self.tool_name,
                field="param",
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
                "sandbox_path": "/sandbox/mock_download.bin",
                "source_url": self.input,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Downloads the file located at the input URL
        and saves it into the sandbox.

        Returns:
            Dict with file metadata

        Raises:
            APIError: If the download fails.
        """
        sandbox_dir = "/sandbox"
        file_id = uuid.uuid4().hex
        filename = f"download_{file_id}"

        output_path = os.path.join(sandbox_dir, filename)

        try:
            response = requests.get(self.input, timeout=30)
        except Exception as e:
            raise APIError(
                f"Network error while downloading: {e}", tool_name=self.tool_name
            )

        if response.status_code != 200:
            raise APIError(
                f"Download failed with status code {response.status_code}",
                tool_name=self.tool_name,
            )

        try:
            with open(output_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            raise APIError(
                f"Failed to write file to sandbox: {e}", tool_name=self.tool_name
            )

        return {
            "sandbox_path": output_path,
            "size_bytes": len(response.content),
            "source_url": self.input,
        }
