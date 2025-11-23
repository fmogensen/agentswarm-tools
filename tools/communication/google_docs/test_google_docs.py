"""
Unit tests for GoogleDocs tool
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from shared.errors import APIError, AuthenticationError, ValidationError

from .google_docs import GoogleDocs


class TestGoogleDocs:
    """Test suite for GoogleDocs tool."""

    def setup_method(self):
        """Setup test environment before each test."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after each test."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Test successful operations

    def test_create_document_success(self):
        """Test successful document creation."""
        tool = GoogleDocs(
            mode="create",
            title="Test Document",
            content="# Test\n\nThis is a test document.",
        )
        result = tool.run()

        assert result["success"] == True
        assert "document_id" in result["result"]
        assert "shareable_link" in result["result"]
        assert result["result"]["title"] == "Test Document"
        assert result["metadata"]["mode"] == "create"

    def test_create_document_with_sharing(self):
        """Test creating document with sharing."""
        tool = GoogleDocs(
            mode="create",
            title="Shared Document",
            content="Content to share",
            share_with=["user1@example.com", "user2@example.com"],
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["result"]["shared_with"]) == 2
        assert "user1@example.com" in result["result"]["shared_with"]

    def test_create_document_with_folder(self):
        """Test creating document in specific folder."""
        tool = GoogleDocs(
            mode="create",
            title="Document in Folder",
            content="Content",
            folder_id="folder123",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["folder_id"] == "folder123"

    def test_modify_document_append(self):
        """Test appending content to existing document."""
        tool = GoogleDocs(
            mode="modify",
            document_id="doc123",
            content="Appended content",
            modify_action="append",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["modify_action"] == "append"
        assert result["result"]["document_id"] == "doc123"

    def test_modify_document_replace(self):
        """Test replacing document content."""
        tool = GoogleDocs(
            mode="modify",
            document_id="doc456",
            content="Replaced content",
            modify_action="replace",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["modify_action"] == "replace"

    def test_modify_document_insert(self):
        """Test inserting content at specific position."""
        tool = GoogleDocs(
            mode="modify",
            document_id="doc789",
            content="Inserted content",
            modify_action="insert",
            insert_index=10,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["modify_action"] == "insert"

    # Test content formatting

    def test_markdown_content_with_headings(self):
        """Test markdown heading conversion."""
        tool = GoogleDocs(
            mode="create",
            title="Markdown Test",
            content="# Heading 1\n## Heading 2\n### Heading 3",
        )
        result = tool.run()

        assert result["success"] == True
        assert (
            "# Heading 1" in result["result"]["content_preview"]
            or "Heading 1" in result["result"]["content_preview"]
        )

    def test_markdown_content_with_bold(self):
        """Test markdown bold formatting."""
        tool = GoogleDocs(
            mode="create",
            title="Bold Test",
            content="This is **bold** text",
        )
        result = tool.run()

        assert result["success"] == True

    def test_markdown_content_with_italic(self):
        """Test markdown italic formatting."""
        tool = GoogleDocs(
            mode="create",
            title="Italic Test",
            content="This is *italic* text",
        )
        result = tool.run()

        assert result["success"] == True

    def test_complex_markdown_content(self):
        """Test complex markdown with multiple formatting types."""
        content = """
# Main Heading

This is a paragraph with **bold** and *italic* text.

## Subheading

More content here.

### Smaller heading

Final content.
"""
        tool = GoogleDocs(
            mode="create",
            title="Complex Document",
            content=content,
        )
        result = tool.run()

        assert result["success"] == True

    # Test validation

    def test_validation_invalid_mode(self):
        """Test validation with invalid mode."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GoogleDocs(
                mode="invalid",
                title="Test",
                content="Content",
            )
            tool.run()

        assert "mode must be 'create' or 'modify'" in str(exc_info.value)

    def test_validation_empty_content(self):
        """Test validation with empty content."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GoogleDocs(
                mode="create",
                title="Test",
                content="",
            )
            tool.run()

        assert "content cannot be empty" in str(exc_info.value)

    def test_validation_missing_title_in_create_mode(self):
        """Test validation when title is missing in create mode."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GoogleDocs(
                mode="create",
                content="Content without title",
            )
            tool.run()

        assert "title is required for create mode" in str(exc_info.value)

    def test_validation_missing_document_id_in_modify_mode(self):
        """Test validation when document_id is missing in modify mode."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GoogleDocs(
                mode="modify",
                content="Content without doc ID",
            )
            tool.run()

        assert "document_id is required for modify mode" in str(exc_info.value)

    def test_validation_invalid_modify_action(self):
        """Test validation with invalid modify action."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GoogleDocs(
                mode="modify",
                document_id="doc123",
                content="Content",
                modify_action="invalid",
            )
            tool.run()

        assert "modify_action must be" in str(exc_info.value)

    def test_validation_invalid_email(self):
        """Test validation with invalid email address."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GoogleDocs(
                mode="create",
                title="Test",
                content="Content",
                share_with=["invalid-email"],
            )
            tool.run()

        assert "Invalid email address" in str(exc_info.value)

    def test_validation_multiple_invalid_emails(self):
        """Test validation with mix of valid and invalid emails."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GoogleDocs(
                mode="create",
                title="Test",
                content="Content",
                share_with=["valid@example.com", "invalid"],
            )
            tool.run()

        assert "Invalid email address" in str(exc_info.value)

    # Test mock mode

    def test_mock_mode_enabled(self):
        """Test that mock mode returns expected structure."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = GoogleDocs(
            mode="create",
            title="Mock Test",
            content="Mock content",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["mock"] == True
        assert "mock-doc-" in result["result"]["document_id"]
        assert result["metadata"]["mock_mode"] == True

    def test_mock_mode_preserves_parameters(self):
        """Test that mock mode preserves input parameters."""
        os.environ["USE_MOCK_APIS"] = "true"

        emails = ["test@example.com"]
        tool = GoogleDocs(
            mode="create",
            title="Preserve Test",
            content="Long content " * 50,
            share_with=emails,
        )
        result = tool.run()

        assert result["result"]["title"] == "Preserve Test"
        assert result["result"]["shared_with"] == emails
        assert "content_preview" in result["result"]

    # Test edge cases

    def test_very_long_content(self):
        """Test handling of very long content."""
        long_content = "Lorem ipsum " * 1000
        tool = GoogleDocs(
            mode="create",
            title="Long Document",
            content=long_content,
        )
        result = tool.run()

        assert result["success"] == True

    def test_special_characters_in_content(self):
        """Test handling of special characters."""
        special_content = "Special chars: @#$%^&*()[]{}|<>?/~`"
        tool = GoogleDocs(
            mode="create",
            title="Special Chars",
            content=special_content,
        )
        result = tool.run()

        assert result["success"] == True

    def test_unicode_content(self):
        """Test handling of unicode characters."""
        unicode_content = "Unicode: 你好 🌍 Привет مرحبا"
        tool = GoogleDocs(
            mode="create",
            title="Unicode Test",
            content=unicode_content,
        )
        result = tool.run()

        assert result["success"] == True

    def test_empty_lines_in_content(self):
        """Test handling of empty lines."""
        content_with_empty_lines = "Line 1\n\n\nLine 2\n\n\n\nLine 3"
        tool = GoogleDocs(
            mode="create",
            title="Empty Lines",
            content=content_with_empty_lines,
        )
        result = tool.run()

        assert result["success"] == True

    def test_whitespace_only_title(self):
        """Test validation rejects whitespace-only title."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GoogleDocs(
                mode="create",
                title="   ",
                content="Content",
            )
            tool.run()

        assert "title is required" in str(exc_info.value)

    def test_insert_index_minimum(self):
        """Test minimum insert index."""
        tool = GoogleDocs(
            mode="modify",
            document_id="doc123",
            content="Insert at start",
            modify_action="insert",
            insert_index=1,
        )
        result = tool.run()

        assert result["success"] == True

    # Test metadata and response structure

    def test_response_structure_create(self):
        """Test response structure for create mode."""
        tool = GoogleDocs(
            mode="create",
            title="Structure Test",
            content="Content",
        )
        result = tool.run()

        # Check top-level keys
        assert "success" in result
        assert "result" in result
        assert "metadata" in result

        # Check result keys
        assert "document_id" in result["result"]
        assert "title" in result["result"]
        assert "shareable_link" in result["result"]

        # Check metadata
        assert result["metadata"]["tool_name"] == "google_docs"
        assert result["metadata"]["mode"] == "create"

    def test_response_structure_modify(self):
        """Test response structure for modify mode."""
        tool = GoogleDocs(
            mode="modify",
            document_id="doc123",
            content="Content",
            modify_action="append",
        )
        result = tool.run()

        # Check result keys
        assert "document_id" in result["result"]
        assert "modify_action" in result["result"]
        assert "shareable_link" in result["result"]

        # Check metadata
        assert result["metadata"]["mode"] == "modify"

    def test_shareable_link_format(self):
        """Test that shareable link has correct format."""
        tool = GoogleDocs(
            mode="create",
            title="Link Test",
            content="Content",
        )
        result = tool.run()

        link = result["result"]["shareable_link"]
        assert link.startswith("https://docs.google.com/document/d/")
        assert link.endswith("/edit")

    # Test tool metadata

    def test_tool_name(self):
        """Test tool name is correct."""
        tool = GoogleDocs(
            mode="create",
            title="Test",
            content="Content",
        )
        assert tool.tool_name == "google_docs"

    def test_tool_category(self):
        """Test tool category is correct."""
        tool = GoogleDocs(
            mode="create",
            title="Test",
            content="Content",
        )
        assert tool.tool_category == "communication"


class TestGoogleDocsRealMode:
    """Test suite for GoogleDocs with real API mode (mocked)."""

    def setup_method(self):
        """Setup test environment."""
        # Don't set USE_MOCK_APIS to test real mode path
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    @patch("tools.communication.google_docs.google_docs.build")
    @patch("tools.communication.google_docs.google_docs.service_account")
    def test_create_document_real_mode(self, mock_service_account, mock_build):
        """Test document creation in real mode with mocked API."""
        # Setup mocks
        mock_creds = Mock()
        mock_service_account.Credentials.from_service_account_info.return_value = mock_creds

        mock_docs = Mock()
        mock_drive = Mock()

        def build_side_effect(service, version, credentials):
            if service == "docs":
                return mock_docs
            return mock_drive

        mock_build.side_effect = build_side_effect

        # Mock docs API responses
        mock_docs.documents().create().execute.return_value = {"documentId": "real-doc-123"}
        mock_docs.documents().batchUpdate().execute.return_value = {}

        # Set credentials
        os.environ["GOOGLE_DOCS_CREDENTIALS"] = '{"type": "service_account", "project_id": "test"}'

        tool = GoogleDocs(
            mode="create",
            title="Real Mode Test",
            content="Content",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["document_id"] == "real-doc-123"

        # Cleanup
        del os.environ["GOOGLE_DOCS_CREDENTIALS"]

    def test_missing_credentials(self):
        """Test error when credentials are missing."""
        # Ensure no credentials in environment
        if "GOOGLE_DOCS_CREDENTIALS" in os.environ:
            del os.environ["GOOGLE_DOCS_CREDENTIALS"]

        tool = GoogleDocs(
            mode="create",
            title="No Creds",
            content="Content",
        )

        with pytest.raises(AuthenticationError) as exc_info:
            tool.run()

        assert "GOOGLE_DOCS_CREDENTIALS" in str(exc_info.value)


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v", "--tb=short"])
