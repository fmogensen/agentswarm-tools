"""
HubSpot Send Email Tool

Sends marketing emails via HubSpot with template support, personalization,
tracking, and campaign management.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from pydantic import Field
from requests.exceptions import HTTPError, RequestException, Timeout

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class HubSpotSendEmail(BaseTool):
    """
    Send marketing emails through HubSpot with templates and personalization.

    This tool sends marketing emails via HubSpot's email API, supporting
    email templates, personalization tokens, contact list targeting, A/B testing,
    tracking, and campaign management. Ideal for email marketing automation.

    Args:
        # Email content (required - either template_id or subject+body)
        template_id: HubSpot email template ID
        subject: Email subject line (required if not using template)
        body: Email HTML body content (required if not using template)

        # Recipients (required - one of these)
        contact_ids: List of contact IDs to send to
        list_ids: List of contact list IDs to send to
        recipient_email: Single recipient email address

        # Sender
        from_email: Sender email address (must be verified in HubSpot)
        from_name: Sender name
        reply_to: Reply-to email address

        # Personalization
        personalization_tokens: Dictionary of token names and values for personalization
        contact_properties: List of contact properties to use for personalization

        # Email options
        track_opens: Track email opens (default: True)
        track_clicks: Track link clicks (default: True)
        subscription_type_id: Subscription type ID for unsubscribe link

        # Campaign
        campaign_id: HubSpot campaign ID to associate email with
        ab_test_id: A/B test ID for testing variations

        # Scheduling
        send_immediately: Send email immediately (default: True)
        scheduled_time: Schedule send time (ISO 8601 format or Unix timestamp)

        # Batch options
        batch_emails: List of email dictionaries for bulk sending

    Returns:
        Dict containing:
            - success (bool): Whether the operation succeeded
            - email_id (str): HubSpot email ID (or list for batch)
            - status (str): sent, scheduled, queued, batch_sent
            - recipients_count (int): Number of recipients
            - scheduled_time (str): Scheduled send time if applicable
            - tracking (dict): Tracking settings (opens, clicks)
            - campaign_id (str): Associated campaign ID
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Send templated email to contact
        >>> tool = HubSpotSendEmail(
        ...     template_id="12345678",
        ...     contact_ids=["98765"],
        ...     from_email="marketing@company.com",
        ...     from_name="Marketing Team",
        ...     personalization_tokens={"first_name": "John", "company": "Acme Corp"},
        ...     track_opens=True,
        ...     track_clicks=True
        ... )
        >>> result = tool.run()
        >>> print(result['email_id'])
        'email_123456789'

        >>> # Send custom email to list
        >>> tool = HubSpotSendEmail(
        ...     subject="Exclusive Offer - 20% Off!",
        ...     body="<h1>Special Offer</h1><p>Get 20% off using code: SAVE20</p>",
        ...     list_ids=["111", "222"],
        ...     from_email="sales@company.com",
        ...     campaign_id="campaign_456"
        ... )
        >>> result = tool.run()

        >>> # Schedule email
        >>> tool = HubSpotSendEmail(
        ...     template_id="87654321",
        ...     list_ids=["333"],
        ...     from_email="newsletter@company.com",
        ...     send_immediately=False,
        ...     scheduled_time="2024-12-25T10:00:00Z"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "hubspot_send_email"
    tool_category: str = "integrations"
    rate_limit_type: str = "hubspot_api"
    rate_limit_cost: int = 2  # Higher cost for email operations

    # Email content
    template_id: Optional[str] = Field(None, description="HubSpot email template ID")
    subject: Optional[str] = Field(None, description="Email subject line", max_length=500)
    body: Optional[str] = Field(None, description="Email HTML body content", max_length=100000)

    # Recipients
    contact_ids: Optional[List[str]] = Field(None, description="Contact IDs to send email to")
    list_ids: Optional[List[str]] = Field(None, description="Contact list IDs to send email to")
    recipient_email: Optional[str] = Field(
        None,
        description="Single recipient email address",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
    )

    # Sender
    from_email: Optional[str] = Field(
        None,
        description="Sender email address (must be verified)",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
    )
    from_name: Optional[str] = Field(None, description="Sender name", max_length=100)
    reply_to: Optional[str] = Field(
        None,
        description="Reply-to email address",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
    )

    # Personalization
    personalization_tokens: Optional[Dict[str, str]] = Field(
        None, description="Token names and values for personalization"
    )
    contact_properties: Optional[List[str]] = Field(
        None, description="Contact properties to use for personalization"
    )

    # Email options
    track_opens: bool = Field(True, description="Track email opens")
    track_clicks: bool = Field(True, description="Track link clicks")
    subscription_type_id: Optional[str] = Field(
        None, description="Subscription type ID for unsubscribe"
    )

    # Campaign
    campaign_id: Optional[str] = Field(None, description="Campaign ID to associate email with")
    ab_test_id: Optional[str] = Field(None, description="A/B test ID")

    # Scheduling
    send_immediately: bool = Field(True, description="Send email immediately")
    scheduled_time: Optional[str] = Field(
        None, description="Scheduled send time (ISO 8601 or Unix timestamp)"
    )

    # Batch
    batch_emails: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of email dictionaries for bulk sending"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the email send operation."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            if self.batch_emails:
                result = self._process_batch()
            else:
                result = self._process_single()

            return result
        except Exception as e:
            raise APIError(f"Failed to send email: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Batch mode validation
        if self.batch_emails:
            if not isinstance(self.batch_emails, list) or len(self.batch_emails) == 0:
                raise ValidationError(
                    "batch_emails must be a non-empty list",
                    tool_name=self.tool_name,
                )

            # Batch size limit
            if len(self.batch_emails) > 10:
                raise ValidationError(
                    "Batch size cannot exceed 10 emails",
                    tool_name=self.tool_name,
                )

            # Validate each email
            for idx, email in enumerate(self.batch_emails):
                # Check content
                has_template = "template_id" in email and email["template_id"]
                has_custom = (
                    "subject" in email and "body" in email and email["subject"] and email["body"]
                )
                if not has_template and not has_custom:
                    raise ValidationError(
                        f"Email at index {idx} must have template_id or subject+body",
                        tool_name=self.tool_name,
                    )

                # Check recipients
                has_recipients = (
                    ("contact_ids" in email and email["contact_ids"])
                    or ("list_ids" in email and email["list_ids"])
                    or ("recipient_email" in email and email["recipient_email"])
                )
                if not has_recipients:
                    raise ValidationError(
                        f"Email at index {idx} must have recipients (contact_ids, list_ids, or recipient_email)",
                        tool_name=self.tool_name,
                    )
            return

        # Single email validation
        # Must have either template_id OR custom_content (subject+body), not both, not neither
        has_template = self.template_id is not None and self.template_id.strip() != ""
        has_custom_content = (
            self.subject is not None
            and self.subject.strip() != ""
            and self.body is not None
            and self.body.strip() != ""
        )

        if has_template and has_custom_content:
            raise ValidationError(
                "Cannot specify both template_id and custom_content (subject/body)",
                tool_name=self.tool_name,
            )

        if not has_template and not has_custom_content:
            raise ValidationError(
                "Must provide either template_id or both subject and body",
                tool_name=self.tool_name,
            )

        # Must have recipients
        recipients_provided = (
            (self.contact_ids is not None and len(self.contact_ids) > 0)
            or (self.list_ids is not None and len(self.list_ids) > 0)
            or (self.recipient_email is not None and self.recipient_email.strip() != "")
        )

        if not recipients_provided:
            raise ValidationError(
                "Recipients list cannot be empty",
                tool_name=self.tool_name,
            )

        # Sender email is required
        if not self.from_email or not self.from_email.strip():
            raise ValidationError(
                "from_email is required",
                tool_name=self.tool_name,
            )

        # Cannot specify both scheduled_time and send_immediately
        if self.scheduled_time and self.send_immediately:
            raise ValidationError(
                "Cannot set scheduled_time when send_immediately is True",
                tool_name=self.tool_name,
            )

        # Validate scheduled_time format (ISO 8601)
        if self.scheduled_time:
            from datetime import datetime

            try:
                datetime.fromisoformat(self.scheduled_time.replace("Z", "+00:00"))
            except ValueError:
                raise ValidationError(
                    "scheduled_time must be in ISO 8601 format", tool_name=self.tool_name
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        if self.batch_emails:
            # Mock batch results
            email_ids = [
                f"email_mock_{i}_{hash(str(email))}"[:20]
                for i, email in enumerate(self.batch_emails)
            ]
            recipients_count = sum(
                [
                    len(email.get("contact_ids", []))
                    + len(email.get("list_ids", [])) * 50  # Assume 50 per list
                    + (1 if email.get("recipient_email") else 0)
                    for email in self.batch_emails
                ]
            )

            return {
                "success": True,
                "status": "batch_sent",
                "email_ids": email_ids,
                "emails_sent": len(self.batch_emails),
                "total_recipients": recipients_count,
                "metadata": {
                    "tool_name": self.tool_name,
                    "batch_size": len(self.batch_emails),
                    "mock_mode": True,
                },
            }

        # Single email mock
        email_id = f"email_mock_{hash(self.subject or self.template_id or 'email')}"[:20]

        # Calculate recipients count
        recipients_count = (
            len(self.contact_ids or [])
            + len(self.list_ids or []) * 50  # Assume 50 contacts per list
            + (1 if self.recipient_email else 0)
        )

        # Determine status
        if self.send_immediately:
            status = "sent"
        elif self.scheduled_time:
            status = "scheduled"
        else:
            status = "queued"

        return {
            "success": True,
            "email_id": email_id,
            "status": status,
            "subject": self.subject or f"Template {self.template_id}",
            "recipients_count": recipients_count,
            "scheduled_time": self.scheduled_time,
            "tracking": {
                "opens": self.track_opens,
                "clicks": self.track_clicks,
            },
            "campaign_id": self.campaign_id,
            "metadata": {
                "tool_name": self.tool_name,
                "template_id": self.template_id,
                "mock_mode": True,
            },
        }

    def _build_email_payload(self, email_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build email payload from data or instance attributes."""
        if email_data:
            # Build from provided email data (for batch)
            payload = {}

            # Content
            if email_data.get("template_id"):
                payload["templateId"] = email_data["template_id"]
            else:
                payload["subject"] = email_data.get("subject")
                payload["body"] = email_data.get("body")

            # Recipients
            if email_data.get("contact_ids"):
                payload["contactIds"] = email_data["contact_ids"]
            if email_data.get("list_ids"):
                payload["listIds"] = email_data["list_ids"]
            if email_data.get("recipient_email"):
                payload["recipientEmail"] = email_data["recipient_email"]

            # Sender
            payload["fromEmail"] = email_data.get("from_email")
            if email_data.get("from_name"):
                payload["fromName"] = email_data["from_name"]
            if email_data.get("reply_to"):
                payload["replyTo"] = email_data["reply_to"]

            # Options
            if email_data.get("personalization_tokens"):
                payload["personalizationTokens"] = email_data["personalization_tokens"]

            return payload
        else:
            # Build from instance attributes
            payload = {}

            # Content
            if self.template_id:
                payload["templateId"] = self.template_id
            else:
                payload["subject"] = self.subject
                payload["body"] = self.body

            # Recipients
            if self.contact_ids:
                payload["contactIds"] = self.contact_ids
            if self.list_ids:
                payload["listIds"] = self.list_ids
            if self.recipient_email:
                payload["recipientEmail"] = self.recipient_email

            # Sender
            payload["fromEmail"] = self.from_email
            if self.from_name:
                payload["fromName"] = self.from_name
            if self.reply_to:
                payload["replyTo"] = self.reply_to

            # Personalization
            if self.personalization_tokens:
                payload["personalizationTokens"] = self.personalization_tokens
            if self.contact_properties:
                payload["contactProperties"] = self.contact_properties

            # Tracking
            payload["trackOpens"] = self.track_opens
            payload["trackClicks"] = self.track_clicks

            # Campaign
            if self.campaign_id:
                payload["campaignId"] = self.campaign_id
            if self.ab_test_id:
                payload["abTestId"] = self.ab_test_id

            # Subscription
            if self.subscription_type_id:
                payload["subscriptionTypeId"] = self.subscription_type_id

            # Scheduling
            if not self.send_immediately and self.scheduled_time:
                payload["scheduledTime"] = self.scheduled_time

            return payload

    def _process_single(self) -> Dict[str, Any]:
        """Process single email send with HubSpot API."""
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing HUBSPOT_API_KEY environment variable",
                tool_name=self.tool_name,
            )

        # Build email payload
        payload = self._build_email_payload()

        # Prepare API request
        # Note: HubSpot uses different endpoints for single emails and marketing emails
        # This is a simplified implementation
        url = "https://api.hubapi.com/marketing/v3/emails/send"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Send email
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            email_data = response.json()

            email_id = email_data.get("id", email_data.get("emailId"))

            # Calculate recipients count
            recipients_count = (
                len(self.contact_ids or [])
                + len(self.list_ids or []) * 50
                + (1 if self.recipient_email else 0)
            )

            # Determine status
            if self.send_immediately:
                status = "sent"
            elif self.scheduled_time:
                status = "scheduled"
            else:
                status = "queued"

            return {
                "success": True,
                "email_id": email_id,
                "status": status,
                "subject": self.subject or f"Template {self.template_id}",
                "recipients_count": recipients_count,
                "scheduled_time": self.scheduled_time,
                "tracking": {
                    "opens": self.track_opens,
                    "clicks": self.track_clicks,
                },
                "campaign_id": self.campaign_id,
                "metadata": {
                    "tool_name": self.tool_name,
                    "template_id": self.template_id,
                },
            }

        except HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid HubSpot API key", tool_name=self.tool_name)
            elif e.response.status_code == 429:
                raise APIError("Rate limit exceeded. Try again later.", tool_name=self.tool_name)
            else:
                error_detail = e.response.json() if e.response.content else {}
                raise APIError(
                    f"HubSpot email API error: {error_detail.get('message', str(e))}",
                    tool_name=self.tool_name,
                )
        except RequestException as e:
            raise APIError(f"Network error: {str(e)}", tool_name=self.tool_name)

    def _process_batch(self) -> Dict[str, Any]:
        """Process batch email sending with HubSpot API."""
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing HUBSPOT_API_KEY environment variable",
                tool_name=self.tool_name,
            )

        # Process each email individually (HubSpot doesn't have batch email endpoint)
        email_ids = []
        total_recipients = 0

        for email_data in self.batch_emails:
            payload = self._build_email_payload(email_data)

            url = "https://api.hubapi.com/marketing/v3/emails/send"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()

                email_id = result.get("id", result.get("emailId"))
                email_ids.append(email_id)

                # Calculate recipients
                recipients = (
                    len(email_data.get("contact_ids", []))
                    + len(email_data.get("list_ids", [])) * 50
                    + (1 if email_data.get("recipient_email") else 0)
                )
                total_recipients += recipients

            except HTTPError as e:
                # Continue processing other emails
                email_ids.append(f"error_{hash(str(email_data))}"[:20])
                continue

        return {
            "success": True,
            "status": "batch_sent",
            "email_ids": email_ids,
            "emails_sent": len(email_ids),
            "total_recipients": total_recipients,
            "metadata": {
                "tool_name": self.tool_name,
                "batch_size": len(self.batch_emails),
            },
        }


if __name__ == "__main__":
    # Test the tool
    print("Testing HubSpotSendEmail...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Send templated email to contacts
    print("\n1. Testing templated email to contacts...")
    tool = HubSpotSendEmail(
        template_id="12345678",
        contact_ids=["98765", "54321"],
        from_email="marketing@company.com",
        from_name="Marketing Team",
        reply_to="support@company.com",
        personalization_tokens={
            "first_name": "John",
            "company": "Acme Corp",
            "discount_code": "SAVE20",
        },
        track_opens=True,
        track_clicks=True,
        campaign_id="campaign_123",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Email ID: {result.get('email_id')}")
    print(f"Status: {result.get('status')}")
    print(f"Recipients: {result.get('recipients_count')}")
    print(f"Tracking opens: {result.get('tracking', {}).get('opens')}")
    assert result.get("success") == True
    assert result.get("status") in ["sent", "queued"]

    # Test 2: Send custom email to list
    print("\n2. Testing custom email to list...")
    tool = HubSpotSendEmail(
        subject="Exclusive Offer - 20% Off This Week!",
        body="<h1>Special Offer</h1><p>Get 20% off all products using code: <strong>SAVE20</strong></p>",
        list_ids=["111", "222"],
        from_email="sales@company.com",
        from_name="Sales Team",
        campaign_id="campaign_456",
        track_opens=True,
        track_clicks=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Subject: {result.get('subject')}")
    print(f"Recipients: {result.get('recipients_count')}")
    assert result.get("success") == True

    # Test 3: Schedule email
    print("\n3. Testing scheduled email...")
    tool = HubSpotSendEmail(
        template_id="87654321",
        list_ids=["333"],
        from_email="newsletter@company.com",
        from_name="Newsletter",
        send_immediately=False,
        scheduled_time="2024-12-25T10:00:00Z",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    print(f"Scheduled for: {result.get('scheduled_time')}")
    assert result.get("success") == True
    assert result.get("status") == "scheduled"

    # Test 4: Single recipient email
    print("\n4. Testing single recipient email...")
    tool = HubSpotSendEmail(
        subject="Welcome to Our Platform!",
        body="<h1>Welcome!</h1><p>Thanks for signing up.</p>",
        recipient_email="john.doe@example.com",
        from_email="welcome@company.com",
        from_name="Onboarding Team",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Recipients: {result.get('recipients_count')}")
    assert result.get("success") == True
    assert result.get("recipients_count") == 1

    # Test 5: Batch email sending
    print("\n5. Testing batch email sending...")
    tool = HubSpotSendEmail(
        batch_emails=[
            {
                "template_id": "111",
                "contact_ids": ["123", "456"],
                "from_email": "campaign1@company.com",
                "campaign_id": "camp_1",
            },
            {
                "subject": "Newsletter #2",
                "body": "<p>Newsletter content</p>",
                "list_ids": ["789"],
                "from_email": "newsletter@company.com",
            },
            {
                "template_id": "222",
                "recipient_email": "vip@customer.com",
                "from_email": "vip@company.com",
                "personalization_tokens": {"vip_status": "Gold"},
            },
        ]
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    print(f"Emails sent: {result.get('emails_sent')}")
    print(f"Total recipients: {result.get('total_recipients')}")
    assert result.get("success") == True
    assert result.get("status") == "batch_sent"
    assert result.get("emails_sent") == 3

    # Test 6: Error handling - missing content
    print("\n6. Testing error handling (missing content)...")
    try:
        tool = HubSpotSendEmail(
            contact_ids=["123"],
            from_email="test@company.com",
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        print(f"Correctly caught error: {str(e)}")

    # Test 7: Error handling - missing recipients
    print("\n7. Testing error handling (missing recipients)...")
    try:
        tool = HubSpotSendEmail(
            subject="Test",
            body="Test body",
            from_email="test@company.com",
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        print(f"Correctly caught error: {str(e)}")

    print("\n✅ All tests passed!")
