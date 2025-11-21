#!/usr/bin/env python3
"""
AI Code Generator for AgentSwarm Tools

Uses Claude Sonnet to generate complete tool implementations
following the BaseTool pattern.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from openai import OpenAI


class ToolCodeGenerator:
    """Generate tool code using OpenAI GPT-4."""

    def __init__(self):
        """Initialize code generator with OpenAI API."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-5.1-chat-latest"  # GPT-5.1 Instant (Nov 2025)

        # Load reference implementation
        self.demo_tool_code = self._load_demo_tool()
        self.demo_tool_test = self._load_demo_tool_test()

        # Load development guidelines
        self.guidelines = self._load_guidelines()

    def _load_demo_tool(self) -> str:
        """Load demo tool reference implementation."""
        demo_path = Path("tools/_examples/demo_tool/demo_tool.py")
        if demo_path.exists():
            return demo_path.read_text()
        return ""

    def _load_demo_tool_test(self) -> str:
        """Load demo tool test reference."""
        test_path = Path("tools/_examples/demo_tool/test_demo_tool.py")
        if test_path.exists():
            return test_path.read_text()
        return ""

    def _load_guidelines(self) -> str:
        """Load development guidelines for context."""
        guidelines_dir = Path("/Users/frank/Documents/Code/Genspark/dev-guidelines")
        quick_start = guidelines_dir / "QUICK-START.md"

        if quick_start.exists():
            return quick_start.read_text()
        return ""

    def generate_tool_code(self, tool_spec: Dict[str, Any]) -> str:
        """
        Generate complete tool implementation code.

        Args:
            tool_spec: Tool specification with name, category, params, etc.

        Returns:
            Complete Python code for the tool
        """
        tool_name = tool_spec["tool_name"]
        category = tool_spec["category"]
        description = tool_spec["description"]
        parameters = tool_spec.get("parameters", {})

        # Create prompt for Claude
        prompt = self._create_code_prompt(tool_name, category, description, parameters)

        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=4000,  # GPT-5.1 uses max_completion_tokens
                # Note: GPT-5.1 only supports temperature=1 (default)
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract code from response
            response_text = response.choices[0].message.content

            # Extract Python code from markdown if present
            if "```python" in response_text:
                code_start = response_text.find("```python") + 9
                code_end = response_text.find("```", code_start)
                code = response_text[code_start:code_end].strip()
            else:
                code = response_text.strip()

            return code

        except Exception as e:
            raise RuntimeError(f"Failed to generate code for {tool_name}: {e}")

    def _create_code_prompt(
        self,
        tool_name: str,
        category: str,
        description: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Create prompt for Claude to generate tool code."""

        class_name = "".join(word.capitalize() for word in tool_name.split("_"))

        param_fields = []
        for param_name, param_def in parameters.items():
            param_type = self._map_type(param_def.get("type", "string"))
            param_desc = param_def.get("description", f"{param_name} parameter")
            required = param_def.get("required", True)

            if required:
                field_def = f'    {param_name}: {param_type} = Field(..., description="{param_desc}")'
            else:
                default = param_def.get("default", "None" if param_type == "Optional[str]" else "10")
                field_def = f'    {param_name}: {param_type} = Field({default}, description="{param_desc}")'

            param_fields.append(field_def)

        params_str = "\n".join(param_fields) if param_fields else '    pass  # No parameters'

        prompt = f"""You are an expert Python developer creating a tool for the AgentSwarm framework.

TASK: Create a complete implementation for the "{tool_name}" tool.

TOOL SPECIFICATION:
- Name: {tool_name}
- Category: {category}
- Description: {description}
- Parameters: {json.dumps(parameters, indent=2)}

REQUIREMENTS:
1. Extend shared.base.BaseTool (NEVER override run() method)
2. Implement ONLY the _execute() method
3. Use type hints on ALL parameters and return values
4. Add Google-style docstrings
5. Use shared.errors (ValidationError, APIError) for error handling
6. Return structured Dict with success, result, metadata
7. Support mock mode (check USE_MOCK_APIS environment variable)
8. Follow the exact pattern from the demo tool below

REFERENCE DEMO TOOL IMPLEMENTATION:
```python
{self.demo_tool_code}
```

DEVELOPMENT GUIDELINES:
{self.guidelines[:2000]}  # Truncated for token limit

TEMPLATE TO FILL:
```python
\"\"\"
{description}
\"\"\"

from typing import Any, Dict, List, Optional
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class {class_name}(BaseTool):
    \"\"\"
    {description}

    Args:
{chr(10).join(f"        {p}: {parameters[p].get('description', '')}" for p in parameters.keys())}

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = {class_name}({', '.join(f'{p}="example"' for p in list(parameters.keys())[:2])})
        >>> result = tool.run()
    \"\"\"

    # Tool metadata
    tool_name: str = "{tool_name}"
    tool_category: str = "{category}"

    # Parameters
{params_str}

    def _execute(self) -> Dict[str, Any]:
        \"\"\"
        Execute the {tool_name} tool.

        Returns:
            Dict with results
        \"\"\"
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {{
                "success": True,
                "result": result,
                "metadata": {{
                    "tool_name": self.tool_name
                }}
            }}
        except Exception as e:
            raise APIError(f"Failed: {{e}}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        \"\"\"Validate input parameters.\"\"\"
        # Add validation logic
        pass

    def _should_use_mock(self) -> bool:
        \"\"\"Check if mock mode enabled.\"\"\"
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        \"\"\"Generate mock results for testing.\"\"\"
        return {{
            "success": True,
            "result": {{"mock": True}},
            "metadata": {{"mock_mode": True}}
        }}

    def _process(self) -> Any:
        \"\"\"Main processing logic.\"\"\"
        # TODO: Implement actual logic
        pass
```

IMPORTANT:
- Follow the template EXACTLY
- Implement _validate_parameters() with actual validation
- Implement _process() with the real tool logic
- Support mock mode for testing without API keys
- Use proper error handling
- Return structured Dict[str, Any]

OUTPUT: Only return the complete Python code, no explanations."""

        return prompt

    def _map_type(self, json_type: str) -> str:
        """Map JSON schema type to Python type hint."""
        type_map = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "object": "Dict[str, Any]",
            "array": "List[Any]"
        }
        return type_map.get(json_type, "str")


def main():
    """Test code generator with web_search tool."""
    import json

    # Load spec
    spec_path = Path("data/tool_specs/web_search.json")
    with open(spec_path) as f:
        spec = json.load(f)

    # Generate code
    generator = ToolCodeGenerator()
    code = generator.generate_tool_code(spec)

    print("Generated code:")
    print("=" * 80)
    print(code)
    print("=" * 80)


if __name__ == "__main__":
    main()
