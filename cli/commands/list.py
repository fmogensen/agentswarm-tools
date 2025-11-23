"""
List command implementation

Lists all available tools with optional filtering and formatting.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

from ..utils.formatters import format_json, format_table, format_yaml


def get_all_tools() -> Dict[str, List[Dict[str, Any]]]:
    """Discover all tools organized by category."""
    tools_dir = Path(__file__).parent.parent.parent / "tools"
    categories = {}

    if not tools_dir.exists():
        return {}

    for category_dir in sorted(tools_dir.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("_"):
            continue

        category_name = category_dir.name
        tools = []

        for tool_file in sorted(category_dir.glob("*.py")):
            if tool_file.name.startswith("_"):
                continue

            tool_name = tool_file.stem
            tools.append(
                {
                    "name": tool_name,
                    "category": category_name,
                    "path": str(tool_file),
                }
            )

        if tools:
            categories[category_name] = tools

    return categories


def execute(args) -> int:
    """Execute the list command."""
    try:
        categories = get_all_tools()

        if not categories:
            print("No tools found.", file=sys.stderr)
            return 1

        # List categories only
        if args.categories:
            if args.format == "json":
                print(json.dumps(list(categories.keys()), indent=2))
            elif args.format == "yaml":
                print(yaml.dump(list(categories.keys()), default_flow_style=False))
            else:
                print("\nAvailable Categories:")
                print("-" * 40)
                for category in sorted(categories.keys()):
                    tool_count = len(categories[category])
                    print(f"  {category:<30} ({tool_count} tools)")
            return 0

        # Filter by category if specified
        if args.category:
            if args.category not in categories:
                print(f"Category '{args.category}' not found.", file=sys.stderr)
                return 1
            categories = {args.category: categories[args.category]}

        # Prepare data for output
        all_tools = []
        for category, tools in categories.items():
            for tool in tools:
                all_tools.append(
                    {
                        "Tool": tool["name"],
                        "Category": category,
                        "Path": tool["path"],
                    }
                )

        # Output based on format
        if args.format == "json":
            print(json.dumps(all_tools, indent=2))
        elif args.format == "yaml":
            print(yaml.dump(all_tools, default_flow_style=False))
        else:
            # Table format
            headers = ["Tool", "Category"]
            rows = [[t["Tool"], t["Category"]] for t in all_tools]
            print(format_table(headers, rows))
            print(f"\nTotal: {len(all_tools)} tools")

        return 0

    except Exception as e:
        print(f"Error listing tools: {e}", file=sys.stderr)
        return 1
