"""
Unit tests for the WebsiteBuilder tool.
"""

import pytest
import os
from website_builder import WebsiteBuilder


class TestWebsiteBuilder:
    """Test suite for WebsiteBuilder tool."""

    def setup_method(self):
        """Set up test environment before each test."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_basic_website_creation(self):
        """Test creating a basic website with default settings."""
        tool = WebsiteBuilder(website_purpose="A portfolio website for a software developer")
        result = tool.run()

        assert result["success"] == True
        assert "website_url" in result
        assert "pages_created" in result
        assert len(result["pages_created"]) == 1
        assert result["framework_used"] == "tailwind"
        assert "preview_url" in result
        assert "download_url" in result

    def test_multi_page_website(self):
        """Test creating a multi-page website."""
        tool = WebsiteBuilder(
            website_purpose="A business website for a consulting company", num_pages=5
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["pages_created"]) == 5
        assert "index" in result["pages_created"]

    def test_custom_style_and_framework(self):
        """Test creating website with custom style and framework."""
        tool = WebsiteBuilder(
            website_purpose="A professional website for a law firm",
            num_pages=3,
            style="professional",
            framework="bootstrap",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["framework_used"] == "bootstrap"
        assert result["metadata"]["style"] == "professional"

    def test_with_contact_form(self):
        """Test creating website with contact form."""
        tool = WebsiteBuilder(
            website_purpose="A business website needing customer contact",
            num_pages=3,
            include_contact_form=True,
        )
        result = tool.run()

        assert result["success"] == True
        assert "contact" in result["pages_created"]
        assert "contact_form" in result["metadata"]["features"]

    def test_with_blog(self):
        """Test creating website with blog section."""
        tool = WebsiteBuilder(
            website_purpose="A personal website with blog", num_pages=4, include_blog=True
        )
        result = tool.run()

        assert result["success"] == True
        assert "blog" in result["pages_created"]
        assert "blog" in result["metadata"]["features"]

    def test_color_scheme_validation(self):
        """Test color scheme validation."""
        # Valid 6-digit hex
        tool = WebsiteBuilder(website_purpose="Testing color validation", color_scheme="#FF5733")
        result = tool.run()
        assert result["success"] == True

        # Valid 3-digit hex
        tool = WebsiteBuilder(website_purpose="Testing color validation", color_scheme="#F73")
        result = tool.run()
        assert result["success"] == True

    def test_all_features_enabled(self):
        """Test creating website with all features enabled."""
        tool = WebsiteBuilder(
            website_purpose="A comprehensive website with all features",
            num_pages=6,
            style="modern",
            color_scheme="#3B82F6",
            include_contact_form=True,
            include_blog=True,
            responsive=True,
            framework="tailwind",
            include_animations=True,
            seo_optimized=True,
            accessibility=True,
        )
        result = tool.run()

        assert result["success"] == True
        features = result["metadata"]["features"]
        assert "responsive" in features
        assert "contact_form" in features
        assert "blog" in features
        assert "animations" in features
        assert "seo" in features
        assert "accessibility" in features

    def test_minimal_website(self):
        """Test creating minimal website with vanilla CSS."""
        tool = WebsiteBuilder(
            website_purpose="A minimal landing page",
            num_pages=1,
            style="minimal",
            framework="vanilla",
            include_animations=False,
            responsive=True,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["framework_used"] == "vanilla"
        assert result["metadata"]["style"] == "minimal"
        assert "animations" not in result["metadata"]["features"]

    def test_html_sample_generation(self):
        """Test that mock mode generates HTML sample."""
        tool = WebsiteBuilder(
            website_purpose="Testing HTML sample generation", seo_optimized=True, accessibility=True
        )
        result = tool.run()

        assert result["success"] == True
        assert "html_sample" in result["metadata"]
        html = result["metadata"]["html_sample"]
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "meta" in html.lower()
        assert "role=" in html  # Accessibility attributes

    # Validation tests

    def test_validation_empty_purpose(self):
        """Test validation fails for empty purpose."""
        with pytest.raises(Exception):
            tool = WebsiteBuilder(website_purpose="   ")
            tool.run()

    def test_validation_short_purpose(self):
        """Test validation fails for too-short purpose."""
        with pytest.raises(Exception):
            tool = WebsiteBuilder(website_purpose="short")
            tool.run()

    def test_validation_num_pages_too_low(self):
        """Test validation fails for num_pages < 1."""
        with pytest.raises(Exception):
            tool = WebsiteBuilder(website_purpose="Testing page count validation", num_pages=0)
            tool.run()

    def test_validation_num_pages_too_high(self):
        """Test validation fails for num_pages > 10."""
        with pytest.raises(Exception):
            tool = WebsiteBuilder(website_purpose="Testing page count validation", num_pages=15)
            tool.run()

    def test_validation_invalid_color_no_hash(self):
        """Test validation fails for color without #."""
        with pytest.raises(Exception):
            tool = WebsiteBuilder(website_purpose="Testing color validation", color_scheme="FF5733")
            tool.run()

    def test_validation_invalid_color_wrong_length(self):
        """Test validation fails for color with wrong length."""
        with pytest.raises(Exception):
            tool = WebsiteBuilder(website_purpose="Testing color validation", color_scheme="#FF57")
            tool.run()

    def test_validation_invalid_color_not_hex(self):
        """Test validation fails for color with non-hex characters."""
        with pytest.raises(Exception):
            tool = WebsiteBuilder(
                website_purpose="Testing color validation", color_scheme="#GGGGGG"
            )
            tool.run()

    # Different style tests

    def test_modern_style(self):
        """Test modern style website."""
        tool = WebsiteBuilder(website_purpose="A modern tech startup website", style="modern")
        result = tool.run()
        assert result["success"] == True
        assert result["metadata"]["style"] == "modern"

    def test_creative_style(self):
        """Test creative style website."""
        tool = WebsiteBuilder(website_purpose="A creative agency portfolio", style="creative")
        result = tool.run()
        assert result["success"] == True
        assert result["metadata"]["style"] == "creative"

    def test_corporate_style(self):
        """Test corporate style website."""
        tool = WebsiteBuilder(website_purpose="A corporate enterprise website", style="corporate")
        result = tool.run()
        assert result["success"] == True
        assert result["metadata"]["style"] == "corporate"

    # Framework tests

    def test_tailwind_framework(self):
        """Test website with Tailwind CSS."""
        tool = WebsiteBuilder(website_purpose="Testing Tailwind framework", framework="tailwind")
        result = tool.run()
        assert result["success"] == True
        assert result["framework_used"] == "tailwind"

    def test_bootstrap_framework(self):
        """Test website with Bootstrap."""
        tool = WebsiteBuilder(website_purpose="Testing Bootstrap framework", framework="bootstrap")
        result = tool.run()
        assert result["success"] == True
        assert result["framework_used"] == "bootstrap"

    def test_vanilla_framework(self):
        """Test website with vanilla CSS."""
        tool = WebsiteBuilder(website_purpose="Testing vanilla CSS", framework="vanilla")
        result = tool.run()
        assert result["success"] == True
        assert result["framework_used"] == "vanilla"

    # Page name generation tests

    def test_portfolio_page_names(self):
        """Test page names for portfolio websites."""
        tool = WebsiteBuilder(
            website_purpose="A portfolio website for a software developer", num_pages=4
        )
        result = tool.run()
        pages = result["pages_created"]
        assert "index" in pages
        # Should include portfolio-related pages

    def test_business_page_names(self):
        """Test page names for business websites."""
        tool = WebsiteBuilder(
            website_purpose="A business website for a consulting company", num_pages=4
        )
        result = tool.run()
        pages = result["pages_created"]
        assert "index" in pages
        # Should include business-related pages

    def test_metadata_completeness(self):
        """Test that all metadata fields are present."""
        tool = WebsiteBuilder(website_purpose="Testing metadata completeness")
        result = tool.run()

        assert result["success"] == True
        assert "metadata" in result
        metadata = result["metadata"]
        assert "tool_name" in metadata
        assert "style" in metadata
        assert "num_pages" in metadata
        assert "features" in metadata
        assert "generation_time" in metadata
        assert "mock_mode" in metadata
        assert metadata["tool_name"] == "website_builder"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
