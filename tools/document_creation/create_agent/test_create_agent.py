"""Tests for create_agent tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any
import os

from tools.document_creation.create_agent import CreateAgent
from shared.errors import ValidationError, APIError


class TestCreateAgent:
    """Test suite for CreateAgent."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_input(self) -> str:
        return "Create a podcast generator"

    @pytest.fixture
    def tool(self, valid_input: str) -> CreateAgent:
        return CreateAgent(input=valid_input)

    @pytest.fixture
    def mock_env_off(self):
        with patch.dict(os.environ, {"USE_MOCK_APIS": "false"}):
            yield

    @pytest.fixture
    def mock_env_on(self):
        with patch.dict(os.environ, {"USE_MOCK_APIS": "true"}):
            yield

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self, valid_input: str):
        tool = CreateAgent(input=valid_input)
        assert tool.input == valid_input
        assert tool.tool_name == "create_agent"
        assert tool.tool_category == "documents"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool: CreateAgent, mock_env_off):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is False
        assert result["metadata"]["input_length"] == len(tool.input)
        assert result["result"]["status"] == "created"

    @pytest.mark.parametrize(
        "input_text,expected_type",
        [
            ("make a podcast script", "podcast_creator"),
            ("generate doc file", "document_generator"),
            ("slides for meeting", "slide_maker"),
            ("spreadsheet automation", "sheet_builder"),
            ("deep research on AI", "deep_research_agent"),
            ("build a website", "website_builder"),
            ("video editing project", "video_editing_agent"),
            ("random unrelated text", "general_creation_agent"),
        ],
    )
    def test_process_agent_type_mapping(self, input_text, expected_type, mock_env_off):
        tool = CreateAgent(input=input_text)
        result = tool.run()
        assert result["result"]["agent_type"] == expected_type

    # ========== MOCK MODE TESTS ==========

    def test_mock_mode(self, tool: CreateAgent, mock_env_on):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["agent_id"] == "mock-123"

    # ========== VALIDATION TESTS ==========

    def test_empty_input_raises_error(self):
        with pytest.raises(ValidationError):
            CreateAgent(input="").run()

    def test_whitespace_input_raises_error(self):
        with pytest.raises(ValidationError):
            CreateAgent(input="   ").run()

    def test_non_string_input_raises_error(self):
        with pytest.raises(ValidationError):
            CreateAgent(input=123).run()

    # ========== ERROR HANDLING TESTS ==========

    def test_process_raises_api_error(self, tool: CreateAgent):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASE TESTS ==========

    def test_unicode_input(self, mock_env_off):
        tool = CreateAgent(input="创建文档代理")
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_input(self, mock_env_off):
        tool = CreateAgent(input="Create agent @#$%^&*(!)")
        result = tool.run()
        assert result["success"] is True

    def test_max_length_input(self, mock_env_off):
        long_input = "a" * 10000
        tool = CreateAgent(input=long_input)
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED VALIDATION TESTS ==========

    @pytest.mark.parametrize(
        "input_text,valid",
        [
            ("valid text", True),
            ("a" * 10000, True),
            ("", False),
            ("   ", False),
            (123, False),
        ],
    )
    def test_parameter_validation(self, input_text, valid):
        if valid:
            tool = CreateAgent(input=input_text)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                CreateAgent(input=input_text).run()

    # ========== INTERNAL METHOD TESTS ==========

    def test_should_use_mock_true(self, tool: CreateAgent, mock_env_on):
        assert tool._should_use_mock() is True

    def test_should_use_mock_false(self, tool: CreateAgent, mock_env_off):
        assert tool._should_use_mock() is False

    def test_generate_mock_results(self, tool: CreateAgent):
        mock = tool._generate_mock_results()
        assert mock["success"] is True
        assert mock["result"]["agent_id"] == "mock-123"

    def test_process_direct_call(self):
        tool = CreateAgent(input="create website")
        result = tool._process()
        assert result["agent_type"] == "website_builder"


class TestCreateAgentIntegration:
    """Integration tests with BaseTool behavior."""

    def test_error_handling_integration(self):
        tool = CreateAgent(input="valid")
        with patch.object(tool, "_execute", side_effect=ValueError("boom")):
            result = tool.run()
            assert result["success"] is False or "error" in result

    def test_rate_limiting_integration(self):
        tool = CreateAgent(input="rate limit test")
        result = tool.run()
        assert result["success"] is True
