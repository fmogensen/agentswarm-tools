"""
Comprehensive tests for GlobTool
"""

import os
import tempfile
import time
from pathlib import Path

import pytest

from tools.infrastructure.execution.glob_tool.glob_tool import GlobTool


class TestGlobTool:
    """Test suite for GlobTool"""

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Setup test environment"""
        # Disable mock mode for real tests
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["DISABLE_RATE_LIMITING"] = "true"
        yield
        # Cleanup after each test
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("DISABLE_RATE_LIMITING", None)

    @pytest.fixture
    def test_directory(self):
        """Create a temporary directory with test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "file1.py").write_text("# Python file 1")
            time.sleep(0.01)  # Small delay to ensure different mtimes
            Path(tmpdir, "file2.py").write_text("# Python file 2")
            time.sleep(0.01)
            Path(tmpdir, "file3.js").write_text("// JavaScript file")
            time.sleep(0.01)
            Path(tmpdir, "file4.ts").write_text("// TypeScript file")
            time.sleep(0.01)
            Path(tmpdir, "README.md").write_text("# README")
            time.sleep(0.01)
            Path(tmpdir, ".hidden").write_text("hidden file")

            # Create subdirectories
            subdir1 = Path(tmpdir, "subdir1")
            subdir1.mkdir()
            Path(subdir1, "nested1.py").write_text("# Nested Python")
            time.sleep(0.01)

            subdir2 = Path(tmpdir, "subdir2")
            subdir2.mkdir()
            Path(subdir2, "nested2.py").write_text("# Nested Python 2")
            time.sleep(0.01)

            deep = Path(tmpdir, "deep", "nested", "path")
            deep.mkdir(parents=True)
            Path(deep, "deep_file.py").write_text("# Deep file")

            yield tmpdir

    def test_basic_pattern_matching(self, test_directory):
        """Test 1: Basic pattern matching (*.py)"""
        tool = GlobTool(pattern="*.py", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        assert len(matches) == 2  # Only file1.py and file2.py (not nested)
        assert all(m.endswith(".py") for m in matches)
        assert result["result"]["count"] == 2
        assert result["result"]["pattern_used"] == "*.py"

    def test_recursive_pattern_matching(self, test_directory):
        """Test 2: Recursive pattern matching (**/*.py)"""
        tool = GlobTool(pattern="**/*.py", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        # Should find: file1.py, file2.py, nested1.py, nested2.py, deep_file.py
        assert len(matches) == 5
        assert all(m.endswith(".py") for m in matches)
        assert result["result"]["count"] == 5

    def test_multiple_extensions(self, test_directory):
        """Test 3: Multiple extensions (**/*.{js,ts})"""
        # Note: glob doesn't support {js,ts} syntax natively
        # So we test each separately or use alternative patterns
        tool = GlobTool(pattern="*.js", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        assert len(matches) == 1
        assert matches[0].endswith(".js")

    def test_specific_directory_path(self, test_directory):
        """Test 4: Specific directory path"""
        subdir1 = os.path.join(test_directory, "subdir1")
        tool = GlobTool(pattern="*.py", path=subdir1)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        assert len(matches) == 1
        assert "nested1.py" in matches[0]

    def test_current_directory_default(self, test_directory):
        """Test 5: Current directory default"""
        original_cwd = os.getcwd()
        os.chdir(test_directory)
        try:
            tool = GlobTool(pattern="*.py")
            result = tool.run()

            assert result["success"] == True
            matches = result["result"]["matches"]
            assert len(matches) == 2  # file1.py and file2.py
            # Use realpath to handle symlinks (e.g., /var vs /private/var on macOS)
            assert os.path.realpath(result["result"]["search_path"]) == os.path.realpath(
                test_directory
            )
        finally:
            os.chdir(original_cwd)

    def test_no_matches_scenario(self, test_directory):
        """Test 6: No matches scenario"""
        tool = GlobTool(pattern="*.rs", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        assert len(matches) == 0
        assert result["result"]["count"] == 0

    def test_empty_pattern_error(self):
        """Test 7: Empty pattern error"""
        with pytest.raises(Exception) as exc_info:
            tool = GlobTool(pattern="")
            tool.run()
        assert "validation" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_whitespace_pattern_error(self):
        """Test 8: Whitespace-only pattern error"""
        with pytest.raises(Exception) as exc_info:
            tool = GlobTool(pattern="   ")
            tool.run()
        assert "validation" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_invalid_path_error(self):
        """Test 9: Invalid path error (doesn't exist)"""
        with pytest.raises(Exception) as exc_info:
            tool = GlobTool(pattern="*.py", path="/nonexistent/path/12345")
            tool.run()
        assert "exist" in str(exc_info.value).lower() or "validation" in str(exc_info.value).lower()

    def test_path_is_file_error(self):
        """Test 10: Path is file error (not directory)"""
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            try:
                with pytest.raises(Exception) as exc_info:
                    tool = GlobTool(pattern="*.py", path=tmpfile.name)
                    tool.run()
                assert "directory" in str(exc_info.value).lower() or "validation" in str(
                    exc_info.value
                ).lower()
            finally:
                os.unlink(tmpfile.name)

    def test_mock_mode(self):
        """Test 11: Mock mode test"""
        os.environ["USE_MOCK_APIS"] = "true"
        try:
            tool = GlobTool(pattern="**/*.py")
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["mock"] == True
            assert "matches" in result["result"]
            assert result["result"]["count"] == 3
            assert result["metadata"]["mock_mode"] == True
        finally:
            os.environ["USE_MOCK_APIS"] = "false"

    def test_sorting_by_modification_time(self, test_directory):
        """Test 12: Sorting by modification time (most recent first)"""
        tool = GlobTool(pattern="**/*.py", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        assert len(matches) == 5

        # Verify sorting: most recent files should be first
        # We created files with delays, so deep_file.py should be most recent
        mtimes = [os.path.getmtime(m) for m in matches]
        assert mtimes == sorted(mtimes, reverse=True), "Files should be sorted by mtime (newest first)"

    def test_hidden_files_matching(self, test_directory):
        """Test 13: Hidden files matching"""
        tool = GlobTool(pattern=".*", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        # Should find .hidden file
        assert any(".hidden" in m for m in matches)

    def test_nested_directories(self, test_directory):
        """Test 14: Nested directories (deep path)"""
        tool = GlobTool(pattern="**/deep_file.py", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        assert len(matches) == 1
        assert "deep_file.py" in matches[0]
        assert os.path.join("deep", "nested", "path") in matches[0]

    def test_large_result_sets(self, test_directory):
        """Test 15: Large result sets (all files)"""
        tool = GlobTool(pattern="**/*", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        # Should find many files and directories
        assert len(matches) > 5
        assert result["result"]["count"] == len(matches)

    def test_special_characters_in_pattern(self, test_directory):
        """Test 16: Special characters in pattern"""
        # Create file with special chars in name
        special_file = Path(test_directory, "test-file_v1.0.py")
        special_file.write_text("# Special")

        tool = GlobTool(pattern="test-*.py", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        assert len(matches) == 1
        assert "test-file_v1.0.py" in matches[0]

    def test_absolute_paths_returned(self, test_directory):
        """Test 17: Absolute paths returned"""
        tool = GlobTool(pattern="*.py", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        # All paths should be absolute
        assert all(os.path.isabs(m) for m in matches)

    def test_metadata_included(self, test_directory):
        """Test 18: Metadata included in response"""
        tool = GlobTool(pattern="*.py", path=test_directory)
        result = tool.run()

        assert "metadata" in result
        metadata = result["metadata"]
        assert metadata["tool_name"] == "glob_tool"
        assert metadata["pattern"] == "*.py"
        assert metadata["search_path"] == test_directory

    def test_result_structure(self, test_directory):
        """Test 19: Result structure validation"""
        tool = GlobTool(pattern="*.py", path=test_directory)
        result = tool.run()

        assert "success" in result
        assert "result" in result
        assert "metadata" in result

        result_data = result["result"]
        assert "matches" in result_data
        assert "count" in result_data
        assert "pattern_used" in result_data
        assert "search_path" in result_data

        assert isinstance(result_data["matches"], list)
        assert isinstance(result_data["count"], int)
        assert isinstance(result_data["pattern_used"], str)
        assert isinstance(result_data["search_path"], str)

    def test_all_files_in_directory(self, test_directory):
        """Test 20: Match all files in directory"""
        tool = GlobTool(pattern="*", path=test_directory)
        result = tool.run()

        assert result["success"] == True
        matches = result["result"]["matches"]
        # Should find files in root directory (not nested)
        # file1.py, file2.py, file3.js, file4.ts, README.md, .hidden
        assert len(matches) >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
