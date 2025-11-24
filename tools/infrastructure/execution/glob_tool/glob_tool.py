"""
Fast file pattern matching tool for finding files by name patterns
"""

import glob as glob_module
import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class GlobTool(BaseTool):
    """
    Fast file pattern matching for finding files by name patterns

    Args:
        pattern: Glob pattern like '**/*.js' or 'src/**/*.ts'
        path: Directory to search in (defaults to current working directory)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (matches, count, pattern, search_path)
        - metadata: Additional information

    Example:
        >>> tool = GlobTool(pattern="**/*.py", path="/home/user/project")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "glob_tool"
    tool_category: str = "infrastructure"
    tool_description: str = "Fast file pattern matching for finding files by name patterns"

    # Parameters
    pattern: str = Field(
        ..., description="Glob pattern like '**/*.js' or 'src/**/*.ts'", min_length=1
    )
    path: Optional[str] = Field(
        None, description="Directory to search in (defaults to current working directory)"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the glob_tool tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid parameters
            APIError: For execution failures
        """

        self._logger.info(
            f"Executing {self.tool_name} with pattern={self.pattern}, path={self.path}"
        )
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
                "metadata": {
                    "tool_name": self.tool_name,
                    "pattern": self.pattern,
                    "search_path": self.path or os.getcwd(),
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to execute glob pattern: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If pattern is empty or path is invalid
        """
        # Validate pattern
        if not self.pattern or not self.pattern.strip():
            raise ValidationError(
                "Pattern cannot be empty",
                tool_name=self.tool_name,
                details={"pattern": self.pattern},
            )

        # Validate path if provided
        if self.path:
            # Check if path exists
            if not os.path.exists(self.path):
                raise ValidationError(
                    f"Path does not exist: {self.path}",
                    tool_name=self.tool_name,
                    details={"path": self.path},
                )

            # Check if path is a directory
            if not os.path.isdir(self.path):
                raise ValidationError(
                    f"Path is not a directory: {self.path}",
                    tool_name=self.tool_name,
                    details={"path": self.path},
                )

        # Basic glob pattern validation - check for invalid characters
        invalid_chars = ["\x00"]  # Null byte
        for char in invalid_chars:
            if char in self.pattern:
                raise ValidationError(
                    f"Pattern contains invalid characters",
                    tool_name=self.tool_name,
                    details={"pattern": self.pattern},
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        search_path = self.path or os.getcwd()
        mock_matches = [
            os.path.join(search_path, "mock", "path", "file1.py"),
            os.path.join(search_path, "mock", "path", "file2.py"),
            os.path.join(search_path, "mock", "path", "subdir", "file3.py"),
        ]

        return {
            "success": True,
            "result": {
                "mock": True,
                "matches": mock_matches,
                "count": len(mock_matches),
                "pattern_used": self.pattern,
                "search_path": search_path,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "pattern": self.pattern,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic.

        Performs glob pattern matching and returns sorted results.

        Returns:
            Dict with matches, count, pattern_used, search_path

        Raises:
            APIError: If glob operation fails
        """
        try:
            # Determine search directory
            search_path = self.path if self.path else os.getcwd()

            # Change to search directory if needed
            original_cwd = os.getcwd()
            if self.path:
                os.chdir(self.path)

            try:
                # Perform glob search
                # Use recursive=True to enable ** pattern matching
                matches = glob_module.glob(self.pattern, recursive=True)

                # Convert to absolute paths
                if self.path:
                    matches = [os.path.abspath(match) for match in matches]
                else:
                    matches = [os.path.abspath(match) for match in matches]

                # Get modification times and sort by most recent first
                matches_with_mtime = []
                for match in matches:
                    try:
                        mtime = os.path.getmtime(match)
                        matches_with_mtime.append((match, mtime))
                    except OSError:
                        # If we can't get mtime, add with time 0
                        matches_with_mtime.append((match, 0))

                # Sort by modification time (most recent first)
                matches_with_mtime.sort(key=lambda x: x[1], reverse=True)
                sorted_matches = [match for match, _ in matches_with_mtime]

                return {
                    "matches": sorted_matches,
                    "count": len(sorted_matches),
                    "pattern_used": self.pattern,
                    "search_path": search_path,
                }

            finally:
                # Restore original directory
                os.chdir(original_cwd)

        except Exception as e:
            self._logger.error(f"Error in glob operation: {str(e)}", exc_info=True)
            raise APIError(f"Glob operation failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    print("Testing GlobTool...")

    import tempfile
    from pathlib import Path

    # Disable rate limiting for tests
    os.environ["DISABLE_RATE_LIMITING"] = "true"

    # Test 1: Mock mode test
    print("\nTest 1: Mock mode test")
    os.environ["USE_MOCK_APIS"] = "true"
    tool = GlobTool(pattern="**/*.py")
    result = tool.run()

    assert result.get("success") == True
    assert "matches" in result.get("result", {})
    assert result.get("result", {}).get("count") == 3
    print("✅ Test 1 passed: Mock mode working")

    # Test 2-5: Real file system tests
    os.environ["USE_MOCK_APIS"] = "false"

    # Create test directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        Path(tmpdir, "test1.py").touch()
        Path(tmpdir, "test2.py").touch()
        Path(tmpdir, "test.txt").touch()
        subdir = Path(tmpdir, "subdir")
        subdir.mkdir()
        Path(subdir, "test3.py").touch()
        Path(subdir, "test4.js").touch()

        # Test 2: Pattern matching *.py
        print("\nTest 2: Pattern matching *.py (non-recursive)")
        tool = GlobTool(pattern="*.py", path=tmpdir)
        result = tool.run()

        assert result.get("success") == True
        matches = result.get("result", {}).get("matches", [])
        assert len(matches) == 2  # test1.py, test2.py (not subdir/test3.py)
        assert all(m.endswith(".py") for m in matches)
        print(f"✅ Test 2 passed: Found {len(matches)} Python files")

        # Test 3: Recursive pattern matching **/*.py
        print("\nTest 3: Recursive pattern matching **/*.py")
        tool = GlobTool(pattern="**/*.py", path=tmpdir)
        result = tool.run()

        assert result.get("success") == True
        matches = result.get("result", {}).get("matches", [])
        assert len(matches) == 3  # test1.py, test2.py, test3.py
        assert all(m.endswith(".py") for m in matches)
        print(f"✅ Test 3 passed: Found {len(matches)} Python files recursively")

        # Test 4: No matches scenario
        print("\nTest 4: No matches scenario")
        tool = GlobTool(pattern="*.rs", path=tmpdir)
        result = tool.run()

        assert result.get("success") == True
        matches = result.get("result", {}).get("matches", [])
        assert len(matches) == 0
        print("✅ Test 4 passed: No matches found for *.rs")

        # Test 5: Current directory default
        print("\nTest 5: Current directory default (no path specified)")
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            tool = GlobTool(pattern="*.txt")
            result = tool.run()

            assert result.get("success") == True
            matches = result.get("result", {}).get("matches", [])
            assert len(matches) == 1  # test.txt
            print("✅ Test 5 passed: Default to current directory working")
        finally:
            os.chdir(original_cwd)

    # Test 6: Validation - empty pattern
    print("\nTest 6: Validation - empty pattern")
    os.environ["USE_MOCK_APIS"] = "false"
    bad_tool = GlobTool(pattern="   ")
    result = bad_tool.run()
    assert result.get("success") == False
    assert "VALIDATION_ERROR" in result.get("error", {}).get("code", "")
    print(f"✅ Test 6 passed: Empty pattern validation")

    # Test 7: Validation - invalid path
    print("\nTest 7: Validation - invalid path (doesn't exist)")
    bad_tool = GlobTool(pattern="*.py", path="/nonexistent/path/12345")
    result = bad_tool.run()
    assert result.get("success") == False
    assert "VALIDATION_ERROR" in result.get("error", {}).get("code", "")
    assert "exist" in result.get("error", {}).get("message", "").lower()
    print(f"✅ Test 7 passed: Invalid path validation")

    # Test 8: Validation - path is file, not directory
    print("\nTest 8: Validation - path is file, not directory")
    with tempfile.NamedTemporaryFile() as tmpfile:
        bad_tool = GlobTool(pattern="*.py", path=tmpfile.name)
        result = bad_tool.run()
        assert result.get("success") == False
        assert "VALIDATION_ERROR" in result.get("error", {}).get("code", "")
        assert "directory" in result.get("error", {}).get("message", "").lower()
        print(f"✅ Test 8 passed: Path is file validation")

    print("\n✅ All tests passed!")
