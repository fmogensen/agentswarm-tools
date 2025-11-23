# rag_pipeline

RAG Pipeline for semantic search across multiple vector databases.

## Category

Data & Search

## Parameters

- **query** (str): Search query for retrieving relevant documents - **Required**
- **vector_db** (Literal["pinecone", "chroma", "weaviate", "qdrant", "milvus"): Vector database to use for search - **Required**
- **collection_name** (str): Collection/index/namespace name in the vector database - Optional
- **top_k** (int): Number of top results to return - Optional
- **embedding_model** (str): No description - Optional
- **search_type** (Literal["semantic", "keyword", "hybrid"): No description - Optional
- **metadata_filter** (Dict[str, Any): Optional metadata filters as key-value pairs - Optional
- **rerank** (bool): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.data.intelligence.rag_pipeline import RAGPipeline

# Initialize the tool
tool = RAGPipeline(
    query="example_value",
    vector_db="example_value",
    collection_name="example_value"  # Optional
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
python rag_pipeline.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../../README.md)
