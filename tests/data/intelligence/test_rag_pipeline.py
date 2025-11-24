"""Comprehensive tests for rag_pipeline tool."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ConfigurationError, ValidationError
from tools.data.intelligence.rag_pipeline.rag_pipeline import RAGPipeline


class TestRAGPipeline:
    """Test suite for RAGPipeline."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_query(self) -> str:
        """Valid test query."""
        return "What is machine learning?"

    @pytest.fixture
    def tool(self, valid_query: str) -> RAGPipeline:
        """Create RAGPipeline instance with valid parameters."""
        return RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="knowledge_base",
            top_k=5,
        )

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, valid_query: str):
        """Test successful execution."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test_collection",
            top_k=5,
        )
        result = tool.run()
        assert result["success"] is True
        assert "results" in result
        assert len(result["results"]) == 5

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_all_vector_databases(self, valid_query: str):
        """Test all supported vector databases."""
        databases = ["pinecone", "chroma", "weaviate", "qdrant", "milvus"]
        for db in databases:
            tool = RAGPipeline(
                query=valid_query,
                vector_db=db,
                collection_name="test_collection",
                top_k=5,
            )
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["vector_db"] == db

    # ========== QUERY VALIDATION ==========

    def test_empty_query_rejected(self):
        """Test that empty query is rejected."""
        with pytest.raises(PydanticValidationError):
            RAGPipeline(query="", vector_db="pinecone", collection_name="test", top_k=5)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_whitespace_query_rejected(self):
        """Test that whitespace-only query is rejected."""
        tool = RAGPipeline(
            query="   ",
            vector_db="pinecone",
            collection_name="test",
            top_k=5,
        )
        with pytest.raises(ValidationError, match="Query cannot be empty"):
            tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_complex_queries(self):
        """Test various complex queries."""
        queries = [
            "What are the applications of deep learning in healthcare?",
            "Explain quantum computing",
            "Compare supervised and unsupervised learning",
            "What is the transformer architecture?",
        ]
        for query in queries:
            tool = RAGPipeline(
                query=query,
                vector_db="pinecone",
                collection_name="test",
                top_k=5,
            )
            result = tool.run()
            assert result["success"] is True

    # ========== VECTOR DB VALIDATION ==========

    def test_invalid_vector_db_rejected(self, valid_query: str):
        """Test that invalid vector database is rejected."""
        with pytest.raises(PydanticValidationError):
            RAGPipeline(
                query=valid_query,
                vector_db="invalid_db",
                collection_name="test",
                top_k=5,
            )

    # ========== COLLECTION NAME VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_empty_collection_name_rejected(self, valid_query: str):
        """Test that empty collection name is rejected."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="",
            top_k=5,
        )
        with pytest.raises(ValidationError, match="Collection name cannot be empty"):
            tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_default_collection_name(self, valid_query: str):
        """Test default collection name."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
        )
        assert tool.collection_name == "default"

    # ========== TOP_K VALIDATION ==========

    def test_top_k_min_boundary(self, valid_query: str):
        """Test minimum top_k value (1)."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            top_k=1,
        )
        assert tool.top_k == 1

    def test_top_k_max_boundary(self, valid_query: str):
        """Test maximum top_k value (100)."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            top_k=100,
        )
        assert tool.top_k == 100

    def test_top_k_zero_rejected(self, valid_query: str):
        """Test that top_k = 0 is rejected."""
        with pytest.raises(PydanticValidationError):
            RAGPipeline(
                query=valid_query,
                vector_db="pinecone",
                collection_name="test",
                top_k=0,
            )

    def test_top_k_negative_rejected(self, valid_query: str):
        """Test that negative top_k is rejected."""
        with pytest.raises(PydanticValidationError):
            RAGPipeline(
                query=valid_query,
                vector_db="pinecone",
                collection_name="test",
                top_k=-5,
            )

    def test_top_k_exceeds_max_rejected(self, valid_query: str):
        """Test that top_k > 100 is rejected."""
        with pytest.raises(PydanticValidationError):
            RAGPipeline(
                query=valid_query,
                vector_db="pinecone",
                collection_name="test",
                top_k=101,
            )

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_results_count_matches_top_k(self, valid_query: str):
        """Test that returned results match top_k."""
        for k in [1, 5, 10, 20]:
            tool = RAGPipeline(
                query=valid_query,
                vector_db="pinecone",
                collection_name="test",
                top_k=k,
            )
            result = tool.run()
            assert len(result["results"]) == min(k, 5)  # Mock returns max 5

    # ========== EMBEDDING MODEL VALIDATION ==========

    def test_default_embedding_model(self, valid_query: str):
        """Test default embedding model."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
        )
        assert tool.embedding_model == "text-embedding-3-small"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_valid_embedding_models(self, valid_query: str):
        """Test all valid embedding models."""
        models = ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]
        for model in models:
            tool = RAGPipeline(
                query=valid_query,
                vector_db="pinecone",
                collection_name="test",
                embedding_model=model,
            )
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["embedding_model"] == model

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_invalid_embedding_model_rejected(self, valid_query: str):
        """Test that invalid embedding model is rejected."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            embedding_model="invalid-model",
        )
        with pytest.raises(ValidationError, match="Invalid embedding model"):
            tool.run()

    # ========== SEARCH TYPE VALIDATION ==========

    def test_default_search_type(self, valid_query: str):
        """Test default search type."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
        )
        assert tool.search_type == "semantic"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_all_search_types(self, valid_query: str):
        """Test all valid search types."""
        search_types = ["semantic", "keyword", "hybrid"]
        for search_type in search_types:
            tool = RAGPipeline(
                query=valid_query,
                vector_db="pinecone",
                collection_name="test",
                search_type=search_type,
            )
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["search_type"] == search_type

    def test_invalid_search_type_rejected(self, valid_query: str):
        """Test that invalid search type is rejected."""
        with pytest.raises(PydanticValidationError):
            RAGPipeline(
                query=valid_query,
                vector_db="pinecone",
                collection_name="test",
                search_type="invalid",
            )

    # ========== METADATA FILTER ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_filter_optional(self, valid_query: str):
        """Test that metadata filter is optional."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
        )
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_filter_with_values(self, valid_query: str):
        """Test metadata filter with various values."""
        filters = [
            {"category": "programming"},
            {"year": 2024},
            {"author": "John Doe", "category": "AI"},
            {"difficulty": "beginner"},
        ]
        for metadata_filter in filters:
            tool = RAGPipeline(
                query=valid_query,
                vector_db="pinecone",
                collection_name="test",
                metadata_filter=metadata_filter,
            )
            result = tool.run()
            assert result["success"] is True

    # ========== RERANK ==========

    def test_rerank_default_false(self, valid_query: str):
        """Test that rerank defaults to False."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
        )
        assert tool.rerank is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_rerank_enabled(self, valid_query: str):
        """Test rerank enabled."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            rerank=True,
        )
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_rerank_disabled(self, valid_query: str):
        """Test rerank disabled."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            rerank=False,
        )
        result = tool.run()
        assert result["success"] is True

    # ========== ERROR HANDLING ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_missing_openai_key(self, valid_query: str):
        """Test error when OpenAI API key is missing."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            top_k=5,
        )
        with patch.dict("os.environ", {}, clear=True):
            with patch.dict("os.environ", {"USE_MOCK_APIS": "false"}):
                with pytest.raises((APIError, ConfigurationError)):
                    tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_handling(self, valid_query: str):
        """Test handling of API errors."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            top_k=5,
        )
        with patch.object(tool, "_process", side_effect=Exception("API error")):
            with pytest.raises(APIError, match="RAG pipeline failed"):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_enabled(self, valid_query: str):
        """Test that mock mode returns mock data."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            top_k=5,
        )
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_mock_mode_disabled(self, valid_query: str):
        """Test that mock mode can be disabled."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            top_k=5,
        )
        assert not tool._should_use_mock()

    # ========== RESULT FORMAT VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_result_format(self, valid_query: str):
        """Test that results have correct format."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test",
            top_k=5,
        )
        result = tool.run()

        assert "success" in result
        assert "results" in result
        assert "metadata" in result
        assert "total_found" in result
        assert isinstance(result["results"], list)

        # Check individual chunk format
        for chunk in result["results"]:
            assert "id" in chunk
            assert "text" in chunk
            assert "score" in chunk
            assert "metadata" in chunk

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_metadata_format(self, valid_query: str):
        """Test metadata format."""
        tool = RAGPipeline(
            query=valid_query,
            vector_db="pinecone",
            collection_name="test_collection",
            top_k=10,
        )
        result = tool.run()

        metadata = result["metadata"]
        assert "tool_name" in metadata
        assert metadata["tool_name"] == "rag_pipeline"
        assert "vector_db" in metadata
        assert metadata["vector_db"] == "pinecone"
        assert "collection_name" in metadata
        assert "search_type" in metadata
        assert "embedding_model" in metadata

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "query,vector_db,collection_name,top_k,expected_valid",
        [
            ("valid query", "pinecone", "test", 5, True),
            ("valid query", "chroma", "test", 10, True),
            ("valid query", "weaviate", "test", 20, True),
            ("valid query", "qdrant", "test", 1, True),
            ("valid query", "milvus", "test", 100, True),
            ("", "pinecone", "test", 5, False),  # Empty query
            ("test", "invalid_db", "test", 5, False),  # Invalid vector DB
            ("test", "pinecone", "", 5, False),  # Empty collection
            ("test", "pinecone", "test", 0, False),  # Invalid top_k
            ("test", "pinecone", "test", 101, False),  # top_k too high
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_parameter_combinations(
        self,
        query: str,
        vector_db: str,
        collection_name: str,
        top_k: int,
        expected_valid: bool,
    ):
        """Test various parameter combinations."""
        if expected_valid:
            tool = RAGPipeline(
                query=query,
                vector_db=vector_db,
                collection_name=collection_name,
                top_k=top_k,
            )
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = RAGPipeline(
                    query=query,
                    vector_db=vector_db,
                    collection_name=collection_name,
                    top_k=top_k,
                )
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow(self):
        """Test complete workflow for RAG pipeline."""
        # Create tool
        tool = RAGPipeline(
            query="What is machine learning?",
            vector_db="pinecone",
            collection_name="knowledge_base",
            top_k=10,
            embedding_model="text-embedding-3-small",
            search_type="semantic",
            rerank=False,
        )

        # Verify parameters
        assert tool.query == "What is machine learning?"
        assert tool.vector_db == "pinecone"
        assert tool.collection_name == "knowledge_base"
        assert tool.top_k == 10
        assert tool.tool_name == "rag_pipeline"
        assert tool.tool_category == "data"

        # Execute
        result = tool.run()

        # Verify results
        assert result["success"] is True
        assert len(result["results"]) == 5  # Mock returns 5
        assert all("text" in chunk for chunk in result["results"])
        assert all("score" in chunk for chunk in result["results"])

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_multiple_vector_databases(self):
        """Test searching across multiple vector databases."""
        databases = ["pinecone", "chroma", "weaviate", "qdrant", "milvus"]
        query = "deep learning"

        for db in databases:
            tool = RAGPipeline(
                query=query,
                vector_db=db,
                collection_name=f"{db}_collection",
                top_k=5,
            )
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["vector_db"] == db

    # ========== TOOL METADATA TESTS ==========

    def test_tool_category(self, tool: RAGPipeline):
        """Test tool category is correct."""
        assert tool.tool_category == "data"

    def test_tool_name(self, tool: RAGPipeline):
        """Test tool name is correct."""
        assert tool.tool_name == "rag_pipeline"
