# Google Slides Tool

Create and modify Google Slides presentations using the Google Slides API v1.

## Overview

The `GoogleSlides` tool enables AI agents to:
- Create new Google Slides presentations
- Modify existing presentations by adding slides
- Support multiple slide layouts (title, title_and_body, section_header, two_columns, blank)
- Insert text content, images, and speaker notes
- Apply themes to presentations
- Share presentations with specific users

## Installation

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Configuration

Set the `GOOGLE_SLIDES_CREDENTIALS` environment variable with your Google API credentials:

```bash
export GOOGLE_SLIDES_CREDENTIALS='{
  "token": "your-access-token",
  "refresh_token": "your-refresh-token",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret"
}'
```

### Getting Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Google Slides API and Google Drive API
4. Create OAuth 2.0 credentials
5. Download the credentials JSON
6. Use OAuth flow to obtain access token and refresh token

## Usage

### Create a New Presentation

```python
from tools.communication.google_slides import GoogleSlides

tool = GoogleSlides(
    mode="create",
    title="Q4 Sales Report",
    slides=[
        {
            "layout": "title",
            "title": "Q4 Sales Report",
            "subtitle": "2024 Performance Overview"
        },
        {
            "layout": "title_and_body",
            "title": "Key Metrics",
            "content": "Revenue: $10M (+25%)\nCustomers: 5,000 (+40%)"
        }
    ],
    theme="modern",
    share_with=["team@example.com"]
)

result = tool.run()
print(f"Presentation URL: {result['result']['url']}")
```

### Modify Existing Presentation

```python
tool = GoogleSlides(
    mode="modify",
    presentation_id="1abc123def456",
    slides=[
        {
            "layout": "title_and_body",
            "title": "Additional Insights",
            "content": "New analysis and findings"
        }
    ]
)

result = tool.run()
print(f"Added {result['result']['slides_added']} slides")
```

### Available Slide Layouts

1. **title**: Title slide with title and subtitle
   ```python
   {
       "layout": "title",
       "title": "Presentation Title",
       "subtitle": "Subtitle text"
   }
   ```

2. **title_and_body**: Title with body content
   ```python
   {
       "layout": "title_and_body",
       "title": "Slide Title",
       "content": "Body content\nSupports multiple lines"
   }
   ```

3. **section_header**: Section divider
   ```python
   {
       "layout": "section_header",
       "title": "Section Name"
   }
   ```

4. **two_columns**: Two-column layout
   ```python
   {
       "layout": "two_columns",
       "title": "Comparison",
       "left_content": "Left column text",
       "right_content": "Right column text"
   }
   ```

5. **blank**: Empty slide for custom content
   ```python
   {
       "layout": "blank"
   }
   ```

### Adding Images

```python
{
    "layout": "title_and_body",
    "title": "Product Overview",
    "content": "Description text",
    "image_url": "https://example.com/product.jpg"
}
```

### Adding Speaker Notes

```python
{
    "layout": "title_and_body",
    "title": "Talking Points",
    "content": "Main content",
    "notes": "Remember to mention quarterly growth"
}
```

### Available Themes

- `default`: Standard Google Slides theme
- `simple`: Clean white background
- `modern`: Light blue professional theme
- `colorful`: Warm tones with accent colors

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mode` | string | Yes | "create" or "modify" |
| `slides` | list | Yes | List of slide definitions |
| `title` | string | Conditional | Required for create mode |
| `presentation_id` | string | Conditional | Required for modify mode |
| `theme` | string | No | Theme name (default: "default") |
| `share_with` | list | No | Email addresses to share with |

## Return Value

```python
{
    "success": True,
    "result": {
        "presentation_id": "1abc123def456",
        "url": "https://docs.google.com/presentation/d/1abc123def456/edit",
        "title": "Presentation Title",
        "slide_count": 5,
        "slides": [
            {"slide_id": "slide_1"},
            {"slide_id": "slide_2"}
        ],
        "theme_applied": "modern",
        "shared_with": ["team@example.com"],
        "created_at": "2024-11-22T10:30:00.000000",
        "mode": "create"
    },
    "metadata": {
        "tool_name": "google_slides",
        "mock_mode": False
    }
}
```

## Error Handling

The tool validates:
- Mode-specific requirements (title for create, presentation_id for modify)
- Slide structure and layout types
- Required fields for each layout type
- Email address formats for sharing
- Credential availability

Common errors:
- `ValidationError`: Invalid parameters or slide definitions
- `AuthenticationError`: Missing or invalid credentials
- `APIError`: Google API call failures

## Testing

### Run Tests

```bash
# Run all tests
pytest tools/communication/google_slides/test_google_slides.py -v

# Run specific test
pytest tools/communication/google_slides/test_google_slides.py::TestGoogleSlides::test_create_presentation_basic -v
```

### Run Built-in Test Block

```bash
cd tools/communication/google_slides
python google_slides.py
```

This will run 8 comprehensive tests in mock mode.

## Mock Mode

Enable mock mode for testing without API calls:

```bash
export USE_MOCK_APIS=true
```

Mock mode returns realistic sample data without making actual API requests.

## Examples

### Business Report Presentation

```python
tool = GoogleSlides(
    mode="create",
    title="Monthly Business Review",
    slides=[
        {
            "layout": "title",
            "title": "Monthly Business Review",
            "subtitle": "November 2024"
        },
        {
            "layout": "section_header",
            "title": "Financial Performance"
        },
        {
            "layout": "title_and_body",
            "title": "Revenue",
            "content": "Total: $2.5M\nGrowth: +15% MoM\nForecast: On track",
            "image_url": "https://charts.example.com/revenue.png"
        },
        {
            "layout": "two_columns",
            "title": "Strengths & Opportunities",
            "left_content": "Strengths:\n- Strong sales\n- New customers\n- Product quality",
            "right_content": "Opportunities:\n- Market expansion\n- New features\n- Partnerships"
        },
        {
            "layout": "title_and_body",
            "title": "Next Steps",
            "content": "1. Launch marketing campaign\n2. Hire sales team\n3. Product roadmap review",
            "notes": "Schedule follow-up meeting for next week"
        }
    ],
    theme="modern",
    share_with=["exec@company.com", "team@company.com"]
)

result = tool.run()
```

### Training Presentation

```python
tool = GoogleSlides(
    mode="create",
    title="Employee Onboarding",
    slides=[
        {
            "layout": "title",
            "title": "Welcome to the Team!",
            "subtitle": "New Employee Orientation"
        },
        {
            "layout": "title_and_body",
            "title": "Company Mission",
            "content": "Our mission is to empower people through technology"
        },
        {
            "layout": "section_header",
            "title": "Getting Started"
        },
        {
            "layout": "two_columns",
            "title": "First Week Checklist",
            "left_content": "Day 1-2:\n- Setup accounts\n- Meet the team\n- Office tour",
            "right_content": "Day 3-5:\n- Training sessions\n- Shadow colleagues\n- First project"
        }
    ],
    theme="colorful"
)

result = tool.run()
```

### Modify Existing Presentation

```python
# Add slides to existing presentation
tool = GoogleSlides(
    mode="modify",
    presentation_id="existing-presentation-id",
    slides=[
        {
            "layout": "section_header",
            "title": "Appendix"
        },
        {
            "layout": "title_and_body",
            "title": "Additional Resources",
            "content": "Documentation: docs.example.com\nSupport: support@example.com"
        }
    ]
)

result = tool.run()
```

## Limitations

- Slide layouts are predefined (cannot create fully custom layouts)
- Theme application is simplified (advanced theming requires manual setup)
- Image positioning is automatic (cannot specify exact coordinates)
- Sharing requires Google Drive API permissions
- Cannot delete or reorder existing slides (modify mode only adds slides)

## Best Practices

1. **Validation**: Always validate slide content before creation
2. **Mock Testing**: Test workflows in mock mode first
3. **Error Handling**: Handle API errors gracefully
4. **Sharing**: Only share with necessary recipients
5. **Credentials**: Rotate credentials regularly
6. **Content Length**: Keep text content concise for readability

## Security

- Never commit credentials to version control
- Use environment variables for sensitive data
- Rotate API tokens regularly
- Limit sharing to necessary users
- Use service accounts for automation

## Support

For issues or questions:
- Check error messages for validation details
- Review Google Slides API documentation
- Verify credentials are properly configured
- Test in mock mode to isolate issues

## License

Part of AgentSwarm Tools Framework - See main repository for license details.
