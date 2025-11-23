# Complete RAG Pipeline with Supabase

Production-ready Retrieval-Augmented Generation pipeline using Supabase vector search.

## Overview

This example demonstrates a complete RAG system with:
- Document ingestion and chunking
- Embedding generation (OpenAI)
- Vector storage and indexing
- Semantic search
- Context-aware answer generation

## Architecture

```
┌─────────────────┐
│   Documents     │
│  (PDF, TXT)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text Chunking  │
│   (LangChain)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Embeddings    │
│    (OpenAI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Supabase     │
│  Vector Store   │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Query  │
    └───┬────┘
        │
        ▼
┌─────────────────┐
│ Vector Search   │
│   (pgvector)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Context + GPT-4 │
│   Answer Gen    │
└─────────────────┘
```

## Complete Implementation

### 1. Setup

```python
import os
from pathlib import Path
from typing import List, Dict, Any
from openai import OpenAI
from tools.integrations.supabase import (
    SupabaseVectorSearch,
    SupabaseInsertEmbeddings
)

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configure embedding model
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
```

### 2. Document Processing

```python
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)

    return chunks


def process_document(file_path: str, doc_id: str) -> List[Dict[str, Any]]:
    """Process document into chunks with metadata."""
    # Read document
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Chunk text
    chunks = chunk_text(content)

    # Prepare chunks with metadata
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        processed_chunks.append({
            "id": f"{doc_id}_chunk_{i}",
            "content": chunk,
            "metadata": {
                "doc_id": doc_id,
                "chunk_index": i,
                "source_file": os.path.basename(file_path),
                "chunk_count": len(chunks)
            }
        })

    return processed_chunks
```

### 3. Embedding Generation

```python
def generate_embeddings(chunks: List[Dict[str, Any]], batch_size: int = 100) -> List[Dict[str, Any]]:
    """Generate embeddings for chunks."""
    embeddings_data = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        # Generate embeddings for batch
        texts = [chunk["content"] for chunk in batch]
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )

        # Combine embeddings with chunks
        for j, chunk in enumerate(batch):
            embeddings_data.append({
                **chunk,
                "embedding": response.data[j].embedding
            })

        print(f"Generated embeddings for {len(embeddings_data)} chunks")

    return embeddings_data
```

### 4. Index Documents

```python
def index_documents(documents_dir: str, table_name: str = "documents"):
    """Index all documents from a directory."""
    all_chunks = []

    # Process all text files
    for file_path in Path(documents_dir).glob("**/*.txt"):
        doc_id = file_path.stem
        chunks = process_document(str(file_path), doc_id)
        all_chunks.extend(chunks)
        print(f"Processed {file_path.name}: {len(chunks)} chunks")

    # Generate embeddings
    embeddings_data = generate_embeddings(all_chunks)

    # Insert into Supabase
    insert_tool = SupabaseInsertEmbeddings(
        table_name=table_name,
        embeddings=embeddings_data,
        batch_size=100,
        upsert=True,
        validate_dimensions=True,
        expected_dimensions=EMBEDDING_DIMENSIONS
    )

    result = insert_tool.run()
    print(f"\nIndexing complete:")
    print(f"  - Total chunks: {len(all_chunks)}")
    print(f"  - Inserted: {result['inserted_count']}")
    print(f"  - Failed: {result['failed_count']}")

    return result


# Example usage
if __name__ == "__main__":
    # Index knowledge base
    index_documents("./knowledge_base", "documents")
```

### 5. Query Pipeline

```python
class RAGPipeline:
    """Complete RAG pipeline."""

    def __init__(
        self,
        table_name: str = "documents",
        embedding_model: str = EMBEDDING_MODEL,
        llm_model: str = "gpt-4-turbo-preview"
    ):
        self.table_name = table_name
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.openai_client = OpenAI()

    def query(
        self,
        question: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        filter_metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Query the RAG pipeline.

        Args:
            question: User question
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
            filter_metadata: Optional metadata filter

        Returns:
            Dictionary with answer, sources, and metadata
        """
        # 1. Generate query embedding
        query_response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=question
        )
        query_embedding = query_response.data[0].embedding

        # 2. Search for similar documents
        search_tool = SupabaseVectorSearch(
            table_name=self.table_name,
            query_embedding=query_embedding,
            match_threshold=similarity_threshold,
            match_count=top_k,
            filter=filter_metadata,
            metric="cosine"
        )
        search_result = search_tool.run()

        if search_result['count'] == 0:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "sources": [],
                "confidence": 0.0
            }

        # 3. Build context from results
        context_parts = []
        sources = []

        for i, doc in enumerate(search_result['results'], 1):
            context_parts.append(f"[{i}] {doc['content']}")
            sources.append({
                "content": doc['content'],
                "similarity": doc['similarity'],
                "metadata": doc.get('metadata', {})
            })

        context = "\n\n".join(context_parts)

        # 4. Generate answer with GPT-4
        completion = self.openai_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that answers questions based on the provided context. "
                        "Always cite your sources using [1], [2], etc. "
                        "If the context doesn't contain enough information, say so."
                    )
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ],
            temperature=0.3
        )

        answer = completion.choices[0].message.content

        # 5. Calculate confidence based on similarity scores
        avg_similarity = sum(doc['similarity'] for doc in search_result['results']) / len(search_result['results'])

        return {
            "answer": answer,
            "sources": sources,
            "confidence": avg_similarity,
            "retrieved_count": search_result['count']
        }


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    rag = RAGPipeline(table_name="documents")

    # Query
    result = rag.query(
        question="How do I optimize database queries?",
        top_k=5,
        similarity_threshold=0.7
    )

    # Display results
    print("Answer:")
    print(result['answer'])
    print(f"\nConfidence: {result['confidence']:.2%}")
    print(f"\nSources ({len(result['sources'])}):")
    for i, source in enumerate(result['sources'], 1):
        print(f"\n[{i}] Similarity: {source['similarity']:.3f}")
        print(f"Content: {source['content'][:100]}...")
```

### 6. Advanced Features

#### Hybrid Search (Vector + Keyword)

```python
def hybrid_search(
    self,
    question: str,
    keywords: List[str],
    top_k: int = 10
) -> Dict[str, Any]:
    """Combine vector search with keyword filtering."""
    # Vector search
    vector_results = self.query(question, top_k=top_k * 2)

    # Filter by keywords
    filtered_sources = []
    for source in vector_results['sources']:
        content_lower = source['content'].lower()
        if any(keyword.lower() in content_lower for keyword in keywords):
            filtered_sources.append(source)

    # Rerank and limit
    filtered_sources = filtered_sources[:top_k]

    # Regenerate answer with filtered context
    if not filtered_sources:
        return {
            "answer": "No results matching your keywords.",
            "sources": [],
            "confidence": 0.0
        }

    # ... (generate answer from filtered sources)
```

#### Multi-query RAG

```python
def multi_query_rag(self, question: str) -> Dict[str, Any]:
    """Generate multiple query variations for better retrieval."""
    # Generate query variations
    variations_prompt = f"Generate 3 variations of this question: {question}"
    variations_response = self.openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": variations_prompt}]
    )

    # Parse variations (implement parsing logic)
    query_variations = [question]  # Include original + variations

    # Search with each variation
    all_results = []
    seen_ids = set()

    for query_text in query_variations:
        result = self.query(query_text, top_k=3)
        for source in result['sources']:
            doc_id = source['metadata'].get('id')
            if doc_id not in seen_ids:
                all_results.append(source)
                seen_ids.add(doc_id)

    # Rerank and generate final answer
    # ... (implementation)
```

---

## Production Deployment

### Docker Compose Setup

```yaml
version: '3.8'

services:
  rag-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./knowledge_base:/app/knowledge_base
```

### FastAPI Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
rag_pipeline = RAGPipeline()

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    similarity_threshold: float = 0.7

@app.post("/query")
async def query_rag(request: QueryRequest):
    try:
        result = rag_pipeline.query(
            question=request.question,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Performance Optimization

### 1. Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_query(question_hash: str, top_k: int):
    # Implement caching logic
    pass
```

### 2. Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_embed(chunks: List[str], batch_size: int = 10):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            futures.append(executor.submit(generate_embeddings, batch))

        results = [f.result() for f in futures]
    return [emb for batch in results for emb in batch]
```

---

**Full code:** `/examples/rag_pipeline_complete.py`
**Version:** 1.0.0
**Last Updated:** 2025-11-23
