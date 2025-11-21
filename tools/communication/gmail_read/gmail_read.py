"""
Read specific email from Gmail by ID and process content
"""

from typing import Any, Dict, Optional
from pydantic import Field
import os
import base64

from shared.base import BaseTool
from shared.errors import ValidationError, APIError

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailRead(BaseTool):
    """
    Read specific email from Gmail by ID and process content.

    Args:
        input: The Gmail message ID to retrieve.

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Email content and metadata
        - metadata: Additional information

    Example:
        >>> tool = GmailRead(input="17ab3e1c9b2a...")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "gmail_read"
    tool_category: str = "communication"

    # Parameters
    input: str = Field(..., description="Gmail message ID to fetch")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the gmail_read tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid inputs
            APIError: For API failures
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
                    "message_id": self.input,
                },
            }

        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If the input is empty or invalid.
        """
        if not self.input or not self.input.strip():
            raise ValidationError(
                "input (message ID) cannot be empty",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "mock": True,
                "message_id": self.input,
                "subject": "Mock Subject",
                "snippet": "This is a mocked email snippet.",
                "body": "This is a mocked email body.",
            },
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Retrieves an email by ID from Gmail using a service account.

        Returns:
            Dict with subject, snippet, body, and full payload.

        Raises:
            APIError: If Gmail API communication fails.
        """
        try:
            service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            if not service_account_json:
                raise APIError(
                    "Missing GOOGLE_SERVICE_ACCOUNT_JSON environment variable",
                    tool_name=self.tool_name,
                )

            creds = service_account.Credentials.from_service_account_file(
                service_account_json,
                scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            )

            service = build("gmail", "v1", credentials=creds)

            msg = (
                service.users()
                .messages()
                .get(userId="me", id=self.input, format="full")
                .execute()
            )

            snippet = msg.get("snippet", "")

            # Extract body if available
            body_text = ""
            payload = msg.get("payload", {})

            if "parts" in payload:
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain":
                        data = part.get("body", {}).get("data")
                        if data:
                            body_text = base64.urlsafe_b64decode(data).decode("utf-8")
                            break
            else:
                # Single-part email
                data = payload.get("body", {}).get("data")
                if data:
                    body_text = base64.urlsafe_b64decode(data).decode("utf-8")

            # Extract subject
            headers = payload.get("headers", [])
            subject = ""
            for header in headers:
                if header.get("name", "").lower() == "subject":
                    subject = header.get("value", "")
                    break

            return {
                "message_id": self.input,
                "subject": subject,
                "snippet": snippet,
                "body": body_text,
                "raw_payload": msg,
            }

        except HttpError as e:
            raise APIError(f"Gmail API error: {e}", tool_name=self.tool_name)
        except Exception as e:
            raise APIError(f"Unexpected error: {e}", tool_name=self.tool_name)
