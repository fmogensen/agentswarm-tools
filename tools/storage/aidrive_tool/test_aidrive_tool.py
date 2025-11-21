"""Tests for aidrive_tool tool."""

import pytest
import os
import base64
from unittest.mock import patch

from tools.storage.aidrive_tool import AidriveTool
from shared.errors import ValidationError, APIError


class TestAidriveTool:
    """Test suite for AidriveTool."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def list_tool(self) -> AidriveTool:
        """Tool instance for listing files."""
        return AidriveTool(input="list")

    @pytest.fixture
    def upload_tool(self) -> AidriveTool:
        """Tool instance for upload."""
        return AidriveTool(input="upload testdata")

    @pytest.fixture
    def download_tool(self) -> AidriveTool:
        """Tool instance for download."""
        return AidriveTool(input="download filename.txt")

    @pytest.fixture
    def compress_tool(self) -> AidriveTool:
        """Tool instance for compress."""
        return AidriveTool(input="compress some text")

    # ========== HAPPY PATH ==========

    def test_metadata_correct(self, list_tool: AidriveTool):
        """Test tool metadata values."""
        assert list_tool.tool_name == "aidrive_tool"
        assert list_tool.tool_category == "storage"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    @pytest.mark.parametrize(
        "operation", ["list", "upload test", "download file", "compress text"]
    )
    def test_mock_mode(self, operation: str):
        """Mock mode should return mock data for all operations."""
        tool = AidriveTool(input=operation)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_list_operation_success(self, list_tool: AidriveTool, tmp_path):
        """Test list mode lists files."""
        storage = tmp_path / "aidrive_storage"
        storage.mkdir()
        (storage / "a.txt").write_text("x")
        (storage / "b.txt").write_text("y")

        with patch("os.path.exists", return_value=True), patch(
            "os.listdir", return_value=["a.txt", "b.txt"]
        ):
            result = list_tool.run()

        assert result["success"] is True
        assert result["result"] == ["a.txt", "b.txt"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_upload_operation_success(self, upload_tool: AidriveTool, tmp_path):
        """Test upload writes file."""
        storage = tmp_path / "aidrive_storage"
        with patch("os.makedirs"), patch("os.listdir", return_value=[]), patch(
            "builtins.open", create=True
        ):
            result = upload_tool.run()

        assert result["success"] is True
        assert "uploaded" in result["result"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_download_operation_success(self, tmp_path, download_tool: AidriveTool):
        """Test file download returns base64."""
        storage_dir = tmp_path / "aidrive_storage"
        storage_dir.mkdir()
        file_path = storage_dir / "filename.txt"
        file_path.write_bytes(b"hello")

        with patch("os.path.exists", return_value=True), patch(
            "builtins.open",
            create=True,
            side_effect=lambda *args, **kw: open(file_path, "rb"),
        ):
            result = download_tool.run()

        assert result["success"] is True
        decoded = base64.b64decode(result["result"])
        assert decoded == b"hello"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_compress_operation_success(self, compress_tool: AidriveTool):
        """Test gzip compression returns base64."""
        result = compress_tool.run()
        assert result["success"] is True
        decoded = base64.b64decode(result["result"])
        assert decoded.startswith(b"\x1f\x8b")  # gzip signature

    # ========== ERROR CASES ==========

    @pytest.mark.parametrize("bad_input", ["", "   ", 123, None])
    def test_validation_invalid_inputs(self, bad_input):
        """Invalid input values should raise ValidationError."""
        with pytest.raises(ValidationError):
            tool = AidriveTool(input=bad_input)
            tool.run()

    def test_validation_invalid_operation(self):
        """Non-recognized operation should raise ValidationError."""
        with pytest.raises(ValidationError):
            tool = AidriveTool(input="invalidop something")
            tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_upload_missing_argument(self):
        with pytest.raises(ValidationError):
            AidriveTool(input="upload").run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_download_missing_argument(self):
        with pytest.raises(ValidationError):
            AidriveTool(input="download").run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_compress_missing_argument(self):
        with pytest.raises(ValidationError):
            AidriveTool(input="compress").run()

    def test_api_error_propagates(self, list_tool: AidriveTool):
        with patch.object(list_tool, "_process", side_effect=Exception("boom")):
            with pytest.raises(APIError):
                list_tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_download_file_not_found(self, download_tool: AidriveTool):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(ValidationError):
                download_tool.run()

    # ========== EDGE CASES ==========

    @pytest.mark.parametrize("text", ["unicode äöü", "symbols !@#$%^&*", "a" * 2000])
    def test_compress_edge_cases(self, text):
        tool = AidriveTool(input=f"compress {text}")
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED ==========

    @pytest.mark.parametrize(
        "operation,arg,should_pass",
        [
            ("list", None, True),
            ("upload", "abc", True),
            ("upload", None, False),
            ("download", "file.txt", True),
            ("download", None, False),
            ("compress", "text", True),
            ("compress", None, False),
        ],
    )
    def test_operation_parameter_validation(self, operation, arg, should_pass):
        input_value = operation if arg is None else f"{operation} {arg}"

        if should_pass:
            tool = AidriveTool(input=input_value)
            assert isinstance(tool, AidriveTool)
        else:
            with pytest.raises(ValidationError):
                tool = AidriveTool(input=input_value)
                tool.run()


# ========== INTEGRATION TESTS ==========


class TestAidriveToolIntegration:
    """Integration-level tests."""

    def test_run_integration_smoke(self):
        tool = AidriveTool(input="list")
        result = tool.run()
        assert "success" in result

    def test_error_formatting_integration(self):
        tool = AidriveTool(input="list")

        with patch.object(tool, "_execute", side_effect=ValueError("X")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
