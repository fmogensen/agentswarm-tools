# research_web_search

Perform web search and URL crawling for research purposes.

## Category

Data & Search

## Parameters

- **query** (str): Research query or question to search for - **Required**
- **max_results** (int): Maximum number of search results to return - Optional
- **crawl_content** (bool): No description - Optional
- **filter_duplicates** (bool): Remove duplicate URLs and near-duplicate content - Optional
- **rank_by** (Literal["relevance", "recency", "authority"): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.data.intelligence.research_web_search import ResearchWebSearch

# Initialize the tool
tool = ResearchWebSearch(
    query="example_value",
    max_results="example_value",  # Optional
    crawl_content="example_value"  # Optional
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
python research_web_search.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
