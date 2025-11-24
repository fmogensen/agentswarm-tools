"""
Comprehensive tests for EditTool
"""

import os
import tempfile

import pytest

from tools.infrastructure.execution.edit_tool.edit_tool import EditTool
from shared.errors import APIError, ValidationError


class TestEditTool:
    """Test suite for EditTool"""

    def setup_method(self):
        """Set up test fixtures"""
        # Enable exception raising in tests
        os.environ["RAISE_TOOL_EXCEPTIONS"] = "true"
        os.environ["DISABLE_RATE_LIMITING"] = "true"
        # Disable mock mode for real tests
        os.environ.pop("USE_MOCK_APIS", None)

        # Create temporary test file
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt")
        self.test_file = self.temp_file.name
        self.temp_file.close()

    def teardown_method(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
        # Clean up environment variables
        os.environ.pop("RAISE_TOOL_EXCEPTIONS", None)
        os.environ.pop("DISABLE_RATE_LIMITING", None)

    def test_basic_single_replacement(self):
        """Test basic single replacement with unique string"""
        # Write test content
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        tool = EditTool(file_path=self.test_file, old_string="Line 2", new_string="Modified 2")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["occurrences_replaced"] == 1
        assert result["result"]["file_path"] == self.test_file

        # Verify file contents
        with open(self.test_file) as f:
            content = f.read()
            assert "Modified 2" in content
            assert "Line 2" not in content

    def test_replace_all_occurrences(self):
        """Test replacing all occurrences of a string"""
        # Write test content with duplicate strings
        with open(self.test_file, "w") as f:
            f.write("foo bar\nfoo baz\nfoo qux\n")

        tool = EditTool(
            file_path=self.test_file, old_string="foo", new_string="bar", replace_all=True
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["occurrences_replaced"] == 3

        # Verify all replaced
        with open(self.test_file) as f:
            content = f.read()
            assert content.count("bar") == 4  # 3 replacements + 1 original
            assert "foo" not in content

    def test_file_not_found_error(self):
        """Test error when file doesn't exist"""
        tool = EditTool(
            file_path="/tmp/nonexistent_file_xyz123.txt", old_string="old", new_string="new"
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "File not found" in str(exc_info.value)

    def test_non_absolute_path_error(self):
        """Test error when path is not absolute"""
        tool = EditTool(file_path="relative/path.txt", old_string="old", new_string="new")

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "must be absolute" in str(exc_info.value)

    def test_old_string_not_found_error(self):
        """Test error when old_string not found in file"""
        with open(self.test_file, "w") as f:
            f.write("Hello World\n")

        tool = EditTool(file_path=self.test_file, old_string="nonexistent string", new_string="new")

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "not found in file" in str(exc_info.value)

    def test_old_string_not_unique_error(self):
        """Test error when old_string not unique and replace_all=False"""
        with open(self.test_file, "w") as f:
            f.write("duplicate\nduplicate\n")

        tool = EditTool(file_path=self.test_file, old_string="duplicate", new_string="new")

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "found 2 times" in str(exc_info.value)
        assert "replace_all=True" in str(exc_info.value)

    def test_identical_strings_error(self):
        """Test error when old_string == new_string"""
        with open(self.test_file, "w") as f:
            f.write("test content\n")

        tool = EditTool(file_path=self.test_file, old_string="same", new_string="same")

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "must be different" in str(exc_info.value)

    def test_empty_old_string_error(self):
        """Test error when old_string is empty"""
        with pytest.raises(ValueError):  # Pydantic validation
            EditTool(file_path=self.test_file, old_string="", new_string="new")

    def test_mock_mode(self):
        """Test mock mode execution"""
        os.environ["USE_MOCK_APIS"] = "true"

        try:
            tool = EditTool(file_path="/mock/path/file.txt", old_string="old", new_string="new")
            result = tool.run()

            assert result["success"] is True
            assert result["result"]["mock"] is True
            assert "lines_changed" in result["result"]
            assert "occurrences_replaced" in result["result"]
        finally:
            os.environ.pop("USE_MOCK_APIS", None)

    def test_large_file_handling(self):
        """Test handling of large file with many lines"""
        # Create a file with 1000 lines
        with open(self.test_file, "w") as f:
            for i in range(1000):
                f.write(f"Line {i}\n")

        tool = EditTool(file_path=self.test_file, old_string="Line 500", new_string="Modified 500")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["occurrences_replaced"] == 1

        # Verify specific line changed
        with open(self.test_file) as f:
            content = f.read()
            assert "Modified 500" in content
            assert "Line 500" not in content

    def test_unicode_character_handling(self):
        """Test handling of unicode characters"""
        # Write unicode content
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("Hello 世界\nBonjour monde\nHola mundo\n")

        tool = EditTool(
            file_path=self.test_file, old_string="世界", new_string="World", replace_all=False
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["occurrences_replaced"] == 1

        # Verify replacement
        with open(self.test_file, encoding="utf-8") as f:
            content = f.read()
            assert "World" in content
            assert "世界" not in content

    def test_multiple_lines_replacement(self):
        """Test replacing text that spans multiple lines"""
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\nLine 4\n")

        # Replace text spanning multiple lines
        tool = EditTool(
            file_path=self.test_file,
            old_string="Line 2\nLine 3",
            new_string="Modified Lines",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["occurrences_replaced"] == 1

        # Verify replacement
        with open(self.test_file) as f:
            content = f.read()
            assert "Modified Lines" in content
            assert "Line 2" not in content
            assert "Line 3" not in content

    def test_whitespace_preservation(self):
        """Test that whitespace is preserved correctly"""
        with open(self.test_file, "w") as f:
            f.write("    indented line\n\ttab indented\n")

        tool = EditTool(
            file_path=self.test_file,
            old_string="    indented line",
            new_string="    modified indented",
        )
        result = tool.run()

        assert result["success"] is True

        # Verify whitespace preserved
        with open(self.test_file) as f:
            content = f.read()
            assert "    modified indented" in content
            assert "\ttab indented" in content  # Other whitespace unchanged

    def test_case_sensitivity(self):
        """Test that replacements are case-sensitive"""
        with open(self.test_file, "w") as f:
            f.write("Hello\nhello\nHELLO\n")

        tool = EditTool(file_path=self.test_file, old_string="hello", new_string="hi")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["occurrences_replaced"] == 1

        # Verify only lowercase replaced
        with open(self.test_file) as f:
            content = f.read()
            assert "hi" in content
            assert "Hello" in content  # Unchanged
            assert "HELLO" in content  # Unchanged

    def test_file_permissions_error_handling(self):
        """Test handling of file permission errors"""
        # Note: This test may not work on all systems
        # Skip if not on Unix-like system
        if os.name != "posix":
            pytest.skip("File permissions test only on Unix-like systems")

        with open(self.test_file, "w") as f:
            f.write("test content\n")

        # Make file read-only
        os.chmod(self.test_file, 0o444)

        try:
            tool = EditTool(file_path=self.test_file, old_string="test", new_string="modified")

            # Should raise APIError due to write permission
            with pytest.raises(APIError) as exc_info:
                result = tool.run()

            assert "Permission denied" in str(exc_info.value)
        finally:
            # Restore write permission for cleanup
            os.chmod(self.test_file, 0o644)

    def test_empty_file_handling(self):
        """Test editing empty file raises error"""
        with open(self.test_file, "w") as f:
            f.write("")

        tool = EditTool(file_path=self.test_file, old_string="anything", new_string="new")

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "not found in file" in str(exc_info.value)

    def test_new_string_can_be_empty(self):
        """Test that new_string can be empty (deletion)"""
        with open(self.test_file, "w") as f:
            f.write("Remove this word from the sentence.\n")

        tool = EditTool(file_path=self.test_file, old_string=" this word", new_string="")
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["occurrences_replaced"] == 1

        # Verify deletion
        with open(self.test_file) as f:
            content = f.read()
            assert content == "Remove from the sentence.\n"

    def test_special_characters_replacement(self):
        """Test replacing text with special characters"""
        with open(self.test_file, "w") as f:
            f.write('print("Hello")\n')

        tool = EditTool(
            file_path=self.test_file,
            old_string='print("Hello")',
            new_string='print("World")',
        )
        result = tool.run()

        assert result["success"] is True

        # Verify replacement
        with open(self.test_file) as f:
            content = f.read()
            assert 'print("World")' in content

    def test_lines_changed_count(self):
        """Test that lines_changed count is accurate"""
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        # Replace single word on one line
        tool = EditTool(file_path=self.test_file, old_string="Line 2", new_string="Modified 2")
        result = tool.run()

        assert result["result"]["lines_changed"] >= 1  # At least one line changed

    def test_metadata_in_response(self):
        """Test that response includes proper metadata"""
        with open(self.test_file, "w") as f:
            f.write("test content\n")

        tool = EditTool(file_path=self.test_file, old_string="test", new_string="modified")
        result = tool.run()

        assert "metadata" in result
        assert result["metadata"]["tool_name"] == "edit_tool"
        assert result["metadata"]["file_path"] == self.test_file
