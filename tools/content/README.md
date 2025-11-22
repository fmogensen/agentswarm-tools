# Content Tools

Tools for creating documents and working with web content.

## Subcategories

### Documents (`documents/`)
Create and manage various document types.

**Tools:**
- `create_agent` - Create specialized agents (docs, slides, sheets, podcasts, research, websites, video editing)
- `office_docs` - Create and edit Word documents
- `office_sheets` - Create and edit spreadsheets
- `office_slides` - Create and edit presentations

### Web (`web/`)
Interact with and extract content from web pages.

**Tools:**
- `crawler` - Crawl and extract content from websites
- `summarize_large_document` - Summarize long web documents
- `url_metadata` - Extract metadata from URLs
- `webpage_capture_screen` - Capture screenshots of web pages
- `resource_discovery` - Discover and catalog web resources
- `website_builder` - Build and deploy websites

## Category Identifier

All tools in this category have:
```python
tool_category: str = "content"
```

## Usage Examples

### Create a document:
```python
from tools.content.documents.create_agent import CreateAgent

tool = CreateAgent(
    input="Create a business proposal document about AI automation"
)
result = tool.run()
```

### Crawl a website:
```python
from tools.content.web.crawler import Crawler

tool = Crawler(
    url="https://example.com",
    max_depth=2,
    extract_content=True
)
result = tool.run()
```

### Capture webpage screenshot:
```python
from tools.content.web.webpage_capture_screen import WebpageCaptureScreen

tool = WebpageCaptureScreen(
    url="https://example.com",
    viewport_width=1920,
    viewport_height=1080
)
result = tool.run()
```
