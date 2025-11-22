"""Tests for SlackSendMessage tool."""

import pytest
import os
from slack_send_message import SlackSendMessage
from shared.errors import ValidationError


class TestSlackSendMessage:
    """Test cases for SlackSendMessage tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_basic_message(self):
        """Test sending basic message."""
        tool = SlackSendMessage(
            channel="#general",
            text="Hello Slack!"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["ok"] == True
        assert "ts" in result["result"]

    def test_thread_reply(self):
        """Test replying in thread."""
        tool = SlackSendMessage(
            channel="#general",
            text="Thread reply",
            thread_ts="1234567890.123456"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["is_thread_reply"] == True

    def test_custom_username(self):
        """Test custom username."""
        tool = SlackSendMessage(
            channel="#general",
            text="Message",
            username="CustomBot"
        )
        result = tool.run()

        assert result["success"] == True

    def test_custom_emoji(self):
        """Test custom emoji icon."""
        tool = SlackSendMessage(
            channel="#general",
            text="Message",
            icon_emoji=":robot_face:"
        )
        result = tool.run()

        assert result["success"] == True

    def test_channel_id_format(self):
        """Test channel ID format."""
        tool = SlackSendMessage(
            channel="C1234567890",
            text="Message by channel ID"
        )
        result = tool.run()

        assert result["success"] == True

    def test_dm_channel(self):
        """Test direct message channel."""
        tool = SlackSendMessage(
            channel="D1234567890",
            text="Direct message"
        )
        result = tool.run()

        assert result["success"] == True

    def test_validation_empty_channel(self):
        """Test validation for empty channel."""
        with pytest.raises(ValidationError):
            tool = SlackSendMessage(
                channel="",
                text="Message"
            )
            tool.run()

    def test_validation_empty_text(self):
        """Test validation for empty text."""
        with pytest.raises(ValidationError):
            tool = SlackSendMessage(
                channel="#general",
                text=""
            )
            tool.run()

    def test_validation_invalid_channel_format(self):
        """Test validation for invalid channel format."""
        with pytest.raises(ValidationError):
            tool = SlackSendMessage(
                channel="invalid-channel",
                text="Message"
            )
            tool.run()

    def test_mock_mode(self):
        """Test mock mode returns expected structure."""
        tool = SlackSendMessage(
            channel="#general",
            text="Test"
        )
        result = tool.run()

        assert result["metadata"]["mock_mode"] == True
        assert "ts" in result["result"]
        assert result["result"]["ok"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
