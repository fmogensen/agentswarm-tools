"""Tests for SlackReadMessages tool."""

import pytest
import os
from slack_read_messages import SlackReadMessages
from shared.errors import ValidationError


class TestSlackReadMessages:
    """Test cases for SlackReadMessages tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_basic_read(self):
        """Test reading basic messages."""
        tool = SlackReadMessages(channel="#general", limit=5)
        result = tool.run()

        assert result["success"] == True
        assert "messages" in result["result"]
        assert len(result["result"]["messages"]) > 0
        assert result["metadata"]["message_count"] > 0

    def test_read_with_limit(self):
        """Test reading with custom limit."""
        tool = SlackReadMessages(channel="#general", limit=20)
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["message_count"] <= 20

    def test_read_with_threads(self):
        """Test reading with thread replies."""
        tool = SlackReadMessages(channel="#general", limit=10, include_threads=True)
        result = tool.run()

        assert result["success"] == True

    def test_channel_id_format(self):
        """Test channel ID format."""
        tool = SlackReadMessages(channel="C1234567890", limit=5)
        result = tool.run()

        assert result["success"] == True

    def test_time_range(self):
        """Test reading with time range."""
        tool = SlackReadMessages(
            channel="#general", limit=10, oldest="1234567890.123456", latest="1234567999.999999"
        )
        result = tool.run()

        assert result["success"] == True

    def test_validation_empty_channel(self):
        """Test validation for empty channel."""
        with pytest.raises(ValidationError):
            tool = SlackReadMessages(channel="", limit=5)
            tool.run()

    def test_validation_invalid_channel_format(self):
        """Test validation for invalid channel format."""
        with pytest.raises(ValidationError):
            tool = SlackReadMessages(channel="invalid-channel", limit=5)
            tool.run()

    def test_validation_invalid_limit(self):
        """Test validation for invalid limit."""
        with pytest.raises(ValidationError):
            tool = SlackReadMessages(channel="#general", limit=0)

    def test_validation_limit_too_high(self):
        """Test validation for limit exceeding max."""
        with pytest.raises(ValidationError):
            tool = SlackReadMessages(channel="#general", limit=200)

    def test_mock_mode(self):
        """Test mock mode returns expected structure."""
        tool = SlackReadMessages(channel="#general", limit=5)
        result = tool.run()

        assert result["metadata"]["mock_mode"] == True
        assert "messages" in result["result"]
        assert result["result"]["ok"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
