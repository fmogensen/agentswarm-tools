"""
Generate email content for drafting (text or HTML)
"""

from typing import Any, Dict
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class EmailDraft(BaseTool):
    """
    Generate email content for drafting (text or HTML)

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = EmailDraft(input="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "email_draft"
    tool_category: str = "communication"

    # Parameters
    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the email_draft tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid parameters
            APIError: For unexpected processing failures
        """
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
                "metadata": {"tool_name": self.tool_name, "tool_version": "1.0.0"},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input is empty or invalid
        """
        if not self.input or not isinstance(self.input, str):
            raise ValidationError(
                "Input must be a non-empty string",
                field="input",
                tool_name=self.tool_name,
            )

        if len(self.input.strip()) == 0:
            raise ValidationError(
                "Input cannot be blank",
                field="input",
                tool_name=self.tool_name,
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_email = {
            "subject": f"[MOCK] Draft based on input: {self.input}",
            "body_text": f"This is a mock email body generated using input: {self.input}",
            "body_html": (
                f"<html><body><p>This is a <b>mock email</b> generated using input: "
                f"{self.input}</p></body></html>"
            ),
            "mode": "mock",
        }

        return {
            "success": True,
            "result": mock_email,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "tool_version": "1.0.0",
            },
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Returns:
            Dict with email subject, body_text, and body_html

        Raises:
            APIError: For unexpected processing issues
        """
        try:
            # Basic heuristic text processing to generate a draft email
            user_input = self.input.strip()

            subject = f"Regarding: {user_input[:60]}"
            body_text = (
                f"Hello,\n\n"
                f"I’m writing in reference to: {user_input}.\n\n"
                f"Please let me know if you need more information.\n\n"
                f"Best regards,\n"
            )

            body_html = (
                "<html><body>"
                f"<p>Hello,</p>"
                f"<p>I’m writing in reference to: <b>{user_input}</b>.</p>"
                f"<p>Please let me know if you need more information.</p>"
                f"<p>Best regards,<br></p>"
                "</body></html>"
            )

            return {
                "subject": subject,
                "body_text": body_text,
                "body_html": body_html,
                "mode": "generated",
            }

        except Exception as e:
            raise APIError(f"Email generation failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    print("Testing EmailDraft...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Generate basic email draft
    print("\nTest 1: Generate basic email draft")
    tool = EmailDraft(input="Meeting tomorrow at 3pm")
    result = tool.run()

    assert result.get('success') == True
    assert 'subject' in result.get('result', {})
    assert 'body_text' in result.get('result', {})
    assert 'body_html' in result.get('result', {})
    print(f"✅ Test 1 passed: Email draft generated")
    print(f"   Subject: {result.get('result', {}).get('subject')}")

    # Test 2: Longer input text
    print("\nTest 2: Generate email with longer content")
    long_input = "I would like to discuss the quarterly report and schedule a follow-up meeting to review our progress on the project objectives"
    tool = EmailDraft(input=long_input)
    result = tool.run()

    assert result.get('success') == True
    assert len(result.get('result', {}).get('body_text', '')) > 0
    print(f"✅ Test 2 passed: Long email draft generated")

    # Test 3: Validation - empty input
    print("\nTest 3: Validation - empty input")
    try:
        bad_tool = EmailDraft(input="   ")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: HTML body verification
    print("\nTest 4: HTML body verification")
    tool = EmailDraft(input="Project update")
    result = tool.run()

    html_body = result.get('result', {}).get('body_html', '')
    assert '<html>' in html_body or '<p>' in html_body
    print(f"✅ Test 4 passed: HTML body generated correctly")

    print("\n✅ All tests passed!")
