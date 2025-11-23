"""Tests for multiedit_tool tool."""

import json
import os
from typing import Any, Dict
from unittest.mock import patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.code_execution.multiedit_tool import MultieditTool


class TestMultieditTool:
    """Test suite for MultieditTool."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def sample_file(tmp_path) -> str:
        """Create a temporary file with sample content."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("line1\nline2\nline3\n", encoding="utf-8")
        return str(file_path)

    @pytest.fixture
    def valid_input(self, sample_file: str) -> str:
        """Valid JSON input for the tool."""
        data = {
            "file_path": sample_file,
            "edits": [
                {"action": "replace", "search": "line2", "replace": "LINE2"},
                {"action": "insert", "line": 1, "text": "inserted"},
                {"action": "delete", "line": 0},
            ],
        }
        return json.dumps(data)

    @pytest.fixture
    def tool(self, valid_input: str) -> MultieditTool:
        """Create tool instance."""
        return MultieditTool(input=valid_input)

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: MultieditTool, sample_file: str):
        """Test successful execution."""
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        content = open(sample_file, "r", encoding="utf-8").read()
        assert "LINE2" in content
        assert "inserted" in content
        assert "line1" not in content

    def test_metadata_correct(self, tool: MultieditTool):
        """Test tool metadata."""
        assert tool.tool_name == "multiedit_tool"
        assert tool.tool_category == "code_execution"

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: MultieditTool):
        """Test mock mode returns mock data."""
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["metadata"]["mock_mode"] is True

    # ========== VALIDATION ERROR CASES ==========

    def test_empty_input_raises_error(self):
        tool = MultieditTool(input="   ")
        result = tool.run()
        assert result["success"] is False

    def test_invalid_json_raises_error(self):
        tool = MultieditTool(input="{bad_json")
        result = tool.run()
        assert result["success"] is False

    @pytest.mark.parametrize(
        "bad_data",
        [
            {},  # missing fields
            {"file_path": 123, "edits": []},
            {"file_path": "/tmp/file", "edits": "not_list"},
            {"file_path": "/tmp/file", "edits": [{}]},  # missing action
        ],
    )
    def test_invalid_structure_raises_error(self, bad_data):
        tool = MultieditTool(input=json.dumps(bad_data))
        result = tool.run()
        assert result["success"] is False

    def test_invalid_insert_line_index(self, sample_file: str):
        data = {
            "file_path": sample_file,
            "edits": [{"action": "insert", "line": -1, "text": "bad"}],
        }
        tool = MultieditTool(input=json.dumps(data))
        result = tool.run()
        assert result["success"] is False

    def test_invalid_delete_line_index(self, sample_file: str):
        data = {"file_path": sample_file, "edits": [{"action": "delete", "line": -5}]}
        tool = MultieditTool(input=json.dumps(data))
        result = tool.run()
        assert result["success"] is False

    def test_unknown_action_raises_error(self, sample_file: str):
        data = {"file_path": sample_file, "edits": [{"action": "unknown"}]}
        tool = MultieditTool(input=json.dumps(data))
        result = tool.run()
        assert result["success"] is False

    def test_missing_file_raises_api_error(self, tmp_path):
        missing_file = str(tmp_path / "missing.txt")
        data = {"file_path": missing_file, "edits": []}
        tool = MultieditTool(input=json.dumps(data))
        result = tool.run()
        assert result["success"] is False

    def test_api_error_from_process(self, tool: MultieditTool):
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    def test_insert_beyond_end_appends(self, sample_file: str):
        data = {
            "file_path": sample_file,
            "edits": [{"action": "insert", "line": 99, "text": "end"}],
        }
        tool = MultieditTool(input=json.dumps(data))
        tool.run()
        content = open(sample_file, "r", encoding="utf-8").read()
        assert "end" in content

    def test_delete_out_of_range_silent(self, sample_file: str):
        data = {"file_path": sample_file, "edits": [{"action": "delete", "line": 99}]}
        tool = MultieditTool(input=json.dumps(data))
        tool.run()
        content = open(sample_file, "r", encoding="utf-8").read()
        assert "line1" in content  # unchanged

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "action,edit",
        [
            ("replace", {"action": "replace", "search": "line1", "replace": "X"}),
            ("insert", {"action": "insert", "line": 0, "text": "X"}),
            ("delete", {"action": "delete", "line": 1}),
        ],
    )
    def test_all_actions(self, sample_file: str, action: str, edit: Dict[str, Any]):
        data = {"file_path": sample_file, "edits": [edit]}
        tool = MultieditTool(input=json.dumps(data))
        result = tool.run()
        assert result["success"] is True

    # ========== INTEGRATION TESTS ==========

    def test_error_formatting_integration(self, tool: MultieditTool):
        with patch.object(tool, "_execute", side_effect=ValueError("bad")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
