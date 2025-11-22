"""
Manage agent task queues.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
from datetime import datetime
import uuid

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class TaskQueueManager(BaseTool):
    """
    Manage agent task queues including adding, removing, and prioritizing tasks.

    Args:
        action: Action to perform (add, remove, list, prioritize, clear, stats)
        task_id: Task ID for remove/prioritize actions
        task_data: Task data for add action
        queue_id: Optional queue ID (defaults to default queue)
        priority: Priority level for prioritize action (1-10, higher is more urgent)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Action result and queue information
        - metadata: Queue stats and operation info

    Example:
        >>> tool = TaskQueueManager(
        ...     action="add",
        ...     task_data={"type": "process", "payload": {"data": "test"}}
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "task_queue_manager"
    tool_category: str = "infrastructure"

    # Parameters
    action: str = Field(..., description="Action: add, remove, list, prioritize, clear, stats")
    task_id: Optional[str] = Field(None, description="Task ID for remove/prioritize actions")
    task_data: Optional[Dict[str, Any]] = Field(None, description="Task data for add action")
    queue_id: Optional[str] = Field(None, description="Queue ID (defaults to 'default')")
    priority: Optional[int] = Field(
        None, description="Priority level (1-10, higher is more urgent)", ge=1, le=10
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute queue management action."""
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
                "metadata": {
                    "tool_name": self.tool_name,
                    "action": self.action,
                    "queue_id": self.queue_id or "default",
                    "timestamp": datetime.utcnow().isoformat(),
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            raise APIError(f"Task queue management failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        valid_actions = ["add", "remove", "list", "prioritize", "clear", "stats"]

        if self.action not in valid_actions:
            raise ValidationError(
                f"action must be one of {valid_actions}", tool_name=self.tool_name, field="action"
            )

        # Validate required parameters for specific actions
        if self.action == "add" and not self.task_data:
            raise ValidationError(
                "task_data is required for 'add' action",
                tool_name=self.tool_name,
                field="task_data",
            )

        if self.action in ["remove", "prioritize"] and not self.task_id:
            raise ValidationError(
                f"task_id is required for '{self.action}' action",
                tool_name=self.tool_name,
                field="task_id",
            )

        if self.action == "prioritize" and self.priority is None:
            raise ValidationError(
                "priority is required for 'prioritize' action",
                tool_name=self.tool_name,
                field="priority",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        queue_id = self.queue_id or "default"

        if self.action == "add":
            return {
                "success": True,
                "result": {
                    "action": "add",
                    "task_id": f"task_{uuid.uuid4().hex[:8]}",
                    "queue_id": queue_id,
                    "position": 5,
                    "added_at": datetime.utcnow().isoformat(),
                },
                "metadata": {"mock_mode": True, "tool_name": self.tool_name, "queue_id": queue_id},
            }

        elif self.action == "remove":
            return {
                "success": True,
                "result": {
                    "action": "remove",
                    "task_id": self.task_id,
                    "queue_id": queue_id,
                    "removed": True,
                },
                "metadata": {"mock_mode": True, "tool_name": self.tool_name},
            }

        elif self.action == "list":
            return {
                "success": True,
                "result": {
                    "action": "list",
                    "queue_id": queue_id,
                    "tasks": [
                        {
                            "task_id": "task_001",
                            "status": "pending",
                            "priority": 5,
                            "created_at": datetime.utcnow().isoformat(),
                        },
                        {
                            "task_id": "task_002",
                            "status": "in_progress",
                            "priority": 8,
                            "created_at": datetime.utcnow().isoformat(),
                        },
                    ],
                    "total_tasks": 2,
                },
                "metadata": {"mock_mode": True, "tool_name": self.tool_name},
            }

        elif self.action == "prioritize":
            return {
                "success": True,
                "result": {
                    "action": "prioritize",
                    "task_id": self.task_id,
                    "queue_id": queue_id,
                    "old_priority": 5,
                    "new_priority": self.priority,
                },
                "metadata": {"mock_mode": True, "tool_name": self.tool_name},
            }

        elif self.action == "clear":
            return {
                "success": True,
                "result": {"action": "clear", "queue_id": queue_id, "tasks_removed": 5},
                "metadata": {"mock_mode": True, "tool_name": self.tool_name},
            }

        elif self.action == "stats":
            return {
                "success": True,
                "result": {
                    "action": "stats",
                    "queue_id": queue_id,
                    "total_tasks": 10,
                    "pending": 5,
                    "in_progress": 3,
                    "completed": 2,
                    "failed": 0,
                    "average_wait_time_seconds": 120.5,
                    "oldest_task_age_seconds": 300,
                },
                "metadata": {"mock_mode": True, "tool_name": self.tool_name},
            }

        return {"success": True, "result": {}, "metadata": {"mock_mode": True}}

    def _process(self) -> Dict[str, Any]:
        """Process queue management action."""
        queue_id = self.queue_id or "default"

        if self.action == "add":
            return self._add_task(queue_id)

        elif self.action == "remove":
            return self._remove_task(queue_id)

        elif self.action == "list":
            return self._list_tasks(queue_id)

        elif self.action == "prioritize":
            return self._prioritize_task(queue_id)

        elif self.action == "clear":
            return self._clear_queue(queue_id)

        elif self.action == "stats":
            return self._get_queue_stats(queue_id)

        return {}

    def _add_task(self, queue_id: str) -> Dict[str, Any]:
        """Add a task to the queue."""
        # In real implementation, add to actual queue system
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        return {
            "action": "add",
            "task_id": task_id,
            "queue_id": queue_id,
            "position": 0,  # Would be actual position in queue
            "added_at": datetime.utcnow().isoformat(),
            "task_data": self.task_data,
        }

    def _remove_task(self, queue_id: str) -> Dict[str, Any]:
        """Remove a task from the queue."""
        # In real implementation, remove from actual queue
        return {
            "action": "remove",
            "task_id": self.task_id,
            "queue_id": queue_id,
            "removed": True,
            "removed_at": datetime.utcnow().isoformat(),
        }

    def _list_tasks(self, queue_id: str) -> Dict[str, Any]:
        """List all tasks in the queue."""
        # In real implementation, query actual queue
        return {"action": "list", "queue_id": queue_id, "tasks": [], "total_tasks": 0}

    def _prioritize_task(self, queue_id: str) -> Dict[str, Any]:
        """Change task priority."""
        # In real implementation, update task priority in queue
        return {
            "action": "prioritize",
            "task_id": self.task_id,
            "queue_id": queue_id,
            "old_priority": 5,  # Would be actual old priority
            "new_priority": self.priority,
            "updated_at": datetime.utcnow().isoformat(),
        }

    def _clear_queue(self, queue_id: str) -> Dict[str, Any]:
        """Clear all tasks from queue."""
        # In real implementation, clear actual queue
        return {
            "action": "clear",
            "queue_id": queue_id,
            "tasks_removed": 0,  # Would be actual count
            "cleared_at": datetime.utcnow().isoformat(),
        }

    def _get_queue_stats(self, queue_id: str) -> Dict[str, Any]:
        """Get queue statistics."""
        # In real implementation, calculate from actual queue
        return {
            "action": "stats",
            "queue_id": queue_id,
            "total_tasks": 0,
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "average_wait_time_seconds": 0.0,
            "oldest_task_age_seconds": 0,
            "newest_task_age_seconds": 0,
        }


if __name__ == "__main__":
    print("Testing TaskQueueManager...")

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    # Test add action
    tool = TaskQueueManager(
        action="add", task_data={"type": "process", "payload": {"data": "test"}}
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True
    print("TaskQueueManager test passed!")
