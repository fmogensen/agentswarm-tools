#!/usr/bin/env python3
"""Test the 3 fixed search tools"""

import os
import sys
sys.path.insert(0, '/app')

# Bypass rate limiting
from shared import security
security.RateLimiter.check_rate_limit = lambda *args, **kwargs: None

results = {"passed": [], "failed": []}

def test(name, func):
    try:
        print(f"\n{'='*60}\n{name}\n{'='*60}")
        func()
        results["passed"].append(name)
        print(f"✅ {name} PASSED")
        return True
    except Exception as e:
        results["failed"].append(f"{name}: {str(e)[:100]}")
        print(f"❌ {name} FAILED: {e}")
        return False

# Test 1: web_search (mock mode)
def test_web_search_mock():
    os.environ["USE_MOCK_APIS"] = "true"
    from tools.search.web_search.web_search import WebSearch
    tool = WebSearch(query="Python programming", max_results=3)
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    assert len(result["result"]) == 3
    print(f"✓ Got {len(result['result'])} mock results")

# Test 2: scholar_search (mock mode)
def test_scholar_search_mock():
    os.environ["USE_MOCK_APIS"] = "true"
    from tools.search.scholar_search.scholar_search import ScholarSearch
    tool = ScholarSearch(query="machine learning", max_results=5)
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    assert len(result["result"]) == 5
    print(f"✓ Got {len(result['result'])} mock articles")

# Test 3: google_product_search (mock mode)
def test_google_product_search_mock():
    os.environ["USE_MOCK_APIS"] = "true"
    from tools.search.google_product_search.google_product_search import GoogleProductSearch
    tool = GoogleProductSearch(query="laptop", num=5)
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    products = result["result"].get("products", [])
    assert len(products) == 5
    print(f"✓ Got {len(products)} mock products")

# Test 4: scholar_search (real API)
def test_scholar_search_real():
    os.environ["USE_MOCK_APIS"] = "false"
    from tools.search.scholar_search.scholar_search import ScholarSearch
    tool = ScholarSearch(query="neural networks", max_results=3)
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    assert len(result["result"]) > 0
    first = result["result"][0]
    print(f"✓ Got {len(result['result'])} real articles")
    print(f"  First: {first['title'][:60]}...")

if __name__ == "__main__":
    print("\n🧪 TESTING 3 FIXED SEARCH TOOLS\n")

    test("1. web_search (mock)", test_web_search_mock)
    test("2. scholar_search (mock)", test_scholar_search_mock)
    test("3. google_product_search (mock)", test_google_product_search_mock)
    test("4. scholar_search (real API)", test_scholar_search_real)

    print(f"\n\n{'='*60}")
    print(f"RESULTS: {len(results['passed'])}/4 passed")
    print(f"{'='*60}")
    for p in results["passed"]:
        print(f"✅ {p}")
    for f in results["failed"]:
        print(f"❌ {f}")
