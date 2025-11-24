"""
Powerful content search tool with regex support
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class GrepTool(BaseTool):
    """
    Powerful content search tool with regex support

    Args:
        pattern: Regular expression pattern to search for
        path: File or directory to search in (defaults to current directory)
        output_mode: Output mode - content, files_with_matches, or count
        case_insensitive: Case insensitive search
        line_numbers: Show line numbers in content mode
        context_before: Lines to show before match (content mode)
        context_after: Lines to show after match (content mode)
        glob: Glob pattern to filter files (e.g., '*.js')
        file_type: File type filter (e.g., 'py', 'js')

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Search results based on output_mode
        - metadata: Additional information

    Example:
        >>> tool = GrepTool(pattern="Hello", path="/tmp", output_mode="files_with_matches")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "grep_tool"
    tool_category: str = "infrastructure"
    tool_description: str = "Powerful content search tool with regex support"

    # Parameters
    pattern: str = Field(..., description="Regular expression pattern to search for", min_length=1)
    path: Optional[str] = Field(
        None, description="File or directory to search in (defaults to current directory)"
    )
    output_mode: str = Field(
        "files_with_matches", description="Output mode: content, files_with_matches, or count"
    )
    case_insensitive: bool = Field(False, description="Case insensitive search")
    line_numbers: bool = Field(False, description="Show line numbers in content mode")
    context_before: int = Field(0, description="Lines to show before match (content mode)", ge=0)
    context_after: int = Field(0, description="Lines to show after match (content mode)", ge=0)
    glob: Optional[str] = Field(None, description="Glob pattern to filter files (e.g., '*.js')")
    file_type: Optional[str] = Field(None, description="File type filter (e.g., 'py', 'js')")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the grep_tool tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid parameters
            APIError: For search failures
        """

        self._logger.info(f"Executing {self.tool_name} with pattern={self.pattern}")
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()
            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "pattern": self.pattern},
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to search: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If pattern is empty, invalid regex, or output_mode is invalid
        """
        # Check pattern is not empty
        if not self.pattern or not self.pattern.strip():
            raise ValidationError(
                "Pattern cannot be empty",
                tool_name=self.tool_name,
                details={"pattern": self.pattern},
            )

        # Validate pattern is valid regex
        try:
            re.compile(self.pattern)
        except re.error as e:
            raise ValidationError(
                f"Invalid regex pattern: {str(e)}",
                tool_name=self.tool_name,
                details={"pattern": self.pattern, "regex_error": str(e)},
            )

        # Check output_mode is valid
        valid_modes = ["content", "files_with_matches", "count"]
        if self.output_mode not in valid_modes:
            raise ValidationError(
                f"Invalid output_mode: {self.output_mode}. Must be one of: {valid_modes}",
                tool_name=self.tool_name,
                details={"output_mode": self.output_mode, "valid_modes": valid_modes},
            )

        # If path provided, check it exists
        if self.path and not os.path.exists(self.path):
            raise ValidationError(
                f"Path does not exist: {self.path}",
                tool_name=self.tool_name,
                details={"path": self.path},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        if self.output_mode == "content":
            mock_results = [
                "1: mock line with pattern match",
                "2: another pattern match here",
            ]
        elif self.output_mode == "count":
            mock_results = {
                "/mock/file1.py": 3,
                "/mock/file2.py": 2,
            }
        else:  # files_with_matches
            mock_results = ["/mock/file1.py", "/mock/file2.py"]

        return {
            "success": True,
            "result": {
                "mock": True,
                "results": mock_results,
                "total_matches": 5,
                "files_searched": 10,
                "pattern_used": self.pattern,
                "output_mode": self.output_mode,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic - search files for pattern.

        Returns:
            Dict with search results

        Raises:
            APIError: If search operation fails
        """
        # Compile regex pattern with flags
        flags = re.IGNORECASE if self.case_insensitive else 0
        try:
            compiled_pattern = re.compile(self.pattern, flags)
        except re.error as e:
            raise APIError(f"Failed to compile regex: {e}", tool_name=self.tool_name)

        # Determine search path
        search_path = Path(self.path) if self.path else Path.cwd()

        # Collect files to search
        files_to_search = self._collect_files(search_path)

        # Search each file
        results = self._search_files(files_to_search, compiled_pattern)

        return results

    def _collect_files(self, search_path: Path) -> List[Path]:
        """
        Collect files to search based on path, glob, and file_type.

        Args:
            search_path: Path to start searching from

        Returns:
            List of file paths to search
        """
        files = []

        if search_path.is_file():
            # Single file
            files = [search_path]
        else:
            # Directory - walk recursively
            for root, _, filenames in os.walk(search_path):
                for filename in filenames:
                    file_path = Path(root) / filename

                    # Skip binary files and common non-text files
                    if self._should_skip_file(file_path):
                        continue

                    # Apply glob filter
                    if self.glob and not file_path.match(self.glob):
                        continue

                    # Apply file_type filter
                    if self.file_type and file_path.suffix != f".{self.file_type}":
                        continue

                    files.append(file_path)

        return files

    def _should_skip_file(self, file_path: Path) -> bool:
        """
        Check if file should be skipped (binary, hidden, etc.).

        Args:
            file_path: Path to check

        Returns:
            True if file should be skipped
        """
        # Skip hidden files
        if file_path.name.startswith("."):
            return True

        # Skip common binary extensions
        binary_extensions = {
            ".pyc",
            ".pyo",
            ".so",
            ".o",
            ".a",
            ".exe",
            ".dll",
            ".dylib",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".ico",
            ".webp",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".wav",
            ".flac",
            ".zip",
            ".tar",
            ".gz",
            ".bz2",
            ".7z",
            ".rar",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
        }

        if file_path.suffix.lower() in binary_extensions:
            return True

        # Try to detect binary files by reading first bytes
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                # Check for null bytes (common in binary files)
                if b"\x00" in chunk:
                    return True
        except (OSError, IOError):
            # If we can't read the file, skip it
            return True

        return False

    def _search_files(self, files: List[Path], pattern: re.Pattern) -> Dict[str, Any]:
        """
        Search files for pattern matches.

        Args:
            files: List of files to search
            pattern: Compiled regex pattern

        Returns:
            Dict with search results based on output_mode
        """
        total_matches = 0
        files_searched = 0

        if self.output_mode == "files_with_matches":
            results = self._search_files_with_matches(files, pattern)
            total_matches = sum(1 for _ in results)
        elif self.output_mode == "count":
            results = self._search_count(files, pattern)
            total_matches = sum(results.values())
        else:  # content
            results = self._search_content(files, pattern)
            total_matches = len(results)

        files_searched = len(files)

        return {
            "results": results,
            "total_matches": total_matches,
            "files_searched": files_searched,
            "pattern_used": self.pattern,
            "output_mode": self.output_mode,
        }

    def _search_files_with_matches(self, files: List[Path], pattern: re.Pattern) -> List[str]:
        """
        Search for files containing matches.

        Args:
            files: List of files to search
            pattern: Compiled regex pattern

        Returns:
            List of file paths containing matches
        """
        matching_files = []

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if pattern.search(content):
                        matching_files.append(str(file_path))
            except (OSError, IOError, UnicodeDecodeError):
                # Skip files we can't read
                continue

        return matching_files

    def _search_count(self, files: List[Path], pattern: re.Pattern) -> Dict[str, int]:
        """
        Count matches in each file.

        Args:
            files: List of files to search
            pattern: Compiled regex pattern

        Returns:
            Dict mapping file paths to match counts
        """
        counts = {}

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    if matches:
                        counts[str(file_path)] = len(matches)
            except (OSError, IOError, UnicodeDecodeError):
                # Skip files we can't read
                continue

        return counts

    def _search_content(self, files: List[Path], pattern: re.Pattern) -> List[str]:
        """
        Search for matching lines with optional context.

        Args:
            files: List of files to search
            pattern: Compiled regex pattern

        Returns:
            List of matching lines with optional context and line numbers
        """
        matching_lines = []

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                    for i, line in enumerate(lines):
                        if pattern.search(line):
                            # Add context before
                            if self.context_before > 0:
                                start = max(0, i - self.context_before)
                                for j in range(start, i):
                                    formatted = self._format_line(
                                        file_path, j, lines[j], is_match=False
                                    )
                                    if formatted not in matching_lines:
                                        matching_lines.append(formatted)

                            # Add matching line
                            formatted = self._format_line(file_path, i, line, is_match=True)
                            matching_lines.append(formatted)

                            # Add context after
                            if self.context_after > 0:
                                end = min(len(lines), i + self.context_after + 1)
                                for j in range(i + 1, end):
                                    formatted = self._format_line(
                                        file_path, j, lines[j], is_match=False
                                    )
                                    if formatted not in matching_lines:
                                        matching_lines.append(formatted)
            except (OSError, IOError, UnicodeDecodeError):
                # Skip files we can't read
                continue

        return matching_lines

    def _format_line(self, file_path: Path, line_num: int, line: str, is_match: bool) -> str:
        """
        Format a line for output.

        Args:
            file_path: Path to the file
            line_num: Line number (0-indexed)
            line: Line content
            is_match: Whether this is a matching line

        Returns:
            Formatted line string
        """
        line = line.rstrip()

        if self.line_numbers:
            # Use 1-indexed line numbers for display
            prefix = f"{file_path}:{line_num + 1}:"
            if is_match:
                return f"{prefix} {line}"
            else:
                return f"{prefix}- {line}"
        else:
            return f"{file_path}: {line}"


if __name__ == "__main__":
    print("Testing GrepTool...")

    import tempfile

    # Create test files
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir, "test.py")
        test_file.write_text("def hello():\n    print('Hello World')\n    return 42\n")

        test_file2 = Path(tmpdir, "test.js")
        test_file2.write_text("function hello() {\n    console.log('Hello');\n}\n")

        # Test 1: files_with_matches mode
        print("\nTest 1: files_with_matches mode")
        tool = GrepTool(pattern="Hello", path=tmpdir, output_mode="files_with_matches")
        result = tool.run()

        assert result.get("success") == True
        results = result.get("result", {}).get("results", [])
        assert len(results) == 2
        print(f"✅ Test 1 passed: Found {len(results)} files")

        # Test 2: content mode with line numbers
        print("\nTest 2: content mode with line numbers")
        tool = GrepTool(
            pattern="Hello", path=str(test_file), output_mode="content", line_numbers=True
        )
        result = tool.run()
        assert result.get("success") == True
        results = result.get("result", {}).get("results", [])
        assert len(results) >= 1
        assert ":2:" in results[0]  # Line number should be present
        print(f"✅ Test 2 passed: Content mode working")

        # Test 3: count mode
        print("\nTest 3: count mode")
        tool = GrepTool(pattern="hello", path=tmpdir, output_mode="count", case_insensitive=True)
        result = tool.run()
        assert result.get("success") == True
        results = result.get("result", {}).get("results", {})
        assert len(results) == 2
        print(f"✅ Test 3 passed: Count mode working")

        # Test 4: glob filtering
        print("\nTest 4: glob filtering")
        tool = GrepTool(pattern="hello", path=tmpdir, glob="*.py", output_mode="files_with_matches")
        result = tool.run()
        assert result.get("success") == True
        results = result.get("result", {}).get("results", [])
        assert len(results) == 1
        assert results[0].endswith(".py")
        print(f"✅ Test 4 passed: Glob filtering working")

        # Test 5: case insensitive
        print("\nTest 5: case insensitive search")
        tool = GrepTool(
            pattern="HELLO", path=tmpdir, case_insensitive=True, output_mode="files_with_matches"
        )
        result = tool.run()
        assert result.get("success") == True
        results = result.get("result", {}).get("results", [])
        assert len(results) == 2
        print(f"✅ Test 5 passed: Case insensitive working")

        # Test 6: Validation - empty pattern
        print("\nTest 6: Validation - empty pattern")
        try:
            bad_tool = GrepTool(pattern="   ", path=tmpdir)
            bad_tool.run()
            assert False, "Should have raised ValidationError"
        except Exception as e:
            print(f"✅ Test 6 passed: Validation working - {type(e).__name__}")

        # Test 7: Validation - invalid regex
        print("\nTest 7: Validation - invalid regex")
        try:
            bad_tool = GrepTool(pattern="[invalid", path=tmpdir)
            bad_tool.run()
            assert False, "Should have raised ValidationError"
        except Exception as e:
            print(f"✅ Test 7 passed: Regex validation working - {type(e).__name__}")

        # Test 8: Validation - invalid output_mode
        print("\nTest 8: Validation - invalid output_mode")
        try:
            bad_tool = GrepTool(pattern="test", path=tmpdir, output_mode="invalid")
            bad_tool.run()
            assert False, "Should have raised ValidationError"
        except Exception as e:
            print(f"✅ Test 8 passed: Output mode validation working - {type(e).__name__}")

        # Test 9: Context before/after
        print("\nTest 9: Context before/after")
        tool = GrepTool(
            pattern="print",
            path=str(test_file),
            output_mode="content",
            context_before=1,
            context_after=1,
            line_numbers=True,
        )
        result = tool.run()
        assert result.get("success") == True
        results = result.get("result", {}).get("results", [])
        assert len(results) >= 3  # Before, match, after
        print(f"✅ Test 9 passed: Context working")

    print("\n✅ All tests passed!")
