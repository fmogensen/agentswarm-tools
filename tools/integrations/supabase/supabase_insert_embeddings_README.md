# SupabaseInsertEmbeddings

Batch insert vector embeddings into Supabase with metadata support.

## Overview

Efficiently insert embeddings for RAG pipelines, knowledge bases, and semantic search applications. Supports batch processing, upserts, and automatic dimension validation.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `table_name` | str | Yes | - | Table to insert embeddings into |
| `embeddings` | List[Dict] | Yes | - | List of embedding objects |
| `embedding_column` | str | No | "embedding" | Vector column name |
| `upsert` | bool | No | False | Use upsert instead of insert |
| `on_conflict` | str | No | "id" | Conflict resolution column |
| `batch_size` | int | No | 100 | Records per batch (1-1000) |
| `validate_dimensions` | bool | No | True | Validate embedding dimensions |
| `expected_dimensions` | int | No | None | Expected embedding size |
| `create_index` | bool | No | False | Create pgvector index after insert |
| `index_type` | str | No | "ivfflat" | Index type (ivfflat, hnsw) |

## Embedding Object Format

```python
{
    "id": "unique_identifier",        # Required
    "embedding": [0.1, 0.2, ...],     # Required: List of floats
    "content": "Document text",       # Optional
    "metadata": {...},                # Optional: Any JSON-serializable data
    # ... any other columns
}
```

## Examples

### Basic Insert

```python
from tools.integrations.supabase import SupabaseInsertEmbeddings
from openai import OpenAI

client = OpenAI()

# Generate embeddings
documents = ["Python guide", "JavaScript tutorial", "ML basics"]
embeddings_data = []

for i, doc in enumerate(documents):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=doc
    )
    embeddings_data.append({
        "id": f"doc_{i}",
        "embedding": response.data[0].embedding,
        "content": doc,
        "metadata": {"category": "programming"}
    })

# Insert into Supabase
tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=embeddings_data
)
result = tool.run()

print(f"Inserted: {result['inserted_count']}")
print(f"Failed: {result['failed_count']}")
```

### Batch Insert with Upsert

```python
# Large batch of embeddings
embeddings = []
for i in range(1000):
    embeddings.append({
        "id": f"doc_{i}",
        "embedding": [0.1 * i % 1.0] * 1536,
        "content": f"Document {i}",
        "metadata": {"batch": "2025-11-23"}
    })

# Insert in batches of 100, update if exists
tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=embeddings,
    batch_size=100,
    upsert=True,
    on_conflict="id"
)
result = tool.run()
```

### Dimension Validation

```python
# Ensure all embeddings have correct dimensions
tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=embeddings_data,
    validate_dimensions=True,
    expected_dimensions=1536  # OpenAI text-embedding-3-small
)
result = tool.run()
```

### Create Index After Insert

```python
# Insert and automatically create index
tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=large_embedding_batch,
    batch_size=500,
    create_index=True,
    index_type="ivfflat"  # or "hnsw" for > 1M vectors
)
result = tool.run()
```

## Performance

### Batch Size Recommendations

| Total Records | Batch Size | Insert Time | Throughput |
|---------------|------------|-------------|------------|
| 100 | 50 | 0.3s | 333 rec/s |
| 1,000 | 100 | 1.8s | 555 rec/s |
| 10,000 | 500 | 15s | 666 rec/s |
| 100,000 | 500 | 150s | 666 rec/s |

### Best Practices

```python
# ✅ Good: Optimal batch size
tool = SupabaseInsertEmbeddings(
    embeddings=large_list,
    batch_size=100  # Sweet spot for most cases
)

# ✅ Good: Validate dimensions
tool = SupabaseInsertEmbeddings(
    embeddings=embeddings,
    validate_dimensions=True,
    expected_dimensions=1536
)

# ✅ Good: Use upsert for updates
tool = SupabaseInsertEmbeddings(
    embeddings=updated_docs,
    upsert=True
)

# ❌ Bad: Batch size too small
tool = SupabaseInsertEmbeddings(
    embeddings=large_list,
    batch_size=1  # Very inefficient
)

# ❌ Bad: No validation
tool = SupabaseInsertEmbeddings(
    embeddings=mixed_dimensions,
    validate_dimensions=False  # May cause errors
)
```

## Error Handling

```python
from shared.errors import ValidationError

try:
    tool = SupabaseInsertEmbeddings(
        table_name="documents",
        embeddings=embeddings_data
    )
    result = tool.run()

    if result['failed_count'] > 0:
        print(f"Errors: {result['errors']}")

except ValidationError as e:
    print(f"Validation failed: {e.message}")
    if 'dimension' in e.message.lower():
        print("Check embedding dimensions match table column")
```

## Common Use Cases

### 1. Index Existing Documents

```python
import json

def index_jsonl_file(file_path: str):
    """Index documents from JSONL file."""
    from openai import OpenAI
    client = OpenAI()

    embeddings = []
    with open(file_path) as f:
        for line in f:
            doc = json.loads(line)

            # Generate embedding
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=doc['content']
            )

            embeddings.append({
                "id": doc['id'],
                "embedding": response.data[0].embedding,
                "content": doc['content'],
                "metadata": doc.get('metadata', {})
            })

            # Insert in batches of 100
            if len(embeddings) >= 100:
                tool = SupabaseInsertEmbeddings(
                    table_name="documents",
                    embeddings=embeddings
                )
                result = tool.run()
                print(f"Inserted {result['inserted_count']}")
                embeddings = []

    # Insert remaining
    if embeddings:
        tool = SupabaseInsertEmbeddings(
            table_name="documents",
            embeddings=embeddings
        )
        result = tool.run()
```

### 2. Update Existing Embeddings

```python
# Re-embed documents with new model
updated_embeddings = []
for doc_id, new_embedding in updates:
    updated_embeddings.append({
        "id": doc_id,
        "embedding": new_embedding
    })

tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=updated_embeddings,
    upsert=True  # Update existing records
)
result = tool.run()
```

### 3. Multi-column Metadata

```python
embeddings = [{
    "id": "doc_1",
    "embedding": [0.1] * 768,
    "content": "Document content",
    "title": "Document Title",
    "author": "John Doe",
    "published_date": "2025-11-23",
    "tags": ["ai", "ml", "nlp"],
    "metadata": {
        "source": "web_scrape",
        "confidence": 0.95,
        "nested": {"key": "value"}
    }
}]

tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=embeddings
)
result = tool.run()
```

## Troubleshooting

### Issue: Dimension mismatch error

**Solution:**
```python
# Check your embeddings
for emb in embeddings:
    print(f"ID: {emb['id']}, Dims: {len(emb['embedding'])}")

# Set expected dimensions
tool = SupabaseInsertEmbeddings(
    embeddings=embeddings,
    expected_dimensions=1536
)
```

### Issue: Upsert not working

**Solution:** Ensure conflict column exists
```sql
-- Add unique constraint
ALTER TABLE documents ADD CONSTRAINT documents_id_unique UNIQUE (id);
```

### Issue: Insert fails silently

**Solution:** Check errors in result
```python
result = tool.run()
if result['failed_count'] > 0:
    for error in result['errors']:
        print(f"Error: {error}")
```

---

**Version:** 1.0.0
