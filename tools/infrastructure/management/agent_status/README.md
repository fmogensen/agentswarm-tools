# agent_status

Check agent status, health metrics, and performance indicators.

## Category

Infrastructure & Code Execution

## Parameters

- **agent_id** (str): No description - Optional
- **include_metrics** (bool): Whether to include performance metrics - Optional
- **include_tasks** (bool): Whether to include current tasks - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.infrastructure.management.agent_status import AgentStatus

# Initialize the tool
tool = AgentStatus(
    agent_id="example_value",  # Optional
    include_metrics="example_value",  # Optional
    include_tasks="example_value"  # Optional
)

# Run the tool
result = tool.run()

# Check result
if result["success"]:
    print(result["result"])
else:
    print(f"Error: {result.get('error')}")
```

## Testing

Run tests with:
```bash
python agent_status.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
