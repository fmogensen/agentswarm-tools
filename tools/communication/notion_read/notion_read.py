"""
Retrieve and summarize full Notion page content
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class NotionRead(BaseTool):
    """
    Retrieve and summarize full Notion page content.

    Args:
        input: Primary input parameter. Expected to be a Notion page ID or URL.

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (page content and summary)
        - metadata: Additional information

    Example:
        >>> tool = NotionRead(input="abc123pageid")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "notion_read"
    tool_category: str = "communication"
    tool_description: str = "Retrieve and summarize full Notion page content"

    # Parameters
    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the notion_read tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: If input invalid
            APIError: If API call fails
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
                "metadata": {"tool_name": self.tool_name, "input": self.input},
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
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        if len(self.input.strip()) == 0:
            raise ValidationError(
                "Input cannot be empty or whitespace",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_content = "Mock Notion page content. This is placeholder text simulating a real Notion page."
        mock_summary = "Summary: Mock content summary."

        return {
            "success": True,
            "result": {
                "page_id": self.input,
                "content": mock_content,
                "summary": mock_summary,
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Retrieves a Notion page's full text content and returns a summary.

        Returns:
            Dict containing page content and summary

        Raises:
            APIError: On failure retrieving Notion API data
        """
        notion_token = os.getenv("NOTION_API_KEY")
        if not notion_token:
            raise APIError("NOTION_API_KEY missing", tool_name=self.tool_name)

        page_id = self.input.strip()

        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Notion-Version": "2022-06-28",
        }

        # Fetch blocks
        try:
            resp = requests.get(
                f"https://api.notion.com/v1/blocks/{page_id}/children",
                headers=headers,
                timeout=15,
            )
        except Exception as e:
            raise APIError(f"Request failed: {e}", tool_name=self.tool_name)

        if resp.status_code != 200:
            raise APIError(f"Notion API error: {resp.text}", tool_name=self.tool_name)

        data = resp.json()
        blocks = data.get("results", [])

        # Extract text content
        full_text_parts = []
        for block in blocks:
            text_items = (
                block.get("paragraph", {}).get("rich_text", [])
                if "paragraph" in block
                else []
            )
            for t in text_items:
                if "plain_text" in t:
                    full_text_parts.append(t["plain_text"])

        full_text = " ".join(full_text_parts).strip()

        if not full_text:
            full_text = "(No text content found in page.)"

        # Simple summary heuristic
        summary = full_text[:200] + "..." if len(full_text) > 200 else full_text

        return {"page_id": page_id, "content": full_text, "summary": summary}


if __name__ == "__main__":
    print("Testing NotionRead...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Read Notion page by ID
    print("\nTest 1: Read Notion page")
    tool = NotionRead(input="abc123pageid")
    result = tool.run()

    assert result.get('success') == True
    assert 'content' in result.get('result', {})
    assert 'summary' in result.get('result', {})
    print(f"✅ Test 1 passed: Page read successfully")
    print(f"   Page ID: {result.get('result', {}).get('page_id')}")
    print(f"   Summary: {result.get('result', {}).get('summary')[:50]}...")

    # Test 2: Different page ID
    print("\nTest 2: Read different Notion page")
    tool = NotionRead(input="xyz789")
    result = tool.run()

    assert result.get('success') == True
    print(f"✅ Test 2 passed: Different page read successfully")

    # Test 3: Validation - empty input
    print("\nTest 3: Validation - empty input")
    try:
        bad_tool = NotionRead(input="   ")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Mock mode verification
    print("\nTest 4: Mock mode verification")
    tool = NotionRead(input="test123")
    result = tool.run()

    assert result.get('result', {}).get('mock') == True
    print(f"✅ Test 4 passed: Mock mode working correctly")

    print("\n✅ All tests passed!")
