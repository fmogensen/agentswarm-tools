# data_aggregator

Aggregate data from multiple sources using different statistical methods.

## Category

Data & Search

## Parameters

- **sources** (List[str): Data source identifiers or numeric values as strings - **Required**
- **aggregation_method** (str): Aggregation method: sum, avg, max, min, count, median - **Required**
- **filters** (Dict[str, Any): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.data.business.data_aggregator import DataAggregator

# Initialize the tool
tool = DataAggregator(
    sources="example_value",
    aggregation_method="example_value",
    filters="example_value"  # Optional
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
python data_aggregator.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
