"""
Comprehensive unit tests for Utility Tools category.

Tests all utility tools:
- think, ask_for_clarification, batch_processor, create_profile
- fact_checker, json_validator, text_formatter, translation
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any
import json

from tools.utils.think.think import Think
from tools.utils.ask_for_clarification.ask_for_clarification import AskForClarification
from tools.utils.batch_processor.batch_processor import BatchProcessor
from tools.utils.create_profile.create_profile import CreateProfile
from tools.utils.fact_checker.fact_checker import FactChecker
from tools.utils.json_validator.json_validator import JsonValidator
from tools.utils.text_formatter.text_formatter import TextFormatter
from tools.utils.translation.translation import Translation

from shared.errors import ValidationError, APIError


# ========== Think Tests ==========


class TestThink:
    """Comprehensive tests for Think tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = Think(thought="Analyzing the problem...")
        assert tool.thought == "Analyzing the problem..."
        assert tool.tool_name == "think"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = Think(thought="Processing information")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_thought(self):
        """Test validation with empty thought"""
        tool = Think(thought="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_edge_case_long_thought(self, monkeypatch):
        """Test handling of very long thoughts"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        long_thought = "Thinking " * 1000
        tool = Think(thought=long_thought)
        result = tool.run()

        assert result["success"] is True


# ========== AskForClarification Tests ==========


class TestAskForClarification:
    """Comprehensive tests for AskForClarification tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = AskForClarification(
            question="Could you clarify the requirements?", context="Project specifications"
        )
        assert tool.question == "Could you clarify the requirements?"
        assert tool.context == "Project specifications"
        assert tool.tool_name == "ask_for_clarification"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AskForClarification(question="What is the deadline?", context="Project timeline")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_question(self):
        """Test validation with empty question"""
        tool = AskForClarification(question="", context="test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== BatchProcessor Tests ==========


class TestBatchProcessor:
    """Comprehensive tests for BatchProcessor tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        items = ["item1", "item2", "item3"]
        tool = BatchProcessor(items=items, operation="process", batch_size=2)
        assert tool.items == items
        assert tool.operation == "process"
        assert tool.batch_size == 2
        assert tool.tool_name == "batch_processor"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        items = ["a", "b", "c"]
        tool = BatchProcessor(items=items, operation="transform")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_items(self):
        """Test validation with empty items list"""
        tool = BatchProcessor(items=[], operation="process")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_batch_size(self):
        """Test validation with invalid batch size"""
        with pytest.raises(ValidationError):
            BatchProcessor(items=["a", "b"], operation="process", batch_size=0)

    def test_edge_case_large_batch(self, monkeypatch):
        """Test processing large batch"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        items = list(range(1000))
        tool = BatchProcessor(items=items, operation="process", batch_size=100)
        result = tool.run()

        assert result["success"] is True


# ========== CreateProfile Tests ==========


class TestCreateProfile:
    """Comprehensive tests for CreateProfile tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = CreateProfile(name="John Doe", email="john@example.com", role="Developer")
        assert tool.name == "John Doe"
        assert tool.email == "john@example.com"
        assert tool.role == "Developer"
        assert tool.tool_name == "create_profile"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = CreateProfile(name="Jane Smith", email="jane@example.com", role="Manager")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_name(self):
        """Test validation with empty name"""
        tool = CreateProfile(name="", email="test@example.com", role="User")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_email(self):
        """Test validation with invalid email"""
        tool = CreateProfile(name="Test", email="invalid-email", role="User")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== FactChecker Tests ==========


class TestFactChecker:
    """Comprehensive tests for FactChecker tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = FactChecker(statement="The Earth is round", sources=["source1", "source2"])
        assert tool.statement == "The Earth is round"
        assert len(tool.sources) == 2
        assert tool.tool_name == "fact_checker"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = FactChecker(
            statement="Water boils at 100 degrees Celsius", sources=["physics textbook"]
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_statement(self):
        """Test validation with empty statement"""
        tool = FactChecker(statement="", sources=["source1"])
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.utils.fact_checker.fact_checker.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked fact-checking API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("FACT_CHECK_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "verdict": "true",
            "confidence": 0.95,
            "sources_verified": 2,
        }
        mock_post.return_value = mock_response

        tool = FactChecker(statement="Test statement", sources=["source1"])
        result = tool.run()

        assert result["success"] is True


# ========== JsonValidator Tests ==========


class TestJsonValidator:
    """Comprehensive tests for JsonValidator tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        json_data = '{"name": "test", "value": 123}'
        tool = JsonValidator(json_data=json_data)
        assert tool.json_data == json_data
        assert tool.tool_name == "json_validator"

    def test_execute_mock_mode_valid_json(self, monkeypatch):
        """Test execution with valid JSON in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        json_data = '{"key": "value"}'
        tool = JsonValidator(json_data=json_data)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_json(self):
        """Test validation with empty JSON"""
        tool = JsonValidator(json_data="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_json(self):
        """Test validation with invalid JSON"""
        tool = JsonValidator(json_data="{invalid json}")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_edge_case_nested_json(self, monkeypatch):
        """Test validation of deeply nested JSON"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        nested_json = json.dumps({"level1": {"level2": {"level3": {"level4": {"data": "value"}}}}})
        tool = JsonValidator(json_data=nested_json)
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_large_json(self, monkeypatch):
        """Test validation of large JSON"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        large_json = json.dumps({"items": [{"id": i, "value": f"item_{i}"} for i in range(1000)]})
        tool = JsonValidator(json_data=large_json)
        result = tool.run()

        assert result["success"] is True


# ========== TextFormatter Tests ==========


class TestTextFormatter:
    """Comprehensive tests for TextFormatter tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = TextFormatter(text="  Hello World  ", format_type="trim")
        assert tool.text == "  Hello World  "
        assert tool.format_type == "trim"
        assert tool.tool_name == "text_formatter"

    def test_execute_mock_mode_trim(self, monkeypatch):
        """Test trim formatting in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = TextFormatter(text="  test  ", format_type="trim")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_execute_mock_mode_uppercase(self, monkeypatch):
        """Test uppercase formatting in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = TextFormatter(text="hello", format_type="uppercase")
        result = tool.run()

        assert result["success"] is True

    def test_execute_mock_mode_lowercase(self, monkeypatch):
        """Test lowercase formatting in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = TextFormatter(text="HELLO", format_type="lowercase")
        result = tool.run()

        assert result["success"] is True

    def test_validate_parameters_empty_text(self):
        """Test validation with empty text"""
        tool = TextFormatter(text="", format_type="trim")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_format_type(self):
        """Test validation with invalid format type"""
        tool = TextFormatter(text="test", format_type="invalid")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_edge_case_special_characters(self, monkeypatch):
        """Test formatting text with special characters"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        special_text = "Hello @#$%^&*() World!"
        tool = TextFormatter(text=special_text, format_type="trim")
        result = tool.run()

        assert result["success"] is True


# ========== Translation Tests ==========


class TestTranslation:
    """Comprehensive tests for Translation tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = Translation(text="Hello world", source_language="en", target_language="es")
        assert tool.text == "Hello world"
        assert tool.source_language == "en"
        assert tool.target_language == "es"
        assert tool.tool_name == "translation"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = Translation(text="Good morning", source_language="en", target_language="fr")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_text(self):
        """Test validation with empty text"""
        tool = Translation(text="", source_language="en", target_language="es")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_language_code(self):
        """Test validation with invalid language code"""
        tool = Translation(text="test", source_language="invalid", target_language="es")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_same_languages(self):
        """Test validation when source and target are the same"""
        tool = Translation(text="test", source_language="en", target_language="en")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.utils.translation.translation.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked translation API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("TRANSLATION_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "translated_text": "Hola mundo",
            "source_language": "en",
            "target_language": "es",
        }
        mock_post.return_value = mock_response

        tool = Translation(text="Hello world", source_language="en", target_language="es")
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_long_text(self, monkeypatch):
        """Test translation of long text"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        long_text = "This is a sentence. " * 500
        tool = Translation(text=long_text, source_language="en", target_language="es")
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_special_characters_translation(self, monkeypatch):
        """Test translation with special characters"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        special_text = "Hello! @user #hashtag $100 50%"
        tool = Translation(text=special_text, source_language="en", target_language="es")
        result = tool.run()

        assert result["success"] is True
