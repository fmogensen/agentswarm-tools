"""
Comprehensive unit tests for Storage Tools category.

Tests all storage tools:
- aidrive_tool
- file_format_converter
- onedrive_search
- onedrive_file_read
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from tools.infrastructure.storage.aidrive_tool.aidrive_tool import AIDriveTool
from tools.infrastructure.storage.file_format_converter.file_format_converter import FileFormatConverter
from tools.infrastructure.storage.onedrive_search.onedrive_search import OneDriveSearch
from tools.infrastructure.storage.onedrive_file_read.onedrive_file_read import OneDriveFileRead

from shared.errors import ValidationError, APIError, ResourceNotFoundError


# ========== AIDriveTool Tests ==========


class TestAIDriveTool:
    """Comprehensive tests for AIDriveTool"""

    def test_initialization_success_list(self):
        """Test successful initialization for list action"""
        tool = AIDriveTool(action="list", path="/test")
        assert tool.action == "list"
        assert tool.path == "/test"
        assert tool.tool_name == "aidrive_tool"

    def test_initialization_success_upload(self):
        """Test successful initialization for upload action"""
        tool = AIDriveTool(action="upload", path="/test/file.txt", content="test content")
        assert tool.action == "upload"
        assert tool.path == "/test/file.txt"
        assert tool.content == "test content"

    def test_initialization_success_download(self):
        """Test successful initialization for download action"""
        tool = AIDriveTool(action="download", path="/test/file.txt")
        assert tool.action == "download"
        assert tool.path == "/test/file.txt"

    def test_execute_mock_mode_list(self, monkeypatch):
        """Test list action in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AIDriveTool(action="list", path="/")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_execute_mock_mode_upload(self, monkeypatch):
        """Test upload action in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AIDriveTool(action="upload", path="/test.txt", content="test")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_execute_mock_mode_download(self, monkeypatch):
        """Test download action in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AIDriveTool(action="download", path="/test.txt")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_execute_mock_mode_delete(self, monkeypatch):
        """Test delete action in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AIDriveTool(action="delete", path="/test.txt")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_invalid_action(self):
        """Test validation with invalid action"""
        tool = AIDriveTool(action="invalid", path="/test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_empty_path(self):
        """Test validation with empty path"""
        with pytest.raises(PydanticValidationError):
            AIDriveTool(action="list", path="")

    def test_validate_parameters_upload_missing_content(self):
        """Test validation for upload without content"""
        tool = AIDriveTool(action="upload", path="/test.txt")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.infrastructure.storage.aidrive_tool.aidrive_tool.os.listdir")
    def test_execute_live_mode_list(self, mock_listdir, monkeypatch):
        """Test list action in live mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        mock_listdir.return_value = ["file1.txt", "file2.txt"]

        tool = AIDriveTool(action="list", path="/mnt/aidrive")
        result = tool.run()

        assert result["success"] is True

    @patch("tools.infrastructure.storage.aidrive_tool.aidrive_tool.open", create=True)
    def test_execute_live_mode_upload(self, mock_open, monkeypatch):
        """Test upload action in live mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        tool = AIDriveTool(action="upload", path="/mnt/aidrive/test.txt", content="test content")
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_large_file_path(self, monkeypatch):
        """Test handling of very long file paths"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        long_path = "/test/" + "a" * 200 + ".txt"
        tool = AIDriveTool(action="list", path=long_path)
        result = tool.run()

        assert result["success"] is True


# ========== FileFormatConverter Tests ==========


class TestFileFormatConverter:
    """Comprehensive tests for FileFormatConverter tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = FileFormatConverter(
            source_file="input.pdf", target_format="docx", task_summary="Convert PDF to DOCX"
        )
        assert tool.source_file == "input.pdf"
        assert tool.target_format == "docx"
        assert tool.tool_name == "file_format_converter"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = FileFormatConverter(
            source_file="test.xlsx", target_format="csv", task_summary="Convert Excel to CSV"
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_source(self):
        """Test validation with empty source file"""
        with pytest.raises(PydanticValidationError):
            FileFormatConverter(source_file="", target_format="pdf", task_summary="Test")

    def test_validate_parameters_empty_target_format(self):
        """Test validation with empty target format"""
        with pytest.raises(PydanticValidationError):
            FileFormatConverter(source_file="test.doc", target_format="", task_summary="Test")

    def test_validate_parameters_unsupported_format(self):
        """Test validation with unsupported format"""
        tool = FileFormatConverter(source_file="test.xyz", target_format="abc", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.infrastructure.storage.file_format_converter.file_format_converter.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked conversion API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("CONVERSION_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "converted_file_url": "https://example.com/converted.docx"
        }
        mock_post.return_value = mock_response

        tool = FileFormatConverter(
            source_file="test.pdf", target_format="docx", task_summary="Test"
        )
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_same_format(self, monkeypatch):
        """Test converting to same format"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = FileFormatConverter(source_file="test.pdf", target_format="pdf", task_summary="Test")
        result = tool.run()

        assert result["success"] is True

    def test_supported_conversions(self, monkeypatch):
        """Test various supported conversion types"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        conversions = [
            ("test.pdf", "docx"),
            ("test.xlsx", "csv"),
            ("test.doc", "pdf"),
            ("test.pptx", "pdf"),
            ("test.png", "jpg"),
        ]

        for source, target in conversions:
            tool = FileFormatConverter(
                source_file=source,
                target_format=target,
                task_summary=f"Convert {source} to {target}",
            )
            result = tool.run()
            assert result["success"] is True


# ========== OneDriveSearch Tests ==========


class TestOneDriveSearch:
    """Comprehensive tests for OneDriveSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = OneDriveSearch(query="quarterly report", max_results=10)
        assert tool.query == "quarterly report"
        assert tool.max_results == 10
        assert tool.tool_name == "onedrive_search"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = OneDriveSearch(query="documents", max_results=5)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        with pytest.raises(PydanticValidationError):
            OneDriveSearch(query="")

    def test_validate_parameters_invalid_max_results(self):
        """Test validation with invalid max_results"""
        with pytest.raises(PydanticValidationError):
            OneDriveSearch(query="test", max_results=0)

    @patch("tools.infrastructure.storage.onedrive_search.onedrive_search.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked OneDrive API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("ONEDRIVE_CLIENT_ID", "test_id")
        monkeypatch.setenv("ONEDRIVE_CLIENT_SECRET", "test_secret")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "value": [
                {"name": "document1.docx", "id": "file1"},
                {"name": "document2.pdf", "id": "file2"},
            ]
        }
        mock_get.return_value = mock_response

        tool = OneDriveSearch(query="document", max_results=2)
        result = tool.run()

        assert result["success"] is True

    @patch("tools.infrastructure.storage.onedrive_search.onedrive_search.requests.get")
    def test_api_error_handling_authentication(self, mock_get, monkeypatch):
        """Test handling of authentication errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.delenv("ONEDRIVE_CLIENT_ID", raising=False)

        tool = OneDriveSearch(query="test")
        with pytest.raises(APIError):
            tool.run()

    def test_edge_case_special_characters_in_query(self, monkeypatch):
        """Test handling of special characters in search query"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        special_queries = ["file@name.txt", "folder/subfolder", "item#123", "test & verify"]

        for query in special_queries:
            tool = OneDriveSearch(query=query)
            result = tool.run()
            assert result["success"] is True


# ========== OneDriveFileRead Tests ==========


class TestOneDriveFileRead:
    """Comprehensive tests for OneDriveFileRead tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = OneDriveFileRead(file_id="12345abc")
        assert tool.file_id == "12345abc"
        assert tool.tool_name == "onedrive_file_read"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = OneDriveFileRead(file_id="test123")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_file_id(self):
        """Test validation with empty file ID"""
        with pytest.raises(PydanticValidationError):
            OneDriveFileRead(file_id="")

    @patch("tools.infrastructure.storage.onedrive_file_read.onedrive_file_read.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked OneDrive API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("ONEDRIVE_CLIENT_ID", "test_id")
        monkeypatch.setenv("ONEDRIVE_CLIENT_SECRET", "test_secret")

        mock_response = MagicMock()
        mock_response.content = b"File content here"
        mock_get.return_value = mock_response

        tool = OneDriveFileRead(file_id="file123")
        result = tool.run()

        assert result["success"] is True

    @patch("tools.infrastructure.storage.onedrive_file_read.onedrive_file_read.requests.get")
    def test_api_error_handling_not_found(self, mock_get, monkeypatch):
        """Test handling of file not found errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("ONEDRIVE_CLIENT_ID", "test_id")
        monkeypatch.setenv("ONEDRIVE_CLIENT_SECRET", "test_secret")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not found")
        mock_get.return_value = mock_response

        tool = OneDriveFileRead(file_id="nonexistent")
        with pytest.raises(APIError):
            tool.run()

    def test_edge_case_large_file_id(self, monkeypatch):
        """Test handling of very long file IDs"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        long_id = "a" * 500
        tool = OneDriveFileRead(file_id=long_id)
        result = tool.run()

        assert result["success"] is True

    @patch("tools.infrastructure.storage.onedrive_file_read.onedrive_file_read.requests.get")
    def test_execute_live_mode_binary_file(self, mock_get, monkeypatch):
        """Test reading binary file content"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("ONEDRIVE_CLIENT_ID", "test_id")
        monkeypatch.setenv("ONEDRIVE_CLIENT_SECRET", "test_secret")

        mock_response = MagicMock()
        mock_response.content = b"\x89PNG\r\n\x1a\n"  # PNG header
        mock_get.return_value = mock_response

        tool = OneDriveFileRead(file_id="image123")
        result = tool.run()

        assert result["success"] is True
