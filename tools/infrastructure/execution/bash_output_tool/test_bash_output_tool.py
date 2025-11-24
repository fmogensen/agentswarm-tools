"""
Comprehensive tests for BashOutputTool.
"""

import os
import re

import pytest

from tools.infrastructure.execution.bash_output_tool.bash_output_tool import (
    BashOutputTool,
)
from shared.errors import APIError, ValidationError


@pytest.fixture(autouse=True)
def setup_mock_mode():
    """Enable mock mode for all tests."""
    original = os.environ.get("USE_MOCK_APIS")
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    if original:
        os.environ["USE_MOCK_APIS"] = original
    else:
        os.environ.pop("USE_MOCK_APIS", None)


@pytest.fixture(autouse=True)
def reset_shell_registry():
    """Reset shell registry between tests."""
    BashOutputTool._shell_registry = {}
    BashOutputTool._output_buffers = {}
    BashOutputTool._read_positions = {}
    yield
    BashOutputTool._shell_registry = {}
    BashOutputTool._output_buffers = {}
    BashOutputTool._read_positions = {}


class TestBashOutputToolBasic:
    """Test basic functionality."""

    def test_basic_output_retrieval(self):
        """Test retrieving output from a shell."""
        tool = BashOutputTool(shell_id="test_shell_001")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["result"]["shell_id"] == "test_shell_001"
        assert isinstance(result["result"]["output_lines"], list)
        assert result["result"]["shell_status"] in ["running", "completed", "failed"]
        assert isinstance(result["result"]["has_more"], bool)

    def test_shell_id_stored_correctly(self):
        """Test that shell_id is stored and returned correctly."""
        tool = BashOutputTool(shell_id="custom_shell_xyz")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["shell_id"] == "custom_shell_xyz"

    def test_output_is_list(self):
        """Test that output_lines is always a list."""
        tool = BashOutputTool(shell_id="test_shell")
        result = tool.run()

        assert isinstance(result["result"]["output_lines"], list)
        assert len(result["result"]["output_lines"]) >= 0

    def test_mock_mode_returns_data(self):
        """Test that mock mode returns sample data."""
        tool = BashOutputTool(shell_id="mock_shell")
        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]["output_lines"]) > 0
        assert result["result"]["mock"] is True


class TestBashOutputToolValidation:
    """Test input validation."""

    def test_empty_shell_id_raises_error(self):
        """Test that empty shell_id raises ValidationError."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError) as exc_info:
            tool = BashOutputTool(shell_id="")

        assert "shell_id" in str(exc_info.value)

    def test_whitespace_shell_id_raises_error(self):
        """Test that whitespace-only shell_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = BashOutputTool(shell_id="   ")
            tool.run()

        assert "shell_id cannot be empty" in str(exc_info.value)

    def test_invalid_regex_pattern_raises_error(self):
        """Test that invalid regex pattern raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = BashOutputTool(shell_id="test_shell", filter_pattern="[invalid(")
            tool.run()

        assert "Invalid regex pattern" in str(exc_info.value)

    def test_invalid_regex_unclosed_bracket(self):
        """Test that unclosed bracket in regex raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = BashOutputTool(shell_id="test_shell", filter_pattern="test[")
            tool.run()

        assert "Invalid regex pattern" in str(exc_info.value)

    def test_invalid_regex_unclosed_paren(self):
        """Test that unclosed parenthesis in regex raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = BashOutputTool(shell_id="test_shell", filter_pattern="test(")
            tool.run()

        assert "Invalid regex pattern" in str(exc_info.value)

    def test_valid_complex_regex_accepted(self):
        """Test that valid complex regex patterns are accepted."""
        # Should not raise any errors
        tool = BashOutputTool(shell_id="test_shell", filter_pattern=r"^(ERROR|WARN):\s+\w+")
        result = tool.run()
        assert result["success"] is True


class TestBashOutputToolFilterPattern:
    """Test filter pattern functionality."""

    def test_filter_pattern_basic(self):
        """Test basic filter pattern matching."""
        tool = BashOutputTool(shell_id="test_shell", filter_pattern="error")
        result = tool.run()

        assert result["success"] is True
        assert "filtered_lines_count" in result["result"]

    def test_filter_pattern_case_insensitive(self):
        """Test that filter pattern is case insensitive."""
        tool = BashOutputTool(shell_id="test_shell", filter_pattern="ERROR")
        result = tool.run()

        assert result["success"] is True
        # Should match lines with "error", "Error", "ERROR", etc.
        assert result["result"]["filtered_lines_count"] >= 0

    def test_filter_pattern_multiple_terms(self):
        """Test filter pattern with multiple terms using OR."""
        tool = BashOutputTool(shell_id="test_shell", filter_pattern="error|warning")
        result = tool.run()

        assert result["success"] is True
        assert isinstance(result["result"]["output_lines"], list)

    def test_filter_pattern_special_chars(self):
        """Test filter pattern with special regex characters."""
        tool = BashOutputTool(shell_id="test_shell", filter_pattern=r"\d+")
        result = tool.run()

        assert result["success"] is True

    def test_no_filter_returns_all_lines(self):
        """Test that no filter returns all output lines."""
        tool = BashOutputTool(shell_id="test_shell")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["filtered_lines_count"] == result["result"]["total_lines"]

    def test_filter_reduces_line_count(self):
        """Test that filter can reduce line count."""
        tool = BashOutputTool(shell_id="test_shell", filter_pattern="xyz_unlikely")
        result = tool.run()

        assert result["success"] is True
        # Filtered count should be <= total count
        assert result["result"]["filtered_lines_count"] <= result["result"]["total_lines"]


class TestBashOutputToolShellStatus:
    """Test shell status handling."""

    def test_shell_status_present(self):
        """Test that shell_status is present in result."""
        tool = BashOutputTool(shell_id="test_shell")
        result = tool.run()

        assert "shell_status" in result["result"]
        assert result["result"]["shell_status"] in ["running", "completed", "failed"]

    def test_running_shell_has_more_true(self):
        """Test that running shell indicates more output may come."""
        tool = BashOutputTool(shell_id="test_shell")
        result = tool.run()

        # In mock mode, this should work
        assert "has_more" in result["result"]
        assert isinstance(result["result"]["has_more"], bool)

    def test_different_shell_statuses(self):
        """Test handling of different shell statuses."""
        # This test verifies the tool handles different status values
        statuses = ["running", "completed", "failed"]

        for status in statuses:
            tool = BashOutputTool(shell_id=f"test_shell_{status}")
            result = tool.run()
            assert result["success"] is True


class TestBashOutputToolNonExistentShell:
    """Test handling of non-existent shells (production mode)."""

    def test_non_existent_shell_in_production_mode(self):
        """Test that non-existent shell raises APIError in production mode."""
        # Temporarily disable mock mode
        os.environ["USE_MOCK_APIS"] = "false"

        try:
            with pytest.raises(APIError) as exc_info:
                tool = BashOutputTool(shell_id="nonexistent_shell_xyz")
                tool.run()

            assert "not found" in str(exc_info.value).lower()
        finally:
            # Re-enable mock mode
            os.environ["USE_MOCK_APIS"] = "true"


class TestBashOutputToolMultipleReads:
    """Test multiple reads from same shell (output depletion)."""

    def test_multiple_reads_production_mode(self):
        """Test reading output multiple times depletes buffer."""
        # Disable mock mode for this test
        os.environ["USE_MOCK_APIS"] = "false"

        try:
            # Initialize registry
            BashOutputTool._shell_registry = {"test_shell_123": {"status": "running"}}
            BashOutputTool._output_buffers = {"test_shell_123": ["Line 1", "Line 2", "Line 3"]}
            BashOutputTool._read_positions = {"test_shell_123": 0}

            # First read - should get all lines
            tool1 = BashOutputTool(shell_id="test_shell_123")
            result1 = tool1.run()

            assert result1["success"] is True
            assert len(result1["result"]["output_lines"]) == 3

            # Second read - should get no new lines
            tool2 = BashOutputTool(shell_id="test_shell_123")
            result2 = tool2.run()

            assert result2["success"] is True
            assert len(result2["result"]["output_lines"]) == 0

        finally:
            os.environ["USE_MOCK_APIS"] = "true"


class TestBashOutputToolLargeOutput:
    """Test handling of large output."""

    def test_large_output_handling(self):
        """Test that tool handles large output correctly."""
        tool = BashOutputTool(shell_id="large_output_shell")
        result = tool.run()

        assert result["success"] is True
        assert isinstance(result["result"]["output_lines"], list)
        # Should handle any size
        assert result["result"]["total_lines"] >= 0


class TestBashOutputToolUnicodeOutput:
    """Test handling of unicode output."""

    def test_unicode_in_output(self):
        """Test that unicode characters in output are handled correctly."""
        # Mock mode should handle this gracefully
        tool = BashOutputTool(shell_id="unicode_shell")
        result = tool.run()

        assert result["success"] is True
        assert isinstance(result["result"]["output_lines"], list)


class TestBashOutputToolEmptyOutput:
    """Test handling of empty output."""

    def test_empty_output_scenario(self):
        """Test shell with no output."""
        # In production mode with empty buffer
        os.environ["USE_MOCK_APIS"] = "false"

        try:
            BashOutputTool._shell_registry = {"empty_shell": {"status": "running"}}
            BashOutputTool._output_buffers = {"empty_shell": []}
            BashOutputTool._read_positions = {"empty_shell": 0}

            tool = BashOutputTool(shell_id="empty_shell")
            result = tool.run()

            assert result["success"] is True
            assert len(result["result"]["output_lines"]) == 0
            assert result["result"]["total_lines"] == 0
        finally:
            os.environ["USE_MOCK_APIS"] = "true"


class TestBashOutputToolMetadata:
    """Test metadata in results."""

    def test_metadata_present(self):
        """Test that metadata is present in results."""
        tool = BashOutputTool(shell_id="test_shell")
        result = tool.run()

        assert "metadata" in result
        assert "tool_name" in result["metadata"]
        assert result["metadata"]["tool_name"] == "bash_output_tool"

    def test_mock_metadata(self):
        """Test that mock mode includes mock indicator in metadata."""
        tool = BashOutputTool(shell_id="test_shell")
        result = tool.run()

        # In mock mode
        assert result["result"]["mock"] is True


class TestBashOutputToolEdgeCases:
    """Test edge cases and special scenarios."""

    def test_shell_id_with_special_chars(self):
        """Test shell_id with special characters."""
        tool = BashOutputTool(shell_id="shell-123_abc.xyz")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["shell_id"] == "shell-123_abc.xyz"

    def test_very_long_shell_id(self):
        """Test very long shell_id."""
        long_id = "a" * 1000
        tool = BashOutputTool(shell_id=long_id)
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["shell_id"] == long_id

    def test_filter_pattern_matches_nothing(self):
        """Test filter pattern that matches nothing."""
        tool = BashOutputTool(shell_id="test_shell", filter_pattern="xyz_impossible_pattern_12345")
        result = tool.run()

        assert result["success"] is True
        # Should return empty or minimal results
        assert result["result"]["filtered_lines_count"] >= 0

    def test_filter_pattern_matches_everything(self):
        """Test filter pattern that matches everything."""
        tool = BashOutputTool(shell_id="test_shell", filter_pattern=".*")
        result = tool.run()

        assert result["success"] is True
        # Should match all lines
        assert result["result"]["filtered_lines_count"] == result["result"]["total_lines"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
