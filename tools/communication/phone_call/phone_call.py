"""
Create AI-assisted phone call card (user clicks to initiate)
"""

from typing import Any, Dict
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class PhoneCall(BaseTool):
    """
    Create AI-assisted phone call card (user clicks to initiate)

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = PhoneCall(input="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "phone_call"
    tool_category: str = "communication"

    # Parameters
    input: str = Field(
        ..., description="Primary input parameter", min_length=1, max_length=2000
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the phone_call tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: If parameters are invalid
            APIError: If processing fails unexpectedly
        """
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
                    "mock_mode": False,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input is empty or invalid
        """
        if not self.input or not self.input.strip():
            raise ValidationError(
                "Input cannot be empty.",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        if len(self.input) > 2000:
            raise ValidationError(
                "Input exceeds maximum length of 2000 characters.",
                tool_name=self.tool_name,
                details={"length": len(self.input)},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """
        Generate mock results for testing.

        Returns:
            Dict with mock response data
        """
        return {
            "success": True,
            "result": {
                "call_card": {
                    "type": "mock_phone_call",
                    "text": self.input,
                    "call_id": "mock-call-1234",
                    "click_to_call": True,
                }
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "tool_version": "1.0.0",
            },
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        This tool generates a data structure representing a call card
        that the frontend can use to trigger an actual phone call.

        Returns:
            Dict containing call card metadata

        Raises:
            APIError: If card creation fails unexpectedly
        """
        try:
            call_card = {
                "call_card": {
                    "type": "ai_phone_call",
                    "text": self.input,
                    "call_id": f"call-{self._generate_call_id()}",
                    "click_to_call": True,
                }
            }
            return call_card
        except Exception as e:
            raise APIError(
                f"Failed to create phone call card: {e}", tool_name=self.tool_name
            )

    def _generate_call_id(self) -> str:
        """
        Generate a deterministic but unique ID for the call card.

        Returns:
            String call ID
        """
        # Simple deterministic ID generation based on hash
        return str(abs(hash(self.input)))[:12]
