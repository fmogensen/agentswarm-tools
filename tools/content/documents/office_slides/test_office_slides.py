"""
Unit tests for OfficeSlidesTool.
Tests all functionality including parameter validation, mock mode, and presentation generation.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from tools.document_creation.office_slides.office_slides import OfficeSlidesTool
from shared.errors import ValidationError, ConfigurationError


class TestOfficeSlidesValidation:
    """Test parameter validation."""

    def test_empty_slides_list_raises_error(self):
        """Test that empty slides list raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSlidesTool(slides=[])
            tool.run()
        assert "cannot be empty" in str(exc_info.value)

    def test_invalid_theme_raises_error(self):
        """Test that invalid theme raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSlidesTool(
                slides=[{"title": "Test", "content": ["Content"], "layout": "content"}],
                theme="invalid_theme"
            )
            tool.run()
        assert "Invalid theme" in str(exc_info.value)

    def test_invalid_output_format_raises_error(self):
        """Test that invalid output format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSlidesTool(
                slides=[{"title": "Test", "content": ["Content"], "layout": "content"}],
                output_format="invalid_format"
            )
            tool.run()
        assert "Invalid output_format" in str(exc_info.value)

    def test_slide_missing_title_raises_error(self):
        """Test that slide missing title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSlidesTool(
                slides=[{"content": ["Content"], "layout": "content"}]
            )
            tool.run()
        assert "missing 'title'" in str(exc_info.value)

    def test_slide_missing_content_raises_error(self):
        """Test that slide missing content raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSlidesTool(
                slides=[{"title": "Test", "layout": "content"}]
            )
            tool.run()
        assert "missing 'content'" in str(exc_info.value)

    def test_slide_missing_layout_raises_error(self):
        """Test that slide missing layout raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSlidesTool(
                slides=[{"title": "Test", "content": ["Content"]}]
            )
            tool.run()
        assert "missing 'layout'" in str(exc_info.value)

    def test_invalid_layout_raises_error(self):
        """Test that invalid layout raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSlidesTool(
                slides=[{"title": "Test", "content": ["Content"], "layout": "invalid_layout"}]
            )
            tool.run()
        assert "invalid layout" in str(exc_info.value)

    def test_title_slide_missing_title_raises_error(self):
        """Test that title_slide missing title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSlidesTool(
                slides=[{"title": "Test", "content": ["Content"], "layout": "content"}],
                title_slide={"subtitle": "Subtitle only"}
            )
            tool.run()
        assert "title_slide missing 'title'" in str(exc_info.value)


class TestOfficeSlidesToolMockMode:
    """Test mock mode functionality."""

    def test_mock_mode_basic_presentation(self):
        """Test basic presentation generation in mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[
                {"title": "Slide 1", "content": ["Point A", "Point B"], "layout": "title_content"},
                {"title": "Slide 2", "content": ["Data"], "layout": "content"}
            ],
            theme="modern",
            title_slide={"title": "Test Presentation", "subtitle": "2025"}
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["slides"] == 3  # 1 title + 2 content
        assert result["result"]["format"] == "pptx"
        assert "presentation_url" in result["result"]
        assert result["metadata"]["mock_mode"] is True

    def test_mock_mode_pdf_format(self):
        """Test PDF format in mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[{"title": "Test", "content": ["Content"], "layout": "content"}],
            output_format="pdf"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["format"] == "pdf"

    def test_mock_mode_no_title_slide(self):
        """Test presentation without title slide in mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[
                {"title": "Slide 1", "content": ["Content"], "layout": "content"},
                {"title": "Slide 2", "content": ["More"], "layout": "content"}
            ]
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["slides"] == 2  # No title slide

    def test_mock_mode_with_charts(self):
        """Test presentation with charts in mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[{"title": "Data", "content": ["Chart here"], "layout": "content"}],
            charts=[{"type": "bar", "data": [1, 2, 3]}]
        )
        result = tool.run()

        assert result["success"] is True

    def test_mock_mode_all_themes(self):
        """Test all theme options in mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

        themes = ["modern", "classic", "minimal", "corporate"]

        for theme in themes:
            tool = OfficeSlidesTool(
                slides=[{"title": "Test", "content": ["Content"], "layout": "content"}],
                theme=theme
            )
            result = tool.run()

            assert result["success"] is True
            assert "presentation_url" in result["result"]

    def test_mock_mode_all_layouts(self):
        """Test all layout types in mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"

        layouts = ["title_content", "content", "two_column", "blank"]

        for layout in layouts:
            tool = OfficeSlidesTool(
                slides=[{"title": "Test", "content": ["Content"], "layout": layout}]
            )
            result = tool.run()

            assert result["success"] is True


class TestOfficeSlidesRealMode:
    """Test real presentation generation (requires python-pptx)."""

    def test_real_mode_basic_presentation(self):
        """Test actual presentation generation."""
        # Skip mock mode
        os.environ["USE_MOCK_APIS"] = "false"

        tool = OfficeSlidesTool(
            slides=[
                {"title": "Introduction", "content": ["Point 1", "Point 2"], "layout": "title_content"},
                {"title": "Details", "content": ["Detail A", "Detail B"], "layout": "content"}
            ],
            theme="modern",
            title_slide={"title": "Test Report", "subtitle": "Q4 2025", "author": "Test User"}
        )

        try:
            result = tool.run()

            assert result["success"] is True
            assert result["result"]["slides"] == 3
            assert result["result"]["format"] == "pptx"
            assert "file_path" in result["result"]

            # Verify file exists
            file_path = result["result"]["file_path"]
            assert os.path.exists(file_path)
            assert file_path.endswith(".pptx")

            # Clean up
            os.remove(file_path)

        except ConfigurationError:
            pytest.skip("python-pptx not installed")

    def test_real_mode_two_column_layout(self):
        """Test two-column layout generation."""
        os.environ["USE_MOCK_APIS"] = "false"

        tool = OfficeSlidesTool(
            slides=[
                {
                    "title": "Comparison",
                    "content": ["Left 1", "Left 2", "Right 1", "Right 2"],
                    "layout": "two_column"
                }
            ],
            theme="corporate"
        )

        try:
            result = tool.run()

            assert result["success"] is True
            assert "file_path" in result["result"]

            # Clean up
            if os.path.exists(result["result"]["file_path"]):
                os.remove(result["result"]["file_path"])

        except ConfigurationError:
            pytest.skip("python-pptx not installed")

    def test_real_mode_blank_layout(self):
        """Test blank layout generation."""
        os.environ["USE_MOCK_APIS"] = "false"

        tool = OfficeSlidesTool(
            slides=[
                {"title": "Blank Slide", "content": [], "layout": "blank"}
            ]
        )

        try:
            result = tool.run()

            assert result["success"] is True

            # Clean up
            if os.path.exists(result["result"]["file_path"]):
                os.remove(result["result"]["file_path"])

        except ConfigurationError:
            pytest.skip("python-pptx not installed")

    def test_real_mode_content_as_string(self):
        """Test content as string instead of list."""
        os.environ["USE_MOCK_APIS"] = "false"

        tool = OfficeSlidesTool(
            slides=[
                {"title": "String Content", "content": "This is a single paragraph.", "layout": "content"}
            ]
        )

        try:
            result = tool.run()

            assert result["success"] is True

            # Clean up
            if os.path.exists(result["result"]["file_path"]):
                os.remove(result["result"]["file_path"])

        except ConfigurationError:
            pytest.skip("python-pptx not installed")

    def test_real_mode_minimal_theme(self):
        """Test minimal theme."""
        os.environ["USE_MOCK_APIS"] = "false"

        tool = OfficeSlidesTool(
            slides=[{"title": "Minimal", "content": ["Clean design"], "layout": "content"}],
            theme="minimal"
        )

        try:
            result = tool.run()

            assert result["success"] is True

            # Clean up
            if os.path.exists(result["result"]["file_path"]):
                os.remove(result["result"]["file_path"])

        except ConfigurationError:
            pytest.skip("python-pptx not installed")


class TestOfficeSlidesEdgeCases:
    """Test edge cases and error handling."""

    def test_single_slide_presentation(self):
        """Test presentation with only one slide."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[{"title": "Only Slide", "content": ["Content"], "layout": "content"}]
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["slides"] == 1

    def test_large_presentation(self):
        """Test presentation with many slides."""
        os.environ["USE_MOCK_APIS"] = "true"

        slides = [
            {"title": f"Slide {i}", "content": [f"Content {i}"], "layout": "content"}
            for i in range(20)
        ]

        tool = OfficeSlidesTool(slides=slides)
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["slides"] == 20

    def test_title_slide_with_all_fields(self):
        """Test title slide with all optional fields."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[{"title": "Content", "content": ["Data"], "layout": "content"}],
            title_slide={
                "title": "Complete Title Slide",
                "subtitle": "Subtitle Information",
                "author": "John Doe"
            }
        )
        result = tool.run()

        assert result["success"] is True

    def test_title_slide_minimal(self):
        """Test title slide with only required title."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[{"title": "Content", "content": ["Data"], "layout": "content"}],
            title_slide={"title": "Just Title"}
        )
        result = tool.run()

        assert result["success"] is True

    def test_empty_content_list(self):
        """Test slide with empty content list."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[{"title": "Empty Content", "content": [], "layout": "content"}]
        )
        result = tool.run()

        assert result["success"] is True


class TestOfficeSlidesIntegration:
    """Integration tests."""

    def test_complete_business_presentation(self):
        """Test complete business presentation with multiple slide types."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[
                {
                    "title": "Executive Summary",
                    "content": ["Revenue up 25%", "New markets entered", "Team expanded"],
                    "layout": "title_content"
                },
                {
                    "title": "Key Metrics",
                    "content": ["Q1: $1M", "Q2: $1.2M", "Q3: $1.5M", "Q4: $2M"],
                    "layout": "two_column"
                },
                {
                    "title": "Detailed Analysis",
                    "content": "This section provides in-depth analysis of our performance...",
                    "layout": "content"
                },
                {
                    "title": "Thank You",
                    "content": [],
                    "layout": "blank"
                }
            ],
            theme="corporate",
            title_slide={
                "title": "Q4 Business Review",
                "subtitle": "2025 Annual Report",
                "author": "Finance Team"
            },
            output_format="pptx"
        )

        result = tool.run()

        assert result["success"] is True
        assert result["result"]["slides"] == 5  # 1 title + 4 content
        assert result["result"]["format"] == "pptx"

    def test_educational_presentation(self):
        """Test educational presentation."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSlidesTool(
            slides=[
                {
                    "title": "Introduction to Python",
                    "content": ["High-level language", "Easy to learn", "Versatile"],
                    "layout": "title_content"
                },
                {
                    "title": "Basic Syntax",
                    "content": ["Variables", "Functions", "Classes", "Modules"],
                    "layout": "content"
                }
            ],
            theme="minimal",
            title_slide={"title": "Python Programming 101", "author": "Prof. Smith"}
        )

        result = tool.run()

        assert result["success"] is True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
