"""Tests for TeamsSendMessage tool."""

import pytest
import os
from teams_send_message import TeamsSendMessage
from shared.errors import ValidationError


class TestTeamsSendMessage:
    """Test cases for TeamsSendMessage tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_basic_message(self):
        """Test sending basic message."""
        tool = TeamsSendMessage(
            team_id="test-team-123",
            channel_id="test-channel-456",
            message="Hello Teams!"
        )
        result = tool.run()

        assert result["success"] == True
        assert "id" in result["result"]
        assert result["result"]["body"]["content"] == "Hello Teams!"

    def test_message_with_subject(self):
        """Test message with subject."""
        tool = TeamsSendMessage(
            team_id="test-team-123",
            channel_id="test-channel-456",
            message="Message content",
            subject="Important Update"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["subject"] == "Important Update"
        assert result["metadata"]["has_subject"] == True

    def test_html_message(self):
        """Test HTML message."""
        tool = TeamsSendMessage(
            team_id="test-team-123",
            channel_id="test-channel-456",
            message="<h1>Title</h1><p>Content</p>",
            content_type="html"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["body"]["contentType"] == "html"

    def test_high_importance(self):
        """Test high importance message."""
        tool = TeamsSendMessage(
            team_id="test-team-123",
            channel_id="test-channel-456",
            message="Urgent message",
            importance="high"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["importance"] == "high"

    def test_low_importance(self):
        """Test low importance message."""
        tool = TeamsSendMessage(
            team_id="test-team-123",
            channel_id="test-channel-456",
            message="FYI",
            importance="low"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["importance"] == "low"

    def test_validation_empty_team_id(self):
        """Test validation for empty team ID."""
        with pytest.raises(ValidationError):
            tool = TeamsSendMessage(
                team_id="",
                channel_id="test-channel-456",
                message="Test"
            )
            tool.run()

    def test_validation_empty_channel_id(self):
        """Test validation for empty channel ID."""
        with pytest.raises(ValidationError):
            tool = TeamsSendMessage(
                team_id="test-team-123",
                channel_id="",
                message="Test"
            )
            tool.run()

    def test_validation_empty_message(self):
        """Test validation for empty message."""
        with pytest.raises(ValidationError):
            tool = TeamsSendMessage(
                team_id="test-team-123",
                channel_id="test-channel-456",
                message=""
            )
            tool.run()

    def test_validation_invalid_content_type(self):
        """Test validation for invalid content type."""
        with pytest.raises(ValidationError):
            tool = TeamsSendMessage(
                team_id="test-team-123",
                channel_id="test-channel-456",
                message="Test",
                content_type="invalid"
            )
            tool.run()

    def test_validation_invalid_importance(self):
        """Test validation for invalid importance."""
        with pytest.raises(ValidationError):
            tool = TeamsSendMessage(
                team_id="test-team-123",
                channel_id="test-channel-456",
                message="Test",
                importance="invalid"
            )
            tool.run()

    def test_mock_mode(self):
        """Test mock mode returns expected structure."""
        tool = TeamsSendMessage(
            team_id="test-team-123",
            channel_id="test-channel-456",
            message="Test"
        )
        result = tool.run()

        assert result["metadata"]["mock_mode"] == True
        assert "id" in result["result"]
        assert "webUrl" in result["result"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
