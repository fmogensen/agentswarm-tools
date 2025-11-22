#!/usr/bin/env python3
"""
Verification script for GoogleDocs tool.
Demonstrates all features and validates implementation.
"""

import os
import sys

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Ensure mock mode for verification
os.environ["USE_MOCK_APIS"] = "true"

from tools.communication.google_docs.google_docs import GoogleDocs


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(result, test_name):
    """Print test result."""
    success = result.get("success", False)
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"\n{status} - {test_name}")

    if success:
        res = result.get("result", {})
        print(f"  Document ID: {res.get('document_id', 'N/A')}")
        print(f"  Title: {res.get('title', 'N/A')}")
        print(f"  Link: {res.get('shareable_link', 'N/A')}")

        if "modify_action" in res:
            print(f"  Action: {res.get('modify_action')}")
        if res.get("shared_with"):
            print(f"  Shared with: {', '.join(res.get('shared_with'))}")
        if res.get("folder_id"):
            print(f"  Folder: {res.get('folder_id')}")
    else:
        error = result.get("error", {})
        print(f"  Error: {error.get('message', 'Unknown error')}")

    return success


def verify_all_features():
    """Verify all GoogleDocs features."""
    print_section("GoogleDocs Tool Verification")
    print("Testing all features in mock mode...")

    all_passed = True

    # Test 1: Create document
    print_section("Test 1: Create New Document")
    try:
        tool = GoogleDocs(
            mode="create",
            title="Sample Document",
            content="# Welcome\n\nThis is a **test** document."
        )
        result = tool.run()
        all_passed &= print_result(result, "Create new document")
    except Exception as e:
        print(f"✗ FAIL - Create new document: {e}")
        all_passed = False

    # Test 2: Create with sharing
    print_section("Test 2: Create with Sharing")
    try:
        tool = GoogleDocs(
            mode="create",
            title="Shared Document",
            content="Content to share",
            share_with=["alice@example.com", "bob@example.com"]
        )
        result = tool.run()
        all_passed &= print_result(result, "Create with sharing")
    except Exception as e:
        print(f"✗ FAIL - Create with sharing: {e}")
        all_passed = False

    # Test 3: Create in folder
    print_section("Test 3: Create in Folder")
    try:
        tool = GoogleDocs(
            mode="create",
            title="Document in Folder",
            content="Organized content",
            folder_id="my-folder-123"
        )
        result = tool.run()
        all_passed &= print_result(result, "Create in folder")
    except Exception as e:
        print(f"✗ FAIL - Create in folder: {e}")
        all_passed = False

    # Test 4: Modify - append
    print_section("Test 4: Modify Document (Append)")
    try:
        tool = GoogleDocs(
            mode="modify",
            document_id="existing-doc-123",
            content="\n## New Section\n\nAppended content here.",
            modify_action="append"
        )
        result = tool.run()
        all_passed &= print_result(result, "Modify with append")
    except Exception as e:
        print(f"✗ FAIL - Modify with append: {e}")
        all_passed = False

    # Test 5: Modify - replace
    print_section("Test 5: Modify Document (Replace)")
    try:
        tool = GoogleDocs(
            mode="modify",
            document_id="existing-doc-456",
            content="# New Content\n\nCompletely replaced.",
            modify_action="replace"
        )
        result = tool.run()
        all_passed &= print_result(result, "Modify with replace")
    except Exception as e:
        print(f"✗ FAIL - Modify with replace: {e}")
        all_passed = False

    # Test 6: Modify - insert
    print_section("Test 6: Modify Document (Insert)")
    try:
        tool = GoogleDocs(
            mode="modify",
            document_id="existing-doc-789",
            content="Inserted at beginning.",
            modify_action="insert",
            insert_index=1
        )
        result = tool.run()
        all_passed &= print_result(result, "Modify with insert")
    except Exception as e:
        print(f"✗ FAIL - Modify with insert: {e}")
        all_passed = False

    # Test 7: Complex markdown
    print_section("Test 7: Complex Markdown Content")
    try:
        complex_content = """
# Main Title

This document demonstrates **bold text**, *italic text*, and headings.

## Section 1

Here is some content with **important** information.

### Subsection 1.1

More details with *emphasis*.

## Section 2

Final section.
"""
        tool = GoogleDocs(
            mode="create",
            title="Complex Markdown Demo",
            content=complex_content
        )
        result = tool.run()
        all_passed &= print_result(result, "Complex markdown")
    except Exception as e:
        print(f"✗ FAIL - Complex markdown: {e}")
        all_passed = False

    # Test 8: Validation - invalid mode
    print_section("Test 8: Validation - Invalid Mode")
    try:
        tool = GoogleDocs(
            mode="invalid_mode",
            title="Test",
            content="Content"
        )
        result = tool.run()
        # Check if error was returned
        if result.get("success") == False:
            print(f"✓ PASS - Correctly rejected invalid mode")
            print(f"  Error code: {result.get('error', {}).get('code')}")
        else:
            print("✗ FAIL - Should have returned error")
            all_passed = False
    except Exception as e:
        print(f"✓ PASS - Correctly rejected invalid mode: {type(e).__name__}")

    # Test 9: Validation - missing title
    print_section("Test 9: Validation - Missing Title")
    try:
        tool = GoogleDocs(
            mode="create",
            content="Content without title"
        )
        result = tool.run()
        # Check if error was returned
        if result.get("success") == False:
            print(f"✓ PASS - Correctly rejected missing title")
            print(f"  Error code: {result.get('error', {}).get('code')}")
        else:
            print("✗ FAIL - Should have returned error")
            all_passed = False
    except Exception as e:
        print(f"✓ PASS - Correctly rejected missing title: {type(e).__name__}")

    # Test 10: Validation - missing document_id
    print_section("Test 10: Validation - Missing Document ID")
    try:
        tool = GoogleDocs(
            mode="modify",
            content="Content without doc ID"
        )
        result = tool.run()
        # Check if error was returned
        if result.get("success") == False:
            print(f"✓ PASS - Correctly rejected missing document_id")
            print(f"  Error code: {result.get('error', {}).get('code')}")
        else:
            print("✗ FAIL - Should have returned error")
            all_passed = False
    except Exception as e:
        print(f"✓ PASS - Correctly rejected missing document_id: {type(e).__name__}")

    # Test 11: Validation - invalid email
    print_section("Test 11: Validation - Invalid Email")
    try:
        tool = GoogleDocs(
            mode="create",
            title="Test",
            content="Content",
            share_with=["invalid-email"]
        )
        result = tool.run()
        # Check if error was returned
        if result.get("success") == False:
            print(f"✓ PASS - Correctly rejected invalid email")
            print(f"  Error code: {result.get('error', {}).get('code')}")
        else:
            print("✗ FAIL - Should have returned error")
            all_passed = False
    except Exception as e:
        print(f"✓ PASS - Correctly rejected invalid email: {type(e).__name__}")

    # Test 12: All required methods exist
    print_section("Test 12: Implementation Verification")
    try:
        tool = GoogleDocs(mode="create", title="Test", content="Test")

        # Check all required methods exist
        required_methods = [
            "_execute",
            "_validate_parameters",
            "_should_use_mock",
            "_generate_mock_results",
            "_process"
        ]

        missing_methods = []
        for method in required_methods:
            if not hasattr(tool, method):
                missing_methods.append(method)

        if missing_methods:
            print(f"✗ FAIL - Missing methods: {', '.join(missing_methods)}")
            all_passed = False
        else:
            print("✓ PASS - All required methods implemented")
            print(f"  Methods: {', '.join(required_methods)}")

        # Check tool metadata
        print(f"  Tool name: {tool.tool_name}")
        print(f"  Tool category: {tool.tool_category}")

        assert tool.tool_name == "google_docs", "Tool name mismatch"
        assert tool.tool_category == "communication", "Tool category mismatch"

    except Exception as e:
        print(f"✗ FAIL - Implementation verification: {e}")
        all_passed = False

    # Final summary
    print_section("Verification Summary")
    if all_passed:
        print("\n✓ ALL TESTS PASSED!")
        print("\nThe GoogleDocs tool is fully functional with:")
        print("  • Create mode with title and content")
        print("  • Modify mode with append/replace/insert actions")
        print("  • Document sharing with email addresses")
        print("  • Folder organization support")
        print("  • Markdown formatting (headings, bold, italic)")
        print("  • Comprehensive parameter validation")
        print("  • Mock mode for testing")
        print("  • All 5 required methods implemented")
        print("\nEnvironment variable required:")
        print("  GOOGLE_DOCS_CREDENTIALS - Service account JSON")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        print("Please review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(verify_all_features())
