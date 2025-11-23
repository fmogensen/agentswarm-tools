"""
Read and process OneDrive/SharePoint files, answer questions about content
"""

from typing import Any, Dict
from pydantic import Field
import os
import base64
import json

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class OnedriveFileRead(BaseTool):
    """
    Read and process OneDrive/SharePoint files, answer questions about content

    Args:
        input: Primary input parameter containing file descriptor or query

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information
    """

    # Tool metadata
    tool_name: str = "onedrive_file_read"
    tool_category: str = "infrastructure"
    tool_description: str = (
        "Read and process OneDrive/SharePoint files, answer questions about content"
    )

    # Parameters
    input: str = Field(
        ...,
        description="Primary input parameter. Expected to be a JSON string with fields such as 'file_path', 'drive_id', 'item_id', or 'question'.",
        min_length=1,
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the onedrive_file_read tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: If parameters are invalid
            APIError: If external API calls fail
        """
        self._validate_parameters()

        if self._should_use_mock():
            return self._generate_mock_results()

        try:
            result = self._process()
            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "version": "1.0.0"},
            }
        except Exception as e:
            raise APIError(f"Failed to read/process OneDrive file: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input is empty or malformed
        """
        if not self.input or not self.input.strip():
            raise ValidationError(
                "Input cannot be empty",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        try:
            parsed = json.loads(self.input)
            if not isinstance(parsed, dict):
                raise ValueError("Input JSON must decode to an object")
        except Exception as e:
            raise ValidationError(
                f"Input must be valid JSON string: {e}",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        required_keys = ["query", "file_reference"]
        # Minimal requirement: at least one key must exist
        if not any(key in parsed for key in required_keys):
            raise ValidationError(
                "Input JSON must include at least one of: 'query', 'file_reference'",
                tool_name=self.tool_name,
                details={"input_keys": list(parsed.keys())},
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
                "content_excerpt": "This is a mock representation of file content.",
                "answer": "Mock answer to the provided query.",
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "version": "1.0.0",
            },
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Returns:
            Any processed result for file content and query response.

        Raises:
            APIError: If file retrieval or parsing fails
        """
        data = json.loads(self.input)

        file_ref = data.get("file_reference")
        query = data.get("query", "").strip() if data.get("query") else None

        if not file_ref:
            raise ValidationError(
                "Missing 'file_reference' in input",
                tool_name=self.tool_name,
                details={"input": data},
            )

        try:
            # Expecting base64 encoded file contents for simplicity
            if "base64_content" in file_ref:
                try:
                    decoded_bytes = base64.b64decode(file_ref["base64_content"])
                    content = decoded_bytes.decode("utf-8", errors="replace")
                except Exception as e:
                    raise APIError(
                        f"Failed to decode base64 file content: {e}",
                        tool_name=self.tool_name,
                    )
            else:
                raise ValidationError(
                    "file_reference must include 'base64_content'",
                    tool_name=self.tool_name,
                    details={"file_reference": file_ref},
                )

            if query:
                answer = self._answer_question_about_content(query, content)
            else:
                answer = None

            return {
                "file_content_excerpt": content[:500],
                "content_length": len(content),
                "answer": answer,
            }

        except Exception as e:
            raise APIError(f"Error reading OneDrive file: {e}", tool_name=self.tool_name)

    def _answer_question_about_content(self, query: str, content: str) -> str:
        """
        Very simple content-based question answering.

        Args:
            query: User question
            content: File content

        Returns:
            A basic answer string
        """
        query_lower = query.lower()

        if query_lower in content.lower():
            return "The content contains the query string."
        return "The content does not contain the requested information."


if __name__ == "__main__":
    # Test the tool
    print("Testing OnedriveFileRead...")

    import os
    import json

    os.environ["USE_MOCK_APIS"] = "true"

    test_input = json.dumps(
        {"query": "test", "file_reference": {"base64_content": "SGVsbG8gV29ybGQ="}}
    )

    tool = OnedriveFileRead(input=test_input)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Result: {result.get('result')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("mock") == True
    print("All tests passed!")
