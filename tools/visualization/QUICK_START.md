# Visualization Tools Quick Start Guide

## TL;DR - What Changed?

**Old:** 16 separate chart tools with 95% duplicate code  
**New:** 2 unified tools + 3 specialized tools with shared renderers

---

## Quick Examples

### Line Chart
```python
from tools.visualization.unified_chart_generator import UnifiedChartGenerator

tool = UnifiedChartGenerator(
    chart_type="line",
    data=[1, 2, 3, 4, 5],
    title="Sales Trend"
)
result = tool.run()
```

### Bar Chart
```python
tool = UnifiedChartGenerator(
    chart_type="bar",
    data={"Q1": 100, "Q2": 150, "Q3": 120, "Q4": 180},
    title="Quarterly Revenue"
)
```

### Pie Chart
```python
tool = UnifiedChartGenerator(
    chart_type="pie",
    data=[
        {"label": "Product A", "value": 40},
        {"label": "Product B", "value": 60}
    ],
    title="Market Share"
)
```

### Organization Chart
```python
from tools.visualization.unified_diagram_generator import UnifiedDiagramGenerator

tool = UnifiedDiagramGenerator(
    diagram_type="org_chart",
    data=[
        {"id": "ceo", "name": "CEO"},
        {"id": "cto", "name": "CTO", "parent": "ceo"}
    ],
    title="Company Structure"
)
```

---

## All Chart Types

### UnifiedChartGenerator

| chart_type | Purpose | Data Format |
|------------|---------|-------------|
| `line` | Trends over time | List of numbers or {x,y} objects |
| `bar` | Horizontal comparisons | Dict or list of {label,value} |
| `column` | Vertical comparisons | Dict or list of {label,value} |
| `pie` | Proportions | List of {label,value} objects |
| `scatter` | Correlations | {x:[...], y:[...]} or list of {x,y} |
| `area` | Cumulative trends | List of numbers or {x,y} objects |
| `histogram` | Distributions | List of numbers |
| `dual_axes` | Two metrics | {primary:[...], secondary:[...]} |
| `radar` | Multi-dimensional | {categories:[...], values:[...]} |

### UnifiedDiagramGenerator

| diagram_type | Purpose | Data Format |
|--------------|---------|-------------|
| `fishbone` | Cause-effect analysis | {effect:str, causes:dict} |
| `flow` | Process flows | {nodes:list, edges:list} |
| `mindmap` | Idea organization | {root:{name:str, children:list}} |
| `org_chart` | Org structure | List of {id, name, parent} |

### Specialized Tools (Unchanged)

- `GenerateWordCloudChart` - Word frequency visualization
- `GenerateTreemapChart` - Hierarchical data
- `GenerateNetworkGraph` - Network relationships

---

## Common Options

```python
tool = UnifiedChartGenerator(
    chart_type="line",
    data=[1, 2, 3],
    title="My Chart",
    width=1200,           # Default: 800
    height=800,           # Default: 600
    options={
        "x_label": "Time",
        "y_label": "Value",
        "grid": True,
        "color": "#4285F4",
        "labels": ["Jan", "Feb", "Mar"]
    }
)
```

---

## Old Code Still Works

```python
# This still works (with deprecation warning)
from tools.visualization.generate_line_chart import GenerateLineChart

tool = GenerateLineChart(prompt="Sales", params={"data": [1,2,3]})
result = tool.run()  # ⚠️ Shows deprecation warning
```

**Migration tip:** Use new unified tools for cleaner code

---

## File Paths

**Unified Tools:**
- `/tools/visualization/unified_chart_generator/`
- `/tools/visualization/unified_diagram_generator/`

**Renderers:**
- `/tools/visualization/renderers/`

**Documentation:**
- `/CONSOLIDATION_SUMMARY.md` - Full details
- `/tools/visualization/MIGRATION_GUIDE.md` - Migration examples
- `/CONSOLIDATION_DELIVERABLES.md` - Implementation summary

---

## Need Help?

1. **See examples:** Check test files in unified_*/test_*.py
2. **Migration:** Read MIGRATION_GUIDE.md
3. **Full docs:** Read CONSOLIDATION_SUMMARY.md
4. **Run tests:** `pytest tools/visualization/ -v`

---

**What to remember:**
- Use `UnifiedChartGenerator` for standard charts (9 types)
- Use `UnifiedDiagramGenerator` for diagrams (4 types)
- Old tools still work but are deprecated
- Same output format, cleaner API
