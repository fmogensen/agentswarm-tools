# BashOutputTool

Monitor output from background bash processes. Retrieves new output since the last check from running or completed shell processes with optional regex filtering.

## Category
**Infrastructure / Execution**

## Description

BashOutputTool enables monitoring of background bash shell processes by retrieving output that has been generated since the last check. It supports:

- Retrieving new output lines from background shells
- Optional regex pattern filtering to extract specific lines
- Shell status tracking (running, completed, failed)
- Output buffer management (tracks read position)
- Case-insensitive pattern matching

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `shell_id` | str | Yes | ID of the background shell to monitor (min length: 1) |
| `filter_pattern` | str | No | Optional regex pattern to filter output lines |

## Returns

```python
{
    "success": True,
    "result": {
        "shell_id": "shell_12345",
        "output_lines": ["Line 1", "Line 2", ...],
        "filtered_lines_count": 2,
        "total_lines": 10,
        "shell_status": "running",  # or "completed", "failed"
        "has_more": True
    },
    "metadata": {
        "tool_name": "bash_output_tool",
        "tool_version": "1.0.0"
    }
}
```

## Use Cases

1. **Monitor Long-Running Processes**
   ```python
   tool = BashOutputTool(shell_id="build_process_001")
   result = tool.run()
   print(result['result']['output_lines'])
   ```

2. **Filter for Errors and Warnings**
   ```python
   tool = BashOutputTool(
       shell_id="app_server_001",
       filter_pattern="error|warning|exception"
   )
   result = tool.run()
   # Only lines matching the pattern are returned
   ```

3. **Check Deployment Status**
   ```python
   tool = BashOutputTool(
       shell_id="deployment_001",
       filter_pattern="^(SUCCESS|FAILED|ERROR)"
   )
   result = tool.run()
   status = result['result']['shell_status']
   ```

4. **Continuous Log Monitoring**
   ```python
   # First check
   tool1 = BashOutputTool(shell_id="log_monitor")
   result1 = tool1.run()  # Gets all output

   # Second check (later)
   tool2 = BashOutputTool(shell_id="log_monitor")
   result2 = tool2.run()  # Gets only new output since first check
   ```

## Validation Rules

### Required Validations
- `shell_id` must not be empty or whitespace-only
- `filter_pattern` must be valid regex (if provided)

### Error Cases

**ValidationError**:
- Empty `shell_id`
- Whitespace-only `shell_id`
- Invalid regex pattern in `filter_pattern`

**APIError**:
- Shell ID not found in registry
- Output retrieval failure

## Examples

### Basic Output Retrieval

```python
from tools.infrastructure.execution.bash_output_tool import BashOutputTool

tool = BashOutputTool(shell_id="shell_001")
result = tool.run()

if result['success']:
    lines = result['result']['output_lines']
    status = result['result']['shell_status']
    print(f"Shell status: {status}")
    print(f"New lines: {len(lines)}")
    for line in lines:
        print(line)
```

### Filtered Output

```python
# Find all error messages
tool = BashOutputTool(
    shell_id="app_001",
    filter_pattern=r"ERROR:\s+.*"
)
result = tool.run()

error_lines = result['result']['output_lines']
print(f"Found {len(error_lines)} error messages")
```

### Complex Pattern Matching

```python
# Match multiple patterns with OR
tool = BashOutputTool(
    shell_id="test_run",
    filter_pattern=r"(PASSED|FAILED|ERROR|WARNING)"
)
result = tool.run()

# Match lines starting with specific prefixes
tool = BashOutputTool(
    shell_id="deployment",
    filter_pattern=r"^(INFO|WARN|ERROR):\s+"
)
result = tool.run()

# Match lines with timestamps
tool = BashOutputTool(
    shell_id="server_log",
    filter_pattern=r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
)
result = tool.run()
```

### Continuous Monitoring Loop

```python
import time
from tools.infrastructure.execution.bash_output_tool import BashOutputTool

shell_id = "background_process"

while True:
    tool = BashOutputTool(shell_id=shell_id)
    result = tool.run()

    if result['success']:
        lines = result['result']['output_lines']
        if lines:
            print(f"New output ({len(lines)} lines):")
            for line in lines:
                print(f"  {line}")

        # Check if shell is still running
        if result['result']['shell_status'] != 'running':
            print(f"Shell completed with status: {result['result']['shell_status']}")
            break

    time.sleep(5)  # Check every 5 seconds
```

## Implementation Details

### Output Buffer Management

The tool maintains internal state to track:
- **Shell Registry**: Maps shell IDs to shell metadata (status, creation time)
- **Output Buffers**: Stores all output lines for each shell
- **Read Positions**: Tracks how much output has been read per shell

When you call the tool multiple times with the same `shell_id`, it only returns new output since the last read.

### Filter Pattern Behavior

- **Case Insensitive**: All pattern matching is case-insensitive by default
- **Line-Based**: Filter is applied to each line independently
- **Regex Support**: Full Python regex syntax is supported
- **No Match**: Returns empty list if no lines match

### Shell Status Values

| Status | Description |
|--------|-------------|
| `running` | Shell is actively executing |
| `completed` | Shell finished successfully |
| `failed` | Shell terminated with error |

## Testing

### Run Built-in Tests

```bash
PYTHONPATH=. python3 tools/infrastructure/execution/bash_output_tool/bash_output_tool.py
```

### Run Comprehensive Test Suite

```bash
pytest tools/infrastructure/execution/bash_output_tool/test_bash_output_tool.py -v
```

### Test Coverage

The test suite includes 20+ comprehensive tests covering:
- Basic output retrieval
- Filter pattern matching (basic, OR, special chars)
- Empty shell_id validation
- Invalid regex validation
- Multiple reads (output depletion)
- Non-existent shell handling
- Large output handling
- Unicode output
- Empty output scenarios
- Shell status states
- Edge cases (long IDs, special characters)

## Mock Mode

Enable mock mode for testing without actual shell processes:

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = BashOutputTool(shell_id="mock_shell")
result = tool.run()
# Returns simulated output data
```

Mock mode returns realistic test data including:
- 5 sample output lines
- Simulated shell status
- Proper filtering behavior
- Mock indicator in results

## Integration with Other Tools

### Chain with BashTool

```python
from tools.infrastructure.execution.bash_tool import BashTool
from tools.infrastructure.execution.bash_output_tool import BashOutputTool

# Start background process (requires BashTool enhancement)
# Then monitor it
tool = BashOutputTool(shell_id="process_123")
result = tool.run()
```

### Use in Monitoring Agents

```python
class ProcessMonitor:
    def __init__(self, shell_id):
        self.shell_id = shell_id

    def check_for_errors(self):
        tool = BashOutputTool(
            shell_id=self.shell_id,
            filter_pattern="error|exception|failed"
        )
        result = tool.run()

        if result['success']:
            error_lines = result['result']['output_lines']
            if error_lines:
                # Alert on errors
                self.send_alert(error_lines)
```

## Notes

- **Read Position Tracking**: Output is tracked per shell ID. Each read advances the read position.
- **Production Usage**: In production, shell registry would connect to a persistent store or API.
- **Filter Performance**: Regex compilation is validated during parameter validation for early error detection.
- **Thread Safety**: Current implementation is not thread-safe. Use locks if accessing from multiple threads.

## Related Tools

- **BashTool**: Execute bash commands in sandboxed environment
- **Read**: Read file contents
- **Write**: Write file contents
- **AgentStatus**: Check agent status and metrics

## Version

**1.0.0** - Initial implementation

## License

Part of AgentSwarm Tools Framework
