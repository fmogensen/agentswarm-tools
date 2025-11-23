"""
Tests for FactChecker Tool
"""

import os

import pytest
from fact_checker import FactChecker

from shared.errors import ValidationError


class TestFactChecker:
    """Test suite for FactChecker tool."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_basic_fact_check(self):
        """Test basic fact checking."""
        tool = FactChecker(claim="The Earth is round", use_scholar=False, max_sources=5)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert "confidence_score" in result["result"]
        assert "verdict" in result["result"]
        assert 0 <= result["result"]["confidence_score"] <= 100
        assert result["result"]["verdict"] in ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]

    def test_with_scholar_sources(self):
        """Test fact checking with academic sources."""
        tool = FactChecker(claim="Climate change is real", use_scholar=True, max_sources=10)
        result = tool.run()

        assert result["success"] is True
        assert "supporting_sources" in result["result"]
        assert "contradicting_sources" in result["result"]
        assert "neutral_sources" in result["result"]

    def test_with_provided_sources(self):
        """Test with user-provided sources."""
        tool = FactChecker(
            claim="Water boils at 100°C",
            sources=["https://www.nasa.gov", "https://www.noaa.gov"],
            max_sources=5,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["sources_analyzed"] >= 0

    def test_analysis_summary(self):
        """Test that analysis summary is generated."""
        tool = FactChecker(
            claim="Python is a programming language", use_scholar=False, max_sources=5
        )
        result = tool.run()

        assert result["success"] is True
        assert "analysis_summary" in result["result"]
        assert len(result["result"]["analysis_summary"]) > 0

    def test_empty_claim_validation(self):
        """Test validation of empty claim."""
        with pytest.raises(ValidationError):
            tool = FactChecker(claim="", max_sources=5)
            tool.run()

    def test_invalid_source_url(self):
        """Test validation of invalid source URLs."""
        with pytest.raises(ValidationError):
            tool = FactChecker(claim="Test claim", sources=["not-a-valid-url"], max_sources=5)
            tool.run()

    def test_max_sources_limit(self):
        """Test that max_sources parameter is respected."""
        tool = FactChecker(claim="Test claim", use_scholar=True, max_sources=3)
        result = tool.run()

        assert result["success"] is True
        total_sources = (
            len(result["result"]["supporting_sources"])
            + len(result["result"]["contradicting_sources"])
            + len(result["result"]["neutral_sources"])
        )
        assert total_sources <= 3

    def test_confidence_score_range(self):
        """Test that confidence score is within valid range."""
        tool = FactChecker(claim="2 + 2 = 4", max_sources=5)
        result = tool.run()

        assert result["success"] is True
        confidence = result["result"]["confidence_score"]
        assert isinstance(confidence, int)
        assert 0 <= confidence <= 100

    def test_mock_mode(self):
        """Test that mock mode works correctly."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = FactChecker(claim="Test claim in mock mode", use_scholar=True, max_sources=10)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        # Mock mode should return data
        assert len(result["result"]["supporting_sources"]) > 0


if __name__ == "__main__":
    # Run tests
    print("Running FactChecker tests...")

    # Enable mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic fact check
    print("\n--- Test 1: Basic fact check ---")
    try:
        tool = FactChecker(claim="The Earth is round", use_scholar=False, max_sources=5)
        result = tool.run()
        print(f"✓ Success: {result['success']}")
        print(f"✓ Verdict: {result['result']['verdict']}")
        print(f"✓ Confidence: {result['result']['confidence_score']}/100")
    except Exception as e:
        print(f"✗ Test failed: {e}")

    # Test 2: With scholar sources
    print("\n--- Test 2: With scholar sources ---")
    try:
        tool = FactChecker(claim="Climate change is real", use_scholar=True, max_sources=10)
        result = tool.run()
        print(f"✓ Success: {result['success']}")
        print(f"✓ Supporting sources: {len(result['result']['supporting_sources'])}")
        print(f"✓ Contradicting sources: {len(result['result']['contradicting_sources'])}")
    except Exception as e:
        print(f"✗ Test failed: {e}")

    # Test 3: With provided sources
    print("\n--- Test 3: With provided sources ---")
    try:
        tool = FactChecker(
            claim="Water boils at 100°C",
            sources=["https://www.nasa.gov", "https://www.noaa.gov"],
            max_sources=5,
        )
        result = tool.run()
        print(f"✓ Success: {result['success']}")
        print(f"✓ Sources analyzed: {result['metadata']['sources_analyzed']}")
    except Exception as e:
        print(f"✗ Test failed: {e}")

    # Test 4: Empty claim validation
    print("\n--- Test 4: Empty claim validation ---")
    try:
        tool = FactChecker(claim="", max_sources=5)
        result = tool.run()
        print(f"✗ Should have raised ValidationError")
    except ValidationError as e:
        print(f"✓ Correctly raised ValidationError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Test 5: Invalid URL validation
    print("\n--- Test 5: Invalid URL validation ---")
    try:
        tool = FactChecker(claim="Test", sources=["invalid-url"], max_sources=5)
        result = tool.run()
        print(f"✗ Should have raised ValidationError")
    except ValidationError as e:
        print(f"✓ Correctly raised ValidationError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    print("\n--- All manual tests completed ---")
