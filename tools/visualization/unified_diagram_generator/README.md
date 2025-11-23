# unified_diagram_generator

Generate diagrams (fishbone, flow, mind maps, org charts).

## Category

Data Visualization

## Parameters

- **diagram_type** (DiagramType): No description - **Required**
- **data** (Any): No description - **Required**
- **title** (str): Diagram title - Optional
- **width** (int): Diagram width in pixels - Optional
- **height** (int): Diagram height in pixels - Optional
- **options** (Dict[str, Any): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.visualization.unified_diagram_generator import UnifiedDiagramGenerator

# Initialize the tool
tool = UnifiedDiagramGenerator(
    diagram_type="example_value",
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
python unified_diagram_generator.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
