"""
Parameter validation utilities

Functions for validating tool parameters.
"""

import inspect
from typing import Any, Dict, Type

from pydantic import ValidationError


def validate_params(tool_class: Type, params: Dict[str, Any]) -> None:
    """
    Validate parameters against a tool class.

    Args:
        tool_class: Tool class to validate against
        params: Parameters to validate

    Raises:
        ValidationError: If validation fails
    """
    try:
        # Try to create an instance with the params
        tool_class(**params)
    except ValidationError as e:
        raise ValidationError(f"Parameter validation failed: {e}")
    except TypeError as e:
        raise TypeError(f"Invalid parameters: {e}")


def validate_tool_structure(tool_class: Type) -> Dict[str, Any]:
    """
    Validate that a tool class follows Agency Swarm standards.

    Args:
        tool_class: Tool class to validate

    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
    }

    # Check for required attributes
    if not hasattr(tool_class, "tool_name"):
        result["errors"].append("Missing 'tool_name' attribute")
        result["valid"] = False

    if not hasattr(tool_class, "tool_category"):
        result["warnings"].append("Missing 'tool_category' attribute")

    # Check for _execute method
    if not hasattr(tool_class, "_execute"):
        result["errors"].append("Missing '_execute' method")
        result["valid"] = False
    else:
        # Validate _execute signature
        sig = inspect.signature(tool_class._execute)
        if len(sig.parameters) != 1:  # Should only have 'self'
            result["errors"].append("_execute should only accept 'self' parameter")
            result["valid"] = False

    # Check for proper inheritance
    base_classes = [c.__name__ for c in inspect.getmro(tool_class)]
    if "BaseTool" not in base_classes:
        result["errors"].append("Tool must inherit from BaseTool")
        result["valid"] = False

    # Check for Pydantic fields
    if hasattr(tool_class, "model_fields"):
        for field_name, field_info in tool_class.model_fields.items():
            if field_name in ["tool_name", "tool_category"]:
                continue

            # Check if field has description
            if not field_info.description:
                result["warnings"].append(f"Field '{field_name}' missing description")

    return result


def validate_file_path(path: str, must_exist: bool = False) -> bool:
    """
    Validate a file path.

    Args:
        path: Path to validate
        must_exist: Whether the file must exist

    Returns:
        True if valid, False otherwise
    """
    from pathlib import Path

    try:
        p = Path(path)

        if must_exist and not p.exists():
            return False

        return True
    except Exception:
        return False


def validate_json(text: str) -> bool:
    """
    Validate JSON text.

    Args:
        text: JSON text to validate

    Returns:
        True if valid, False otherwise
    """
    import json

    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


def validate_yaml(text: str) -> bool:
    """
    Validate YAML text.

    Args:
        text: YAML text to validate

    Returns:
        True if valid, False otherwise
    """
    import yaml

    try:
        yaml.safe_load(text)
        return True
    except yaml.YAMLError:
        return False
