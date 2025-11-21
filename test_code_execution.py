#!/usr/bin/env python3
"""Test 3 remaining code execution tools"""

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

# Test 1: bash_tool - uses generic 'input' parameter
def test_bash():
    os.environ["USE_MOCK_APIS"] = "true"
    from tools.code_execution.bash_tool.bash_tool import BashTool
    tool = BashTool(input="echo 'hello world'")
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Bash tool executed")

# Test 2: multiedit_tool - uses generic 'input' parameter with JSON
def test_multiedit():
    from tools.code_execution.multiedit_tool.multiedit_tool import MultieditTool
    import json

    # Create test file first (mock mode has env conflicts)
    test_file = "/tmp/multiedit_test.txt"
    with open(test_file, "w") as f:
        f.write("line 1\nline 2\nline 3")

    # Multiedit expects JSON with file_path and edits
    tool = MultieditTool(
        input=json.dumps({
            "file_path": test_file,
            "edits": [
                {"action": "replace", "old_text": "line 2", "new_text": "LINE 2"}
            ]
        })
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ MultiEdit tool executed")

# Test 3: downloadfilewrapper_tool - expects direct URL string in input
def test_download():
    os.environ["USE_MOCK_APIS"] = "true"
    from tools.code_execution.downloadfilewrapper_tool.downloadfilewrapper_tool import DownloadfilewrapperTool

    # Tool expects just the URL string, not JSON
    tool = DownloadfilewrapperTool(input="https://example.com/test.pdf")
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Download tool executed")

if __name__ == "__main__":
    print("\n🧪 TESTING 3 CODE EXECUTION TOOLS\n")

    test("1. bash_tool", test_bash)
    test("2. multiedit_tool", test_multiedit)
    test("3. downloadfilewrapper_tool", test_download)

    print(f"\n\n{'='*60}")
    print(f"RESULTS: {len(results['passed'])}/3 passed")
    print(f"{'='*60}")
    for p in results["passed"]:
        print(f"✅ {p}")
    for f in results["failed"]:
        print(f"❌ {f}")
