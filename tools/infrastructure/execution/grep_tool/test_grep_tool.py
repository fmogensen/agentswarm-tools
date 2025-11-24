"""
Comprehensive tests for GrepTool
"""

import os
import tempfile
from pathlib import Path

import pytest

from tools.infrastructure.execution.grep_tool.grep_tool import GrepTool


# Ensure we're not in mock mode for these tests
@pytest.fixture(autouse=True)
def disable_mock_mode():
    """Disable mock mode for all tests except those that specifically test it"""
    original_value = os.environ.get("USE_MOCK_APIS")
    os.environ["USE_MOCK_APIS"] = "false"
    yield
    if original_value is None:
        os.environ.pop("USE_MOCK_APIS", None)
    else:
        os.environ["USE_MOCK_APIS"] = original_value


class TestGrepToolValidation:
    """Test validation logic"""

    def test_empty_pattern_raises_error(self):
        """Test that empty pattern raises ValidationError"""
        with pytest.raises(Exception) as exc_info:
            tool = GrepTool(pattern="   ")
            tool.run()
        assert "empty" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()

    def test_invalid_regex_raises_error(self):
        """Test that invalid regex pattern raises ValidationError"""
        with pytest.raises(Exception) as exc_info:
            tool = GrepTool(pattern="[invalid(regex")
            tool.run()
        assert "regex" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()

    def test_invalid_output_mode_raises_error(self):
        """Test that invalid output_mode raises ValidationError"""
        with pytest.raises(Exception) as exc_info:
            tool = GrepTool(pattern="test", output_mode="invalid_mode")
            tool.run()
        assert (
            "output_mode" in str(exc_info.value).lower()
            or "validation" in str(exc_info.value).lower()
        )

    def test_nonexistent_path_raises_error(self):
        """Test that nonexistent path raises ValidationError"""
        with pytest.raises(Exception) as exc_info:
            tool = GrepTool(pattern="test", path="/nonexistent/path/12345")
            tool.run()
        assert "exist" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()


class TestGrepToolBasicSearch:
    """Test basic search functionality"""

    def test_files_with_matches_mode(self):
        """Test files_with_matches mode returns matching file paths"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_file = Path(tmpdir, "test1.txt")
            test_file.write_text("Hello World\nGoodbye World")

            test_file2 = Path(tmpdir, "test2.txt")
            test_file2.write_text("No match here")

            # Search
            tool = GrepTool(pattern="Hello", path=tmpdir, output_mode="files_with_matches")
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 1
            assert str(test_file) in results[0]

    def test_content_mode_returns_matching_lines(self):
        """Test content mode returns actual matching lines"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Line 1: Hello\nLine 2: World\nLine 3: Hello again")

            tool = GrepTool(pattern="Hello", path=str(test_file), output_mode="content")
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 2
            assert "Hello" in results[0]
            assert "Hello" in results[1]

    def test_count_mode_returns_match_counts(self):
        """Test count mode returns match counts per file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test1.txt")
            test_file.write_text("test test test")

            test_file2 = Path(tmpdir, "test2.txt")
            test_file2.write_text("test test")

            tool = GrepTool(pattern="test", path=tmpdir, output_mode="count")
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert str(test_file) in results
            assert results[str(test_file)] == 3
            assert results[str(test_file2)] == 2

    def test_case_insensitive_search(self):
        """Test case insensitive search matches regardless of case"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("HELLO\nhello\nHeLLo")

            tool = GrepTool(
                pattern="hello", path=str(test_file), case_insensitive=True, output_mode="content"
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 3

    def test_case_sensitive_search(self):
        """Test case sensitive search only matches exact case"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("HELLO\nhello\nHeLLo")

            tool = GrepTool(
                pattern="hello", path=str(test_file), case_insensitive=False, output_mode="content"
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 1


class TestGrepToolLineNumbers:
    """Test line number functionality"""

    def test_line_numbers_in_content_mode(self):
        """Test that line numbers appear when enabled"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Line 1\nLine 2: match\nLine 3")

            tool = GrepTool(
                pattern="match", path=str(test_file), output_mode="content", line_numbers=True
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) >= 1
            # Line 2 should have line number 2
            assert ":2:" in results[0]

    def test_no_line_numbers_when_disabled(self):
        """Test that line numbers don't appear when disabled"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Line 1\nLine 2: match\nLine 3")

            tool = GrepTool(
                pattern="match", path=str(test_file), output_mode="content", line_numbers=False
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            # Format is "filepath: content" without line numbers
            assert ":" in results[0]
            assert ":2:" not in results[0]


class TestGrepToolContext:
    """Test context before/after functionality"""

    def test_context_before(self):
        """Test context lines before match"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Before 1\nBefore 2\nMatch line\nAfter 1")

            tool = GrepTool(
                pattern="Match",
                path=str(test_file),
                output_mode="content",
                context_before=2,
                line_numbers=True,
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            # Should have 2 before + 1 match = 3 lines
            assert len(results) >= 3
            assert "Before 1" in results[0]
            assert "Before 2" in results[1]
            assert "Match" in results[2]

    def test_context_after(self):
        """Test context lines after match"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Before 1\nMatch line\nAfter 1\nAfter 2")

            tool = GrepTool(
                pattern="Match",
                path=str(test_file),
                output_mode="content",
                context_after=2,
                line_numbers=True,
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            # Should have 1 match + 2 after = 3 lines
            assert len(results) >= 3
            assert "Match" in results[0]
            assert "After 1" in results[1]
            assert "After 2" in results[2]

    def test_context_before_and_after(self):
        """Test context lines before and after match"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Before 1\nBefore 2\nMatch line\nAfter 1\nAfter 2")

            tool = GrepTool(
                pattern="Match",
                path=str(test_file),
                output_mode="content",
                context_before=2,
                context_after=2,
                line_numbers=True,
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            # Should have 2 before + 1 match + 2 after = 5 lines
            assert len(results) >= 5


class TestGrepToolFiltering:
    """Test glob and file_type filtering"""

    def test_glob_filter_matches_pattern(self):
        """Test glob filter only searches matching files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with different extensions
            py_file = Path(tmpdir, "test.py")
            py_file.write_text("Python content")

            js_file = Path(tmpdir, "test.js")
            js_file.write_text("JavaScript content")

            txt_file = Path(tmpdir, "test.txt")
            txt_file.write_text("Text content")

            # Search only .py files
            tool = GrepTool(
                pattern="content",
                path=tmpdir,
                glob="*.py",
                output_mode="files_with_matches",
                case_insensitive=True,
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 1
            assert results[0].endswith(".py")

    def test_file_type_filter(self):
        """Test file_type filter only searches matching extensions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with different extensions
            py_file = Path(tmpdir, "test.py")
            py_file.write_text("Python content")

            js_file = Path(tmpdir, "test.js")
            js_file.write_text("JavaScript content")

            # Search only .js files
            tool = GrepTool(
                pattern="content",
                path=tmpdir,
                file_type="js",
                output_mode="files_with_matches",
                case_insensitive=True,
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 1
            assert results[0].endswith(".js")


class TestGrepToolRegex:
    """Test regex pattern functionality"""

    def test_simple_regex_pattern(self):
        """Test simple regex pattern matching"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("test123\ntest456\nabc789")

            tool = GrepTool(pattern=r"test\d+", path=str(test_file), output_mode="content")
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 2

    def test_complex_regex_pattern(self):
        """Test complex regex pattern with groups"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("user@example.com\nadmin@test.org\ninvalid-email")

            tool = GrepTool(pattern=r"\w+@\w+\.\w+", path=str(test_file), output_mode="content")
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 2


class TestGrepToolEdgeCases:
    """Test edge cases and special scenarios"""

    def test_no_matches_returns_empty_results(self):
        """Test that no matches returns empty results"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Some text without the pattern")

            tool = GrepTool(
                pattern="nonexistent", path=str(test_file), output_mode="files_with_matches"
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 0
            assert result["result"]["total_matches"] == 0

    def test_search_single_file(self):
        """Test searching a single file (not directory)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Hello World")

            tool = GrepTool(pattern="Hello", path=str(test_file), output_mode="files_with_matches")
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 1
            assert result["result"]["files_searched"] == 1

    def test_recursive_directory_search(self):
        """Test recursive search through subdirectories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir, "subdir")
            subdir.mkdir()

            file1 = Path(tmpdir, "file1.txt")
            file1.write_text("Pattern here")

            file2 = Path(subdir, "file2.txt")
            file2.write_text("Pattern here too")

            tool = GrepTool(pattern="Pattern", path=tmpdir, output_mode="files_with_matches")
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 2

    def test_binary_file_handling(self):
        """Test that binary files are skipped"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a binary file
            binary_file = Path(tmpdir, "binary.bin")
            binary_file.write_bytes(b"\x00\x01\x02\x03\x04")

            # Create a text file
            text_file = Path(tmpdir, "text.txt")
            text_file.write_text("Pattern here")

            tool = GrepTool(pattern="Pattern", path=tmpdir, output_mode="files_with_matches")
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            # Should only find text file, not binary
            assert len(results) == 1
            assert "text.txt" in results[0]

    def test_empty_file(self):
        """Test searching empty file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "empty.txt")
            test_file.write_text("")

            tool = GrepTool(
                pattern="anything", path=str(test_file), output_mode="files_with_matches"
            )
            result = tool.run()

            assert result["success"] is True
            results = result["result"]["results"]
            assert len(results) == 0


class TestGrepToolMockMode:
    """Test mock mode functionality"""

    def test_mock_mode_enabled(self):
        """Test that mock mode returns mock results"""
        # Enable mock mode
        os.environ["USE_MOCK_APIS"] = "true"

        try:
            tool = GrepTool(pattern="test", output_mode="files_with_matches")
            result = tool.run()

            assert result["success"] is True
            assert result["result"]["mock"] is True
            assert "results" in result["result"]
            assert result["result"]["pattern_used"] == "test"
        finally:
            # Clean up
            os.environ.pop("USE_MOCK_APIS", None)

    def test_mock_mode_content_output(self):
        """Test mock mode with content output"""
        os.environ["USE_MOCK_APIS"] = "true"

        try:
            tool = GrepTool(pattern="test", output_mode="content")
            result = tool.run()

            assert result["success"] is True
            assert result["result"]["mock"] is True
            assert isinstance(result["result"]["results"], list)
            assert result["result"]["output_mode"] == "content"
        finally:
            os.environ.pop("USE_MOCK_APIS", None)

    def test_mock_mode_count_output(self):
        """Test mock mode with count output"""
        os.environ["USE_MOCK_APIS"] = "true"

        try:
            tool = GrepTool(pattern="test", output_mode="count")
            result = tool.run()

            assert result["success"] is True
            assert result["result"]["mock"] is True
            assert isinstance(result["result"]["results"], dict)
            assert result["result"]["output_mode"] == "count"
        finally:
            os.environ.pop("USE_MOCK_APIS", None)


class TestGrepToolMetadata:
    """Test metadata and response structure"""

    def test_metadata_includes_pattern(self):
        """Test that metadata includes the pattern used"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Test content")

            tool = GrepTool(pattern="Test", path=str(test_file))
            result = tool.run()

            assert result["success"] is True
            assert "metadata" in result
            assert result["metadata"]["pattern"] == "Test"

    def test_result_includes_search_stats(self):
        """Test that result includes search statistics"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir, "test.txt")
            test_file.write_text("Test content")

            tool = GrepTool(pattern="Test", path=str(test_file))
            result = tool.run()

            assert result["success"] is True
            assert "total_matches" in result["result"]
            assert "files_searched" in result["result"]
            assert "pattern_used" in result["result"]
            assert "output_mode" in result["result"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
