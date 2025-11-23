# trend_analyzer

Analyze trends in time-series data and identify patterns.

## Category

Data & Search

## Parameters

- **data_points** (List[float): List of numeric data points in chronological order - **Required**
- **time_labels** (List[str): No description - Optional
- **analysis_type** (str): Type of analysis: trend, volatility, seasonality, all - Optional
- **window_size** (int): Window size for moving average calculations - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.data.business.trend_analyzer import TrendAnalyzer

# Initialize the tool
tool = TrendAnalyzer(
    data_points="example_value",
    time_labels="example_value",  # Optional
    analysis_type="example_value"  # Optional
)

# Run the tool
result = tool.run()

# Check result
if result["success"]:
    print(result["result"])
else:
    print(f"Error: {result.get('error')}")
```

## Testing

Run tests with:
```bash
python trend_analyzer.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
