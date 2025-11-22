# Google Docs Tool

Create and modify Google Docs using the Google Docs API v1.

## Features

- **Create new documents** with title and formatted content
- **Modify existing documents** with append, replace, or insert actions
- **Format text** using markdown (headings, bold, italic)
- **Share documents** with email addresses
- **Organize documents** into Google Drive folders
- **Get shareable links** for easy access

## Installation

Requires Google API Python client:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Authentication

Set up Google Docs API credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Docs API** and **Google Drive API**
4. Create a **Service Account**
5. Download the service account JSON credentials
6. Set environment variable:

```bash
export GOOGLE_DOCS_CREDENTIALS='{"type": "service_account", "project_id": "...", ...}'
```

Or store the JSON credentials as a string in the environment variable.

## Usage

### Create New Document

```python
from tools.communication.google_docs import GoogleDocs

tool = GoogleDocs(
    mode="create",
    title="My Document",
    content="# Hello World\n\nThis is **bold** and this is *italic*."
)
result = tool.run()

print(f"Document ID: {result['result']['document_id']}")
print(f"Link: {result['result']['shareable_link']}")
```

### Modify Existing Document (Append)

```python
tool = GoogleDocs(
    mode="modify",
    document_id="abc123xyz",
    content="## New Section\n\nAppended content.",
    modify_action="append"
)
result = tool.run()
```

### Modify Document (Replace All Content)

```python
tool = GoogleDocs(
    mode="modify",
    document_id="abc123xyz",
    content="# New Title\n\nCompletely replaced content.",
    modify_action="replace"
)
result = tool.run()
```

### Modify Document (Insert at Position)

```python
tool = GoogleDocs(
    mode="modify",
    document_id="abc123xyz",
    content="Inserted at beginning.",
    modify_action="insert",
    insert_index=1
)
result = tool.run()
```

### Create and Share Document

```python
tool = GoogleDocs(
    mode="create",
    title="Shared Document",
    content="Content to share with team.",
    share_with=["user1@example.com", "user2@example.com"]
)
result = tool.run()
```

### Create Document in Folder

```python
tool = GoogleDocs(
    mode="create",
    title="Organized Document",
    content="This goes in a specific folder.",
    folder_id="your-folder-id-here"
)
result = tool.run()
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mode` | str | Yes | - | Operation mode: "create" or "modify" |
| `content` | str | Yes | - | Document content (supports markdown) |
| `title` | str | Conditional | None | Document title (required for create mode) |
| `document_id` | str | Conditional | None | Document ID (required for modify mode) |
| `share_with` | List[str] | No | None | Email addresses to share with |
| `folder_id` | str | No | None | Google Drive folder ID for new documents |
| `modify_action` | str | No | "append" | Modify action: "append", "replace", or "insert" |
| `insert_index` | int | No | 1 | Position for insert action (1 = beginning) |

## Markdown Support

The tool supports basic markdown formatting:

### Headings

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

### Text Formatting

```markdown
**bold text**
*italic text*
```

### Example

```python
content = """
# Main Title

This is a paragraph with **bold** and *italic* text.

## Section 1

Content here.

### Subsection

More content.
"""

tool = GoogleDocs(mode="create", title="Formatted Doc", content=content)
```

## Response Structure

### Create Mode Response

```python
{
    "success": True,
    "result": {
        "document_id": "abc123xyz",
        "title": "My Document",
        "shareable_link": "https://docs.google.com/document/d/abc123xyz/edit",
        "shared_with": ["user@example.com"],
        "folder_id": "folder123"
    },
    "metadata": {
        "tool_name": "google_docs",
        "mode": "create"
    }
}
```

### Modify Mode Response

```python
{
    "success": True,
    "result": {
        "document_id": "abc123xyz",
        "title": "Existing Document",
        "shareable_link": "https://docs.google.com/document/d/abc123xyz/edit",
        "modify_action": "append",
        "shared_with": []
    },
    "metadata": {
        "tool_name": "google_docs",
        "mode": "modify"
    }
}
```

## Error Handling

The tool raises specific exceptions for different error cases:

### ValidationError

- Invalid mode (not "create" or "modify")
- Empty content
- Missing title (create mode)
- Missing document_id (modify mode)
- Invalid modify_action
- Invalid email addresses

### AuthenticationError

- Missing GOOGLE_DOCS_CREDENTIALS
- Invalid credentials format
- Expired credentials

### APIError

- Document not found
- API communication failures
- Permission denied

## Testing

### Run Tests

```bash
# Run all tests
pytest tools/communication/google_docs/test_google_docs.py -v

# Run specific test
pytest tools/communication/google_docs/test_google_docs.py::TestGoogleDocs::test_create_document_success -v

# Run with coverage
pytest tools/communication/google_docs/test_google_docs.py --cov=tools.communication.google_docs
```

### Test with Mock Mode

```bash
# Enable mock mode
export USE_MOCK_APIS=true

# Run the tool directly
python tools/communication/google_docs/google_docs.py
```

### Run Built-in Tests

The tool includes a comprehensive test block:

```bash
cd tools/communication/google_docs
python google_docs.py
```

This runs 8 test cases covering:
- Create new document
- Modify with append
- Modify with replace
- Modify with insert
- Validation errors
- Email validation
- Folder support

## Examples

### Example 1: Meeting Notes

```python
meeting_notes = """
# Team Meeting - 2024-01-15

## Attendees
- Alice
- Bob
- Charlie

## Agenda
1. Project updates
2. Q1 planning
3. Action items

## Discussion

### Project Updates
Alice shared progress on **Project Alpha**. The team is on track for the Q1 deadline.

### Q1 Planning
Bob presented the *roadmap* for next quarter.

## Action Items
- [ ] Alice: Finalize design docs
- [ ] Bob: Schedule client meeting
- [ ] Charlie: Review budget
"""

tool = GoogleDocs(
    mode="create",
    title="Team Meeting Notes - Jan 15",
    content=meeting_notes,
    share_with=["alice@company.com", "bob@company.com", "charlie@company.com"]
)
result = tool.run()
```

### Example 2: Report Generation

```python
report = f"""
# Monthly Report - {current_month}

## Executive Summary
This month saw **significant growth** in user engagement.

## Key Metrics
- Users: {user_count}
- Revenue: ${revenue}
- NPS: {nps_score}

## Highlights
{highlights_section}

## Next Steps
{next_steps}
"""

tool = GoogleDocs(
    mode="create",
    title=f"Monthly Report - {current_month}",
    content=report,
    folder_id="reports-folder-id",
    share_with=["manager@company.com"]
)
```

### Example 3: Collaborative Document

```python
# Create initial document
tool = GoogleDocs(
    mode="create",
    title="Brainstorming Session",
    content="# Ideas\n\nAdd your ideas below:",
    share_with=["team@company.com"]
)
result = tool.run()
doc_id = result["result"]["document_id"]

# Later, append new ideas
tool = GoogleDocs(
    mode="modify",
    document_id=doc_id,
    content="\n## New Idea\nDescription here.",
    modify_action="append"
)
```

### Example 4: Template Update

```python
# Replace entire document with updated template
new_template = """
# Project Template

## Overview
[Add project overview]

## Requirements
[List requirements]

## Timeline
[Add milestones]
"""

tool = GoogleDocs(
    mode="modify",
    document_id="template-doc-id",
    content=new_template,
    modify_action="replace"
)
```

## Permissions

The service account needs these Google API scopes:
- `https://www.googleapis.com/auth/documents` - Read and write Google Docs
- `https://www.googleapis.com/auth/drive.file` - Manage files in Google Drive

## Limitations

- Markdown support is basic (headings, bold, italic)
- Lists, links, and tables are not yet supported
- Images and complex formatting require direct API calls
- Service account must have access to documents it modifies
- Folder operations require Drive API permissions

## Best Practices

1. **Use descriptive titles** for better organization
2. **Share selectively** - only with necessary collaborators
3. **Organize with folders** to keep documents structured
4. **Test in mock mode** before using real API
5. **Handle errors gracefully** in production code
6. **Cache document IDs** for future modifications

## Troubleshooting

### "Missing GOOGLE_DOCS_CREDENTIALS"
Set the environment variable with your service account JSON.

### "Document not found"
Ensure the document_id is correct and the service account has access.

### "Permission denied"
The service account needs access to the document. Share it with the service account email.

### "Invalid email address"
Verify email addresses are in correct format: `user@domain.com`

## License

Part of AgentSwarm Tools Framework
