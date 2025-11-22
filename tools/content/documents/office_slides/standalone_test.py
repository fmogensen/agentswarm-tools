"""
Standalone test for OfficeSlidesTool that doesn't depend on agency_swarm.
Tests the tool implementation directly.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Mock the BaseTool to avoid agency_swarm import issues
from typing import Any, Dict
from pydantic import BaseModel
from abc import abstractmethod


class BaseTool(BaseModel):
    """Mock BaseTool for testing."""

    tool_name: str = "base_tool"
    tool_category: str = "general"

    class Config:
        arbitrary_types_allowed = True

    def run(self) -> Any:
        """Run the tool."""
        return self._execute()

    @abstractmethod
    def _execute(self) -> Any:
        """Execute the tool logic."""
        pass


# Replace the shared.base import
import shared.base

shared.base.BaseTool = BaseTool

# Now import our tool
from tools.document_creation.office_slides.office_slides import OfficeSlidesTool


def test_mock_mode_basic():
    """Test basic functionality in mock mode."""
    print("Test 1: Basic presentation in mock mode")
    os.environ["USE_MOCK_APIS"] = "true"

    tool = OfficeSlidesTool(
        slides=[
            {"title": "Slide 1", "content": ["Point A", "Point B"], "layout": "title_content"},
            {"title": "Slide 2", "content": ["Data"], "layout": "content"},
        ],
        theme="modern",
        title_slide={"title": "Test Presentation", "subtitle": "2025"},
    )
    result = tool.run()

    assert result["success"] is True
    assert result["result"]["slides"] == 3  # 1 title + 2 content
    assert result["result"]["format"] == "pptx"
    assert "presentation_url" in result["result"]
    print("✅ PASS: Basic presentation test")
    return True


def test_mock_mode_pdf():
    """Test PDF format in mock mode."""
    print("\nTest 2: PDF format in mock mode")
    os.environ["USE_MOCK_APIS"] = "true"

    tool = OfficeSlidesTool(
        slides=[{"title": "Test", "content": ["Content"], "layout": "content"}], output_format="pdf"
    )
    result = tool.run()

    assert result["success"] is True
    assert result["result"]["format"] == "pdf"
    print("✅ PASS: PDF format test")
    return True


def test_validation_empty_slides():
    """Test validation for empty slides."""
    print("\nTest 3: Validation - empty slides list")
    os.environ["USE_MOCK_APIS"] = "true"

    try:
        tool = OfficeSlidesTool(slides=[])
        result = tool.run()
        print("❌ FAIL: Should have raised ValidationError")
        return False
    except Exception as e:
        if "cannot be empty" in str(e):
            print("✅ PASS: Correctly raised ValidationError for empty slides")
            return True
        else:
            print(f"❌ FAIL: Wrong error: {e}")
            return False


def test_validation_invalid_theme():
    """Test validation for invalid theme."""
    print("\nTest 4: Validation - invalid theme")
    os.environ["USE_MOCK_APIS"] = "true"

    try:
        tool = OfficeSlidesTool(
            slides=[{"title": "Test", "content": ["Content"], "layout": "content"}],
            theme="invalid_theme",
        )
        result = tool.run()
        print("❌ FAIL: Should have raised ValidationError")
        return False
    except Exception as e:
        if "Invalid theme" in str(e):
            print("✅ PASS: Correctly raised ValidationError for invalid theme")
            return True
        else:
            print(f"❌ FAIL: Wrong error: {e}")
            return False


def test_all_themes():
    """Test all theme options."""
    print("\nTest 5: All theme options")
    os.environ["USE_MOCK_APIS"] = "true"

    themes = ["modern", "classic", "minimal", "corporate"]

    for theme in themes:
        tool = OfficeSlidesTool(
            slides=[{"title": "Test", "content": ["Content"], "layout": "content"}], theme=theme
        )
        result = tool.run()
        assert result["success"] is True

    print("✅ PASS: All themes work correctly")
    return True


def test_all_layouts():
    """Test all layout types."""
    print("\nTest 6: All layout types")
    os.environ["USE_MOCK_APIS"] = "true"

    layouts = ["title_content", "content", "two_column", "blank"]

    for layout in layouts:
        tool = OfficeSlidesTool(
            slides=[{"title": "Test", "content": ["Content"], "layout": layout}]
        )
        result = tool.run()
        assert result["success"] is True

    print("✅ PASS: All layouts work correctly")
    return True


def test_real_mode():
    """Test actual presentation generation."""
    print("\nTest 7: Real presentation generation")
    os.environ["USE_MOCK_APIS"] = "false"

    try:
        tool = OfficeSlidesTool(
            slides=[
                {
                    "title": "Introduction",
                    "content": ["Point 1", "Point 2"],
                    "layout": "title_content",
                },
                {"title": "Details", "content": ["Detail A"], "layout": "content"},
            ],
            theme="modern",
            title_slide={"title": "Test Report", "subtitle": "Q4 2025", "author": "Test User"},
        )

        result = tool.run()

        assert result["success"] is True
        assert result["result"]["slides"] == 3
        assert "file_path" in result["result"]

        # Verify file exists
        file_path = result["result"]["file_path"]
        assert os.path.exists(file_path)

        print(f"✅ PASS: Real presentation generated at {file_path}")
        print(f"   File size: {result['result']['file_size']}")

        # Clean up
        os.remove(file_path)

        return True

    except Exception as e:
        if "not installed" in str(e):
            print("⚠️  SKIP: python-pptx not available")
            return True
        else:
            print(f"❌ FAIL: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("STANDALONE TEST SUITE FOR OfficeSlidesTool")
    print("=" * 60)

    tests = [
        test_mock_mode_basic,
        test_mock_mode_pdf,
        test_validation_empty_slides,
        test_validation_invalid_theme,
        test_all_themes,
        test_all_layouts,
        test_real_mode,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ FAIL: {test.__name__} - {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)

    if all(results):
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
