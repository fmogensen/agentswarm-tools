# deep_research_agent

Perform comprehensive research on a topic with multi-source aggregation, AI synthesis, and fact-checking.

## Category

Data & Search

## Parameters

- **research_topic** (str): The research topic or question to investigate - **Required**
- **depth** (Literal["quick", "standard", "comprehensive"): No description - Optional
- **sources** (List[Literal["web", "scholar", "documents", "news"): No description - Optional
- **max_sources** (int): Maximum number of sources to gather per source type - Optional
- **citation_style** (Literal["apa", "mla", "chicago", "ieee"): No description - Optional
- **output_format** (Literal["markdown", "html", "pdf"): Format for the research report output - Optional
- **include_methodology** (bool): Include research methodology section in report - Optional
- **fact_check** (bool): Perform fact-checking on key claims using AI - Optional
- **generate_summary** (bool): Generate executive summary at the beginning of report - Optional
- **generate_outline** (bool): Generate research outline before full report - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.data.intelligence.deep_research_agent import DeepResearchAgent

# Initialize the tool
tool = DeepResearchAgent(
    research_topic="example_value",
    depth="example_value",  # Optional
    sources="example_value"  # Optional
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
python deep_research_agent.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
