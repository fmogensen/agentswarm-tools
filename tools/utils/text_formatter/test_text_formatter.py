"""Test cases for TextFormatter tool."""

import os

import pytest

from shared.errors import ValidationError

from .text_formatter import TextFormatter


class TestTextFormatter:
    """Test suite for TextFormatter tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_trim_operation(self):
        """Test trim operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="  hello  ", operations=["trim"])
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formatted_text"] == "hello"

    def test_lowercase_operation(self):
        """Test lowercase operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="HELLO WORLD", operations=["lowercase"])
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formatted_text"] == "hello world"

    def test_uppercase_operation(self):
        """Test uppercase operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="hello world", operations=["uppercase"])
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formatted_text"] == "HELLO WORLD"

    def test_title_operation(self):
        """Test title operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="hello world", operations=["title"])
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formatted_text"] == "Hello World"

    def test_remove_whitespace(self):
        """Test remove whitespace operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="hello world", operations=["remove_whitespace"])
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formatted_text"] == "helloworld"

    def test_remove_punctuation(self):
        """Test remove punctuation operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="hello, world!", operations=["remove_punctuation"])
        result = tool.run()

        assert result["success"] == True
        assert "," not in result["result"]["formatted_text"]
        assert "!" not in result["result"]["formatted_text"]

    def test_normalize_spaces(self):
        """Test normalize spaces operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="hello    world", operations=["normalize_spaces"])
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formatted_text"] == "hello world"

    def test_remove_numbers(self):
        """Test remove numbers operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="hello123world456", operations=["remove_numbers"])
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formatted_text"] == "helloworld"

    def test_remove_special_chars(self):
        """Test remove special characters operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="hello@world#test", operations=["remove_special_chars"])
        result = tool.run()

        assert result["success"] == True
        assert "@" not in result["result"]["formatted_text"]
        assert "#" not in result["result"]["formatted_text"]

    def test_multiple_operations(self):
        """Test multiple operations."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(
            text="  HELLO WORLD!  ", operations=["trim", "lowercase", "remove_punctuation"]
        )
        result = tool.run()

        assert result["success"] == True
        formatted = result["result"]["formatted_text"]
        assert formatted.startswith("hello")
        assert "!" not in formatted

    def test_custom_replacements(self):
        """Test custom replacements."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(
            text="hello world",
            operations=["trim"],
            custom_replacements={"hello": "hi", "world": "there"},
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formatted_text"] == "hi there"

    def test_strip_html(self):
        """Test HTML stripping."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="<p>hello <b>world</b></p>", operations=["trim"], strip_html=True)
        result = tool.run()

        assert result["success"] == True
        assert "<p>" not in result["result"]["formatted_text"]
        assert "<b>" not in result["result"]["formatted_text"]

    def test_invalid_operation(self):
        """Test invalid operation."""
        with pytest.raises(ValidationError):
            tool = TextFormatter(text="test", operations=["invalid_op"])
            tool._validate_parameters()

    def test_empty_operations(self):
        """Test empty operations list."""
        with pytest.raises(Exception):  # Pydantic will catch min_items=1
            tool = TextFormatter(text="test", operations=[])

    def test_changes_log(self):
        """Test changes log is recorded."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = TextFormatter(text="  HELLO  ", operations=["trim", "lowercase"])
        result = tool.run()

        assert result["success"] == True
        assert "changes_log" in result["result"]
        assert len(result["result"]["changes_log"]) > 0

    def test_mock_mode(self):
        """Test mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = TextFormatter(text="test", operations=["trim"])
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
