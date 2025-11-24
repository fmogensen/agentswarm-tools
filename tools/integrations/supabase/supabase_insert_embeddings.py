"""
Supabase Insert Embeddings Tool

Inserts vector embeddings into Supabase with metadata support.
Supports batch inserts, upserts, and automatic index optimization.
"""

import json
import os
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class SupabaseInsertEmbeddings(BaseTool):
    """
    Insert vector embeddings into Supabase table with metadata.

    This tool enables batch insertion of embeddings for RAG pipelines,
    semantic search, and vector similarity applications. Supports upserts,
    automatic indexing, and metadata storage.

    Args:
        table_name: Name of the table to insert into
        embeddings: List of embedding objects with 'id', 'embedding', and optional metadata
        embedding_column: Name of the vector column (default: 'embedding')
        upsert: Whether to use upsert (update if exists) instead of insert (default: False)
        on_conflict: Columns to check for conflicts during upsert (default: 'id')
        batch_size: Number of records to insert per batch (1-1000, default: 100)
        validate_dimensions: Whether to validate embedding dimensions (default: True)
        expected_dimensions: Expected embedding dimensions (optional)
        create_index: Whether to create pgvector index after insert (default: False)
        index_type: Type of index - 'ivfflat' or 'hnsw' (default: 'ivfflat')

    Returns:
        Dict containing:
            - success (bool): Whether the insertion was successful
            - inserted_count (int): Number of records inserted
            - failed_count (int): Number of records that failed
            - errors (list): List of errors if any
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Insert embeddings with metadata
        >>> embeddings = [
        ...     {
        ...         "id": "doc_1",
        ...         "embedding": [0.1, 0.2, ..., 0.5],
        ...         "content": "First document",
        ...         "metadata": {"category": "tech", "timestamp": "2025-11-23"}
        ...     },
        ...     {
        ...         "id": "doc_2",
        ...         "embedding": [0.3, 0.4, ..., 0.6],
        ...         "content": "Second document",
        ...         "metadata": {"category": "science", "timestamp": "2025-11-23"}
        ...     }
        ... ]
        >>> tool = SupabaseInsertEmbeddings(
        ...     table_name="documents",
        ...     embeddings=embeddings,
        ...     upsert=True,
        ...     batch_size=100
        ... )
        >>> result = tool.run()
        >>> print(f"Inserted {result['inserted_count']} embeddings")
    """

    # Tool metadata
    tool_name: str = "supabase_insert_embeddings"
    tool_category: str = "integrations"

    # Required parameters
    table_name: str = Field(
        ...,
        description="Name of the table to insert into",
        min_length=1,
        max_length=63,
        pattern=r"^.+$",  # Ensure not empty after strip
    )
    embeddings: List[Dict[str, Any]] = Field(
        ...,
        description="List of embedding objects with id, embedding, and metadata",
        min_length=1,
    )

    # Optional parameters
    embedding_column: str = Field(
        "embedding",
        description="Name of the vector column in the table",
        min_length=1,
    )
    upsert: bool = Field(
        False,
        description="Use upsert (update if exists) instead of insert",
    )
    on_conflict: str = Field(
        "id",
        description="Column(s) to check for conflicts during upsert",
    )
    batch_size: int = Field(
        100,
        description="Number of records to insert per batch",
        ge=1,
        le=1000,
    )
    validate_dimensions: bool = Field(
        True,
        description="Validate that all embeddings have same dimensions",
    )
    expected_dimensions: Optional[int] = Field(
        None,
        description="Expected embedding dimensions (optional)",
        ge=1,
        le=4096,
    )
    create_index: bool = Field(
        False,
        description="Create pgvector index after insert",
    )
    index_type: Literal["ivfflat", "hnsw"] = Field(
        "ivfflat",
        description="Type of vector index to create",
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the embedding insertion."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            inserted, failed, errors = self._process()
            return {
                "success": failed == 0,
                "inserted_count": inserted,
                "failed_count": failed,
                "errors": errors,
                "metadata": {
                    "tool_name": self.tool_name,
                    "table": self.table_name,
                    "total_records": len(self.embeddings),
                    "batch_size": self.batch_size,
                    "upsert": self.upsert,
                },
            }
        except Exception as e:
            raise APIError(
                f"Embedding insertion failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase",
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate table name
        if not self.table_name or not self.table_name.strip():
            raise ValidationError(
                "Table name cannot be empty",
                tool_name=self.tool_name,
                field="table_name",
            )

        # Validate each embedding
        embedding_dims = None
        for i, emb in enumerate(self.embeddings):
            # Check required fields
            if not isinstance(emb, dict):
                raise ValidationError(
                    f"Embedding at index {i} must be a dictionary",
                    tool_name=self.tool_name,
                    field="embeddings",
                )

            if "id" not in emb:
                raise ValidationError(
                    "Each embedding must have an 'id' field",
                    tool_name=self.tool_name,
                    field="embeddings",
                )

            if "embedding" not in emb:
                raise ValidationError(
                    "Each embedding must have an 'embedding' field",
                    tool_name=self.tool_name,
                    field="embeddings",
                )

            # Validate embedding is a list of numbers
            embedding = emb["embedding"]
            if not isinstance(embedding, list):
                raise ValidationError(
                    "Embedding must be a list of numbers",
                    tool_name=self.tool_name,
                    field="embeddings",
                )

            if len(embedding) == 0:
                raise ValidationError(
                    f"Embedding at index {i} cannot be empty",
                    tool_name=self.tool_name,
                    field="embeddings",
                )

            # Check all values are numeric
            for j, val in enumerate(embedding):
                if not isinstance(val, (int, float)):
                    raise ValidationError(
                        f"Embedding value at index {j} must be numeric",
                        tool_name=self.tool_name,
                        field="embeddings",
                    )

            # Validate dimensions consistency
            if self.validate_dimensions:
                current_dims = len(embedding)

                # Check against expected dimensions
                if self.expected_dimensions and current_dims != self.expected_dimensions:
                    raise ValidationError(
                        f"Embedding at index {i} has {current_dims} dimensions, "
                        f"expected {self.expected_dimensions}",
                        tool_name=self.tool_name,
                        field="embeddings",
                    )

                # Check all embeddings have same dimensions
                if embedding_dims is None:
                    embedding_dims = current_dims
                elif current_dims != embedding_dims:
                    raise ValidationError(
                        "All embeddings must have the same dimension",
                        tool_name=self.tool_name,
                        field="embeddings",
                    )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        total = len(self.embeddings)
        inserted = total
        failed = 0
        errors = []

        return {
            "success": True,
            "inserted_count": inserted,
            "failed_count": failed,
            "errors": errors,
            "metadata": {
                "tool_name": self.tool_name,
                "table": self.table_name,
                "total_records": total,
                "batch_size": self.batch_size,
                "upsert": self.upsert,
                "mock_mode": True,
            },
        }

    def _process(self) -> tuple[int, int, List[str]]:
        """Process embedding insertion with Supabase."""
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

        # Process in batches
        inserted_count = 0
        failed_count = 0
        errors = []

        for i in range(0, len(self.embeddings), self.batch_size):
            batch = self.embeddings[i : i + self.batch_size]

            try:
                # Prepare records for insertion
                records = []
                for emb in batch:
                    record = {k: v for k, v in emb.items()}
                    records.append(record)

                # Insert or upsert
                if self.upsert:
                    response = (
                        supabase.table(self.table_name)
                        .upsert(records, on_conflict=self.on_conflict)
                        .execute()
                    )
                else:
                    response = supabase.table(self.table_name).insert(records).execute()

                inserted_count += len(batch)

            except Exception as e:
                failed_count += len(batch)
                error_msg = f"Batch {i // self.batch_size + 1} failed: {str(e)}"
                errors.append(error_msg)
                self._logger.error(error_msg)

        # Create index if requested
        if self.create_index and inserted_count > 0:
            try:
                self._create_vector_index(supabase)
            except Exception as e:
                self._logger.warning(f"Failed to create index: {e}")

        return inserted_count, failed_count, errors

    def _create_vector_index(self, supabase: Any) -> None:
        """
        Create pgvector index on the embedding column.

        Args:
            supabase: Supabase client instance
        """
        # Index creation requires SQL execution
        # This would typically be done through database migrations or SQL runner
        index_name = f"{self.table_name}_{self.embedding_column}_idx"

        if self.index_type == "ivfflat":
            # IVFFlat index - faster build, good for < 1M vectors
            sql = f"""
            CREATE INDEX IF NOT EXISTS {index_name}
            ON {self.table_name}
            USING ivfflat ({self.embedding_column} vector_cosine_ops)
            WITH (lists = 100);
            """
        else:
            # HNSW index - slower build, better for > 1M vectors
            sql = f"""
            CREATE INDEX IF NOT EXISTS {index_name}
            ON {self.table_name}
            USING hnsw ({self.embedding_column} vector_cosine_ops);
            """

        # Execute SQL (requires appropriate permissions)
        try:
            supabase.rpc("exec_sql", {"sql": sql}).execute()
            self._logger.info(f"Created {self.index_type} index: {index_name}")
        except Exception as e:
            raise APIError(
                f"Failed to create index: {e}. "
                "Ensure 'exec_sql' RPC function exists or create index manually.",
                tool_name=self.tool_name,
            )


if __name__ == "__main__":
    # Test the tool
    print("Testing SupabaseInsertEmbeddings...")
    print("=" * 60)

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic embedding insertion
    print("\n1. Testing basic embedding insertion...")
    embeddings = [
        {
            "id": "doc_1",
            "embedding": [0.1, 0.2, 0.3] * 512,  # 1536 dims
            "content": "First document about AI",
            "metadata": {"category": "technology", "timestamp": "2025-11-23"},
        },
        {
            "id": "doc_2",
            "embedding": [0.4, 0.5, 0.6] * 512,
            "content": "Second document about ML",
            "metadata": {"category": "technology", "timestamp": "2025-11-23"},
        },
    ]

    tool = SupabaseInsertEmbeddings(table_name="documents", embeddings=embeddings, batch_size=100)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Inserted: {result.get('inserted_count')}")
    print(f"Failed: {result.get('failed_count')}")
    assert result.get("success") == True
    assert result.get("inserted_count") == 2
    assert result.get("failed_count") == 0

    # Test 2: Upsert mode
    print("\n2. Testing upsert mode...")
    embeddings = [
        {
            "id": "doc_1",
            "embedding": [0.7, 0.8, 0.9] * 512,
            "content": "Updated first document",
        }
    ]

    tool = SupabaseInsertEmbeddings(
        table_name="documents",
        embeddings=embeddings,
        upsert=True,
        on_conflict="id",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Upsert mode: {result.get('metadata', {}).get('upsert')}")
    assert result.get("success") == True
    assert result.get("metadata", {}).get("upsert") == True

    # Test 3: Batch insertion (100+ embeddings)
    print("\n3. Testing batch insertion (150 embeddings)...")
    large_batch = []
    for i in range(150):
        large_batch.append(
            {
                "id": f"batch_doc_{i}",
                "embedding": [0.1 * i % 1.0] * 1536,
                "content": f"Batch document {i}",
            }
        )

    tool = SupabaseInsertEmbeddings(table_name="documents", embeddings=large_batch, batch_size=50)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Total records: {result.get('metadata', {}).get('total_records')}")
    print(f"Batch size: {result.get('metadata', {}).get('batch_size')}")
    print(f"Inserted: {result.get('inserted_count')}")
    assert result.get("success") == True
    assert result.get("inserted_count") == 150

    # Test 4: Dimension validation
    print("\n4. Testing dimension validation...")
    embeddings = [
        {"id": "doc_1", "embedding": [0.1] * 768},
        {"id": "doc_2", "embedding": [0.2] * 768},
        {"id": "doc_3", "embedding": [0.3] * 768},
    ]

    tool = SupabaseInsertEmbeddings(
        table_name="documents",
        embeddings=embeddings,
        validate_dimensions=True,
        expected_dimensions=768,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"All embeddings validated: {tool.validate_dimensions}")
    assert result.get("success") == True

    # Test 5: Error handling - dimension mismatch
    print("\n5. Testing error handling (dimension mismatch)...")
    try:
        embeddings = [
            {"id": "doc_1", "embedding": [0.1] * 768},
            {"id": "doc_2", "embedding": [0.2] * 1536},  # Different dimensions
        ]
        tool = SupabaseInsertEmbeddings(
            table_name="documents",
            embeddings=embeddings,
            validate_dimensions=True,
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 6: Error handling - missing required field
    print("\n6. Testing error handling (missing id field)...")
    try:
        embeddings = [{"embedding": [0.1] * 768, "content": "Missing ID"}]  # No 'id' field
        tool = SupabaseInsertEmbeddings(table_name="documents", embeddings=embeddings)
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 7: Different embedding dimensions
    print("\n7. Testing different embedding dimensions...")
    dims = [384, 768, 1536]
    for dim in dims:
        embeddings = [{"id": f"doc_{dim}_1", "embedding": [0.1] * dim, "content": f"Doc {dim}"}]
        tool = SupabaseInsertEmbeddings(
            table_name="documents",
            embeddings=embeddings,
            expected_dimensions=dim,
        )
        result = tool.run()
        print(f"  Dimension {dim}: {result.get('inserted_count')} inserted")
        assert result.get("success") == True

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
