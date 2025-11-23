"""
Unit tests for GoogleSlides tool
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from google_slides import GoogleSlides


class TestGoogleSlides:
    """Test suite for GoogleSlides tool"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        os.environ["USE_MOCK_APIS"] = "true"
        yield
        # Cleanup
        if "GOOGLE_SLIDES_CREDENTIALS" in os.environ:
            del os.environ["GOOGLE_SLIDES_CREDENTIALS"]

    def test_create_presentation_basic(self):
        """Test creating a basic presentation"""
        tool = GoogleSlides(
            mode="create",
            title="Test Presentation",
            slides=[{"layout": "title", "title": "Welcome", "subtitle": "Introduction"}],
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["title"] == "Test Presentation"
        assert result["result"]["slide_count"] == 1
        assert result["result"]["mode"] == "create"
        assert "presentation_id" in result["result"]
        assert "url" in result["result"]

    def test_create_presentation_multiple_slides(self):
        """Test creating presentation with multiple slides"""
        tool = GoogleSlides(
            mode="create",
            title="Multi-Slide Presentation",
            slides=[
                {"layout": "title", "title": "Title Slide", "subtitle": "Subtitle"},
                {"layout": "title_and_body", "title": "Content", "content": "Body text"},
                {"layout": "section_header", "title": "Section"},
                {
                    "layout": "two_columns",
                    "title": "Columns",
                    "left_content": "Left",
                    "right_content": "Right",
                },
                {"layout": "blank"},
            ],
            theme="modern",
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["slide_count"] == 5
        assert result["result"]["theme_applied"] == "modern"
        assert len(result["result"]["slides"]) == 5

    def test_create_presentation_with_sharing(self):
        """Test creating presentation with sharing"""
        tool = GoogleSlides(
            mode="create",
            title="Shared Presentation",
            slides=[{"layout": "blank"}],
            share_with=["user1@example.com", "user2@example.com"],
        )

        result = tool.run()

        assert result["success"] == True
        assert len(result["result"]["shared_with"]) == 2
        assert "user1@example.com" in result["result"]["shared_with"]
        assert "user2@example.com" in result["result"]["shared_with"]

    def test_create_presentation_with_image(self):
        """Test creating presentation with image"""
        tool = GoogleSlides(
            mode="create",
            title="Presentation with Image",
            slides=[
                {
                    "layout": "title_and_body",
                    "title": "Image Slide",
                    "content": "Description",
                    "image_url": "https://example.com/image.jpg",
                }
            ],
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["slides"][0]["object_count"] >= 2  # Title, content, image

    def test_create_presentation_with_notes(self):
        """Test creating presentation with speaker notes"""
        tool = GoogleSlides(
            mode="create",
            title="Presentation with Notes",
            slides=[
                {
                    "layout": "title_and_body",
                    "title": "Slide with Notes",
                    "content": "Main content",
                    "notes": "Speaker notes here",
                }
            ],
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["slide_count"] == 1

    def test_modify_presentation(self):
        """Test modifying existing presentation"""
        tool = GoogleSlides(
            mode="modify",
            presentation_id="existing-presentation-id",
            slides=[{"layout": "title_and_body", "title": "New Slide", "content": "Added content"}],
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["mode"] == "modify"
        assert result["result"]["presentation_id"] == "existing-presentation-id"
        assert result["result"]["slide_count"] == 1

    def test_all_themes(self):
        """Test all available themes"""
        themes = ["default", "simple", "modern", "colorful"]

        for theme in themes:
            tool = GoogleSlides(
                mode="create",
                title=f"Presentation with {theme} theme",
                slides=[{"layout": "blank"}],
                theme=theme,
            )

            result = tool.run()

            assert result["success"] == True
            assert result["result"]["theme_applied"] == theme

    def test_all_layouts(self):
        """Test all available slide layouts"""
        layouts = [
            {"layout": "title", "title": "Title", "subtitle": "Subtitle"},
            {"layout": "title_and_body", "title": "Title", "content": "Body"},
            {"layout": "section_header", "title": "Section"},
            {
                "layout": "two_columns",
                "title": "Columns",
                "left_content": "L",
                "right_content": "R",
            },
            {"layout": "blank"},
        ]

        tool = GoogleSlides(mode="create", title="All Layouts", slides=layouts)

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["slide_count"] == 5

    # Validation Tests

    def test_validation_missing_title_create_mode(self):
        """Test validation fails when title missing in create mode"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(mode="create", slides=[{"layout": "blank"}])
            tool.run()

        assert "title is required" in str(exc_info.value).lower()

    def test_validation_missing_presentation_id_modify_mode(self):
        """Test validation fails when presentation_id missing in modify mode"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(mode="modify", slides=[{"layout": "blank"}])
            tool.run()

        assert "presentation_id is required" in str(exc_info.value).lower()

    def test_validation_empty_slides(self):
        """Test validation fails when slides list is empty"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(mode="create", title="Test", slides=[])
            tool.run()

        assert "at least one slide" in str(exc_info.value).lower()

    def test_validation_missing_layout(self):
        """Test validation fails when slide missing layout"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(mode="create", title="Test", slides=[{"title": "No Layout"}])
            tool.run()

        assert "missing required 'layout' field" in str(exc_info.value).lower()

    def test_validation_invalid_layout(self):
        """Test validation fails for invalid layout"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(mode="create", title="Test", slides=[{"layout": "invalid_layout"}])
            tool.run()

        assert "invalid layout" in str(exc_info.value).lower()

    def test_validation_title_layout_missing_title(self):
        """Test validation fails when title layout missing title field"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(
                mode="create", title="Test", slides=[{"layout": "title", "subtitle": "Sub"}]
            )
            tool.run()

        assert "requires 'title' field" in str(exc_info.value).lower()

    def test_validation_title_and_body_missing_title(self):
        """Test validation fails when title_and_body layout missing title"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(
                mode="create",
                title="Test",
                slides=[{"layout": "title_and_body", "content": "Content"}],
            )
            tool.run()

        assert "requires 'title' field" in str(exc_info.value).lower()

    def test_validation_two_columns_missing_content(self):
        """Test validation fails when two_columns missing required content"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(
                mode="create", title="Test", slides=[{"layout": "two_columns", "title": "Title"}]
            )
            tool.run()

        assert "requires 'left_content' and 'right_content'" in str(exc_info.value).lower()

    def test_validation_invalid_email(self):
        """Test validation fails for invalid email"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(
                mode="create",
                title="Test",
                slides=[{"layout": "blank"}],
                share_with=["invalid-email"],
            )
            tool.run()

        assert "invalid email" in str(exc_info.value).lower()

    def test_validation_invalid_mode(self):
        """Test validation fails for invalid mode"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(mode="invalid", title="Test", slides=[{"layout": "blank"}])

        # Pydantic validation should catch this
        assert "mode" in str(exc_info.value).lower()

    def test_validation_invalid_theme(self):
        """Test validation fails for invalid theme"""
        with pytest.raises(Exception) as exc_info:
            tool = GoogleSlides(
                mode="create", title="Test", slides=[{"layout": "blank"}], theme="invalid_theme"
            )

        # Pydantic validation should catch this
        assert "theme" in str(exc_info.value).lower()

    # Mock Mode Tests

    def test_mock_mode_enabled(self):
        """Test that mock mode returns mock results"""
        tool = GoogleSlides(mode="create", title="Mock Test", slides=[{"layout": "blank"}])

        result = tool.run()

        assert result["metadata"]["mock_mode"] == True
        assert result["result"]["mock"] == True
        assert "mock-presentation-id" in result["result"]["presentation_id"]

    def test_mock_mode_preserves_input_data(self):
        """Test that mock mode preserves input data in results"""
        tool = GoogleSlides(
            mode="create",
            title="Test Title",
            slides=[
                {"layout": "title", "title": "Slide 1", "subtitle": "Sub"},
                {"layout": "blank"},
            ],
            theme="modern",
            share_with=["user@example.com"],
        )

        result = tool.run()

        assert result["result"]["title"] == "Test Title"
        assert result["result"]["slide_count"] == 2
        assert result["result"]["theme_applied"] == "modern"
        assert result["result"]["shared_with"] == ["user@example.com"]

    # Edge Cases

    def test_long_title(self):
        """Test with very long title"""
        long_title = "A" * 250  # Near max length

        tool = GoogleSlides(mode="create", title=long_title, slides=[{"layout": "blank"}])

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["title"] == long_title

    def test_many_slides(self):
        """Test with many slides"""
        slides = [{"layout": "blank"} for _ in range(50)]

        tool = GoogleSlides(mode="create", title="Many Slides", slides=slides)

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["slide_count"] == 50

    def test_many_share_recipients(self):
        """Test sharing with many recipients"""
        emails = [f"user{i}@example.com" for i in range(20)]

        tool = GoogleSlides(
            mode="create", title="Widely Shared", slides=[{"layout": "blank"}], share_with=emails
        )

        result = tool.run()

        assert result["success"] == True
        assert len(result["result"]["shared_with"]) == 20

    def test_unicode_content(self):
        """Test with unicode characters"""
        tool = GoogleSlides(
            mode="create",
            title="Unicode Test 日本語",
            slides=[
                {
                    "layout": "title_and_body",
                    "title": "Unicode Content 中文",
                    "content": "Emoji support: 🎉 🚀 💡",
                }
            ],
        )

        result = tool.run()

        assert result["success"] == True

    def test_special_characters(self):
        """Test with special characters"""
        tool = GoogleSlides(
            mode="create",
            title="Special & Characters <Test>",
            slides=[
                {
                    "layout": "title_and_body",
                    "title": "Title with \"quotes\" and 'apostrophes'",
                    "content": "Content with\nnewlines\tand\ttabs",
                }
            ],
        )

        result = tool.run()

        assert result["success"] == True

    def test_mixed_slide_types(self):
        """Test with various mixed slide configurations"""
        tool = GoogleSlides(
            mode="create",
            title="Mixed Slides",
            slides=[
                {"layout": "title", "title": "Start"},
                {"layout": "blank"},
                {
                    "layout": "title_and_body",
                    "title": "Content",
                    "content": "Text",
                    "image_url": "https://example.com/img.jpg",
                    "notes": "Notes",
                },
                {"layout": "section_header", "title": "Section"},
                {
                    "layout": "two_columns",
                    "title": "Cols",
                    "left_content": "L",
                    "right_content": "R",
                },
            ],
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["slide_count"] == 5


# Integration-style tests (still using mock mode)


class TestGoogleSlidesIntegration:
    """Integration-style tests for GoogleSlides tool"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        os.environ["USE_MOCK_APIS"] = "true"
        yield

    def test_create_and_share_workflow(self):
        """Test complete create and share workflow"""
        # Create presentation
        create_tool = GoogleSlides(
            mode="create",
            title="Team Update",
            slides=[
                {"layout": "title", "title": "Team Update", "subtitle": "Q4 2024"},
                {"layout": "title_and_body", "title": "Updates", "content": "Key points"},
            ],
            share_with=["team@example.com"],
        )

        create_result = create_tool.run()
        assert create_result["success"] == True

        presentation_id = create_result["result"]["presentation_id"]

        # Modify presentation
        modify_tool = GoogleSlides(
            mode="modify",
            presentation_id=presentation_id,
            slides=[{"layout": "title_and_body", "title": "Follow-up", "content": "Next steps"}],
        )

        modify_result = modify_tool.run()
        assert modify_result["success"] == True
        assert modify_result["result"]["presentation_id"] == presentation_id

    def test_full_featured_presentation(self):
        """Test creating presentation with all features"""
        tool = GoogleSlides(
            mode="create",
            title="Full Featured Presentation",
            slides=[
                {"layout": "title", "title": "Welcome", "subtitle": "Comprehensive Demo"},
                {"layout": "section_header", "title": "Section 1: Overview"},
                {
                    "layout": "title_and_body",
                    "title": "Content Slide",
                    "content": "Detailed information\nBullet points\nKey facts",
                    "notes": "Remember to emphasize the key facts",
                },
                {
                    "layout": "two_columns",
                    "title": "Comparison",
                    "left_content": "Pros:\n- Benefit 1\n- Benefit 2",
                    "right_content": "Cons:\n- Challenge 1\n- Challenge 2",
                },
                {
                    "layout": "title_and_body",
                    "title": "Visual Content",
                    "content": "Chart and diagrams below",
                    "image_url": "https://example.com/chart.png",
                },
                {"layout": "blank"},
            ],
            theme="modern",
            share_with=["stakeholder@example.com"],
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["slide_count"] == 6
        assert result["result"]["theme_applied"] == "modern"
        assert len(result["result"]["shared_with"]) == 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
