"""
Fetch and summarize text-based documents, answering specific questions
"""

from typing import Any, Dict
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class SummarizeLargeDocument(BaseTool):
    """
    Fetch and summarize text-based documents, answering specific questions

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = SummarizeLargeDocument(input="http://example.com/document")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "summarize_large_document"
    tool_category: str = "content"
    tool_description: str = "Fetch and summarize text-based documents, answering specific questions"

    # Parameters
    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the summarize_large_document tool.

        Returns:
            Dict with results
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
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.input.startswith("http://") and not self.input.startswith("https://"):
            raise ValidationError(
                "Input must be a valid URL starting with http:// or https://",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "summary": "This is a mock summary of the document.",
                "questions": {
                    "What is the main topic?": "Mock topic",
                    "What are the key points?": ["Mock point 1", "Mock point 2"],
                },
            },
            "metadata": {"mock_mode": True, "tool_version": "1.0.0"},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        try:
            response = requests.get(self.input, timeout=30)
            response.raise_for_status()
            document_text = response.text

            # Here, you would implement the logic to summarize the document
            # and answer specific questions. For demonstration, we'll return
            # a simple mock result.
            summary = "This is a summary of the document."
            questions = {
                "What is the main topic?": "Sample topic",
                "What are the key points?": ["Point 1", "Point 2"],
            }

            return {"summary": summary, "questions": questions}

        except requests.RequestException as e:
            raise APIError(f"Error fetching document: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = SummarizeLargeDocument(input="https://example.com/document.pdf")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
