"""
Create and modify Google Docs using Google Docs API v1

DEPRECATED: This tool is now a backward compatibility wrapper around UnifiedGoogleWorkspace.
For new code, use UnifiedGoogleWorkspace with workspace_type="docs" instead.
This wrapper will be maintained for backward compatibility but may be removed in a future version.
"""

from typing import Any, Dict, Optional, List
from pydantic import Field
import os
import warnings

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError


class GoogleDocs(BaseTool):
    """
    Create and modify Google Docs using Google Docs API v1.

    DEPRECATED: Use UnifiedGoogleWorkspace with workspace_type="docs" instead.

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
        Execute the google_docs tool by delegating to UnifiedGoogleWorkspace.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid inputs
            APIError: For API failures
        """
        # Emit deprecation warning
        warnings.warn(
            "GoogleDocs is deprecated. Use UnifiedGoogleWorkspace with workspace_type='docs' instead. "
            "This wrapper will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Import here to avoid circular dependency
        from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

        # Create unified tool with equivalent parameters
        unified_tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode=self.mode,
            title=self.title,
            document_id=self.document_id,
            content=self.content,
            modify_action=self.modify_action,
            insert_index=self.insert_index,
            share_with=self.share_with,
            folder_id=self.folder_id,
        )

        # Execute and get result
        result = unified_tool._execute()

        # Preserve original tool name in metadata for backward compatibility
        if "metadata" in result:
            result["metadata"]["tool_name"] = self.tool_name
            result["metadata"]["deprecated"] = True
            result["metadata"]["delegate_to"] = "unified_google_workspace"

        return result

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Note: Validation is now handled by UnifiedGoogleWorkspace,
        but we keep this method for backward compatibility.
        """
        pass

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """
        Generate mock results for testing.

        Note: Now delegated to UnifiedGoogleWorkspace.
        """
        pass

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic.

        Note: Now delegated to UnifiedGoogleWorkspace.
        """
        pass


if __name__ == "__main__":
    """Test the google_docs tool."""
    print("Testing GoogleDocs tool (backward compatibility wrapper)...")
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
    print(f"Deprecated: {result.get('metadata', {}).get('deprecated')}")
    assert result.get("success") == True
    assert "document_id" in result.get("result", {})
    assert result.get("metadata", {}).get("deprecated") == True
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

    # Test 4: Validation - missing title in create mode
    print("\nTest 4: Validation - missing title")
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
        print(f"Expected error caught: {str(e)}")
        print("✓ Test 4 passed")

    # Test 5: Validation - missing document_id in modify mode
    print("\nTest 5: Validation - missing document_id")
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
        print(f"Expected error caught: {str(e)}")
        print("✓ Test 5 passed")

    print("\n" + "=" * 60)
    print("All backward compatibility tests passed!")
    print("Note: This wrapper delegates to UnifiedGoogleWorkspace")
    print("=" * 60)
