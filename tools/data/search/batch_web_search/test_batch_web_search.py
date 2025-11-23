"""
Unit tests for BatchWebSearch tool
"""

import os
import sys

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

from tools.data.search.batch_web_search.batch_web_search import BatchWebSearch


def test_batch_web_search_mock():
    """Test BatchWebSearch with mock mode enabled."""
    # Enable mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    tool = BatchWebSearch(
        queries=[
            "Python programming",
            "Machine learning basics",
            "Data science tools",
        ],
        max_results_per_query=3,
        max_workers=5,
        show_progress=False,
    )

    result = tool.run()

    # The BaseTool.run() returns the result from _execute directly
    # which is structured as {"success": True, "result": {...}, "metadata": {...}}
    print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")

    # Check if result is success
    assert isinstance(result, dict)
    assert result.get("success") == True or result.get("total_queries") == 3

    # The result might be wrapped or unwrapped depending on _execute
    if "result" in result:
        data = result["result"]
    else:
        data = result

    assert data.get("total_queries") == 3
    assert data.get("successful_queries") == 3
    assert data.get("mock") == True

    print("✓ test_batch_web_search_mock passed")


def test_batch_web_search_validation():
    """Test BatchWebSearch validation."""
    os.environ["USE_MOCK_APIS"] = "true"

    # Test empty queries
    try:
        tool = BatchWebSearch(
            queries=[],
            max_results_per_query=3,
        )
        result = tool.run()
        assert False, "Should have raised validation error"
    except Exception as e:
        error_msg = str(e).lower()
        assert "min" in error_msg or "at least" in error_msg or "too_short" in error_msg

    print("✓ test_batch_web_search_validation passed")


if __name__ == "__main__":
    print("Testing BatchWebSearch...")
    test_batch_web_search_mock()
    test_batch_web_search_validation()
    print("\n✓ All BatchWebSearch tests passed!")
