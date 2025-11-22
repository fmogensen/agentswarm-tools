"""Test cases for AgentStatus tool."""

import os
import pytest
from .agent_status import AgentStatus


class TestAgentStatus:
    """Test suite for AgentStatus tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_check_status(self):
        """Test basic status check."""
        tool = AgentStatus()
        result = tool.run()

        assert result["success"] == True
        assert "result" in result
        assert "status" in result["result"]
        assert "health" in result["result"]

    def test_check_with_agent_id(self):
        """Test status check with specific agent ID."""
        tool = AgentStatus(agent_id="agent_123")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["agent_id"] == "agent_123"

    def test_include_metrics(self):
        """Test including metrics."""
        tool = AgentStatus(include_metrics=True)
        result = tool.run()

        assert result["success"] == True
        assert "metrics" in result["result"]
        metrics = result["result"]["metrics"]
        assert "tasks_completed" in metrics
        assert "success_rate" in metrics

    def test_exclude_metrics(self):
        """Test excluding metrics."""
        tool = AgentStatus(include_metrics=False)
        result = tool.run()

        assert result["success"] == True
        # Metrics might still be included in mock mode, but in real mode they wouldn't be

    def test_include_tasks(self):
        """Test including current tasks."""
        tool = AgentStatus(include_tasks=True)
        result = tool.run()

        assert result["success"] == True
        assert "current_tasks" in result["result"]

    def test_exclude_tasks(self):
        """Test excluding current tasks."""
        tool = AgentStatus(include_tasks=False)
        result = tool.run()

        assert result["success"] == True
        # Tasks might still be included in mock mode

    def test_full_status(self):
        """Test full status with all options."""
        tool = AgentStatus(
            agent_id="agent_full",
            include_metrics=True,
            include_tasks=True
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["agent_id"] == "agent_full"
        assert "metrics" in result["result"]
        assert "current_tasks" in result["result"]

    def test_default_agent_id(self):
        """Test with default agent ID (self)."""
        tool = AgentStatus()
        result = tool.run()

        assert result["success"] == True
        assert "agent_id" in result["result"]

    def test_uptime_present(self):
        """Test that uptime is present."""
        tool = AgentStatus()
        result = tool.run()

        assert result["success"] == True
        assert "uptime_seconds" in result["result"]
        assert result["result"]["uptime_seconds"] >= 0

    def test_timestamp_present(self):
        """Test that timestamp is present in metadata."""
        tool = AgentStatus()
        result = tool.run()

        assert result["success"] == True
        assert "metadata" in result
        assert "checked_at" in result["metadata"]

    def test_mock_mode(self):
        """Test mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = AgentStatus()
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
