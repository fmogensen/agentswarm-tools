"""Tests for downloadfilewrapper_tool tool."""

import pytest
from unittest.mock import patch, MagicMock
import os

from tools.code_execution.downloadfilewrapper_tool import DownloadfilewrapperTool
from shared.errors import ValidationError, APIError


class TestDownloadfilewrapperTool:
    """Test suite for DownloadfilewrapperTool."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_url(self) -> str:
        return "https://example.com/file.bin"

    @pytest.fixture
    def tool(self, valid_url: str) -> DownloadfilewrapperTool:
        return DownloadfilewrapperTool(input=valid_url)

    @pytest.fixture
    def mock_response(self):
        mock = MagicMock()
        mock.status_code = 200
        mock.content = b"fakebinarydata"
        return mock

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_url: str):
        tool = DownloadfilewrapperTool(input=valid_url)
        assert tool.input == valid_url
        assert tool.tool_name == "downloadfilewrapper_tool"
        assert tool.tool_category == "code_execution"

    # ========== HAPPY PATH TESTS ==========

    @patch("requests.get")
    @patch("builtins.open", new_callable=MagicMock)
    def test_execute_success(self, mock_open, mock_get, tool, mock_response):
        mock_get.return_value = mock_response

        result = tool.run()
        assert result["success"] is True
        assert "sandbox_path" in result["result"]
        assert result["result"]["size_bytes"] == len(mock_response.content)
        mock_open.assert_called()

    def test_metadata_correct(self, tool: DownloadfilewrapperTool):
        assert tool.tool_name == "downloadfilewrapper_tool"
        assert tool.tool_category == "code_execution"

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: DownloadfilewrapperTool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("requests.get")
    def test_real_mode(self, mock_get, tool, mock_response):
        mock_get.return_value = mock_response
        result = tool.run()
        assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_input", [None, "", 123, "ftp://invalid.com"])
    def test_validation_error(self, bad_input):
        with pytest.raises(ValidationError):
            tool = DownloadfilewrapperTool(input=bad_input)
            tool.run()

    # ========== ERROR CASE TESTS ==========

    @patch("requests.get", side_effect=Exception("Network down"))
    def test_process_network_error(self, mock_get, tool):
        with pytest.raises(APIError):
            tool.run()

    @patch("requests.get")
    def test_bad_status_code(self, mock_get, tool):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.content = b""
        mock_get.return_value = mock_resp

        with pytest.raises(APIError):
            tool.run()

    @patch("requests.get")
    @patch("builtins.open", side_effect=Exception("Write failed"))
    def test_write_error(self, mock_open, mock_get, tool, mock_response):
        mock_get.return_value = mock_response
        with pytest.raises(APIError):
            tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_url(self):
        url = "https://example.com/файл.bin"
        tool = DownloadfilewrapperTool(input=url)
        assert tool.input == url

    def test_special_character_url(self):
        url = "https://example.com/file?name=@#$"
        tool = DownloadfilewrapperTool(input=url)
        assert tool.input == url

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "url,should_pass",
        [
            ("https://valid.com/file", True),
            ("http://valid.com/file", True),
            ("invalid://bad", False),
            ("", False),
            (123, False),
        ],
    )
    def test_param_validation(self, url, should_pass):
        if should_pass:
            tool = DownloadfilewrapperTool(input=url)
            assert tool.input == url
        else:
            with pytest.raises(Exception):
                tool = DownloadfilewrapperTool(input=url)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch("requests.get")
    def test_integration_full_flow(self, mock_get, mock_response):
        mock_get.return_value = mock_response
        tool = DownloadfilewrapperTool(input="https://example.com/test.bin")
        result = tool.run()
        assert result["success"] is True
        assert "sandbox_path" in result["result"]

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("boom")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
