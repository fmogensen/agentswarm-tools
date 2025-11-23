"""
Comprehensive tests for OfficeDocsTool
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from shared.errors import ConfigurationError, ValidationError
from tools.document_creation.office_docs.office_docs import OfficeDocsTool


class TestOfficeDocsTool:
    """Test suite for OfficeDocsTool"""

    def setup_method(self):
        """Setup for each test method"""
        # Enable mock mode by default
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after each test"""
        # Clean up environment
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Basic Functionality Tests

    def test_basic_document_creation(self):
        """Test basic document creation with minimal parameters"""
        tool = OfficeDocsTool(content="This is a simple document.")
        result = tool.run()

        assert result["success"] == True
        assert "result" in result
        assert "document_url" in result["result"]
        assert result["result"]["format"] == "docx"
        assert result["result"]["title"] == "Untitled Document"

    def test_document_with_title(self):
        """Test document creation with custom title"""
        tool = OfficeDocsTool(content="Document content here.", title="My Custom Title")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["title"] == "My Custom Title"

    def test_report_template(self):
        """Test report template"""
        tool = OfficeDocsTool(
            content="# Report\n\nThis is a report.", template="report", title="Q4 Sales Report"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["template"] == "report"

    def test_memo_template(self):
        """Test memo template"""
        tool = OfficeDocsTool(
            content="Important announcement.", template="memo", title="Company Update"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["template"] == "memo"

    def test_proposal_template(self):
        """Test proposal template"""
        tool = OfficeDocsTool(
            content="# Proposal\n\nProject details here.",
            template="proposal",
            title="Project Proposal",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["template"] == "proposal"

    def test_letter_template(self):
        """Test letter template"""
        tool = OfficeDocsTool(
            content="Dear Sir/Madam,\n\nLetter content.", template="letter", title="Business Letter"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["template"] == "letter"

    def test_blank_template(self):
        """Test blank template"""
        tool = OfficeDocsTool(content="Blank document content.", template="blank")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["template"] == "blank"

    # Table of Contents Tests

    def test_document_with_toc(self):
        """Test document with table of contents"""
        tool = OfficeDocsTool(
            content="# Chapter 1\n\nContent...\n\n# Chapter 2\n\nMore content...", include_toc=True
        )
        result = tool.run()

        assert result["success"] == True
        assert "document_url" in result["result"]

    def test_document_without_toc(self):
        """Test document without table of contents"""
        tool = OfficeDocsTool(content="# Section 1\n\nContent here.", include_toc=False)
        result = tool.run()

        assert result["success"] == True

    # Font Configuration Tests

    def test_calibri_font(self):
        """Test Calibri font"""
        tool = OfficeDocsTool(content="Test content.", font_name="Calibri")
        result = tool.run()

        assert result["success"] == True

    def test_arial_font(self):
        """Test Arial font"""
        tool = OfficeDocsTool(content="Test content.", font_name="Arial")
        result = tool.run()

        assert result["success"] == True

    def test_times_new_roman_font(self):
        """Test Times New Roman font"""
        tool = OfficeDocsTool(content="Test content.", font_name="Times New Roman")
        result = tool.run()

        assert result["success"] == True

    def test_font_size_minimum(self):
        """Test minimum font size"""
        tool = OfficeDocsTool(content="Small text.", font_size=8)
        result = tool.run()

        assert result["success"] == True

    def test_font_size_maximum(self):
        """Test maximum font size"""
        tool = OfficeDocsTool(content="Large text.", font_size=24)
        result = tool.run()

        assert result["success"] == True

    def test_font_size_default(self):
        """Test default font size"""
        tool = OfficeDocsTool(content="Normal text.", font_size=11)
        result = tool.run()

        assert result["success"] == True

    # Output Format Tests

    def test_docx_output(self):
        """Test DOCX output format"""
        tool = OfficeDocsTool(content="Document content.", output_format="docx")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["format"] == "docx"

    def test_pdf_output(self):
        """Test PDF output format"""
        tool = OfficeDocsTool(content="Document content.", output_format="pdf")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["format"] == "pdf"

    def test_both_output(self):
        """Test both DOCX and PDF output"""
        tool = OfficeDocsTool(content="Document content.", output_format="both")
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["format"] == "both"

    # Markdown Content Tests

    def test_markdown_headings(self):
        """Test markdown heading support"""
        tool = OfficeDocsTool(content="# Heading 1\n\n## Heading 2\n\n### Heading 3")
        result = tool.run()

        assert result["success"] == True

    def test_markdown_bullet_points(self):
        """Test markdown bullet points"""
        tool = OfficeDocsTool(content="- Point 1\n- Point 2\n- Point 3")
        result = tool.run()

        assert result["success"] == True

    def test_markdown_numbered_list(self):
        """Test markdown numbered lists"""
        tool = OfficeDocsTool(content="1. First\n2. Second\n3. Third")
        result = tool.run()

        assert result["success"] == True

    def test_complex_markdown(self):
        """Test complex markdown document"""
        content = """# Introduction

This is a comprehensive document.

## Section 1

- Bullet point 1
- Bullet point 2

## Section 2

1. Numbered item 1
2. Numbered item 2

### Subsection

Regular paragraph text here."""

        tool = OfficeDocsTool(content=content, title="Complex Document")
        result = tool.run()

        assert result["success"] == True

    # Validation Tests

    def test_empty_content_validation(self):
        """Test validation fails for empty content"""
        # Pydantic will catch this during initialization
        with pytest.raises(Exception):  # Pydantic ValidationError
            tool = OfficeDocsTool(content="")

    def test_whitespace_only_content_validation(self):
        """Test validation fails for whitespace-only content"""
        tool = OfficeDocsTool(content="   \n\n   ")
        result = tool.run()
        # BaseTool wraps errors - check the result
        assert result["success"] == False
        assert "empty" in result["error"]["message"].lower()

    def test_invalid_template_validation(self):
        """Test validation fails for invalid template"""
        tool = OfficeDocsTool(content="Test content.", template="invalid_template")
        result = tool.run()
        # BaseTool wraps errors
        assert result["success"] == False
        assert "template" in result["error"]["message"].lower()

    def test_invalid_output_format_validation(self):
        """Test validation fails for invalid output format"""
        tool = OfficeDocsTool(content="Test content.", output_format="invalid_format")
        result = tool.run()
        assert result["success"] == False
        assert "output_format" in result["error"]["message"].lower()

    def test_invalid_font_validation(self):
        """Test validation fails for invalid font"""
        tool = OfficeDocsTool(content="Test content.", font_name="InvalidFont")
        result = tool.run()
        assert result["success"] == False
        assert "font" in result["error"]["message"].lower()

    def test_font_size_below_minimum(self):
        """Test validation fails for font size below minimum"""
        with pytest.raises(Exception):  # Pydantic validation
            tool = OfficeDocsTool(content="Test content.", font_size=7)

    def test_font_size_above_maximum(self):
        """Test validation fails for font size above maximum"""
        with pytest.raises(Exception):  # Pydantic validation
            tool = OfficeDocsTool(content="Test content.", font_size=25)

    # Mock Mode Tests

    def test_mock_mode_enabled(self):
        """Test that mock mode returns mock results"""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeDocsTool(content="Test content.")
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True
        assert "mock.example.com" in result["result"]["document_url"]

    def test_mock_mode_disabled(self):
        """Test mock mode can be disabled"""
        os.environ["USE_MOCK_APIS"] = "false"

        # This test would actually create a document
        # For safety, we'll just verify the tool can be instantiated
        tool = OfficeDocsTool(content="Test content.")
        assert tool._should_use_mock() == False

    # Result Structure Tests

    def test_result_contains_required_fields(self):
        """Test that result contains all required fields"""
        tool = OfficeDocsTool(content="Test content.")
        result = tool.run()

        assert "success" in result
        assert "result" in result
        assert "metadata" in result

        result_data = result["result"]
        assert "document_url" in result_data
        assert "format" in result_data
        assert "pages" in result_data
        assert "file_size" in result_data
        assert "title" in result_data
        assert "template" in result_data

    def test_mock_result_structure(self):
        """Test mock result has correct structure"""
        tool = OfficeDocsTool(
            content="Test content.", title="Test Title", template="report", output_format="pdf"
        )
        result = tool.run()

        assert result["result"]["title"] == "Test Title"
        assert result["result"]["template"] == "report"
        assert result["result"]["format"] == "pdf"
        assert isinstance(result["result"]["pages"], int)
        assert result["result"]["pages"] > 0

    # Edge Cases

    def test_very_long_content(self):
        """Test with very long content"""
        long_content = "# Long Document\n\n" + ("This is a paragraph.\n\n" * 100)
        tool = OfficeDocsTool(content=long_content)
        result = tool.run()

        assert result["success"] == True
        # Should estimate more pages
        assert result["result"]["pages"] >= 1

    def test_special_characters_in_content(self):
        """Test content with special characters"""
        tool = OfficeDocsTool(content="Special chars: © ™ ® € £ ¥ § ¶")
        result = tool.run()

        assert result["success"] == True

    def test_unicode_content(self):
        """Test content with unicode characters"""
        tool = OfficeDocsTool(content="Unicode: 你好 مرحبا Здравствуйте")
        result = tool.run()

        assert result["success"] == True

    def test_content_with_line_breaks(self):
        """Test content with various line breaks"""
        tool = OfficeDocsTool(content="Line 1\n\nLine 2\n\n\nLine 3")
        result = tool.run()

        assert result["success"] == True

    # Integration Tests

    def test_all_templates(self):
        """Test all available templates"""
        templates = ["report", "proposal", "memo", "letter", "blank"]

        for template in templates:
            tool = OfficeDocsTool(
                content=f"# {template.title()}\n\nContent for {template}.",
                template=template,
                title=f"{template.title()} Document",
            )
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["template"] == template

    def test_all_fonts(self):
        """Test all available fonts"""
        fonts = ["Calibri", "Arial", "Times New Roman", "Georgia", "Verdana"]

        for font in fonts:
            tool = OfficeDocsTool(content="Test content.", font_name=font)
            result = tool.run()

            assert result["success"] == True

    def test_all_output_formats(self):
        """Test all output formats"""
        formats = ["docx", "pdf", "both"]

        for fmt in formats:
            tool = OfficeDocsTool(content="Test content.", output_format=fmt)
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["format"] == fmt

    # Method Tests

    def test_execute_method(self):
        """Test _execute method directly"""
        tool = OfficeDocsTool(content="Test content.")
        result = tool._execute()

        assert result["success"] == True

    def test_validate_parameters_method(self):
        """Test _validate_basic_parameters method (works in mock mode)"""
        tool = OfficeDocsTool(content="Valid content.")
        # Should not raise exception for basic validation
        tool._validate_basic_parameters()

    def test_should_use_mock_method(self):
        """Test _should_use_mock method"""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = OfficeDocsTool(content="Test")
        assert tool._should_use_mock() == True

        os.environ["USE_MOCK_APIS"] = "false"
        tool2 = OfficeDocsTool(content="Test")
        assert tool2._should_use_mock() == False

    def test_generate_mock_results_method(self):
        """Test _generate_mock_results method"""
        tool = OfficeDocsTool(content="Test", title="Mock Test", output_format="pdf")
        result = tool._generate_mock_results()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True
        assert result["result"]["title"] == "Mock Test"
        assert result["result"]["format"] == "pdf"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
