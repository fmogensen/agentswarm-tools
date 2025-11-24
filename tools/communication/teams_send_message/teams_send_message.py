"""
Send messages to Microsoft Teams channels via Microsoft Graph API
"""

import os
from typing import Any, Dict, Optional

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class TeamsSendMessage(BaseTool):
    """
    Send messages to Microsoft Teams channels via Microsoft Graph API.

    Args:
        team_id: The ID of the Microsoft Teams team
        channel_id: The ID of the channel within the team
        message: Message content (supports text and HTML)
        subject: Optional message subject/title
        content_type: Content type - 'text' or 'html' (default: 'text')
        importance: Message importance - 'normal', 'high', or 'low' (default: 'normal')

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Message details including ID
        - metadata: Additional information

    Example:
        >>> tool = TeamsSendMessage(
        ...     team_id="abc-team-123",
        ...     channel_id="xyz-channel-456",
        ...     message="Hello from AgentSwarm!",
        ...     subject="Important Update"
        ... )
        >>> result = tool.run()
        >>> print(result["result"]["id"])  # Message ID
    """

    # Tool metadata
    tool_name: str = "teams_send_message"
    tool_category: str = "communication"

    # Parameters
    team_id: str = Field(..., description="The ID of the Microsoft Teams team", min_length=1)
    channel_id: str = Field(..., description="The ID of the channel within the team", min_length=1)
    message: str = Field(..., description="Message content (supports text and HTML)", min_length=1)
    subject: Optional[str] = Field(None, description="Message subject/title")
    content_type: str = Field("text", description="Content type - 'text' or 'html'")
    importance: str = Field("normal", description="Message importance - 'normal', 'high', or 'low'")

    def _execute(self) -> Dict[str, Any]:
        """Execute Teams message send."""

        self._logger.info(
            f"Executing {self.tool_name} with team_id={self.team_id}, channel_id={self.channel_id}, message={self.message}, ..."
        )
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()
            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "team_id": self.team_id,
                    "channel_id": self.channel_id,
                    "has_subject": self.subject is not None,
                },
            }
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Invalid Microsoft Graph API credentials",
                    tool_name=self.tool_name,
                    api_name="Microsoft Graph API",
                )
            elif e.response.status_code == 404:
                raise ValidationError(
                    "Team or channel not found",
                    tool_name=self.tool_name,
                    field="team_id/channel_id",
                )
            raise APIError(
                f"Microsoft Graph API error: {e}",
                tool_name=self.tool_name,
                api_name="Microsoft Graph API",
                status_code=e.response.status_code,
            )
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to send Teams message: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        if not self.team_id.strip():
            raise ValidationError(
                "team_id cannot be empty", tool_name=self.tool_name, field="team_id"
            )

        if not self.channel_id.strip():
            raise ValidationError(
                "channel_id cannot be empty", tool_name=self.tool_name, field="channel_id"
            )

        if not self.message.strip():
            raise ValidationError(
                "message cannot be empty", tool_name=self.tool_name, field="message"
            )

        valid_content_types = ["text", "html"]
        if self.content_type not in valid_content_types:
            raise ValidationError(
                f"content_type must be one of: {', '.join(valid_content_types)}",
                tool_name=self.tool_name,
                field="content_type",
            )

        valid_importance = ["normal", "high", "low"]
        if self.importance not in valid_importance:
            raise ValidationError(
                f"importance must be one of: {', '.join(valid_importance)}",
                tool_name=self.tool_name,
                field="importance",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        import uuid
        from datetime import datetime

        mock_id = str(uuid.uuid4())

        return {
            "success": True,
            "result": {
                "id": mock_id,
                "messageType": "message",
                "createdDateTime": datetime.utcnow().isoformat() + "Z",
                "importance": self.importance,
                "subject": self.subject or None,
                "body": {"contentType": self.content_type, "content": self.message},
                "from": {"application": {"displayName": "AgentSwarm Bot"}},
                "webUrl": f"https://teams.microsoft.com/l/message/{self.channel_id}/{mock_id}",
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "team_id": self.team_id,
                "channel_id": self.channel_id,
                "has_subject": self.subject is not None,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Send message via Microsoft Graph API."""
        # Get access token
        access_token = self._get_access_token()

        # Prepare message body
        body = {"body": {"contentType": self.content_type, "content": self.message}}

        if self.subject:
            body["subject"] = self.subject

        if self.importance != "normal":
            body["importance"] = self.importance

        # Send message
        url = f"https://graph.microsoft.com/v1.0/teams/{self.team_id}/channels/{self.channel_id}/messages"

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()

        result = response.json()

        return {
            "id": result.get("id"),
            "messageType": result.get("messageType"),
            "createdDateTime": result.get("createdDateTime"),
            "importance": result.get("importance"),
            "subject": result.get("subject"),
            "body": result.get("body", {}),
            "webUrl": result.get("webUrl"),
        }

    def _get_access_token(self) -> str:
        """Get Microsoft Graph API access token."""
        client_id = os.getenv("MICROSOFT_CLIENT_ID")
        client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
        tenant_id = os.getenv("MICROSOFT_TENANT_ID")

        if not all([client_id, client_secret, tenant_id]):
            raise AuthenticationError(
                "Missing Microsoft Graph API credentials. Required: "
                "MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT_ID",
                tool_name=self.tool_name,
                api_name="Microsoft Graph API",
            )

        # Get OAuth token
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }

        response = requests.post(token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        return token_data.get("access_token")


if __name__ == "__main__":
    print("Testing TeamsSendMessage...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic message
    tool = TeamsSendMessage(
        team_id="test-team-123", channel_id="test-channel-456", message="Hello from AgentSwarm!"
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Message ID: {result.get('result', {}).get('id')}")
    assert result.get("success") == True
    assert "id" in result.get("result", {})

    # Test message with subject
    tool2 = TeamsSendMessage(
        team_id="test-team-123",
        channel_id="test-channel-456",
        message="Important update",
        subject="Q4 Results",
        importance="high",
    )
    result2 = tool2.run()

    print(f"With Subject Success: {result2.get('success')}")
    assert result2.get("success") == True
    assert result2.get("result", {}).get("subject") == "Q4 Results"
    assert result2.get("result", {}).get("importance") == "high"

    # Test HTML message
    tool3 = TeamsSendMessage(
        team_id="test-team-123",
        channel_id="test-channel-456",
        message="<h1>Hello</h1><p>This is <b>HTML</b> content.</p>",
        content_type="html",
    )
    result3 = tool3.run()

    print(f"HTML Message Success: {result3.get('success')}")
    assert result3.get("success") == True
    assert result3.get("result", {}).get("body", {}).get("contentType") == "html"

    # Test low importance message
    tool4 = TeamsSendMessage(
        team_id="test-team-123",
        channel_id="test-channel-456",
        message="FYI: Minor update",
        importance="low",
    )
    result4 = tool4.run()

    print(f"Low Importance Success: {result4.get('success')}")
    assert result4.get("success") == True

    print("TeamsSendMessage tests passed!")
