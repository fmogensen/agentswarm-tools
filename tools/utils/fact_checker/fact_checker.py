"""
Fact Checker Tool - Verify claims using web search and academic sources

This tool searches for evidence to support or contradict a given claim,
analyzes source credibility, and provides a confidence score.
"""

import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class FactChecker(BaseTool):
    """
    Verify claims using web search and academic sources.

    This tool performs fact-checking by:
    1. Searching for evidence using web_search and optionally scholar_search
    2. Analyzing source credibility based on domain reputation
    3. Categorizing sources as supporting, contradicting, or neutral
    4. Computing a confidence score (0-100) based on evidence strength

    Args:
        claim: The claim or statement to verify (required)
        sources: Optional list of specific source URLs to check
        use_scholar: Whether to include academic sources via scholar search
        max_sources: Maximum number of sources to analyze (default: 10)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Dict with:
            - confidence_score: Score from 0-100 (0=false, 100=true)
            - verdict: "SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"
            - supporting_sources: List of sources supporting the claim
            - contradicting_sources: List of sources contradicting the claim
            - neutral_sources: List of neutral/informational sources
            - analysis_summary: Brief explanation of the verdict
        - metadata: Additional information about the fact-check

    Raises:
        ValidationError: If claim is empty or invalid
        APIError: If search APIs fail

    Example:
        >>> tool = FactChecker(
        ...     claim="The Earth is round",
        ...     use_scholar=True,
        ...     max_sources=10
        ... )
        >>> result = tool.run()
        >>> print(result["result"]["verdict"])
        SUPPORTED
    """

    # Tool metadata
    tool_name: str = "fact_checker"
    tool_category: str = "utils"

    # Parameters
    claim: str = Field(
        ..., description="The claim or statement to verify", min_length=5, max_length=500
    )

    sources: Optional[List[str]] = Field(
        default=None, description="Optional list of specific source URLs to check"
    )

    use_scholar: bool = Field(
        default=False, description="Whether to include academic sources via scholar search"
    )

    max_sources: int = Field(
        default=10, description="Maximum number of sources to analyze", ge=1, le=50
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the fact_checker tool.

        Returns:
            Dict with fact-checking results
        """

        self._logger.info(
            f"Executing {self.tool_name} with claim={self.claim}, sources={self.sources}, use_scholar={self.use_scholar}, max_sources={self.max_sources}"
        )
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "claim": self.claim,
                    "sources_analyzed": len(result.get("supporting_sources", []))
                    + len(result.get("contradicting_sources", []))
                    + len(result.get("neutral_sources", [])),
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.claim.strip():
            raise ValidationError(
                "Claim cannot be empty", tool_name=self.tool_name, details={"claim": self.claim}
            )

        # Validate source URLs if provided
        if self.sources:
            for source in self.sources:
                if not self._is_valid_url(source):
                    raise ValidationError(
                        f"Invalid source URL: {source}",
                        tool_name=self.tool_name,
                        details={"source": source},
                    )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_supporting = [
            {
                "url": "https://example.com/source1",
                "title": "Mock Supporting Source 1",
                "snippet": f"This source supports the claim: {self.claim}",
                "credibility_score": 85,
                "domain": "example.com",
            },
            {
                "url": "https://scholar.example.edu/paper1",
                "title": "Academic Study Supporting Claim",
                "snippet": "Research confirms this statement.",
                "credibility_score": 95,
                "domain": "scholar.example.edu",
            },
        ]

        mock_contradicting = [
            {
                "url": "https://skeptic.example.org/article1",
                "title": "Critical Analysis",
                "snippet": "This analysis questions the validity of the claim.",
                "credibility_score": 75,
                "domain": "skeptic.example.org",
            }
        ]

        mock_neutral = [
            {
                "url": "https://wiki.example.com/topic",
                "title": "General Information",
                "snippet": "Background information on the topic.",
                "credibility_score": 70,
                "domain": "wiki.example.com",
            }
        ]

        # Calculate mock confidence score
        confidence_score = 72  # More supporting than contradicting

        return {
            "success": True,
            "result": {
                "confidence_score": confidence_score,
                "verdict": "SUPPORTED",
                "supporting_sources": mock_supporting,
                "contradicting_sources": mock_contradicting,
                "neutral_sources": mock_neutral,
                "analysis_summary": f"Found {len(mock_supporting)} supporting sources and {len(mock_contradicting)} contradicting sources. The claim appears to be supported by available evidence.",
            },
            "metadata": {"mock_mode": True, "sources_analyzed": 4},
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        all_sources = []

        # Step 1: Gather sources
        if self.sources:
            # Use provided sources
            all_sources.extend(self._analyze_provided_sources(self.sources))
        else:
            # Search for sources
            all_sources.extend(self._search_web_sources())

            if self.use_scholar:
                all_sources.extend(self._search_scholar_sources())

        # Limit to max_sources
        all_sources = all_sources[: self.max_sources]

        # Step 2: Categorize sources
        supporting_sources = []
        contradicting_sources = []
        neutral_sources = []

        for source in all_sources:
            category = self._categorize_source(source)
            if category == "supporting":
                supporting_sources.append(source)
            elif category == "contradicting":
                contradicting_sources.append(source)
            else:
                neutral_sources.append(source)

        # Step 3: Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            supporting_sources, contradicting_sources, neutral_sources
        )

        # Step 4: Determine verdict
        verdict = self._determine_verdict(confidence_score)

        # Step 5: Generate analysis summary
        analysis_summary = self._generate_analysis_summary(
            confidence_score,
            len(supporting_sources),
            len(contradicting_sources),
            len(neutral_sources),
        )

        return {
            "confidence_score": confidence_score,
            "verdict": verdict,
            "supporting_sources": supporting_sources,
            "contradicting_sources": contradicting_sources,
            "neutral_sources": neutral_sources,
            "analysis_summary": analysis_summary,
        }

    def _search_web_sources(self) -> List[Dict[str, Any]]:
        """Search for sources using web search API."""
        try:
            api_key = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_SHOPPING_API_KEY")
            engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID") or os.getenv(
                "GOOGLE_SHOPPING_ENGINE_ID"
            )

            if not api_key or not engine_id:
                raise APIError(
                    "Missing API credentials. Set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID",
                    tool_name=self.tool_name,
                )

            # Construct fact-checking query
            query = f'"{self.claim}" fact check verify'

            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "q": query,
                    "num": min(10, self.max_sources),
                    "key": api_key,
                    "cx": engine_id,
                },
                timeout=30,
            )
            response.raise_for_status()
            search_results = response.json()
            self._logger.debug(f"Received response from API").get("items", [])

            sources = []
            for item in search_results:
                url = item.get("link", "")
                domain = urlparse(url).netloc
                sources.append(
                    {
                        "url": url,
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "credibility_score": self._assess_credibility(domain),
                        "domain": domain,
                    }
                )

            return sources

        except requests.RequestException as e:
            self._logger.error(f"API request failed: {str(e)}", exc_info=True)
            raise APIError(f"Web search API request failed: {e}", tool_name=self.tool_name)

    def _search_scholar_sources(self) -> List[Dict[str, Any]]:
        """Search for academic sources (simplified implementation)."""
        # Note: In production, this would use Google Scholar API or similar
        # For now, we'll simulate by searching with 'scholar' or 'research' keywords
        try:
            api_key = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_SHOPPING_API_KEY")
            engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID") or os.getenv(
                "GOOGLE_SHOPPING_ENGINE_ID"
            )

            if not api_key or not engine_id:
                return []  # Gracefully skip if no credentials

            query = f"{self.claim} site:edu OR site:gov research study"

            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "q": query,
                    "num": min(5, self.max_sources // 2),
                    "key": api_key,
                    "cx": engine_id,
                },
                timeout=30,
            )
            response.raise_for_status()
            search_results = response.json()
            self._logger.debug(f"Received response from API").get("items", [])

            sources = []
            for item in search_results:
                url = item.get("link", "")
                domain = urlparse(url).netloc
                # Boost credibility for academic sources
                base_credibility = self._assess_credibility(domain)
                academic_bonus = 20 if any(ext in domain for ext in [".edu", ".gov"]) else 0

                sources.append(
                    {
                        "url": url,
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "credibility_score": min(100, base_credibility + academic_bonus),
                        "domain": domain,
                    }
                )

            return sources

        except requests.RequestException:
            return []  # Gracefully skip on error

    def _analyze_provided_sources(self, source_urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze user-provided source URLs."""
        sources = []
        for url in source_urls:
            domain = urlparse(url).netloc
            sources.append(
                {
                    "url": url,
                    "title": "User-provided source",
                    "snippet": "",
                    "credibility_score": self._assess_credibility(domain),
                    "domain": domain,
                }
            )
        return sources

    def _categorize_source(self, source: Dict[str, Any]) -> str:
        """
        Categorize a source as supporting, contradicting, or neutral.

        This is a simplified heuristic based on snippet content.
        In production, this would use NLP or LLM analysis.
        """
        snippet = source.get("snippet", "").lower()
        title = source.get("title", "").lower()
        text = f"{title} {snippet}"

        # Keywords indicating support
        support_keywords = [
            "confirmed",
            "true",
            "verified",
            "correct",
            "supports",
            "validates",
            "proves",
        ]
        contradict_keywords = [
            "false",
            "debunked",
            "myth",
            "incorrect",
            "wrong",
            "contradicts",
            "refutes",
        ]

        support_count = sum(1 for word in support_keywords if word in text)
        contradict_count = sum(1 for word in contradict_keywords if word in text)

        if support_count > contradict_count:
            return "supporting"
        elif contradict_count > support_count:
            return "contradicting"
        else:
            return "neutral"

    def _assess_credibility(self, domain: str) -> int:
        """
        Assess source credibility based on domain.
        Returns a score from 0-100.
        """
        # Highly credible sources
        high_credibility = [".edu", ".gov", ".org"]
        # Moderate credibility
        moderate_credibility = [".com", ".net"]
        # Known fact-checking sites
        fact_checkers = [
            "snopes.com",
            "factcheck.org",
            "politifact.com",
            "reuters.com",
            "apnews.com",
        ]

        domain_lower = domain.lower()

        # Check for fact-checking sites
        if any(checker in domain_lower for checker in fact_checkers):
            return 95

        # Check for high credibility domains
        if any(ext in domain_lower for ext in high_credibility):
            return 85

        # Check for moderate credibility
        if any(ext in domain_lower for ext in moderate_credibility):
            return 70

        # Default credibility
        return 60

    def _calculate_confidence_score(
        self, supporting: List[Dict], contradicting: List[Dict], neutral: List[Dict]
    ) -> int:
        """
        Calculate confidence score (0-100) based on evidence.

        Formula considers:
        - Number and credibility of supporting sources
        - Number and credibility of contradicting sources
        - Overall source quality
        """
        if not supporting and not contradicting:
            return 50  # Insufficient evidence

        # Calculate weighted scores
        support_score = sum(s.get("credibility_score", 70) for s in supporting)
        contradict_score = sum(s.get("credibility_score", 70) for s in contradicting)

        # Normalize to 0-100 scale
        total_score = support_score + contradict_score
        if total_score == 0:
            return 50

        # Confidence = (support_score / total_score) * 100
        confidence = int((support_score / total_score) * 100)

        return max(0, min(100, confidence))

    def _determine_verdict(self, confidence_score: int) -> str:
        """Determine verdict based on confidence score."""
        if confidence_score >= 70:
            return "SUPPORTED"
        elif confidence_score <= 30:
            return "CONTRADICTED"
        else:
            return "INSUFFICIENT_EVIDENCE"

    def _generate_analysis_summary(
        self, confidence_score: int, num_supporting: int, num_contradicting: int, num_neutral: int
    ) -> str:
        """Generate human-readable analysis summary."""
        verdict = self._determine_verdict(confidence_score)

        if verdict == "SUPPORTED":
            return (
                f"Found {num_supporting} supporting sources and {num_contradicting} contradicting sources. "
                f"Confidence score: {confidence_score}/100. The claim appears to be SUPPORTED by available evidence."
            )
        elif verdict == "CONTRADICTED":
            return (
                f"Found {num_supporting} supporting sources and {num_contradicting} contradicting sources. "
                f"Confidence score: {confidence_score}/100. The claim appears to be CONTRADICTED by available evidence."
            )
        else:
            return (
                f"Found {num_supporting} supporting sources, {num_contradicting} contradicting sources, "
                f"and {num_neutral} neutral sources. Confidence score: {confidence_score}/100. "
                f"INSUFFICIENT EVIDENCE to make a definitive determination."
            )

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False


if __name__ == "__main__":
    # Test the fact_checker tool
    print("Testing FactChecker tool...")

    # Test with mock mode
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic usage
    print("\n--- Test 1: Basic fact check ---")
    tool = FactChecker(claim="The Earth is round", use_scholar=True, max_sources=10)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Verdict: {result['result']['verdict']}")
    print(f"Confidence: {result['result']['confidence_score']}/100")
    print(f"Supporting sources: {len(result['result']['supporting_sources'])}")
    print(f"Contradicting sources: {len(result['result']['contradicting_sources'])}")
    print(f"Analysis: {result['result']['analysis_summary']}")

    # Test 2: With specific sources
    print("\n--- Test 2: With specific sources ---")
    tool2 = FactChecker(
        claim="Climate change is real",
        sources=["https://www.nasa.gov", "https://www.noaa.gov"],
        max_sources=5,
    )
    result2 = tool2.run()

    print(f"Success: {result2.get('success')}")
    print(f"Verdict: {result2['result']['verdict']}")
    print(f"Sources analyzed: {result2['metadata']['sources_analyzed']}")

    # Test 3: No scholar sources
    print("\n--- Test 3: Web sources only ---")
    tool3 = FactChecker(claim="Python is a programming language", use_scholar=False, max_sources=5)
    result3 = tool3.run()

    print(f"Success: {result3.get('success')}")
    print(f"Confidence: {result3['result']['confidence_score']}/100")
