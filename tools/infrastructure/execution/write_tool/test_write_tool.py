"""Tests for write_tool tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
import os
from pydantic import ValidationError as PydanticValidationError

from tools.code_execution.write_tool import WriteTool
from shared.errors import ValidationError, APIError


class TestWriteTool:
    """Test suite for WriteTool."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_file_path(self) -> str:
        return "/tmp/test.txt"

    @pytest.fixture
    def valid_content(self) -> str:
        return "hello world"

    @pytest.fixture
    def tool(self, valid_file_path: str, valid_content: str) -> WriteTool:
        return WriteTool(file_path=valid_file_path, content=valid_content)

    @pytest.fixture
    def tmp_dir(self, tmp_path):
        return tmp_path

    # ========== INITIALIZATION ==========

    def test_tool_metadata(self, tool: WriteTool):
        assert tool.tool_name == "write_tool"
        assert tool.tool_category == "code_execution"

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tmp_dir):
        path = str(tmp_dir / "out.txt")
        tool = WriteTool(file_path=path, content="data")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["written"] is True
        assert os.path.exists(path)

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock_results(self):
        tool = WriteTool(file_path="/tmp/test.txt", content="hello")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode_runs_process(self, valid_file_path: str, valid_content: str):
        tool = WriteTool(file_path=valid_file_path, content=valid_content)
        with patch.object(tool, "_process", return_value={"written": True}) as mock_proc:
            result = tool.run()

        assert mock_proc.called
        assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    def test_empty_file_path_raises_pydantic_error(self):
        """Empty file_path is caught by Pydantic min_length or tool validation."""
        # The tool itself validates empty paths
        tool = WriteTool(file_path="   ", content="data")
        result = tool.run()
        assert result["success"] is False

    def test_missing_file_path_raises_pydantic_error(self):
        """Missing file_path raises Pydantic validation error."""
        with pytest.raises(PydanticValidationError):
            WriteTool(content="data")

    def test_missing_content_raises_pydantic_error(self):
        """Missing content raises Pydantic validation error."""
        with pytest.raises(PydanticValidationError):
            WriteTool(file_path="/tmp/test.txt")

    # ========== API ERROR ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_process_raises_api_error(self, valid_file_path: str, valid_content: str):
        tool = WriteTool(file_path=valid_file_path, content=valid_content)
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            result = tool.run()
            assert result["success"] is False

    # ========== _VALIDATE_PARAMETERS DIRECT TESTING ==========

    def test_validate_parameters_success(self, tool: WriteTool):
        tool._validate_parameters()  # Should not raise

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_unicode_content(self, tmp_dir):
        path = str(tmp_dir / "unicode.txt")
        content = "こんにちは世界"
        tool = WriteTool(file_path=path, content=content)
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["bytes_written"] == len(content)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_nested_directories_created(self, tmp_dir):
        nested_path = str(tmp_dir / "a/b/c.txt")
        tool = WriteTool(file_path=nested_path, content="ok")
        result = tool.run()

        assert result["success"] is True
        assert os.path.exists(nested_path)

    # ========== PARAMETRIZED TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @pytest.mark.parametrize(
        "content", ["", " ", "special chars !@#$%^&*()", "12345", "line1\nline2"]
    )
    def test_various_contents(self, tmp_dir, content):
        path = str(tmp_dir / "file.txt")
        tool = WriteTool(file_path=path, content=content)
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["bytes_written"] == len(content)

    # ========== FAILURE SIMULATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_os_error_during_write(self, valid_file_path: str, valid_content: str):
        tool = WriteTool(file_path=valid_file_path, content=valid_content)
        with patch("builtins.open", side_effect=OSError("disk error")):
            result = tool.run()
            assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_integration_basic_write(self, tmp_dir):
        path = str(tmp_dir / "integration.txt")
        tool = WriteTool(file_path=path, content="integration")
        result = tool.run()

        assert result["success"] is True
        with open(path) as f:
            assert f.read() == "integration"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_integration_error_formatting(self, valid_file_path: str, valid_content: str):
        tool = WriteTool(file_path=valid_file_path, content=valid_content)
        with patch.object(tool, "_execute", side_effect=ValueError("bad")):
            output = tool.run()

        assert output["success"] is False or "error" in output
