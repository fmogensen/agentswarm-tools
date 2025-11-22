"""Tests for read_tool tool."""

import pytest
import os
from unittest.mock import patch, MagicMock
from pydantic import ValidationError as PydanticValidationError

from tools.code_execution.read_tool import ReadTool
from shared.errors import ValidationError, APIError


class TestReadTool:
    """Test suite for ReadTool."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def tmp_file(self, tmp_path):
        """Create a temporary file with known content."""
        p = tmp_path / "sample.txt"
        p.write_text("line1\nline2\nline3", encoding="utf-8")
        return str(p)

    @pytest.fixture
    def tool(self, tmp_file) -> ReadTool:
        """Create tool instance with valid parameters."""
        return ReadTool(file_path=tmp_file)

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization_success(self, tmp_file):
        tool = ReadTool(file_path=tmp_file)
        assert tool.file_path == tmp_file
        assert tool.tool_name == "read_tool"
        assert tool.tool_category == "code_execution"

    # ========== HAPPY PATH TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert isinstance(result["result"], list)
        assert result["metadata"]["path"] == tool.file_path
        assert result["metadata"]["tool_name"] == "read_tool"
        assert result["result"][0] == "1: line1"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_line_numbering_correct(self, tool):
        result = tool.run()
        assert result["result"] == [
            "1: line1",
            "2: line2",
            "3: line3",
        ]

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert len(result["result"]) == 3

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode_runs_process(self, tool):
        result = tool.run()
        assert result["success"] is True

    # ========== ERROR CASE TESTS ==========

    @pytest.mark.parametrize("bad_input", [None, 123])
    def test_invalid_input_type(self, bad_input):
        with pytest.raises(PydanticValidationError):
            ReadTool(file_path=bad_input)

    def test_missing_file_path_raises_pydantic_error(self):
        with pytest.raises(PydanticValidationError):
            ReadTool()

    def test_directory_traversal_rejected(self):
        tool = ReadTool(file_path="../secret.txt")
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_file_not_found_raises_api_error(self, tmp_path):
        tool = ReadTool(file_path=str(tmp_path / "nonexistent.txt"))
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_input_is_directory_raises_api_error(self, tmp_path):
        tool = ReadTool(file_path=str(tmp_path))
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_process_error_propagates_as_api_error(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.txt"
        p.write_text("", encoding="utf-8")
        tool = ReadTool(file_path=str(p))
        result = tool.run()
        assert result["success"] is True
        assert result["result"] == []

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_unicode_file_contents(self, tmp_path):
        p = tmp_path / "unicode.txt"
        p.write_text("第一行\n第二行", encoding="utf-8")
        tool = ReadTool(file_path=str(p))
        result = tool.run()
        assert result["result"] == ["1: 第一行", "2: 第二行"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_special_characters_in_file(self, tmp_path):
        p = tmp_path / "special.txt"
        p.write_text("@#$%^&*()", encoding="utf-8")
        tool = ReadTool(file_path=str(p))
        result = tool.run()
        assert result["result"] == ["1: @#$%^&*()"]

    # ========== PARAMETRIZED TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @pytest.mark.parametrize(
        "filename,expected_valid",
        [
            ("valid.txt", True),
            ("../hack.txt", False),
        ],
    )
    def test_param_validation(self, filename, expected_valid, tmp_path):
        if expected_valid:
            p = tmp_path / filename
            p.write_text("data", encoding="utf-8")
            tool = ReadTool(file_path=str(p))
            result = tool.run()
            assert result["success"] is True
        else:
            tool = ReadTool(file_path=filename)
            result = tool.run()
            assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    def test_integration_with_shared_error_formatting(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("oops")):
            result = tool.run()
            assert "success" in result
            assert result.get("success") is False or "error" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_integration_environment_mock_off(self, tool):
        result = tool.run()
        assert result["success"] is True
