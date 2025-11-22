# Agent Management Tools

This directory contains tools for managing agents, monitoring their status, and controlling task queues.

## Tools

### AgentStatus
**File:** `agent_status/agent_status.py`

Check agent status, health metrics, and performance indicators.

**Example:**
```python
from tools.agent_management.agent_status import AgentStatus

tool = AgentStatus(
    agent_id="agent_001",
    include_metrics=True,
    include_tasks=True
)
result = tool.run()
```

### TaskQueueManager
**File:** `task_queue_manager/task_queue_manager.py`

Manage agent task queues including adding, removing, and prioritizing tasks.

**Example:**
```python
from tools.agent_management.task_queue_manager import TaskQueueManager

# Add task
tool = TaskQueueManager(
    action="add",
    task_data={"type": "process", "payload": {"data": "test"}},
    priority=8
)
result = tool.run()

# Get stats
tool = TaskQueueManager(action="stats")
result = tool.run()
```

## Usage

All tools follow the Agency Swarm pattern:
1. Import the tool
2. Initialize with parameters
3. Call `run()` method
4. Check `result['success']` and process `result['result']`

## Queue Actions

TaskQueueManager supports these actions:
- `add` - Add task to queue
- `remove` - Remove task from queue
- `list` - List all tasks
- `prioritize` - Change task priority (1-10)
- `clear` - Clear queue
- `stats` - Get statistics

## Testing

Each tool has a comprehensive test file:
- `test_agent_status.py`
- `test_task_queue_manager.py`

Run tests:
```bash
python3 -m pytest tools/agent_management/
```

## Documentation

See [PHASE_2_TOOLS_GUIDE.md](../../PHASE_2_TOOLS_GUIDE.md) for complete usage examples.
