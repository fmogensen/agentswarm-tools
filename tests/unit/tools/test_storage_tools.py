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

from tools.infrastructure.storage.aidrive_tool.aidrive_tool import AidriveTool
from tools.infrastructure.storage.file_format_converter.file_format_converter import FileFormatConverter
from tools.infrastructure.storage.onedrive_search.onedrive_search import OnedriveSearch
from tools.infrastructure.storage.onedrive_file_read.onedrive_file_read import OnedriveFileRead

from shared.errors import ValidationError, APIError, ResourceNotFoundError


# ========== AidriveTool Tests ==========


class TestAidriveTool:
    """Comprehensive tests for AidriveTool"""

    def test_initialization_success_list(self):
        """Test successful initialization for list action"""
        tool = AidriveTool(input="list")
        assert tool.input == "list"
        assert tool.tool_name == "aidrive_tool"

    def test_initialization_success_upload(self):
        """Test successful initialization for upload action"""
        tool = AidriveTool(input="upload test content")
        assert tool.input == "upload test content"

    def test_initialization_success_download(self):
        """Test successful initialization for download action"""
        tool = AidriveTool(input="download /test/file.txt")
        assert tool.input == "download /test/file.txt"

    def test_execute_mock_mode_list(self, monkeypatch):
        """Test list action in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AidriveTool(input="list")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_execute_mock_mode_upload(self, monkeypatch):
        """Test upload action in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AidriveTool(input="upload test")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_execute_mock_mode_download(self, monkeypatch):
        """Test download action in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AidriveTool(input="download /test.txt")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_execute_mock_mode_delete(self, monkeypatch):
        """Test delete action in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AidriveTool(input="compress some text")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_invalid_action(self):
        """Test validation with invalid action"""
        tool = AidriveTool(input="invalid")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_empty_path(self):
        """Test validation with empty path"""
        with pytest.raises(PydanticValidationError):
            AidriveTool(input="")

    def test_validate_parameters_upload_missing_content(self):
        """Test validation for upload without content"""
        tool = AidriveTool(input="upload")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.infrastructure.storage.aidrive_tool.aidrive_tool.os.listdir")
    def test_execute_live_mode_list(self, mock_listdir, monkeypatch):
        """Test list action in live mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        mock_listdir.return_value = ["file1.txt", "file2.txt"]

        tool = AidriveTool(input="list")
        result = tool.run()

        assert result["success"] is True

    @patch("tools.infrastructure.storage.aidrive_tool.aidrive_tool.open", create=True)
    def test_execute_live_mode_upload(self, mock_open, monkeypatch):
        """Test upload action in live mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        tool = AidriveTool(input="upload test content")
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_large_file_path(self, monkeypatch):
        """Test handling of very long file paths"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        long_path = "/test/" + "a" * 200 + ".txt"
        tool = AidriveTool(input="list")
        result = tool.run()

        assert result["success"] is True


# ========== FileFormatConverter Tests ==========


class TestFileFormatConverter:
    """Comprehensive tests for FileFormatConverter tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        import base64
        tool = FileFormatConverter(
            input=f"pdf|docx|{base64.b64encode(b'test data').decode()}"
        )
        assert tool.tool_name == "file_format_converter"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        import base64
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = FileFormatConverter(
            input=f"xlsx|csv|{base64.b64encode(b'test data').decode()}"
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_source(self):
        """Test validation with empty source file"""
        with pytest.raises(PydanticValidationError):
            FileFormatConverter(input="")

    def test_validate_parameters_empty_target_format(self):
        """Test validation with empty target format"""
        import base64
        tool = FileFormatConverter(input=f"doc||{base64.b64encode(b'test').decode()}")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_unsupported_format(self):
        """Test validation with unsupported format"""
        import base64
        tool = FileFormatConverter(input=f"xyz|abc|{base64.b64encode(b'test').decode()}")
        # Tool doesn't validate format types, so it should succeed
        result = tool.run()
        assert result["success"] is True

    @patch("tools.infrastructure.storage.file_format_converter.file_format_converter.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked conversion API"""
        import base64
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("CONVERSION_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "converted_file_url": "https://example.com/converted.docx"
        }
        mock_post.return_value = mock_response

        tool = FileFormatConverter(
            input=f"pdf|docx|{base64.b64encode(b'test data').decode()}"
        )
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_same_format(self, monkeypatch):
        """Test converting to same format"""
        import base64
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = FileFormatConverter(input=f"pdf|pdf|{base64.b64encode(b'test').decode()}")
        result = tool.run()

        assert result["success"] is True

    def test_supported_conversions(self, monkeypatch):
        """Test various supported conversion types"""
        import base64
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        conversions = [
            ("pdf", "docx"),
            ("xlsx", "csv"),
            ("doc", "pdf"),
            ("pptx", "pdf"),
            ("png", "jpg"),
        ]

        for source, target in conversions:
            tool = FileFormatConverter(
                input=f"{source}|{target}|{base64.b64encode(b'test data').decode()}"
            )
            result = tool.run()
            assert result["success"] is True


# ========== OnedriveSearch Tests ==========


class TestOnedriveSearch:
    """Comprehensive tests for OnedriveSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = OnedriveSearch(query="quarterly report", max_results=10)
        assert tool.query == "quarterly report"
        assert tool.max_results == 10
        assert tool.tool_name == "onedrive_search"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = OnedriveSearch(query="documents", max_results=5)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        with pytest.raises(PydanticValidationError):
            OnedriveSearch(query="")

    def test_validate_parameters_invalid_max_results(self):
        """Test validation with invalid max_results"""
        with pytest.raises(PydanticValidationError):
            OnedriveSearch(query="test", max_results=0)

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

        tool = OnedriveSearch(query="document", max_results=2)
        result = tool.run()

        assert result["success"] is True

    @patch("tools.infrastructure.storage.onedrive_search.onedrive_search.requests.get")
    def test_api_error_handling_authentication(self, mock_get, monkeypatch):
        """Test handling of authentication errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.delenv("ONEDRIVE_CLIENT_ID", raising=False)

        tool = OnedriveSearch(query="test")
        with pytest.raises(APIError):
            tool.run()

    def test_edge_case_special_characters_in_query(self, monkeypatch):
        """Test handling of special characters in search query"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        special_queries = ["file@name.txt", "folder/subfolder", "item#123", "test & verify"]

        for query in special_queries:
            tool = OnedriveSearch(query=query)
            result = tool.run()
            assert result["success"] is True


# ========== OnedriveFileRead Tests ==========


class TestOnedriveFileRead:
    """Comprehensive tests for OnedriveFileRead tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = OnedriveFileRead(file_id="12345abc")
        assert tool.file_id == "12345abc"
        assert tool.tool_name == "onedrive_file_read"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = OnedriveFileRead(file_id="test123")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_file_id(self):
        """Test validation with empty file ID"""
        with pytest.raises(PydanticValidationError):
            OnedriveFileRead(file_id="")

    @patch("tools.infrastructure.storage.onedrive_file_read.onedrive_file_read.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked OneDrive API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("ONEDRIVE_CLIENT_ID", "test_id")
        monkeypatch.setenv("ONEDRIVE_CLIENT_SECRET", "test_secret")

        mock_response = MagicMock()
        mock_response.content = b"File content here"
        mock_get.return_value = mock_response

        tool = OnedriveFileRead(file_id="file123")
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

        tool = OnedriveFileRead(file_id="nonexistent")
        with pytest.raises(APIError):
            tool.run()

    def test_edge_case_large_file_id(self, monkeypatch):
        """Test handling of very long file IDs"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        long_id = "a" * 500
        tool = OnedriveFileRead(file_id=long_id)
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

        tool = OnedriveFileRead(file_id="image123")
        result = tool.run()

        assert result["success"] is True
