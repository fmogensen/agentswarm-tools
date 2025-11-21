"""
Query call history logs with optional filtering and transcripts
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import datetime

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class QueryCallLogs(BaseTool):
    """
    Query call history logs with optional filtering and transcripts

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = QueryCallLogs(input="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "query_call_logs"
    tool_category: str = "communication"

    # Parameters
    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the query_call_logs tool.

        Returns:
            Dict with results
        """
        self._validate_parameters()

        if self._should_use_mock():
            return self._generate_mock_results()

        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not isinstance(self.input, str):
            raise ValidationError(
                "Input must be a string",
                tool_name=self.tool_name,
                details={"input": self.input},
            )
        if not self.input.strip():
            raise ValidationError(
                "Input cannot be empty",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_logs = [
            {
                "call_id": f"call_{i}",
                "timestamp": f"2025-01-0{i}T10:00:00Z",
                "direction": "outbound" if i % 2 == 0 else "inbound",
                "duration_seconds": 30 + i,
                "transcript": f"Mock transcript for call {i}",
            }
            for i in range(1, 6)
        ]

        return {
            "success": True,
            "result": {"logs": mock_logs, "count": len(mock_logs)},
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        # Simulated call log store (real implementation would query a DB or API)
        simulated_logs = [
            {
                "call_id": "abc123",
                "timestamp": "2025-11-15T14:21:00Z",
                "direction": "inbound",
                "duration_seconds": 120,
                "transcript": "Hello, I need assistance with my account.",
            },
            {
                "call_id": "xyz789",
                "timestamp": "2025-11-16T09:10:00Z",
                "direction": "outbound",
                "duration_seconds": 45,
                "transcript": "Following up on your recent inquiry.",
            },
            {
                "call_id": "qwe456",
                "timestamp": "2025-11-17T18:32:00Z",
                "direction": "inbound",
                "duration_seconds": 210,
                "transcript": "Can you help me reset my password?",
            },
        ]

        query = self.input.lower()

        filtered = [
            log
            for log in simulated_logs
            if query in log["call_id"].lower()
            or query in log["direction"].lower()
            or query in log["transcript"].lower()
        ]

        return {"logs": filtered, "count": len(filtered)}
