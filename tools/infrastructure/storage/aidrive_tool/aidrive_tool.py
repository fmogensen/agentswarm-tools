"""
AI Drive cloud storage management (list, upload, download, compress)
"""

from typing import Any, Dict
from pydantic import Field
import os
import base64
import gzip
import io

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class AidriveTool(BaseTool):
    """
    AI Drive cloud storage management (list, upload, download, compress)

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = AidriveTool(input="list")
        >>> result = tool.run()
    """

    tool_name: str = "aidrive_tool"
    tool_category: str = "infrastructure"

    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the aidrive_tool tool.

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
                "metadata": {"tool_name": self.tool_name, "operation": self.input},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: For invalid input operations
        """
        if not isinstance(self.input, str) or not self.input.strip():
            raise ValidationError(
                "Input must be a non-empty string",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        valid_ops = ["list", "upload", "download", "compress"]
        if not any(self.input.startswith(op) for op in valid_ops):
            raise ValidationError(
                f"Invalid operation. Must start with one of {valid_ops}",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        op = self.input.split()[0]

        mock_data = {
            "list": ["file1.txt", "file2.png", "archive.gz"],
            "upload": "mock_upload_success",
            "download": base64.b64encode(b"mock file content").decode("utf-8"),
            "compress": base64.b64encode(b"mock compressed data").decode("utf-8"),
        }

        return {
            "success": True,
            "result": mock_data.get(op, "mock_default"),
            "metadata": {"mock_mode": True, "operation": op},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Supports:
        - list
        - upload <filepath>
        - download <filename>
        - compress <text>
        """
        parts = self.input.split(maxsplit=1)
        operation = parts[0]
        argument = parts[1] if len(parts) > 1 else None

        if operation == "list":
            return self._list_files()

        if operation == "upload":
            if not argument:
                raise ValidationError(
                    "Upload requires file data string", tool_name=self.tool_name
                )
            return self._upload(argument)

        if operation == "download":
            if not argument:
                raise ValidationError(
                    "Download requires filename", tool_name=self.tool_name
                )
            return self._download(argument)

        if operation == "compress":
            if not argument:
                raise ValidationError(
                    "Compress requires text content", tool_name=self.tool_name
                )
            return self._compress(argument)

        raise APIError("Unknown operation", tool_name=self.tool_name)

    def _list_files(self) -> Any:
        """List files in AI Drive (local mock logic)."""
        storage_dir = "aidrive_storage"
        if not os.path.exists(storage_dir):
            return []
        return os.listdir(storage_dir)

    def _upload(self, data: str) -> Any:
        """Upload base64-encoded text as a file."""
        try:
            storage_dir = "aidrive_storage"
            os.makedirs(storage_dir, exist_ok=True)

            content = data.encode("utf-8")
            filename = f"file_{len(os.listdir(storage_dir)) + 1}.txt"
            path = os.path.join(storage_dir, filename)

            with open(path, "wb") as f:
                f.write(content)

            return {"uploaded": filename}

        except Exception as e:
            raise APIError(f"Upload failed: {e}", tool_name=self.tool_name)

    def _download(self, filename: str) -> Any:
        """Download a file by name and return base64 data."""
        storage_dir = "aidrive_storage"
        path = os.path.join(storage_dir, filename)

        if not os.path.exists(path):
            raise ValidationError(
                "File not found",
                tool_name=self.tool_name,
                details={"filename": filename},
            )

        try:
            with open(path, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode("utf-8")
        except Exception as e:
            raise APIError(f"Download failed: {e}", tool_name=self.tool_name)

    def _compress(self, text: str) -> Any:
        """Compress text using gzip and return base64 encoded result."""
        try:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
                gz.write(text.encode("utf-8"))
            compressed = buf.getvalue()
            return base64.b64encode(compressed).decode("utf-8")
        except Exception as e:
            raise APIError(f"Compression failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = AidriveTool(input="list")
    result = tool.run()
    print(f"Success: {result.get('success')}")
