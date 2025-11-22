# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Repository Overview

AgentSwarm Tools Framework - **101 production-ready tools** organized into **18 categories** for the SuperAgentSwarm platform, built on the Agency Swarm framework. Tools provide search, media generation, file management, communication, data visualization, and code execution capabilities.

## Development Rules

This project follows **Agency Swarm** tool development standards.

### Core Principles

1. **Tools Must Be Standalone** - Each tool works independently with configurable parameters
2. **Production-Ready Code** - Well-commented, functional code with comprehensive error handling
3. **No Hardcoded Secrets** - Always use environment variables via `os.getenv()`
4. **Test Blocks Required** - Every tool file must include `if __name__ == "__main__":` test block
5. **Pydantic Fields** - Use `Field()` with clear descriptions for all parameters
6. **Atomic & Specific** - Tools perform single, concrete actions

## File Structure

```
agentswarm-tools/
├── tools/                    # All tool implementations
│   ├── search/              # Search & information tools
│   ├── web_content/         # Web scraping tools
│   ├── media_generation/    # Image/video/audio generation
│   ├── media_analysis/      # Media processing tools
│   ├── storage/             # File & storage tools
│   ├── communication/       # Email, calendar, phone tools
│   ├── visualization/       # Chart generation tools
│   └── ...
├── shared/                   # Shared utilities
│   ├── base.py             # BaseTool class
│   ├── errors.py           # Custom exceptions
│   ├── analytics.py        # Request tracking
│   ├── security.py         # API key management
│   └── validators.py       # Input validation
├── tests/                    # Test suite
├── cli/                      # Command-line interface
└── docs/                     # Documentation
```

## Tool Development Pattern

```python
from typing import Any, Dict, List
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class MyTool(BaseTool):
    """
    Clear description for AI agents.

    Args:
        param1: Description of parameter
        param2: Description with default

    Returns:
        Dict containing success, result, and metadata

    Example:
        >>> tool = MyTool(param1="value", param2=10)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "my_tool"
    tool_category: str = "category"

    # Parameters with Pydantic Field
    param1: str = Field(..., description="Required parameter", min_length=1)
    param2: int = Field(10, description="Optional with default", ge=1, le=100)

    def _execute(self) -> Dict[str, Any]:
        """Execute the tool logic."""
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
        if not self.param1.strip():
            raise ValidationError("param1 cannot be empty", tool_name=self.tool_name)

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {"mock": True, "data": "sample"},
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        api_key = os.getenv("MY_API_KEY")
        if not api_key:
            raise APIError("Missing MY_API_KEY", tool_name=self.tool_name)

        # Implementation here
        return {"data": "result"}


if __name__ == "__main__":
    # Test the tool
    print("Testing MyTool...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = MyTool(param1="test", param2=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Result: {result.get('result')}")
```

## Security Rules

**CRITICAL - Follow these rules strictly:**

1. **NEVER commit `.env` files** - Add to `.gitignore`
2. **NEVER hardcode API keys** - No secrets in source code
3. **Always use `os.getenv()`** for secrets:
   ```python
   # CORRECT
   api_key = os.getenv("GOOGLE_SEARCH_API_KEY")

   # WRONG - Never do this
   api_key = "HARDCODED_KEY_HERE"  # Will be rejected
   ```
4. **Validate API keys exist** before use:
   ```python
   if not api_key:
       raise APIError("Missing API_KEY environment variable", tool_name=self.tool_name)
   ```

## Testing Requirements

### Every Tool Needs:

1. **Test file** in same directory: `test_{tool_name}.py`
2. **`if __name__ == "__main__":` block** at end of tool file
3. **Mock mode support** via `USE_MOCK_APIS=true`

### Test Block Template:

```python
if __name__ == "__main__":
    print("Testing ToolName...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = ToolName(param1="value", param2="value")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get('success') == True
    # Additional assertions
```

### Running Tests:

```bash
# Run all tests
pytest

# Run specific tool test
pytest tests/unit/search/test_web_search.py

# Run with coverage
pytest --cov=agentswarm_tools --cov-report=html
```

## Code Standards

### Required Methods in Every Tool:

| Method | Purpose |
|--------|---------|
| `_execute()` | Main entry point, orchestrates validation/mock/process |
| `_validate_parameters()` | Input validation, raise `ValidationError` on failure |
| `_should_use_mock()` | Check `USE_MOCK_APIS` environment variable |
| `_generate_mock_results()` | Return realistic mock data for testing |
| `_process()` | Actual API calls and business logic |

### Error Types (from `shared/errors.py`):

| Error Class | Use Case |
|-------------|----------|
| `ValidationError` | Invalid input parameters |
| `APIError` | External API failures |
| `RateLimitError` | Rate limit exceeded |
| `AuthenticationError` | Auth/authorization failures |
| `TimeoutError` | Operation timed out |
| `ResourceNotFoundError` | Resource not found |
| `ConfigurationError` | Missing/invalid config |
| `SecurityError` | Security violations |

### Pydantic Field Usage:

```python
# Required field
query: str = Field(..., description="Search query", min_length=1)

# Optional with default
max_results: int = Field(10, description="Max results", ge=1, le=100)

# Optional nullable
filter: Optional[str] = Field(None, description="Optional filter")
```

## Important Instructions

- **FOLLOW** Agency Swarm tool development standards
- **Tools must be standalone** with test blocks
- **Never hardcode secrets** - use environment variables
- **Use Pydantic Field()** with descriptions for all parameters
- **Tools perform concrete, atomic actions** - avoid abstract tools
- **Always implement all 5 required methods** in tool classes
- **Test with mock mode** before testing with real APIs

## Quick Reference

### Environment Variables:

```bash
# Testing
USE_MOCK_APIS=true

# Search APIs
GOOGLE_SEARCH_API_KEY=...
GOOGLE_SEARCH_ENGINE_ID=...
SERPAPI_KEY=...

# Media Generation
OPENAI_API_KEY=...
STABILITY_API_KEY=...
ELEVENLABS_API_KEY=...

# Communication
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
```

### CLI Commands:

```bash
agentswarm-tools list              # List all tools
agentswarm-tools test web_search   # Test specific tool
agentswarm-tools test --all        # Run all tests
agentswarm-tools validate-keys     # Validate API keys
```
