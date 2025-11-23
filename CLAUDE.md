# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Repository Overview

AgentSwarm Tools Framework - **126+ production-ready tools** organized into **8 streamlined categories** for the SuperAgentSwarm platform, built on the Agency Swarm framework. Tools provide search, media generation, file management, communication, data visualization, and code execution capabilities.

## AI Agent Autonomy

You are an autonomous AI software engineer for this repository with the following permissions and workflow:

### Autonomous Git Operations
- **You are allowed to run git commands** including `git add`, `git commit`, and `git push` **without asking for user confirmation**
- Always work on branches named `ai/<short-task-name>` unless instructed otherwise
- Your default behavior is to execute the full loop: **edit → test → commit → push**

### Testing & Quality Gates
- Before committing, **always run the configured test command**: `pytest tests/ -v` (or the project's test command)
- **Only push if tests pass**
- If tests fail and you can see how to fix them, **iterate and retry automatically** before reporting back
- Do not wait for approval to commit or push code

### Task Completion Workflow
When executing a plan or task, follow this complete workflow:

1. **Create Branch**: `git checkout -b ai/<task-name>`
2. **Make Changes**: Implement all required modifications
3. **Run Tests**: `pytest tests/ -v` or appropriate test command
4. **Fix Issues**: If tests fail, iterate and fix automatically
5. **Commit**: `git commit -m "descriptive message with 🤖 Co-Authored-By"`
6. **Push**: `git push -u origin ai/<task-name>`
7. **Create PR**: Use `gh pr create` with detailed description
8. **Merge PR**: Use `gh pr merge --squash` (if approved/passing)
9. **Clean Up Branches**:
   - Delete local branch: `git branch -D ai/<task-name>`
   - Delete remote branch: `git push origin --delete ai/<task-name>`
   - Switch back to main: `git checkout main`
10. **Report Completion**: Provide summary with PR link and changes made

### Post-Execution Cleanup (CRITICAL)

After successfully merging a PR, **ALWAYS** perform these cleanup steps:

```bash
# 1. Switch to main branch
git checkout main

# 2. Delete local feature branch
git branch -D ai/<task-name>

# 3. Delete remote feature branch
git push origin --delete ai/<task-name>

# 4. Verify cleanup
git branch -a  # Should only show main and remotes/origin/main
```

**Why this matters:**
- Prevents branch clutter in the repository
- Follows standard Git workflow best practices
- Keeps repository clean and organized
- Makes it clear which work is in-progress vs completed

### Pull Request Handling
- When you finish a task, push the branch to GitHub
- Create PR using `gh pr create` with comprehensive description including:
  - Summary of changes
  - Testing performed
  - Impact assessment
  - List of commits
  - Co-authored-by tag
- **After merging**: Immediately clean up branches (see Post-Execution Cleanup)
- Include summary of changes and test results in PR description

### Commit Message Format
```
<type>: <subject>

<body>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Development Rules

This project follows **Agency Swarm** tool development standards.

### Core Principles

1. **Tools Must Be Standalone** - Each tool works independently with configurable parameters
2. **Production-Ready Code** - Well-commented, functional code with comprehensive error handling
3. **No Hardcoded Secrets** - Always use environment variables via `os.getenv()`
4. **Test Blocks Required** - Every tool file must include `if __name__ == "__main__":` test block
5. **Pydantic Fields** - Use `Field()` with clear descriptions for all parameters
6. **Atomic & Specific** - Tools perform single, concrete actions
7. **Use Sub-Agents Proactively** - For complex, multi-file, or repetitive tasks (like fixing multiple test files, implementing multiple tools, updating multiple docs), ALWAYS use Task tool with sub-agents without being asked. Don't do these tasks manually.

## File Structure

```
agentswarm-tools/
├── tools/                    # All tool implementations (8 categories)
│   ├── data/                # Search, business analytics, AI intelligence
│   │   ├── search/         # Web, scholar, image, video, product search (8)
│   │   ├── business/       # Data aggregation, reporting, analytics (3)
│   │   └── intelligence/   # RAG pipeline, deep research (2)
│   ├── communication/       # Email, calendar, workspace, messaging, phone (23)
│   ├── media/              # Generation, analysis, processing
│   │   ├── generation/     # Image, video, audio, podcast (7)
│   │   ├── analysis/       # Understanding, transcription (10)
│   │   └── processing/     # Editing, clipping, merging (3)
│   ├── visualization/       # Charts, diagrams, graphs (16)
│   ├── content/            # Documents, web content
│   │   ├── documents/      # Agent creation, office formats, websites (6)
│   │   └── web/           # Crawler, summarization, metadata (4)
│   ├── infrastructure/      # Code execution, storage, management
│   │   ├── execution/      # Bash, Read, Write, MultiEdit (5)
│   │   ├── storage/        # AI Drive, OneDrive, file conversion (4)
│   │   └── management/     # Agent status, task queues (2)
│   ├── utils/              # Utilities and helpers (8)
│   └── integrations/       # External service connectors (0, extensible)
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
    tool_category: str = "data"  # One of: data, communication, media, visualization, content, infrastructure, utils, integrations

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
