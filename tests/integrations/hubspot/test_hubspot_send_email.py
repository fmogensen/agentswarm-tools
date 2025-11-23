"""
Tests for HubSpot Send Email Tool

Comprehensive test suite covering email sending, templates, personalization,
scheduling, tracking, and batch operations.
"""

import os
import pytest
from unittest.mock import Mock, patch
from tools.integrations.hubspot.hubspot_send_email import HubSpotSendEmail
from shared.errors import ValidationError, APIError


class TestHubSpotSendEmail:
    """Test suite for HubSpotSendEmail tool."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"
        yield
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_send_templated_email(self):
        """Test sending email with template."""
        tool = HubSpotSendEmail(
            template_id="12345678",
            contact_ids=["98765"],
            from_email="marketing@company.com",
            from_name="Marketing Team",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "sent"
        assert "email_id" in result
        assert result["recipients_count"] >= 1

    def test_send_custom_email(self):
        """Test sending custom email without template."""
        tool = HubSpotSendEmail(
            subject="Special Offer - 20% Off!",
            body="<h1>Special Offer</h1><p>Get 20% off using code: SAVE20</p>",
            list_ids=["111"],
            from_email="sales@company.com",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["subject"] == "Special Offer - 20% Off!"
        assert result["recipients_count"] >= 50  # Assumes 50 per list

    def test_send_to_single_recipient(self):
        """Test sending email to single recipient."""
        tool = HubSpotSendEmail(
            subject="Welcome!",
            body="<p>Welcome to our platform</p>",
            recipient_email="john@example.com",
            from_email="welcome@company.com",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["recipients_count"] == 1

    def test_email_with_personalization(self):
        """Test email with personalization tokens."""
        tool = HubSpotSendEmail(
            template_id="87654321",
            contact_ids=["123"],
            from_email="marketing@company.com",
            personalization_tokens={
                "first_name": "John",
                "company": "Acme Corp",
                "discount_code": "SAVE20",
            },
        )
        result = tool.run()

        assert result["success"] == True

    def test_email_tracking_options(self):
        """Test email tracking configuration."""
        tool = HubSpotSendEmail(
            subject="Tracked Email",
            body="<p>This email is tracked</p>",
            contact_ids=["123"],
            from_email="test@company.com",
            track_opens=True,
            track_clicks=True,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["tracking"]["opens"] == True
        assert result["tracking"]["clicks"] == True

    def test_scheduled_email(self):
        """Test scheduling email for future send."""
        tool = HubSpotSendEmail(
            template_id="11111",
            list_ids=["222"],
            from_email="newsletter@company.com",
            send_immediately=False,
            scheduled_time="2024-12-25T10:00:00Z",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "scheduled"
        assert result["scheduled_time"] == "2024-12-25T10:00:00Z"

    def test_email_with_campaign(self):
        """Test associating email with campaign."""
        tool = HubSpotSendEmail(
            subject="Campaign Email",
            body="<p>Campaign content</p>",
            list_ids=["333"],
            from_email="campaign@company.com",
            campaign_id="campaign_123",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["campaign_id"] == "campaign_123"

    def test_batch_email_sending(self):
        """Test sending multiple emails in batch."""
        batch_emails = [
            {
                "template_id": "111",
                "contact_ids": ["123", "456"],
                "from_email": "email1@company.com",
            },
            {
                "subject": "Newsletter",
                "body": "<p>Newsletter content</p>",
                "list_ids": ["789"],
                "from_email": "newsletter@company.com",
            },
            {
                "template_id": "222",
                "recipient_email": "vip@customer.com",
                "from_email": "vip@company.com",
            },
        ]

        tool = HubSpotSendEmail(batch_emails=batch_emails)
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "batch_sent"
        assert result["emails_sent"] == 3
        assert len(result["email_ids"]) == 3

    def test_missing_content_error(self):
        """Test that either template or subject+body is required."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSendEmail(
                contact_ids=["123"],
                from_email="test@company.com",
            )
            tool.run()
        assert "template_id or both subject and body" in str(exc_info.value)

    def test_missing_recipients_error(self):
        """Test that recipients are required."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSendEmail(
                subject="Test",
                body="Test body",
                from_email="test@company.com",
            )
            tool.run()
        assert "recipients" in str(exc_info.value).lower()

    def test_missing_from_email_error(self):
        """Test that from_email is required."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSendEmail(
                subject="Test",
                body="Test body",
                contact_ids=["123"],
            )
            tool.run()
        assert "from_email is required" in str(exc_info.value)

    def test_scheduled_time_conflict(self):
        """Test that scheduled_time conflicts with send_immediately."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSendEmail(
                subject="Test",
                body="Test body",
                contact_ids=["123"],
                from_email="test@company.com",
                send_immediately=True,
                scheduled_time="2024-12-25T10:00:00Z",
            )
            tool.run()
        assert "Cannot set scheduled_time when send_immediately is True" in str(exc_info.value)

    def test_invalid_scheduled_time_format(self):
        """Test validation of scheduled time format."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSendEmail(
                subject="Test",
                body="Test body",
                contact_ids=["123"],
                from_email="test@company.com",
                send_immediately=False,
                scheduled_time="invalid-time",
            )
            tool.run()
        assert "ISO 8601 format" in str(exc_info.value)

    def test_batch_size_limit(self):
        """Test batch size cannot exceed 10 emails."""
        large_batch = [
            {
                "subject": f"Email {i}",
                "body": f"Body {i}",
                "recipient_email": f"user{i}@example.com",
                "from_email": "test@company.com",
            }
            for i in range(11)
        ]

        with pytest.raises(Exception) as exc_info:
            tool = HubSpotSendEmail(batch_emails=large_batch)
            tool.run()
        assert "cannot exceed 10" in str(exc_info.value)

    def test_batch_email_validation(self):
        """Test validation of batch emails."""
        # Missing content
        with pytest.raises(Exception) as exc_info:
            batch_emails = [
                {
                    "contact_ids": ["123"],
                    "from_email": "test@company.com",
                }
            ]
            tool = HubSpotSendEmail(batch_emails=batch_emails)
            tool.run()
        assert "must have template_id or subject+body" in str(exc_info.value)

        # Missing recipients
        with pytest.raises(Exception) as exc_info:
            batch_emails = [
                {
                    "subject": "Test",
                    "body": "Body",
                    "from_email": "test@company.com",
                }
            ]
            tool = HubSpotSendEmail(batch_emails=batch_emails)
            tool.run()
        assert "must have recipients" in str(exc_info.value)

    def test_email_with_reply_to(self):
        """Test setting reply-to address."""
        tool = HubSpotSendEmail(
            subject="Test Email",
            body="<p>Test content</p>",
            contact_ids=["123"],
            from_email="noreply@company.com",
            reply_to="support@company.com",
        )
        result = tool.run()

        assert result["success"] == True

    def test_email_with_reminder(self):
        """Test setting reminder time."""
        tool = HubSpotSendEmail(
            subject="Meeting Reminder",
            body="<p>Don't forget our meeting</p>",
            contact_ids=["123"],
            from_email="calendar@company.com",
            reminder_minutes=15,
        )
        result = tool.run()

        assert result["success"] == True

    def test_contact_properties_personalization(self):
        """Test using contact properties for personalization."""
        tool = HubSpotSendEmail(
            template_id="12345",
            contact_ids=["123"],
            from_email="marketing@company.com",
            contact_properties=["firstname", "lastname", "company"],
        )
        result = tool.run()

        assert result["success"] == True

    def test_email_to_multiple_lists(self):
        """Test sending to multiple contact lists."""
        tool = HubSpotSendEmail(
            subject="Multi-list Email",
            body="<p>Sent to multiple lists</p>",
            list_ids=["111", "222", "333"],
            from_email="marketing@company.com",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["recipients_count"] >= 150  # 3 lists * 50

    def test_tool_metadata(self):
        """Test tool metadata."""
        tool = HubSpotSendEmail(
            subject="Test",
            body="Test",
            contact_ids=["123"],
            from_email="test@company.com",
        )

        assert tool.tool_name == "hubspot_send_email"
        assert tool.tool_category == "integrations"
        assert tool.rate_limit_cost == 2  # Higher cost for email

    def test_tracking_disabled(self):
        """Test disabling email tracking."""
        tool = HubSpotSendEmail(
            subject="Untracked Email",
            body="<p>Not tracked</p>",
            contact_ids=["123"],
            from_email="test@company.com",
            track_opens=False,
            track_clicks=False,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["tracking"]["opens"] == False
        assert result["tracking"]["clicks"] == False

    @patch("tools.integrations.hubspot.hubspot_send_email.requests")
    def test_api_call_structure(self, mock_requests):
        """Test API call structure (mocked)."""
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ["HUBSPOT_API_KEY"] = "test_key"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "email123",
            "emailId": "email123",
        }
        mock_requests.post.return_value = mock_response

        tool = HubSpotSendEmail(
            subject="Test",
            body="Test body",
            contact_ids=["123"],
            from_email="test@company.com",
        )
        result = tool.run()

        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        assert "https://api.hubapi.com/marketing/v3/emails/send" in call_args[0][0]

        os.environ.pop("HUBSPOT_API_KEY")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
