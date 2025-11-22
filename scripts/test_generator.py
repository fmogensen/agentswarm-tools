#!/usr/bin/env python3
"""
AI Test Generator for AgentSwarm Tools

Uses Claude Sonnet to generate comprehensive pytest tests
with 80%+ coverage.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI


class ToolTestGenerator:
    """Generate pytest tests using OpenAI GPT-4."""

    def __init__(self):
        """Initialize test generator with OpenAI API."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-5.1-chat-latest"  # GPT-5.1 Instant (Nov 2025)

        # Load reference test
        self.demo_test = self._load_demo_test()

    def _load_demo_test(self) -> str:
        """Load demo tool test reference."""
        test_path = Path("tools/_examples/demo_tool/test_demo_tool.py")
        if test_path.exists():
            return test_path.read_text()
        return ""

    def generate_test_code(self, tool_spec: Dict[str, Any], tool_code: str) -> str:
        """
        Generate comprehensive pytest tests.

        Args:
            tool_spec: Tool specification
            tool_code: Generated tool implementation code

        Returns:
            Complete pytest test code
        """
        tool_name = tool_spec["tool_name"]
        category = tool_spec["category"]
        description = tool_spec["description"]

        # Create prompt
        prompt = self._create_test_prompt(tool_name, category, description, tool_code)

        # Call OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=4000,  # GPT-5.1 uses max_completion_tokens
                # Note: GPT-5.1 only supports temperature=1 (default)
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.choices[0].message.content

            # Extract code
            if "```python" in response_text:
                code_start = response_text.find("```python") + 9
                code_end = response_text.find("```", code_start)
                code = response_text[code_start:code_end].strip()
            else:
                code = response_text.strip()

            return code

        except Exception as e:
            raise RuntimeError(f"Failed to generate tests for {tool_name}: {e}")

    def _create_test_prompt(
        self, tool_name: str, category: str, description: str, tool_code: str
    ) -> str:
        """Create prompt for test generation."""

        class_name = "".join(word.capitalize() for word in tool_name.split("_"))

        prompt = f"""You are an expert Python test developer creating comprehensive pytest tests.

TASK: Create complete pytest tests for the "{tool_name}" tool with ≥80% coverage.

TOOL IMPLEMENTATION TO TEST:
```python
{tool_code}
```

REQUIREMENTS:
1. Test ALL methods and code paths
2. Achieve ≥80% code coverage
3. Use pytest fixtures from conftest.py
4. Test happy path, error cases, edge cases
5. Use parametrized tests where appropriate
6. Mock external dependencies
7. Follow the demo test pattern EXACTLY

REFERENCE DEMO TEST:
```python
{self.demo_test}
```

TEST STRUCTURE REQUIRED:
1. Fixtures section - tool instances, mock data
2. Happy path tests - successful execution
3. Error case tests - validation errors, API errors
4. Edge case tests - boundary values, unicode, special chars
5. Parametrized tests - multiple input combinations
6. Integration tests - with shared modules

TEMPLATE:
```python
\"\"\"Tests for {tool_name} tool.\"\"\"

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from tools.{category}.{tool_name} import {class_name}
from shared.errors import ValidationError, APIError


class Test{class_name}:
    \"\"\"Test suite for {class_name}.\"\"\"

    # ========== FIXTURES ==========

    @pytest.fixture
    def tool(self) -> {class_name}:
        \"\"\"Create tool instance.\"\"\"
        return {class_name}(...)  # Fill with valid params

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool: {class_name}):
        \"\"\"Test successful execution.\"\"\"
        result = tool.run()
        assert result["success"] is True
        assert "result" in result

    def test_metadata_correct(self, tool: {class_name}):
        \"\"\"Test tool metadata.\"\"\"
        assert tool.tool_name == "{tool_name}"
        assert tool.tool_category == "{category}"

    # ========== ERROR CASES ==========

    def test_validation_error(self):
        \"\"\"Test validation errors.\"\"\"
        with pytest.raises(ValidationError):
            tool = {class_name}(...)  # Invalid params
            tool.run()

    def test_api_error_handled(self, tool: {class_name}):
        \"\"\"Test API error handling.\"\"\"
        with patch.object(tool, '_process', side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {{"USE_MOCK_APIS": "true"}})
    def test_mock_mode(self, tool: {class_name}):
        \"\"\"Test mock mode returns mock data.\"\"\"
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    # ========== EDGE CASES ==========

    # Add edge case tests here

    # ========== PARAMETRIZED ==========

    # Add parametrized tests here
```

OUTPUT: Complete pytest test code with ≥80% coverage. Only code, no explanations."""

        return prompt


def main():
    """Test the test generator."""
    # Load spec and code
    spec_path = Path("data/tool_specs/web_search.json")
    with open(spec_path) as f:
        spec = json.load(f)

    # For testing, use a simple mock code
    tool_code = """
class WebSearch(BaseTool):
    tool_name = "web_search"
    tool_category = "search"
    query: str = Field(..., description="Search query")

    def _execute(self):
        return {"success": True, "result": []}
"""

    generator = ToolTestGenerator()
    test_code = generator.generate_test_code(spec, tool_code)

    print("Generated test:")
    print("=" * 80)
    print(test_code)


if __name__ == "__main__":
    main()
