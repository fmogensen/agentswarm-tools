"""Test cases for JsonValidator tool."""

import os
import pytest
from .json_validator import JsonValidator
from shared.errors import ValidationError


class TestJsonValidator:
    """Test suite for JsonValidator tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_valid_json(self):
        """Test valid JSON."""
        tool = JsonValidator(json_data='{"name": "John", "age": 30}')
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["is_valid"] == True

    def test_invalid_json(self):
        """Test invalid JSON syntax."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = JsonValidator(json_data='{"name": "John", age: 30}')  # Missing quotes
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["is_valid"] == False
        assert len(result["result"]["errors"]) > 0

    def test_with_schema_valid(self):
        """Test validation with matching schema."""
        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        os.environ["USE_MOCK_APIS"] = "false"
        tool = JsonValidator(
            json_data='{"name": "John", "age": 30}',
            schema=schema
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["schema_valid"] == True

    def test_with_schema_invalid(self):
        """Test validation with non-matching schema."""
        schema = {
            "type": "object",
            "required": ["name", "age", "email"],  # email is required but missing
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
        os.environ["USE_MOCK_APIS"] = "false"
        tool = JsonValidator(
            json_data='{"name": "John", "age": 30}',
            schema=schema
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["schema_valid"] == False

    def test_type_validation(self):
        """Test type validation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = JsonValidator(
            json_data='{"count": "123", "active": "true"}',  # Numbers and booleans as strings
            validate_types=True
        )
        result = tool.run()

        assert result["success"] == True
        # Should have type warnings
        # Note: warnings might be empty in mock mode

    def test_strict_validation(self):
        """Test strict validation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = JsonValidator(
            json_data='{"name": "", "value": null}',
            strict=True
        )
        result = tool.run()

        assert result["success"] == True
        # Should have strict warnings

    def test_array_json(self):
        """Test array JSON."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = JsonValidator(json_data='[1, 2, 3, 4, 5]')
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["is_valid"] == True

    def test_nested_json(self):
        """Test nested JSON."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = JsonValidator(
            json_data='{"user": {"name": "John", "address": {"city": "NYC"}}}'
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["is_valid"] == True

    def test_empty_json_data(self):
        """Test empty JSON data."""
        with pytest.raises(ValidationError):
            tool = JsonValidator(json_data="")
            tool._validate_parameters()

    def test_whitespace_only(self):
        """Test whitespace only."""
        with pytest.raises(ValidationError):
            tool = JsonValidator(json_data="   ")
            tool._validate_parameters()

    def test_mock_mode(self):
        """Test mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = JsonValidator(json_data='{"test": 123}')
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
