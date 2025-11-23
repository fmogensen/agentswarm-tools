"""
Unit tests for UnifiedGoogleWorkspace tool
"""

import os
from unittest.mock import Mock, patch

import pytest

from shared.errors import APIError, AuthenticationError, ValidationError

from .unified_google_workspace import UnifiedGoogleWorkspace


class TestUnifiedGoogleWorkspaceDocs:
    """Test suite for UnifiedGoogleWorkspace - Docs workspace type."""

    def setup_method(self):
        """Setup test environment before each test."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after each test."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Test successful operations

    def test_create_doc_success(self):
        """Test successful document creation."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="create",
            title="Test Document",
            content="# Test\n\nThis is a test document.",
        )
        result = tool.run()

        assert result["success"] == True
        assert "document_id" in result["result"]
        assert "shareable_link" in result["result"]
        assert result["result"]["title"] == "Test Document"
        assert result["metadata"]["workspace_type"] == "docs"
        assert result["metadata"]["mode"] == "create"

    def test_create_doc_with_sharing(self):
        """Test creating document with sharing."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="create",
            title="Shared Document",
            content="Content to share",
            share_with=["user1@example.com", "user2@example.com"],
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["result"]["shared_with"]) == 2
        assert "user1@example.com" in result["result"]["shared_with"]

    def test_create_doc_with_folder(self):
        """Test creating document in specific folder."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="create",
            title="Document in Folder",
            content="Content",
            folder_id="folder123",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["folder_id"] == "folder123"

    def test_modify_doc_append(self):
        """Test appending content to existing document."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="modify",
            document_id="doc123",
            content="Appended content",
            modify_action="append",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["modify_action"] == "append"
        assert result["result"]["document_id"] == "doc123"

    def test_modify_doc_replace(self):
        """Test replacing document content."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="modify",
            document_id="doc456",
            content="Replaced content",
            modify_action="replace",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["modify_action"] == "replace"

    def test_modify_doc_insert(self):
        """Test inserting content at specific position."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="modify",
            document_id="doc789",
            content="Inserted content",
            modify_action="insert",
            insert_index=10,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["modify_action"] == "insert"

    # Test validation

    def test_validation_missing_title_docs_create(self):
        """Test validation when title is missing in create mode."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="docs",
                mode="create",
                content="Content without title",
            )
            tool.run()

        assert "title is required" in str(exc_info.value)

    def test_validation_missing_content_docs(self):
        """Test validation when content is missing."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="docs",
                mode="create",
                title="Test",
            )
            tool.run()

        assert "content is required" in str(exc_info.value)

    def test_validation_missing_document_id_docs_modify(self):
        """Test validation when document_id is missing in modify mode."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="docs",
                mode="modify",
                content="Content without doc ID",
            )
            tool.run()

        assert "document_id is required" in str(exc_info.value)

    def test_validation_invalid_modify_action_docs(self):
        """Test validation with invalid modify action."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="docs",
                mode="modify",
                document_id="doc123",
                content="Content",
                modify_action="invalid",
            )
            tool.run()

        assert "modify_action must be" in str(exc_info.value)


class TestUnifiedGoogleWorkspaceSheets:
    """Test suite for UnifiedGoogleWorkspace - Sheets workspace type."""

    def setup_method(self):
        """Setup test environment before each test."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after each test."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Test successful operations

    def test_create_sheet_success(self):
        """Test successful spreadsheet creation."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="sheets",
            mode="create",
            title="Sales Report Q4 2024",
            data=[
                ["Product", "Q1", "Q2", "Q3", "Q4"],
                ["Widget A", 1000, 1200, 1100, 1500],
                ["Widget B", 800, 900, 950, 1000],
            ],
            sheet_name="Sales Data",
        )
        result = tool.run()

        assert result["success"] == True
        assert "spreadsheet_id" in result["result"]
        assert "spreadsheet_url" in result["result"]
        assert result["result"]["rows_written"] == 3
        assert result["metadata"]["workspace_type"] == "sheets"

    def test_create_sheet_with_formulas(self):
        """Test creating spreadsheet with formulas."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="sheets",
            mode="create",
            title="Report with Formulas",
            data=[["A", "B"], [1, 2], [3, 4]],
            formulas={"C1": "=SUM(A1:B1)", "C2": "=A2+B2"},
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formulas_applied"] == 2

    def test_create_sheet_with_formatting(self):
        """Test creating spreadsheet with formatting."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="sheets",
            mode="create",
            title="Formatted Report",
            data=[["Header1", "Header2"], [1, 2]],
            formatting={"bold_header": True},
        )
        result = tool.run()

        assert result["success"] == True

    def test_modify_sheet_success(self):
        """Test modifying existing spreadsheet."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="sheets",
            mode="modify",
            spreadsheet_id="1ABC123XYZ",
            data=[["Updated", "Data"], [100, 200]],
            sheet_name="Sheet1",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["status"] == "modified"
        assert result["result"]["spreadsheet_id"] == "1ABC123XYZ"

    def test_create_sheet_with_sharing(self):
        """Test creating spreadsheet with sharing."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="sheets",
            mode="create",
            title="Shared Sheet",
            data=[["Data"]],
            share_with=["user@example.com"],
        )
        result = tool.run()

        assert result["success"] == True
        assert "user@example.com" in result["result"]["shared_with"]

    # Test validation

    def test_validation_missing_title_sheets_create(self):
        """Test validation when title is missing in create mode."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="sheets",
                mode="create",
                data=[["Test"]],
            )
            tool.run()

        assert "title is required" in str(exc_info.value)

    def test_validation_missing_data_sheets(self):
        """Test validation when data is missing."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="sheets",
                mode="create",
                title="Test",
            )
            tool.run()

        assert "data is required" in str(exc_info.value)

    def test_validation_invalid_data_sheets(self):
        """Test validation with invalid data format."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="sheets",
                mode="create",
                title="Test",
                data="not a list",
            )
            tool.run()

        assert "data" in str(exc_info.value)

    def test_validation_missing_spreadsheet_id_sheets_modify(self):
        """Test validation when spreadsheet_id is missing in modify mode."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="sheets",
                mode="modify",
                data=[["Test"]],
            )
            tool.run()

        assert "spreadsheet_id is required" in str(exc_info.value)


class TestUnifiedGoogleWorkspaceSlides:
    """Test suite for UnifiedGoogleWorkspace - Slides workspace type."""

    def setup_method(self):
        """Setup test environment before each test."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after each test."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Test successful operations

    def test_create_slides_success(self):
        """Test successful presentation creation."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="slides",
            mode="create",
            title="Q4 Sales Report 2024",
            slides=[
                {
                    "layout": "title",
                    "title": "Q4 Sales Report",
                    "subtitle": "2024 Performance Overview",
                },
                {"layout": "title_and_body", "title": "Key Metrics", "content": "Revenue: $10M"},
            ],
            theme="modern",
        )
        result = tool.run()

        assert result["success"] == True
        assert "presentation_id" in result["result"]
        assert "url" in result["result"]
        assert result["result"]["slide_count"] == 2
        assert result["metadata"]["workspace_type"] == "slides"

    def test_create_slides_all_layouts(self):
        """Test creating presentation with all layout types."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="slides",
            mode="create",
            title="Layout Showcase",
            slides=[
                {"layout": "title", "title": "Title Slide"},
                {"layout": "title_and_body", "title": "Content Slide"},
                {"layout": "section_header", "title": "Section Header"},
                {
                    "layout": "two_columns",
                    "title": "Two Columns",
                    "left_content": "Left",
                    "right_content": "Right",
                },
                {"layout": "blank"},
            ],
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["slide_count"] == 5

    def test_modify_slides_success(self):
        """Test modifying existing presentation."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="slides",
            mode="modify",
            presentation_id="1abc123def456",
            slides=[
                {
                    "layout": "title_and_body",
                    "title": "Additional Insights",
                    "content": "Market analysis",
                }
            ],
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["slides_added"] == 1
        assert result["result"]["presentation_id"] == "1abc123def456"

    def test_create_slides_with_sharing(self):
        """Test creating presentation with sharing."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="slides",
            mode="create",
            title="Shared Presentation",
            slides=[{"layout": "blank"}],
            share_with=["team@example.com"],
        )
        result = tool.run()

        assert result["success"] == True
        assert "team@example.com" in result["result"]["shared_with"]

    def test_create_slides_with_themes(self):
        """Test creating presentation with different themes."""
        themes = ["default", "simple", "modern", "colorful"]

        for theme in themes:
            tool = UnifiedGoogleWorkspace(
                workspace_type="slides",
                mode="create",
                title=f"Presentation with {theme} theme",
                slides=[{"layout": "blank"}],
                theme=theme,
            )
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["theme_applied"] == theme

    # Test validation

    def test_validation_missing_title_slides_create(self):
        """Test validation when title is missing in create mode."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="slides",
                mode="create",
                slides=[{"layout": "blank"}],
            )
            tool.run()

        assert "title is required" in str(exc_info.value)

    def test_validation_missing_slides(self):
        """Test validation when slides are missing."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="slides",
                mode="create",
                title="Test",
            )
            tool.run()

        assert "slides is required" in str(exc_info.value)

    def test_validation_empty_slides(self):
        """Test validation with empty slides list."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="slides",
                mode="create",
                title="Test",
                slides=[],
            )
            tool.run()

        assert "slides is required" in str(exc_info.value)

    def test_validation_missing_layout_in_slide(self):
        """Test validation when slide is missing layout."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="slides",
                mode="create",
                title="Test",
                slides=[{"title": "No layout"}],
            )
            tool.run()

        assert "missing required 'layout' field" in str(exc_info.value)

    def test_validation_invalid_layout(self):
        """Test validation with invalid layout."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="slides",
                mode="create",
                title="Test",
                slides=[{"layout": "invalid_layout"}],
            )
            tool.run()

        assert "invalid layout" in str(exc_info.value)

    def test_validation_missing_presentation_id_slides_modify(self):
        """Test validation when presentation_id is missing in modify mode."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="slides",
                mode="modify",
                slides=[{"layout": "blank"}],
            )
            tool.run()

        assert "presentation_id is required" in str(exc_info.value)


class TestUnifiedGoogleWorkspaceCommon:
    """Test suite for UnifiedGoogleWorkspace - Common functionality."""

    def setup_method(self):
        """Setup test environment before each test."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after each test."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Test email validation

    def test_validation_invalid_email(self):
        """Test validation with invalid email address."""
        with pytest.raises(ValidationError) as exc_info:
            tool = UnifiedGoogleWorkspace(
                workspace_type="docs",
                mode="create",
                title="Test",
                content="Content",
                share_with=["invalid-email"],
            )
            tool.run()

        assert "Invalid email address" in str(exc_info.value)

    def test_validation_multiple_emails(self):
        """Test validation with multiple email addresses."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="create",
            title="Test",
            content="Content",
            share_with=["user1@example.com", "user2@example.com", "user3@example.com"],
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["result"]["shared_with"]) == 3

    # Test mock mode

    def test_mock_mode_docs(self):
        """Test that mock mode works for docs."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="create",
            title="Mock Test",
            content="Mock content",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["mock"] == True
        assert result["metadata"]["mock_mode"] == True

    def test_mock_mode_sheets(self):
        """Test that mock mode works for sheets."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="sheets",
            mode="create",
            title="Mock Test",
            data=[["Test"]],
        )
        result = tool.run()

        assert result["success"] == True

    def test_mock_mode_slides(self):
        """Test that mock mode works for slides."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="slides",
            mode="create",
            title="Mock Test",
            slides=[{"layout": "blank"}],
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["mock"] == True

    # Test response structure

    def test_response_structure_all_workspace_types(self):
        """Test that all workspace types return correct structure."""
        workspace_configs = [
            ("docs", {"title": "Test", "content": "Content"}),
            ("sheets", {"title": "Test", "data": [["Data"]]}),
            ("slides", {"title": "Test", "slides": [{"layout": "blank"}]}),
        ]

        for workspace_type, params in workspace_configs:
            tool = UnifiedGoogleWorkspace(workspace_type=workspace_type, mode="create", **params)
            result = tool.run()

            # Check top-level keys
            assert "success" in result
            assert "result" in result
            assert "metadata" in result

            # Check metadata
            assert result["metadata"]["tool_name"] == "unified_google_workspace"
            assert result["metadata"]["workspace_type"] == workspace_type
            assert result["metadata"]["mode"] == "create"

    # Test tool metadata

    def test_tool_name(self):
        """Test tool name is correct."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="create",
            title="Test",
            content="Content",
        )
        assert tool.tool_name == "unified_google_workspace"

    def test_tool_category(self):
        """Test tool category is correct."""
        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="create",
            title="Test",
            content="Content",
        )
        assert tool.tool_category == "communication"


class TestUnifiedGoogleWorkspaceRealMode:
    """Test suite for UnifiedGoogleWorkspace with real API mode (mocked)."""

    def setup_method(self):
        """Setup test environment."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_missing_credentials(self):
        """Test error when credentials are missing."""
        # Ensure no credentials in environment
        for var in [
            "GOOGLE_DOCS_CREDENTIALS",
            "GOOGLE_SHEETS_CREDENTIALS",
            "GOOGLE_SLIDES_CREDENTIALS",
            "GOOGLE_WORKSPACE_CREDENTIALS",
        ]:
            if var in os.environ:
                del os.environ[var]

        tool = UnifiedGoogleWorkspace(
            workspace_type="docs",
            mode="create",
            title="No Creds",
            content="Content",
        )

        with pytest.raises(AuthenticationError) as exc_info:
            tool.run()

        assert "CREDENTIALS" in str(exc_info.value)


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v", "--tb=short"])
