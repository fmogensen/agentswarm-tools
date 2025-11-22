"""Tests for EmailSend tool."""

import pytest
import os
from email_send import EmailSend
from shared.errors import ValidationError


class TestEmailSend:
    """Test cases for EmailSend tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_basic_email(self):
        """Test sending basic email."""
        tool = EmailSend(to="test@example.com", subject="Test Subject", body="Test body content")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["status"] == "sent"
        assert "message_id" in result["result"]
        assert result["metadata"]["to"] == "test@example.com"
        assert result["metadata"]["subject"] == "Test Subject"

    def test_html_email(self):
        """Test sending HTML email."""
        tool = EmailSend(
            to="test@example.com",
            subject="HTML Email",
            body="<html><body><h1>Hello</h1></body></html>",
            is_html=True,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["is_html"] == True

    def test_email_with_cc_bcc(self):
        """Test email with CC and BCC."""
        tool = EmailSend(
            to="test@example.com",
            subject="Test",
            body="Test",
            cc="cc@example.com",
            bcc="bcc@example.com",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["has_cc"] == True
        assert result["metadata"]["has_bcc"] == True

    def test_multiple_recipients(self):
        """Test multiple TO recipients."""
        tool = EmailSend(
            to="user1@example.com,user2@example.com,user3@example.com",
            subject="Multiple Recipients",
            body="Test body",
        )
        result = tool.run()

        assert result["success"] == True

    def test_validation_empty_to(self):
        """Test validation for empty TO field."""
        with pytest.raises((ValidationError, ValueError)):
            tool = EmailSend(to="", subject="Test", body="Test")

    def test_validation_invalid_email(self):
        """Test validation for invalid email format."""
        with pytest.raises((ValidationError, ValueError)):
            tool = EmailSend(to="not-an-email", subject="Test", body="Test")

    def test_validation_empty_subject(self):
        """Test validation for empty subject."""
        with pytest.raises(ValidationError):
            tool = EmailSend(to="test@example.com", subject="", body="Test")
            tool.run()

    def test_validation_empty_body(self):
        """Test validation for empty body."""
        with pytest.raises(ValidationError):
            tool = EmailSend(to="test@example.com", subject="Test", body="")
            tool.run()

    def test_mock_mode(self):
        """Test mock mode returns expected structure."""
        tool = EmailSend(to="test@example.com", subject="Test", body="Test body")
        result = tool.run()

        assert result["metadata"]["mock_mode"] == True
        assert "message_id" in result["result"]
        assert result["result"]["message_id"].startswith("mock-msg-")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
