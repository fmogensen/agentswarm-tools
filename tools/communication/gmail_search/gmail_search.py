"""
Search and list emails from Gmail based on query
"""

from typing import Any, Dict, List
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailSearch(BaseTool):
    """
    Search and list emails from Gmail based on query

    Args:
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GmailSearch(query="example", max_results=5)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "gmail_search"
    tool_category: str = "communication"

    # Parameters
    query: str = Field(..., description="Search query string", min_length=1)
    max_results: int = Field(10, description="Maximum number of results to return")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the gmail_search tool.

        Returns:
            Dict with results
        """
        # 1. VALIDATE INPUT PARAMETERS
        self._validate_parameters()

        # 2. MOCK MODE SUPPORT
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. REAL EXECUTION
        try:
            emails = self._process()

            return {
                "success": True,
                "result": emails,
                "metadata": {
                    "query": self.query,
                    "max_results": self.max_results,
                    "tool_name": self.tool_name,
                    "mock_mode": False,
                },
            }

        except Exception as e:
            raise APIError(f"Failed to search Gmail: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.query or not self.query.strip():
            raise ValidationError(
                "Query cannot be empty",
                tool_name=self.tool_name,
                field="query",
            )

        if not isinstance(self.max_results, int) or self.max_results <= 0:
            raise ValidationError(
                "max_results must be a positive integer",
                tool_name=self.tool_name,
                field="max_results",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_emails = [
            {
                "id": f"mock-id-{i}",
                "snippet": f"This is a mock email snippet containing query: {self.query}",
                "subject": f"Mock Subject {i}",
                "from": "mock.sender@example.com",
            }
            for i in range(1, min(self.max_results, 10) + 1)
        ]

        return {
            "success": True,
            "result": mock_emails,
            "metadata": {
                "mock_mode": True,
                "query": self.query,
                "max_results": self.max_results,
            },
        }

    def _process(self) -> List[Dict[str, Any]]:
        """Main processing logic for Gmail API search."""
        try:
            credentials_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
            if not credentials_path:
                raise APIError(
                    "Missing environment variable: GOOGLE_SERVICE_ACCOUNT_FILE",
                    tool_name=self.tool_name,
                )

            scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
            creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)

            service = build("gmail", "v1", credentials=creds)

            response = (
                service.users()
                .messages()
                .list(userId="me", q=self.query, maxResults=self.max_results)
                .execute()
            )

            messages = response.get("messages", [])
            results = []

            for msg in messages:
                msg_detail = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg["id"],
                        format="metadata",
                        metadataHeaders=["Subject", "From"],
                    )
                    .execute()
                )

                headers = msg_detail.get("payload", {}).get("headers", [])
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "")
                snippet = msg_detail.get("snippet", "")

                results.append(
                    {
                        "id": msg["id"],
                        "subject": subject,
                        "from": sender,
                        "snippet": snippet,
                    }
                )

            return results

        except HttpError as e:
            raise APIError(f"Gmail API error: {e}", tool_name=self.tool_name)
        except Exception as e:
            raise APIError(f"Unexpected error: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GmailSearch(query="from:example@gmail.com", max_results=5)
    result = tool.run()
    print(f"Success: {result.get('success')}")
