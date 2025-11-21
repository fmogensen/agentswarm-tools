"""Tests for write_tool tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
import os

from tools.code_execution.write_tool import WriteTool
from shared.errors import ValidationError, APIError


class TestWriteTool:
    """Test suite for WriteTool."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        return '{"path": "tmp/test.txt", "content": "hello world"}'

    @pytest.fixture
    def tool(self, valid_input: str) -> WriteTool:
        return WriteTool(input=valid_input)

    @pytest.fixture
    def tmp_dir(self, tmp_path):
        return tmp_path

    # ========== INITIALIZATION ==========

    def test_tool_metadata(self, tool: WriteTool):
        assert tool.tool_name == "write_tool"
        assert tool.tool_category == "code_execution"

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tmp_dir, valid_input):
        path = tmp_dir / "out.txt"
        tool = WriteTool(input=f'{{"path": "{path}", "content": "data"}}')
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["written"] is True
        assert os.path.exists(path)

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock_results(self, tool: WriteTool):
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode_runs_process(self, tool: WriteTool):
        with patch.object(
            tool, "_process", return_value={"written": True}
        ) as mock_proc:
            result = tool.run()

        assert mock_proc.called
        assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize(
        "bad_input",
        [
            "",
            "   ",
            "not json",
            "[]",
            '{"missing":"keys"}',
            '{"path": "", "content": "data"}',
            '{"path": 123, "content": "data"}',
            '{"path": "file.txt", "content": 123}',
        ],
    )
    def test_invalid_inputs_raise_validation_error(self, bad_input):
        with pytest.raises(ValidationError):
            tool = WriteTool(input=bad_input)
            tool.run()

    # ========== API ERROR ==========

    def test_process_raises_api_error(self, tool: WriteTool):
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            with pytest.raises(APIError):
                tool.run()

    # ========== _VALIDATE_PARAMETERS DIRECT TESTING ==========

    def test_validate_parameters_success(self, tool: WriteTool):
        tool._validate_parameters()  # Should not raise

    # ========== EDGE CASES ==========

    def test_unicode_content(self, tmp_dir):
        path = tmp_dir / "unicode.txt"
        content = "こんにちは世界"
        tool = WriteTool(input=f'{{"path": "{path}", "content": "{content}"}}')
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["bytes_written"] == len(content)

    def test_nested_directories_created(self, tmp_dir):
        nested_path = tmp_dir / "a/b/c.txt"
        tool = WriteTool(input=f'{{"path": "{nested_path}", "content": "ok"}}')
        result = tool.run()

        assert result["success"] is True
        assert nested_path.exists()

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "content", ["", " ", "special chars !@#$%^&*()", "12345", "line1\nline2"]
    )
    def test_various_contents(self, tmp_dir, content):
        path = tmp_dir / "file.txt"
        tool = WriteTool(input=f'{{"path": "{path}", "content": "{content}"}}')
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["bytes_written"] == len(content)

    # ========== FAILURE SIMULATION ==========

    def test_os_error_during_write(self, tool: WriteTool):
        with patch("builtins.open", side_effect=OSError("disk error")):
            with pytest.raises(APIError):
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_integration_basic_write(self, tmp_dir):
        path = tmp_dir / "integration.txt"
        tool = WriteTool(input=f'{{"path": "{path}", "content": "integration"}}')
        result = tool.run()

        assert result["success"] is True
        assert path.read_text() == "integration"

    def test_integration_error_formatting(self, tool: WriteTool):
        with patch.object(tool, "_execute", side_effect=ValueError("bad")):
            output = tool.run()

        assert output["success"] is False or "error" in output
