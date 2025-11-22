# Migration Guide: v1.1.0 → v1.2.0

**Release Date**: November 22, 2025
**Type**: Category Reorganization (Breaking Change for Metadata Only)

## Overview

AgentSwarm Tools v1.2.0 introduces a streamlined 8-category structure, consolidating the previous 19 categories into logical groupings for improved discoverability and maintainability.

**Good News**: Import paths remain fully backward compatible. Only tool metadata attributes have changed.

---

## What Changed

### Category Consolidation (19 → 8)

| Old Categories (v1.1.0) | New Category (v1.2.0) | Tool Count |
|------------------------|----------------------|------------|
| search, business_intelligence, ai_intelligence | **data** | 13 |
| communication, workspace_integration, location_services | **communication** | 23 |
| media_generation, media_analysis, media_processing | **media** | 20 |
| visualization | **visualization** | 16 |
| document_creation, content_creation, web, web_content | **content** | 10 |
| code_execution, storage, agent_management | **infrastructure** | 11 |
| utilities | **utils** | 8 |
| *(new)* | **integrations** | 0 (extensible) |

### Directory Structure Changes

#### Old Structure (v1.1.0)
```
tools/
├── search/
├── business_intelligence/
├── ai_intelligence/
├── media_generation/
├── media_analysis/
├── media_processing/
├── communication/
├── workspace_integration/
├── location_services/
├── document_creation/
├── content_creation/
├── web/
├── web_content/
├── code_execution/
├── storage/
├── agent_management/
├── visualization/
└── utilities/
```

#### New Structure (v1.2.0)
```
tools/
├── data/
│   ├── search/
│   ├── business/
│   └── intelligence/
├── communication/          # Enhanced with workspace + location
├── media/
│   ├── generation/
│   ├── analysis/
│   └── processing/
├── visualization/          # Unchanged
├── content/
│   ├── documents/
│   └── web/
├── infrastructure/
│   ├── execution/
│   ├── storage/
│   └── management/
├── utils/                  # Unchanged
└── integrations/          # New (empty, extensible)
```

---

## Breaking Changes

### 1. Tool Category Metadata

The `tool_category` attribute has been updated in all tool classes:

```python
# OLD (v1.1.0)
class WebSearch(BaseTool):
    tool_name: str = "web_search"
    tool_category: str = "search"  # Old category

# NEW (v1.2.0)
class WebSearch(BaseTool):
    tool_name: str = "web_search"
    tool_category: str = "data"  # New consolidated category
```

**Impact**: If you filter or group tools by `tool_category`, update your category names.

### 2. Category-Based Filtering

If your code filters tools by category:

```python
# OLD (v1.1.0)
media_tools = [t for t in all_tools if t.tool_category == "media_generation"]

# NEW (v1.2.0)
media_tools = [t for t in all_tools if t.tool_category == "media"]
```

Or use more granular filtering with directory paths:

```python
# NEW (v1.2.0) - Check subdirectory
from pathlib import Path

generation_tools = [
    t for t in all_tools
    if "media/generation" in str(Path(t.__module__).parent)
]
```

---

## What Didn't Change (Fully Backward Compatible)

### ✅ Import Paths

All import paths remain unchanged:

```python
# Still works in v1.2.0 (no changes needed)
from tools.data.search.web_search import WebSearch
from tools.media.generation.image_generation import ImageGenerationTool
from tools.content.documents.create_agent import CreateAgentTool
from tools.infrastructure.execution.bash_tool import BashTool
from tools.communication.gmail_search import GmailSearch
from tools.visualization.generate_line_chart import GenerateLineChart
from tools.utils.think import Think
```

### ✅ Tool Names

All tool names remain unchanged:

```python
# Still works in v1.2.0
tool = WebSearch(query="AI news")
tool = ImageGenerationTool(model="flux-pro", query="sunset")
tool = CreateAgentTool(type="docs", title="Report")
```

### ✅ Tool Functionality

No changes to tool behavior, parameters, or return values.

### ✅ API Interfaces

All tool APIs remain identical.

---

## Migration Steps

### Step 1: Update Category Filters (If Applicable)

If you have code that filters tools by category:

```python
# BEFORE (v1.1.0)
def get_search_tools():
    return [t for t in all_tools if t.tool_category == "search"]

def get_media_generation_tools():
    return [t for t in all_tools if t.tool_category == "media_generation"]

# AFTER (v1.2.0)
def get_search_tools():
    return [t for t in all_tools if t.tool_category == "data"]
    # Or filter by subdirectory: if "data/search" in t.__module__

def get_media_generation_tools():
    return [t for t in all_tools if t.tool_category == "media"]
    # Or filter by subdirectory: if "media/generation" in t.__module__
```

### Step 2: Update Documentation References

Update any documentation, comments, or configuration files that reference old category names:

```yaml
# BEFORE (v1.1.0)
tool_config:
  category: "media_generation"

# AFTER (v1.2.0)
tool_config:
  category: "media"
```

### Step 3: Update Category Mappings

If you have category mappings in your code:

```python
# BEFORE (v1.1.0)
CATEGORY_MAP = {
    "search": "Search & Information",
    "media_generation": "Media Generation",
    "communication": "Communication",
}

# AFTER (v1.2.0)
CATEGORY_MAP = {
    "data": "Data & Intelligence",
    "media": "Media",
    "communication": "Communication & Collaboration",
    "visualization": "Visualization",
    "content": "Content",
    "infrastructure": "Infrastructure",
    "utils": "Utilities",
    "integrations": "Integrations",
}
```

### Step 4: Update Tests (If Needed)

If your tests reference category names:

```python
# BEFORE (v1.1.0)
def test_category():
    tool = WebSearch(query="test")
    assert tool.tool_category == "search"

# AFTER (v1.2.0)
def test_category():
    tool = WebSearch(query="test")
    assert tool.tool_category == "data"
```

---

## Category Mapping Reference

Use this reference to update category-based logic:

| Old Category (v1.1.0) | New Category (v1.2.0) | Subdirectory |
|----------------------|----------------------|--------------|
| search | data | data/search/ |
| business_intelligence | data | data/business/ |
| ai_intelligence | data | data/intelligence/ |
| media_generation | media | media/generation/ |
| media_analysis | media | media/analysis/ |
| media_processing | media | media/processing/ |
| communication | communication | communication/ |
| workspace_integration | communication | communication/ |
| location_services | communication | communication/ |
| document_creation | content | content/documents/ |
| content_creation | content | content/documents/ |
| web | content | content/web/ |
| web_content | content | content/web/ |
| code_execution | infrastructure | infrastructure/execution/ |
| storage | infrastructure | infrastructure/storage/ |
| agent_management | infrastructure | infrastructure/management/ |
| visualization | visualization | visualization/ |
| utilities | utils | utils/ |

---

## Benefits of v1.2.0

### 1. Improved Discoverability
- **58% fewer categories** (19 → 8) reduces cognitive load
- Logical groupings match common use cases
- Easier to find the right tool for the job

### 2. Better Maintainability
- Clear separation of concerns
- Consistent organizational patterns
- Easier to add new tools

### 3. Scalable Structure
- Hierarchical organization supports growth
- `integrations/` category ready for external services
- Room for future expansion without restructuring

### 4. Enhanced Navigation
- Intuitive category names
- Related tools grouped together
- Clearer mental model of available capabilities

---

## FAQ

### Q: Do I need to update my import statements?
**A**: No, all import paths remain unchanged and fully backward compatible.

### Q: Will my existing code break?
**A**: Only if you filter or group tools by `tool_category` attribute. Update category names in those cases.

### Q: How do I know which new category a tool belongs to?
**A**: Check the [Category Mapping Reference](#category-mapping-reference) table above, or view the tool's `tool_category` attribute.

### Q: Can I still use the old category names?
**A**: No, the `tool_category` attributes have been updated to the new 8-category names. Update your code accordingly.

### Q: What happened to the old categories?
**A**: They were consolidated into broader, more intuitive categories. See the [Category Consolidation](#category-consolidation-19--8) table.

### Q: Is there a way to see the old granular categories?
**A**: Yes, the directory structure maintains subcategories (e.g., `data/search/`, `media/generation/`) for granular organization.

### Q: What is the `integrations/` category for?
**A**: Reserved for future external service integrations and third-party tool connectors.

---

## Need Help?

- **Documentation**: See updated docs in `docs/references/`
- **Examples**: Check `docs/tutorials/TOOL_EXAMPLES.md`
- **Issues**: Report on [GitHub Issues](https://github.com/fmogensen/agentswarm-tools/issues)
- **Discussions**: Ask on [GitHub Discussions](https://github.com/fmogensen/agentswarm-tools/discussions)

---

## Rollback Instructions

If you need to temporarily rollback to v1.1.0:

```bash
# Using git
git checkout v1.1.0

# Using pip
pip install agentswarm-tools==1.1.0
```

**Note**: v1.2.0 is the recommended version with improved organization and no functional changes.

---

**Version**: 1.2.0
**Last Updated**: November 22, 2025
