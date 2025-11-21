"""Tests for query_call_logs tool."""

import pytest
from unittest.mock import patch
from typing import Any, Dict
import os

from tools.communication.query_call_logs import QueryCallLogs
from shared.errors import ValidationError, APIError


class TestQueryCallLogs:
    """Test suite for QueryCallLogs."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        return "inbound"

    @pytest.fixture
    def tool(self, valid_input: str) -> QueryCallLogs:
        return QueryCallLogs(input=valid_input)

    @pytest.fixture
    def mock_logs(self) -> list:
        return [
            {"call_id": "abc123", "direction": "inbound", "transcript": "hello"},
            {"call_id": "xyz789", "direction": "outbound", "transcript": "bye"},
        ]

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self, valid_input: str):
        tool = QueryCallLogs(input=valid_input)
        assert tool.input == valid_input
        assert tool.tool_name == "query_call_logs"
        assert tool.tool_category == "communication"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool: QueryCallLogs):
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert "metadata" in result
        assert "logs" in result["result"]

    def test_filtering_results(self):
        tool = QueryCallLogs(input="xyz")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["count"] <= 1

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: QueryCallLogs):
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["count"] == 5

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: QueryCallLogs):
        result = tool.run()
        assert result["success"] is True

    # ========== VALIDATION TESTS ==========

    def test_empty_input_raises_error(self):
        with pytest.raises(ValidationError):
            QueryCallLogs(input=" ").run()

    @pytest.mark.parametrize("bad_value", [None, 123, {}, [], 3.14])
    def test_invalid_input_type(self, bad_value):
        with pytest.raises(ValidationError):
            QueryCallLogs(input=bad_value).run()

    # ========== API ERROR TESTS ==========

    def test_api_error_raised(self, tool: QueryCallLogs):
        with patch.object(tool, "_process", side_effect=Exception("boom")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASE TESTS ==========

    def test_unicode_input(self):
        tool = QueryCallLogs(input="密码")
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_input(self):
        tool = QueryCallLogs(input="@@@###$$$")
        result = tool.run()
        assert result["success"] is True

    def test_no_matches(self):
        tool = QueryCallLogs(input="nomatchstring")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["count"] == 0

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "query,expected_valid",
        [
            ("abc", True),
            ("inbound", True),
            ("", False),
            ("   ", False),
            (123, False),
        ],
    )
    def test_parameter_validation(self, query, expected_valid):
        if expected_valid:
            tool = QueryCallLogs(input=query)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                QueryCallLogs(input=query).run()

    # ========== INTEGRATION TESTS ==========

    def test_integration_metadata(self, tool: QueryCallLogs):
        result = tool.run()
        assert result["metadata"]["tool_name"] == "query_call_logs"

    def test_integration_error_formatting(self, tool: QueryCallLogs):
        with patch.object(tool, "_execute", side_effect=ValueError("fail")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
