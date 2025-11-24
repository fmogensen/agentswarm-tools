# EditTool

Performs exact string replacements in files for surgical code edits.

## Overview

The EditTool provides a reliable way to modify file contents by replacing exact strings. It's designed for surgical edits where you know the exact text to replace and want to ensure precision.

## Features

- **Exact string matching**: Replaces only exact matches
- **Uniqueness validation**: Ensures old_string is unique unless replace_all=True
- **UTF-8 support**: Handles unicode characters correctly
- **Whitespace preservation**: Maintains exact formatting
- **Comprehensive error handling**: Clear validation messages
- **Mock mode support**: Test without actual file modifications

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | str | Yes | Absolute path to file to modify |
| `old_string` | str | Yes | Exact text to replace (min 1 char) |
| `new_string` | str | Yes | Text to replace with (can be empty) |
| `replace_all` | bool | No | Replace all occurrences (default: False) |

## Returns

```python
{
    "success": True,
    "result": {
        "lines_changed": 5,          # Number of lines modified
        "occurrences_replaced": 1,   # Number of replacements made
        "file_path": "/path/to/file" # Path to modified file
    },
    "metadata": {
        "tool_name": "edit_tool",
        "file_path": "/path/to/file"
    }
}
```

## Usage Examples

### Basic Single Replacement

```python
from tools.infrastructure.execution.edit_tool import EditTool

tool = EditTool(
    file_path="/tmp/code.py",
    old_string="def old_function():",
    new_string="def new_function():"
)
result = tool.run()
```

### Replace All Occurrences

```python
tool = EditTool(
    file_path="/tmp/config.txt",
    old_string="localhost",
    new_string="production.server.com",
    replace_all=True
)
result = tool.run()
```

### Multi-line Replacement

```python
tool = EditTool(
    file_path="/tmp/script.py",
    old_string="# Old comment\nold_code()",
    new_string="# New comment\nnew_code()"
)
result = tool.run()
```

### Deletion (Empty new_string)

```python
tool = EditTool(
    file_path="/tmp/text.txt",
    old_string=" unnecessary word",
    new_string=""
)
result = tool.run()
```

## Validation Rules

The tool validates parameters before execution:

1. **Absolute Path**: `file_path` must be an absolute path (starts with `/`)
2. **File Exists**: File must exist and be readable
3. **Not a Directory**: Path must point to a file, not a directory
4. **Different Strings**: `old_string` and `new_string` must be different
5. **String Found**: `old_string` must exist in the file
6. **Uniqueness**: If `replace_all=False`, `old_string` must be unique in the file

## Error Handling

### ValidationError

Raised for invalid parameters or validation failures:

- Non-absolute file path
- File not found
- old_string not found in file
- old_string not unique (when replace_all=False)
- old_string equals new_string

### APIError

Raised for file operation failures:

- Permission denied
- Disk full
- I/O errors

## Mock Mode

Enable mock mode for testing without actual file modifications:

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = EditTool(
    file_path="/any/path/file.txt",
    old_string="old",
    new_string="new"
)
result = tool.run()
# Returns mock results without modifying file
```

## Best Practices

1. **Use Unique Strings**: When possible, include surrounding context to make old_string unique
2. **Verify Before Replace**: Read the file first to confirm old_string exists
3. **Handle Errors**: Always catch ValidationError and APIError
4. **Backup Important Files**: Create backups before modifying critical files
5. **Test First**: Use mock mode to test your edits before running on real files

## Edge Cases

### Case Sensitivity
Replacements are case-sensitive:
```python
# Will only replace "hello", not "Hello" or "HELLO"
tool = EditTool(file_path="/tmp/file.txt", old_string="hello", new_string="hi")
```

### Whitespace Matters
Whitespace is part of the match:
```python
# These are different strings:
"Hello World"   # Single space
"Hello  World"  # Double space
```

### Empty new_string
Empty string effectively deletes old_string:
```python
# Removes "DEPRECATED " from the line
tool = EditTool(
    file_path="/tmp/code.py",
    old_string="DEPRECATED ",
    new_string=""
)
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tools/infrastructure/execution/edit_tool/test_edit_tool.py -v

# Run specific test
pytest tools/infrastructure/execution/edit_tool/test_edit_tool.py::TestEditTool::test_basic_single_replacement -v

# Run built-in tests
python3 -m tools.infrastructure.execution.edit_tool.edit_tool
```

## Related Tools

- **ReadTool**: Read file contents before editing
- **WriteTool**: Create or completely overwrite files
- **MultiEditTool**: Edit multiple files in one operation
- **BashTool**: Use sed/awk for complex pattern replacements

## Implementation Notes

- Uses UTF-8 encoding for all file operations
- Preserves line endings as-is (\\n, \\r\\n)
- Counts lines changed by comparing before/after content
- Validates parameters before processing to fail fast
- Re-raises ValidationError without retry (no point retrying invalid input)
- Retries up to 3 times for transient errors (network drives, etc.)
