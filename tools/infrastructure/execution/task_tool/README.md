# TaskTool

Launch specialized sub-agents for complex multi-step tasks.

## Overview

The TaskTool delegates complex, multi-step operations to specialized sub-agents that can focus on specific types of work. This allows for better task organization and specialized execution strategies based on the task type.

## Features

- **Multiple Agent Types**: Support for general-purpose, code-reviewer, test-runner, and doc-writer agents
- **Task Tracking**: Unique task IDs for monitoring and auditing
- **Execution Reporting**: Comprehensive completion reports with actions taken
- **Mock Mode**: Full mock support for testing without spawning actual agents
- **Validation**: Strict parameter validation with clear error messages

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Detailed task description (min 50 chars) |
| `description` | string | Yes | Short 3-5 word summary (max 50 chars) |
| `subagent_type` | string | Yes | Type of agent to use |

### Subagent Types

- **general-purpose**: For diverse, multi-faceted tasks
- **code-reviewer**: For code analysis, security audits, quality checks
- **test-runner**: For test execution, coverage analysis, test generation
- **doc-writer**: For documentation creation and updates

## Returns

```python
{
    "success": True,
    "result": {
        "task_id": "task_general-purpose_20231124_143022_a1b2c3d4",
        "status": "completed",
        "completion_report": "Sub-agent completed task...",
        "subagent_type": "general-purpose",
        "task_description": "Security audit",
        "execution_time_ms": 2450,
        "actions_taken": [
            "Analyzed task requirements",
            "Executed primary actions",
            "Generated completion report"
        ],
        "started_at": "2023-11-24T14:30:22.123456",
        "completed_at": "2023-11-24T14:30:24.573456"
    },
    "metadata": {
        "tool_name": "task_tool",
        "subagent_type": "general-purpose",
        "task_description": "Security audit",
        "tool_version": "1.0.0"
    }
}
```

## Usage Examples

### Code Review Task

```python
from tools.infrastructure.execution.task_tool import TaskTool

tool = TaskTool(
    prompt="Review the authentication module for security vulnerabilities. "
           "Check for SQL injection, XSS, CSRF, and insecure session management. "
           "Analyze password hashing algorithms and encryption methods. "
           "Provide detailed recommendations for improvements.",
    description="Security code review",
    subagent_type="code-reviewer"
)

result = tool.run()
print(f"Task ID: {result['result']['task_id']}")
print(f"Status: {result['result']['status']}")
print(f"Report: {result['result']['completion_report']}")
```

### Test Execution Task

```python
tool = TaskTool(
    prompt="Execute the entire test suite for the user management module. "
           "Run unit tests, integration tests, and end-to-end tests. "
           "Collect coverage metrics and identify failing tests. "
           "Generate a comprehensive test report with recommendations.",
    description="Run test suite",
    subagent_type="test-runner"
)

result = tool.run()
print(f"Execution time: {result['result']['execution_time_ms']}ms")
print(f"Actions: {result['result']['actions_taken']}")
```

### Documentation Generation

```python
tool = TaskTool(
    prompt="Create comprehensive documentation for the REST API endpoints. "
           "Include detailed descriptions, parameter specifications, and examples. "
           "Add authentication requirements and rate limiting information. "
           "Ensure documentation follows OpenAPI 3.0 specification.",
    description="API documentation",
    subagent_type="doc-writer"
)

result = tool.run()
```

### General Purpose Task

```python
tool = TaskTool(
    prompt="Analyze the database schema for optimization opportunities. "
           "Identify slow queries and missing indexes. "
           "Review the data normalization strategy. "
           "Provide recommendations for performance improvements.",
    description="Database optimization",
    subagent_type="general-purpose"
)

result = tool.run()
```

## Error Handling

The tool validates all parameters and raises clear errors:

```python
# Prompt too short (< 50 characters)
try:
    tool = TaskTool(
        prompt="Short",
        description="Test",
        subagent_type="general-purpose"
    )
    tool.run()
except Exception as e:
    print(f"Error: {e}")
    # Error: Prompt must be at least 50 characters long

# Description too long (> 50 characters)
try:
    tool = TaskTool(
        prompt="Valid long prompt...",
        description="This description is way too long for the field",
        subagent_type="general-purpose"
    )
    tool.run()
except Exception as e:
    print(f"Error: {e}")
    # Error: Description must be 50 characters or less

# Invalid subagent type
try:
    tool = TaskTool(
        prompt="Valid long prompt...",
        description="Valid",
        subagent_type="invalid-type"
    )
    tool.run()
except Exception as e:
    print(f"Error: {e}")
    # Error: Invalid subagent_type: invalid-type
```

## Mock Mode

Enable mock mode for testing without spawning actual agents:

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = TaskTool(
    prompt="Test task with detailed instructions...",
    description="Mock test",
    subagent_type="general-purpose"
)

result = tool.run()
assert result['result']['mock'] == True
```

## Integration with Agent Framework

In a production environment, this tool integrates with an agent orchestration framework to:

1. Spawn specialized agent instances based on `subagent_type`
2. Pass the `prompt` and context to the agent
3. Monitor agent execution and collect metrics
4. Return structured completion reports

The current implementation simulates this behavior for development and testing.

## Best Practices

1. **Detailed Prompts**: Provide comprehensive task descriptions (aim for 100+ chars)
2. **Clear Instructions**: Include specific steps and expected outcomes
3. **Appropriate Agent Type**: Choose the subagent type that matches your task
4. **Concise Descriptions**: Keep descriptions under 50 characters
5. **Error Handling**: Always handle potential ValidationError exceptions

## Testing

Run the test suite:

```bash
pytest tools/infrastructure/execution/task_tool/test_task_tool.py -v
```

Run the built-in test block:

```bash
python tools/infrastructure/execution/task_tool/task_tool.py
```

## Version History

- **1.0.0** (2024-11-24): Initial release with 4 subagent types
