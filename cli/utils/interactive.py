"""
Interactive mode utilities

Functions for interactive parameter prompting.
"""

import sys
from typing import Dict, Any, Type, get_type_hints, get_origin, get_args


def prompt_for_params(tool_class: Type) -> Dict[str, Any]:
    """
    Interactively prompt for tool parameters.

    Args:
        tool_class: Tool class to get parameters for

    Returns:
        Dictionary of parameters
    """
    params = {}

    print(f"\nEnter parameters for {tool_class.__name__}:")
    print("=" * 60)

    if not hasattr(tool_class, 'model_fields'):
        return params

    for field_name, field_info in tool_class.model_fields.items():
        # Skip tool metadata fields
        if field_name in ['tool_name', 'tool_category']:
            continue

        # Get field information
        field_type = field_info.annotation
        is_required = field_info.is_required()
        description = field_info.description or ""
        default = field_info.default if hasattr(field_info, 'default') else None

        # Build prompt
        prompt_parts = [f"\n{field_name}"]

        if description:
            prompt_parts.append(f"  ({description})")

        # Add type hint
        type_str = str(field_type).replace('typing.', '')
        prompt_parts.append(f"  Type: {type_str}")

        if is_required:
            prompt_parts.append("  [Required]")
        else:
            prompt_parts.append(f"  [Optional, default: {default}]")

        prompt_parts.append("\n  > ")

        # Show prompt
        print("\n".join(prompt_parts), end='')

        # Get input
        value = input().strip()

        # Handle empty input
        if not value:
            if is_required:
                print("  Error: This field is required!")
                sys.exit(1)
            continue

        # Convert value based on type
        try:
            converted_value = convert_input_value(value, field_type)
            params[field_name] = converted_value
        except ValueError as e:
            print(f"  Error: Invalid value - {e}")
            sys.exit(1)

    return params


def convert_input_value(value: str, field_type: Type) -> Any:
    """
    Convert string input to appropriate type.

    Args:
        value: String value to convert
        field_type: Target type

    Returns:
        Converted value
    """
    # Handle optional types
    origin = get_origin(field_type)

    if origin is None:
        # Simple type
        if field_type == str:
            return value
        elif field_type == int:
            return int(value)
        elif field_type == float:
            return float(value)
        elif field_type == bool:
            return value.lower() in ('true', 'yes', '1', 't', 'y')
        else:
            # Try to parse as JSON for complex types
            import json
            return json.loads(value)
    else:
        # Complex type (Optional, List, Dict, etc.)
        import json
        return json.loads(value)


def confirm(prompt: str, default: bool = False) -> bool:
    """
    Ask for user confirmation.

    Args:
        prompt: Confirmation prompt
        default: Default value if user just presses Enter

    Returns:
        True if confirmed, False otherwise
    """
    suffix = " [Y/n]" if default else " [y/N]"
    response = input(f"{prompt}{suffix}: ").strip().lower()

    if not response:
        return default

    return response in ('y', 'yes')


def select_from_list(items: list, prompt: str = "Select an option") -> Any:
    """
    Let user select from a list of items.

    Args:
        items: List of items to choose from
        prompt: Selection prompt

    Returns:
        Selected item
    """
    print(f"\n{prompt}:")

    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")

    while True:
        try:
            choice = input("\nEnter number: ").strip()
            index = int(choice) - 1

            if 0 <= index < len(items):
                return items[index]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nSelection cancelled.")
            sys.exit(130)


def get_multiline_input(prompt: str = "Enter text (Ctrl+D to finish)") -> str:
    """
    Get multiline input from user.

    Args:
        prompt: Input prompt

    Returns:
        Multiline text
    """
    print(f"{prompt}:")
    lines = []

    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    return "\n".join(lines)
