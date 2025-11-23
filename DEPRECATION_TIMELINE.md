# Deprecation Timeline for AgentSwarm Tools

## Overview

This document tracks all deprecated tools and their removal timeline. All deprecated tools are currently functional as backward compatibility wrappers but will be removed in **v3.0.0**.

**Current Version:** v2.x
**Target Removal Version:** v3.0.0
**Last Updated:** 2025-11-23

---

## Deprecation Policy

1. **Deprecation Notice:** Tools are marked as deprecated with clear warnings
2. **Grace Period:** Minimum 6 months of backward compatibility support
3. **Migration Guide:** Comprehensive migration documentation provided
4. **Removal:** Complete removal in v3.0.0 (planned for Q3 2025)

---

## Deprecated Tools by Category

### 1. Visualization Tools (8 deprecated)

Tools consolidated into `UnifiedChartGenerator` and `UnifiedDiagramGenerator`.

| Deprecated Tool | Replacement | Status | Removal Version |
|----------------|-------------|--------|-----------------|
| `GenerateLineChart` | `UnifiedChartGenerator(chart_type="line")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateBarChart` | `UnifiedChartGenerator(chart_type="bar")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateColumnChart` | `UnifiedChartGenerator(chart_type="column")` | ⚠️ Deprecated | v3.0.0 |
| `GeneratePieChart` | `UnifiedChartGenerator(chart_type="pie")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateScatterChart` | `UnifiedChartGenerator(chart_type="scatter")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateAreaChart` | `UnifiedChartGenerator(chart_type="area")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateHistogramChart` | `UnifiedChartGenerator(chart_type="histogram")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateDualAxesChart` | `UnifiedChartGenerator(chart_type="dual_axes")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateRadarChart` | `UnifiedChartGenerator(chart_type="radar")` | ⚠️ Deprecated | v3.0.0 |

**Migration Guide:** `tools/visualization/MIGRATION_GUIDE.md`

#### Example Migration

```python
# OLD (deprecated)
from tools.visualization.generate_line_chart import GenerateLineChart
tool = GenerateLineChart(
    prompt="Sales Trend",
    params={"data": [1, 2, 3, 4, 5]}
)

# NEW (recommended)
from tools.visualization.unified_chart_generator import UnifiedChartGenerator
tool = UnifiedChartGenerator(
    chart_type="line",
    data=[1, 2, 3, 4, 5],
    title="Sales Trend"
)
```

---

### 2. Diagram Tools (4 deprecated)

| Deprecated Tool | Replacement | Status | Removal Version |
|----------------|-------------|--------|-----------------|
| `GenerateFishboneDiagram` | `UnifiedDiagramGenerator(diagram_type="fishbone")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateFlowDiagram` | `UnifiedDiagramGenerator(diagram_type="flow")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateMindMap` | `UnifiedDiagramGenerator(diagram_type="mindmap")` | ⚠️ Deprecated | v3.0.0 |
| `GenerateOrganizationChart` | `UnifiedDiagramGenerator(diagram_type="org_chart")` | ⚠️ Deprecated | v3.0.0 |

**Migration Guide:** `tools/visualization/MIGRATION_GUIDE.md`

#### Example Migration

```python
# OLD (deprecated)
from tools.visualization.generate_fishbone_diagram import GenerateFishboneDiagram
tool = GenerateFishboneDiagram(
    prompt="Customer Complaints",
    params={"format": "text"}
)

# NEW (recommended)
from tools.visualization.unified_diagram_generator import UnifiedDiagramGenerator
tool = UnifiedDiagramGenerator(
    diagram_type="fishbone",
    data={
        "effect": "Customer Complaints",
        "causes": {
            "Methods": ["Poor training"],
            "Materials": ["Low quality"]
        }
    },
    title="Customer Complaints Analysis"
)
```

---

### 3. Google Workspace Tools (3 deprecated)

Tools consolidated into `UnifiedGoogleWorkspace`.

| Deprecated Tool | Replacement | Status | Removal Version |
|----------------|-------------|--------|-----------------|
| `GoogleDocs` | `UnifiedGoogleWorkspace(workspace_type="docs")` | ⚠️ Deprecated | v3.0.0 |
| `GoogleSheets` | `UnifiedGoogleWorkspace(workspace_type="sheets")` | ⚠️ Deprecated | v3.0.0 |
| `GoogleSlides` | `UnifiedGoogleWorkspace(workspace_type="slides")` | ⚠️ Deprecated | v3.0.0 |

**Migration Guide:** `docs/guides/MIGRATION_GUIDE.md` (to be created)

#### Example Migration

```python
# OLD (deprecated)
from tools.communication.google_sheets import GoogleSheets
tool = GoogleSheets(
    mode="create",
    title="Sales Report",
    data=[["Product", "Sales"], ["Widget A", 1000]]
)

# NEW (recommended)
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace
tool = UnifiedGoogleWorkspace(
    workspace_type="sheets",
    mode="create",
    title="Sales Report",
    data=[["Product", "Sales"], ["Widget A", 1000]]
)
```

---

### 4. Google Calendar Tools (4 deprecated)

Tools consolidated into `UnifiedGoogleCalendar`.

| Deprecated Tool | Replacement | Status | Removal Version |
|----------------|-------------|--------|-----------------|
| `GoogleCalendarCreateEventDraft` | `UnifiedGoogleCalendar(action="create")` | ⚠️ Deprecated | v3.0.0 |
| `GoogleCalendarList` | `UnifiedGoogleCalendar(action="list")` | ⚠️ Deprecated | v3.0.0 |
| `GoogleCalendarUpdateEvent` | `UnifiedGoogleCalendar(action="update")` | ⚠️ Deprecated | v3.0.0 |
| `GoogleCalendarDeleteEvent` | `UnifiedGoogleCalendar(action="delete")` | ⚠️ Deprecated | v3.0.0 |

**Migration Guide:** `docs/guides/MIGRATION_GUIDE.md` (to be created)

#### Example Migration

```python
# OLD (deprecated)
from tools.communication.google_calendar_create_event_draft import GoogleCalendarCreateEventDraft
import json
tool = GoogleCalendarCreateEventDraft(
    input=json.dumps({
        "title": "Team Meeting",
        "start_time": "2025-01-15T10:00:00Z",
        "end_time": "2025-01-15T11:00:00Z"
    })
)

# NEW (recommended)
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar
tool = UnifiedGoogleCalendar(
    action="create",
    summary="Team Meeting",
    start_time="2025-01-15T10:00:00Z",
    end_time="2025-01-15T11:00:00Z"
)
```

---

## Summary Statistics

| Category | Deprecated Tools | Unified Replacements |
|----------|-----------------|---------------------|
| Visualization (Charts) | 9 | 1 (`UnifiedChartGenerator`) |
| Visualization (Diagrams) | 4 | 1 (`UnifiedDiagramGenerator`) |
| Google Workspace | 3 | 1 (`UnifiedGoogleWorkspace`) |
| Google Calendar | 4 | 1 (`UnifiedGoogleCalendar`) |
| **TOTAL** | **20** | **4** |

**Benefits of Consolidation:**
- 80% reduction in tool count (20 → 4)
- Single import per category
- Consistent parameter structure
- Easier testing and maintenance
- Better type safety with Literal types

---

## Timeline

### Phase 1: Deprecation Warnings (Current - Q1 2025)
- ✅ All deprecated tools emit DeprecationWarning
- ✅ Backward compatibility maintained
- ✅ Migration guides published
- 🔄 Internal codebase migration in progress

### Phase 2: Migration Support (Q2 2025)
- 📋 Automated migration scripts
- 📋 Updated documentation
- 📋 Example conversions in all repos
- 📋 Developer outreach and support

### Phase 3: Removal (Q3 2025 - v3.0.0)
- 📋 Remove deprecated tool implementations
- 📋 Keep minimal wrappers for error messages
- 📋 Update all documentation
- 📋 Breaking change announcements

---

## Migration Instructions

### Quick Start

1. **Identify deprecated tools in your code:**
   ```bash
   grep -r "from tools.visualization.generate_" . --include="*.py"
   grep -r "from tools.communication.google_" . --include="*.py"
   ```

2. **Review migration guide:**
   - Charts/Diagrams: `tools/visualization/MIGRATION_GUIDE.md`
   - Communication: `docs/guides/MIGRATION_GUIDE.md` (to be created)

3. **Update imports and parameters:**
   - Replace old tool imports with unified tool imports
   - Update parameter structure (see examples above)
   - Test thoroughly

4. **Run tests:**
   ```bash
   pytest tests/
   ```

### Common Migration Patterns

#### Pattern 1: Chart Type Selection
```python
# Before: Different imports
from tools.visualization.generate_line_chart import GenerateLineChart
from tools.visualization.generate_bar_chart import GenerateBarChart

# After: Single import with type parameter
from tools.visualization.unified_chart_generator import UnifiedChartGenerator
line = UnifiedChartGenerator(chart_type="line", ...)
bar = UnifiedChartGenerator(chart_type="bar", ...)
```

#### Pattern 2: Parameter Flattening
```python
# Before: Nested params dict
tool = OldTool(prompt="Title", params={"data": [...], "width": 800})

# After: Flat parameters
tool = NewTool(chart_type="line", title="Title", data=[...], width=800)
```

#### Pattern 3: Action-Based Tools
```python
# Before: Separate tools per action
from tools.communication.google_calendar_create_event_draft import ...
from tools.communication.google_calendar_list import ...

# After: Single tool with action parameter
from tools.communication.unified_google_calendar import UnifiedGoogleCalendar
create = UnifiedGoogleCalendar(action="create", ...)
list = UnifiedGoogleCalendar(action="list", ...)
```

---

## Breaking Changes in v3.0.0

### Removed Tools
All 20 deprecated tools listed above will be completely removed.

### API Changes
None for the unified tools (they are already stable).

### Migration Path
All deprecated tools currently work as wrappers, providing a smooth migration path.

---

## Support and Resources

### Documentation
- **Visualization Migration:** `tools/visualization/MIGRATION_GUIDE.md`
- **Communication Migration:** `docs/guides/MIGRATION_GUIDE.md` (planned)
- **API Reference:** `genspark_tools_documentation.md`
- **Examples:** `tool_examples_complete.md`

### Testing
- **Mock Mode:** Set `USE_MOCK_APIS=true` for testing
- **Test Files:** Each unified tool has comprehensive test coverage
- **Automated Tests:** `pytest tests/unit/visualization/` and `pytest tests/unit/communication/`

### Getting Help
- Review migration guides (linked above)
- Check test files for usage examples
- Consult API documentation
- File issues for migration problems

---

## Checklist for Developers

Before v3.0.0 release, ensure:

- [ ] All internal code migrated to unified tools
- [ ] All tests passing with new tools
- [ ] Migration scripts tested and documented
- [ ] Breaking changes documented in CHANGELOG
- [ ] Version bumped to 3.0.0
- [ ] Release notes published
- [ ] Deprecated tool files removed
- [ ] Documentation updated

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.0.0 | 2024-11-15 | Initial deprecation warnings added |
| v2.1.0 | 2024-11-20 | Unified tools introduced |
| v2.2.0 | 2024-11-23 | Deprecation timeline formalized |
| v3.0.0 | 2025-Q3 (planned) | Deprecated tools removed |

---

**Last Updated:** 2025-11-23
**Next Review:** 2025-12-23
**Maintainer:** AgentSwarm Tools Team
