# Contributing to AgentSwarm Tools

**Version:** 2.0.0
**Last Updated:** 2025-11-22

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
- [v2.0.0 Updates](#v20-updates)

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

- Python 3.10 or higher (3.12 recommended for full compatibility)
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

4. **Set up pre-commit hooks** (Recommended):
   ```bash
   # Install pre-commit framework
   pip install pre-commit

   # Install Git hooks
   pre-commit install

   # (Optional) Run on all files to verify setup
   pre-commit run --all-files
   ```

   Pre-commit hooks automatically check code quality before each commit. See [Pre-Commit Setup Guide](docs/guides/PRE_COMMIT_SETUP.md) for details.

5. **Run tests to verify setup**:
   ```bash
   pytest tests/integration/live/ -v
   ```

   **Note:** Some tests may be skipped due to missing API keys. This is expected behavior.

## Tool Development

All tools must follow the Agency Swarm framework standards. In v2.0.0, tools are organized into 8 streamlined categories:

1. **data/** - Search, business analytics, AI intelligence
2. **communication/** - Email, calendar, workspace, messaging, phone
3. **media/** - Generation, analysis, processing
4. **visualization/** - Charts, diagrams, graphs
5. **content/** - Documents, web content
6. **infrastructure/** - Code execution, storage, management
7. **utils/** - Helper tools and validators
8. **integrations/** - External service connectors (extensible)

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
    tool_category: str = "category"  # One of: data, communication, media, visualization, content, infrastructure, utils, integrations

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

### Caching Guidelines

**When to Enable Caching:**

Tools should enable caching when:
- They make expensive API calls (cost time/money)
- Results are relatively stable over time
- Same queries are likely to be repeated

**How to Enable Caching:**

```python
class MySearchTool(BaseTool):
    """Search tool with caching."""

    tool_name: str = "my_search"
    tool_category: str = "data"

    # Enable caching
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour in seconds
    cache_key_params: list = ["query", "max_results"]

    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Max results")

    def _execute(self) -> Dict[str, Any]:
        # Implementation
        pass
```

**TTL Recommendations:**

| Tool Type | Recommended TTL | Reason |
|-----------|----------------|--------|
| Web/Scholar Search | 3600s (1 hour) | Content changes moderately |
| Image Search | 3600s (1 hour) | Results relatively stable |
| Product Search | 1800s (30 min) | Prices change frequently |
| Real-time Data | 300s (5 min) | Data changes rapidly |
| Analytics Reports | 21600s (6 hours) | Expensive, stable data |

**Cache Configuration:**

```bash
# Development (default)
CACHE_BACKEND=memory

# Production (recommended)
CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379

# Disable caching
CACHE_BACKEND=none
```

**See the complete guide:** [docs/guides/CACHING.md](docs/guides/CACHING.md)

## Testing

### Test Requirements

- **Minimum coverage**: 85-95% for shared modules
- **Core logic coverage**: 90%+
- **Error handling coverage**: 100%
- **Mock mode support**: All tools must support `USE_MOCK_APIS=true`

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

# Run integration tests (recommended for verification)
pytest tests/integration/live/ -v

# Run specific tool tests
pytest tools/category/your_tool/test_your_tool.py

# Run with coverage
pytest --cov=tools --cov=shared --cov-report=html

# Run in parallel
pytest -n auto

# Run specific category
pytest tests/unit/ -k "test_your_category"
```

### Test Status in v2.0.0

- **Total Tests:** 262 test cases (plus 400+ in shared modules)
- **Pass Rate:** 90.1% (236 passing, 22 failing)
- **Integration Tests:** 11/11 passing (100%)
- **Shared Module Coverage:** 85-95%
- **Note:** See [TEST_REPORT.md](TEST_REPORT.md) for current test status.

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

3. **Run quality checks**:
   ```bash
   # If using pre-commit hooks (recommended)
   pre-commit run --all-files

   # Or manually
   black tools/ shared/ tests/
   isort tools/ shared/ tests/
   flake8 tools/
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
- Maximum line length: 100 characters (Black default)
- Use descriptive variable names
- **All code must be formatted with Black**

### Formatting (Required in v2.0.0)

```bash
# Format code with black (REQUIRED before committing)
black tools/ shared/ tests/

# Sort imports
isort tools/ shared/ tests/

# Check with flake8 (optional)
flake8 tools/
```

**Important:** All Python code in v2.0.0 has been formatted with Black. Your contributions must also be Black-formatted to maintain consistency.

### Pre-Commit Hooks (Recommended)

Pre-commit hooks automatically enforce code quality standards before each commit:

```bash
# One-time setup
pip install pre-commit
pre-commit install

# Hooks run automatically on git commit
git commit -m "Your changes"
```

**What pre-commit hooks check:**
- **Black** - Code formatting (Python 3.12)
- **isort** - Import sorting
- **flake8** - Linting (max line length 100)
- **mypy** - Type checking (with Pydantic support)
- **bandit** - Security scanning (tools/, shared/)
- **pytest-quick** - Fast unit tests

If hooks modify files (e.g., Black formatting), simply re-stage and commit:

```bash
# Hooks modified files
git add .
git commit -m "Your changes"  # Will pass this time
```

See [Pre-Commit Setup Guide](docs/guides/PRE_COMMIT_SETUP.md) for complete documentation, troubleshooting, and customization options.

### Naming Conventions

- **Classes**: PascalCase (e.g., `WebSearchTool`)
- **Functions/Methods**: snake_case (e.g., `_validate_parameters`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RESULTS`)
- **Files**: snake_case (e.g., `web_search.py`)

## v2.0.0 Updates

### What Changed in v2.0.0

1. **Code Quality and Cleanup:**
   - All 239 Python files formatted with Black
   - Removed 278 __pycache__ directories and 2,699 .pyc files
   - Cleaned up orphaned test files
   - Standardized to pytest exclusively

2. **Category Reorganization (v1.2.0 → v2.0.0):**
   - Reduced from 19 categories to 8 streamlined categories
   - New structure: data, communication, media, visualization, content, infrastructure, utils, integrations
   - All tool_category attributes updated

3. **Test Suite Status:**
   - 262 tool tests + 400+ shared module tests
   - 90.1% pass rate (236/262 tests passing)
   - Integration tests prove tools work correctly (100% pass rate)
   - See [TEST_REPORT.md](TEST_REPORT.md) for current status
   - See [docs/archive/TEST_HISTORY.md](docs/archive/TEST_HISTORY.md) for improvement history

4. **Documentation Updates:**
   - All documentation reflects v2.0.0 structure
   - Migration guide available (MIGRATION_GUIDE_v1.2.0.md)
   - Test reports and coverage documentation added

### Contributing to v2.0.0

When contributing, please:

1. **Use correct category paths:**
   ```python
   # Correct v2.0.0 imports
   from tools.data.search.web_search import WebSearch
   from tools.media.generation.image_generation import ImageGenerationTool
   from tools.infrastructure.execution.bash import Bash
   ```

2. **Format with Black:**
   ```bash
   black your_file.py
   ```

3. **Update tool_category metadata:**
   ```python
   tool_category: str = "data"  # Not "search"
   ```

4. **Test with mock mode:**
   ```bash
   export USE_MOCK_APIS=true
   pytest tests/integration/live/ -v
   ```

### Migration from v1.x

If updating existing tools or tests:

1. Update import paths to new category structure
2. Update tool_category to one of 8 categories
3. Format code with Black
4. Update tests to use new structure
5. Run integration tests to verify

See [MIGRATION_GUIDE_v1.2.0.md](MIGRATION_GUIDE_v1.2.0.md) for complete migration instructions.

---

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Review [TEST_REPORT.md](TEST_REPORT.md) for current test status
- Check [CHANGELOG.md](CHANGELOG.md) for version history

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to AgentSwarm Tools v2.0.0!**
