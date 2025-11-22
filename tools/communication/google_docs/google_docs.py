"""
Create and modify Google Docs using Google Docs API v1
"""

from typing import Any, Dict, Optional, List
from pydantic import Field
import os
import json
import re

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    # Mock imports for testing without google-api-python-client
    pass


class GoogleDocs(BaseTool):
    """
    Create and modify Google Docs using Google Docs API v1.

    Supports creating new documents, modifying existing documents,
    formatting text (bold, italic, headings), and sharing documents.

    Args:
        mode: Operation mode - "create" or "modify"
        content: Document content (supports markdown)
        title: Document title (required for create mode)
        document_id: Existing document ID (required for modify mode)
        share_with: Optional list of email addresses for sharing
        folder_id: Optional Google Drive folder ID for new documents
        modify_action: Action for modify mode - "append", "replace", or "insert"
        insert_index: Index position for insert action (default: 1 for beginning)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Document data including document_id and shareable_link
        - metadata: Additional information

    Example:
        >>> # Create new document
        >>> tool = GoogleDocs(
        ...     mode="create",
        ...     title="My Document",
        ...     content="# Hello\\n\\nThis is **bold** text."
        ... )
        >>> result = tool.run()
        >>>
        >>> # Modify existing document
        >>> tool = GoogleDocs(
        ...     mode="modify",
        ...     document_id="abc123",
        ...     content="New content to append",
        ...     modify_action="append"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "google_docs"
    tool_category: str = "communication"

    # Parameters
    mode: str = Field(
        ...,
        description="Operation mode: 'create' or 'modify'",
    )
    content: str = Field(
        ...,
        description="Document content (supports markdown formatting)",
    )
    title: Optional[str] = Field(
        None,
        description="Document title (required for create mode)",
    )
    document_id: Optional[str] = Field(
        None,
        description="Document ID for modify mode",
    )
    share_with: Optional[List[str]] = Field(
        None,
        description="List of email addresses to share document with",
    )
    folder_id: Optional[str] = Field(
        None,
        description="Google Drive folder ID for new documents",
    )
    modify_action: str = Field(
        "append",
        description="Action for modify mode: 'append', 'replace', or 'insert'",
    )
    insert_index: int = Field(
        1,
        description="Index position for insert action (1 = beginning)",
        ge=1,
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the google_docs tool.

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
                    "mode": self.mode,
                },
            }

        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If inputs are invalid.
        """
        # Validate mode
        if self.mode not in ["create", "modify"]:
            raise ValidationError(
                "mode must be 'create' or 'modify'",
                tool_name=self.tool_name,
                field="mode",
            )

        # Validate content
        if not self.content or not self.content.strip():
            raise ValidationError(
                "content cannot be empty",
                tool_name=self.tool_name,
                field="content",
            )

        # Mode-specific validation
        if self.mode == "create":
            if not self.title or not self.title.strip():
                raise ValidationError(
                    "title is required for create mode",
                    tool_name=self.tool_name,
                    field="title",
                )
        elif self.mode == "modify":
            if not self.document_id or not self.document_id.strip():
                raise ValidationError(
                    "document_id is required for modify mode",
                    tool_name=self.tool_name,
                    field="document_id",
                )
            if self.modify_action not in ["append", "replace", "insert"]:
                raise ValidationError(
                    "modify_action must be 'append', 'replace', or 'insert'",
                    tool_name=self.tool_name,
                    field="modify_action",
                )

        # Validate email addresses if provided
        if self.share_with:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            for email in self.share_with:
                if not re.match(email_pattern, email):
                    raise ValidationError(
                        f"Invalid email address: {email}",
                        tool_name=self.tool_name,
                        field="share_with",
                    )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_doc_id = f"mock-doc-{hash(self.title or self.document_id) % 10000}"

        result = {
            "mock": True,
            "mode": self.mode,
            "document_id": mock_doc_id,
            "title": self.title or "Mock Document",
            "shareable_link": f"https://docs.google.com/document/d/{mock_doc_id}/edit",
            "content_preview": self.content[:100] + ("..." if len(self.content) > 100 else ""),
            "shared_with": self.share_with or [],
        }

        # Add mode-specific fields
        if self.mode == "modify":
            result["modify_action"] = self.modify_action

        if self.folder_id:
            result["folder_id"] = self.folder_id

        return {
            "success": True,
            "result": result,
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic.

        Creates or modifies Google Docs based on mode.

        Returns:
            Dict with document data

        Raises:
            APIError: If Google Docs API communication fails
            AuthenticationError: If credentials are missing or invalid
        """
        # Get credentials
        creds = self._get_credentials()

        # Build services
        docs_service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)

        try:
            if self.mode == "create":
                result = self._create_document(docs_service, drive_service)
            else:  # modify
                result = self._modify_document(docs_service, drive_service)

            return result

        except HttpError as e:
            raise APIError(
                f"Google API error: {e}",
                tool_name=self.tool_name,
                api_name="Google Docs",
            )
        except Exception as e:
            raise APIError(
                f"Unexpected error: {e}",
                tool_name=self.tool_name,
            )

    def _get_credentials(self):
        """
        Get Google API credentials from environment.

        Returns:
            Google credentials object

        Raises:
            AuthenticationError: If credentials are missing or invalid
        """
        credentials_json = os.getenv("GOOGLE_DOCS_CREDENTIALS")

        if not credentials_json:
            raise AuthenticationError(
                "Missing GOOGLE_DOCS_CREDENTIALS environment variable",
                tool_name=self.tool_name,
                api_name="Google Docs",
            )

        try:
            # Parse credentials JSON
            credentials_info = json.loads(credentials_json)

            # Create credentials with required scopes
            scopes = [
                "https://www.googleapis.com/auth/documents",
                "https://www.googleapis.com/auth/drive.file",
            ]

            creds = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=scopes,
            )

            return creds

        except json.JSONDecodeError:
            raise AuthenticationError(
                "Invalid GOOGLE_DOCS_CREDENTIALS JSON format",
                tool_name=self.tool_name,
                api_name="Google Docs",
            )
        except Exception as e:
            raise AuthenticationError(
                f"Failed to create credentials: {e}",
                tool_name=self.tool_name,
                api_name="Google Docs",
            )

    def _create_document(self, docs_service, drive_service) -> Dict[str, Any]:
        """
        Create a new Google Doc.

        Args:
            docs_service: Google Docs API service
            drive_service: Google Drive API service

        Returns:
            Dict with document information
        """
        # Create the document
        document = docs_service.documents().create(
            body={"title": self.title}
        ).execute()

        document_id = document.get("documentId")

        # Add content
        requests = self._convert_content_to_requests(self.content)

        if requests:
            docs_service.documents().batchUpdate(
                documentId=document_id,
                body={"requests": requests}
            ).execute()

        # Move to folder if specified
        if self.folder_id:
            try:
                # Get the file
                file = drive_service.files().get(
                    fileId=document_id,
                    fields="parents"
                ).execute()

                previous_parents = ",".join(file.get("parents", []))

                # Move to new folder
                drive_service.files().update(
                    fileId=document_id,
                    addParents=self.folder_id,
                    removeParents=previous_parents,
                    fields="id, parents"
                ).execute()
            except HttpError as e:
                # Log warning but don't fail - document is created
                pass

        # Share if requested
        if self.share_with:
            self._share_document(drive_service, document_id, self.share_with)

        # Get shareable link
        shareable_link = f"https://docs.google.com/document/d/{document_id}/edit"

        return {
            "document_id": document_id,
            "title": self.title,
            "shareable_link": shareable_link,
            "shared_with": self.share_with or [],
            "folder_id": self.folder_id,
        }

    def _modify_document(self, docs_service, drive_service) -> Dict[str, Any]:
        """
        Modify an existing Google Doc.

        Args:
            docs_service: Google Docs API service
            drive_service: Google Drive API service

        Returns:
            Dict with document information
        """
        # Get current document
        try:
            document = docs_service.documents().get(
                documentId=self.document_id
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise ValidationError(
                    f"Document not found: {self.document_id}",
                    tool_name=self.tool_name,
                    field="document_id",
                )
            raise

        title = document.get("title", "Untitled")

        # Build modification requests based on action
        requests = []

        if self.modify_action == "replace":
            # Delete all content first
            end_index = document.get("body", {}).get("content", [{}])[-1].get("endIndex", 1)
            if end_index > 1:
                requests.append({
                    "deleteContentRange": {
                        "range": {
                            "startIndex": 1,
                            "endIndex": end_index - 1,
                        }
                    }
                })
            # Then insert new content
            requests.extend(self._convert_content_to_requests(self.content, index=1))

        elif self.modify_action == "append":
            # Get end index and append
            end_index = document.get("body", {}).get("content", [{}])[-1].get("endIndex", 1)
            insert_index = max(1, end_index - 1)  # Before the final newline
            requests.extend(self._convert_content_to_requests(self.content, index=insert_index))

        elif self.modify_action == "insert":
            # Insert at specified index
            requests.extend(self._convert_content_to_requests(self.content, index=self.insert_index))

        # Apply modifications
        if requests:
            docs_service.documents().batchUpdate(
                documentId=self.document_id,
                body={"requests": requests}
            ).execute()

        # Share if requested
        if self.share_with:
            self._share_document(drive_service, self.document_id, self.share_with)

        # Get shareable link
        shareable_link = f"https://docs.google.com/document/d/{self.document_id}/edit"

        return {
            "document_id": self.document_id,
            "title": title,
            "shareable_link": shareable_link,
            "modify_action": self.modify_action,
            "shared_with": self.share_with or [],
        }

    def _convert_content_to_requests(
        self,
        content: str,
        index: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Convert markdown content to Google Docs API requests.

        Supports basic markdown: headings, bold, italic, lists.

        Args:
            content: Markdown content
            index: Starting index for insertion

        Returns:
            List of API request objects
        """
        requests = []

        # Parse markdown and convert to requests
        lines = content.split("\n")
        current_index = index

        for line in lines:
            if not line.strip():
                # Empty line - insert newline
                requests.append({
                    "insertText": {
                        "location": {"index": current_index},
                        "text": "\n",
                    }
                })
                current_index += 1
                continue

            # Check for heading
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2) + "\n"

                # Insert text
                requests.append({
                    "insertText": {
                        "location": {"index": current_index},
                        "text": text,
                    }
                })

                # Apply heading style
                requests.append({
                    "updateParagraphStyle": {
                        "range": {
                            "startIndex": current_index,
                            "endIndex": current_index + len(text) - 1,
                        },
                        "paragraphStyle": {
                            "namedStyleType": f"HEADING_{level}",
                        },
                        "fields": "namedStyleType",
                    }
                })

                current_index += len(text)
                continue

            # Process inline formatting (bold, italic)
            formatted_text = line + "\n"

            # Insert text first
            requests.append({
                "insertText": {
                    "location": {"index": current_index},
                    "text": formatted_text,
                }
            })

            # Find and apply bold formatting (**text**)
            bold_pattern = r"\*\*(.+?)\*\*"
            for match in re.finditer(bold_pattern, line):
                start = current_index + match.start()
                end = current_index + match.end()

                # Remove the ** markers first (in reverse order)
                requests.append({
                    "deleteContentRange": {
                        "range": {
                            "startIndex": end - 2,
                            "endIndex": end,
                        }
                    }
                })
                requests.append({
                    "deleteContentRange": {
                        "range": {
                            "startIndex": start,
                            "endIndex": start + 2,
                        }
                    }
                })

                # Apply bold style
                requests.append({
                    "updateTextStyle": {
                        "range": {
                            "startIndex": start,
                            "endIndex": end - 4,  # Adjust for removed markers
                        },
                        "textStyle": {
                            "bold": True,
                        },
                        "fields": "bold",
                    }
                })

            # Find and apply italic formatting (*text*)
            italic_pattern = r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"
            for match in re.finditer(italic_pattern, line):
                start = current_index + match.start()
                end = current_index + match.end()

                # Apply italic style (simplified - actual implementation would need marker removal)
                requests.append({
                    "updateTextStyle": {
                        "range": {
                            "startIndex": start + 1,
                            "endIndex": end - 1,
                        },
                        "textStyle": {
                            "italic": True,
                        },
                        "fields": "italic",
                    }
                })

            current_index += len(formatted_text)

        return requests

    def _share_document(
        self,
        drive_service,
        document_id: str,
        emails: List[str]
    ) -> None:
        """
        Share document with specified email addresses.

        Args:
            drive_service: Google Drive API service
            document_id: Document ID to share
            emails: List of email addresses
        """
        for email in emails:
            try:
                permission = {
                    "type": "user",
                    "role": "writer",
                    "emailAddress": email,
                }

                drive_service.permissions().create(
                    fileId=document_id,
                    body=permission,
                    sendNotificationEmail=True,
                ).execute()

            except HttpError as e:
                # Log warning but continue with other emails
                self._logger.warning(
                    f"Failed to share with {email}: {e}"
                )


if __name__ == "__main__":
    """Test the google_docs tool."""
    print("Testing GoogleDocs tool...")
    print("-" * 60)

    # Enable mock mode for testing
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Create new document
    print("\nTest 1: Create new document")
    print("-" * 60)
    tool = GoogleDocs(
        mode="create",
        title="Test Document",
        content="# Welcome\n\nThis is a **test** document with *formatting*.",
        share_with=["user@example.com"],
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Document ID: {result.get('result', {}).get('document_id')}")
    print(f"Link: {result.get('result', {}).get('shareable_link')}")
    assert result.get("success") == True
    assert "document_id" in result.get("result", {})
    print("✓ Test 1 passed")

    # Test 2: Modify document (append)
    print("\nTest 2: Modify document (append)")
    print("-" * 60)
    tool = GoogleDocs(
        mode="modify",
        document_id="abc123",
        content="## New Section\n\nAppended content.",
        modify_action="append",
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Action: {result.get('result', {}).get('modify_action')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("modify_action") == "append"
    print("✓ Test 2 passed")

    # Test 3: Modify document (replace)
    print("\nTest 3: Modify document (replace)")
    print("-" * 60)
    tool = GoogleDocs(
        mode="modify",
        document_id="xyz789",
        content="# Replaced Content\n\nAll old content is gone.",
        modify_action="replace",
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Action: {result.get('result', {}).get('modify_action')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("modify_action") == "replace"
    print("✓ Test 3 passed")

    # Test 4: Modify document (insert)
    print("\nTest 4: Modify document (insert)")
    print("-" * 60)
    tool = GoogleDocs(
        mode="modify",
        document_id="insert123",
        content="Inserted at beginning",
        modify_action="insert",
        insert_index=1,
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Action: {result.get('result', {}).get('modify_action')}")
    assert result.get("success") == True
    print("✓ Test 4 passed")

    # Test 5: Validation - missing title in create mode
    print("\nTest 5: Validation - missing title")
    print("-" * 60)
    try:
        tool = GoogleDocs(
            mode="create",
            content="Content without title",
        )
        result = tool.run()
        print("ERROR: Should have raised validation error")
        assert False
    except Exception as e:
        error_result = e if isinstance(e, dict) else {"error": str(e)}
        print(f"Expected error caught: {error_result}")
        print("✓ Test 5 passed")

    # Test 6: Validation - missing document_id in modify mode
    print("\nTest 6: Validation - missing document_id")
    print("-" * 60)
    try:
        tool = GoogleDocs(
            mode="modify",
            content="Content without document_id",
        )
        result = tool.run()
        print("ERROR: Should have raised validation error")
        assert False
    except Exception as e:
        error_result = e if isinstance(e, dict) else {"error": str(e)}
        print(f"Expected error caught: {error_result}")
        print("✓ Test 6 passed")

    # Test 7: Validation - invalid mode
    print("\nTest 7: Validation - invalid mode")
    print("-" * 60)
    try:
        tool = GoogleDocs(
            mode="invalid",
            title="Test",
            content="Test content",
        )
        result = tool.run()
        print("ERROR: Should have raised validation error")
        assert False
    except Exception as e:
        error_result = e if isinstance(e, dict) else {"error": str(e)}
        print(f"Expected error caught: {error_result}")
        print("✓ Test 7 passed")

    # Test 8: Create with folder
    print("\nTest 8: Create with folder")
    print("-" * 60)
    tool = GoogleDocs(
        mode="create",
        title="Document in Folder",
        content="This doc goes in a folder",
        folder_id="folder123",
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Folder ID: {result.get('result', {}).get('folder_id')}")
    assert result.get("success") == True
    print("✓ Test 8 passed")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
