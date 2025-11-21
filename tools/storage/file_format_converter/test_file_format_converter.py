"""Tests for file_format_converter tool."""

import pytest
from unittest.mock import patch
import base64

from tools.storage.file_format_converter import FileFormatConverter
from shared.errors import ValidationError, APIError


class TestFileFormatConverter:
    """Test suite for FileFormatConverter."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_base64(self):
        return base64.b64encode(b"hello").decode()

    @pytest.fixture
    def valid_input(self, valid_base64):
        return f"txt|pdf|{valid_base64}"

    @pytest.fixture
    def tool(self, valid_input) -> FileFormatConverter:
        return FileFormatConverter(input=valid_input)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_input):
        tool = FileFormatConverter(input=valid_input)
        assert tool.input == valid_input
        assert tool.tool_name == "file_format_converter"
        assert tool.tool_category == "storage"
        assert tool.tool_description == "Convert files between different formats"

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: FileFormatConverter):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert result["result"]["source_format"] == "txt"
        assert result["result"]["target_format"] == "pdf"
        assert "converted_data" in result["result"]

    def test_metadata_correct(self, tool: FileFormatConverter):
        result = tool.run()
        assert result["metadata"]["tool_name"] == "file_format_converter"
        assert result["metadata"]["conversion"] == "file_format_conversion"

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: FileFormatConverter):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool):
        result = tool.run()
        assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize(
        "bad_input",
        [
            "",
            "   ",
            "missing_parts",
            "only|two",
            "txt||abcd",
            "|pdf|abcd",
            "txt|pdf|",
        ],
    )
    def test_invalid_inputs(self, bad_input):
        with pytest.raises(ValidationError):
            tool = FileFormatConverter(input=bad_input)
            tool.run()

    def test_invalid_base64(self):
        bad = "txt|pdf|not_base64!!"
        with pytest.raises(ValidationError):
            tool = FileFormatConverter(input=bad)
            tool.run()

    # ========== ERROR CASES ==========

    def test_api_error(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            with pytest.raises(APIError):
                tool.run()

    # ========== PROCESS TESTS ==========

    def test_process_decoding_encoding(self, tool, valid_base64):
        result = tool._process()
        assert result["converted_data"] == valid_base64

    # ========== EDGE CASES ==========

    def test_unicode_in_data(self):
        encoded = base64.b64encode("ñöç".encode()).decode()
        tool = FileFormatConverter(input=f"txt|bin|{encoded}")
        result = tool.run()
        assert result["success"] is True

    def test_large_base64(self):
        data = base64.b64encode(b"a" * 5000).decode()
        tool = FileFormatConverter(input=f"bin|zip|{data}")
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "src,tgt",
        [
            ("txt", "pdf"),
            ("png", "jpg"),
            ("csv", "json"),
            ("xml", "yaml"),
        ],
    )
    def test_various_format_pairs(self, src, tgt):
        encoded = base64.b64encode(b"abc123").decode()
        tool = FileFormatConverter(input=f"{src}|{tgt}|{encoded}")
        result = tool.run()
        assert result["result"]["source_format"] == src
        assert result["result"]["target_format"] == tgt

    @pytest.mark.parametrize(
        "base",
        [
            base64.b64encode(b"1").decode(),
            base64.b64encode(b"hello world").decode(),
            base64.b64encode(b"\x00\x01\x02").decode(),
        ],
    )
    def test_various_base64_payloads(self, base):
        tool = FileFormatConverter(input=f"txt|bin|{base}")
        result = tool.run()
        assert result["success"] is True

    # ========== INTEGRATION TESTS ==========

    def test_integration_run(self, tool):
        result = tool.run()
        assert result["success"] is True

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("bad error")):
            response = tool.run()
            assert "error" in response or response.get("success") is False
