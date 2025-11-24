# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Repository Overview

AgentSwarm Tools Framework - **117 production-ready tools** organized into **7 streamlined categories** for the SuperAgentSwarm platform, built on the Agency Swarm framework. Adopts MCP-first strategy for enterprise integrations. Tools provide search, media generation, file management, communication, data visualization, and code execution capabilities.

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
│   └── integrations/       # External service connectors (0, use MCP servers instead)
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
    tool_category: str = "data"  # One of: data, communication, media, visualization, content, infrastructure, utils

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

### Critical: Validation Requirements

**MUST implement `_validate_parameters()` with proper error raising:**

```python
def _validate_parameters(self) -> None:
    """Validate all input parameters before execution."""
    # Example validations - ALWAYS raise errors, never return silently

    # 1. Required field validation
    if not self.required_field or not self.required_field.strip():
        raise ValidationError("required_field is required", tool_name=self.tool_name)

    # 2. Enum/choice validation
    valid_choices = ["option1", "option2", "option3"]
    if self.choice_field and self.choice_field not in valid_choices:
        raise ValidationError(
            f"Invalid choice_field: {self.choice_field}. Must be one of: {valid_choices}",
            tool_name=self.tool_name
        )

    # 3. Format validation (email, date, URL, etc.)
    if self.email_field and "@" not in self.email_field:
        raise ValidationError("Invalid email format", tool_name=self.tool_name)

    # 4. Range validation
    if self.numeric_field < 1 or self.numeric_field > 100:
        raise ValidationError(
            f"numeric_field must be between 1 and 100, got {self.numeric_field}",
            tool_name=self.tool_name
        )

    # 5. Logical constraint validation
    if self.start_date and self.end_date and self.start_date > self.end_date:
        raise ValidationError("start_date must be before end_date", tool_name=self.tool_name)

    # 6. Mutually exclusive parameters
    if self.option_a and self.option_b:
        raise ValidationError("Cannot specify both option_a and option_b", tool_name=self.tool_name)

    # 7. Conditional requirements
    if self.operation == "update" and not self.record_id:
        raise ValidationError("record_id is required for update operation", tool_name=self.tool_name)
```

**Common validation patterns for tools:**
- Date formats: `YYYY-MM-DD` or ISO 8601
- ID formats: Proper prefix validation (e.g., `cus_` for Stripe customers)
- Batch size limits: Max 100 items per batch
- Email validation: Basic format check
- URL validation: Proper scheme (http/https)
- Authentication: Check for required API keys/tokens in `_validate_parameters()`

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

## Documentation & Release Management

### Root Directory Organization

**Keep root directory clean with ONLY essential documentation:**

```
root/
├── README.md           # Project overview
├── CHANGELOG.md        # Complete version history (single source of truth)
├── CONTRIBUTING.md     # Contribution guidelines
└── CLAUDE.md          # AI development guidelines (this file)
```

**Rules:**
- ❌ **NEVER create versioned release notes** (e.g., `RELEASE_NOTES_v1.2.0.md`)
- ❌ **NEVER create versioned migration guides** (e.g., `MIGRATION_GUIDE_v1.2.0.md`)
- ❌ **NEVER create standalone deprecation files** (e.g., `DEPRECATION_TIMELINE.md`)
- ❌ **NEVER create standalone test reports** (e.g., `TEST_REPORT.md`)
- ✅ **ALWAYS update CHANGELOG.md** for all releases and changes

### CHANGELOG.md Format

Follow [Keep a Changelog](https://keepachangelog.com/) standard:

```markdown
## [Unreleased]

## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes

### Migration Notes
- Breaking changes and upgrade instructions
```

**Guidelines:**
- Include migration notes directly in each version section
- Document breaking changes with clear upgrade paths
- Keep deprecation notices within relevant version entries
- Link to related PRs and issues
- Use semantic versioning (Major.Minor.Patch)

### When Creating Releases

1. **Update CHANGELOG.md** with new version section
2. **Include migration notes** if breaking changes exist
3. **Document all changes** (Added, Changed, Deprecated, Removed, Fixed)
4. **Create git tag**: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
5. **Push tag**: `git push origin vX.Y.Z`
6. **Use GitHub Releases** for detailed release notes (not root files)

**DO NOT create separate versioned documentation files in root.**

## Code Quality & CI/CD Standards

### Pre-Commit Requirements

**ALWAYS run before committing:**

```bash
# 1. Format code with Black
black .

# 2. Sort imports with isort
isort .

# 3. Run linters
flake8 .

# 4. Run tests locally
pytest tests/ -v

# 5. Check coverage
pytest --cov=. --cov-report=term-missing
```

### Code Formatting Rules

1. **Black**: All Python code MUST be formatted with Black (line length 127)
2. **isort**: All imports MUST be sorted with isort
3. **Flake8**: Code MUST pass flake8 linting (E9, F63, F7, F82 errors are blocking)
4. **Type Hints**: Prefer type hints for function signatures
5. **Docstrings**: Use Google-style docstrings for all public functions/classes

### Import Organization

**CRITICAL**: All imports must be properly organized and complete

```python
# Standard library imports (alphabetical)
import hashlib
import hmac
import json
import os
import warnings  # ALWAYS import warnings if using warnings.warn()
from datetime import datetime
from typing import Any, Dict, List, Optional

# Third-party imports (alphabetical)
from pydantic import Field

# Local imports (alphabetical)
from shared.base import BaseTool
from shared.errors import (
    APIError,
    AuthenticationError,
    SecurityError,  # Import ALL error types used
    ValidationError,
)
```

**Common Import Mistakes to Avoid:**
- ❌ Using `SecurityWarning` without importing it
- ❌ Using `warnings.warn()` without `import warnings`
- ❌ Importing from a module that doesn't export the attribute
- ✅ ALWAYS verify imports match usage in code

### Testing Before Commit

**Required checks before pushing:**

1. **Local test run**: `pytest tests/ -v` - ALL tests must pass
2. **Format check**: `black --check .` - No files should need reformatting
3. **Import check**: `isort --check-only .` - Imports must be sorted
4. **Lint check**: `flake8 .` - No critical errors

**If any check fails:**
- Fix formatting: `black .`
- Fix imports: `isort .`
- Fix validation: Add proper error raising in `_validate_parameters()`
- Fix tests: Ensure tool behavior matches test expectations

### CI/CD Workflow Success Criteria

**All three workflows must pass:**

1. ✅ **Code Quality** (lint.yml):
   - Black formatting check passes
   - isort import sorting passes
   - Flake8 linting passes (critical errors only)
   - MyPy type checking (non-blocking)
   - Pylint (non-blocking)

2. ✅ **Test Suite** (test.yml):
   - All unit tests pass (Python 3.12 and 3.13)
   - Integration tests pass (allowed to continue on error)
   - Coverage meets threshold (70% minimum)

3. ✅ **Security Scan** (security.yml):
   - Bandit security scan passes
   - Safety dependency check passes
   - CodeQL analysis passes

### Debugging CI/CD Failures

**When workflows fail:**

1. **View failure logs**: `gh run view <run-id> --log-failed`
2. **Check error type**:
   - Formatting errors → Run `black .` and `isort .`
   - Import errors → Check for missing imports, typos in module names
   - Test failures → Check if `_validate_parameters()` raises proper errors
   - Coverage failures → Add tests for uncovered code paths

3. **Reproduce locally**:
   ```bash
   # Run exact CI command locally
   pytest tests/unit/tools/ tests/integration/ -v --cov=. --cov-report=term-missing
   ```

4. **Common fixes**:
   - Missing imports: Add to import block
   - Validation not implemented: Add proper error raising
   - Tests expect errors: Make sure tool validates and raises `ValidationError`/`AuthenticationError`

## Important Instructions

- **FOLLOW** Agency Swarm tool development standards
- **Tools must be standalone** with test blocks
- **Never hardcode secrets** - use environment variables
- **Use Pydantic Field()** with descriptions for all parameters
- **Tools perform concrete, atomic actions** - avoid abstract tools
- **Always implement all 5 required methods** in tool classes
- **Test with mock mode** before testing with real APIs
- **Keep root directory clean** - only essential docs (README, CHANGELOG, CONTRIBUTING, CLAUDE)
- **Use CHANGELOG.md as single source of truth** - no versioned release files

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
