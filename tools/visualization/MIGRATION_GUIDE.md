# Visualization Tools Migration Guide

## Quick Reference

### Old → New Mapping

| Old Tool | New Tool | Chart/Diagram Type |
|----------|----------|-------------------|
| `GenerateLineChart` | `UnifiedChartGenerator` | `chart_type="line"` |
| `GenerateBarChart` | `UnifiedChartGenerator` | `chart_type="bar"` |
| `GenerateColumnChart` | `UnifiedChartGenerator` | `chart_type="column"` |
| `GeneratePieChart` | `UnifiedChartGenerator` | `chart_type="pie"` |
| `GenerateScatterChart` | `UnifiedChartGenerator` | `chart_type="scatter"` |
| `GenerateAreaChart` | `UnifiedChartGenerator` | `chart_type="area"` |
| `GenerateHistogramChart` | `UnifiedChartGenerator` | `chart_type="histogram"` |
| `GenerateDualAxesChart` | `UnifiedChartGenerator` | `chart_type="dual_axes"` |
| `GenerateRadarChart` | `UnifiedChartGenerator` | `chart_type="radar"` |
| `GenerateFishboneDiagram` | `UnifiedDiagramGenerator` | `diagram_type="fishbone"` |
| `GenerateFlowDiagram` | `UnifiedDiagramGenerator` | `diagram_type="flow"` |
| `GenerateMindMap` | `UnifiedDiagramGenerator` | `diagram_type="mindmap"` |
| `GenerateOrganizationChart` | `UnifiedDiagramGenerator` | `diagram_type="org_chart"` |

**Unchanged (Specialized):**
- `GenerateWordCloudChart` - Unique text processing requirements
- `GenerateTreemapChart` - Hierarchical data structure
- `GenerateNetworkGraph` - Graph relationships

---

## Migration Examples

### Line Chart

**Before:**
```python
from tools.visualization.generate_line_chart import GenerateLineChart

tool = GenerateLineChart(
    prompt="Sales Trend",
    params={
        "data": [1, 2, 3, 4, 5],
        "title": "Q1 Sales",
        "x_label": "Month",
        "y_label": "Revenue",
        "width": 800,
        "height": 600
    }
)
result = tool.run()
```

**After:**
```python
from tools.visualization.unified_chart_generator import UnifiedChartGenerator

tool = UnifiedChartGenerator(
    chart_type="line",
    data=[1, 2, 3, 4, 5],
    title="Q1 Sales",
    width=800,
    height=600,
    options={
        "x_label": "Month",
        "y_label": "Revenue"
    }
)
result = tool.run()
```

### Bar Chart

**Before:**
```python
from tools.visualization.generate_bar_chart import GenerateBarChart

tool = GenerateBarChart(
    prompt="Sales by Region",
    params={
        "data": {"North": 45, "South": 32, "East": 38}
    }
)
result = tool.run()
```

**After:**
```python
from tools.visualization.unified_chart_generator import UnifiedChartGenerator

tool = UnifiedChartGenerator(
    chart_type="bar",
    data={"North": 45, "South": 32, "East": 38},
    title="Sales by Region"
)
result = tool.run()
```

### Pie Chart

**Before:**
```python
from tools.visualization.generate_pie_chart import GeneratePieChart

tool = GeneratePieChart(
    prompt="Market Share",
    params={
        "data": [
            {"label": "A", "value": 40},
            {"label": "B", "value": 60}
        ],
        "title": "Market Share Distribution",
        "colors": ["#FF6384", "#36A2EB"]
    }
)
result = tool.run()
```

**After:**
```python
from tools.visualization.unified_chart_generator import UnifiedChartGenerator

tool = UnifiedChartGenerator(
    chart_type="pie",
    data=[
        {"label": "A", "value": 40},
        {"label": "B", "value": 60}
    ],
    title="Market Share Distribution",
    options={
        "colors": ["#FF6384", "#36A2EB"]
    }
)
result = tool.run()
```

### Fishbone Diagram

**Before:**
```python
from tools.visualization.generate_fishbone_diagram import GenerateFishboneDiagram

tool = GenerateFishboneDiagram(
    prompt="Customer Complaints Analysis",
    params={
        "format": "text",
        "max_branches": 4
    }
)
result = tool.run()
```

**After:**
```python
from tools.visualization.unified_diagram_generator import UnifiedDiagramGenerator

tool = UnifiedDiagramGenerator(
    diagram_type="fishbone",
    data={
        "effect": "Customer Complaints",
        "causes": {
            "Methods": ["Poor training", "Inconsistent process"],
            "Materials": ["Low quality supplies"]
        }
    },
    title="Customer Complaints Analysis",
    options={
        "max_branches": 4
    }
)
result = tool.run()
```

### Organization Chart

**Before:**
```python
from tools.visualization.generate_organization_chart import GenerateOrganizationChart

tool = GenerateOrganizationChart(
    data=[
        {"id": "ceo", "name": "CEO", "title": "Chief Executive Officer"},
        {"id": "cto", "name": "CTO", "parent": "ceo"}
    ],
    title="Company Structure",
    width=1200,
    height=800,
    orientation="vertical"
)
result = tool.run()
```

**After:**
```python
from tools.visualization.unified_diagram_generator import UnifiedDiagramGenerator

tool = UnifiedDiagramGenerator(
    diagram_type="org_chart",
    data=[
        {"id": "ceo", "name": "CEO", "title": "Chief Executive Officer"},
        {"id": "cto", "name": "CTO", "parent": "ceo"}
    ],
    title="Company Structure",
    width=1200,
    height=800,
    options={
        "orientation": "vertical"
    }
)
result = tool.run()
```

---

## Parameter Mapping

### Common Parameters

| Old Parameter | New Parameter | Location | Notes |
|--------------|---------------|----------|-------|
| `prompt` | `title` | Direct | More descriptive name |
| `params["data"]` | `data` | Direct | Promoted to top-level |
| `params["title"]` | `title` | Direct | Promoted to top-level |
| `params["width"]` | `width` | Direct | Promoted to top-level |
| `params["height"]` | `height` | Direct | Promoted to top-level |
| `params["x_label"]` | `options["x_label"]` | Options dict | Chart-specific options |
| `params["y_label"]` | `options["y_label"]` | Options dict | Chart-specific options |
| `params["colors"]` | `options["colors"]` | Options dict | Chart-specific options |
| `params["grid"]` | `options["grid"]` | Options dict | Chart-specific options |

### Chart Type Selection

**Old:** Different import for each chart type
```python
from tools.visualization.generate_line_chart import GenerateLineChart
from tools.visualization.generate_bar_chart import GenerateBarChart
from tools.visualization.generate_pie_chart import GeneratePieChart
```

**New:** Single import with type parameter
```python
from tools.visualization.unified_chart_generator import UnifiedChartGenerator

# Select type with parameter
line_chart = UnifiedChartGenerator(chart_type="line", ...)
bar_chart = UnifiedChartGenerator(chart_type="bar", ...)
pie_chart = UnifiedChartGenerator(chart_type="pie", ...)
```

---

## Data Format Changes

### Line Chart Data

**Both formats supported:**
```python
# Simple list of numbers
data=[1, 2, 3, 4, 5]

# List of {x, y} objects
data=[
    {"x": 0, "y": 1},
    {"x": 1, "y": 2},
    {"x": 2, "y": 4}
]
```

### Bar/Column Chart Data

**Both formats supported:**
```python
# Dictionary (category -> value)
data={"North": 45, "South": 32}

# List of {label, value} objects
data=[
    {"label": "North", "value": 45},
    {"label": "South", "value": 32}
]
```

### Pie Chart Data

**Both formats supported:**
```python
# Dictionary with labels and values
data={
    "labels": ["A", "B"],
    "values": [40, 60]
}

# List of {label, value} objects (recommended)
data=[
    {"label": "A", "value": 40},
    {"label": "B", "value": 60}
]
```

### Scatter Chart Data

**Both formats supported:**
```python
# Dictionary with x and y arrays
data={
    "x": [1, 2, 3],
    "y": [2, 4, 6]
}

# List of {x, y} objects
data=[
    {"x": 1, "y": 2},
    {"x": 2, "y": 4},
    {"x": 3, "y": 6}
]
```

---

## Benefits of Migration

### 1. Cleaner API
- Fewer imports to remember
- Type-safe chart selection with Literal types
- Consistent parameter names across all chart types

### 2. Better Maintainability
- Single codebase for chart features
- Shared validation and error handling
- Easier to add new chart types

### 3. Improved Developer Experience
- IDE autocomplete for chart_type parameter
- Better error messages
- Consistent return format

### 4. Future-Proof
- New chart types added to unified tool
- Features added once, available everywhere
- Easier testing and debugging

---

## Deprecation Timeline

- **Now - Month 3:** Old tools work with deprecation warnings
- **Month 3 - Month 6:** Migrate internal usage
- **Month 6+:** Remove old implementations, keep wrappers for compatibility

---

## Need Help?

- Check the comprehensive test files for examples:
  - `/tools/visualization/unified_chart_generator/test_unified_chart_generator.py`
  - `/tools/visualization/unified_diagram_generator/test_unified_diagram_generator.py`

- See full documentation:
  - `/CONSOLIDATION_SUMMARY.md` - Complete consolidation details
  - `/genspark_tools_documentation.md` - Tool reference

- Use wrapper generator for automated migration:
  - `/tools/visualization/_create_compatibility_wrappers.py`
