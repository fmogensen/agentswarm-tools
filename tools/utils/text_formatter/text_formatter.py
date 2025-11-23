"""
Format and clean text data.
"""

import os
import re
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class TextFormatter(BaseTool):
    """
    Format and clean text data with various transformations.

    Args:
        text: Text to format
        operations: List of operations to apply (trim, lowercase, uppercase, title, remove_whitespace, remove_punctuation, normalize_spaces)
        custom_replacements: Optional dict of custom find/replace pairs
        strip_html: Whether to strip HTML tags (default: False)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Formatted text and transformation info
        - metadata: Operations applied and statistics

    Example:
        >>> tool = TextFormatter(
        ...     text="  Hello World!  ",
        ...     operations=["trim", "lowercase"]
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "text_formatter"
    tool_category: str = "utils"

    # Parameters
    text: str = Field(..., description="Text to format", min_length=1)
    operations: List[str] = Field(
        ...,
        description="List of operations: trim, lowercase, uppercase, title, remove_whitespace, remove_punctuation, normalize_spaces, remove_numbers, remove_special_chars",
        min_items=1,
    )
    custom_replacements: Optional[Dict[str, str]] = Field(
        None, description="Optional custom find/replace pairs"
    )
    strip_html: bool = Field(False, description="Whether to strip HTML tags")

    def _execute(self) -> Dict[str, Any]:
        """Execute text formatting."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "operations_count": len(self.operations),
                    "operations_applied": self.operations,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            raise APIError(f"Text formatting failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        valid_operations = [
            "trim",
            "lowercase",
            "uppercase",
            "title",
            "remove_whitespace",
            "remove_punctuation",
            "normalize_spaces",
            "remove_numbers",
            "remove_special_chars",
        ]

        for operation in self.operations:
            if operation not in valid_operations:
                raise ValidationError(
                    f"Invalid operation '{operation}'. Must be one of {valid_operations}",
                    tool_name=self.tool_name,
                    field="operations",
                )

        if not self.text or not isinstance(self.text, str):
            raise ValidationError(
                "text must be a non-empty string", tool_name=self.tool_name, field="text"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        return {
            "success": True,
            "result": {
                "original_text": self.text,
                "formatted_text": "[MOCK] Formatted text here",
                "operations_applied": self.operations,
                "changes_made": len(self.operations),
                "original_length": len(self.text),
                "formatted_length": 25,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "operations_count": len(self.operations),
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Format the text."""
        original_text = self.text
        formatted_text = self.text
        changes_log = []

        # Strip HTML if requested
        if self.strip_html:
            before_length = len(formatted_text)
            formatted_text = self._strip_html_tags(formatted_text)
            if len(formatted_text) != before_length:
                changes_log.append("Stripped HTML tags")

        # Apply each operation in order
        for operation in self.operations:
            before = formatted_text

            if operation == "trim":
                formatted_text = formatted_text.strip()

            elif operation == "lowercase":
                formatted_text = formatted_text.lower()

            elif operation == "uppercase":
                formatted_text = formatted_text.upper()

            elif operation == "title":
                formatted_text = formatted_text.title()

            elif operation == "remove_whitespace":
                formatted_text = formatted_text.replace(" ", "").replace("\t", "").replace("\n", "")

            elif operation == "remove_punctuation":
                formatted_text = re.sub(r"[^\w\s]", "", formatted_text)

            elif operation == "normalize_spaces":
                # Replace multiple spaces with single space
                formatted_text = re.sub(r"\s+", " ", formatted_text)

            elif operation == "remove_numbers":
                formatted_text = re.sub(r"\d+", "", formatted_text)

            elif operation == "remove_special_chars":
                # Keep only alphanumeric and spaces
                formatted_text = re.sub(r"[^a-zA-Z0-9\s]", "", formatted_text)

            if before != formatted_text:
                changes_log.append(f"Applied {operation}")

        # Apply custom replacements if provided
        if self.custom_replacements:
            for find, replace in self.custom_replacements.items():
                before = formatted_text
                formatted_text = formatted_text.replace(find, replace)
                if before != formatted_text:
                    changes_log.append(f"Replaced '{find}' with '{replace}'")

        return {
            "original_text": original_text,
            "formatted_text": formatted_text,
            "operations_applied": self.operations,
            "changes_made": len(changes_log),
            "changes_log": changes_log,
            "original_length": len(original_text),
            "formatted_length": len(formatted_text),
            "length_change": len(formatted_text) - len(original_text),
        }

    def _strip_html_tags(self, text: str) -> str:
        """Remove HTML tags from text."""
        # Simple HTML tag removal
        clean_text = re.sub(r"<[^>]+>", "", text)
        return clean_text


if __name__ == "__main__":
    print("Testing TextFormatter...")

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    tool = TextFormatter(text="  Hello World!  ", operations=["trim", "lowercase"])
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True
    print("TextFormatter test passed!")
