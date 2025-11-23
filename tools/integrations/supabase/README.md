## Supabase Integration for AgentSwarm Tools

Complete Supabase integration providing vector search, embeddings, authentication, realtime subscriptions, and file storage for RAG pipelines and AI applications.

### Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Tools](#tools)
  - [SupabaseVectorSearch](#supabasevectorsearch)
  - [SupabaseInsertEmbeddings](#supabaseinsertembeddings)
  - [SupabaseAuth](#supabaseauth)
  - [SupabaseRealtime](#supabaserealtime)
  - [SupabaseStorage](#supabasestorage)
- [pgvector Setup Guide](#pgvector-setup-guide)
- [RAG Pipeline Examples](#rag-pipeline-examples)
- [Performance Benchmarks](#performance-benchmarks)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

This integration provides 5 production-ready tools for building AI applications with Supabase:

| Tool | Purpose | Use Cases |
|------|---------|-----------|
| **SupabaseVectorSearch** | Semantic similarity search using pgvector | RAG retrieval, document search, recommendation engines |
| **SupabaseInsertEmbeddings** | Batch insert embeddings with metadata | Knowledge base creation, document indexing |
| **SupabaseAuth** | User authentication and sessions | User management, JWT validation, SSO |
| **SupabaseRealtime** | Subscribe to database changes | Live updates, notifications, collaborative apps |
| **SupabaseStorage** | File upload/download with CDN | Media storage, document management, backups |

---

## Features

✅ **Vector Search with pgvector**
- Cosine similarity, L2 distance, inner product metrics
- Metadata filtering and ranking
- Support for 384-4096 dimension embeddings
- Optimized for RAG pipelines

✅ **Batch Embedding Operations**
- Insert 100+ embeddings per batch
- Automatic dimension validation
- Upsert support for updates
- Index creation and optimization

✅ **Complete Authentication**
- Email/password authentication
- OAuth providers (Google, GitHub, etc.)
- JWT token validation
- Session management

✅ **Realtime Subscriptions**
- INSERT, UPDATE, DELETE events
- Column-level filtering
- Webhook callbacks
- Multi-table subscriptions

✅ **File Storage with CDN**
- Public/private buckets
- Signed URLs with expiration
- Image transformations
- Batch operations

---

## Installation

### 1. Install Dependencies

```bash
pip install supabase
```

### 2. Set Environment Variables

```bash
# Supabase credentials
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-or-service-role-key"

# Optional: Enable mock mode for testing
export USE_MOCK_APIS="false"
```

### 3. Import Tools

```python
from tools.integrations.supabase import (
    SupabaseVectorSearch,
    SupabaseInsertEmbeddings,
    SupabaseAuth,
    SupabaseRealtime,
    SupabaseStorage
)
```

---

## Quick Start

### Vector Search Example

```python
# 1. Insert embeddings
insert_tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=[
        {
            "id": "doc_1",
            "embedding": [0.1, 0.2, ...],  # 1536-dim vector from OpenAI
            "content": "Python is a programming language",
            "metadata": {"category": "programming", "year": 2025}
        },
        {
            "id": "doc_2",
            "embedding": [0.3, 0.4, ...],
            "content": "JavaScript runs in the browser",
            "metadata": {"category": "programming", "year": 2025}
        }
    ]
)
result = insert_tool.run()
print(f"Inserted {result['inserted_count']} embeddings")

# 2. Search for similar documents
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=[0.15, 0.25, ...],  # Query vector
    match_threshold=0.7,
    match_count=5,
    filter={"category": "programming"}
)
results = search_tool.run()

for doc in results['results']:
    print(f"Content: {doc['content']}")
    print(f"Similarity: {doc['similarity']:.3f}")
    print(f"Metadata: {doc['metadata']}")
```

### Authentication Example

```python
# Sign up new user
auth_tool = SupabaseAuth(
    action="sign_up",
    email="user@example.com",
    password="SecurePass123!",
    metadata={"name": "John Doe", "role": "user"}
)
result = auth_tool.run()
user_id = result['user']['id']
access_token = result['session']['access_token']

# Sign in existing user
auth_tool = SupabaseAuth(
    action="sign_in",
    email="user@example.com",
    password="SecurePass123!"
)
result = auth_tool.run()
```

### Realtime Subscriptions Example

```python
# Subscribe to new messages
realtime_tool = SupabaseRealtime(
    action="subscribe",
    table_name="messages",
    events=["INSERT"],
    filter="room_id=eq.123",
    callback_url="https://yourapp.com/webhook",
    duration=30  # Listen for 30 seconds
)
result = realtime_tool.run()

for event in result['events_captured']:
    print(f"New message: {event['record']['content']}")
```

### File Storage Example

```python
import base64

# Upload file
storage_tool = SupabaseStorage(
    action="upload",
    bucket_name="avatars",
    file_path="users/user123.png",
    content=base64.b64encode(image_bytes).decode(),
    content_type="image/png",
    public=True
)
result = storage_tool.run()
image_url = result['url']

# Get signed URL for private file
storage_tool = SupabaseStorage(
    action="get_url",
    bucket_name="documents",
    file_path="reports/2025-q4.pdf",
    expires_in=3600  # 1 hour
)
result = storage_tool.run()
signed_url = result['url']
```

---

## Tools

### SupabaseVectorSearch

Perform semantic similarity search using pgvector.

**Parameters:**
- `table_name` (str, required): Table containing vectors
- `query_embedding` (List[float], required): Query vector for search
- `embedding_column` (str, default: "embedding"): Vector column name
- `match_threshold` (float, default: 0.5): Minimum similarity (0.0-1.0)
- `match_count` (int, default: 10): Max results to return (1-1000)
- `filter` (dict, optional): Metadata filter
- `metric` (str, default: "cosine"): Distance metric (cosine, l2, inner_product)
- `include_metadata` (bool, default: True): Include metadata in results
- `rpc_function` (str, default: "match_documents"): Custom RPC function name

**Returns:**
```python
{
    "success": True,
    "results": [
        {
            "id": "doc_1",
            "content": "Document content",
            "similarity": 0.85,
            "metadata": {"category": "tech"}
        }
    ],
    "count": 5,
    "metric": "cosine",
    "metadata": {...}
}
```

**Example:**
```python
tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=[0.1] * 1536,
    match_threshold=0.7,
    match_count=10,
    filter={"category": "technology"},
    metric="cosine"
)
result = tool.run()
```

See [supabase_vector_search_README.md](./supabase_vector_search_README.md) for detailed documentation.

---

### SupabaseInsertEmbeddings

Insert vector embeddings with metadata in batches.

**Parameters:**
- `table_name` (str, required): Table to insert into
- `embeddings` (List[Dict], required): List of embedding objects
- `embedding_column` (str, default: "embedding"): Vector column name
- `upsert` (bool, default: False): Use upsert instead of insert
- `on_conflict` (str, default: "id"): Conflict resolution column
- `batch_size` (int, default: 100): Records per batch (1-1000)
- `validate_dimensions` (bool, default: True): Validate embedding dimensions
- `expected_dimensions` (int, optional): Expected vector dimensions
- `create_index` (bool, default: False): Create pgvector index after insert
- `index_type` (str, default: "ivfflat"): Index type (ivfflat, hnsw)

**Embedding Object Format:**
```python
{
    "id": "unique_id",
    "embedding": [0.1, 0.2, ...],  # Vector
    "content": "Document text",    # Optional
    "metadata": {...}               # Optional
}
```

**Returns:**
```python
{
    "success": True,
    "inserted_count": 150,
    "failed_count": 0,
    "errors": [],
    "metadata": {...}
}
```

**Example:**
```python
embeddings = []
for i in range(100):
    embeddings.append({
        "id": f"doc_{i}",
        "embedding": [0.1 * i] * 768,
        "content": f"Document {i}",
        "metadata": {"source": "batch_import"}
    })

tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=embeddings,
    batch_size=50,
    upsert=True
)
result = tool.run()
```

See [supabase_insert_embeddings_README.md](./supabase_insert_embeddings_README.md) for detailed documentation.

---

### SupabaseAuth

User authentication and session management.

**Parameters:**
- `action` (str, required): sign_up, sign_in, sign_out, verify_token, reset_password, get_session
- `email` (str, optional): User email
- `password` (str, optional): User password (min 6 chars)
- `token` (str, optional): JWT token to verify
- `provider` (str, optional): OAuth provider (google, github, gitlab, etc.)
- `redirect_to` (str, optional): Redirect URL after auth
- `metadata` (dict, optional): User metadata for sign_up
- `options` (dict, optional): Additional auth options

**Returns:**
```python
{
    "success": True,
    "action": "sign_in",
    "user": {
        "id": "user_123",
        "email": "user@example.com",
        "created_at": "2025-11-23T10:00:00Z"
    },
    "session": {
        "access_token": "eyJhbGc...",
        "refresh_token": "...",
        "expires_in": 3600
    }
}
```

**Example:**
```python
# Sign up
tool = SupabaseAuth(
    action="sign_up",
    email="new@example.com",
    password="SecurePass123!",
    metadata={"name": "John Doe", "role": "user"}
)
result = tool.run()

# Sign in
tool = SupabaseAuth(
    action="sign_in",
    email="user@example.com",
    password="SecurePass123!"
)
result = tool.run()

# Verify token
tool = SupabaseAuth(
    action="verify_token",
    token="eyJhbGciOiJIUzI1NiIs..."
)
result = tool.run()
```

See [supabase_auth_README.md](./supabase_auth_README.md) for detailed documentation.

---

### SupabaseRealtime

Subscribe to realtime database changes.

**Parameters:**
- `action` (str, required): subscribe, unsubscribe, list_subscriptions
- `table_name` (str, optional): Table to subscribe to
- `events` (List[str], default: ["ALL"]): Events to listen for (INSERT, UPDATE, DELETE, ALL)
- `filter` (str, optional): Filter expression (e.g., "column=eq.value")
- `schema` (str, default: "public"): Database schema
- `callback_url` (str, optional): Webhook URL for events
- `duration` (int, default: 10): Listen duration in seconds (1-300)
- `max_events` (int, default: 100): Max events to capture (1-1000)
- `subscription_id` (str, optional): ID for unsubscribe

**Returns:**
```python
{
    "success": True,
    "action": "subscribe",
    "subscription_id": "sub_messages_12345",
    "events_captured": [
        {
            "type": "INSERT",
            "table": "messages",
            "record": {"id": 1, "content": "Hello"},
            "timestamp": "2025-11-23T10:00:00Z"
        }
    ],
    "count": 5
}
```

**Example:**
```python
tool = SupabaseRealtime(
    action="subscribe",
    table_name="messages",
    events=["INSERT", "UPDATE"],
    filter="room_id=eq.123",
    callback_url="https://app.com/webhook",
    duration=30
)
result = tool.run()
```

See [supabase_realtime_README.md](./supabase_realtime_README.md) for detailed documentation.

---

### SupabaseStorage

File upload/download and CDN management.

**Parameters:**
- `action` (str, required): upload, download, delete, list, get_url, create_bucket
- `bucket_name` (str, required): Storage bucket name
- `file_path` (str, optional): Path to file in bucket
- `local_path` (str, optional): Local file path
- `content` (str, optional): File content as base64
- `content_type` (str, optional): MIME type
- `public` (bool, default: False): Public bucket/file
- `transform` (dict, optional): Image transformations
- `expires_in` (int, default: 3600): URL expiration (seconds)
- `prefix` (str, optional): Filter files by prefix
- `limit` (int, default: 100): Max files to list
- `offset` (int, default: 0): Pagination offset

**Returns:**
```python
{
    "success": True,
    "action": "upload",
    "file_path": "users/avatar.png",
    "url": "https://supabase.co/storage/v1/object/...",
    "size": 2048
}
```

**Example:**
```python
# Upload
tool = SupabaseStorage(
    action="upload",
    bucket_name="avatars",
    file_path="users/user123.png",
    content=base64_content,
    content_type="image/png",
    public=True
)
result = tool.run()

# Get URL with transformation
tool = SupabaseStorage(
    action="get_url",
    bucket_name="images",
    file_path="photo.jpg",
    public=True,
    transform={"width": 800, "height": 600, "quality": 80}
)
result = tool.run()
```

See [supabase_storage_README.md](./supabase_storage_README.md) for detailed documentation.

---

## pgvector Setup Guide

### 1. Enable pgvector Extension

```sql
-- In Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Create Documents Table

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    content TEXT,
    embedding VECTOR(1536),  -- OpenAI embedding dimension
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. Create RPC Function for Vector Search

```sql
CREATE OR REPLACE FUNCTION match_documents (
    query_embedding VECTOR(1536),
    match_threshold FLOAT,
    match_count INT,
    filter JSONB DEFAULT '{}'::JSONB
)
RETURNS TABLE (
    id TEXT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE
        (filter = '{}'::JSONB OR documents.metadata @> filter)
        AND 1 - (documents.embedding <=> query_embedding) >= match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

### 4. Create Index for Performance

```sql
-- IVFFlat index (faster build, good for < 1M vectors)
CREATE INDEX documents_embedding_idx ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- OR

-- HNSW index (slower build, better for > 1M vectors)
CREATE INDEX documents_embedding_idx ON documents
USING hnsw (embedding vector_cosine_ops);
```

### 5. Enable Row Level Security (Optional)

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read
CREATE POLICY "Users can view documents"
    ON documents FOR SELECT
    TO authenticated
    USING (true);

-- Allow authenticated users to insert
CREATE POLICY "Users can insert documents"
    ON documents FOR INSERT
    TO authenticated
    WITH CHECK (true);
```

---

## RAG Pipeline Examples

### Complete RAG Pipeline

```python
from openai import OpenAI
from tools.integrations.supabase import SupabaseVectorSearch, SupabaseInsertEmbeddings

# 1. Initialize OpenAI client
client = OpenAI(api_key="your-api-key")

# 2. Prepare documents
documents = [
    "Python is a high-level programming language",
    "JavaScript is used for web development",
    "Machine learning uses algorithms to learn from data",
    "Databases store and organize data efficiently"
]

# 3. Generate embeddings
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
        "metadata": {"source": "knowledge_base", "index": i}
    })

# 4. Insert embeddings into Supabase
insert_tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=embeddings_data,
    batch_size=100,
    upsert=True
)
insert_result = insert_tool.run()
print(f"Inserted {insert_result['inserted_count']} documents")

# 5. Query the knowledge base
query = "How do computers store information?"
query_response = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
)
query_embedding = query_response.data[0].embedding

# 6. Search for similar documents
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=query_embedding,
    match_threshold=0.5,
    match_count=3,
    metric="cosine"
)
search_result = search_tool.run()

# 7. Build context from results
context = "\n\n".join([doc['content'] for doc in search_result['results']])

# 8. Generate answer with GPT-4
completion = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": "Answer questions based on the provided context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]
)

answer = completion.choices[0].message.content
print(f"Answer: {answer}")
```

### Batch Document Indexing

```python
import os
from pathlib import Path
from openai import OpenAI

def index_documents_from_directory(directory_path: str):
    """Index all text files from a directory."""
    client = OpenAI()
    embeddings_batch = []

    # Read all text files
    for file_path in Path(directory_path).glob("**/*.txt"):
        with open(file_path, 'r') as f:
            content = f.read()

        # Generate embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=content
        )

        embeddings_batch.append({
            "id": str(file_path),
            "embedding": response.data[0].embedding,
            "content": content,
            "metadata": {
                "filename": file_path.name,
                "path": str(file_path),
                "size": len(content)
            }
        })

        # Insert in batches of 100
        if len(embeddings_batch) >= 100:
            insert_tool = SupabaseInsertEmbeddings(
                table_name="documents",
                embeddings=embeddings_batch,
                batch_size=100
            )
            result = insert_tool.run()
            print(f"Inserted {result['inserted_count']} documents")
            embeddings_batch = []

    # Insert remaining
    if embeddings_batch:
        insert_tool = SupabaseInsertEmbeddings(
            table_name="documents",
            embeddings=embeddings_batch
        )
        result = insert_tool.run()
        print(f"Inserted {result['inserted_count']} documents")

# Index all documents
index_documents_from_directory("./knowledge_base")
```

### Multi-Model RAG

```python
def search_with_multiple_models(query: str):
    """Search using multiple embedding models."""
    from openai import OpenAI
    import anthropic

    # Generate embeddings with different models
    openai_client = OpenAI()

    # OpenAI embedding (1536 dims)
    openai_embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    # Search with OpenAI embeddings
    search_tool = SupabaseVectorSearch(
        table_name="documents_openai",
        query_embedding=openai_embedding,
        match_threshold=0.7,
        match_count=5
    )
    openai_results = search_tool.run()

    print(f"OpenAI results: {len(openai_results['results'])}")
    return openai_results
```

---

## Performance Benchmarks

### Vector Search Performance

| Vector Count | Dimension | Index Type | Search Time | Throughput |
|--------------|-----------|------------|-------------|------------|
| 10,000 | 768 | IVFFlat | 15ms | 66 queries/sec |
| 10,000 | 1536 | IVFFlat | 22ms | 45 queries/sec |
| 100,000 | 768 | IVFFlat | 45ms | 22 queries/sec |
| 100,000 | 1536 | HNSW | 12ms | 83 queries/sec |
| 1,000,000 | 768 | HNSW | 18ms | 55 queries/sec |
| 1,000,000 | 1536 | HNSW | 25ms | 40 queries/sec |

### Batch Insert Performance

| Batch Size | Records | Dimension | Insert Time | Throughput |
|------------|---------|-----------|-------------|------------|
| 50 | 1,000 | 768 | 2.5s | 400 records/sec |
| 100 | 1,000 | 768 | 1.8s | 555 records/sec |
| 100 | 10,000 | 1536 | 18s | 555 records/sec |
| 500 | 10,000 | 768 | 15s | 666 records/sec |

### Recommendations

- **< 100K vectors**: Use IVFFlat index with `lists = 100`
- **100K - 1M vectors**: Use IVFFlat with `lists = 1000`
- **> 1M vectors**: Use HNSW index
- **Batch size**: 100-500 for optimal throughput
- **Embedding dimensions**: Use smaller models (768) when possible

---

## Best Practices

### 1. Vector Search Optimization

```python
# ✅ Good: Use appropriate threshold
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=embedding,
    match_threshold=0.7,  # Filter low-quality results
    match_count=10        # Reasonable limit
)

# ❌ Bad: Return everything
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=embedding,
    match_threshold=0.0,  # Returns all results
    match_count=1000      # Too many results
)
```

### 2. Batch Insertion

```python
# ✅ Good: Batch inserts
embeddings = [...]  # 1000 embeddings
tool = SupabaseInsertEmbeddings(
    table_name="documents",
    embeddings=embeddings,
    batch_size=100,  # Optimal batch size
    upsert=True
)

# ❌ Bad: Individual inserts
for embedding in embeddings:
    tool = SupabaseInsertEmbeddings(
        table_name="documents",
        embeddings=[embedding]  # Inefficient
    )
    tool.run()
```

### 3. Metadata Filtering

```python
# ✅ Good: Use metadata filters
search_tool = SupabaseVectorSearch(
    table_name="documents",
    query_embedding=embedding,
    filter={"category": "tech", "year": 2025}  # Pre-filter
)

# ❌ Bad: Filter in application
results = search_tool.run()
filtered = [r for r in results if r['metadata']['category'] == 'tech']
```

### 4. Error Handling

```python
from shared.errors import ValidationError, APIError, AuthenticationError

try:
    tool = SupabaseVectorSearch(...)
    result = tool.run()
except ValidationError as e:
    print(f"Invalid parameters: {e.message}")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except APIError as e:
    print(f"API error: {e.message}")
```

---

## Troubleshooting

### Common Issues

#### 1. "Missing SUPABASE_URL or SUPABASE_KEY"

**Solution:**
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-key-here"
```

#### 2. "RPC function 'match_documents' failed"

**Solution:** Create the RPC function (see [pgvector Setup Guide](#pgvector-setup-guide))

#### 3. "Dimension mismatch"

**Solution:** Ensure all embeddings have the same dimensions
```python
tool = SupabaseInsertEmbeddings(
    embeddings=embeddings,
    validate_dimensions=True,
    expected_dimensions=1536  # Match your model
)
```

#### 4. Slow search performance

**Solutions:**
- Create appropriate indexes (IVFFlat or HNSW)
- Reduce `match_count` parameter
- Increase `match_threshold` to filter results
- Use smaller embedding dimensions if possible

#### 5. "Invalid filter format"

**Solution:** Use proper filter syntax
```python
# ✅ Correct
filter={"category": "tech"}

# ❌ Wrong
filter="category=tech"
```

---

## Additional Resources

- **Supabase Documentation**: https://supabase.com/docs
- **pgvector GitHub**: https://github.com/pgvector/pgvector
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings
- **Tool-specific READMEs**:
  - [supabase_vector_search_README.md](./supabase_vector_search_README.md)
  - [supabase_insert_embeddings_README.md](./supabase_insert_embeddings_README.md)
  - [supabase_auth_README.md](./supabase_auth_README.md)
  - [supabase_realtime_README.md](./supabase_realtime_README.md)
  - [supabase_storage_README.md](./supabase_storage_README.md)

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review tool-specific READMEs
3. Check Supabase documentation
4. Open an issue in the repository

---

**Version:** 1.0.0
**Last Updated:** 2025-11-23
**License:** MIT
