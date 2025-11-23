"""
Create specialized agents (podcasts, docs, slides, sheets, deep research, websites, video editing)
"""

import os
from typing import Any, Dict

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class CreateAgent(BaseTool):
    """
    Create specialized agents (podcasts, docs, slides, sheets, deep research, websites, video editing)

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = CreateAgent(input="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "create_agent"
    tool_category: str = "content"

    # Parameters
    input: str = Field(..., description="Primary input parameter", min_length=1, max_length=10000)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the create_agent tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: If parameters are invalid
            APIError: If execution fails
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
                "metadata": {
                    "tool_name": self.tool_name,
                    "input_length": len(self.input),
                    "mock_mode": False,
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input is empty or invalid
        """
        if not isinstance(self.input, str):
            raise ValidationError(
                "Input must be a string",
                tool_name=self.tool_name,
                details={"input_type": str(type(self.input))},
            )

        if not self.input.strip():
            raise ValidationError(
                "Input cannot be empty",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_agent = {
            "agent_id": "mock-123",
            "type": "mock_agent",
            "description": f"Mock agent created for input: {self.input}",
        }

        return {
            "success": True,
            "result": mock_agent,
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Returns:
            Agent creation result metadata

        Raises:
            APIError: For unexpected errors during processing
        """
        # Simulate mapping input text to an agent type
        normalized = self.input.lower()

        if "podcast" in normalized:
            agent_type = "podcast_creator"
        elif "doc" in normalized or "document" in normalized:
            agent_type = "document_generator"
        elif "slide" in normalized or "slides" in normalized:
            agent_type = "slide_maker"
        elif "sheet" in normalized or "spreadsheet" in normalized:
            agent_type = "sheet_builder"
        elif "research" in normalized or "deep research" in normalized:
            agent_type = "deep_research_agent"
        elif "website" in normalized or "web" in normalized:
            agent_type = "website_builder"
        elif "video" in normalized or "edit" in normalized:
            agent_type = "video_editing_agent"
        else:
            agent_type = "general_creation_agent"

        # Simulated successful creation payload
        return {
            "agent_id": f"agent_{hash(self.input) % 10_000_000}",
            "agent_type": agent_type,
            "input_summary": self.input[:200],
            "status": "created",
        }


if __name__ == "__main__":
    print("Testing CreateAgent...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Create podcast agent
    print("\nTest 1: Create podcast agent")
    tool = CreateAgent(input="Create a podcast about AI and technology")
    result = tool.run()

    assert result.get("success") == True
    assert "podcast" in result.get("result", {}).get("agent_type", "")
    print(f"✅ Test 1 passed: Created {result.get('result', {}).get('agent_type')}")
    print(f"   Agent ID: {result.get('result', {}).get('agent_id')}")

    # Test 2: Create document agent
    print("\nTest 2: Create document agent")
    tool = CreateAgent(input="Generate a comprehensive document about machine learning")
    result = tool.run()

    assert result.get("success") == True
    assert "document" in result.get("result", {}).get("agent_type", "")
    print(f"✅ Test 2 passed: Created {result.get('result', {}).get('agent_type')}")

    # Test 3: Validation test - empty input
    print("\nTest 3: Validation - empty input")
    try:
        bad_tool = CreateAgent(input="   ")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Create research agent
    print("\nTest 4: Create deep research agent")
    tool = CreateAgent(input="Conduct deep research on quantum computing")
    result = tool.run()

    assert result.get("success") == True
    assert "research" in result.get("result", {}).get("agent_type", "")
    print(f"✅ Test 4 passed: Created {result.get('result', {}).get('agent_type')}")

    print("\n✅ All tests passed!")
