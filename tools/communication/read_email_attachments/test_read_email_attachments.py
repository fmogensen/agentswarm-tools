"""Tests for read_email_attachments tool."""

import pytest
import os
import json
from unittest.mock import patch, mock_open
from pydantic import ValidationError as PydanticValidationError

from tools.communication.read_email_attachments import ReadEmailAttachments
from shared.errors import ValidationError, APIError


class TestReadEmailAttachments:
    """Test suite for ReadEmailAttachments."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        return json.dumps({"email_id": "abc123"})

    @pytest.fixture
    def tool(self, valid_input: str) -> ReadEmailAttachments:
        return ReadEmailAttachments(input=valid_input)

    @pytest.fixture
    def cache_key(self):
        import hashlib

        return hashlib.sha256("abc123".encode("utf-8")).hexdigest()

    @pytest.fixture
    def cache_path(self, cache_key):
        return f".email_attachment_cache/{cache_key}.json"

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_input):
        tool = ReadEmailAttachments(input=valid_input)
        assert tool.input == valid_input
        assert tool.tool_name == "read_email_attachments"
        assert tool.tool_category == "communication"

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=mock_open)
    def test_execute_new_attachment_fetch(self, mock_file, mock_exists, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["from_cache"] is False
        assert len(result["result"]["attachments"]) == 1
        assert "metadata" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("os.path.exists", return_value=True)
    def test_execute_cache_hit(self, mock_exists, tool, cache_path):
        cached_data = [{"filename": "cached.pdf"}]
        with patch("builtins.open", mock_open(read_data=json.dumps(cached_data))):
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["from_cache"] is True
            assert result["result"]["attachments"] == cached_data

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool):
        with patch("os.path.exists", return_value=False), patch(
            "builtins.open", new_callable=mock_open
        ):
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["from_cache"] is False

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("invalid_input", ["", "   ", "not-json", json.dumps({})])
    def test_invalid_inputs(self, invalid_input):
        tool = ReadEmailAttachments(input=invalid_input)
        result = tool.run()
        assert result["success"] is False

    # ========== ERROR CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_propagates(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("fail")):
            result = tool.run()
            assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    @patch("os.path.exists", return_value=True)
    def test_cache_read_failure(self, mock_exists, tool):
        with patch("builtins.open", side_effect=Exception("read error")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    def test_unicode_email_id(self):
        input_data = json.dumps({"email_id": "邮箱123"})
        tool = ReadEmailAttachments(input=input_data)
        with patch("os.path.exists", return_value=False), patch(
            "builtins.open", new_callable=mock_open
        ):
            result = tool.run()
            assert result["success"] is True

    def test_special_characters_email_id(self):
        input_data = json.dumps({"email_id": "@#$%^&*()!"})
        tool = ReadEmailAttachments(input=input_data)
        with patch("os.path.exists", return_value=False), patch(
            "builtins.open", new_callable=mock_open
        ):
            result = tool.run()
            assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize("email_id", ["a", "long" * 50, "1234567890"])
    def test_various_email_ids(self, email_id):
        tool = ReadEmailAttachments(input=json.dumps({"email_id": email_id}))
        with patch("os.path.exists", return_value=False), patch(
            "builtins.open", new_callable=mock_open
        ):
            result = tool.run()
            assert result["success"] is True

    # ========== INTEGRATION TESTS ==========

    def test_integration_base_run(self, tool):
        with patch("os.path.exists", return_value=False), patch(
            "builtins.open", new_callable=mock_open
        ):
            result = tool.run()
            assert "success" in result

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("boom")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
