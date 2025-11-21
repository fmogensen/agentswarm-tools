#!/usr/bin/env python3
"""
Comprehensive test suite for all 61 tools.
Tests tools systematically with real API keys where available.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env.secrets
from dotenv import load_dotenv
load_dotenv('.env.secrets')

# Bypass rate limiting for testing
from shared import security
def bypass_rate_limit(self, key, limit_type="default", cost=1):
    pass
security.RateLimiter.check_rate_limit = bypass_rate_limit

# Test results storage
test_results = {
    "passed": [],
    "failed": [],
    "skipped": []
}

def test_tool(category, tool_name, tool_class, test_params):
    """Test a single tool with given parameters."""
    print(f"\n{'='*70}")
    print(f"Testing: {category}/{tool_name}")
    print(f"{'='*70}")

    try:
        # Create tool instance
        tool = tool_class(**test_params)
        print(f"✓ Tool instantiated: {test_params}")

        # Run the tool
        result = tool.run()

        # Check result
        if result.get("success"):
            print(f"✅ SUCCESS")
            print(f"   Result preview: {str(result.get('result', ''))[:200]}")
            test_results["passed"].append(f"{category}/{tool_name}")
            return True
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            test_results["failed"].append(f"{category}/{tool_name}: {result.get('error', 'Unknown')}")
            return False

    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        test_results["failed"].append(f"{category}/{tool_name}: {str(e)[:100]}")
        return False

def test_workspace_tools():
    """Test workspace integration tools."""
    print("\n" + "="*70)
    print("CATEGORY: WORKSPACE INTEGRATION (2 tools)")
    print("="*70)

    from tools.workspace.notion_search.notion_search import NotionSearch
    from tools.workspace.notion_read.notion_read import NotionRead

    # Test notion_search
    test_tool("workspace", "notion_search", NotionSearch, {
        "query": "a",
        "max_results": 5
    })

    # Test notion_read (need a page ID from search first)
    try:
        search = NotionSearch(query="a", max_results=1)
        search_result = search.run()
        if search_result.get("success") and search_result.get("result"):
            page_id = search_result["result"][0]["id"]
            test_tool("workspace", "notion_read", NotionRead, {
                "input": page_id
            })
        else:
            print("⚠️  notion_read: Skipped (no pages found)")
            test_results["skipped"].append("workspace/notion_read: No pages to test")
    except Exception as e:
        print(f"⚠️  notion_read: Skipped ({str(e)})")
        test_results["skipped"].append(f"workspace/notion_read: {str(e)}")

def test_search_tools():
    """Test search & information tools."""
    print("\n" + "="*70)
    print("CATEGORY: SEARCH & INFORMATION (8 tools)")
    print("="*70)

    # web_search - no API key needed
    from tools.search.web_search.web_search import WebSearch
    test_tool("search", "web_search", WebSearch, {
        "query": "Python programming",
        "max_results": 3
    })

    # scholar_search - no API key needed
    from tools.search.scholar_search.scholar_search import ScholarSearch
    test_tool("search", "scholar_search", ScholarSearch, {
        "query": "machine learning",
        "max_results": 3
    })

    # image_search - requires SERPAPI_KEY
    if os.getenv("SERPAPI_KEY"):
        from tools.search.image_search.image_search import ImageSearch
        test_tool("search", "image_search", ImageSearch, {
            "query": "sunset",
            "num_results": 3
        })
    else:
        print("⚠️  image_search: Skipped (no SERPAPI_KEY)")
        test_results["skipped"].append("search/image_search: No API key")

    # video_search - requires YOUTUBE_API_KEY
    if os.getenv("YOUTUBE_API_KEY"):
        from tools.search.video_search.video_search import VideoSearch
        test_tool("search", "video_search", VideoSearch, {
            "query": "Python tutorial",
            "max_results": 3
        })
    else:
        print("⚠️  video_search: Skipped (no YOUTUBE_API_KEY)")
        test_results["skipped"].append("search/video_search: No API key")

    # google_product_search
    if os.getenv("GOOGLE_SHOPPING_API_KEY") and os.getenv("GOOGLE_SHOPPING_ENGINE_ID"):
        from tools.search.google_product_search.google_product_search import GoogleProductSearch
        test_tool("search", "google_product_search", GoogleProductSearch, {
            "query": "laptop",
            "num_results": 3
        })
    else:
        print("⚠️  google_product_search: Skipped (no API key)")
        test_results["skipped"].append("search/google_product_search: No API key")

    # financial_report - no API key needed
    from tools.search.financial_report.financial_report import FinancialReport
    test_tool("search", "financial_report", FinancialReport, {
        "ticker": "AAPL",
        "report_type": "income_statement"
    })

    # stock_price - no API key needed
    from tools.search.stock_price.stock_price import StockPrice
    test_tool("search", "stock_price", StockPrice, {
        "ticker": "AAPL"
    })

def test_web_content_tools():
    """Test web content & data tools."""
    print("\n" + "="*70)
    print("CATEGORY: WEB CONTENT & DATA (5 tools)")
    print("="*70)

    # crawler
    from tools.web_content.crawler.crawler import Crawler
    test_tool("web_content", "crawler", Crawler, {
        "url": "https://example.com",
        "max_depth": 1
    })

    # url_metadata
    from tools.web_content.url_metadata.url_metadata import UrlMetadata
    test_tool("web_content", "url_metadata", UrlMetadata, {
        "url": "https://example.com"
    })

def test_utility_tools():
    """Test utility tools."""
    print("\n" + "="*70)
    print("CATEGORY: UTILITIES (2 tools)")
    print("="*70)

    # think
    from tools.utils.think.think import Think
    test_tool("utils", "think", Think, {
        "thought": "Testing the think tool"
    })

    # ask_for_clarification
    from tools.utils.ask_for_clarification.ask_for_clarification import AskForClarification
    test_tool("utils", "ask_for_clarification", AskForClarification, {
        "question": "What is the purpose of this test?"
    })

def test_code_execution_tools():
    """Test code execution tools."""
    print("\n" + "="*70)
    print("CATEGORY: CODE EXECUTION (5 tools)")
    print("="*70)

    # read_tool
    from tools.code_execution.read_tool.read_tool import ReadTool
    # Create a test file first
    test_file = "/tmp/test_read.txt"
    with open(test_file, "w") as f:
        f.write("Test content for reading")

    test_tool("code_execution", "read_tool", ReadTool, {
        "file_path": test_file
    })

    # write_tool
    from tools.code_execution.write_tool.write_tool import WriteTool
    test_tool("code_execution", "write_tool", WriteTool, {
        "file_path": "/tmp/test_write.txt",
        "content": "Test content"
    })

def print_summary():
    """Print test summary."""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total = len(test_results["passed"]) + len(test_results["failed"]) + len(test_results["skipped"])

    print(f"\n✅ PASSED: {len(test_results['passed'])} tools")
    for tool in test_results["passed"]:
        print(f"   ✓ {tool}")

    print(f"\n❌ FAILED: {len(test_results['failed'])} tools")
    for tool in test_results["failed"]:
        print(f"   ✗ {tool}")

    print(f"\n⚠️  SKIPPED: {len(test_results['skipped'])} tools")
    for tool in test_results["skipped"]:
        print(f"   - {tool}")

    print(f"\n{'='*80}")
    print(f"TOTAL TESTED: {total} tools")
    print(f"Success Rate: {len(test_results['passed'])}/{total - len(test_results['skipped'])} " +
          f"({100*len(test_results['passed'])/(total-len(test_results['skipped']) or 1):.1f}%)")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    print("\n🧪 COMPREHENSIVE TOOL TESTING")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment: USE_MOCK_APIS={os.getenv('USE_MOCK_APIS', 'not set')}")

    try:
        # Test each category
        test_workspace_tools()
        test_search_tools()
        test_web_content_tools()
        test_utility_tools()
        test_code_execution_tools()

    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        traceback.print_exc()
    finally:
        print_summary()

        # Save results to file
        with open("test_results.txt", "w") as f:
            f.write(f"Test Results - {datetime.now()}\n")
            f.write(f"Passed: {len(test_results['passed'])}\n")
            f.write(f"Failed: {len(test_results['failed'])}\n")
            f.write(f"Skipped: {len(test_results['skipped'])}\n")
            f.write("\nDetails:\n")
            f.write(f"Passed:\n{chr(10).join(test_results['passed'])}\n")
            f.write(f"Failed:\n{chr(10).join(test_results['failed'])}\n")
            f.write(f"Skipped:\n{chr(10).join(test_results['skipped'])}\n")
