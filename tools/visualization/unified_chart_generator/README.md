# unified_chart_generator

Generate standard charts with multiple chart types.

## Category

Data Visualization

## Parameters

- **chart_type** (ChartType): No description - **Required**
- **data** (Any): No description - **Required**
- **title** (str): Chart title - Optional
- **width** (int): Chart width in pixels - Optional
- **height** (int): Chart height in pixels - Optional
- **options** (Dict[str, Any): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.visualization.unified_chart_generator import UnifiedChartGenerator

# Initialize the tool
tool = UnifiedChartGenerator(
    chart_type="example_value",
    data="example_value",
    title="example_value"  # Optional
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
python unified_chart_generator.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
