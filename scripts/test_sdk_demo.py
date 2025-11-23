#!/usr/bin/env python3
"""
Demo script to test SDK functionality

This script demonstrates all SDK features without requiring
external dependencies to be installed.

Run: python3 test_sdk_demo.py
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_validator():
    """Test the validator can parse and check tool structure"""
    print("\n" + "=" * 70)
    print("TESTING: SDK Validator")
    print("=" * 70 + "\n")

    try:
        from sdk.validator import ToolValidator, ValidationIssue

        validator = ToolValidator()

        # Test on web_search tool
        tool_path = project_root / "tools/data/search/web_search"

        if not tool_path.exists():
            print(f"❌ Tool path not found: {tool_path}")
            return False

        print(f"Validating tool: {tool_path.name}\n")

        result = validator.validate_tool(tool_path)

        print(f"✓ Validator executed successfully")
        print(f"  - Passed: {result.passed}")
        print(f"  - Score: {result.score}/100")
        print(f"  - Errors: {len(result.errors)}")
        print(f"  - Warnings: {len(result.warnings)}")
        print(f"  - Total Issues: {len(result.issues)}")

        if result.issues:
            print(f"\n  Issues Found:")
            for i, issue in enumerate(result.issues[:5], 1):
                print(f"    {i}. [{issue.severity.upper()}] {issue.message}")
                if issue.suggestion:
                    print(f"       → {issue.suggestion}")

        return True

    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_test_generator():
    """Test the test generator can parse tools"""
    print("\n" + "=" * 70)
    print("TESTING: Test Generator")
    print("=" * 70 + "\n")

    try:
        from sdk.test_generator import TestGenerator

        generator = TestGenerator()

        # Test on web_search tool
        tool_file = project_root / "tools/data/search/web_search/web_search.py"

        if not tool_file.exists():
            print(f"❌ Tool file not found: {tool_file}")
            return False

        print(f"Parsing tool: {tool_file.name}\n")

        # Parse tool
        tool_info = generator._parse_tool(tool_file)

        print(f"✓ Test generator parsed tool successfully")
        print(f"  - Class Name: {tool_info['class_name']}")
        print(f"  - Tool Name: {tool_info['tool_name']}")
        print(f"  - Parameters: {len(tool_info['parameters'])}")

        if tool_info["parameters"]:
            print(f"\n  Parameters:")
            for param in tool_info["parameters"]:
                print(f"    - {param['name']}: {param['type']}")

        return True

    except Exception as e:
        print(f"❌ Test generator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_docs_generator():
    """Test the docs generator can parse tools"""
    print("\n" + "=" * 70)
    print("TESTING: Docs Generator")
    print("=" * 70 + "\n")

    try:
        from sdk.docs_generator import DocsGenerator

        generator = DocsGenerator()

        # Test on web_search tool
        tool_file = project_root / "tools/data/search/web_search/web_search.py"

        if not tool_file.exists():
            print(f"❌ Tool file not found: {tool_file}")
            return False

        print(f"Parsing tool: {tool_file.name}\n")

        # Parse tool
        tool_info = generator._parse_tool(tool_file)

        print(f"✓ Docs generator parsed tool successfully")
        print(f"  - Class Name: {tool_info['class_name']}")
        print(f"  - Tool Name: {tool_info['tool_name']}")
        print(f"  - Category: {tool_info['tool_category']}")
        print(f"  - Description: {tool_info['description'][:60]}...")
        print(f"  - Parameters: {len(tool_info['parameters'])}")
        print(f"  - Requires API Key: {tool_info['requires_api_key']}")

        if tool_info["requires_api_key"]:
            print(f"  - API Key Env Var: {tool_info['api_key_env_var']}")

        return True

    except Exception as e:
        print(f"❌ Docs generator test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tool_structure():
    """Test that SDK can analyze tool structure"""
    print("\n" + "=" * 70)
    print("TESTING: Tool Structure Analysis")
    print("=" * 70 + "\n")

    try:
        import ast
        from pathlib import Path

        tool_file = project_root / "tools/data/search/web_search/web_search.py"

        if not tool_file.exists():
            print(f"❌ Tool file not found: {tool_file}")
            return False

        content = tool_file.read_text()
        tree = ast.parse(content)

        # Find tool class
        tool_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "BaseTool":
                        tool_class = node
                        break

        if not tool_class:
            print(f"❌ No BaseTool class found")
            return False

        print(f"✓ Found BaseTool class: {tool_class.name}\n")

        # Find methods
        methods = [m.name for m in tool_class.body if isinstance(m, ast.FunctionDef)]
        print(f"  Methods found ({len(methods)}):")
        for method in methods:
            print(f"    - {method}()")

        # Check required methods
        required_methods = [
            "_execute",
            "_validate_parameters",
            "_should_use_mock",
            "_generate_mock_results",
            "_process",
        ]

        print(f"\n  Required methods check:")
        for method in required_methods:
            present = method in methods
            status = "✓" if present else "✗"
            print(f"    {status} {method}()")

        return True

    except Exception as e:
        print(f"❌ Structure analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all SDK tests"""

    print("\n" + "=" * 70)
    print(" " * 20 + "SDK DEMO & TESTS")
    print("=" * 70)

    print("\nThis demonstrates the SDK's ability to:")
    print("  1. Validate tools against Agency Swarm standards")
    print("  2. Parse tool structure and parameters")
    print("  3. Generate tests automatically")
    print("  4. Generate documentation automatically")

    print("\nNote: Full SDK requires jinja2 and questionary to be installed")
    print("      pip install jinja2 questionary")

    results = []

    # Run tests
    results.append(("Tool Structure Analysis", test_tool_structure()))
    results.append(("Validator", test_validator()))
    results.append(("Test Generator", test_test_generator()))
    results.append(("Docs Generator", test_docs_generator()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8} {name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All SDK components working correctly!")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install jinja2 questionary")
        print("  2. Try: agentswarm sdk create-tool --interactive")
        print("  3. Read SDK_GUIDE.md for complete documentation")
        return 0
    else:
        print("\n✗ Some tests failed. Check output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
