"""
Send messages to Slack channels via Slack API
"""

import os
from typing import Any, Dict, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    SLACK_SDK_AVAILABLE = True
except ImportError:
    SLACK_SDK_AVAILABLE = False


class SlackSendMessage(BaseTool):
    """
    Send messages to Slack channels via Slack API.

    Args:
        channel: Channel ID or name (e.g., #general, C1234567890)
        text: Message text content
        thread_ts: Optional timestamp of parent message to reply in thread
        blocks: Optional structured blocks (JSON format for rich formatting)
        username: Optional bot username override
        icon_emoji: Optional emoji icon (e.g., :robot_face:)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Message details including timestamp
        - metadata: Additional information

    Example:
        >>> tool = SlackSendMessage(
        ...     channel="#general",
        ...     text="Hello from AgentSwarm!"
        ... )
        >>> result = tool.run()
        >>> print(result["result"]["ts"])  # Message timestamp
    """

    # Tool metadata
    tool_name: str = "slack_send_message"
    tool_category: str = "communication"

    # Parameters
    channel: str = Field(
        ..., description="Channel ID or name (e.g., #general, C1234567890)", min_length=1
    )
    text: str = Field(..., description="Message text content", min_length=1)
    thread_ts: Optional[str] = Field(
        None, description="Timestamp of parent message to reply in thread"
    )
    blocks: Optional[str] = Field(
        None, description="Structured blocks in JSON format for rich formatting"
    )
    username: Optional[str] = Field(None, description="Bot username override")
    icon_emoji: Optional[str] = Field(None, description="Emoji icon (e.g., :robot_face:)")

    def _execute(self) -> Dict[str, Any]:
        """Execute Slack message send."""

        self._logger.info(
            f"Executing {self.tool_name} with channel={self.channel}, text={self.text}, thread_ts={self.thread_ts}, ..."
        )
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        if not SLACK_SDK_AVAILABLE:
            raise APIError(
                "slack_sdk package not installed. Install with: pip install slack-sdk",
                tool_name=self.tool_name,
            )

        try:
            result = self._process()
            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "channel": self.channel,
                    "is_thread_reply": self.thread_ts is not None,
                },
            }
        except SlackApiError as e:
            error_msg = e.response.get("error", str(e))
            if error_msg == "channel_not_found":
                raise ValidationError(
                    f"Channel not found: {self.channel}", tool_name=self.tool_name, field="channel"
                )
            elif error_msg in ["invalid_auth", "not_authed"]:
                raise AuthenticationError(
                    "Invalid Slack API token", tool_name=self.tool_name, api_name="Slack API"
                )
            raise APIError(
                f"Slack API error: {error_msg}", tool_name=self.tool_name, api_name="Slack API"
            )
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to send Slack message: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        if not self.channel.strip():
            raise ValidationError(
                "channel cannot be empty", tool_name=self.tool_name, field="channel"
            )

        if not self.text.strip():
            raise ValidationError("text cannot be empty", tool_name=self.tool_name, field="text")

        # Validate channel format
        channel = self.channel.strip()
        if not (channel.startswith("#") or channel.startswith("C") or channel.startswith("D")):
            raise ValidationError(
                "channel must start with # (name) or C/D (ID)",
                tool_name=self.tool_name,
                field="channel",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        import time
        from datetime import datetime

        mock_ts = str(time.time())

        return {
            "success": True,
            "result": {
                "ok": True,
                "channel": self.channel,
                "ts": mock_ts,
                "message": {
                    "text": self.text,
                    "username": self.username or "AgentSwarm Bot",
                    "bot_id": "B0MOCKBOT123",
                    "type": "message",
                    "subtype": "bot_message",
                    "ts": mock_ts,
                },
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "channel": self.channel,
                "is_thread_reply": self.thread_ts is not None,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Send message via Slack API."""
        # Get Slack bot token
        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            raise AuthenticationError(
                "Missing SLACK_BOT_TOKEN environment variable",
                tool_name=self.tool_name,
                api_name="Slack API",
            )

        # Create Slack client
        client = WebClient(token=token)

        # Prepare message arguments
        kwargs = {"channel": self.channel, "text": self.text}

        if self.thread_ts:
            kwargs["thread_ts"] = self.thread_ts

        if self.blocks:
            import json

            try:
                kwargs["blocks"] = json.loads(self.blocks)
            except json.JSONDecodeError:
                raise ValidationError(
                    "blocks must be valid JSON", tool_name=self.tool_name, field="blocks"
                )

        if self.username:
            kwargs["username"] = self.username

        if self.icon_emoji:
            kwargs["icon_emoji"] = self.icon_emoji

        # Send message
        response = client.chat_postMessage(**kwargs)

        return {
            "ok": response.get("ok"),
            "channel": response.get("channel"),
            "ts": response.get("ts"),
            "message": response.get("message", {}),
        }


if __name__ == "__main__":
    print("Testing SlackSendMessage...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic message
    tool = SlackSendMessage(channel="#general", text="Hello from AgentSwarm!")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Message timestamp: {result.get('result', {}).get('ts')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("ok") == True

    # Test thread reply
    tool2 = SlackSendMessage(
        channel="#general", text="This is a thread reply", thread_ts="1234567890.123456"
    )
    result2 = tool2.run()

    print(f"Thread Reply Success: {result2.get('success')}")
    assert result2.get("success") == True
    assert result2.get("metadata", {}).get("is_thread_reply") == True

    # Test with custom username and emoji
    tool3 = SlackSendMessage(
        channel="#general",
        text="Custom bot message",
        username="CustomBot",
        icon_emoji=":robot_face:",
    )
    result3 = tool3.run()

    print(f"Custom Bot Success: {result3.get('success')}")
    assert result3.get("success") == True

    # Test channel ID format
    tool4 = SlackSendMessage(channel="C1234567890", text="Message to channel by ID")
    result4 = tool4.run()

    print(f"Channel ID Success: {result4.get('success')}")
    assert result4.get("success") == True

    print("SlackSendMessage tests passed!")
