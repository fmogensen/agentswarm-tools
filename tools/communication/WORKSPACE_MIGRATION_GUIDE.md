# Google Workspace Tools Migration Guide

## Overview

This guide helps you migrate from the individual Google Workspace tools (GoogleDocs, GoogleSheets, GoogleSlides) to the new `UnifiedGoogleWorkspace` tool.

## Quick Start

### TL;DR

- **Old tools still work** - No immediate action required
- **Deprecation warnings** - Old tools emit warnings pointing to UnifiedGoogleWorkspace
- **Easy migration** - Just add `workspace_type` parameter and update import

### Why Migrate?

1. **Future-proof**: Old tools will be removed in a future version
2. **Consistency**: Unified error handling and validation
3. **Maintainability**: Single tool for all workspace operations
4. **New features**: Future enhancements will only apply to unified tool

## Migration Examples

### Google Docs Migration

#### Old Code (GoogleDocs)

```python
from tools.communication.google_docs import GoogleDocs

# Create document
tool = GoogleDocs(
    mode="create",
    title="My Document",
    content="# Hello World\n\nThis is **bold** text.",
    share_with=["user@example.com"],
    folder_id="folder123"
)
result = tool.run()
```

#### New Code (UnifiedGoogleWorkspace)

```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

# Create document
tool = UnifiedGoogleWorkspace(
    workspace_type="docs",  # ← Add this parameter
    mode="create",
    title="My Document",
    content="# Hello World\n\nThis is **bold** text.",
    share_with=["user@example.com"],
    folder_id="folder123"
)
result = tool.run()
```

#### Modify Document Example

**Old:**
```python
tool = GoogleDocs(
    mode="modify",
    document_id="abc123",
    content="New content to append",
    modify_action="append"
)
result = tool.run()
```

**New:**
```python
tool = UnifiedGoogleWorkspace(
    workspace_type="docs",
    mode="modify",
    document_id="abc123",
    content="New content to append",
    modify_action="append"
)
result = tool.run()
```

### Google Sheets Migration

#### Old Code (GoogleSheets)

```python
from tools.communication.google_sheets import GoogleSheets

# Create spreadsheet
tool = GoogleSheets(
    mode="create",
    title="Sales Report Q4",
    data=[
        ["Product", "Sales"],
        ["Widget A", 1000],
        ["Widget B", 1500]
    ],
    sheet_name="Q4 Data",
    formulas={"C1": "=SUM(B2:B3)"},
    formatting={"bold_header": True},
    share_with=["user@example.com"]
)
result = tool.run()
```

#### New Code (UnifiedGoogleWorkspace)

```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

# Create spreadsheet
tool = UnifiedGoogleWorkspace(
    workspace_type="sheets",  # ← Add this parameter
    mode="create",
    title="Sales Report Q4",
    data=[
        ["Product", "Sales"],
        ["Widget A", 1000],
        ["Widget B", 1500]
    ],
    sheet_name="Q4 Data",
    formulas={"C1": "=SUM(B2:B3)"},
    formatting={"bold_header": True},
    share_with=["user@example.com"]
)
result = tool.run()
```

#### Modify Spreadsheet Example

**Old:**
```python
tool = GoogleSheets(
    mode="modify",
    spreadsheet_id="1ABC123XYZ",
    data=[["Updated", "Data"]],
    sheet_name="Sheet1"
)
result = tool.run()
```

**New:**
```python
tool = UnifiedGoogleWorkspace(
    workspace_type="sheets",
    mode="modify",
    spreadsheet_id="1ABC123XYZ",
    data=[["Updated", "Data"]],
    sheet_name="Sheet1"
)
result = tool.run()
```

### Google Slides Migration

#### Old Code (GoogleSlides)

```python
from tools.communication.google_slides import GoogleSlides

# Create presentation
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
            "content": "Revenue: $10M (+25%)"
        }
    ],
    theme="modern",
    share_with=["team@example.com"]
)
result = tool.run()
```

#### New Code (UnifiedGoogleWorkspace)

```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

# Create presentation
tool = UnifiedGoogleWorkspace(
    workspace_type="slides",  # ← Add this parameter
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
            "content": "Revenue: $10M (+25%)"
        }
    ],
    theme="modern",
    share_with=["team@example.com"]
)
result = tool.run()
```

#### Modify Presentation Example

**Old:**
```python
tool = GoogleSlides(
    mode="modify",
    presentation_id="1abc123def456",
    slides=[
        {
            "layout": "title_and_body",
            "title": "Additional Insights",
            "content": "Market analysis"
        }
    ]
)
result = tool.run()
```

**New:**
```python
tool = UnifiedGoogleWorkspace(
    workspace_type="slides",
    mode="modify",
    presentation_id="1abc123def456",
    slides=[
        {
            "layout": "title_and_body",
            "title": "Additional Insights",
            "content": "Market analysis"
        }
    ]
)
result = tool.run()
```

## Parameter Mapping

### All Parameters Remain the Same

The only addition is the `workspace_type` parameter. All other parameters work identically:

| Old Tool | workspace_type | All Other Parameters |
|----------|----------------|---------------------|
| GoogleDocs | `"docs"` | Unchanged |
| GoogleSheets | `"sheets"` | Unchanged |
| GoogleSlides | `"slides"` | Unchanged |

### Parameter Reference

#### Common Parameters (All Workspace Types)

```python
workspace_type: "docs" | "sheets" | "slides"  # NEW - Required
mode: "create" | "modify"                      # Required
title: str                                     # Required for create mode
share_with: List[str]                          # Optional
```

#### Docs-Specific Parameters

```python
document_id: str         # Required for modify mode
content: str             # Required - supports markdown
modify_action: str       # "append" | "replace" | "insert" (default: "append")
insert_index: int        # Position for insert (default: 1)
folder_id: str           # Optional - Google Drive folder ID
```

#### Sheets-Specific Parameters

```python
spreadsheet_id: str                # Required for modify mode
data: List[List[Any]]              # Required - rows and columns
sheet_name: str                    # Worksheet name (default: "Sheet1")
formulas: Dict[str, str]           # Cell formulas (e.g., {"A1": "=SUM(B1:B10)"})
formatting: Dict[str, Any]         # Formatting options
```

#### Slides-Specific Parameters

```python
presentation_id: str               # Required for modify mode
slides: List[Dict[str, Any]]       # Required - slide definitions
theme: str                         # "default" | "simple" | "modern" | "colorful"
```

## Return Value Compatibility

### No Changes to Return Values

The unified tool returns the same structure as the old tools:

```python
{
    "success": True,
    "result": {
        # Workspace-specific fields (same as before)
        "document_id": "...",          # For docs
        "spreadsheet_id": "...",       # For sheets
        "presentation_id": "...",      # For slides
        # ... other fields unchanged
    },
    "metadata": {
        "tool_name": "unified_google_workspace",  # Changed
        "workspace_type": "docs",                  # NEW
        "mode": "create"
    }
}
```

### Using with Deprecated Tools

When using old tools, the return value includes deprecation metadata:

```python
{
    "success": True,
    "result": { ... },
    "metadata": {
        "tool_name": "google_docs",              # Original tool name
        "deprecated": True,                       # NEW
        "delegate_to": "unified_google_workspace" # NEW
    }
}
```

## Credential Configuration

### No Changes Required

Credentials work exactly the same way:

#### Workspace-Specific Credentials (Preferred)

```bash
# Docs
export GOOGLE_DOCS_CREDENTIALS='{"type": "service_account", ...}'

# Sheets
export GOOGLE_SHEETS_CREDENTIALS='{"type": "service_account", ...}'

# Slides
export GOOGLE_SLIDES_CREDENTIALS='{"type": "service_account", ...}'
```

#### Generic Workspace Credentials (Fallback)

```bash
# Works for all workspace types
export GOOGLE_WORKSPACE_CREDENTIALS='{"type": "service_account", ...}'
```

The unified tool checks workspace-specific credentials first, then falls back to generic credentials.

## Error Handling

### Same Error Types

All error types remain the same:

```python
from shared.errors import ValidationError, APIError, AuthenticationError

try:
    tool = UnifiedGoogleWorkspace(
        workspace_type="docs",
        mode="create",
        # ... parameters
    )
    result = tool.run()
except ValidationError as e:
    # Same validation errors as before
    print(f"Invalid input: {e}")
except AuthenticationError as e:
    # Same auth errors as before
    print(f"Auth failed: {e}")
except APIError as e:
    # Same API errors as before
    print(f"API call failed: {e}")
```

## Testing

### Mock Mode Works Identically

```python
import os

# Enable mock mode
os.environ["USE_MOCK_APIS"] = "true"

# Works for all workspace types
tool = UnifiedGoogleWorkspace(
    workspace_type="docs",
    mode="create",
    title="Test",
    content="Test content"
)
result = tool.run()

assert result["success"] == True
assert result["metadata"]["mock_mode"] == True
```

## Migration Checklist

### For Each Tool Usage

- [ ] Identify which old tool is being used (GoogleDocs/GoogleSheets/GoogleSlides)
- [ ] Add import for UnifiedGoogleWorkspace
- [ ] Add `workspace_type` parameter ("docs"/"sheets"/"slides")
- [ ] Keep all other parameters unchanged
- [ ] Test in mock mode first
- [ ] Test with real API
- [ ] Remove deprecation warning imports if present

### Example Pull Request Description

```markdown
## Migrate to UnifiedGoogleWorkspace

**Changes:**
- Replaced GoogleDocs with UnifiedGoogleWorkspace(workspace_type="docs")
- Replaced GoogleSheets with UnifiedGoogleWorkspace(workspace_type="sheets")
- Replaced GoogleSlides with UnifiedGoogleWorkspace(workspace_type="slides")

**Testing:**
- [x] All existing tests pass
- [x] Mock mode tests pass
- [x] Integration tests pass

**Backward Compatibility:**
- No breaking changes
- All parameters work identically
- Return values unchanged
```

## Common Migration Patterns

### Pattern 1: Simple Replace

Find:
```python
from tools.communication.google_docs import GoogleDocs
tool = GoogleDocs(
```

Replace with:
```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace
tool = UnifiedGoogleWorkspace(
    workspace_type="docs",
```

### Pattern 2: Conditional Workspace Type

If you're dynamically choosing workspace type:

```python
# Before (multiple tool classes)
tool_map = {
    "docs": GoogleDocs,
    "sheets": GoogleSheets,
    "slides": GoogleSlides
}
tool_class = tool_map[workspace_type]
tool = tool_class(mode="create", ...)

# After (single tool class)
tool = UnifiedGoogleWorkspace(
    workspace_type=workspace_type,  # "docs", "sheets", or "slides"
    mode="create",
    ...
)
```

### Pattern 3: Batch Processing

```python
# Process multiple workspace types in a loop
workspace_configs = [
    {"workspace_type": "docs", "title": "Doc1", "content": "Content1"},
    {"workspace_type": "sheets", "title": "Sheet1", "data": [["A", "B"]]},
    {"workspace_type": "slides", "title": "Slides1", "slides": [{"layout": "blank"}]},
]

for config in workspace_configs:
    tool = UnifiedGoogleWorkspace(mode="create", **config)
    result = tool.run()
    print(f"Created {config['workspace_type']}: {result['result']}")
```

## FAQs

### Q: Do I need to migrate immediately?

**A:** No. The old tools still work and will continue to work. However, they emit deprecation warnings to encourage migration.

### Q: Will old tools be removed?

**A:** Yes, in a future major version. You'll have plenty of notice (at least 2 major versions).

### Q: Are there any breaking changes?

**A:** No. All parameters and return values work identically. The only addition is the `workspace_type` parameter.

### Q: What if I encounter issues during migration?

**A:** The old tools still work as fallback. If you encounter issues with the unified tool, you can continue using the old tools and report the issue.

### Q: Can I mix old and new tools in the same codebase?

**A:** Yes. Both work simultaneously during the transition period.

### Q: Are there performance differences?

**A:** No. Both make the same API calls with the same logic. Performance is identical.

### Q: Do I need to change my tests?

**A:** Only the import and tool instantiation. All assertions on return values remain the same.

## Support

### Need Help?

- Check existing code examples in `test_unified_google_workspace.py`
- Review `WORKSPACE_CONSOLIDATION.md` for technical details
- Open an issue with migration questions

### Found a Bug?

- Test with the old tool to confirm it's not a regression
- Open an issue with:
  - Old tool code (working)
  - New tool code (not working)
  - Expected vs actual behavior
  - Full error message

## Timeline

| Version | Status | Notes |
|---------|--------|-------|
| **Current** | Old tools work, emit warnings | Both old and new tools available |
| **X+1** | Old tools deprecated in docs | Documentation updated to show only new tool |
| **X+2** | Old tools removed from docs | Only shown in migration guide |
| **X+3** | Old tools removed from codebase | Must use unified tool |

*Replace X with current major version*
