"""Tests for aidrive_tool tool."""

import pytest
import os
import base64
import io
from unittest.mock import patch, MagicMock, mock_open
from pydantic import ValidationError as PydanticValidationError

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
    def test_download_operation_success(self, download_tool: AidriveTool):
        """Test file download returns base64."""
        mock_data = b"hello"

        with patch("shared.base.get_rate_limiter") as mock_limiter, \
             patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=mock_data)):

            mock_limiter.return_value.check_rate_limit.return_value = None
            result = download_tool.run()

        assert result["success"] is True
        decoded = base64.b64decode(result["result"])
        assert decoded == mock_data

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_compress_operation_success(self, compress_tool: AidriveTool):
        """Test gzip compression returns base64."""
        result = compress_tool.run()
        assert result["success"] is True
        decoded = base64.b64decode(result["result"])
        assert decoded.startswith(b"\x1f\x8b")  # gzip signature

    # ========== ERROR CASES ==========

    @pytest.mark.parametrize("bad_input", [123, None])
    def test_validation_invalid_inputs_type(self, bad_input):
        """Invalid input types should raise PydanticValidationError."""
        with pytest.raises(PydanticValidationError):
            AidriveTool(input=bad_input)

    @pytest.mark.parametrize("bad_input", ["", "   "])
    def test_validation_invalid_inputs_empty(self, bad_input):
        """Empty input values should return error dict."""
        tool = AidriveTool(input=bad_input)
        result = tool.run()
        assert result["success"] is False

    def test_validation_invalid_operation(self):
        """Non-recognized operation should return error dict."""
        tool = AidriveTool(input="invalidop something")
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_upload_missing_argument(self):
        result = AidriveTool(input="upload").run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_download_missing_argument(self):
        result = AidriveTool(input="download").run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_compress_missing_argument(self):
        result = AidriveTool(input="compress").run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_propagates(self, list_tool: AidriveTool):
        with patch.object(list_tool, "_process", side_effect=Exception("boom")):
            result = list_tool.run()
            assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_download_file_not_found(self, download_tool: AidriveTool):
        with patch("os.path.exists", return_value=False):
            result = download_tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    @pytest.mark.parametrize("text", ["unicode äöü", "symbols !@#$%^&*", "a" * 2000])
    def test_compress_edge_cases(self, text):
        tool = AidriveTool(input=f"compress {text}")
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
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
            tool = AidriveTool(input=input_value)
            result = tool.run()
            assert result["success"] is False


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
