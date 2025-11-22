"""
Send emails via Gmail API
"""

from typing import Any, Dict, List, Optional
from pydantic import Field, field_validator
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class EmailSend(BaseTool):
    """
    Send emails via Gmail API.

    Args:
        to: Recipient email address(es) - can be single email or comma-separated list
        subject: Email subject line
        body: Email body content (plain text or HTML)
        cc: Optional CC recipients - comma-separated list
        bcc: Optional BCC recipients - comma-separated list
        is_html: Whether body is HTML format (default: False)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Message ID and status
        - metadata: Additional information

    Example:
        >>> tool = EmailSend(
        ...     to="user@example.com",
        ...     subject="Test Email",
        ...     body="Hello, this is a test email."
        ... )
        >>> result = tool.run()
        >>> print(result["result"]["message_id"])
    """

    # Tool metadata
    tool_name: str = "email_send"
    tool_category: str = "communication"

    # Parameters
    to: str = Field(
        ...,
        description="Recipient email address(es) - single email or comma-separated list",
        min_length=1
    )
    subject: str = Field(
        ...,
        description="Email subject line",
        min_length=1
    )
    body: str = Field(
        ...,
        description="Email body content (plain text or HTML)",
        min_length=1
    )
    cc: Optional[str] = Field(
        None,
        description="CC recipients - comma-separated list"
    )
    bcc: Optional[str] = Field(
        None,
        description="BCC recipients - comma-separated list"
    )
    is_html: bool = Field(
        False,
        description="Whether body is HTML format"
    )

    @field_validator('to')
    @classmethod
    def validate_to(cls, v: str) -> str:
        """Validate recipient email addresses."""
        if not v or not v.strip():
            raise ValueError("to cannot be empty")

        # Check for @ symbol in each email
        emails = [e.strip() for e in v.split(',')]
        for email in emails:
            if '@' not in email:
                raise ValueError(f"Invalid email address: {email}")

        return v

    @field_validator('cc', 'bcc')
    @classmethod
    def validate_optional_emails(cls, v: Optional[str]) -> Optional[str]:
        """Validate optional email fields."""
        if v is None or not v.strip():
            return None

        # Check for @ symbol in each email
        emails = [e.strip() for e in v.split(',')]
        for email in emails:
            if '@' not in email:
                raise ValueError(f"Invalid email address: {email}")

        return v

    def _execute(self) -> Dict[str, Any]:
        """Execute email send."""
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
                    "to": self.to,
                    "subject": self.subject,
                    "has_cc": self.cc is not None,
                    "has_bcc": self.bcc is not None,
                    "is_html": self.is_html
                }
            }
        except HttpError as e:
            raise APIError(
                f"Gmail API error: {e}",
                tool_name=self.tool_name,
                api_name="Gmail API"
            )
        except Exception as e:
            raise APIError(
                f"Failed to send email: {e}",
                tool_name=self.tool_name
            )

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        if not self.to.strip():
            raise ValidationError(
                "to cannot be empty",
                tool_name=self.tool_name,
                field="to"
            )

        if not self.subject.strip():
            raise ValidationError(
                "subject cannot be empty",
                tool_name=self.tool_name,
                field="subject"
            )

        if not self.body.strip():
            raise ValidationError(
                "body cannot be empty",
                tool_name=self.tool_name,
                field="body"
            )

        # Validate email format
        to_emails = [e.strip() for e in self.to.split(',')]
        for email in to_emails:
            if '@' not in email or '.' not in email:
                raise ValidationError(
                    f"Invalid email address: {email}",
                    tool_name=self.tool_name,
                    field="to"
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        import uuid
        mock_id = f"mock-msg-{uuid.uuid4().hex[:12]}"

        return {
            "success": True,
            "result": {
                "message_id": mock_id,
                "status": "sent",
                "to": self.to,
                "subject": self.subject,
                "thread_id": f"mock-thread-{uuid.uuid4().hex[:12]}"
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "to": self.to,
                "subject": self.subject
            }
        }

    def _process(self) -> Dict[str, Any]:
        """Send email via Gmail API."""
        # Get credentials
        credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        if not credentials_path:
            raise AuthenticationError(
                "Missing GOOGLE_SERVICE_ACCOUNT_FILE environment variable",
                tool_name=self.tool_name,
                api_name="Gmail API"
            )

        # Create credentials with Gmail scopes
        scopes = ["https://www.googleapis.com/auth/gmail.send"]
        creds = Credentials.from_service_account_file(
            credentials_path,
            scopes=scopes
        )

        # Build Gmail service
        service = build("gmail", "v1", credentials=creds)

        # Create message
        message = self._create_message()

        # Send message
        sent_message = service.users().messages().send(
            userId="me",
            body=message
        ).execute()

        return {
            "message_id": sent_message.get("id"),
            "status": "sent",
            "thread_id": sent_message.get("threadId"),
            "label_ids": sent_message.get("labelIds", [])
        }

    def _create_message(self) -> Dict[str, str]:
        """Create email message in Gmail API format."""
        # Create MIME message
        if self.is_html:
            message = MIMEMultipart('alternative')
            html_part = MIMEText(self.body, 'html')
            message.attach(html_part)
        else:
            message = MIMEText(self.body, 'plain')

        # Set headers
        message['to'] = self.to
        message['subject'] = self.subject

        if self.cc:
            message['cc'] = self.cc

        if self.bcc:
            message['bcc'] = self.bcc

        # Encode message
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode('utf-8')

        return {'raw': raw_message}


if __name__ == "__main__":
    print("Testing EmailSend...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic email
    tool = EmailSend(
        to="test@example.com",
        subject="Test Email",
        body="This is a test email."
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Message ID: {result.get('result', {}).get('message_id')}")
    assert result.get('success') == True
    assert result.get('result', {}).get('status') == 'sent'

    # Test HTML email with CC
    tool2 = EmailSend(
        to="test@example.com",
        subject="HTML Test",
        body="<html><body><h1>Hello</h1><p>This is <b>HTML</b> email.</p></body></html>",
        cc="cc@example.com",
        is_html=True
    )
    result2 = tool2.run()

    print(f"HTML Email Success: {result2.get('success')}")
    assert result2.get('success') == True

    # Test multiple recipients
    tool3 = EmailSend(
        to="user1@example.com,user2@example.com",
        subject="Multiple Recipients",
        body="Test with multiple recipients"
    )
    result3 = tool3.run()

    print(f"Multiple Recipients Success: {result3.get('success')}")
    assert result3.get('success') == True

    print("EmailSend tests passed!")
