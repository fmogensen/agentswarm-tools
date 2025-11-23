"""
Read messages from Slack channels via Slack API
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    SLACK_SDK_AVAILABLE = True
except ImportError:
    SLACK_SDK_AVAILABLE = False


class SlackReadMessages(BaseTool):
    """
    Read messages from Slack channels via Slack API.

    Args:
        channel: Channel ID or name (e.g., #general, C1234567890)
        limit: Maximum number of messages to retrieve (default: 10, max: 100)
        oldest: Optional timestamp to get messages after (e.g., 1234567890.123456)
        latest: Optional timestamp to get messages before (e.g., 1234567890.123456)
        include_threads: Whether to include thread replies (default: False)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: List of messages with metadata
        - metadata: Additional information

    Example:
        >>> tool = SlackReadMessages(
        ...     channel="#general",
        ...     limit=20
        ... )
        >>> result = tool.run()
        >>> for msg in result["result"]["messages"]:
        ...     print(msg["text"])
    """

    # Tool metadata
    tool_name: str = "slack_read_messages"
    tool_category: str = "communication"

    # Parameters
    channel: str = Field(
        ..., description="Channel ID or name (e.g., #general, C1234567890)", min_length=1
    )
    limit: int = Field(10, description="Maximum number of messages to retrieve", ge=1, le=100)
    oldest: Optional[str] = Field(None, description="Timestamp to get messages after")
    latest: Optional[str] = Field(None, description="Timestamp to get messages before")
    include_threads: bool = Field(False, description="Whether to include thread replies")

    def _execute(self) -> Dict[str, Any]:
        """Execute Slack message read."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        if not SLACK_SDK_AVAILABLE:
            raise APIError(
                "slack_sdk package not installed. Install with: pip install slack-sdk",
                tool_name=self.tool_name,
            )

        try:
            result = self._process()
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "channel": self.channel,
                    "message_count": len(result.get("messages", [])),
                    "has_more": result.get("has_more", False),
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
            raise APIError(f"Failed to read Slack messages: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        if not self.channel.strip():
            raise ValidationError(
                "channel cannot be empty", tool_name=self.tool_name, field="channel"
            )

        # Validate channel format
        channel = self.channel.strip()
        if not (channel.startswith("#") or channel.startswith("C") or channel.startswith("D")):
            raise ValidationError(
                "channel must start with # (name) or C/D (ID)",
                tool_name=self.tool_name,
                field="channel",
            )

        if self.limit < 1 or self.limit > 100:
            raise ValidationError(
                "limit must be between 1 and 100", tool_name=self.tool_name, field="limit"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        import time
        from datetime import datetime, timedelta

        # Generate mock messages
        mock_messages = []
        base_time = time.time()

        for i in range(min(self.limit, 5)):
            msg_time = base_time - (i * 3600)  # 1 hour apart
            mock_messages.append(
                {
                    "type": "message",
                    "user": f"U{i:08d}",
                    "text": f"Mock message {i + 1}: This is a test message from Slack channel {self.channel}",
                    "ts": str(msg_time),
                    "thread_ts": str(msg_time) if i == 0 and self.include_threads else None,
                    "reply_count": 2 if i == 0 and self.include_threads else 0,
                }
            )

        return {
            "success": True,
            "result": {
                "ok": True,
                "messages": mock_messages,
                "has_more": len(mock_messages) == self.limit,
                "channel": self.channel,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "channel": self.channel,
                "message_count": len(mock_messages),
                "has_more": False,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Read messages via Slack API."""
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

        # First, resolve channel name to ID if needed
        channel_id = self.channel
        if self.channel.startswith("#"):
            # Get channel ID from name
            channels_response = client.conversations_list(
                exclude_archived=True, types="public_channel,private_channel"
            )
            for channel in channels_response.get("channels", []):
                if channel["name"] == self.channel[1:]:  # Remove # prefix
                    channel_id = channel["id"]
                    break

        # Prepare arguments
        kwargs = {"channel": channel_id, "limit": self.limit}

        if self.oldest:
            kwargs["oldest"] = self.oldest

        if self.latest:
            kwargs["latest"] = self.latest

        # Get messages
        response = client.conversations_history(**kwargs)

        messages = response.get("messages", [])

        # Get thread replies if requested
        if self.include_threads:
            for msg in messages:
                if msg.get("thread_ts") and msg.get("reply_count", 0) > 0:
                    thread_response = client.conversations_replies(
                        channel=channel_id, ts=msg["thread_ts"]
                    )
                    msg["thread_replies"] = thread_response.get("messages", [])[
                        1:
                    ]  # Exclude parent

        return {
            "ok": response.get("ok"),
            "messages": messages,
            "has_more": response.get("has_more", False),
            "channel": channel_id,
        }


if __name__ == "__main__":
    print("Testing SlackReadMessages...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic read
    tool = SlackReadMessages(channel="#general", limit=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Message count: {result.get('metadata', {}).get('message_count')}")
    assert result.get("success") == True
    assert len(result.get("result", {}).get("messages", [])) > 0

    # Test with threads
    tool2 = SlackReadMessages(channel="#general", limit=10, include_threads=True)
    result2 = tool2.run()

    print(f"With Threads Success: {result2.get('success')}")
    assert result2.get("success") == True

    # Test with channel ID
    tool3 = SlackReadMessages(channel="C1234567890", limit=3)
    result3 = tool3.run()

    print(f"Channel ID Success: {result3.get('success')}")
    assert result3.get("success") == True

    # Test with time range
    tool4 = SlackReadMessages(channel="#general", limit=20, oldest="1234567890.123456")
    result4 = tool4.run()

    print(f"Time Range Success: {result4.get('success')}")
    assert result4.get("success") == True

    print("SlackReadMessages tests passed!")
