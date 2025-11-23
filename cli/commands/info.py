"""
Info command implementation

Shows detailed information about a specific tool.
"""

import importlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict

import yaml

from ..utils.formatters import format_json, format_yaml


def get_tool_info(tool_name: str) -> Dict[str, Any]:
    """Get detailed information about a tool."""
    tools_dir = Path(__file__).parent.parent.parent / "tools"

    # Find the tool file
    tool_file = None
    category = None

    for category_dir in tools_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("_"):
            continue

        potential_file = category_dir / f"{tool_name}.py"
        if potential_file.exists():
            tool_file = potential_file
            category = category_dir.name
            break

    if not tool_file:
        raise FileNotFoundError(f"Tool '{tool_name}' not found")

    # Import the tool module
    try:
        module_path = f"tools.{category}.{tool_name}"
        module = importlib.import_module(module_path)

        # Find the tool class (should be a subclass of BaseTool)
        tool_class = None
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, "tool_name") and not name.startswith("_"):
                tool_class = obj
                break

        if not tool_class:
            raise ValueError(f"No valid tool class found in {tool_name}")

        # Extract information
        info = {
            "name": tool_name,
            "category": category,
            "class_name": tool_class.__name__,
            "description": inspect.getdoc(tool_class) or "No description available",
            "path": str(tool_file),
            "fields": {},
        }

        # Get field information from Pydantic model
        if hasattr(tool_class, "model_fields"):
            for field_name, field_info in tool_class.model_fields.items():
                if field_name in ["tool_name", "tool_category"]:
                    continue
                info["fields"][field_name] = {
                    "type": str(field_info.annotation),
                    "required": field_info.is_required(),
                    "description": field_info.description or "",
                }

        return info

    except ImportError as e:
        raise ImportError(f"Failed to import tool '{tool_name}': {e}")


def execute(args) -> int:
    """Execute the info command."""
    try:
        info = get_tool_info(args.tool)

        if args.format == "json":
            print(json.dumps(info, indent=2))
        elif args.format == "yaml":
            print(yaml.dump(info, default_flow_style=False))
        else:
            # Text format
            print(f"\n{'=' * 60}")
            print(f"Tool: {info['name']}")
            print(f"{'=' * 60}")
            print(f"Category:    {info['category']}")
            print(f"Class:       {info['class_name']}")
            print(f"Path:        {info['path']}")
            print(f"\nDescription:\n{info['description']}\n")

            if info["fields"]:
                print("Parameters:")
                print("-" * 60)
                for field_name, field_data in info["fields"].items():
                    required = "Required" if field_data["required"] else "Optional"
                    print(f"  {field_name}")
                    print(f"    Type:        {field_data['type']}")
                    print(f"    Required:    {required}")
                    if field_data["description"]:
                        print(f"    Description: {field_data['description']}")
                    print()

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error getting tool info: {e}", file=sys.stderr)
        return 1
