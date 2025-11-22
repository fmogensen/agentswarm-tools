"""Tests for onedrive_file_read tool."""

import pytest
import base64
import json
from unittest.mock import patch
from pydantic import ValidationError as PydanticValidationError

from tools.storage.onedrive_file_read import OnedriveFileRead
from shared.errors import ValidationError, APIError


class TestOnedriveFileRead:
    """Test suite for OnedriveFileRead."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def simple_content(self) -> str:
        return "This is sample file content for testing."

    @pytest.fixture
    def encoded_content(self, simple_content: str) -> str:
        return base64.b64encode(simple_content.encode()).decode()

    @pytest.fixture
    def valid_input_json(self, encoded_content: str) -> str:
        return json.dumps(
            {"query": "sample", "file_reference": {"base64_content": encoded_content}}
        )

    @pytest.fixture
    def tool(self, valid_input_json: str) -> OnedriveFileRead:
        return OnedriveFileRead(input=valid_input_json)

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool: OnedriveFileRead):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result

    def test_metadata_correct(self, tool: OnedriveFileRead):
        assert tool.tool_name == "onedrive_file_read"
        assert tool.tool_category == "storage"
        assert "process" in tool.tool_description.lower()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_process_decodes_content(self, tool: OnedriveFileRead, simple_content: str):
        result = tool.run()
        assert result["success"] is True
        assert simple_content[:10] in result["result"]["file_content_excerpt"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_question_answering_positive(self, encoded_content: str):
        input_json = json.dumps(
            {"query": "sample", "file_reference": {"base64_content": encoded_content}}
        )
        tool = OnedriveFileRead(input=input_json)
        result = tool.run()
        assert result["success"] is True
        assert "contains" in result["result"]["answer"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_question_answering_negative(self, encoded_content: str):
        input_json = json.dumps(
            {
                "query": "missingword",
                "file_reference": {"base64_content": encoded_content},
            }
        )
        tool = OnedriveFileRead(input=input_json)
        result = tool.run()
        assert result["success"] is True
        assert "does not" in result["result"]["answer"]

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: OnedriveFileRead):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    # ========== VALIDATION TESTS ==========

    def test_empty_input_raises_error(self):
        tool = OnedriveFileRead(input="")
        result = tool.run()
        assert result["success"] is False

    def test_invalid_json_raises_error(self):
        tool = OnedriveFileRead(input="not valid json")
        result = tool.run()
        assert result["success"] is False

    def test_missing_required_keys_raises_error(self):
        bad_json = json.dumps({"foo": "bar"})
        tool = OnedriveFileRead(input=bad_json)
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_missing_file_reference_raises_error(self):
        good_json = json.dumps({"query": "test"})
        tool = OnedriveFileRead(input=good_json)
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_missing_base64_field_raises_error(self):
        bad_json = json.dumps({"query": "test", "file_reference": {}})
        tool = OnedriveFileRead(input=bad_json)
        result = tool.run()
        assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_invalid_base64_raises_api_error(self):
        bad_json = json.dumps(
            {"query": "test", "file_reference": {"base64_content": "%%%NOTBASE64%%%"}}
        )
        tool = OnedriveFileRead(input=bad_json)
        result = tool.run()
        assert result["success"] is False

    # ========== API ERROR TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_from_process(self, tool: OnedriveFileRead):
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_unicode_query(self, encoded_content: str):
        input_json = json.dumps(
            {
                "query": "ユニコード",
                "file_reference": {"base64_content": encoded_content},
            }
        )
        tool = OnedriveFileRead(input=input_json)
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_empty_query_allowed(self, encoded_content: str):
        input_json = json.dumps(
            {"query": "", "file_reference": {"base64_content": encoded_content}}
        )
        tool = OnedriveFileRead(input=input_json)
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["answer"] is None

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "query,should_pass",
        [
            ("hello", True),
            ("", True),
            (None, True),
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_query_variations(self, query, should_pass: bool, encoded_content: str):
        obj = {"file_reference": {"base64_content": encoded_content}}
        if query is not None:
            obj["query"] = query
        input_json = json.dumps(obj)

        tool = OnedriveFileRead(input=input_json)
        result = tool.run()
        if should_pass:
            assert result["success"] is True
        else:
            assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_full_workflow(self, valid_input_json: str):
        tool = OnedriveFileRead(input=valid_input_json)
        result = tool.run()
        assert result["success"] is True
        assert "file_content_excerpt" in result["result"]

    def test_error_formatting_integration(self, tool: OnedriveFileRead):
        with patch.object(tool, "_execute", side_effect=ValueError("bad error")):
            output = tool.run()
            assert output.get("success") is False or "error" in output
