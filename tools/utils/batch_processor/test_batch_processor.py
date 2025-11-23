"""Test cases for BatchProcessor tool."""

import os

import pytest

from shared.errors import ValidationError

from .batch_processor import BatchProcessor


class TestBatchProcessor:
    """Test suite for BatchProcessor tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_transform_uppercase(self):
        """Test transform operation with uppercase."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(
            items=["hello", "world"],
            operation="transform",
            operation_config={"method": "uppercase"},
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["successful"] == 2
        assert "HELLO" in result["result"]["processed_items"]

    def test_transform_numbers(self):
        """Test transform operation with numbers."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(
            items=[1, 2, 3], operation="transform", operation_config={"method": "double"}
        )
        result = tool.run()

        assert result["success"] == True
        assert 2 in result["result"]["processed_items"]
        assert 4 in result["result"]["processed_items"]
        assert 6 in result["result"]["processed_items"]

    def test_filter_operation(self):
        """Test filter operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(
            items=["hello", "", "world"],
            operation="filter",
            operation_config={"condition": "non_empty"},
        )
        result = tool.run()

        assert result["success"] == True
        # Empty string should fail
        assert result["result"]["failed"] == 1

    def test_validate_operation(self):
        """Test validate operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(
            items=["hello", "hi"],
            operation="validate",
            operation_config={
                "rules": [
                    {"type": "type_check", "expected_type": "string"},
                    {"type": "min_length", "value": 2},
                ]
            },
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["successful"] == 2

    def test_count_operation(self):
        """Test count operation."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(items=["a", "b", "c"], operation="count")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["successful"] == 3

    def test_batch_size(self):
        """Test batch size processing."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(items=["1", "2", "3", "4", "5"], operation="count", batch_size=2)
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["total_batches"] == 3  # 5 items / 2 per batch = 3 batches

    def test_continue_on_error(self):
        """Test continue on error."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(
            items=["hello", "", "world"],
            operation="filter",
            operation_config={"condition": "non_empty"},
            continue_on_error=True,
        )
        result = tool.run()

        assert result["success"] == True
        # Should process all items despite error
        assert result["result"]["successful"] == 2
        assert result["result"]["failed"] == 1

    def test_stop_on_error(self):
        """Test stop on error."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(
            items=["hello", "", "world"],
            operation="filter",
            operation_config={"condition": "non_empty"},
            continue_on_error=False,
        )
        result = tool.run()

        assert result["success"] == True
        # Should stop after first error in batch

    def test_invalid_operation(self):
        """Test invalid operation."""
        with pytest.raises(ValidationError):
            tool = BatchProcessor(items=["test"], operation="invalid_op")
            tool._validate_parameters()

    def test_empty_items(self):
        """Test empty items list."""
        with pytest.raises(Exception):  # Pydantic will catch min_items=1
            tool = BatchProcessor(items=[], operation="count")

    def test_processing_time_recorded(self):
        """Test that processing time is recorded."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(items=["a", "b", "c"], operation="count")
        result = tool.run()

        assert result["success"] == True
        assert "processing_time_ms" in result["result"]
        assert result["result"]["processing_time_ms"] >= 0

    def test_errors_captured(self):
        """Test that errors are captured."""
        os.environ["USE_MOCK_APIS"] = "false"
        tool = BatchProcessor(
            items=["hello", "", "world"],
            operation="filter",
            operation_config={"condition": "non_empty"},
            continue_on_error=True,
        )
        result = tool.run()

        assert result["success"] == True
        assert "errors" in result["result"]
        if result["result"]["failed"] > 0:
            assert len(result["result"]["errors"]) > 0

    def test_mock_mode(self):
        """Test mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = BatchProcessor(items=["a", "b", "c"], operation="transform")
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
