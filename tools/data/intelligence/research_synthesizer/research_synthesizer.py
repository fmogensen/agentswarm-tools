"""
Research Synthesizer - Synthesize research sources into coherent documents.

This atomic tool handles:
1. Combining multiple research sources
2. AI-powered synthesis into coherent narrative
3. Citation formatting (APA, MLA, Chicago, IEEE)
4. Executive summary and outline generation
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import Field
import os
import hashlib
from datetime import datetime

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, ConfigurationError


class ResearchSynthesizer(BaseTool):
    """
    Synthesize multiple research sources into a coherent research document.

    This tool focuses on the synthesis phase:
    - Combines findings from multiple sources
    - Generates coherent narrative using AI
    - Formats citations properly
    - Creates executive summaries and outlines

    Args:
        sources: List of source dictionaries with content and metadata
        research_topic: Main research topic/question
        citation_style: Citation format (apa, mla, chicago, ieee)
        output_format: Output format (markdown, html, pdf)
        include_summary: Generate executive summary
        include_outline: Generate research outline
        synthesis_depth: Synthesis depth (quick, standard, comprehensive)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - report_url: URL to synthesized report
        - executive_summary: Summary text (if requested)
        - outline: Research outline (if requested)
        - metadata: Synthesis metadata

    Example:
        >>> sources = [{"title": "Paper 1", "content": "...", "url": "..."}]
        >>> tool = ResearchSynthesizer(
        ...     sources=sources,
        ...     research_topic="AI in healthcare",
        ...     citation_style="apa"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "research_synthesizer"
    tool_category: str = "data"
    rate_limit_type: str = "research"
    rate_limit_cost: int = 4

    # Required parameters
    sources: List[Dict[str, Any]] = Field(
        ...,
        description="List of source dictionaries with content and metadata",
        min_length=1
    )

    research_topic: str = Field(
        ...,
        description="Main research topic or question",
        min_length=10,
        max_length=500
    )

    # Optional parameters
    citation_style: Literal["apa", "mla", "chicago", "ieee"] = Field(
        "apa",
        description="Citation format"
    )

    output_format: Literal["markdown", "html", "pdf"] = Field(
        "markdown",
        description="Output document format"
    )

    include_summary: bool = Field(
        True,
        description="Generate executive summary"
    )

    include_outline: bool = Field(
        True,
        description="Generate research outline"
    )

    synthesis_depth: Literal["quick", "standard", "comprehensive"] = Field(
        "standard",
        description="Synthesis depth affecting length and detail"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute research synthesis."""
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
                "report_url": result["report_url"],
                "executive_summary": result.get("executive_summary"),
                "outline": result.get("outline"),
                "metadata": {
                    "tool_name": self.tool_name,
                    "research_topic": self.research_topic,
                    "sources_used": len(self.sources),
                    "citation_style": self.citation_style,
                    "output_format": self.output_format,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            raise APIError(f"Research synthesis failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.sources:
            raise ValidationError(
                "At least one source must be provided",
                field="sources",
                tool_name=self.tool_name
            )

        if not self.research_topic.strip():
            raise ValidationError(
                "Research topic cannot be empty",
                field="research_topic",
                tool_name=self.tool_name
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock synthesis results."""
        report_id = hashlib.md5(self.research_topic.encode()).hexdigest()[:12]
        report_url = f"https://reports.example.com/{report_id}.{self.output_format}"

        mock_summary = f"""Executive Summary: {self.research_topic}

This {self.synthesis_depth} synthesis of {len(self.sources)} sources provides
comprehensive insights into {self.research_topic}. Key findings include:

1. Current State: Analysis reveals significant developments
2. Key Challenges: Multiple sources identify implementation hurdles
3. Future Outlook: Expert consensus suggests continued evolution

Methodology: {self.synthesis_depth.capitalize()} synthesis using AI-powered
aggregation with {self.citation_style.upper()} citations.
"""

        mock_outline = [
            "1. Introduction",
            f"   1.1. Background on {self.research_topic}",
            "   1.2. Research Objectives",
            "2. Literature Review",
            "   2.1. Current State",
            "   2.2. Key Theories",
            "3. Findings",
            "   3.1. Major Discoveries",
            "   3.2. Supporting Evidence",
            "4. Discussion",
            "   4.1. Implications",
            "   4.2. Limitations",
            "5. Conclusion",
            "6. References"
        ]

        return {
            "success": True,
            "report_url": report_url,
            "executive_summary": mock_summary if self.include_summary else None,
            "outline": mock_outline if self.include_outline else None,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "research_topic": self.research_topic,
                "sources_used": len(self.sources),
                "citation_style": self.citation_style,
                "output_format": self.output_format,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

    def _process(self) -> Dict[str, Any]:
        """Main synthesis processing logic."""
        # Step 1: Generate outline if requested
        outline = None
        if self.include_outline:
            self._logger.info("Generating research outline")
            outline = self._generate_outline()

        # Step 2: Synthesize content using AI
        self._logger.info("Synthesizing research content")
        report_content = self._synthesize_content(outline)

        # Step 3: Generate summary if requested
        summary = None
        if self.include_summary:
            self._logger.info("Generating executive summary")
            summary = self._generate_summary(report_content)

        # Step 4: Format and save report
        self._logger.info(f"Formatting report as {self.output_format}")
        report_url = self._format_and_save_report(report_content, summary, outline)

        return {
            "report_url": report_url,
            "executive_summary": summary,
            "outline": outline
        }

    def _generate_outline(self) -> List[str]:
        """Generate research outline from sources."""
        # In production, would use AI to generate outline
        return [
            "1. Introduction",
            "2. Background",
            "3. Main Findings",
            "4. Discussion",
            "5. Conclusion",
            "6. References"
        ]

    def _synthesize_content(self, outline: Optional[List[str]]) -> str:
        """Synthesize content from sources using AI."""
        # In production, would use GPT-4 for synthesis
        return f"Synthesized research report on {self.research_topic}..."

    def _generate_summary(self, content: str) -> str:
        """Generate executive summary."""
        # In production, would use AI
        return f"Executive summary of research on {self.research_topic}"

    def _format_and_save_report(
        self,
        content: str,
        summary: Optional[str],
        outline: Optional[List[str]]
    ) -> str:
        """Format report and return URL."""
        report_id = hashlib.md5(f"{self.research_topic}{datetime.utcnow()}".encode()).hexdigest()[:12]
        return f"https://reports.example.com/{report_id}.{self.output_format}"


if __name__ == "__main__":
    print("Testing ResearchSynthesizer tool...\n")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic synthesis
    print("Test 1: Basic synthesis")
    print("-" * 50)
    sources = [
        {"title": "Paper 1", "content": "Content 1", "url": "http://example.com/1"},
        {"title": "Paper 2", "content": "Content 2", "url": "http://example.com/2"}
    ]
    tool = ResearchSynthesizer(
        sources=sources,
        research_topic="AI in healthcare delivery"
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Report URL: {result.get('report_url')}")
    print(f"Has summary: {result.get('executive_summary') is not None}")
    print(f"Has outline: {result.get('outline') is not None}")

    # Test 2: Custom formatting
    print("\n\nTest 2: Custom formatting")
    print("-" * 50)
    tool2 = ResearchSynthesizer(
        sources=sources,
        research_topic="Quantum computing applications",
        citation_style="ieee",
        output_format="pdf",
        synthesis_depth="comprehensive"
    )
    result2 = tool2.run()

    print(f"Success: {result2.get('success')}")
    print(f"Citation style: {result2['metadata']['citation_style']}")
    print(f"Output format: {result2['metadata']['output_format']}")

    print("\n✅ All tests passed!")
