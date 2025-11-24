# GlobTool

Fast file pattern matching tool for finding files by name patterns, based on Claude Code's Glob tool specification.

## Overview

GlobTool provides efficient file search capabilities using glob patterns, with results sorted by modification time. It's designed for finding files across codebases of any size.

## Features

- **Fast pattern matching** using Python's glob module
- **Recursive search** with `**` pattern support
- **Sorted results** by modification time (most recent first)
- **Flexible path specification** - search specific directories or use current working directory
- **Comprehensive validation** with clear error messages
- **Mock mode support** for testing
- **Built-in analytics** and performance monitoring

## Installation

The tool is part of the AgentSwarm Tools infrastructure package:

```python
from tools.infrastructure.execution.glob_tool import GlobTool
```

## Usage

### Basic Usage

```python
# Search for Python files in current directory
tool = GlobTool(pattern="*.py")
result = tool.run()

# Access matches
matches = result["result"]["matches"]
count = result["result"]["count"]
```

### Recursive Search

```python
# Search for all Python files recursively
tool = GlobTool(pattern="**/*.py", path="/path/to/project")
result = tool.run()

# Files are sorted by modification time (newest first)
for file_path in result["result"]["matches"]:
    print(file_path)
```

### Multiple Extensions

```python
# Search for JavaScript files
tool = GlobTool(pattern="**/*.js", path="/path/to/project")
result = tool.run()

# Search for TypeScript files
tool = GlobTool(pattern="**/*.ts", path="/path/to/project")
result = tool.run()
```

### Hidden Files

```python
# Find hidden files
tool = GlobTool(pattern=".*", path="/path/to/directory")
result = tool.run()
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | str | Yes | Glob pattern like `**/*.js` or `src/**/*.ts` |
| `path` | str | No | Directory to search in (defaults to current working directory) |

## Response Format

```python
{
    "success": True,
    "result": {
        "matches": [
            "/absolute/path/to/file1.py",
            "/absolute/path/to/file2.py"
        ],
        "count": 2,
        "pattern_used": "**/*.py",
        "search_path": "/absolute/path/to/search"
    },
    "metadata": {
        "tool_name": "glob_tool",
        "pattern": "**/*.py",
        "search_path": "/absolute/path/to/search"
    }
}
```

## Pattern Syntax

GlobTool supports standard glob patterns:

- `*` - Matches any characters (except directory separator)
- `?` - Matches any single character
- `[seq]` - Matches any character in seq
- `[!seq]` - Matches any character not in seq
- `**` - Matches any files and zero or more directories (recursive)

### Examples

```python
# All Python files in current directory (non-recursive)
pattern = "*.py"

# All Python files in all subdirectories (recursive)
pattern = "**/*.py"

# All files in a specific subdirectory
pattern = "src/**/*"

# Test files only
pattern = "**/test_*.py"

# Multiple file types (must use separate calls)
pattern = "**/*.js"  # JavaScript files
pattern = "**/*.ts"  # TypeScript files
```

## Error Handling

The tool validates inputs and provides clear error messages:

### Empty Pattern
```python
tool = GlobTool(pattern="")
result = tool.run()
# Returns: {"success": False, "error": {"code": "VALIDATION_ERROR", ...}}
```

### Invalid Path
```python
tool = GlobTool(pattern="*.py", path="/nonexistent/path")
result = tool.run()
# Returns: {"success": False, "error": {"code": "VALIDATION_ERROR", ...}}
```

### Path is File (Not Directory)
```python
tool = GlobTool(pattern="*.py", path="/path/to/file.txt")
result = tool.run()
# Returns: {"success": False, "error": {"code": "VALIDATION_ERROR", ...}}
```

## Sorting Behavior

Results are automatically sorted by modification time (most recent first):

```python
tool = GlobTool(pattern="**/*.py", path="/project")
result = tool.run()

# First file is the most recently modified
most_recent = result["result"]["matches"][0]

# Last file is the oldest
oldest = result["result"]["matches"][-1]
```

## Testing

GlobTool includes comprehensive tests covering:

- Basic pattern matching
- Recursive searches
- Edge cases (no matches, empty directories)
- Validation scenarios
- Mock mode operation
- Sorting behavior
- Hidden files
- Nested directories

Run tests:

```bash
# Run all glob_tool tests
pytest tools/infrastructure/execution/glob_tool/test_glob_tool.py -v

# Run specific test
pytest tools/infrastructure/execution/glob_tool/test_glob_tool.py::TestGlobTool::test_recursive_pattern_matching -v

# Run built-in test block
python -m tools.infrastructure.execution.glob_tool.glob_tool
```

## Mock Mode

For testing without file system access:

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = GlobTool(pattern="**/*.py")
result = tool.run()

# Returns mock data
assert result["result"]["mock"] == True
assert len(result["result"]["matches"]) == 3
```

## Performance Considerations

- **Large result sets**: GlobTool handles large result sets efficiently
- **Deep directories**: Recursive patterns work well with deeply nested structures
- **Modification time sorting**: Adds minimal overhead for typical result set sizes
- **Path resolution**: All paths are converted to absolute paths

## Comparison with Other Tools

### vs. Find Command
- **GlobTool**: Fast Python implementation, sorted results, structured output
- **Find**: More powerful filtering, but slower for simple pattern matching

### vs. Grep Tool
- **GlobTool**: Searches for file names/patterns
- **GrepTool**: Searches file contents

## Best Practices

1. **Use specific patterns** to reduce result set size:
   ```python
   # Good: Specific pattern
   pattern = "src/**/*.test.py"

   # Less ideal: Too broad
   pattern = "**/*"
   ```

2. **Specify path when possible** to speed up searches:
   ```python
   # Good: Limited scope
   tool = GlobTool(pattern="*.py", path="/project/src")

   # Less ideal: Searches everywhere
   tool = GlobTool(pattern="*.py")
   ```

3. **Handle no matches gracefully**:
   ```python
   result = tool.run()
   if result["result"]["count"] == 0:
       print("No files found matching pattern")
   ```

## Integration Examples

### Find Recently Modified Files

```python
tool = GlobTool(pattern="**/*.py", path="/project")
result = tool.run()

# Get 5 most recently modified files
recent_files = result["result"]["matches"][:5]
```

### Search Multiple Directories

```python
directories = ["/project/src", "/project/tests", "/project/scripts"]
all_matches = []

for directory in directories:
    tool = GlobTool(pattern="*.py", path=directory)
    result = tool.run()
    all_matches.extend(result["result"]["matches"])
```

### Filter by Extension

```python
extensions = ["*.py", "*.js", "*.ts"]
files_by_extension = {}

for ext in extensions:
    tool = GlobTool(pattern=f"**/{ext}", path="/project")
    result = tool.run()
    files_by_extension[ext] = result["result"]["matches"]
```

## Related Tools

- **ReadTool**: Read file contents
- **GrepTool**: Search within file contents
- **BashTool**: Execute shell commands including `find`
- **WriteTool**: Write files

## License

Part of the AgentSwarm Tools Framework.
