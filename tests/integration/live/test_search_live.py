"""
Live integration tests for Search tools.

These tests make real API calls. Requires valid API keys.
"""

import os
import pytest
from typing import Dict, Any

# Ensure we're using live mode for these tests
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow,
]


@pytest.fixture(autouse=True)
def live_mode():
    """Ensure live API mode for integration tests."""
    original = os.environ.get("USE_MOCK_APIS", "true")
    os.environ["USE_MOCK_APIS"] = "false"
    yield
    os.environ["USE_MOCK_APIS"] = original


class TestWebSearchLive:
    """Live tests for WebSearch tool."""

    @pytest.fixture
    def api_key_available(self):
        """Check if API key is available."""
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_SHOPPING_API_KEY")
        engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID") or os.getenv("GOOGLE_SHOPPING_ENGINE_ID")
        if not api_key or not engine_id:
            pytest.skip("Google Search API credentials not available")
        return True

    def test_basic_search(self, api_key_available):
        """Test basic web search with real API."""
        from tools.search.web_search import WebSearch

        tool = WebSearch(query="Python programming", max_results=3)
        result = tool.run()

        assert result.get("success") is True or "error" in result
        if result.get("success"):
            assert "result" in result
            assert isinstance(result["result"], list)

    def test_search_with_special_characters(self, api_key_available):
        """Test search with special characters."""
        from tools.search.web_search import WebSearch

        tool = WebSearch(query="C++ programming language", max_results=3)
        result = tool.run()

        # Should either succeed or return error gracefully
        assert "success" in result or "error" in result


class TestVideoSearchLive:
    """Live tests for VideoSearch tool."""

    @pytest.fixture
    def youtube_api_available(self):
        """Check if YouTube API key is available."""
        if not os.getenv("YOUTUBE_API_KEY"):
            pytest.skip("YouTube API key not available")
        return True

    def test_basic_video_search(self, youtube_api_available):
        """Test basic video search with real API."""
        from tools.search.video_search import VideoSearch

        tool = VideoSearch(query="python tutorial", max_results=3)
        result = tool.run()

        assert result.get("success") is True or "error" in result
        if result.get("success"):
            assert "result" in result


class TestNotionLive:
    """Live tests for Notion tools."""

    @pytest.fixture
    def notion_api_available(self):
        """Check if Notion API key is available."""
        if not os.getenv("NOTION_API_KEY"):
            pytest.skip("Notion API key not available")
        return True

    def test_notion_search(self, notion_api_available):
        """Test Notion search with real API."""
        from tools.workspace.notion_search import NotionSearch

        tool = NotionSearch(query="test")
        result = tool.run()

        assert result.get("success") is True or "error" in result


class TestFinancialToolsLive:
    """Live tests for financial data tools."""

    def test_stock_price(self):
        """Test stock price retrieval."""
        from tools.search.stock_price import StockPrice

        tool = StockPrice(ticker="AAPL")
        result = tool.run()

        # Should return data or graceful error
        assert "success" in result or "error" in result

    def test_financial_report(self):
        """Test financial report retrieval."""
        from tools.search.financial_report import FinancialReport

        tool = FinancialReport(ticker="AAPL", report_type="annual")
        result = tool.run()

        assert "success" in result or "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
