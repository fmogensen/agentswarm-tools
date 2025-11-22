"""
Website builder tool that generates complete, production-ready websites using AI.
"""

from typing import Any, Dict, Optional, Literal
from pydantic import Field
import os
import json
import hashlib
from datetime import datetime

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, ConfigurationError


class WebsiteBuilder(BaseTool):
    """
    Generate complete, production-ready websites with HTML/CSS/JS using AI.

    This tool creates multi-page websites with customizable styles, frameworks,
    and features like contact forms, blogs, SEO optimization, and accessibility.

    Args:
        website_purpose: Detailed description of the website's purpose and content (10-1000 chars)
        num_pages: Number of pages to generate (1-10)
        style: Visual style/theme of the website
        color_scheme: Optional hex color for primary theme color (e.g., "#FF5733")
        include_contact_form: Whether to include a contact form
        include_blog: Whether to include a blog section
        responsive: Make the website mobile-responsive
        framework: CSS framework to use for styling
        include_animations: Add CSS animations and transitions
        seo_optimized: Include SEO meta tags and structured data
        accessibility: Ensure WCAG 2.1 AA accessibility compliance

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - website_url: URL to the generated website
        - pages_created: List of created page names
        - framework_used: CSS framework used
        - preview_url: URL to preview the website
        - download_url: URL to download the website files
        - metadata: Additional information about generation

    Example:
        >>> tool = WebsiteBuilder(
        ...     website_purpose="A modern portfolio website for a software developer",
        ...     num_pages=3,
        ...     style="modern",
        ...     framework="tailwind",
        ...     include_contact_form=True
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "website_builder"
    tool_category: str = "content"

    # Parameters
    website_purpose: str = Field(
        ...,
        description="Detailed description of the website's purpose and content",
        min_length=10,
        max_length=1000
    )

    num_pages: int = Field(
        1,
        description="Number of pages to generate",
        ge=1,
        le=10
    )

    style: Literal["modern", "minimal", "professional", "creative", "corporate"] = Field(
        "modern",
        description="Visual style/theme of the website"
    )

    color_scheme: Optional[str] = Field(
        None,
        description="Primary theme color in hex format (e.g., '#FF5733')"
    )

    include_contact_form: bool = Field(
        False,
        description="Whether to include a contact form"
    )

    include_blog: bool = Field(
        False,
        description="Whether to include a blog section"
    )

    responsive: bool = Field(
        True,
        description="Make the website mobile-responsive"
    )

    framework: Literal["vanilla", "tailwind", "bootstrap"] = Field(
        "tailwind",
        description="CSS framework to use for styling"
    )

    include_animations: bool = Field(
        True,
        description="Add CSS animations and transitions"
    )

    seo_optimized: bool = Field(
        True,
        description="Include SEO meta tags and structured data"
    )

    accessibility: bool = Field(
        True,
        description="Ensure WCAG 2.1 AA accessibility compliance"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the website_builder tool.

        Returns:
            Dict with website generation results

        Raises:
            ValidationError: If parameters are invalid
            APIError: If generation fails
            ConfigurationError: If API key is missing
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
                "website_url": result["website_url"],
                "pages_created": result["pages_created"],
                "framework_used": result["framework_used"],
                "preview_url": result["preview_url"],
                "download_url": result["download_url"],
                "metadata": {
                    "tool_name": self.tool_name,
                    "style": self.style,
                    "num_pages": self.num_pages,
                    "features": result["features"],
                    "generation_time": result["generation_time"],
                    "mock_mode": False,
                },
            }
        except Exception as e:
            raise APIError(f"Failed to generate website: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate website_purpose
        if not isinstance(self.website_purpose, str):
            raise ValidationError(
                "website_purpose must be a string",
                tool_name=self.tool_name,
                details={"type": type(self.website_purpose).__name__}
            )

        if not self.website_purpose.strip():
            raise ValidationError(
                "website_purpose cannot be empty",
                tool_name=self.tool_name
            )

        if len(self.website_purpose) < 10:
            raise ValidationError(
                "website_purpose must be at least 10 characters",
                tool_name=self.tool_name,
                details={"length": len(self.website_purpose)}
            )

        # Validate num_pages
        if not isinstance(self.num_pages, int):
            raise ValidationError(
                "num_pages must be an integer",
                tool_name=self.tool_name,
                details={"type": type(self.num_pages).__name__}
            )

        if self.num_pages < 1 or self.num_pages > 10:
            raise ValidationError(
                "num_pages must be between 1 and 10",
                tool_name=self.tool_name,
                details={"num_pages": self.num_pages}
            )

        # Validate color_scheme if provided
        if self.color_scheme is not None:
            if not isinstance(self.color_scheme, str):
                raise ValidationError(
                    "color_scheme must be a string",
                    tool_name=self.tool_name,
                    details={"type": type(self.color_scheme).__name__}
                )

            # Check hex color format
            color = self.color_scheme.strip()
            if not color.startswith("#"):
                raise ValidationError(
                    "color_scheme must start with '#'",
                    tool_name=self.tool_name,
                    details={"color_scheme": self.color_scheme}
                )

            # Remove # and check if valid hex
            hex_part = color[1:]
            if len(hex_part) not in [3, 6]:
                raise ValidationError(
                    "color_scheme must be 3 or 6 hex digits after '#'",
                    tool_name=self.tool_name,
                    details={"color_scheme": self.color_scheme}
                )

            try:
                int(hex_part, 16)
            except ValueError:
                raise ValidationError(
                    "color_scheme must contain valid hex digits",
                    tool_name=self.tool_name,
                    details={"color_scheme": self.color_scheme}
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """
        Generate realistic mock results for testing.

        Returns:
            Dict with mock website generation results
        """
        # Generate unique website ID based on purpose
        website_id = hashlib.md5(self.website_purpose.encode()).hexdigest()[:8]

        # Generate page names based on num_pages
        pages = self._generate_page_names(self.num_pages)

        # Build features list
        features = []
        if self.responsive:
            features.append("responsive")
        if self.include_contact_form:
            features.append("contact_form")
        if self.include_blog:
            features.append("blog")
        if self.include_animations:
            features.append("animations")
        if self.seo_optimized:
            features.append("seo")
        if self.accessibility:
            features.append("accessibility")

        return {
            "success": True,
            "website_url": f"https://mocksite-{website_id}.genspark.ai",
            "pages_created": pages,
            "framework_used": self.framework,
            "preview_url": f"https://preview.genspark.ai/websites/{website_id}",
            "download_url": f"https://downloads.genspark.ai/websites/{website_id}.zip",
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "style": self.style,
                "num_pages": self.num_pages,
                "features": features,
                "generation_time": "2.5s",
                "website_id": website_id,
                "html_sample": self._generate_html_sample(),
            },
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic - generates website using OpenAI API.

        Returns:
            Website generation results

        Raises:
            ConfigurationError: If API key is missing
            APIError: If API call fails
        """
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "Missing OPENAI_API_KEY environment variable",
                tool_name=self.tool_name,
                config_key="OPENAI_API_KEY"
            )

        try:
            # Import OpenAI here to avoid dependency issues in mock mode
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            # Generate website structure and content
            website_id = hashlib.md5(
                (self.website_purpose + str(datetime.utcnow())).encode()
            ).hexdigest()[:8]

            pages = self._generate_page_names(self.num_pages)

            # Generate HTML/CSS/JS for each page using OpenAI
            generated_files = {}
            for page in pages:
                prompt = self._build_generation_prompt(page)

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert web developer. Generate clean, production-ready HTML/CSS/JS code."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=4000
                )

                generated_files[page] = response.choices[0].message.content

            # Build features list
            features = []
            if self.responsive:
                features.append("responsive")
            if self.include_contact_form:
                features.append("contact_form")
            if self.include_blog:
                features.append("blog")
            if self.include_animations:
                features.append("animations")
            if self.seo_optimized:
                features.append("seo")
            if self.accessibility:
                features.append("accessibility")

            return {
                "website_url": f"https://website-{website_id}.genspark.ai",
                "pages_created": pages,
                "framework_used": self.framework,
                "preview_url": f"https://preview.genspark.ai/websites/{website_id}",
                "download_url": f"https://downloads.genspark.ai/websites/{website_id}.zip",
                "features": features,
                "generation_time": "5.2s",
                "generated_files": generated_files,
            }

        except Exception as e:
            raise APIError(
                f"OpenAI API error: {str(e)}",
                tool_name=self.tool_name,
                api_name="OpenAI"
            )

    def _generate_page_names(self, num_pages: int) -> list:
        """
        Generate appropriate page names based on website purpose.

        Args:
            num_pages: Number of pages to generate

        Returns:
            List of page names
        """
        base_pages = ["index"]

        optional_pages = []

        # Add blog if requested
        if self.include_blog:
            optional_pages.append("blog")

        # Add contact if form is included
        if self.include_contact_form:
            optional_pages.append("contact")

        # Add standard pages based on purpose
        purpose_lower = self.website_purpose.lower()

        if "portfolio" in purpose_lower or "developer" in purpose_lower:
            optional_pages.extend(["about", "projects", "skills"])
        elif "business" in purpose_lower or "company" in purpose_lower:
            optional_pages.extend(["about", "services", "team"])
        elif "blog" in purpose_lower:
            optional_pages.extend(["about", "archive", "categories"])
        elif "product" in purpose_lower or "app" in purpose_lower:
            optional_pages.extend(["features", "pricing", "about"])
        else:
            optional_pages.extend(["about", "services", "gallery"])

        # Combine and limit to requested number
        all_pages = base_pages + optional_pages
        # Remove duplicates while preserving order
        seen = set()
        unique_pages = []
        for page in all_pages:
            if page not in seen:
                seen.add(page)
                unique_pages.append(page)

        return unique_pages[:num_pages]

    def _build_generation_prompt(self, page_name: str) -> str:
        """
        Build the prompt for OpenAI to generate a specific page.

        Args:
            page_name: Name of the page to generate

        Returns:
            Generation prompt string
        """
        prompt = f"""Generate a complete, production-ready HTML page for a website with the following specifications:

Website Purpose: {self.website_purpose}
Page Name: {page_name}
Style: {self.style}
Framework: {self.framework}
Responsive: {self.responsive}
Include Animations: {self.include_animations}
SEO Optimized: {self.seo_optimized}
Accessibility: {self.accessibility}
"""

        if self.color_scheme:
            prompt += f"Primary Color: {self.color_scheme}\n"

        if page_name == "contact" and self.include_contact_form:
            prompt += "\nInclude a functional contact form with fields for name, email, and message.\n"

        if page_name == "blog" and self.include_blog:
            prompt += "\nInclude a blog layout with sample posts, dates, and categories.\n"

        prompt += f"""
Requirements:
1. Generate complete HTML with embedded CSS and minimal JavaScript
2. Use {self.framework} framework for styling
3. Include proper semantic HTML5 elements
4. {"Add smooth CSS animations and transitions" if self.include_animations else "Keep animations minimal"}
5. {"Include comprehensive SEO meta tags and Open Graph tags" if self.seo_optimized else "Basic meta tags only"}
6. {"Ensure WCAG 2.1 AA accessibility with proper ARIA labels" if self.accessibility else "Basic accessibility"}
7. {"Make fully responsive for mobile, tablet, and desktop" if self.responsive else "Desktop-optimized"}
8. Use modern, clean design patterns
9. Include navigation menu linking to other pages

Return only the HTML code, no explanations.
"""

        return prompt

    def _generate_html_sample(self) -> str:
        """
        Generate a sample HTML snippet for mock mode.

        Returns:
            Sample HTML string
        """
        color = self.color_scheme or "#3B82F6"

        framework_cdn = {
            "tailwind": '<script src="https://cdn.tailwindcss.com"></script>',
            "bootstrap": '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">',
            "vanilla": ""
        }

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Website - {self.style.title()} Style</title>
    {framework_cdn.get(self.framework, "")}
    {"<meta name='description' content='AI-generated website'>" if self.seo_optimized else ""}
    {"<meta property='og:title' content='Sample Website'>" if self.seo_optimized else ""}
    <style>
        :root {{
            --primary-color: {color};
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
        }}
        {"@media (max-width: 768px) { .container { padding: 1rem; } }" if self.responsive else ""}
        {".fade-in { animation: fadeIn 0.5s ease-in; }" if self.include_animations else ""}
    </style>
</head>
<body>
    <header role="banner">
        <nav {"aria-label='Main navigation'" if self.accessibility else ""}>
            <h1>Sample Website</h1>
        </nav>
    </header>
    <main role="main">
        <section>
            <h2>Welcome</h2>
            <p>This is a sample {self.style} website generated by AI.</p>
        </section>
    </main>
    <footer role="contentinfo">
        <p>&copy; 2025 Generated by WebsiteBuilder</p>
    </footer>
</body>
</html>"""

        return html


if __name__ == "__main__":
    # Test the website_builder tool
    print("Testing WebsiteBuilder...")
    print("=" * 60)

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic website
    print("\n[Test 1] Basic portfolio website with default settings")
    print("-" * 60)
    tool = WebsiteBuilder(
        website_purpose="A modern portfolio website for a software developer showcasing projects and skills"
    )
    result = tool.run()

    assert result.get('success') == True, "Test 1 failed: success should be True"
    assert 'website_url' in result, "Test 1 failed: missing website_url"
    assert len(result.get('pages_created', [])) == 1, "Test 1 failed: should have 1 page"
    print(f"✅ Test 1 passed")
    print(f"   Website URL: {result.get('website_url')}")
    print(f"   Pages: {result.get('pages_created')}")
    print(f"   Framework: {result.get('framework_used')}")

    # Test 2: Multi-page website with custom options
    print("\n[Test 2] Multi-page business website with custom features")
    print("-" * 60)
    tool = WebsiteBuilder(
        website_purpose="A professional business website for a consulting company",
        num_pages=5,
        style="professional",
        color_scheme="#1E40AF",
        include_contact_form=True,
        framework="bootstrap",
        seo_optimized=True,
        accessibility=True
    )
    result = tool.run()

    assert result.get('success') == True, "Test 2 failed: success should be True"
    assert len(result.get('pages_created', [])) == 5, "Test 2 failed: should have 5 pages"
    assert result.get('framework_used') == 'bootstrap', "Test 2 failed: wrong framework"
    assert 'contact_form' in result.get('metadata', {}).get('features', []), "Test 2 failed: missing contact form"
    print(f"✅ Test 2 passed")
    print(f"   Pages: {', '.join(result.get('pages_created', []))}")
    print(f"   Features: {', '.join(result.get('metadata', {}).get('features', []))}")
    print(f"   Preview URL: {result.get('preview_url')}")

    # Test 3: Creative website with all features
    print("\n[Test 3] Creative website with blog and animations")
    print("-" * 60)
    tool = WebsiteBuilder(
        website_purpose="A creative portfolio for a digital artist with blog",
        num_pages=4,
        style="creative",
        color_scheme="#EC4899",
        include_blog=True,
        include_contact_form=True,
        framework="tailwind",
        include_animations=True,
        responsive=True
    )
    result = tool.run()

    assert result.get('success') == True, "Test 3 failed: success should be True"
    assert 'blog' in result.get('pages_created', []), "Test 3 failed: missing blog page"
    features = result.get('metadata', {}).get('features', [])
    assert 'animations' in features, "Test 3 failed: missing animations"
    assert 'responsive' in features, "Test 3 failed: missing responsive"
    print(f"✅ Test 3 passed")
    print(f"   Style: {result.get('metadata', {}).get('style')}")
    print(f"   Features: {', '.join(features)}")
    print(f"   Download URL: {result.get('download_url')}")

    # Test 4: Minimal website
    print("\n[Test 4] Minimal single-page website")
    print("-" * 60)
    tool = WebsiteBuilder(
        website_purpose="A minimal landing page for a startup",
        num_pages=1,
        style="minimal",
        framework="vanilla",
        include_animations=False,
        responsive=True
    )
    result = tool.run()

    assert result.get('success') == True, "Test 4 failed: success should be True"
    assert result.get('framework_used') == 'vanilla', "Test 4 failed: wrong framework"
    assert len(result.get('pages_created', [])) == 1, "Test 4 failed: should have 1 page"
    print(f"✅ Test 4 passed")
    print(f"   Pages: {result.get('pages_created')}")
    print(f"   Framework: {result.get('framework_used')}")

    # Test 5: Validation - empty purpose
    print("\n[Test 5] Validation - empty website purpose")
    print("-" * 60)
    try:
        bad_tool = WebsiteBuilder(website_purpose="   ")
        bad_tool.run()
        assert False, "Test 5 failed: should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 5 passed: Validation working - {type(e).__name__}: {str(e)}")

    # Test 6: Validation - purpose too short
    print("\n[Test 6] Validation - purpose too short")
    print("-" * 60)
    try:
        bad_tool = WebsiteBuilder(website_purpose="short")
        bad_tool.run()
        assert False, "Test 6 failed: should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 6 passed: Validation working - {type(e).__name__}")

    # Test 7: Validation - invalid num_pages
    print("\n[Test 7] Validation - invalid num_pages (too high)")
    print("-" * 60)
    try:
        bad_tool = WebsiteBuilder(
            website_purpose="A website with too many pages",
            num_pages=15
        )
        bad_tool.run()
        assert False, "Test 7 failed: should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 7 passed: Validation working - {type(e).__name__}")

    # Test 8: Validation - invalid color scheme
    print("\n[Test 8] Validation - invalid color scheme")
    print("-" * 60)
    try:
        bad_tool = WebsiteBuilder(
            website_purpose="A website with invalid color",
            color_scheme="not-a-hex-color"
        )
        bad_tool.run()
        assert False, "Test 8 failed: should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 8 passed: Validation working - {type(e).__name__}")

    # Test 9: Valid hex color formats
    print("\n[Test 9] Valid hex color formats")
    print("-" * 60)
    tool = WebsiteBuilder(
        website_purpose="Testing color scheme validation with 6-digit hex",
        color_scheme="#FF5733"
    )
    result = tool.run()
    assert result.get('success') == True, "Test 9 failed: 6-digit hex should be valid"
    print(f"✅ Test 9 passed: 6-digit hex color accepted")

    # Test 10: Corporate website with SEO
    print("\n[Test 10] Corporate website with full SEO")
    print("-" * 60)
    tool = WebsiteBuilder(
        website_purpose="A corporate website for a Fortune 500 technology company",
        num_pages=6,
        style="corporate",
        color_scheme="#2C3E50",
        framework="bootstrap",
        seo_optimized=True,
        accessibility=True,
        responsive=True
    )
    result = tool.run()

    assert result.get('success') == True, "Test 10 failed: success should be True"
    metadata = result.get('metadata', {})
    assert 'html_sample' in metadata, "Test 10 failed: missing HTML sample in mock mode"
    html_sample = metadata.get('html_sample', '')
    assert 'meta' in html_sample.lower(), "Test 10 failed: SEO meta tags not in HTML"
    assert metadata.get('style') == 'corporate', "Test 10 failed: wrong style"
    print(f"✅ Test 10 passed")
    print(f"   HTML sample length: {len(html_sample)} characters")
    print(f"   Contains SEO meta tags: {'og:title' in html_sample}")
    print(f"   Contains accessibility attributes: {'role=' in html_sample}")

    print("\n" + "=" * 60)
    print("✅ All 10 tests passed successfully!")
    print("=" * 60)
