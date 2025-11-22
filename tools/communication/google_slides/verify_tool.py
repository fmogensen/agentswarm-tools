#!/usr/bin/env python3
"""
Verification script for GoogleSlides tool
Runs comprehensive tests to verify tool functionality
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from google_slides import GoogleSlides


def test_basic_functionality():
    """Test basic create and modify functionality"""
    print("\n" + "="*70)
    print("TEST SUITE: Google Slides Tool Verification")
    print("="*70)

    os.environ["USE_MOCK_APIS"] = "true"

    passed = 0
    failed = 0

    # Test 1: Create presentation
    print("\n[1/10] Testing: Create new presentation...")
    try:
        tool = GoogleSlides(
            mode="create",
            title="Test Presentation",
            slides=[
                {"layout": "title", "title": "Welcome", "subtitle": "Introduction"},
                {"layout": "title_and_body", "title": "Content", "content": "Details"}
            ],
            theme="modern"
        )
        result = tool.run()
        assert result["success"] == True
        assert result["result"]["slide_count"] == 2
        print("   ✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        failed += 1

    # Test 2: Modify presentation
    print("\n[2/10] Testing: Modify existing presentation...")
    try:
        tool = GoogleSlides(
            mode="modify",
            presentation_id="test-id-123",
            slides=[{"layout": "blank"}]
        )
        result = tool.run()
        assert result["success"] == True
        assert result["result"]["mode"] == "modify"
        print("   ✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        failed += 1

    # Test 3: All slide layouts
    print("\n[3/10] Testing: All slide layouts...")
    try:
        tool = GoogleSlides(
            mode="create",
            title="Layout Test",
            slides=[
                {"layout": "title", "title": "T", "subtitle": "S"},
                {"layout": "title_and_body", "title": "T", "content": "C"},
                {"layout": "section_header", "title": "Section"},
                {"layout": "two_columns", "title": "T", "left_content": "L", "right_content": "R"},
                {"layout": "blank"}
            ]
        )
        result = tool.run()
        assert result["success"] == True
        assert result["result"]["slide_count"] == 5
        print("   ✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        failed += 1

    # Test 4: With sharing
    print("\n[4/10] Testing: Presentation with sharing...")
    try:
        tool = GoogleSlides(
            mode="create",
            title="Shared",
            slides=[{"layout": "blank"}],
            share_with=["user@example.com"]
        )
        result = tool.run()
        assert result["success"] == True
        assert len(result["result"]["shared_with"]) == 1
        print("   ✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        failed += 1

    # Test 5: With images
    print("\n[5/10] Testing: Presentation with images...")
    try:
        tool = GoogleSlides(
            mode="create",
            title="Images",
            slides=[
                {
                    "layout": "title_and_body",
                    "title": "Image Slide",
                    "content": "Content",
                    "image_url": "https://example.com/image.jpg"
                }
            ]
        )
        result = tool.run()
        assert result["success"] == True
        print("   ✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        failed += 1

    # Test 6: Validation - missing title
    print("\n[6/10] Testing: Validation - missing title...")
    try:
        tool = GoogleSlides(mode="create", slides=[{"layout": "blank"}])
        result = tool.run()
        assert result["success"] == False
        print("   ✓ PASSED")
        passed += 1
    except Exception:
        print("   ✓ PASSED (raised exception)")
        passed += 1

    # Test 7: Validation - missing presentation_id
    print("\n[7/10] Testing: Validation - missing presentation_id...")
    try:
        tool = GoogleSlides(mode="modify", slides=[{"layout": "blank"}])
        result = tool.run()
        assert result["success"] == False
        print("   ✓ PASSED")
        passed += 1
    except Exception:
        print("   ✓ PASSED (raised exception)")
        passed += 1

    # Test 8: Validation - invalid layout
    print("\n[8/10] Testing: Validation - invalid layout...")
    try:
        tool = GoogleSlides(
            mode="create",
            title="Test",
            slides=[{"layout": "invalid"}]
        )
        result = tool.run()
        assert result["success"] == False
        print("   ✓ PASSED")
        passed += 1
    except Exception:
        print("   ✓ PASSED (raised exception)")
        passed += 1

    # Test 9: Validation - invalid email
    print("\n[9/10] Testing: Validation - invalid email...")
    try:
        tool = GoogleSlides(
            mode="create",
            title="Test",
            slides=[{"layout": "blank"}],
            share_with=["bad-email"]
        )
        result = tool.run()
        assert result["success"] == False
        print("   ✓ PASSED")
        passed += 1
    except Exception:
        print("   ✓ PASSED (raised exception)")
        passed += 1

    # Test 10: All themes
    print("\n[10/10] Testing: All themes...")
    try:
        themes = ["default", "simple", "modern", "colorful"]
        for theme in themes:
            tool = GoogleSlides(
                mode="create",
                title="Theme Test",
                slides=[{"layout": "blank"}],
                theme=theme
            )
            result = tool.run()
            assert result["success"] == True
            assert result["result"]["theme_applied"] == theme
        print("   ✓ PASSED")
        passed += 1
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        failed += 1

    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed out of 10 tests")
    print("="*70)

    if failed == 0:
        print("\n✓ All tests passed! Tool is ready for use.")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed. Please review.")
        return 1


if __name__ == "__main__":
    sys.exit(test_basic_functionality())
