"""Test cases for TaskQueueManager tool."""

import os
import pytest
from .task_queue_manager import TaskQueueManager
from shared.errors import ValidationError


class TestTaskQueueManager:
    """Test suite for TaskQueueManager tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_add_task(self):
        """Test adding a task."""
        tool = TaskQueueManager(
            action="add", task_data={"type": "test", "payload": {"data": "value"}}
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["action"] == "add"
        assert "task_id" in result["result"]

    def test_remove_task(self):
        """Test removing a task."""
        tool = TaskQueueManager(action="remove", task_id="task_123")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["action"] == "remove"
        assert result["result"]["task_id"] == "task_123"

    def test_list_tasks(self):
        """Test listing tasks."""
        tool = TaskQueueManager(action="list")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["action"] == "list"
        assert "tasks" in result["result"]
        assert "total_tasks" in result["result"]

    def test_prioritize_task(self):
        """Test prioritizing a task."""
        tool = TaskQueueManager(action="prioritize", task_id="task_123", priority=9)
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["action"] == "prioritize"
        assert result["result"]["new_priority"] == 9

    def test_clear_queue(self):
        """Test clearing the queue."""
        tool = TaskQueueManager(action="clear")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["action"] == "clear"
        assert "tasks_removed" in result["result"]

    def test_queue_stats(self):
        """Test getting queue stats."""
        tool = TaskQueueManager(action="stats")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["action"] == "stats"
        assert "total_tasks" in result["result"]
        assert "pending" in result["result"]

    def test_custom_queue_id(self):
        """Test with custom queue ID."""
        tool = TaskQueueManager(action="list", queue_id="custom_queue")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["queue_id"] == "custom_queue"

    def test_invalid_action(self):
        """Test invalid action."""
        with pytest.raises(ValidationError):
            tool = TaskQueueManager(action="invalid_action")
            tool._validate_parameters()

    def test_add_without_task_data(self):
        """Test add action without task data."""
        with pytest.raises(ValidationError):
            tool = TaskQueueManager(action="add")
            tool._validate_parameters()

    def test_remove_without_task_id(self):
        """Test remove action without task ID."""
        with pytest.raises(ValidationError):
            tool = TaskQueueManager(action="remove")
            tool._validate_parameters()

    def test_prioritize_without_task_id(self):
        """Test prioritize action without task ID."""
        with pytest.raises(ValidationError):
            tool = TaskQueueManager(action="prioritize", priority=5)
            tool._validate_parameters()

    def test_prioritize_without_priority(self):
        """Test prioritize action without priority."""
        with pytest.raises(ValidationError):
            tool = TaskQueueManager(action="prioritize", task_id="task_123")
            tool._validate_parameters()

    def test_priority_bounds(self):
        """Test priority bounds validation."""
        # Priority too low
        with pytest.raises(Exception):  # Pydantic validation
            tool = TaskQueueManager(
                action="prioritize", task_id="task_123", priority=0  # Below minimum
            )

        # Priority too high
        with pytest.raises(Exception):  # Pydantic validation
            tool = TaskQueueManager(
                action="prioritize", task_id="task_123", priority=11  # Above maximum
            )

    def test_add_with_priority(self):
        """Test adding task with priority."""
        tool = TaskQueueManager(action="add", task_data={"type": "urgent"}, priority=10)
        result = tool.run()

        assert result["success"] == True

    def test_timestamp_in_metadata(self):
        """Test that timestamp is in metadata."""
        tool = TaskQueueManager(action="stats")
        result = tool.run()

        assert result["success"] == True
        assert "metadata" in result
        assert "timestamp" in result["metadata"]

    def test_mock_mode(self):
        """Test mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = TaskQueueManager(action="stats")
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
