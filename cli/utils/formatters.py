"""
Output formatting utilities

Functions for formatting CLI output in various formats.
"""

import json
import yaml
from typing import List, Any, Dict


def format_table(headers: List[str], rows: List[List[Any]], max_width: int = 100) -> str:
    """
    Format data as a table.

    Args:
        headers: Column headers
        rows: Data rows
        max_width: Maximum column width

    Returns:
        Formatted table string
    """
    if not rows:
        return "No data to display"

    # Calculate column widths
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            cell_str = str(cell)
            col_widths[i] = min(max(col_widths[i], len(cell_str)), max_width)

    # Create format string
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)

    # Build table
    lines = []

    # Header
    lines.append(fmt.format(*headers))
    lines.append("-" * (sum(col_widths) + 2 * (len(headers) - 1)))

    # Rows
    for row in rows:
        # Truncate long cells
        truncated = []
        for i, cell in enumerate(row):
            cell_str = str(cell)
            if len(cell_str) > col_widths[i]:
                truncated.append(cell_str[:col_widths[i] - 3] + "...")
            else:
                truncated.append(cell_str)
        lines.append(fmt.format(*truncated))

    return "\n".join(lines)


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as JSON.

    Args:
        data: Data to format
        indent: Indentation level

    Returns:
        JSON string
    """
    return json.dumps(data, indent=indent, default=str)


def format_yaml(data: Any) -> str:
    """
    Format data as YAML.

    Args:
        data: Data to format

    Returns:
        YAML string
    """
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def format_list(items: List[str], indent: int = 2) -> str:
    """
    Format a list of items.

    Args:
        items: Items to format
        indent: Indentation level

    Returns:
        Formatted list string
    """
    prefix = " " * indent
    return "\n".join(f"{prefix}- {item}" for item in items)


def format_key_value(data: Dict[str, Any], indent: int = 2) -> str:
    """
    Format key-value pairs.

    Args:
        data: Dictionary to format
        indent: Indentation level

    Returns:
        Formatted string
    """
    prefix = " " * indent
    max_key_len = max(len(str(k)) for k in data.keys()) if data else 0

    lines = []
    for key, value in data.items():
        key_str = str(key).ljust(max_key_len)
        lines.append(f"{prefix}{key_str}: {value}")

    return "\n".join(lines)


def truncate_text(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_error(error: str, prefix: str = "Error") -> str:
    """
    Format an error message.

    Args:
        error: Error message
        prefix: Prefix for the error

    Returns:
        Formatted error string
    """
    return f"\n{prefix}: {error}\n"


def format_success(message: str) -> str:
    """
    Format a success message.

    Args:
        message: Success message

    Returns:
        Formatted success string
    """
    return f"✓ {message}"


def format_warning(message: str) -> str:
    """
    Format a warning message.

    Args:
        message: Warning message

    Returns:
        Formatted warning string
    """
    return f"⚠ {message}"
