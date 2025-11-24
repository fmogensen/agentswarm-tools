"""
Test command implementation

Tests tools with mock data to verify functionality.
"""

import importlib
import inspect
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def get_all_tool_classes(verbose: bool = False) -> List[tuple]:
    """Get all tool classes."""
    tools_dir = Path(__file__).parent.parent.parent / "tools"
    tool_classes = []

    for category_dir in tools_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("_"):
            continue

        for tool_file in category_dir.glob("*.py"):
            if tool_file.name.startswith("_"):
                continue

            tool_name = tool_file.stem
            category = category_dir.name

            try:
                module_path = f"tools.{category}.{tool_name}"
                module = importlib.import_module(module_path)

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if hasattr(obj, "tool_name") and not name.startswith("_"):
                        tool_classes.append((tool_name, category, obj))
                        break

            except Exception as e:
                if verbose:
                    print(f"Warning: Could not import {tool_name}: {e}")

    return tool_classes


def test_single_tool(tool_name: str, tool_class: type, verbose: bool = False) -> Dict[str, Any]:
    """Test a single tool."""
    result = {
        "tool": tool_name,
        "success": False,
        "error": None,
        "output": None,
    }

    try:
        # Set mock mode
        os.environ["USE_MOCK_APIS"] = "true"

        # Get test parameters from the tool's test block if available
        # For now, we'll just try to instantiate with minimal params
        if verbose:
            print(f"  Testing {tool_name}...", end=" ")

        # Try to run the tool
        tool_instance = tool_class()
        output = tool_instance.run()

        result["success"] = True
        result["output"] = output

        if verbose:
            print("✓ PASS")

    except Exception as e:
        result["error"] = str(e)
        if verbose:
            print(f"✗ FAIL: {e}")

    finally:
        # Clean up mock mode
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    return result


def execute(args) -> int:
    """Execute the test command."""
    try:
        # Enable mock mode
        if args.mock:
            os.environ["USE_MOCK_APIS"] = "true"

        results = []
        passed = 0
        failed = 0

        if args.tool:
            # Test single tool
            tools_dir = Path(__file__).parent.parent.parent / "tools"
            tool_class = None
            category = None

            for category_dir in tools_dir.iterdir():
                if not category_dir.is_dir() or category_dir.name.startswith("_"):
                    continue

                potential_file = category_dir / f"{args.tool}.py"
                if potential_file.exists():
                    category = category_dir.name
                    module_path = f"tools.{category}.{args.tool}"
                    module = importlib.import_module(module_path)

                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if hasattr(obj, "tool_name") and not name.startswith("_"):
                            tool_class = obj
                            break
                    break

            if not tool_class:
                print(f"Tool '{args.tool}' not found", file=sys.stderr)
                return 1

            result = test_single_tool(args.tool, tool_class, args.verbose)
            results.append(result)

        else:
            # Test all tools
            print("Testing all tools...\n")
            tool_classes = get_all_tool_classes(args.verbose)

            for tool_name, category, tool_class in tool_classes:
                result = test_single_tool(tool_name, tool_class, args.verbose)
                results.append(result)

        # Count results
        for result in results:
            if result["success"]:
                passed += 1
            else:
                failed += 1

        # Print summary
        print(f"\n{'=' * 60}")
        print(f"Test Summary")
        print(f"{'=' * 60}")
        print(f"Total:   {len(results)}")
        print(f"Passed:  {passed} ✓")
        print(f"Failed:  {failed} ✗")

        if failed > 0:
            print(f"\nFailed tests:")
            for result in results:
                if not result["success"]:
                    print(f"  - {result['tool']}: {result['error']}")

        return 0 if failed == 0 else 1

    except Exception as e:
        print(f"Error running tests: {e}", file=sys.stderr)
        return 1
    finally:
        # Clean up mock mode
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]
