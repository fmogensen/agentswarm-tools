# Communication Tools Migration Guide

## Overview

This guide helps you migrate from deprecated Google Workspace and Google Calendar tools to their unified replacements.

**Deprecation Notice:** All tools listed below are deprecated and will be removed in **v3.0.0**. They currently work as backward compatibility wrappers.

---

## Quick Reference

### Google Workspace Tools

| Old Tool | New Tool | Workspace Type |
|----------|----------|----------------|
| `GoogleDocs` | `UnifiedGoogleWorkspace` | `workspace_type="docs"` |
| `GoogleSheets` | `UnifiedGoogleWorkspace` | `workspace_type="sheets"` |
| `GoogleSlides` | `UnifiedGoogleWorkspace` | `workspace_type="slides"` |

### Google Calendar Tools

| Old Tool | New Tool | Action |
|----------|----------|--------|
| `GoogleCalendarCreateEventDraft` | `UnifiedGoogleCalendar` | `action="create"` |
| `GoogleCalendarList` | `UnifiedGoogleCalendar` | `action="list"` |
| `GoogleCalendarUpdateEvent` | `UnifiedGoogleCalendar` | `action="update"` |
| `GoogleCalendarDeleteEvent` | `UnifiedGoogleCalendar` | `action="delete"` |

---

## Google Workspace Migration

### GoogleDocs → UnifiedGoogleWorkspace

#### Create New Document

**Before:**
```python
from tools.communication.google_docs import GoogleDocs

tool = GoogleDocs(
    mode="create",
    title="Project Proposal",
    content="# Introduction\n\nThis is a **bold** statement.",
    share_with=["team@example.com"],
    folder_id="abc123"
)
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

tool = UnifiedGoogleWorkspace(
    workspace_type="docs",
    mode="create",
    title="Project Proposal",
    content="# Introduction\n\nThis is a **bold** statement.",
    share_with=["team@example.com"],
    folder_id="abc123"
)
result = tool.run()
```

#### Modify Existing Document

**Before:**
```python
from tools.communication.google_docs import GoogleDocs

tool = GoogleDocs(
    mode="modify",
    document_id="doc123",
    content="## New Section\n\nAdditional content.",
    modify_action="append"
)
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

tool = UnifiedGoogleWorkspace(
    workspace_type="docs",
    mode="modify",
    document_id="doc123",
    content="## New Section\n\nAdditional content.",
    modify_action="append"
)
result = tool.run()
```

---

### GoogleSheets → UnifiedGoogleWorkspace

#### Create New Spreadsheet

**Before:**
```python
from tools.communication.google_sheets import GoogleSheets

tool = GoogleSheets(
    mode="create",
    title="Sales Report Q4",
    data=[
        ["Product", "Sales"],
        ["Widget A", 1000],
        ["Widget B", 1500]
    ],
    sheet_name="Sales Data",
    formulas={"C2": "=SUM(B2:B3)"},
    formatting={"bold_header": True},
    share_with=["user@example.com"]
)
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

tool = UnifiedGoogleWorkspace(
    workspace_type="sheets",
    mode="create",
    title="Sales Report Q4",
    data=[
        ["Product", "Sales"],
        ["Widget A", 1000],
        ["Widget B", 1500]
    ],
    sheet_name="Sales Data",
    formulas={"C2": "=SUM(B2:B3)"},
    formatting={"bold_header": True},
    share_with=["user@example.com"]
)
result = tool.run()
```

#### Modify Existing Spreadsheet

**Before:**
```python
from tools.communication.google_sheets import GoogleSheets

tool = GoogleSheets(
    mode="modify",
    spreadsheet_id="sheet123",
    data=[["Updated", "Data"]],
    sheet_name="Sheet1",
    formulas={"C1": "=SUM(B2:B10)"}
)
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

tool = UnifiedGoogleWorkspace(
    workspace_type="sheets",
    mode="modify",
    spreadsheet_id="sheet123",
    data=[["Updated", "Data"]],
    sheet_name="Sheet1",
    formulas={"C1": "=SUM(B2:B10)"}
)
result = tool.run()
```

---

### GoogleSlides → UnifiedGoogleWorkspace

#### Create New Presentation

**Before:**
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
            "content": "Revenue increased by 25%"
        }
    ],
    theme="modern",
    share_with=["team@example.com"]
)
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

tool = UnifiedGoogleWorkspace(
    workspace_type="slides",
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
            "content": "Revenue increased by 25%"
        }
    ],
    theme="modern",
    share_with=["team@example.com"]
)
result = tool.run()
```

#### Modify Existing Presentation

**Before:**
```python
from tools.communication.google_slides import GoogleSlides

tool = GoogleSlides(
    mode="modify",
    presentation_id="pres123",
    slides=[
        {
            "layout": "title_and_body",
            "title": "Additional Insights",
            "content": "Market analysis shows positive trends"
        }
    ]
)
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

tool = UnifiedGoogleWorkspace(
    workspace_type="slides",
    mode="modify",
    presentation_id="pres123",
    slides=[
        {
            "layout": "title_and_body",
            "title": "Additional Insights",
            "content": "Market analysis shows positive trends"
        }
    ]
)
result = tool.run()
```

---

## Google Calendar Migration

### GoogleCalendarCreateEventDraft → UnifiedGoogleCalendar

**Before:**
```python
from tools.communication.google_calendar_create_event_draft import GoogleCalendarCreateEventDraft
import json

event_data = {
    "title": "Team Meeting",
    "start_time": "2025-01-15T10:00:00Z",
    "end_time": "2025-01-15T11:00:00Z",
    "description": "Weekly sync",
    "location": "Conference Room A"
}

tool = GoogleCalendarCreateEventDraft(input=json.dumps(event_data))
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

tool = UnifiedGoogleCalendar(
    action="create",
    summary="Team Meeting",  # Note: "title" becomes "summary"
    start_time="2025-01-15T10:00:00Z",
    end_time="2025-01-15T11:00:00Z",
    description="Weekly sync",
    location="Conference Room A"
)
result = tool.run()
```

**Key Changes:**
- No need for JSON encoding
- `title` parameter renamed to `summary`
- Direct parameter passing instead of nested dict

---

### GoogleCalendarList → UnifiedGoogleCalendar

**Before:**
```python
from tools.communication.google_calendar_list import GoogleCalendarList

tool = GoogleCalendarList(input="team meeting")
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

tool = UnifiedGoogleCalendar(
    action="list",
    query="team meeting"  # Note: "input" becomes "query"
)
result = tool.run()
```

**Key Changes:**
- `input` parameter renamed to `query`
- More descriptive parameter name

---

### GoogleCalendarUpdateEvent → UnifiedGoogleCalendar

**Before:**
```python
from tools.communication.google_calendar_update_event import GoogleCalendarUpdateEvent

tool = GoogleCalendarUpdateEvent(
    event_id="event123",
    summary="Updated Meeting Title",
    start_time="2025-01-15T14:00:00",
    location="Conference Room B"
)
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

tool = UnifiedGoogleCalendar(
    action="update",
    event_id="event123",
    summary="Updated Meeting Title",
    start_time="2025-01-15T14:00:00",
    location="Conference Room B"
)
result = tool.run()
```

**Key Changes:**
- Add `action="update"` parameter
- All other parameters remain the same

---

### GoogleCalendarDeleteEvent → UnifiedGoogleCalendar

**Before:**
```python
from tools.communication.google_calendar_delete_event import GoogleCalendarDeleteEvent

tool = GoogleCalendarDeleteEvent(
    event_id="event123",
    send_updates="all"
)
result = tool.run()
```

**After:**
```python
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar

tool = UnifiedGoogleCalendar(
    action="delete",
    event_id="event123",
    send_updates="all"
)
result = tool.run()
```

**Key Changes:**
- Add `action="delete"` parameter
- All other parameters remain the same

---

## Parameter Mapping

### Google Workspace Tools

| Old Parameter | New Parameter | Notes |
|--------------|---------------|-------|
| `mode` | `mode` | Unchanged ("create" or "modify") |
| `title` | `title` | Unchanged |
| `document_id` | `document_id` | Unchanged (for Docs) |
| `spreadsheet_id` | `spreadsheet_id` | Unchanged (for Sheets) |
| `presentation_id` | `presentation_id` | Unchanged (for Slides) |
| `content` | `content` | Unchanged |
| `data` | `data` | Unchanged |
| `slides` | `slides` | Unchanged |
| `share_with` | `share_with` | Unchanged |

**New Required Parameter:**
- `workspace_type`: Must be "docs", "sheets", or "slides"

### Google Calendar Tools

| Old Tool | Old Parameter | New Parameter | Notes |
|----------|--------------|---------------|-------|
| CreateEventDraft | `input` (JSON string) | Individual params | No JSON encoding needed |
| CreateEventDraft | JSON: `title` | `summary` | Renamed for clarity |
| List | `input` | `query` | Renamed for clarity |
| UpdateEvent | All params | Same params | No changes |
| DeleteEvent | All params | Same params | No changes |

**New Required Parameter:**
- `action`: Must be "create", "list", "update", or "delete"

---

## Benefits of Migration

### 1. Cleaner API
- **Single import per category** instead of multiple tool imports
- **Consistent parameter structure** across all workspace types
- **Type-safe selection** with Literal types

### 2. Better Developer Experience
- **IDE autocomplete** for workspace_type and action parameters
- **Reduced boilerplate** (no JSON encoding for calendar events)
- **More descriptive names** (query instead of input)

### 3. Easier Maintenance
- **Shared validation logic** across all tools in category
- **Centralized error handling**
- **Consistent return formats**

### 4. Future-Proof
- **New workspace types** easily added
- **New calendar actions** easily added
- **Single codebase** to update and test

---

## Migration Checklist

- [ ] Identify all deprecated tool usage in codebase
- [ ] Update imports to unified tools
- [ ] Add workspace_type or action parameter
- [ ] Update parameter names where changed (title→summary, input→query)
- [ ] Remove JSON encoding for calendar events
- [ ] Run tests to verify functionality
- [ ] Update documentation and comments
- [ ] Remove old import statements

---

## Testing Your Migration

### Enable Mock Mode
```python
import os
os.environ["USE_MOCK_APIS"] = "true"
```

### Test Each Tool Type

**Google Workspace:**
```python
# Test Docs
docs_tool = UnifiedGoogleWorkspace(
    workspace_type="docs",
    mode="create",
    title="Test Doc",
    content="Test content"
)
assert docs_tool.run()["success"] == True

# Test Sheets
sheets_tool = UnifiedGoogleWorkspace(
    workspace_type="sheets",
    mode="create",
    title="Test Sheet",
    data=[["A", "B"], [1, 2]]
)
assert sheets_tool.run()["success"] == True

# Test Slides
slides_tool = UnifiedGoogleWorkspace(
    workspace_type="slides",
    mode="create",
    title="Test Slides",
    slides=[{"layout": "title", "title": "Test"}]
)
assert slides_tool.run()["success"] == True
```

**Google Calendar:**
```python
# Test Create
create_tool = UnifiedGoogleCalendar(
    action="create",
    summary="Test Event",
    start_time="2025-01-15T10:00:00Z",
    end_time="2025-01-15T11:00:00Z"
)
assert create_tool.run()["success"] == True

# Test List
list_tool = UnifiedGoogleCalendar(
    action="list",
    query="test"
)
assert list_tool.run()["success"] == True

# Test Update
update_tool = UnifiedGoogleCalendar(
    action="update",
    event_id="test123",
    summary="Updated Event"
)
assert update_tool.run()["success"] == True

# Test Delete
delete_tool = UnifiedGoogleCalendar(
    action="delete",
    event_id="test123"
)
assert delete_tool.run()["success"] == True
```

---

## Common Migration Patterns

### Pattern 1: Type Selection
```python
# Before: Different imports for different types
from tools.communication.google_docs import GoogleDocs
from tools.communication.google_sheets import GoogleSheets
from tools.communication.google_slides import GoogleSlides

# After: Single import with type parameter
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace
docs = UnifiedGoogleWorkspace(workspace_type="docs", ...)
sheets = UnifiedGoogleWorkspace(workspace_type="sheets", ...)
slides = UnifiedGoogleWorkspace(workspace_type="slides", ...)
```

### Pattern 2: Action-Based Operations
```python
# Before: Different imports for different actions
from tools.communication.google_calendar_create_event_draft import ...
from tools.communication.google_calendar_list import ...
from tools.communication.google_calendar_update_event import ...
from tools.communication.google_calendar_delete_event import ...

# After: Single import with action parameter
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar
create = UnifiedGoogleCalendar(action="create", ...)
list_events = UnifiedGoogleCalendar(action="list", ...)
update = UnifiedGoogleCalendar(action="update", ...)
delete = UnifiedGoogleCalendar(action="delete", ...)
```

### Pattern 3: Calendar Event Creation
```python
# Before: JSON encoding required
import json
event_data = {"title": "Meeting", "start_time": "...", "end_time": "..."}
tool = OldTool(input=json.dumps(event_data))

# After: Direct parameters
tool = UnifiedGoogleCalendar(
    action="create",
    summary="Meeting",  # Note: title → summary
    start_time="...",
    end_time="..."
)
```

---

## Troubleshooting

### Issue: ImportError after migration
**Solution:** Ensure you're importing from the correct unified tool:
```python
# Correct
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar
```

### Issue: ValidationError on workspace_type/action
**Solution:** Check valid values:
- `workspace_type`: Must be "docs", "sheets", or "slides"
- `action`: Must be "create", "list", "update", or "delete"

### Issue: Calendar event creation fails
**Solution:** Use `summary` instead of `title`:
```python
# Wrong
tool = UnifiedGoogleCalendar(action="create", title="Meeting", ...)

# Correct
tool = UnifiedGoogleCalendar(action="create", summary="Meeting", ...)
```

### Issue: Deprecation warnings still showing
**Solution:** This is expected until v3.0.0. The warnings indicate you're using the old API through the compatibility wrapper. Complete the migration to remove warnings.

---

## Support Resources

- **API Documentation:** `/genspark_tools_documentation.md`
- **Deprecation Timeline:** `/DEPRECATION_TIMELINE.md`
- **Test Examples:**
  - `/tools/communication/unified_google_workspace/test_unified_google_workspace.py`
  - `/tools/communication/unified_google_calendar/test_unified_google_calendar.py`
- **Complete Examples:** `/tool_examples_complete.md`

---

**Last Updated:** 2025-11-23
**Removal Version:** v3.0.0 (planned Q3 2025)
