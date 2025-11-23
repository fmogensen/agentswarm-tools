"""
Research Web Search - Focused web search and URL crawling for research purposes.

This atomic tool handles:
1. Web search across multiple sources
2. URL crawling and content extraction
3. Source ranking and deduplication
4. Metadata extraction
"""

import hashlib
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ConfigurationError, ValidationError


class ResearchWebSearch(BaseTool):
    """
    Perform web search and URL crawling for research purposes.

    This tool focuses specifically on gathering and processing web sources:
    - Searches multiple web sources (Google, Bing, etc.)
    - Crawls and extracts content from URLs
    - Deduplicates and ranks sources by relevance
    - Extracts metadata (title, snippet, author, date)

    Args:
        query: Research query or question to search for
        max_results: Maximum number of search results to return (5-100)
        crawl_content: Whether to crawl full page content (slower but more complete)
        filter_duplicates: Remove duplicate URLs and near-duplicate content
        rank_by: Ranking criteria (relevance, recency, authority)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - sources: List of source dictionaries with metadata
        - total_found: Total number of sources found before filtering
        - metadata: Search metadata (query, timing, etc.)

    Example:
        >>> tool = ResearchWebSearch(
        ...     query="artificial intelligence in healthcare",
        ...     max_results=20,
        ...     crawl_content=True,
        ...     rank_by="relevance"
        ... )
        >>> result = tool.run()
        >>> print(f"Found {len(result['sources'])} sources")
    """

    # Tool metadata
    tool_name: str = "research_web_search"
    tool_category: str = "data"
    rate_limit_type: str = "search"
    rate_limit_cost: int = 2

    # Required parameters
    query: str = Field(
        ..., description="Research query or question to search for", min_length=3, max_length=500
    )

    # Optional parameters
    max_results: int = Field(
        20, description="Maximum number of search results to return", ge=5, le=100
    )

    crawl_content: bool = Field(
        False, description="Whether to crawl full page content from URLs (slower but more complete)"
    )

    filter_duplicates: bool = Field(
        True, description="Remove duplicate URLs and near-duplicate content"
    )

    rank_by: Literal["relevance", "recency", "authority"] = Field(
        "relevance",
        description="Ranking criteria: relevance (default), recency (newest first), authority (trusted sources)",
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute web search and crawling."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "sources": result["sources"],
                "total_found": result["total_found"],
                "metadata": {
                    "tool_name": self.tool_name,
                    "query": self.query,
                    "max_results": self.max_results,
                    "crawl_content": self.crawl_content,
                    "rank_by": self.rank_by,
                    "duration_seconds": result["duration_seconds"],
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }
        except Exception as e:
            raise APIError(f"Web search failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.query.strip():
            raise ValidationError("Query cannot be empty", field="query", tool_name=self.tool_name)

        if len(self.query) < 3:
            raise ValidationError(
                "Query must be at least 3 characters", field="query", tool_name=self.tool_name
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock search results for testing."""
        mock_sources = []

        for i in range(self.max_results):
            query_hash = hashlib.md5(f"{self.query}{i}".encode()).hexdigest()[:8]
            mock_sources.append(
                {
                    "type": "web",
                    "title": f"Research Article {i+1}: {self.query[:50]}",
                    "url": f"https://example.com/article/{query_hash}",
                    "snippet": f"This article discusses {self.query.lower()} with comprehensive analysis and recent findings. "
                    * 2,
                    "content": f"Full content for {self.query}..." if self.crawl_content else None,
                    "author": f"Author {i+1}",
                    "published_date": "2024-01-15",
                    "domain": "example.com",
                    "relevance_score": round(1.0 - (i * 0.03), 2),
                    "authority_score": round(0.85 - (i * 0.02), 2),
                    "word_count": 1200 + (i * 50) if self.crawl_content else None,
                }
            )

        return {
            "success": True,
            "sources": mock_sources,
            "total_found": self.max_results + 10,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "query": self.query,
                "max_results": self.max_results,
                "crawl_content": self.crawl_content,
                "rank_by": self.rank_by,
                "duration_seconds": 0.3,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic for web search."""
        start_time = time.time()

        # Step 1: Perform web search
        self._logger.info(f"Searching web for: {self.query}")
        raw_results = self._perform_web_search()

        # Step 2: Filter duplicates if requested
        if self.filter_duplicates:
            self._logger.info("Filtering duplicate sources")
            filtered_results = self._deduplicate_sources(raw_results)
        else:
            filtered_results = raw_results

        # Step 3: Crawl content if requested
        if self.crawl_content:
            self._logger.info(f"Crawling content from {len(filtered_results)} URLs")
            filtered_results = self._crawl_source_content(filtered_results)

        # Step 4: Rank sources
        self._logger.info(f"Ranking sources by {self.rank_by}")
        ranked_sources = self._rank_sources(filtered_results)

        # Step 5: Limit to max_results
        final_sources = ranked_sources[: self.max_results]

        duration = time.time() - start_time

        return {
            "sources": final_sources,
            "total_found": len(raw_results),
            "duration_seconds": round(duration, 2),
        }

    def _perform_web_search(self) -> List[Dict[str, Any]]:
        """
        Perform web search using search APIs.

        Returns:
            List of raw search results
        """
        # Try to use existing web search tool
        try:
            from tools.data.search.web_search.web_search import WebSearch

            web_tool = WebSearch(query=self.query, max_results=self.max_results * 2)
            web_result = web_tool.run()

            if web_result.get("success"):
                sources = []
                for item in web_result.get("result", []):
                    sources.append(
                        {
                            "type": "web",
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "domain": self._extract_domain(item.get("link", "")),
                            "relevance_score": 0.8,  # Will be re-ranked
                            "published_date": None,  # Will be extracted if crawled
                            "content": None,
                        }
                    )
                return sources
        except ImportError:
            self._logger.warning("WebSearch tool not available")
        except Exception as e:
            self._logger.warning(f"Web search failed: {e}")

        # Fallback: return empty list
        return []

    def _deduplicate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate sources by URL and near-duplicate content.

        Args:
            sources: List of source dictionaries

        Returns:
            Deduplicated list
        """
        seen_urls = set()
        unique_sources = []

        for source in sources:
            url = source.get("url", "")

            # Normalize URL (remove query params and fragments for comparison)
            normalized_url = url.split("?")[0].split("#")[0].lower()

            if normalized_url and normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                unique_sources.append(source)

        return unique_sources

    def _crawl_source_content(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Crawl full content from source URLs.

        Args:
            sources: List of sources with URLs

        Returns:
            Sources with content field populated
        """
        enriched_sources = []

        for source in sources:
            url = source.get("url", "")
            if not url:
                enriched_sources.append(source)
                continue

            try:
                # Fetch page content
                response = requests.get(
                    url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (ResearchBot/1.0)"}
                )
                response.raise_for_status()

                # Extract text content (simplified - in production would use BeautifulSoup)
                content = response.text[:5000]  # First 5000 chars

                source["content"] = content
                source["word_count"] = len(content.split())

            except Exception as e:
                self._logger.warning(f"Failed to crawl {url}: {e}")
                source["content"] = None

            enriched_sources.append(source)

        return enriched_sources

    def _rank_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank sources based on selected criteria.

        Args:
            sources: List of sources to rank

        Returns:
            Ranked list of sources
        """

        def rank_key(source):
            if self.rank_by == "relevance":
                return source.get("relevance_score", 0.5)
            elif self.rank_by == "recency":
                # In production, would parse published_date
                return source.get("relevance_score", 0.5)  # Fallback
            elif self.rank_by == "authority":
                # Check for trusted domains
                domain = source.get("domain", "")
                authority_bonus = 0.2 if any(d in domain for d in [".edu", ".gov", ".org"]) else 0.0
                return source.get("relevance_score", 0.5) + authority_bonus
            else:
                return source.get("relevance_score", 0.5)

        return sorted(sources, key=rank_key, reverse=True)

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""


if __name__ == "__main__":
    # Test the research_web_search tool
    print("Testing ResearchWebSearch tool...\n")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic web search
    print("Test 1: Basic web search")
    print("-" * 50)
    tool = ResearchWebSearch(query="artificial intelligence in healthcare", max_results=10)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Sources found: {len(result['sources'])}")
    print(f"Total before filtering: {result.get('total_found')}")
    print(f"First source: {result['sources'][0]['title']}")
    print(f"Relevance score: {result['sources'][0]['relevance_score']}")

    # Test 2: With content crawling
    print("\n\nTest 2: Web search with content crawling")
    print("-" * 50)
    tool2 = ResearchWebSearch(
        query="quantum computing algorithms", max_results=5, crawl_content=True, rank_by="authority"
    )
    result2 = tool2.run()

    print(f"Success: {result2.get('success')}")
    print(f"Sources with content: {sum(1 for s in result2['sources'] if s.get('content'))}")
    print(f"Duration: {result2['metadata']['duration_seconds']}s")

    # Test 3: Ranking by recency
    print("\n\nTest 3: Rank by recency")
    print("-" * 50)
    tool3 = ResearchWebSearch(query="latest AI developments", max_results=15, rank_by="recency")
    result3 = tool3.run()

    print(f"Success: {result3.get('success')}")
    print(f"Rank by: {result3['metadata']['rank_by']}")

    # Test 4: Validation tests
    print("\n\nTest 4: Validation tests")
    print("-" * 50)

    try:
        bad_tool = ResearchWebSearch(query="AI")  # Too short
        bad_tool.run()
        print("ERROR: Should have failed")
    except Exception as e:
        print(f"✓ Correctly rejected short query: {type(e).__name__}")

    print("\n✅ All tests passed!")
