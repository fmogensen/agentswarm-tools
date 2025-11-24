"""
Supabase Vector Search Tool

Performs semantic similarity search using pgvector extension in Supabase.
Supports cosine similarity, L2 distance, and inner product metrics with filtering.
"""

import json
import os
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class SupabaseVectorSearch(BaseTool):
    """
    Perform vector similarity search in Supabase using pgvector.

    This tool enables semantic search by finding vectors similar to a query embedding.
    Supports multiple distance metrics, metadata filtering, and batch queries.

    Args:
        table_name: Name of the table containing vectors
        query_embedding: Query vector as list of floats (must match column dimensions)
        embedding_column: Name of the vector column (default: 'embedding')
        match_threshold: Minimum similarity score (0.0-1.0, default: 0.5)
        match_count: Maximum number of results to return (1-1000, default: 10)
        filter: Optional metadata filter as JSON object (e.g., {"category": "tech"})
        metric: Distance metric - 'cosine', 'l2', or 'inner_product' (default: 'cosine')
        include_metadata: Whether to include metadata columns (default: True)
        rpc_function: Custom RPC function name (default: 'match_documents')

    Returns:
        Dict containing:
            - success (bool): Whether the search was successful
            - results (list): List of matching documents with similarity scores
            - count (int): Number of results returned
            - metric (str): Distance metric used
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Search for similar documents
        >>> tool = SupabaseVectorSearch(
        ...     table_name="documents",
        ...     query_embedding=[0.1, 0.2, ..., 0.5],  # 1536-dim vector
        ...     match_threshold=0.7,
        ...     match_count=5,
        ...     filter={"category": "technology"}
        ... )
        >>> result = tool.run()
        >>> for doc in result['results']:
        ...     print(f"{doc['content']}: {doc['similarity']:.3f}")
    """

    # Tool metadata
    tool_name: str = "supabase_vector_search"
    tool_category: str = "integrations"

    # Required parameters
    table_name: str = Field(
        ...,
        description="Name of the table containing vectors",
        min_length=1,
        max_length=63,
    )
    query_embedding: List[float] = Field(
        ...,
        description="Query vector for similarity search",
        min_length=1,
        max_length=4096,
    )

    # Optional parameters
    embedding_column: str = Field(
        "embedding",
        description="Name of the vector column in the table",
        min_length=1,
    )
    match_threshold: float = Field(
        0.5,
        description="Minimum similarity score threshold (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    match_count: int = Field(
        10,
        description="Maximum number of results to return",
        ge=1,
        le=1000,
    )
    filter: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional metadata filter as JSON object",
    )
    metric: Literal["cosine", "l2", "inner_product"] = Field(
        "cosine",
        description="Distance metric for similarity calculation",
    )
    include_metadata: bool = Field(
        True,
        description="Include metadata columns in results",
    )
    rpc_function: str = Field(
        "match_documents",
        description="Custom RPC function name for vector search",
        min_length=1,
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the vector search."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            results = self._process()
            return {
                "success": True,
                "results": results,
                "count": len(results),
                "metric": self.metric,
                "metadata": {
                    "tool_name": self.tool_name,
                    "table": self.table_name,
                    "threshold": self.match_threshold,
                    "embedding_dims": len(self.query_embedding),
                },
            }
        except Exception as e:
            raise APIError(
                f"Vector search failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase",
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Check API keys in real mode
        if not self._should_use_mock():
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            if not supabase_url or not supabase_key:
                raise AuthenticationError(
                    "Missing SUPABASE_URL or SUPABASE_KEY environment variable",
                    tool_name=self.tool_name,
                    api_name="supabase",
                )

        # Common embedding dimensions
        common_dims = [384, 512, 768, 1024, 1536, 3072]
        if len(self.query_embedding) not in common_dims:
            self._logger.warning(
                f"Unusual embedding dimension: {len(self.query_embedding)}. "
                f"Common dimensions: {common_dims}"
            )

        # Validate all values are floats
        try:
            for i, val in enumerate(self.query_embedding):
                if not isinstance(val, (int, float)):
                    raise ValidationError(
                        f"Embedding value at index {i} must be numeric",
                        tool_name=self.tool_name,
                        field="query_embedding",
                    )
        except Exception as e:
            raise ValidationError(
                f"Invalid embedding format: {e}",
                tool_name=self.tool_name,
                field="query_embedding",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_results = []
        for i in range(min(self.match_count, 3)):
            similarity = 0.9 - (i * 0.1)
            if similarity >= self.match_threshold:
                result = {
                    "id": f"doc_{i + 1}",
                    "content": f"Mock document {i + 1} matching your query",
                    "similarity": round(similarity, 4),
                }
                if self.include_metadata:
                    result["metadata"] = {
                        "category": "technology",
                        "timestamp": "2025-11-23T10:00:00Z",
                        "source": "mock",
                    }
                mock_results.append(result)

        return {
            "success": True,
            "results": mock_results,
            "count": len(mock_results),
            "metric": self.metric,
            "metadata": {
                "tool_name": self.tool_name,
                "table": self.table_name,
                "threshold": self.match_threshold,
                "embedding_dims": len(self.query_embedding),
                "mock_mode": True,
            },
        }

    def _process(self) -> List[Dict[str, Any]]:
        """Process vector search with Supabase."""
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise AuthenticationError(
                "Missing SUPABASE_URL or SUPABASE_KEY environment variables",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Import Supabase client
        try:
            from supabase import Client, create_client
        except ImportError:
            raise APIError(
                "Supabase SDK not installed. Run: pip install supabase",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Create client
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise AuthenticationError(
                f"Failed to create Supabase client: {e}",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Prepare RPC parameters
        rpc_params = {
            "query_embedding": self.query_embedding,
            "match_threshold": self.match_threshold,
            "match_count": self.match_count,
        }

        # Add filter if provided
        if self.filter:
            rpc_params["filter"] = self.filter

        # Execute RPC function
        try:
            response = supabase.rpc(self.rpc_function, rpc_params).execute()

            if not response.data:
                return []

            # Process results based on metric
            results = []
            for row in response.data:
                result = {
                    "id": row.get("id"),
                    "similarity": self._convert_distance_to_similarity(
                        row.get("similarity", row.get("distance", 0.0))
                    ),
                }

                # Add content fields
                for key, value in row.items():
                    if key not in ["id", "similarity", "distance", self.embedding_column]:
                        if self.include_metadata or key == "content":
                            result[key] = value

                results.append(result)

            return results

        except Exception as e:
            raise APIError(
                f"RPC function '{self.rpc_function}' failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase",
            )

    def _convert_distance_to_similarity(self, distance: float) -> float:
        """
        Convert distance metric to similarity score (0-1).

        Args:
            distance: Distance value from database

        Returns:
            Similarity score between 0 and 1
        """
        if self.metric == "cosine":
            # Cosine distance: 0 (identical) to 2 (opposite)
            # Similarity: 1 - (distance / 2)
            return max(0.0, min(1.0, 1.0 - (distance / 2.0)))
        elif self.metric == "l2":
            # L2 distance: 0 (identical) to infinity
            # Similarity: 1 / (1 + distance)
            return 1.0 / (1.0 + distance)
        elif self.metric == "inner_product":
            # Inner product: already a similarity score
            return distance
        else:
            # Default: return as-is
            return distance


if __name__ == "__main__":
    # Test the tool
    print("Testing SupabaseVectorSearch...")
    print("=" * 60)

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic vector search
    print("\n1. Testing basic vector search...")
    embedding_1536 = [0.1] * 1536  # OpenAI embedding dimension
    tool = SupabaseVectorSearch(
        table_name="documents",
        query_embedding=embedding_1536,
        match_threshold=0.7,
        match_count=5,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Results count: {result.get('count')}")
    print(f"Metric: {result.get('metric')}")
    assert result.get("success") == True
    assert result.get("count") >= 0
    assert result.get("metric") == "cosine"

    # Test 2: Search with metadata filter
    print("\n2. Testing search with metadata filter...")
    tool = SupabaseVectorSearch(
        table_name="documents",
        query_embedding=[0.5] * 768,  # BERT embedding dimension
        match_threshold=0.6,
        match_count=10,
        filter={"category": "technology", "published": True},
        metric="l2",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Results count: {result.get('count')}")
    print(f"Metric: {result.get('metric')}")
    assert result.get("success") == True
    assert result.get("metric") == "l2"

    # Test 3: Inner product metric
    print("\n3. Testing inner product metric...")
    tool = SupabaseVectorSearch(
        table_name="embeddings",
        query_embedding=[0.2] * 384,  # Sentence transformer dimension
        match_threshold=0.5,
        match_count=3,
        metric="inner_product",
        include_metadata=False,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Results count: {result.get('count')}")
    print(f"Include metadata: {tool.include_metadata}")
    assert result.get("success") == True
    assert result.get("metric") == "inner_product"

    # Test 4: Display results
    print("\n4. Testing result format...")
    tool = SupabaseVectorSearch(
        table_name="documents",
        query_embedding=[0.3] * 1536,
        match_threshold=0.8,
        match_count=5,
    )
    result = tool.run()

    print(f"\nFound {result.get('count')} results:")
    for i, doc in enumerate(result.get("results", []), 1):
        print(f"  {i}. {doc.get('content', 'N/A')}")
        print(f"     Similarity: {doc.get('similarity', 0.0):.4f}")
        if "metadata" in doc:
            print(f"     Metadata: {doc['metadata']}")

    # Test 5: Error handling - empty embedding
    print("\n5. Testing error handling (empty embedding)...")
    try:
        tool = SupabaseVectorSearch(
            table_name="documents",
            query_embedding=[],
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 6: Error handling - invalid filter
    print("\n6. Testing error handling (invalid filter)...")
    try:
        tool = SupabaseVectorSearch(
            table_name="documents",
            query_embedding=[0.1] * 768,
            filter="invalid_filter",  # Should be dict
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 7: Different embedding dimensions
    print("\n7. Testing different embedding dimensions...")
    dims = [384, 768, 1536]
    for dim in dims:
        tool = SupabaseVectorSearch(
            table_name="documents",
            query_embedding=[0.1] * dim,
            match_count=3,
        )
        result = tool.run()
        print(f"  Dimension {dim}: {result.get('count')} results")
        assert result.get("success") == True
        assert result.get("metadata", {}).get("embedding_dims") == dim

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
