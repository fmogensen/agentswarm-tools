"""
Validate command implementation

Validates tool structure and compliance with Agency Swarm standards.
"""

import sys
import ast
import inspect
import importlib
from pathlib import Path
from typing import Dict, Any, List


def validate_tool_file(tool_path: Path, strict: bool = False) -> Dict[str, Any]:
    """Validate a single tool file."""
    result = {
        'tool': tool_path.stem,
        'path': str(tool_path),
        'valid': True,
        'errors': [],
        'warnings': [],
    }

    try:
        # Parse the file
        with open(tool_path, 'r') as f:
            content = f.read()

        tree = ast.parse(content)

        # Check for required imports
        has_field_import = False
        has_basetool_import = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'pydantic' and any(alias.name == 'Field' for alias in node.names):
                    has_field_import = True
                if node.module and 'base' in node.module and any(alias.name == 'BaseTool' for alias in node.names):
                    has_basetool_import = True

        if not has_field_import:
            result['warnings'].append("Missing 'from pydantic import Field'")

        if not has_basetool_import:
            result['errors'].append("Missing BaseTool import")
            result['valid'] = False

        # Check for test block
        has_test_block = '__main__' in content

        if not has_test_block:
            if strict:
                result['errors'].append("Missing if __name__ == '__main__': test block")
                result['valid'] = False
            else:
                result['warnings'].append("Missing test block (recommended)")

        # Check for hardcoded secrets
        suspicious_patterns = [
            'password = "',
            'api_key = "',
            'secret = "',
            'token = "',
        ]

        for pattern in suspicious_patterns:
            if pattern in content.lower():
                result['warnings'].append(f"Possible hardcoded secret: {pattern}")

        # Try to import and validate class
        try:
            category = tool_path.parent.name
            tool_name = tool_path.stem
            module_path = f"tools.{category}.{tool_name}"
            module = importlib.import_module(module_path)

            # Find tool class
            tool_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, 'tool_name') and not name.startswith('_'):
                    tool_class = obj
                    break

            if not tool_class:
                result['errors'].append("No valid tool class found")
                result['valid'] = False
            else:
                # Check for required attributes
                if not hasattr(tool_class, 'tool_name'):
                    result['errors'].append("Missing 'tool_name' attribute")
                    result['valid'] = False

                if not hasattr(tool_class, 'tool_category'):
                    result['warnings'].append("Missing 'tool_category' attribute")

                # Check for _execute method
                if not hasattr(tool_class, '_execute'):
                    result['errors'].append("Missing '_execute' method")
                    result['valid'] = False

        except ImportError as e:
            result['errors'].append(f"Import error: {e}")
            result['valid'] = False

    except SyntaxError as e:
        result['errors'].append(f"Syntax error: {e}")
        result['valid'] = False
    except Exception as e:
        result['errors'].append(f"Validation error: {e}")
        result['valid'] = False

    return result


def execute(args) -> int:
    """Execute the validate command."""
    try:
        tools_dir = Path(__file__).parent.parent.parent / 'tools'
        results = []
        valid_count = 0
        invalid_count = 0

        if args.tool:
            # Validate single tool
            tool_file = None
            for category_dir in tools_dir.iterdir():
                if not category_dir.is_dir() or category_dir.name.startswith('_'):
                    continue

                potential_file = category_dir / f"{args.tool}.py"
                if potential_file.exists():
                    tool_file = potential_file
                    break

            if not tool_file:
                print(f"Tool '{args.tool}' not found", file=sys.stderr)
                return 1

            result = validate_tool_file(tool_file, args.strict)
            results.append(result)

        else:
            # Validate all tools
            print("Validating all tools...\n")

            for category_dir in sorted(tools_dir.iterdir()):
                if not category_dir.is_dir() or category_dir.name.startswith('_'):
                    continue

                for tool_file in sorted(category_dir.glob('*.py')):
                    if tool_file.name.startswith('_'):
                        continue

                    result = validate_tool_file(tool_file, args.strict)
                    results.append(result)

        # Print results
        for result in results:
            if result['valid']:
                valid_count += 1
                print(f"✓ {result['tool']}")
            else:
                invalid_count += 1
                print(f"✗ {result['tool']}")

            if result['errors']:
                for error in result['errors']:
                    print(f"  ERROR: {error}")

            if result['warnings']:
                for warning in result['warnings']:
                    print(f"  WARNING: {warning}")

            print()

        # Print summary
        print(f"{'=' * 60}")
        print(f"Validation Summary")
        print(f"{'=' * 60}")
        print(f"Total:   {len(results)}")
        print(f"Valid:   {valid_count} ✓")
        print(f"Invalid: {invalid_count} ✗")

        return 0 if invalid_count == 0 else 1

    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
