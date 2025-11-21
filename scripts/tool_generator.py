#!/usr/bin/env python3
"""
Tool Generator - Tool Scaffolding Utility

Generates tool file structure from templates.
Creates tool implementation, tests, and documentation stubs.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ToolGenerator:
    """Generates tool scaffolding."""

    def __init__(self, base_path: str = "/app"):
        self.base_path = Path(base_path)
        self.tools_dir = self.base_path / "tools"
        self.tests_dir = self.base_path / "tests"
        self.docs_dir = self.base_path / "docs"

    def generate_tool_file(self, tool_name: str, category: str, description: str = "") -> Path:
        """Generate tool implementation file."""
        # Convert tool_name to Python class name
        class_name = ''.join(word.capitalize() for word in tool_name.split('_'))

        # Create category directory if needed
        category_dir = self.tools_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Tool file path
        tool_file = category_dir / f"{tool_name}.py"

        # Generate tool code
        code = f'''"""
{class_name} - {description or 'Tool description'}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Category: {category}
"""

from typing import Any, Optional
from pydantic import Field
from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class {class_name}(BaseTool):
    """
    {description or 'Tool description'}

    This tool is part of the {category} category.
    """

    # Tool metadata
    tool_name: str = "{tool_name}"
    tool_category: str = "{category}"

    # Input parameters (customize based on tool requirements)
    query: str = Field(
        ...,
        description="Primary input parameter",
        min_length=1
    )

    # Optional parameters
    options: Optional[dict] = Field(
        default=None,
        description="Additional options"
    )

    def _execute(self) -> Any:
        """
        Execute the tool logic.

        Returns:
            Result of the tool execution

        Raises:
            ValidationError: If input validation fails
            APIError: If external API call fails
        """
        try:
            # Validate inputs
            if not self.query:
                raise ValidationError("Query parameter is required")

            # TODO: Implement tool logic here
            # This is a stub implementation
            result = {{
                "status": "success",
                "query": self.query,
                "data": "TODO: Implement actual logic"
            }}

            return result

        except ValidationError:
            raise
        except Exception as e:
            raise APIError(f"Tool execution failed: {{str(e)}}")

    @classmethod
    def get_schema(cls) -> dict:
        """Get the tool schema for Agency Swarm."""
        return super().get_schema()
'''

        # Write tool file
        with open(tool_file, 'w') as f:
            f.write(code)

        logger.info(f"✅ Created tool file: {tool_file}")
        return tool_file

    def generate_test_file(self, tool_name: str, category: str) -> Path:
        """Generate test file."""
        # Convert tool_name to Python class name
        class_name = ''.join(word.capitalize() for word in tool_name.split('_'))

        # Create test directory structure
        test_category_dir = self.tests_dir / "tools" / category
        test_category_dir.mkdir(parents=True, exist_ok=True)

        # Test file path
        test_file = test_category_dir / f"test_{tool_name}.py"

        # Generate test code
        code = f'''"""
Tests for {class_name}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pytest
from tools.{category}.{tool_name} import {class_name}


class Test{class_name}:
    """Test suite for {class_name}."""

    def test_initialization(self):
        """Test tool initialization."""
        tool = {class_name}(query="test query")
        assert tool.tool_name == "{tool_name}"
        assert tool.tool_category == "{category}"

    def test_execute_success(self):
        """Test successful execution."""
        tool = {class_name}(query="test query")
        result = tool.run()
        assert result is not None
        # TODO: Add specific assertions based on expected output

    def test_execute_with_options(self):
        """Test execution with options."""
        tool = {class_name}(
            query="test query",
            options={{"key": "value"}}
        )
        result = tool.run()
        assert result is not None

    def test_validation_error(self):
        """Test validation error handling."""
        with pytest.raises(Exception):
            tool = {class_name}(query="")
            tool.run()

    def test_schema_generation(self):
        """Test schema generation for Agency Swarm."""
        schema = {class_name}.get_schema()
        assert schema is not None
        assert "properties" in schema
        assert "query" in schema["properties"]

    @pytest.mark.asyncio
    async def test_async_execution(self):
        """Test async execution if applicable."""
        # TODO: Add async tests if tool supports async
        pass

    def test_rate_limiting(self):
        """Test rate limiting."""
        # TODO: Add rate limiting tests
        pass

    def test_error_handling(self):
        """Test error handling."""
        # TODO: Add error handling tests
        pass
'''

        # Write test file
        with open(test_file, 'w') as f:
            f.write(code)

        logger.info(f"✅ Created test file: {test_file}")
        return test_file

    def generate_documentation(self, tool_name: str, category: str, description: str = "") -> Path:
        """Generate documentation file."""
        # Create docs directory structure
        docs_category_dir = self.docs_dir / "api" / category
        docs_category_dir.mkdir(parents=True, exist_ok=True)

        # Doc file path
        doc_file = docs_category_dir / f"{tool_name}.md"

        # Generate documentation
        class_name = ''.join(word.capitalize() for word in tool_name.split('_'))

        markdown = f'''# {class_name}

**Category:** {category}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Description

{description or 'Tool description goes here.'}

## Usage

```python
from tools.{category}.{tool_name} import {class_name}

# Basic usage
tool = {class_name}(query="your query here")
result = tool.run()
print(result)
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Primary input parameter |
| options | dict | No | Additional options |

## Response Format

```json
{{
  "status": "success",
  "query": "your query",
  "data": "result data"
}}
```

## Error Handling

The tool may raise the following exceptions:

- `ValidationError`: Invalid input parameters
- `APIError`: External API call failed
- `RateLimitError`: Rate limit exceeded

## Examples

### Basic Example

```python
tool = {class_name}(query="example query")
result = tool.run()
```

### With Options

```python
tool = {class_name}(
    query="example query",
    options={{"key": "value"}}
)
result = tool.run()
```

## Integration with Agency Swarm

```python
from agency_swarm import Agent
from tools.{category}.{tool_name} import {class_name}

agent = Agent(
    name="My Agent",
    tools=[{class_name}]
)
```

## Rate Limits

- Default rate limit: As configured in environment
- Rate limit type: `{category}`

## Dependencies

- agency-swarm
- pydantic
- Additional dependencies as needed

## Notes

- TODO: Add specific notes about this tool
- TODO: Add usage tips and best practices

---

Generated by AgentSwarm Tools Framework
'''

        # Write documentation file
        with open(doc_file, 'w') as f:
            f.write(markdown)

        logger.info(f"✅ Created documentation: {doc_file}")
        return doc_file

    def generate_complete_tool(
        self,
        tool_name: str,
        category: str,
        description: str = ""
    ) -> Dict[str, Path]:
        """Generate complete tool scaffolding."""
        logger.info(f"🔨 Generating complete tool: {tool_name} ({category})")

        files = {
            "tool": self.generate_tool_file(tool_name, category, description),
            "test": self.generate_test_file(tool_name, category),
            "docs": self.generate_documentation(tool_name, category, description)
        }

        logger.info(f"✅ Complete tool scaffolding generated for: {tool_name}")
        return files


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate tool scaffolding')
    parser.add_argument('tool_name', help='Tool name (e.g., web_search)')
    parser.add_argument('--category', required=True, help='Tool category')
    parser.add_argument('--description', default='', help='Tool description')
    parser.add_argument('--base-path', default='/app', help='Base path for project')

    args = parser.parse_args()

    generator = ToolGenerator(base_path=args.base_path)

    try:
        files = generator.generate_complete_tool(
            tool_name=args.tool_name,
            category=args.category,
            description=args.description
        )

        print("\n✅ Tool scaffolding generated successfully!")
        print(f"\nFiles created:")
        for file_type, file_path in files.items():
            print(f"  - {file_type}: {file_path}")

    except Exception as e:
        logger.error(f"❌ Failed to generate tool: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
