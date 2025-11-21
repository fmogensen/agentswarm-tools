"""Tests for read_tool tool."""

import pytest
import os
from unittest.mock import patch, MagicMock

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
        return ReadTool(input=os.path.basename(tmp_file))

    @pytest.fixture
    def run_in_tmpdir(self, monkeypatch, tmp_path):
        """Ensure working dir is tmp_path so relative paths work."""
        monkeypatch.chdir(tmp_path)
        return tmp_path

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization_success(self, tmp_file):
        tool = ReadTool(input=os.path.basename(tmp_file))
        assert tool.input == os.path.basename(tmp_file)
        assert tool.tool_name == "read_tool"
        assert tool.tool_category == "code_execution"
        assert (
            tool.tool_description
            == "Read files from sandboxed environment with line numbers"
        )

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool, tmp_file, run_in_tmpdir):
        result = tool.run()
        assert result["success"] is True
        assert isinstance(result["result"], list)
        assert result["metadata"]["path"] == tool.input
        assert result["metadata"]["tool_name"] == "read_tool"
        assert result["result"][0] == "1: line1"

    def test_line_numbering_correct(self, tool, tmp_file, run_in_tmpdir):
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
    def test_real_mode_runs_process(self, tool, tmp_file, run_in_tmpdir):
        result = tool.run()
        assert result["success"] is True

    # ========== ERROR CASE TESTS ==========

    @pytest.mark.parametrize("bad_input", ["", None, 123])
    def test_invalid_input_type_or_empty(self, bad_input):
        with pytest.raises(ValidationError):
            tool = ReadTool(input=bad_input)
            tool.run()

    @pytest.mark.parametrize("bad_path", ["../secret.txt", "/absolute/path.txt"])
    def test_directory_traversal_rejected(self, bad_path):
        with pytest.raises(ValidationError):
            tool = ReadTool(input=bad_path)
            tool.run()

    def test_file_not_found_raises_api_error(self, tool, run_in_tmpdir):
        tool.input = "nonexistent.txt"
        with pytest.raises(APIError):
            tool.run()

    def test_input_is_directory_raises_api_error(self, tool, tmp_path, run_in_tmpdir):
        os.makedirs("somedir", exist_ok=True)
        tool.input = "somedir"
        with pytest.raises(APIError):
            tool.run()

    def test_process_error_propagates_as_api_error(self, tool, run_in_tmpdir):
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            with pytest.raises(APIError) as exc:
                tool.run()
            assert "boom" in str(exc.value)

    # ========== EDGE CASES ==========

    def test_empty_file(self, tmp_path, run_in_tmpdir):
        p = tmp_path / "empty.txt"
        p.write_text("", encoding="utf-8")
        tool = ReadTool(input="empty.txt")
        result = tool.run()
        assert result["result"] == []

    def test_unicode_file_contents(self, tmp_path, run_in_tmpdir):
        p = tmp_path / "unicode.txt"
        p.write_text("第一行\n第二行", encoding="utf-8")
        tool = ReadTool(input="unicode.txt")
        result = tool.run()
        assert result["result"] == ["1: 第一行", "2: 第二行"]

    def test_special_characters_in_file(self, tmp_path, run_in_tmpdir):
        p = tmp_path / "special.txt"
        p.write_text("@#$%^&*()", encoding="utf-8")
        tool = ReadTool(input="special.txt")
        result = tool.run()
        assert result["result"] == ["1: @#$%^&*()"]

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "filename,expected_valid",
        [
            ("valid.txt", True),
            ("../hack.txt", False),
            ("/abs/path.txt", False),
            ("", False),
        ],
    )
    def test_param_validation(self, filename, expected_valid, tmp_path, run_in_tmpdir):
        if expected_valid:
            (tmp_path / filename).write_text("data", encoding="utf-8")
            tool = ReadTool(input=filename)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = ReadTool(input=filename)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_integration_with_shared_error_formatting(self, tool, run_in_tmpdir):
        with patch.object(tool, "_execute", side_effect=ValueError("oops")):
            result = tool.run()
            assert "success" in result
            assert result.get("success") is False or "error" in result

    def test_integration_environment_mock_off(self, tool, tmp_file, run_in_tmpdir):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "false"}):
            result = tool.run()
            assert result["success"] is True
