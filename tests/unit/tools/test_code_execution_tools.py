"""
Comprehensive unit tests for Code Execution Tools category.

Tests all 5 code execution tools:
- bash_tool (Bash)
- read_tool (Read)
- write_tool (Write)
- multiedit_tool (MultiEdit)
- downloadfilewrapper_tool (DownloadFileWrapper)
"""

import pytest
from unittest.mock import patch, MagicMock, Mock, mock_open
from typing import Dict, Any
import os

from tools.infrastructure.execution.bash_tool.bash_tool import BashTool
from tools.infrastructure.execution.read_tool.read_tool import ReadTool
from tools.infrastructure.execution.write_tool.write_tool import WriteTool
from tools.infrastructure.execution.multiedit_tool.multiedit_tool import MultiEditTool
from tools.infrastructure.execution.downloadfilewrapper_tool.downloadfilewrapper_tool import (
    DownloadFileWrapperTool,
)

from shared.errors import ValidationError, APIError


# ========== BashTool Tests ==========


class TestBashTool:
    """Comprehensive tests for BashTool (Bash command execution)"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = BashTool(command="ls -la")
        assert tool.command == "ls -la"
        assert tool.tool_name == "bash_tool"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = BashTool(command="echo 'Hello World'")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_command(self):
        """Test validation with empty command"""
        tool = BashTool(command="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_whitespace_command(self):
        """Test validation with whitespace only command"""
        tool = BashTool(command="   ")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.infrastructure.execution.bash_tool.bash_tool.subprocess.run")
    def test_execute_live_mode_success(self, mock_run, monkeypatch):
        """Test execution with mocked subprocess"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        mock_result = MagicMock()
        mock_result.stdout = "command output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        tool = BashTool(command="echo test")
        result = tool.run()

        assert result["success"] is True
        mock_run.assert_called_once()

    @patch("tools.infrastructure.execution.bash_tool.bash_tool.subprocess.run")
    def test_execute_live_mode_error(self, mock_run, monkeypatch):
        """Test execution with command error"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "command not found"
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        tool = BashTool(command="invalid_command")
        with pytest.raises(APIError):
            tool.run()

    def test_edge_case_long_command(self, monkeypatch):
        """Test handling of very long commands"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        long_command = "echo " + "x" * 1000
        tool = BashTool(command=long_command)
        result = tool.run()

        assert result["success"] is True

    def test_security_dangerous_commands(self):
        """Test validation of potentially dangerous commands"""
        dangerous_commands = ["rm -rf /", "dd if=/dev/zero of=/dev/sda", ":(){ :|:& };:"]

        for cmd in dangerous_commands:
            tool = BashTool(command=cmd)
            # Should either validate or execute safely in mock mode
            with pytest.raises((ValidationError, APIError)):
                tool._validate_parameters()


# ========== ReadTool Tests ==========


class TestReadTool:
    """Comprehensive tests for ReadTool (File reading)"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ReadTool(file_path="/path/to/file.txt")
        assert tool.file_path == "/path/to/file.txt"
        assert tool.tool_name == "read_tool"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ReadTool(file_path="/test/file.txt")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_path(self):
        """Test validation with empty file path"""
        tool = ReadTool(file_path="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_execute_live_mode_success(self, mock_file, monkeypatch):
        """Test execution with mocked file reading"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        tool = ReadTool(file_path="/test/file.txt")
        result = tool.run()

        assert result["success"] is True
        mock_file.assert_called_once()

    @patch("builtins.open")
    def test_execute_live_mode_file_not_found(self, mock_file, monkeypatch):
        """Test execution with file not found error"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        mock_file.side_effect = FileNotFoundError("File not found")

        tool = ReadTool(file_path="/nonexistent/file.txt")
        with pytest.raises(APIError):
            tool.run()

    def test_edge_case_special_characters_in_path(self, monkeypatch):
        """Test handling of special characters in file path"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        special_paths = [
            "/path/with spaces/file.txt",
            "/path/with-dashes/file.txt",
            "/path/with_underscores/file.txt",
        ]

        for path in special_paths:
            tool = ReadTool(file_path=path)
            result = tool.run()
            assert result["success"] is True


# ========== WriteTool Tests ==========


class TestWriteTool:
    """Comprehensive tests for WriteTool (File writing)"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = WriteTool(file_path="/path/to/file.txt", content="test content")
        assert tool.file_path == "/path/to/file.txt"
        assert tool.content == "test content"
        assert tool.tool_name == "write_tool"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = WriteTool(file_path="/test/output.txt", content="Hello World")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_path(self):
        """Test validation with empty file path"""
        tool = WriteTool(file_path="", content="test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_empty_content(self):
        """Test validation with empty content"""
        tool = WriteTool(file_path="/test.txt", content="")
        # Empty content might be valid for creating empty files
        tool._validate_parameters()  # Should not raise

    @patch("builtins.open", new_callable=mock_open)
    def test_execute_live_mode_success(self, mock_file, monkeypatch):
        """Test execution with mocked file writing"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        tool = WriteTool(file_path="/test/output.txt", content="test content")
        result = tool.run()

        assert result["success"] is True
        mock_file.assert_called_once()

    def test_edge_case_large_content(self, monkeypatch):
        """Test writing large content"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        large_content = "x" * 1000000  # 1MB
        tool = WriteTool(file_path="/test/large.txt", content=large_content)
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_binary_content(self, monkeypatch):
        """Test writing binary content"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        binary_content = bytes([0, 1, 2, 3, 4, 5])
        tool = WriteTool(file_path="/test/binary.dat", content=binary_content)
        result = tool.run()

        assert result["success"] is True


# ========== MultiEditTool Tests ==========


class TestMultiEditTool:
    """Comprehensive tests for MultiEditTool (Multiple file edits)"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        edits = [
            {"file_path": "/file1.txt", "old_text": "old1", "new_text": "new1"},
            {"file_path": "/file2.txt", "old_text": "old2", "new_text": "new2"},
        ]
        tool = MultiEditTool(edits=edits)
        assert len(tool.edits) == 2
        assert tool.tool_name == "multiedit_tool"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        edits = [{"file_path": "/test.txt", "old_text": "hello", "new_text": "world"}]
        tool = MultiEditTool(edits=edits)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_edits(self):
        """Test validation with empty edits list"""
        tool = MultiEditTool(edits=[])
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_edit_format(self):
        """Test validation with invalid edit format"""
        edits = [{"file_path": "/test.txt"}]  # Missing old_text and new_text
        tool = MultiEditTool(edits=edits)
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("builtins.open", new_callable=mock_open, read_data="old text here")
    def test_execute_live_mode_success(self, mock_file, monkeypatch):
        """Test execution with mocked file editing"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        edits = [{"file_path": "/test.txt", "old_text": "old", "new_text": "new"}]
        tool = MultiEditTool(edits=edits)
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_multiple_edits_same_file(self, monkeypatch):
        """Test multiple edits to the same file"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        edits = [
            {"file_path": "/test.txt", "old_text": "a", "new_text": "b"},
            {"file_path": "/test.txt", "old_text": "c", "new_text": "d"},
        ]
        tool = MultiEditTool(edits=edits)
        result = tool.run()

        assert result["success"] is True


# ========== DownloadFileWrapperTool Tests ==========


class TestDownloadFileWrapperTool:
    """Comprehensive tests for DownloadFileWrapperTool (File downloading)"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = DownloadFileWrapperTool(
            url="https://example.com/file.txt", destination="/path/to/save/file.txt"
        )
        assert tool.url == "https://example.com/file.txt"
        assert tool.destination == "/path/to/save/file.txt"
        assert tool.tool_name == "downloadfilewrapper_tool"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = DownloadFileWrapperTool(
            url="https://example.com/test.pdf", destination="/downloads/test.pdf"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty URL"""
        tool = DownloadFileWrapperTool(url="", destination="/test.txt")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = DownloadFileWrapperTool(url="not-a-url", destination="/test.txt")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_empty_destination(self):
        """Test validation with empty destination"""
        tool = DownloadFileWrapperTool(url="https://example.com/file.txt", destination="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.infrastructure.execution.downloadfilewrapper_tool.downloadfilewrapper_tool.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    def test_execute_live_mode_success(self, mock_file, mock_get, monkeypatch):
        """Test execution with mocked download"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        mock_response = MagicMock()
        mock_response.content = b"file content"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        tool = DownloadFileWrapperTool(
            url="https://example.com/file.txt", destination="/downloads/file.txt"
        )
        result = tool.run()

        assert result["success"] is True
        mock_get.assert_called_once()

    @patch("tools.infrastructure.execution.downloadfilewrapper_tool.downloadfilewrapper_tool.requests.get")
    def test_execute_live_mode_download_error(self, mock_get, monkeypatch):
        """Test execution with download error"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not found")
        mock_get.return_value = mock_response

        tool = DownloadFileWrapperTool(
            url="https://example.com/nonexistent.txt", destination="/downloads/file.txt"
        )
        with pytest.raises(APIError):
            tool.run()

    def test_edge_case_large_file_download(self, monkeypatch):
        """Test downloading large file"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = DownloadFileWrapperTool(
            url="https://example.com/large-file.zip", destination="/downloads/large-file.zip"
        )
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_special_characters_in_destination(self, monkeypatch):
        """Test destination path with special characters"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = DownloadFileWrapperTool(
            url="https://example.com/file.txt", destination="/path with spaces/file name.txt"
        )
        result = tool.run()

        assert result["success"] is True
