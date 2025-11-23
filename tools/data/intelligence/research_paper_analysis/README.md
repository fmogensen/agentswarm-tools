# research_paper_analysis

Analyze academic papers to extract key findings, methodology, and citations.

## Category

Data & Search

## Parameters

- **paper_urls** (List[str): List of paper URLs or DOIs to analyze - **Required**
- **research_question** (str): Optional research question to focus the analysis - Optional
- **extract_citations** (bool): Whether to extract and analyze citations from papers - Optional
- **include_methodology** (bool): Extract and summarize methodology sections - Optional
- **max_papers** (int): Maximum number of papers to analyze - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.data.intelligence.research_paper_analysis import ResearchPaperAnalysis

# Initialize the tool
tool = ResearchPaperAnalysis(
    paper_urls="example_value",
    research_question="example_value",  # Optional
    extract_citations="example_value"  # Optional
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
python research_paper_analysis.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
