# research_synthesizer

Synthesize multiple research sources into a coherent research document.

## Category

Data & Search

## Parameters

- **sources** (List[Dict[str, Any): List of source dictionaries with content and metadata - **Required**
- **research_topic** (str): Main research topic or question - **Required**
- **citation_style** (Literal["apa", "mla", "chicago", "ieee"): Citation format - Optional
- **output_format** (Literal["markdown", "html", "pdf"): Output document format - Optional
- **include_summary** (bool): Generate executive summary - Optional
- **include_outline** (bool): Generate research outline - Optional
- **synthesis_depth** (Literal["quick", "standard", "comprehensive"): Synthesis depth affecting length and detail - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.data.intelligence.research_synthesizer import ResearchSynthesizer

# Initialize the tool
tool = ResearchSynthesizer(
    sources="example_value",
    research_topic="example_value",
    citation_style="example_value"  # Optional
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
python research_synthesizer.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
