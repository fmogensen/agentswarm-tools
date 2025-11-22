# Business Analytics Tools

This directory contains business and analytics tools for data processing, reporting, and trend analysis.

## Tools

### DataAggregator
**File:** `data_aggregator/data_aggregator.py`

Aggregate data from multiple sources using statistical methods (sum, avg, max, min, count, median).

**Example:**
```python
from tools.business.data_aggregator import DataAggregator

tool = DataAggregator(
    sources=["10", "20", "30"],
    aggregation_method="avg"
)
result = tool.run()
```

### ReportGenerator
**File:** `report_generator/report_generator.py`

Generate business reports from structured data in JSON, Markdown, or HTML formats.

**Example:**
```python
from tools.business.report_generator import ReportGenerator

tool = ReportGenerator(
    data={"revenue": 100000, "expenses": 60000},
    report_type="executive",
    title="Q4 Financial Report",
    format="markdown"
)
result = tool.run()
```

### TrendAnalyzer
**File:** `trend_analyzer/trend_analyzer.py`

Analyze trends, volatility, and seasonality in time-series data.

**Example:**
```python
from tools.business.trend_analyzer import TrendAnalyzer

tool = TrendAnalyzer(
    data_points=[10, 12, 15, 18, 20],
    analysis_type="all"
)
result = tool.run()
```

## Usage

All tools follow the Agency Swarm pattern:
1. Import the tool
2. Initialize with parameters
3. Call `run()` method
4. Check `result['success']` and process `result['result']`

## Testing

Each tool has a comprehensive test file:
- `test_data_aggregator.py`
- `test_report_generator.py`
- `test_trend_analyzer.py`

Run tests:
```bash
python3 -m pytest tools/business/
```

## Documentation

See [PHASE_2_TOOLS_GUIDE.md](../../PHASE_2_TOOLS_GUIDE.md) for complete usage examples.
