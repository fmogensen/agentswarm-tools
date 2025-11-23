#!/usr/bin/env python3
"""
Audit script to check which tools have README.md files
"""
import os
from pathlib import Path
import json

def find_tool_files(base_path):
    """Find all tool Python files"""
    tools_dir = Path(base_path) / "tools"
    tool_files = []

    for py_file in tools_dir.rglob("*.py"):
        # Skip __init__.py, test files, and utility files
        if (py_file.name.startswith("__") or
            py_file.name.startswith("test_") or
            "renderers" in str(py_file) or
            "_create_compatibility_wrappers" in str(py_file)):
            continue
        tool_files.append(py_file)

    return tool_files

def get_tool_directory(tool_file):
    """Get the directory containing the tool"""
    return tool_file.parent

def check_readme_exists(tool_dir):
    """Check if README.md exists in tool directory"""
    readme_path = tool_dir / "README.md"
    return readme_path.exists(), readme_path

def categorize_tools(tool_files):
    """Categorize tools by their parent directory"""
    categories = {}
    for tool_file in tool_files:
        # Get category (e.g., 'visualization', 'media', etc.)
        parts = tool_file.parts
        tools_index = parts.index('tools')
        if tools_index + 1 < len(parts):
            category = parts[tools_index + 1]
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_file)

    return categories

def main():
    base_path = "/Users/frank/Documents/Code/Genspark/agentswarm-tools"

    # Find all tool files
    tool_files = find_tool_files(base_path)

    # Categorize tools
    categories = categorize_tools(tool_files)

    # Check for READMEs
    tools_with_readme = []
    tools_without_readme = []

    for tool_file in tool_files:
        tool_dir = get_tool_directory(tool_file)
        has_readme, readme_path = check_readme_exists(tool_dir)

        tool_info = {
            'file': str(tool_file),
            'dir': str(tool_dir),
            'name': tool_file.stem,
            'readme_path': str(readme_path),
            'category': tool_file.parts[tool_file.parts.index('tools') + 1] if 'tools' in tool_file.parts else 'unknown'
        }

        if has_readme:
            tools_with_readme.append(tool_info)
        else:
            tools_without_readme.append(tool_info)

    # Print report
    print("=" * 80)
    print("TOOL README AUDIT REPORT")
    print("=" * 80)
    print()
    print(f"Total tool files found: {len(tool_files)}")
    print(f"Tools with README.md: {len(tools_with_readme)}")
    print(f"Tools missing README.md: {len(tools_without_readme)}")
    print()

    # Group by category
    print("=" * 80)
    print("BREAKDOWN BY CATEGORY")
    print("=" * 80)
    print()

    for category in sorted(categories.keys()):
        cat_tools = categories[category]
        cat_with_readme = [t for t in tools_with_readme if t['category'] == category]
        cat_without_readme = [t for t in tools_without_readme if t['category'] == category]

        print(f"{category.upper()}")
        print(f"  Total: {len(cat_tools)}")
        print(f"  With README: {len(cat_with_readme)}")
        print(f"  Missing README: {len(cat_without_readme)}")
        print()

    # List tools missing READMEs
    if tools_without_readme:
        print("=" * 80)
        print("TOOLS MISSING README.md")
        print("=" * 80)
        print()

        current_category = None
        for tool in sorted(tools_without_readme, key=lambda x: (x['category'], x['name'])):
            if current_category != tool['category']:
                current_category = tool['category']
                print(f"\n{current_category.upper()}:")
            print(f"  - {tool['name']}")
            print(f"    Path: {tool['dir']}")

    # Save detailed report
    report = {
        'summary': {
            'total_tools': len(tool_files),
            'with_readme': len(tools_with_readme),
            'without_readme': len(tools_without_readme)
        },
        'tools_with_readme': tools_with_readme,
        'tools_without_readme': tools_without_readme
    }

    report_path = Path(base_path) / "tool_readme_audit.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print()
    print("=" * 80)
    print(f"Detailed report saved to: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
