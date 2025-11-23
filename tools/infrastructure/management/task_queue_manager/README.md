# task_queue_manager

Manage agent task queues including adding, removing, and prioritizing tasks.

## Category

Infrastructure & Code Execution

## Parameters

- **action** (str): Action: add, remove, list, prioritize, clear, stats - **Required**
- **task_id** (str): Task ID for remove/prioritize actions - Optional
- **task_data** (Dict[str, Any): Task data for add action - Optional
- **queue_id** (str): No description - Optional
- **priority** (int): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.infrastructure.management.task_queue_manager import TaskQueueManager

# Initialize the tool
tool = TaskQueueManager(
    action="example_value",
    task_id="example_value",  # Optional
    task_data="example_value"  # Optional
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
python task_queue_manager.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
