#!/usr/bin/env python3
"""Quick test of key tools with live APIs"""

import os
import sys
sys.path.insert(0, '/app')

# Bypass rate limiting
from shared import security
security.RateLimiter.check_rate_limit = lambda *args, **kwargs: None

results = {"passed": [], "failed": []}

def test(name, func):
    try:
        print(f"\n{'='*60}\nTesting: {name}\n{'='*60}")
        func()
        results["passed"].append(name)
        print(f"✅ {name} PASSED")
        return True
    except Exception as e:
        results["failed"].append(f"{name}: {str(e)[:100]}")
        print(f"❌ {name} FAILED: {e}")
        return False

# Test 1: Notion Search
def test_notion():
    from tools.workspace.notion_search.notion_search import NotionSearch
    tool = NotionSearch(query="a", max_results=5)
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"Found {len(result['result'])} pages")

# Test 2: Notion Read
def test_notion_read():
    from tools.workspace.notion_search.notion_search import NotionSearch
    from tools.workspace.notion_read.notion_read import NotionRead
    search = NotionSearch(query="a", max_results=1)
    res = search.run()
    if res["success"] and res["result"]:
        page_id = res["result"][0]["id"]
        tool = NotionRead(input=page_id)
        result = tool.run()
        assert result["success"]
        print(f"Read page content: {result['result']['content'][:100]}...")

# Test 3: YouTube Video Search
def test_youtube():
    from tools.search.video_search.video_search import VideoSearch
    tool = VideoSearch(query="Python tutorial", max_results=3)
    result = tool.run()
    assert result["success"]
    print(f"Found {len(result['result'])} videos")

# Test 4: Think tool
def test_think():
    from tools.utils.think.think import Think
    tool = Think(thought="Testing")
    result = tool.run()
    assert result["success"]

# Test 5: Ask for Clarification
def test_clarify():
    from tools.utils.ask_for_clarification.ask_for_clarification import AskForClarification
    tool = AskForClarification(question="Test question?")
    result = tool.run()
    assert result["success"]

if __name__ == "__main__":
    print("\n🧪 QUICK TOOL TEST SUITE\n")

    test("Notion Search", test_notion)
    test("Notion Read", test_notion_read)
    test("YouTube Video Search", test_youtube)
    test("Think Tool", test_think)
    test("Ask Clarification", test_clarify)

    print(f"\n\n{'='*60}")
    print(f"RESULTS: {len(results['passed'])} passed, {len(results['failed'])} failed")
    print(f"{'='*60}")
    for p in results["passed"]:
        print(f"✅ {p}")
    for f in results["failed"]:
        print(f"❌ {f}")
