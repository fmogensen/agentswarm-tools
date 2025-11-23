"""
Supabase Integration Tools for AgentSwarm

Complete suite of Supabase tools for vector search, embeddings, auth, realtime, and storage.

Tools:
- SupabaseVectorSearch: Semantic similarity search using pgvector
- SupabaseInsertEmbeddings: Batch insert embeddings with metadata
- SupabaseAuth: User authentication and session management
- SupabaseRealtime: Subscribe to database changes
- SupabaseStorage: File upload/download and CDN management

Example:
    >>> from agentswarm_tools.tools.integrations.supabase import (
    ...     SupabaseVectorSearch,
    ...     SupabaseInsertEmbeddings,
    ...     SupabaseAuth,
    ...     SupabaseRealtime,
    ...     SupabaseStorage
    ... )

    >>> # Vector search
    >>> search = SupabaseVectorSearch(
    ...     table_name="documents",
    ...     query_embedding=[0.1] * 1536,
    ...     match_threshold=0.7
    ... )
    >>> results = search.run()

    >>> # Insert embeddings
    >>> insert = SupabaseInsertEmbeddings(
    ...     table_name="documents",
    ...     embeddings=[
    ...         {"id": "doc_1", "embedding": [...], "content": "..."}
    ...     ]
    ... )
    >>> result = insert.run()
"""

from .supabase_vector_search import SupabaseVectorSearch
from .supabase_insert_embeddings import SupabaseInsertEmbeddings
from .supabase_auth import SupabaseAuth
from .supabase_realtime import SupabaseRealtime
from .supabase_storage import SupabaseStorage

__all__ = [
    "SupabaseVectorSearch",
    "SupabaseInsertEmbeddings",
    "SupabaseAuth",
    "SupabaseRealtime",
    "SupabaseStorage",
]

__version__ = "1.0.0"
__author__ = "AgentSwarm Tools Framework"
__description__ = "Supabase integration tools for vector search, auth, realtime, and storage"
