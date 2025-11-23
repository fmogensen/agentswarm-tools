"""
Check agent status and health metrics.
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class AgentStatus(BaseTool):
    """
    Check agent status, health metrics, and performance indicators.

    Args:
        agent_id: ID of the agent to check (optional, defaults to self)
        include_metrics: Whether to include performance metrics (default: True)
        include_tasks: Whether to include current tasks (default: True)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Agent status, health, and metrics
        - metadata: Status check info and timestamp

    Example:
        >>> tool = AgentStatus(
        ...     agent_id="agent_001",
        ...     include_metrics=True
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "agent_status"
    tool_category: str = "infrastructure"

    # Parameters
    agent_id: Optional[str] = Field(None, description="ID of the agent to check (None for self)")
    include_metrics: bool = Field(True, description="Whether to include performance metrics")
    include_tasks: bool = Field(True, description="Whether to include current tasks")

    def _execute(self) -> Dict[str, Any]:
        """Execute agent status check."""
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
                    "agent_id": self.agent_id or "self",
                    "checked_at": datetime.utcnow().isoformat(),
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            raise APIError(f"Agent status check failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        # No strict validation needed for optional agent_id
        pass

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        mock_result = {
            "agent_id": self.agent_id or "agent_mock_001",
            "status": "active",
            "health": "healthy",
            "uptime_seconds": 3600,
            "last_activity": datetime.utcnow().isoformat(),
        }

        if self.include_metrics:
            mock_result["metrics"] = {
                "tasks_completed": 42,
                "tasks_failed": 2,
                "average_response_time_ms": 150.5,
                "cpu_usage_percent": 25.0,
                "memory_usage_mb": 512.0,
                "success_rate": 95.5,
            }

        if self.include_tasks:
            mock_result["current_tasks"] = [
                {
                    "task_id": "task_001",
                    "status": "in_progress",
                    "started_at": datetime.utcnow().isoformat(),
                },
                {
                    "task_id": "task_002",
                    "status": "queued",
                    "queued_at": datetime.utcnow().isoformat(),
                },
            ]

        return {
            "success": True,
            "result": mock_result,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "agent_id": self.agent_id or "mock",
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Check agent status."""
        # In a real implementation, this would query an agent management system
        # For now, we'll return simulated status information

        agent_id = self.agent_id or self._get_current_agent_id()

        status_info = {
            "agent_id": agent_id,
            "status": self._get_agent_status(agent_id),
            "health": self._get_agent_health(agent_id),
            "uptime_seconds": self._get_uptime(agent_id),
            "last_activity": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }

        # Include metrics if requested
        if self.include_metrics:
            status_info["metrics"] = self._get_agent_metrics(agent_id)

        # Include current tasks if requested
        if self.include_tasks:
            status_info["current_tasks"] = self._get_current_tasks(agent_id)

        return status_info

    def _get_current_agent_id(self) -> str:
        """Get the current agent's ID."""
        # In a real system, this would retrieve the actual agent ID
        return os.getenv("AGENT_ID", "agent_unknown")

    def _get_agent_status(self, agent_id: str) -> str:
        """Get agent status."""
        # Possible statuses: active, idle, busy, error, offline
        # In real implementation, query agent registry
        return "active"

    def _get_agent_health(self, agent_id: str) -> str:
        """Get agent health status."""
        # Possible health states: healthy, degraded, unhealthy, unknown
        # In real implementation, check health metrics
        return "healthy"

    def _get_uptime(self, agent_id: str) -> int:
        """Get agent uptime in seconds."""
        # In real implementation, calculate from agent start time
        return 3600  # 1 hour

    def _get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get agent performance metrics."""
        # In real implementation, query metrics database
        return {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_in_progress": 0,
            "average_response_time_ms": 0.0,
            "cpu_usage_percent": 0.0,
            "memory_usage_mb": 0.0,
            "success_rate": 0.0,
            "last_error": None,
        }

    def _get_current_tasks(self, agent_id: str) -> list:
        """Get current tasks for agent."""
        # In real implementation, query task queue
        return []


if __name__ == "__main__":
    print("Testing AgentStatus...")

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    tool = AgentStatus(agent_id="agent_001", include_metrics=True, include_tasks=True)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True
    print("AgentStatus test passed!")
