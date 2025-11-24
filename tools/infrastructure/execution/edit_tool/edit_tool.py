"""
Perform exact string replacements in files for surgical code edits
"""

import os
from typing import Any, Dict

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class EditTool(BaseTool):
    """
    Perform exact string replacements in files for surgical code edits

    Args:
        file_path: Absolute path to file to modify
        old_string: Exact text to replace
        new_string: Text to replace with
        replace_all: Replace all occurrences (default: false)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (lines_changed, occurrences_replaced, file_path)
        - metadata: Additional information

    Example:
        >>> tool = EditTool(
        ...     file_path="/tmp/example.txt",
        ...     old_string="Hello World",
        ...     new_string="Hi There",
        ...     replace_all=False
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "edit_tool"
    tool_category: str = "infrastructure"
    tool_description: str = "Performs exact string replacements in files for surgical code edits"

    # Parameters
    file_path: str = Field(..., description="Absolute path to file to modify", min_length=1)
    old_string: str = Field(..., description="Exact text to replace", min_length=1)
    new_string: str = Field(..., description="Text to replace with")
    replace_all: bool = Field(False, description="Replace all occurrences (default: false)")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the edit_tool tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid input
            APIError: For execution failures
        """

        self._logger.info(
            f"Executing {self.tool_name} with file_path={self.file_path}, "
            f"old_string_length={len(self.old_string)}, new_string_length={len(self.new_string)}, "
            f"replace_all={self.replace_all}"
        )
        # 1. CHECK MOCK MODE (before validation to allow mocking with non-existent files)
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 2. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 3. EXECUTE
        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "file_path": self.file_path},
            }
        except ValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to edit file: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input is invalid
        """
        # Check file_path is absolute
        if not os.path.isabs(self.file_path):
            raise ValidationError(
                f"File path must be absolute, got: {self.file_path}",
                tool_name=self.tool_name,
                details={"file_path": self.file_path},
            )

        # Check file exists
        if not os.path.exists(self.file_path):
            raise ValidationError(
                f"File not found: {self.file_path}",
                tool_name=self.tool_name,
                details={"file_path": self.file_path},
            )

        # Check file is readable
        if not os.path.isfile(self.file_path):
            raise ValidationError(
                f"Not a file: {self.file_path}",
                tool_name=self.tool_name,
                details={"file_path": self.file_path},
            )

        # Check old_string and new_string are different
        if self.old_string == self.new_string:
            raise ValidationError(
                "old_string and new_string must be different",
                tool_name=self.tool_name,
                details={"old_string": self.old_string, "new_string": self.new_string},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "mock": True,
                "lines_changed": 5,
                "occurrences_replaced": 1 if not self.replace_all else 3,
                "file_path": self.file_path,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic: Perform exact string replacement in file.

        Returns:
            Dict with lines_changed, occurrences_replaced, file_path

        Raises:
            ValidationError: If old_string not found or not unique
            APIError: If file operations fail
        """
        try:
            # Read file contents
            with open(self.file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Count occurrences of old_string
            occurrences = original_content.count(self.old_string)

            # Validate occurrences
            if occurrences == 0:
                raise ValidationError(
                    f"old_string not found in file: {self.file_path}",
                    tool_name=self.tool_name,
                    details={"old_string": self.old_string[:100]},  # Truncate for readability
                )

            if occurrences > 1 and not self.replace_all:
                raise ValidationError(
                    f"old_string found {occurrences} times in file. Use replace_all=True to replace all occurrences, or provide a more specific old_string.",
                    tool_name=self.tool_name,
                    details={"occurrences": occurrences, "file_path": self.file_path},
                )

            # Perform replacement
            if self.replace_all:
                new_content = original_content.replace(self.old_string, self.new_string)
                occurrences_replaced = occurrences
            else:
                # Replace only first occurrence
                new_content = original_content.replace(self.old_string, self.new_string, 1)
                occurrences_replaced = 1

            # Count lines changed
            original_lines = original_content.splitlines()
            new_lines = new_content.splitlines()
            lines_changed = sum(1 for old, new in zip(original_lines, new_lines) if old != new)
            # Account for line count differences
            lines_changed += abs(len(original_lines) - len(new_lines))

            # Write modified content back to file
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return {
                "lines_changed": lines_changed,
                "occurrences_replaced": occurrences_replaced,
                "file_path": self.file_path,
            }

        except ValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to edit file: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    print("Testing EditTool...")

    import os
    import tempfile

    # Disable rate limiting for tests
    os.environ["DISABLE_RATE_LIMITING"] = "true"

    # Test with real file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Hello World\nHello World\n")
        test_file = f.name

    # Enable exception raising for tests
    os.environ["RAISE_TOOL_EXCEPTIONS"] = "true"

    try:
        # Test 1: Single replacement (should fail - not unique)
        print("\nTest 1: Single replacement with non-unique string")
        try:
            tool = EditTool(file_path=test_file, old_string="Hello World", new_string="Hi There")
            result = tool.run()
            print("❌ Test 1 failed: Should have raised ValidationError")
        except (ValidationError, Exception) as e:
            if "found 2 times" in str(e) or isinstance(e, ValidationError):
                print(f"✅ Test 1 passed: Correctly raised ValidationError - {e}")
            else:
                print(f"❌ Test 1 failed with wrong error: {e}")
                raise

        # Test 2: Replace all occurrences
        print("\nTest 2: Replace all occurrences")
        tool = EditTool(
            file_path=test_file, old_string="Hello World", new_string="Hi There", replace_all=True
        )
        result = tool.run()
        assert result.get("success") is True
        assert result.get("result", {}).get("occurrences_replaced") == 2

        # Verify file contents
        with open(test_file) as f:
            content = f.read()
            assert "Hi There" in content
            assert content.count("Hello World") == 0  # All replaced

        print(f"✅ Test 2 passed: All occurrences replaced")
        print(f"   Occurrences replaced: {result.get('result', {}).get('occurrences_replaced')}")

        # Test 3: Single replacement with unique string
        print("\nTest 3: Single replacement with unique string")
        with open(test_file, "w") as f:
            f.write("First line\nSecond line\nThird line\n")

        tool = EditTool(file_path=test_file, old_string="Second line", new_string="Modified line")
        result = tool.run()
        assert result.get("success") is True
        assert result.get("result", {}).get("occurrences_replaced") == 1

        # Verify file contents
        with open(test_file) as f:
            content = f.read()
            assert "Modified line" in content
            assert "Second line" not in content

        print(f"✅ Test 3 passed: Single occurrence replaced correctly")

        # Test 4: Non-absolute path error
        print("\nTest 4: Non-absolute path error")
        try:
            tool = EditTool(file_path="relative/path.txt", old_string="old", new_string="new")
            result = tool.run()
            print("❌ Test 4 failed: Should have raised ValidationError")
        except ValidationError as e:
            print(f"✅ Test 4 passed: Correctly raised ValidationError for non-absolute path")

        # Test 5: File not found error
        print("\nTest 5: File not found error")
        try:
            tool = EditTool(
                file_path="/tmp/nonexistent_file_12345.txt", old_string="old", new_string="new"
            )
            result = tool.run()
            print("❌ Test 5 failed: Should have raised ValidationError")
        except ValidationError as e:
            print(f"✅ Test 5 passed: Correctly raised ValidationError for missing file")

        # Test 6: Old string == new string error
        print("\nTest 6: Old string == new string error")
        try:
            tool = EditTool(file_path=test_file, old_string="same", new_string="same")
            result = tool.run()
            print("❌ Test 6 failed: Should have raised ValidationError")
        except ValidationError as e:
            print(f"✅ Test 6 passed: Correctly raised ValidationError for identical strings")

        # Test 7: Old string not found error
        print("\nTest 7: Old string not found error")
        try:
            tool = EditTool(
                file_path=test_file, old_string="nonexistent string", new_string="new"
            )
            result = tool.run()
            print("❌ Test 7 failed: Should have raised ValidationError")
        except ValidationError as e:
            print(f"✅ Test 7 passed: Correctly raised ValidationError for string not found")

        print("\n✅ All EditTool tests passed!")

    finally:
        os.unlink(test_file)
