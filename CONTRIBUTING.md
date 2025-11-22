# Contributing to AgentSwarm Tools

Thank you for your interest in contributing to AgentSwarm Tools! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Tool Development](#tool-development)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/agentswarm-tools.git
   cd agentswarm-tools
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/genspark/agentswarm-tools.git
   ```

## Development Setup

### Prerequisites

- Python 3.12 or higher
- pip and virtualenv
- Git

### Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run tests to verify setup**:
   ```bash
   pytest
   ```

## Tool Development

All tools must follow the Agency Swarm framework standards:

### Tool Structure

```python
from typing import Any, Dict
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class YourTool(BaseTool):
    """
    Clear description of what this tool does.

    This description is used by AI agents to understand when to use the tool.
    Be specific and include use cases.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2

    Returns:
        Dict containing success status, result data, and metadata

    Example:
        >>> tool = YourTool(param1="value", param2=10)
        >>> result = tool.run()
        >>> print(result['success'])
        True
    """

    # Tool metadata
    tool_name: str = "your_tool"
    tool_category: str = "category"

    # Parameters
    param1: str = Field(..., description="Clear description for AI agents")
    param2: int = Field(10, description="Optional parameter with default", ge=1)

    def _execute(self) -> Dict[str, Any]:
        """Execute the tool logic."""
        # 1. Validate parameters
        self._validate_parameters()

        # 2. Check if mock mode enabled
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. Execute actual logic
        return self._process()

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.param1.strip():
            raise ValidationError(
                "param1 cannot be empty",
                tool_name=self.tool_name
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {"mock": True, "data": "sample"},
            "metadata": {"mock_mode": True}
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        # Get API key from environment
        api_key = os.getenv("YOUR_API_KEY")
        if not api_key:
            raise APIError(
                "Missing YOUR_API_KEY environment variable",
                tool_name=self.tool_name
            )

        # Your implementation here
        result = {"data": "result"}

        return {
            "success": True,
            "result": result,
            "metadata": {"tool_name": self.tool_name}
        }


if __name__ == "__main__":
    # Test the tool
    print("Testing YourTool...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    tool = YourTool(param1="test", param2=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get('success') == True
    print("Test passed!")
```

### Required Components

Every tool must include:

1. **Clear docstring** - Explains what the tool does and when to use it
2. **Pydantic Fields** - All parameters with descriptions
3. **Five core methods**:
   - `_execute()` - Main orchestration
   - `_validate_parameters()` - Input validation
   - `_should_use_mock()` - Check mock mode
   - `_generate_mock_results()` - Mock data for testing
   - `_process()` - Actual implementation
4. **Test block** - `if __name__ == "__main__":` section
5. **Error handling** - Use custom exceptions from `shared/errors.py`

### Security Requirements

**CRITICAL - Never violate these rules:**

1. **No hardcoded secrets** - Always use `os.getenv()`
2. **No `.env` files in commits** - Already in `.gitignore`
3. **Validate API keys** before use
4. **Use custom exceptions** for errors

```python
# CORRECT
api_key = os.getenv("MY_API_KEY")

# WRONG - Never do this
api_key = "hardcoded_key_here"  # Will be rejected
```

## Testing

### Test Requirements

- **Minimum coverage**: 90%
- **Core logic coverage**: 100%
- **Error handling coverage**: 100%

### Test Structure

Create test file in the same directory as the tool:

```python
# tools/category/your_tool/test_your_tool.py

import pytest
import os
from .your_tool import YourTool


def test_your_tool_basic():
    """Test basic functionality"""
    os.environ["USE_MOCK_APIS"] = "true"

    tool = YourTool(param1="test", param2=5)
    result = tool.run()

    assert result['success'] == True
    assert 'result' in result
    assert 'metadata' in result


def test_your_tool_validation():
    """Test parameter validation"""
    with pytest.raises(ValidationError):
        tool = YourTool(param1="", param2=5)
        tool.run()


def test_your_tool_mock_mode():
    """Test mock mode"""
    os.environ["USE_MOCK_APIS"] = "true"

    tool = YourTool(param1="test")
    result = tool.run()

    assert result['metadata']['mock_mode'] == True
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific tool tests
pytest tools/category/your_tool/test_your_tool.py

# Run with coverage
pytest --cov=agentswarm_tools --cov-report=html

# Run specific category
pytest tests/unit/search/
```

## Documentation

### Documentation Requirements

Every tool needs:

1. **Docstring in tool class** - Clear description, parameters, returns, examples
2. **Code comments** - Explain complex logic
3. **Example usage** - In docstring and test block

### Documentation Style

- Use clear, concise language
- Include use cases and examples
- Explain when AI agents should use the tool
- Document all parameters and return values

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following the tool development pattern
   - Add comprehensive tests
   - Update documentation

3. **Run tests locally**:
   ```bash
   pytest
   pytest --cov=agentswarm_tools
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**:
   - Go to GitHub and create a PR from your fork
   - Fill out the PR template
   - Link any related issues

### PR Requirements

Your PR must:

- Pass all CI tests
- Maintain or improve test coverage (minimum 90%)
- Include tests for new functionality
- Update documentation
- Follow code style guidelines
- Include clear commit messages

## Code Style

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use descriptive variable names

### Formatting

```bash
# Format code with black
black tools/

# Sort imports
isort tools/

# Check with flake8
flake8 tools/
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `WebSearchTool`)
- **Functions/Methods**: snake_case (e.g., `_validate_parameters`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RESULTS`)
- **Files**: snake_case (e.g., `web_search.py`)

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Email support@agentswarm.ai for other inquiries

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AgentSwarm Tools!
