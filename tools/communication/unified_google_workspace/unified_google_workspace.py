"""
Unified Google Workspace Tool - Consolidates Google Docs, Sheets, and Slides operations
"""

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ConfigurationError, ValidationError

try:
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    # Mock imports for testing without google-api-python-client
    pass


class UnifiedGoogleWorkspace(BaseTool):
    """
    Unified Google Workspace operations for Docs, Sheets, and Slides.

    Consolidates three workspace tools into a single interface with workspace-type
    based delegation. Supports creating and modifying documents, spreadsheets, and
    presentations with shared credential management and sharing logic.

    Args:
        workspace_type: Type of workspace - "docs", "sheets", or "slides"
        mode: Operation mode - "create" or "modify"
        title: Title (required for create mode)
        share_with: List of email addresses to share with (optional)

        # Docs parameters
        document_id: Document ID for modify mode (docs)
        content: Document content with markdown support (docs)
        modify_action: Modification action - "append", "replace", or "insert" (docs)
        insert_index: Insert position for insert action (docs)
        folder_id: Google Drive folder ID (docs)

        # Sheets parameters
        spreadsheet_id: Spreadsheet ID for modify mode (sheets)
        data: List of lists representing rows and columns (sheets)
        sheet_name: Worksheet name within spreadsheet (sheets)
        formulas: Dict mapping cell references to formulas (sheets)
        formatting: Dict with formatting options (sheets)

        # Slides parameters
        presentation_id: Presentation ID for modify mode (slides)
        slides: List of slide definitions (slides)
        theme: Theme to apply - "default", "simple", "modern", "colorful" (slides)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Workspace-specific data (document/spreadsheet/presentation info)
        - metadata: Additional information including tool name and workspace type

    Example:
        >>> # Create Google Doc
        >>> tool = UnifiedGoogleWorkspace(
        ...     workspace_type="docs",
        ...     mode="create",
        ...     title="My Document",
        ...     content="# Hello World\\n\\nThis is **bold** text."
        ... )
        >>> result = tool.run()

        >>> # Create Google Sheet
        >>> tool = UnifiedGoogleWorkspace(
        ...     workspace_type="sheets",
        ...     mode="create",
        ...     title="Sales Report",
        ...     data=[["Product", "Sales"], ["Widget A", 1000]],
        ...     sheet_name="Q4 Data"
        ... )
        >>> result = tool.run()

        >>> # Create Google Slides
        >>> tool = UnifiedGoogleWorkspace(
        ...     workspace_type="slides",
        ...     mode="create",
        ...     title="Presentation",
        ...     slides=[{"layout": "title", "title": "Welcome"}]
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "unified_google_workspace"
    tool_category: str = "communication"

    # Core parameters
    workspace_type: Literal["docs", "sheets", "slides"] = Field(
        ..., description="Type of Google Workspace resource: 'docs', 'sheets', or 'slides'"
    )
    mode: Literal["create", "modify"] = Field(
        ...,
        description="Operation mode: 'create' to create new resource or 'modify' to update existing",
    )

    # Common parameters
    title: Optional[str] = Field(None, description="Resource title (required for create mode)")
    share_with: Optional[List[str]] = Field(
        None, description="List of email addresses to share the resource with"
    )

    # Docs-specific parameters
    document_id: Optional[str] = Field(None, description="Document ID for modify mode (docs only)")
    content: Optional[str] = Field(
        None, description="Document content with markdown support (docs only)"
    )
    modify_action: str = Field(
        "append", description="Modification action: 'append', 'replace', or 'insert' (docs only)"
    )
    insert_index: int = Field(1, description="Insert position for insert action (docs only)", ge=1)
    folder_id: Optional[str] = Field(
        None, description="Google Drive folder ID for new documents (docs only)"
    )

    # Sheets-specific parameters
    spreadsheet_id: Optional[str] = Field(
        None, description="Spreadsheet ID for modify mode (sheets only)"
    )
    data: Optional[List[List[Any]]] = Field(
        None, description="List of lists representing rows and columns (sheets only)"
    )
    sheet_name: str = Field("Sheet1", description="Worksheet name within spreadsheet (sheets only)")
    formulas: Optional[Dict[str, str]] = Field(
        None, description="Dictionary mapping cell references to formulas (sheets only)"
    )
    formatting: Optional[Dict[str, Any]] = Field(
        None, description="Dictionary with formatting options (sheets only)"
    )

    # Slides-specific parameters
    presentation_id: Optional[str] = Field(
        None, description="Presentation ID for modify mode (slides only)"
    )
    slides: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of slide definitions with layout and content (slides only)"
    )
    theme: str = Field(
        "default",
        description="Theme to apply: 'default', 'simple', 'modern', 'colorful' (slides only)",
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the unified workspace tool.

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
            # Get shared credentials
            credentials = self._get_credentials()

            # Delegate to workspace-specific handler
            handlers = {
                "docs": self._handle_docs,
                "sheets": self._handle_sheets,
                "slides": self._handle_slides,
            }

            result = handlers[self.workspace_type](credentials)

            # Share if requested
            if self.share_with:
                resource_id = (
                    result.get("document_id")
                    or result.get("spreadsheet_id")
                    or result.get("presentation_id")
                )
                self._share_resource(credentials, resource_id)
                result["shared_with"] = self.share_with

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "workspace_type": self.workspace_type,
                    "mode": self.mode,
                },
            }

        except HttpError as e:
            raise APIError(
                f"Google Workspace API error: {e}",
                tool_name=self.tool_name,
                api_name=f"Google {self.workspace_type.capitalize()}",
                status_code=e.resp.status if hasattr(e, "resp") else None,
            )
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters with workspace-specific logic.

        Raises:
            ValidationError: If inputs are invalid
        """
        # Common validation
        if self.mode == "create" and not self.title:
            raise ValidationError(
                "title is required for create mode", tool_name=self.tool_name, field="title"
            )

        # Workspace-specific validation
        if self.workspace_type == "docs":
            self._validate_docs_parameters()
        elif self.workspace_type == "sheets":
            self._validate_sheets_parameters()
        elif self.workspace_type == "slides":
            self._validate_slides_parameters()

        # Validate email addresses if provided
        if self.share_with:
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            for email in self.share_with:
                if not re.match(email_pattern, email):
                    raise ValidationError(
                        f"Invalid email address: {email}",
                        tool_name=self.tool_name,
                        field="share_with",
                    )

    def _validate_docs_parameters(self) -> None:
        """Validate docs-specific parameters."""
        if not self.content or not self.content.strip():
            raise ValidationError(
                "content is required for docs", tool_name=self.tool_name, field="content"
            )

        if self.mode == "modify":
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

    def _validate_sheets_parameters(self) -> None:
        """Validate sheets-specific parameters."""
        if not self.data or not isinstance(self.data, list):
            raise ValidationError(
                "data is required for sheets and must be a list of lists",
                tool_name=self.tool_name,
                field="data",
            )

        if not all(isinstance(row, list) for row in self.data):
            raise ValidationError(
                "data must be a list of lists (rows)", tool_name=self.tool_name, field="data"
            )

        if self.mode == "modify" and not self.spreadsheet_id:
            raise ValidationError(
                "spreadsheet_id is required for modify mode",
                tool_name=self.tool_name,
                field="spreadsheet_id",
            )

    def _validate_slides_parameters(self) -> None:
        """Validate slides-specific parameters."""
        if not self.slides or len(self.slides) == 0:
            raise ValidationError(
                "slides is required for slides and must contain at least one slide",
                tool_name=self.tool_name,
                field="slides",
            )

        # Validate each slide
        valid_layouts = ["title", "title_and_body", "section_header", "two_columns", "blank"]
        for idx, slide in enumerate(self.slides):
            if "layout" not in slide:
                raise ValidationError(
                    f"Slide {idx + 1} missing required 'layout' field",
                    tool_name=self.tool_name,
                    field="slides",
                )

            if slide["layout"] not in valid_layouts:
                raise ValidationError(
                    f"Slide {idx + 1} has invalid layout: {slide['layout']}",
                    tool_name=self.tool_name,
                    field="slides",
                    details={"valid_layouts": valid_layouts},
                )

        if self.mode == "modify" and not self.presentation_id:
            raise ValidationError(
                "presentation_id is required for modify mode",
                tool_name=self.tool_name,
                field="presentation_id",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        if self.workspace_type == "docs":
            return self._generate_mock_docs_results()
        elif self.workspace_type == "sheets":
            return self._generate_mock_sheets_results()
        else:  # slides
            return self._generate_mock_slides_results()

    def _generate_mock_docs_results(self) -> Dict[str, Any]:
        """Generate mock results for docs."""
        mock_doc_id = f"mock-doc-{hash(self.title or self.document_id) % 10000}"

        result = {
            "mock": True,
            "mode": self.mode,
            "document_id": self.document_id if self.mode == "modify" else mock_doc_id,
            "title": self.title or "Mock Document",
            "shareable_link": f"https://docs.google.com/document/d/{mock_doc_id}/edit",
            "content_preview": self.content[:100] + ("..." if len(self.content) > 100 else ""),
            "shared_with": self.share_with or [],
        }

        if self.mode == "modify":
            result["modify_action"] = self.modify_action
        if self.folder_id:
            result["folder_id"] = self.folder_id

        return {
            "success": True,
            "result": result,
            "metadata": {"mock_mode": True, "workspace_type": "docs", "mode": self.mode},
        }

    def _generate_mock_sheets_results(self) -> Dict[str, Any]:
        """Generate mock results for sheets."""
        mock_id = self.spreadsheet_id if self.mode == "modify" else "1mock_ABC123XYZ"

        result = {
            "spreadsheet_id": mock_id,
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{mock_id}/edit",
            "mode": self.mode,
            "rows_written": len(self.data),
            "columns_written": len(self.data[0]) if self.data else 0,
            "sheet_name": self.sheet_name,
            "status": "created" if self.mode == "create" else "modified",
        }

        if self.mode == "create":
            result["title"] = self.title
        if self.formulas:
            result["formulas_applied"] = len(self.formulas)
        if self.share_with:
            result["shared_with"] = self.share_with

        return {
            "success": True,
            "result": result,
            "metadata": {"mock_mode": True, "workspace_type": "sheets", "mode": self.mode},
        }

    def _generate_mock_slides_results(self) -> Dict[str, Any]:
        """Generate mock results for slides."""
        presentation_id = (
            self.presentation_id if self.mode == "modify" else "mock-presentation-id-123abc"
        )

        result = {
            "presentation_id": presentation_id,
            "url": f"https://docs.google.com/presentation/d/{presentation_id}/edit",
            "title": self.title if self.mode == "create" else "Modified Presentation",
            "slide_count": len(self.slides),
            "slides": [
                {
                    "slide_id": f"mock-slide-{i+1}",
                    "layout": slide.get("layout"),
                    "title": slide.get("title", ""),
                }
                for i, slide in enumerate(self.slides)
            ],
            "theme_applied": self.theme,
            "shared_with": self.share_with or [],
            "mode": self.mode,
            "mock": True,
        }

        # Add slides_added for modify mode
        if self.mode == "modify":
            result["slides_added"] = len(self.slides)

        return {
            "success": True,
            "result": result,
            "metadata": {"mock_mode": True, "workspace_type": "slides", "mode": self.mode},
        }

    def _get_credentials(self):
        """
        Get Google API credentials from environment.

        Checks for workspace-specific credentials or falls back to generic ones.

        Returns:
            Google credentials object

        Raises:
            AuthenticationError: If credentials are missing or invalid
        """
        # Try workspace-specific credentials first
        env_vars = {
            "docs": "GOOGLE_DOCS_CREDENTIALS",
            "sheets": "GOOGLE_SHEETS_CREDENTIALS",
            "slides": "GOOGLE_SLIDES_CREDENTIALS",
        }

        credentials_json = os.getenv(env_vars[self.workspace_type])

        # Fall back to generic workspace credentials
        if not credentials_json:
            credentials_json = os.getenv("GOOGLE_WORKSPACE_CREDENTIALS")

        if not credentials_json:
            raise AuthenticationError(
                f"Missing {env_vars[self.workspace_type]} or GOOGLE_WORKSPACE_CREDENTIALS environment variable",
                tool_name=self.tool_name,
                api_name=f"Google {self.workspace_type.capitalize()}",
            )

        try:
            # Parse credentials JSON
            credentials_info = json.loads(credentials_json)

            # Determine scopes based on workspace type
            scopes_map = {
                "docs": [
                    "https://www.googleapis.com/auth/documents",
                    "https://www.googleapis.com/auth/drive.file",
                ],
                "sheets": [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file",
                ],
                "slides": [
                    "https://www.googleapis.com/auth/presentations",
                    "https://www.googleapis.com/auth/drive.file",
                ],
            }

            scopes = scopes_map[self.workspace_type]

            # Create credentials
            creds = service_account.Credentials.from_service_account_info(
                credentials_info, scopes=scopes
            )

            return creds

        except json.JSONDecodeError:
            raise AuthenticationError(
                "Invalid credentials JSON format",
                tool_name=self.tool_name,
                api_name=f"Google {self.workspace_type.capitalize()}",
            )
        except Exception as e:
            raise AuthenticationError(
                f"Failed to create credentials: {e}",
                tool_name=self.tool_name,
                api_name=f"Google {self.workspace_type.capitalize()}",
            )

    def _handle_docs(self, credentials) -> Dict[str, Any]:
        """Handle Google Docs operations."""
        docs_service = build("docs", "v1", credentials=credentials)
        drive_service = build("drive", "v3", credentials=credentials)

        if self.mode == "create":
            return self._create_document(docs_service, drive_service)
        else:
            return self._modify_document(docs_service, drive_service)

    def _handle_sheets(self, credentials) -> Dict[str, Any]:
        """Handle Google Sheets operations."""
        sheets_service = build("sheets", "v4", credentials=credentials)

        if self.mode == "create":
            return self._create_spreadsheet(sheets_service)
        else:
            return self._modify_spreadsheet(sheets_service)

    def _handle_slides(self, credentials) -> Dict[str, Any]:
        """Handle Google Slides operations."""
        slides_service = build("slides", "v1", credentials=credentials)

        if self.mode == "create":
            return self._create_presentation(slides_service)
        else:
            return self._modify_presentation(slides_service)

    # Docs implementation methods

    def _create_document(self, docs_service, drive_service) -> Dict[str, Any]:
        """Create a new Google Doc."""
        document = docs_service.documents().create(body={"title": self.title}).execute()

        document_id = document.get("documentId")

        # Add content
        requests = self._convert_content_to_requests(self.content)
        if requests:
            docs_service.documents().batchUpdate(
                documentId=document_id, body={"requests": requests}
            ).execute()

        # Move to folder if specified
        if self.folder_id:
            try:
                file = drive_service.files().get(fileId=document_id, fields="parents").execute()

                previous_parents = ",".join(file.get("parents", []))

                drive_service.files().update(
                    fileId=document_id,
                    addParents=self.folder_id,
                    removeParents=previous_parents,
                    fields="id, parents",
                ).execute()
            except HttpError:
                pass  # Don't fail if folder move fails

        return {
            "document_id": document_id,
            "title": self.title,
            "shareable_link": f"https://docs.google.com/document/d/{document_id}/edit",
            "folder_id": self.folder_id,
        }

    def _modify_document(self, docs_service, drive_service) -> Dict[str, Any]:
        """Modify an existing Google Doc."""
        try:
            document = docs_service.documents().get(documentId=self.document_id).execute()
        except HttpError as e:
            if e.resp.status == 404:
                raise ValidationError(
                    f"Document not found: {self.document_id}",
                    tool_name=self.tool_name,
                    field="document_id",
                )
            raise

        title = document.get("title", "Untitled")

        # Build modification requests
        requests = []

        if self.modify_action == "replace":
            # Delete all content first
            end_index = document.get("body", {}).get("content", [{}])[-1].get("endIndex", 1)
            if end_index > 1:
                requests.append(
                    {
                        "deleteContentRange": {
                            "range": {
                                "startIndex": 1,
                                "endIndex": end_index - 1,
                            }
                        }
                    }
                )
            requests.extend(self._convert_content_to_requests(self.content, index=1))

        elif self.modify_action == "append":
            end_index = document.get("body", {}).get("content", [{}])[-1].get("endIndex", 1)
            insert_index = max(1, end_index - 1)
            requests.extend(self._convert_content_to_requests(self.content, index=insert_index))

        elif self.modify_action == "insert":
            requests.extend(
                self._convert_content_to_requests(self.content, index=self.insert_index)
            )

        if requests:
            docs_service.documents().batchUpdate(
                documentId=self.document_id, body={"requests": requests}
            ).execute()

        return {
            "document_id": self.document_id,
            "title": title,
            "shareable_link": f"https://docs.google.com/document/d/{self.document_id}/edit",
            "modify_action": self.modify_action,
        }

    def _convert_content_to_requests(self, content: str, index: int = 1) -> List[Dict[str, Any]]:
        """Convert markdown content to Google Docs API requests."""
        requests = []
        lines = content.split("\n")
        current_index = index

        for line in lines:
            if not line.strip():
                requests.append(
                    {
                        "insertText": {
                            "location": {"index": current_index},
                            "text": "\n",
                        }
                    }
                )
                current_index += 1
                continue

            # Check for heading
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2) + "\n"

                requests.append(
                    {
                        "insertText": {
                            "location": {"index": current_index},
                            "text": text,
                        }
                    }
                )

                requests.append(
                    {
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
                    }
                )

                current_index += len(text)
                continue

            # Process inline formatting
            formatted_text = line + "\n"
            requests.append(
                {
                    "insertText": {
                        "location": {"index": current_index},
                        "text": formatted_text,
                    }
                }
            )

            current_index += len(formatted_text)

        return requests

    # Sheets implementation methods

    def _create_spreadsheet(self, service) -> Dict[str, Any]:
        """Create a new Google Spreadsheet."""
        spreadsheet = {"properties": {"title": self.title}}

        spreadsheet = (
            service.spreadsheets().create(body=spreadsheet, fields="spreadsheetId").execute()
        )

        spreadsheet_id = spreadsheet.get("spreadsheetId")

        # Write data
        self._write_data(service, spreadsheet_id)

        # Apply formulas if provided
        if self.formulas:
            self._apply_formulas(service, spreadsheet_id)

        # Apply formatting if provided
        if self.formatting:
            self._apply_formatting(service, spreadsheet_id)

        return {
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
            "title": self.title,
            "status": "created",
            "rows_written": len(self.data),
            "columns_written": len(self.data[0]) if self.data else 0,
            "sheet_name": self.sheet_name,
            "formulas_applied": len(self.formulas) if self.formulas else 0,
        }

    def _modify_spreadsheet(self, service) -> Dict[str, Any]:
        """Modify an existing Google Spreadsheet."""
        # Write data
        self._write_data(service, self.spreadsheet_id)

        # Apply formulas if provided
        if self.formulas:
            self._apply_formulas(service, self.spreadsheet_id)

        # Apply formatting if provided
        if self.formatting:
            self._apply_formatting(service, self.spreadsheet_id)

        return {
            "spreadsheet_id": self.spreadsheet_id,
            "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit",
            "status": "modified",
            "rows_written": len(self.data),
            "columns_written": len(self.data[0]) if self.data else 0,
            "sheet_name": self.sheet_name,
            "formulas_applied": len(self.formulas) if self.formulas else 0,
        }

    def _write_data(self, service, spreadsheet_id: str) -> None:
        """Write data to spreadsheet."""
        range_name = f"{self.sheet_name}!A1"
        body = {"values": self.data}

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def _apply_formulas(self, service, spreadsheet_id: str) -> None:
        """Apply formulas to specific cells."""
        if not self.formulas:
            return

        for cell_ref, formula in self.formulas.items():
            range_name = f"{self.sheet_name}!{cell_ref}"
            body = {"values": [[formula]]}

            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            ).execute()

    def _apply_formatting(self, service, spreadsheet_id: str) -> None:
        """Apply cell formatting."""
        if not self.formatting:
            return

        requests = []

        if self.formatting.get("bold_header", False):
            requests.append(
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                        },
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat.bold",
                    }
                }
            )

        if requests:
            body = {"requests": requests}
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    # Slides implementation methods

    def _create_presentation(self, service) -> Dict[str, Any]:
        """Create a new Google Slides presentation."""
        presentation = {"title": self.title}

        created_presentation = service.presentations().create(body=presentation).execute()
        presentation_id = created_presentation["presentationId"]

        # Add slides
        slide_ids = []
        requests = []

        for idx, slide_def in enumerate(self.slides):
            slide_id = f"slide_{idx}"
            slide_ids.append(slide_id)

            requests.append(
                {
                    "createSlide": {
                        "objectId": slide_id,
                        "slideLayoutReference": {
                            "predefinedLayout": self._get_predefined_layout(slide_def["layout"])
                        },
                    }
                }
            )

        if requests:
            service.presentations().batchUpdate(
                presentationId=presentation_id, body={"requests": requests}
            ).execute()

        return {
            "presentation_id": presentation_id,
            "url": f"https://docs.google.com/presentation/d/{presentation_id}/edit",
            "title": self.title,
            "slide_count": len(self.slides),
            "slides": [{"slide_id": sid} for sid in slide_ids],
            "created_at": datetime.now().isoformat(),
        }

    def _modify_presentation(self, service) -> Dict[str, Any]:
        """Modify an existing Google Slides presentation."""
        presentation = service.presentations().get(presentationId=self.presentation_id).execute()

        # Add new slides
        slide_ids = []
        requests = []

        for idx, slide_def in enumerate(self.slides):
            slide_id = f"new_slide_{idx}_{datetime.utcnow().timestamp()}"
            slide_ids.append(slide_id)

            requests.append(
                {
                    "createSlide": {
                        "objectId": slide_id,
                        "slideLayoutReference": {
                            "predefinedLayout": self._get_predefined_layout(slide_def["layout"])
                        },
                    }
                }
            )

        if requests:
            service.presentations().batchUpdate(
                presentationId=self.presentation_id, body={"requests": requests}
            ).execute()

        updated_presentation = (
            service.presentations().get(presentationId=self.presentation_id).execute()
        )

        return {
            "presentation_id": self.presentation_id,
            "url": f"https://docs.google.com/presentation/d/{self.presentation_id}/edit",
            "title": presentation.get("title", ""),
            "slide_count": len(updated_presentation.get("slides", [])),
            "slides_added": len(self.slides),
            "new_slide_ids": slide_ids,
            "modified_at": datetime.now().isoformat(),
        }

    def _get_predefined_layout(self, layout: str) -> str:
        """Map custom layout names to Google Slides predefined layouts."""
        layout_map = {
            "title": "TITLE",
            "title_and_body": "TITLE_AND_BODY",
            "section_header": "SECTION_HEADER",
            "two_columns": "TITLE_AND_TWO_COLUMNS",
            "blank": "BLANK",
        }
        return layout_map.get(layout, "BLANK")

    # Shared resource methods

    def _share_resource(self, credentials, resource_id: str) -> None:
        """Share resource with specified email addresses."""
        if not self.share_with:
            return

        try:
            drive_service = build("drive", "v3", credentials=credentials)

            for email in self.share_with:
                permission = {
                    "type": "user",
                    "role": "writer",
                    "emailAddress": email,
                }

                drive_service.permissions().create(
                    fileId=resource_id,
                    body=permission,
                    sendNotificationEmail=True,
                ).execute()

        except Exception as e:
            # Log warning but don't fail
            self._logger.warning(f"Failed to share with {email}: {e}")


if __name__ == "__main__":
    """Test the unified_google_workspace tool."""
    print("Testing UnifiedGoogleWorkspace tool...")
    print("=" * 60)

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Create Google Doc
    print("\nTest 1: Create Google Doc")
    print("-" * 60)
    tool = UnifiedGoogleWorkspace(
        workspace_type="docs",
        mode="create",
        title="Test Document",
        content="# Hello World\n\nThis is **bold** text.",
        share_with=["user@example.com"],
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Document ID: {result.get('result', {}).get('document_id')}")
    print(f"Link: {result.get('result', {}).get('shareable_link')}")
    assert result.get("success") == True
    assert "document_id" in result.get("result", {})
    print("✓ Test 1 passed")

    # Test 2: Modify Google Doc
    print("\nTest 2: Modify Google Doc")
    print("-" * 60)
    tool = UnifiedGoogleWorkspace(
        workspace_type="docs",
        mode="modify",
        document_id="doc123",
        content="New content",
        modify_action="append",
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Action: {result.get('result', {}).get('modify_action')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("modify_action") == "append"
    print("✓ Test 2 passed")

    # Test 3: Create Google Sheet
    print("\nTest 3: Create Google Sheet")
    print("-" * 60)
    tool = UnifiedGoogleWorkspace(
        workspace_type="sheets",
        mode="create",
        title="Sales Report",
        data=[["Product", "Sales"], ["Widget A", 1000], ["Widget B", 1500]],
        sheet_name="Q4 Data",
        formulas={"C1": "=SUM(B2:B3)"},
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Spreadsheet ID: {result.get('result', {}).get('spreadsheet_id')}")
    print(f"Rows: {result.get('result', {}).get('rows_written')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("rows_written") == 3
    print("✓ Test 3 passed")

    # Test 4: Modify Google Sheet
    print("\nTest 4: Modify Google Sheet")
    print("-" * 60)
    tool = UnifiedGoogleWorkspace(
        workspace_type="sheets",
        mode="modify",
        spreadsheet_id="sheet123",
        data=[["Updated", "Data"]],
        sheet_name="Sheet1",
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('result', {}).get('status')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("status") == "modified"
    print("✓ Test 4 passed")

    # Test 5: Create Google Slides
    print("\nTest 5: Create Google Slides")
    print("-" * 60)
    tool = UnifiedGoogleWorkspace(
        workspace_type="slides",
        mode="create",
        title="Q4 Presentation",
        slides=[
            {"layout": "title", "title": "Welcome"},
            {"layout": "title_and_body", "title": "Content", "content": "Details here"},
        ],
        theme="modern",
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Presentation ID: {result.get('result', {}).get('presentation_id')}")
    print(f"Slides: {result.get('result', {}).get('slide_count')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("slide_count") == 2
    print("✓ Test 5 passed")

    # Test 6: Modify Google Slides
    print("\nTest 6: Modify Google Slides")
    print("-" * 60)
    tool = UnifiedGoogleWorkspace(
        workspace_type="slides",
        mode="modify",
        presentation_id="pres123",
        slides=[{"layout": "blank"}],
    )
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Slides added: {result.get('result', {}).get('slides_added')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("slides_added") == 1
    print("✓ Test 6 passed")

    # Test 7: Validation - missing title
    print("\nTest 7: Validation - missing title in create mode")
    print("-" * 60)
    try:
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs", mode="create", content="Content without title"
        )
        result = tool.run()
        print("ERROR: Should have raised validation error")
        assert False
    except Exception as e:
        print(f"Expected error: {str(e)}")
        print("✓ Test 7 passed")

    # Test 8: Validation - missing workspace-specific field
    print("\nTest 8: Validation - missing content for docs")
    print("-" * 60)
    try:
        tool = UnifiedGoogleWorkspace(workspace_type="docs", mode="create", title="Test")
        result = tool.run()
        print("ERROR: Should have raised validation error")
        assert False
    except Exception as e:
        print(f"Expected error: {str(e)}")
        print("✓ Test 8 passed")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
