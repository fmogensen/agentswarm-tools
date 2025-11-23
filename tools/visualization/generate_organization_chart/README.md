# generate_organization_chart

Generate organization chart for hierarchical structure visualization.

## Category

Data Visualization

## Parameters

- **data** (List[Dict[str, Any): List of organization nodes with id, name, title, and optional parent - **Required**
- **title** (str): Chart title - Optional
- **width** (int): Chart width in pixels - Optional
- **height** (int): Chart height in pixels - Optional
- **orientation** (str): No description - Optional
- **node_template** (str): Node display template: standard, compact, detailed, custom - Optional
- **params** (Dict[str, Any): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.visualization.generate_organization_chart import GenerateOrganizationChart

# Initialize the tool
tool = GenerateOrganizationChart(
    data="example_value",
    title="example_value",  # Optional
    width="example_value"  # Optional
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
python generate_organization_chart.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
