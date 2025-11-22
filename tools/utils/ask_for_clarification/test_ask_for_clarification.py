"""Tests for ask_for_clarification tool."""

import pytest
from unittest.mock import patch
from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError

from tools.utils.ask_for_clarification import AskForClarification
from shared.errors import ValidationError, APIError


class TestAskForClarification:
    """Test suite for AskForClarification."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_question(self) -> str:
        return "What is your name?"

    @pytest.fixture
    def tool(self, valid_question: str) -> AskForClarification:
        return AskForClarification(question=valid_question)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization_success(self, valid_question: str):
        tool = AskForClarification(question=valid_question)
        assert tool.question == valid_question
        assert tool.tool_name == "ask_for_clarification"
        assert tool.tool_category == "utils"

    def test_metadata_correct(self, tool: AskForClarification):
        assert (
            tool.tool_description
            == "Request additional information from user when needed"
        )

    # ========== HAPPY PATH TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool: AskForClarification):
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["result"]["awaiting_user_response"] is True
        assert result["result"]["question"] == tool.question
        assert "metadata" in result

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock_results(self, tool: AskForClarification):
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True
        assert result["result"]["question"] == tool.question

    # ========== VALIDATION TESTS ==========

    def test_validation_error_on_empty_question(self):
        # Empty string fails Pydantic min_length=1 at construction
        with pytest.raises(PydanticValidationError):
            AskForClarification(question="")

    def test_validation_error_on_whitespace_question(self):
        # Whitespace passes Pydantic, fails custom validation at runtime
        tool = AskForClarification(question="   ")
        result = tool.run()
        assert result["success"] is False

    def test_validation_error_on_none_question(self):
        with pytest.raises(PydanticValidationError):
            AskForClarification(question=None)

    # ========== ERROR CASE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_propagates(self, tool: AskForClarification):
        with patch.object(tool, "_process", side_effect=Exception("Failure occurred")):
            result = tool.run()
            assert result["success"] is False

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "question", ["Hello?", "¿Cómo estás?", "Name @#$?", "a" * 200]
    )
    def test_valid_questions(self, question):
        tool = AskForClarification(question=question)
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["question"] == question

    # ========== EDGE CASE TESTS ==========

    def test_unicode_characters(self):
        tool = AskForClarification(question="Привет, как дела?")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["question"] == "Привет, как дела?"

    def test_long_question(self):
        long_q = "A" * 500
        tool = AskForClarification(question=long_q)
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["question"] == long_q

    # ========== INTEGRATION TESTS ==========

    def test_error_formatting_integration(self, tool: AskForClarification):
        with patch.object(tool, "_execute", side_effect=ValueError("Integration fail")):
            result = tool.run()
            assert result.get("success") is False or "error" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_full_workflow(self):
        tool = AskForClarification(question="Tell me more?")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["awaiting_user_response"] is True
        assert result["metadata"]["tool_name"] == "ask_for_clarification"
