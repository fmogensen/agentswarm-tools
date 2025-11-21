"""Tests for bash_tool tool."""

import pytest
from unittest.mock import patch, MagicMock
import subprocess
import os

from tools.code_execution.bash_tool import BashTool
from shared.errors import ValidationError, APIError


class TestBashTool:
    """Test suite for BashTool."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_command(self) -> str:
        return "echo hello"

    @pytest.fixture
    def tool(self, valid_command: str) -> BashTool:
        return BashTool(input=valid_command)

    @pytest.fixture
    def mock_completed_process(self) -> subprocess.CompletedProcess:
        cp = MagicMock()
        cp.stdout = "hello\n"
        cp.stderr = ""
        cp.returncode = 0
        return cp

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization_success(self, valid_command: str):
        tool = BashTool(input=valid_command)
        assert tool.input == valid_command
        assert tool.tool_name == "bash_tool"
        assert tool.tool_category == "code_execution"

    def test_metadata_correct(self, tool: BashTool):
        assert tool.tool_name == "bash_tool"
        assert tool.tool_category == "code_execution"
        assert (
            tool.tool_description
            == "Execute bash commands in sandboxed Linux environment"
        )

    # ========== HAPPY PATH ==========

    @patch("subprocess.run")
    def test_execute_success(self, mock_run, tool: BashTool, mock_completed_process):
        mock_run.return_value = mock_completed_process
        result = tool.run()

        assert result["success"] is True
        assert "stdout" in result["result"]
        assert result["result"]["stdout"] == "hello\n"
        assert result["metadata"]["tool_name"] == "bash_tool"

    @patch("subprocess.run")
    def test_process_called_correctly(
        self, mock_run, tool: BashTool, mock_completed_process
    ):
        mock_run.return_value = mock_completed_process

        tool.run()
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert kwargs["shell"] is True
        assert kwargs["capture_output"] is True

    # ========== MOCK MODE TESTS ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock_results(self, tool: BashTool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "MOCK: Executed" in result["result"]["stdout"]

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    @patch("subprocess.run")
    def test_real_mode_process(self, mock_run, tool: BashTool, mock_completed_process):
        mock_run.return_value = mock_completed_process
        result = tool.run()
        assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_input", ["", "   "])
    def test_empty_input_raises_validation_error(self, bad_input: str):
        with pytest.raises(ValidationError):
            tool = BashTool(input=bad_input)
            tool.run()

    @pytest.mark.parametrize(
        "forbidden", ["rm -rf", "shutdown", "reboot", ":(){:|:&};:"]
    )
    def test_forbidden_commands_raise_error(self, forbidden: str):
        with pytest.raises(ValidationError):
            tool = BashTool(input=f"{forbidden} /tmp/test")
            tool.run()

    # ========== API ERROR TESTING ==========

    @patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="x", timeout=20))
    def test_timeout_raises_api_error(self, mock_run, tool: BashTool):
        with pytest.raises(APIError):
            tool.run()

    @patch("subprocess.run", side_effect=Exception("boom"))
    def test_execution_exception_raises_api_error(self, mock_run, tool: BashTool):
        with pytest.raises(APIError):
            tool.run()

    @patch.object(BashTool, "_process", side_effect=Exception("process failed"))
    def test_process_error_propagates(self, mock_proc, tool: BashTool):
        with pytest.raises(APIError):
            tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_input(self):
        tool = BashTool(input="echo 你好")
        assert tool.input == "echo 你好"

    def test_special_characters(self):
        tool = BashTool(input="echo @$%^*(){}[]")
        assert tool.input == "echo @$%^*(){}[]"

    def test_max_length_input(self):
        long_cmd = "a" * 5000
        tool = BashTool(input=long_cmd)
        assert tool.input == long_cmd

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "input_value, expected_valid",
        [
            ("echo hi", True),
            ("a" * 5000, True),
            ("", False),
            ("   ", False),
            ("rm -rf /", False),
        ],
    )
    def test_parameter_validation(self, input_value: str, expected_valid: bool):
        if expected_valid:
            tool = BashTool(input=input_value)
            assert tool.input == input_value
        else:
            with pytest.raises(Exception):
                tool = BashTool(input=input_value)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch("subprocess.run")
    def test_integration_full_flow(self, mock_run, mock_completed_process):
        mock_run.return_value = mock_completed_process
        tool = BashTool(input="echo integration")
        result = tool.run()

        assert result["success"] is True
        assert "stdout" in result["result"]

    @patch.object(BashTool, "_execute", side_effect=ValueError("test error"))
    def test_base_error_handling_integration(self, mock_exec, tool: BashTool):
        result = tool.run()
        assert "error" in result or result.get("success") is False
