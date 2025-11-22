# Website Builder Tool

Generate complete, production-ready websites with HTML/CSS/JS using AI.

## Overview

The `WebsiteBuilder` tool creates multi-page websites with customizable styles, frameworks, and features like contact forms, blogs, SEO optimization, and accessibility compliance. It uses OpenAI's API to generate intelligent, well-structured code based on your website's purpose.

## Features

- **Multi-page generation**: Create 1-10 pages per website
- **5 visual styles**: Modern, Minimal, Professional, Creative, Corporate
- **3 CSS frameworks**: Tailwind CSS, Bootstrap, or Vanilla CSS
- **Contact forms**: Optional contact form with validation
- **Blog sections**: Built-in blog layout with posts
- **Responsive design**: Mobile-first, responsive layouts
- **SEO optimization**: Meta tags, Open Graph, structured data
- **Accessibility**: WCAG 2.1 AA compliant markup
- **Animations**: Smooth CSS transitions and effects
- **Custom colors**: Support for hex color themes

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `website_purpose` | str | Yes | - | Detailed description of the website's purpose (10-1000 chars) |
| `num_pages` | int | No | 1 | Number of pages to generate (1-10) |
| `style` | str | No | "modern" | Visual style: "modern", "minimal", "professional", "creative", "corporate" |
| `color_scheme` | str | No | None | Primary hex color (e.g., "#FF5733") |
| `include_contact_form` | bool | No | False | Include a contact form page |
| `include_blog` | bool | No | False | Include a blog section |
| `responsive` | bool | No | True | Make website mobile-responsive |
| `framework` | str | No | "tailwind" | CSS framework: "tailwind", "bootstrap", "vanilla" |
| `include_animations` | bool | No | True | Add CSS animations |
| `seo_optimized` | bool | No | True | Include SEO meta tags |
| `accessibility` | bool | No | True | Ensure WCAG 2.1 AA compliance |

## Returns

```python
{
    "success": True,
    "website_url": "https://website-abc123.genspark.ai",
    "pages_created": ["index", "about", "contact"],
    "framework_used": "tailwind",
    "preview_url": "https://preview.genspark.ai/websites/abc123",
    "download_url": "https://downloads.genspark.ai/websites/abc123.zip",
    "metadata": {
        "tool_name": "website_builder",
        "style": "modern",
        "num_pages": 3,
        "features": ["responsive", "contact_form", "animations", "seo", "accessibility"],
        "generation_time": "5.2s",
        "mock_mode": False
    }
}
```

## Usage Examples

### Basic Portfolio Website

```python
from tools.content_creation.website_builder import WebsiteBuilder

tool = WebsiteBuilder(
    website_purpose="A modern portfolio website for a software developer showcasing projects and skills"
)
result = tool.run()

print(f"Website URL: {result['website_url']}")
print(f"Pages: {result['pages_created']}")
```

### Business Website with Contact Form

```python
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

print(f"Preview: {result['preview_url']}")
print(f"Download: {result['download_url']}")
```

### Creative Portfolio with Blog

```python
tool = WebsiteBuilder(
    website_purpose="A creative portfolio for a digital artist with blog",
    num_pages=4,
    style="creative",
    color_scheme="#EC4899",
    include_blog=True,
    include_contact_form=True,
    framework="tailwind",
    include_animations=True
)
result = tool.run()

print(f"Pages: {', '.join(result['pages_created'])}")
print(f"Features: {', '.join(result['metadata']['features'])}")
```

### Minimal Landing Page

```python
tool = WebsiteBuilder(
    website_purpose="A minimal landing page for a startup product launch",
    num_pages=1,
    style="minimal",
    framework="vanilla",
    include_animations=False,
    responsive=True
)
result = tool.run()
```

## Environment Variables

```bash
# Required for production mode
OPENAI_API_KEY=sk-...

# Optional for testing
USE_MOCK_APIS=true  # Use mock mode for testing without API calls
```

## Testing

The tool includes comprehensive tests:

```bash
# Run built-in test block
python3 -m tools.content_creation.website_builder.website_builder

# Run pytest tests
pytest tools/content_creation/website_builder/test_website_builder.py -v
```

## Page Name Generation

The tool intelligently generates page names based on the website purpose:

- **Portfolio/Developer**: index, about, projects, skills, contact
- **Business/Company**: index, about, services, team, contact
- **Blog**: index, about, blog, archive, categories
- **Product/App**: index, features, pricing, about, contact
- **Default**: index, about, services, gallery, contact

## Validation

The tool validates:

- `website_purpose`: Must be 10-1000 characters, non-empty
- `num_pages`: Must be 1-10
- `color_scheme`: Must be valid hex format (#RGB or #RRGGBB)
- All parameters must be correct types

## Error Handling

```python
try:
    tool = WebsiteBuilder(
        website_purpose="My website",
        color_scheme="invalid"
    )
    result = tool.run()
except ValidationError as e:
    print(f"Validation failed: {e.message}")
except APIError as e:
    print(f"API error: {e.message}")
except ConfigurationError as e:
    print(f"Config error: {e.message}")
```

## Framework Comparison

### Tailwind CSS (Default)
- Utility-first approach
- Highly customizable
- Modern, clean output
- Fast development

### Bootstrap
- Component-based
- Pre-built components
- Wide browser support
- Professional look

### Vanilla CSS
- No dependencies
- Lightweight
- Full control
- Best for minimal sites

## Accessibility Features

When `accessibility=True`, the tool ensures:

- Semantic HTML5 elements
- ARIA labels and roles
- Proper heading hierarchy
- Alt text for images
- Keyboard navigation support
- Sufficient color contrast
- Focus indicators
- Screen reader compatibility

## SEO Features

When `seo_optimized=True`, the tool includes:

- Title and meta description tags
- Open Graph tags for social sharing
- Twitter Card metadata
- Canonical URLs
- Structured data (JSON-LD)
- Sitemap generation
- Robots meta tags
- Language declarations

## Architecture

The tool follows Agency Swarm standards:

1. **Inherits from BaseTool**: Full error handling, analytics, logging
2. **5 Required Methods**:
   - `_execute()`: Main orchestration
   - `_validate_parameters()`: Input validation
   - `_should_use_mock()`: Mock mode check
   - `_generate_mock_results()`: Realistic mock data
   - `_process()`: OpenAI API integration
3. **Pydantic Fields**: Type-safe parameters with validation
4. **Test Block**: Comprehensive `if __name__ == "__main__"` tests

## Dependencies

```python
from typing import Any, Dict, Optional, Literal
from pydantic import Field
from shared.base import BaseTool
from shared.errors import ValidationError, APIError, ConfigurationError
from openai import OpenAI  # Required for production mode
```

## License

Part of the AgentSwarm Tools Framework.

## Support

For issues or questions:
1. Check validation error messages
2. Verify OPENAI_API_KEY is set
3. Test with USE_MOCK_APIS=true first
4. Review generated HTML samples
5. Check logs for detailed error traces
