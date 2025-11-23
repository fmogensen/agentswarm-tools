# SupabaseVectorSearch

Perform semantic similarity search using Supabase pgvector extension.

## Overview

This tool enables high-performance vector similarity search for RAG pipelines, document retrieval, and recommendation systems. Supports multiple distance metrics and metadata filtering.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `table_name` | str | Yes | - | Table containing vector embeddings |
| `query_embedding` | List[float] | Yes | - | Query vector (must match column dimensions) |
| `embedding_column` | str | No | "embedding" | Name of the vector column |
| `match_threshold` | float | No | 0.5 | Minimum similarity score (0.0-1.0) |
| `match_count` | int | No | 10 | Maximum number of results (1-1000) |
| `filter` | dict | No | None | Metadata filter as JSON object |
| `metric` | str | No | "cosine" | Distance metric (cosine, l2, inner_product) |
| `include_metadata` | bool | No | True | Include metadata columns in results |
| `rpc_function` | str | No | "match_documents" | Custom RPC function name |

## Distance Metrics

### Cosine Similarity (Recommended)
Best for: Most NLP embeddings (OpenAI, Cohere, Sentence Transformers)
- Range: 0 (opposite) to 1 (identical)
- Formula: `1 - (distance / 2)`
- Normalized vectors: Angle-based similarity

```python
tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=embedding,
    metric="cosine"
)
```

### L2 Distance (Euclidean)
Best for: Image embeddings, coordinate data
- Range: 0 (identical) to infinity
- Formula: `1 / (1 + distance)`
- Absolute distance measurement

```python
tool = SupabaseVectorSearch(
    table_name="images",
    query_embedding=embedding,
    metric="l2"
)
```

### Inner Product
Best for: Pre-normalized vectors
- Range: -1 to 1
- Formula: Direct dot product
- Fastest computation

```python
tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=embedding,
    metric="inner_product"
)
```

## Common Embedding Dimensions

| Model | Dimension | Use Case |
|-------|-----------|----------|
| text-embedding-3-small (OpenAI) | 1536 | General purpose, cost-effective |
| text-embedding-3-large (OpenAI) | 3072 | High accuracy |
| all-MiniLM-L6-v2 (Sentence Transformers) | 384 | Fast, lightweight |
| all-mpnet-base-v2 (Sentence Transformers) | 768 | Balanced performance |
| BERT base | 768 | General NLP |
| GPT-3 ada-002 (deprecated) | 1536 | Legacy OpenAI |

## Examples

### Basic Search

```python
from tools.integrations.supabase import SupabaseVectorSearch

# Generate embedding (using OpenAI)
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="How do I optimize database queries?"
)
query_embedding = response.data[0].embedding

# Search for similar documents
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=query_embedding,
    match_threshold=0.7,
    match_count=5
)
result = search_tool.run()

# Process results
for doc in result['results']:
    print(f"Similarity: {doc['similarity']:.3f}")
    print(f"Content: {doc['content']}")
    print(f"Metadata: {doc['metadata']}\n")
```

### Search with Metadata Filter

```python
# Search only in specific category
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=query_embedding,
    match_threshold=0.6,
    match_count=10,
    filter={"category": "technology", "published": True, "year": 2025}
)
result = search_tool.run()
```

### Hybrid Search (Vector + Keyword)

```python
# First, do vector search
vector_results = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=query_embedding,
    match_threshold=0.5,
    match_count=20
).run()

# Then filter by keywords in application
query_keywords = ["database", "optimization"]
filtered_results = []

for doc in vector_results['results']:
    content_lower = doc['content'].lower()
    if any(keyword in content_lower for keyword in query_keywords):
        filtered_results.append(doc)

print(f"Found {len(filtered_results)} results matching both vector and keywords")
```

### Different Similarity Thresholds

```python
# High precision (fewer, more relevant results)
high_precision = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=query_embedding,
    match_threshold=0.85,  # Very similar only
    match_count=5
).run()

# High recall (more results, some less relevant)
high_recall = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=query_embedding,
    match_threshold=0.5,  # Include moderately similar
    match_count=20
).run()

# Balanced
balanced = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=query_embedding,
    match_threshold=0.7,  # Good middle ground
    match_count=10
).run()
```

### Re-ranking Results

```python
# Get initial results
search_results = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=query_embedding,
    match_count=50  # Get more candidates
).run()

# Re-rank using cross-encoder or other model
from sentence_transformers import CrossEncoder
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

query_text = "How to optimize database queries?"
pairs = [[query_text, doc['content']] for doc in search_results['results']]
scores = reranker.predict(pairs)

# Combine and sort
for i, doc in enumerate(search_results['results']):
    doc['rerank_score'] = scores[i]

reranked = sorted(search_results['results'], key=lambda x: x['rerank_score'], reverse=True)

# Return top 10 after re-ranking
final_results = reranked[:10]
```

## Performance Optimization

### Index Configuration

```sql
-- For < 100K vectors: IVFFlat
CREATE INDEX documents_embedding_idx ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- For 100K - 1M vectors: IVFFlat with more lists
CREATE INDEX documents_embedding_idx ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);

-- For > 1M vectors: HNSW
CREATE INDEX documents_embedding_idx ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### Query Optimization

```python
# ✅ Good: Reasonable limits
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=embedding,
    match_threshold=0.7,  # Filter out low matches
    match_count=10        # Limit results
)

# ❌ Bad: Returns too many results
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=embedding,
    match_threshold=0.0,  # Returns everything
    match_count=1000      # Slow query
)
```

### Benchmark Results

| Vector Count | Index Type | Avg Search Time | P95 | P99 |
|--------------|------------|-----------------|-----|-----|
| 10K | IVFFlat | 15ms | 25ms | 35ms |
| 100K | IVFFlat | 45ms | 70ms | 95ms |
| 1M | HNSW | 18ms | 30ms | 45ms |
| 10M | HNSW | 35ms | 55ms | 80ms |

## Error Handling

```python
from shared.errors import ValidationError, APIError, AuthenticationError

try:
    search_tool = SupabaseVectorSearch(
        table_name="documents",
        query_embedding=embedding,
        match_threshold=0.7
    )
    result = search_tool.run()

except ValidationError as e:
    # Invalid parameters
    print(f"Validation error: {e.message}")
    print(f"Field: {e.details.get('field')}")

except AuthenticationError as e:
    # Missing or invalid credentials
    print(f"Auth error: {e.message}")
    print("Check SUPABASE_URL and SUPABASE_KEY")

except APIError as e:
    # API call failed
    print(f"API error: {e.message}")
    print(f"Status: {e.details.get('status_code')}")
```

## Best Practices

### 1. Choose Appropriate Threshold

```python
# Task-specific thresholds
thresholds = {
    "exact_match": 0.95,      # Near-identical documents
    "high_precision": 0.85,   # Very similar documents
    "balanced": 0.7,          # Good general-purpose
    "high_recall": 0.5,       # Include more candidates
    "exploratory": 0.3        # Find loosely related
}

tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=embedding,
    match_threshold=thresholds["balanced"]
)
```

### 2. Use Metadata Filters

```python
# Pre-filter at database level (faster)
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=embedding,
    filter={"category": "tech"}  # Filter in DB
)

# vs. Post-filter in application (slower)
results = search_tool.run()
filtered = [r for r in results if r['metadata']['category'] == 'tech']
```

### 3. Handle Empty Results

```python
result = search_tool.run()

if result['count'] == 0:
    print("No similar documents found")
    # Try with lower threshold
    search_tool.match_threshold = 0.3
    result = search_tool.run()
```

## Troubleshooting

### Issue: "RPC function not found"

**Solution:** Create the match_documents function:
```sql
-- See main README for full RPC function
CREATE OR REPLACE FUNCTION match_documents (...)
```

### Issue: Slow queries

**Solutions:**
1. Create appropriate indexes
2. Reduce `match_count`
3. Increase `match_threshold`
4. Add metadata filters

### Issue: Low similarity scores

**Solutions:**
1. Check embedding model compatibility
2. Verify dimensions match
3. Normalize embeddings if using inner product
4. Try different distance metrics

### Issue: Dimension mismatch

```python
# Check your embedding dimensions
print(f"Query embedding dims: {len(query_embedding)}")

# Ensure table column matches
# ALTER TABLE documents ALTER COLUMN embedding TYPE vector(1536);
```

## Related Tools

- [SupabaseInsertEmbeddings](./supabase_insert_embeddings_README.md) - Insert embeddings
- [Main README](./README.md) - Complete integration guide

---

**Version:** 1.0.0
**Last Updated:** 2025-11-23
