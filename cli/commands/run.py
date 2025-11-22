"""
Run command implementation

Executes a tool with provided parameters.
"""

import sys
import json
import yaml
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, Optional
from ..utils.interactive import prompt_for_params
from ..utils.validators import validate_params


def load_params_from_file(file_path: str) -> Dict[str, Any]:
    """Load parameters from a JSON or YAML file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Parameter file not found: {file_path}")

    with open(path, 'r') as f:
        if path.suffix in ['.yaml', '.yml']:
            return yaml.safe_load(f)
        else:
            return json.load(f)


def get_tool_class(tool_name: str):
    """Import and return the tool class."""
    tools_dir = Path(__file__).parent.parent.parent / 'tools'

    # Find the tool file
    tool_file = None
    category = None

    for category_dir in tools_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith('_'):
            continue

        potential_file = category_dir / f"{tool_name}.py"
        if potential_file.exists():
            tool_file = potential_file
            category = category_dir.name
            break

    if not tool_file:
        raise FileNotFoundError(f"Tool '{tool_name}' not found")

    # Import the tool module
    module_path = f"tools.{category}.{tool_name}"
    module = importlib.import_module(module_path)

    # Find the tool class
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if hasattr(obj, 'tool_name') and not name.startswith('_'):
            return obj

    raise ValueError(f"No valid tool class found in {tool_name}")


def execute(args) -> int:
    """Execute the run command."""
    try:
        tool_class = get_tool_class(args.tool)

        # Get parameters
        params = {}

        if args.interactive:
            # Interactive mode - prompt for parameters
            params = prompt_for_params(tool_class)
        elif args.params:
            # Load from file or parse JSON
            if args.params.startswith('@'):
                file_path = args.params[1:]
                params = load_params_from_file(file_path)
            else:
                params = json.loads(args.params)

        # Validate parameters
        try:
            validate_params(tool_class, params)
        except Exception as e:
            print(f"Parameter validation failed: {e}", file=sys.stderr)
            return 1

        # Run the tool
        print(f"\nRunning {args.tool}...\n")
        tool_instance = tool_class(**params)
        result = tool_instance.run()

        # Format output
        if args.format == 'json':
            output = json.dumps(result, indent=2)
        elif args.format == 'yaml':
            output = yaml.dump(result, default_flow_style=False)
        else:
            output = str(result)

        # Print or save output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output)
            print(f"Output saved to: {args.output}")
        else:
            print(output)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing parameters: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error running tool: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
