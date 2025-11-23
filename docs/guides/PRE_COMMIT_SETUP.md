# Pre-Commit Hooks Setup Guide

**Version:** 2.0.0
**Last Updated:** 2025-11-23

This guide explains how to set up and use pre-commit hooks for automated code quality checks in the AgentSwarm Tools repository.

## Table of Contents

- [What are Pre-Commit Hooks?](#what-are-pre-commit-hooks)
- [Quick Setup](#quick-setup)
- [Hook Overview](#hook-overview)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Customization](#customization)
- [CI/CD Integration](#cicd-integration)

## What are Pre-Commit Hooks?

Pre-commit hooks are automated checks that run before you commit code to Git. They help ensure:

- **Code Quality**: Consistent formatting and style
- **Security**: Detection of potential security issues
- **Testing**: Fast verification that code works
- **Standards Compliance**: Adherence to project conventions

In this repository, pre-commit hooks automatically run:
1. Black code formatter
2. isort import sorter
3. flake8 linter
4. mypy type checker
5. bandit security scanner
6. pytest quick tests

## Quick Setup

### Step 1: Install pre-commit

```bash
# Install pre-commit framework
pip install pre-commit

# Or if using the project's virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pre-commit
```

### Step 2: Install Git Hooks

```bash
# From repository root
cd /path/to/agentswarm-tools

# Install the hooks
pre-commit install
```

You should see:
```
pre-commit installed at .git/hooks/pre-commit
```

### Step 3: (Optional) Run on All Files

```bash
# Run hooks on all files (good for initial setup)
pre-commit run --all-files
```

**Note:** This may take a few minutes on first run as it sets up environments.

## Hook Overview

### 1. Black - Code Formatting

**What it does:** Formats Python code to Black's opinionated style
**Config:** Python 3.12 language version
**Why:** Ensures consistent code style across all contributions

**Example:**
```python
# Before
def   my_function(  x,y  ):
    return x+y

# After (Black formatted)
def my_function(x, y):
    return x + y
```

### 2. isort - Import Sorting

**What it does:** Sorts and organizes Python imports
**Config:** Default isort settings
**Why:** Consistent import organization, easier to read

**Example:**
```python
# Before
import os
from pydantic import Field
import sys
from shared.base import BaseTool

# After (isort)
import os
import sys

from pydantic import Field

from shared.base import BaseTool
```

### 3. flake8 - Linting

**What it does:** Checks for code style violations and errors
**Config:** Max line length 100 characters
**Why:** Catches common mistakes and style issues

**Common checks:**
- Unused imports
- Undefined variables
- Line too long
- Trailing whitespace

### 4. mypy - Type Checking

**What it does:** Verifies type hints are correct
**Config:** Includes pydantic>=2.0.0
**Why:** Catches type-related bugs before runtime

**Example:**
```python
def add(x: int, y: int) -> int:
    return x + y

# mypy will catch:
result: str = add(1, 2)  # Error: int is not compatible with str
```

### 5. bandit - Security Scanning

**What it does:** Scans for common security issues
**Config:** Low severity (-ll), recursive on tools/ and shared/
**Why:** Prevents security vulnerabilities

**Detects:**
- Hardcoded passwords/secrets
- Unsafe use of `eval()`, `exec()`
- SQL injection risks
- Insecure random number generation

### 6. pytest-quick - Fast Tests

**What it does:** Runs unit tests marked as quick
**Config:** `-m "unit and not slow"` marker
**Why:** Fast verification before commit

**Note:** Only runs fast unit tests, not full integration suite.

## Usage

### Normal Workflow

Once installed, hooks run automatically:

```bash
# Make your changes
vim tools/data/search/web_search/__init__.py

# Stage changes
git add tools/data/search/web_search/__init__.py

# Commit - hooks run automatically
git commit -m "Update web search tool"
```

### Hook Output

When you commit, you'll see:

```
black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
mypy.....................................................................Passed
bandit...................................................................Passed
pytest-quick.............................................................Passed
[main abc1234] Update web search tool
 1 file changed, 10 insertions(+), 5 deletions(-)
```

### If Hooks Fail

If a hook fails, your commit is blocked:

```
black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted tools/data/search/web_search/__init__.py
```

**What to do:**
1. Review the changes made by the hooks
2. Stage the fixed files: `git add tools/data/search/web_search/__init__.py`
3. Commit again: `git commit -m "Update web search tool"`

### Skip Hooks (Not Recommended)

In rare cases, you can bypass hooks:

```bash
# Skip all hooks (use sparingly!)
git commit --no-verify -m "Emergency hotfix"
```

**Warning:** Only use `--no-verify` for emergency situations. Your PR may fail CI checks.

## Troubleshooting

### Hook Installation Issues

**Problem:** `pre-commit: command not found`

**Solution:**
```bash
# Ensure pre-commit is installed
pip install pre-commit

# Verify installation
pre-commit --version
```

### Black/isort Conflicts

**Problem:** Black and isort keep reformatting the same file differently

**Solution:**
```bash
# Update to compatible versions (already in .pre-commit-config.yaml)
pre-commit autoupdate

# Run isort with Black profile
isort --profile black tools/ shared/
```

### mypy Type Errors

**Problem:** mypy reports type errors in existing code

**Solution:**
```bash
# Add type: ignore comment for known issues
result = api_call()  # type: ignore[attr-defined]

# Or add type hints
result: Dict[str, Any] = api_call()
```

### Bandit False Positives

**Problem:** Bandit flags safe code as insecure

**Solution:**
```bash
# Add nosec comment with justification
password = os.getenv("API_PASSWORD")  # nosec B105 - from environment
```

### pytest-quick Failures

**Problem:** Fast tests fail before commit

**Solution:**
```bash
# Run tests manually to debug
pytest -m "unit and not slow" -v

# Fix the failing tests
# Then commit again
```

### Hook Hangs or Times Out

**Problem:** A hook runs forever

**Solution:**
```bash
# Kill the process (Ctrl+C)
# Run the hook manually to debug
pre-commit run <hook-id> --all-files

# Example:
pre-commit run mypy --all-files
```

## Customization

### Skip Specific Hooks

Create `.pre-commit-config.yaml` in your home directory:

```yaml
# Skip hooks you don't want
default_stages: [commit]
skip:
  - mypy  # Skip type checking
```

### Modify Hook Arguments

Edit `.pre-commit-config.yaml`:

```yaml
# Change flake8 line length
- repo: https://github.com/PyCQA/flake8
  rev: 6.1.0
  hooks:
    - id: flake8
      args: ['--max-line-length=120']  # Changed from 100
```

### Add File Exclusions

```yaml
# Exclude specific files/directories
- repo: https://github.com/psf/black
  rev: 23.12.0
  hooks:
    - id: black
      exclude: ^legacy/  # Skip legacy directory
```

### Update Hook Versions

```bash
# Update to latest versions
pre-commit autoupdate

# This updates all hooks in .pre-commit-config.yaml
```

## CI/CD Integration

### GitHub Actions

Pre-commit hooks also run in CI:

```yaml
# .github/workflows/ci.yml
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
```

### Local Testing Before Push

```bash
# Run all hooks on changed files
pre-commit run

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

## Best Practices

### 1. Install Hooks Immediately

```bash
# After cloning the repository
git clone https://github.com/genspark/agentswarm-tools.git
cd agentswarm-tools
pip install -r requirements.txt
pre-commit install  # Don't forget this!
```

### 2. Run Before Large Commits

```bash
# Before committing many files
pre-commit run --all-files

# Then commit
git commit -m "Large refactoring"
```

### 3. Keep Hooks Updated

```bash
# Periodically update hooks
pre-commit autoupdate

# Commit the updated config
git add .pre-commit-config.yaml
git commit -m "Update pre-commit hooks"
```

### 4. Format Code Before Committing

```bash
# Manually format code
black tools/ shared/ tests/
isort tools/ shared/ tests/

# Then commit
git add .
git commit -m "Format code"
```

### 5. Write Type Hints

```python
# Good - clear types
def search(query: str, max_results: int = 10) -> Dict[str, Any]:
    return {"results": []}

# Bad - no type hints
def search(query, max_results=10):
    return {"results": []}
```

## Testing Your Setup

### Verify Installation

```bash
# Check pre-commit is installed
pre-commit --version

# List installed hooks
pre-commit run --all-files --verbose
```

### Test Each Hook

```bash
# Test Black
pre-commit run black --all-files

# Test isort
pre-commit run isort --all-files

# Test flake8
pre-commit run flake8 --all-files

# Test mypy
pre-commit run mypy --all-files

# Test bandit
pre-commit run bandit --all-files

# Test pytest-quick
pre-commit run pytest-quick
```

### Verify Git Integration

```bash
# Create a test commit
echo "# Test" >> test_file.py
git add test_file.py
git commit -m "Test pre-commit hooks"

# Hooks should run automatically
# Clean up
git reset HEAD~1
rm test_file.py
```

## Hook Execution Time

Typical execution times:

| Hook | Time | When it Runs |
|------|------|--------------|
| Black | 1-3s | On modified Python files |
| isort | 1-2s | On modified Python files |
| flake8 | 2-5s | On modified Python files |
| mypy | 5-10s | On modified Python files |
| bandit | 3-5s | Always (tools/, shared/) |
| pytest-quick | 5-15s | Always (unit tests only) |

**Total:** ~20-40 seconds for typical commits

## FAQ

### Q: Can I skip hooks for a single commit?

**A:** Yes, but not recommended:
```bash
git commit --no-verify -m "Skip hooks"
```

### Q: Why are my commits being rejected?

**A:** A hook found an issue. Check the output and fix the problems.

### Q: Can I configure hooks per-developer?

**A:** Yes, create `~/.pre-commit-config.yaml` for personal overrides.

### Q: Do hooks run on all files every time?

**A:** No, only on staged files unless you use `--all-files`.

### Q: How do I disable a specific hook?

**A:** Edit `.pre-commit-config.yaml` and remove or comment out the hook.

### Q: Why is mypy failing on valid code?

**A:** Type hints may be incomplete. Add proper type annotations or `# type: ignore`.

## Additional Resources

- [pre-commit documentation](https://pre-commit.com/)
- [Black formatter](https://black.readthedocs.io/)
- [isort](https://pycqa.github.io/isort/)
- [flake8](https://flake8.pycqa.org/)
- [mypy](https://mypy.readthedocs.io/)
- [bandit](https://bandit.readthedocs.io/)
- [Contributing Guide](../../CONTRIBUTING.md)
- [Testing Guide](TESTING_GUIDE.md)

## Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review the [CONTRIBUTING.md](../../CONTRIBUTING.md) guide
3. Check [GitHub Issues](https://github.com/genspark/agentswarm-tools/issues)
4. Ask in project discussions

---

**Remember:** Pre-commit hooks are your friends! They catch issues early and maintain code quality across the entire project.
