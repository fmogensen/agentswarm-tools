"""
API key management

Functions for managing API keys and credentials.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


def get_config_path() -> Path:
    """Get the path to the config file."""
    config_dir = Path.home() / ".agentswarm"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def load_config() -> Dict[str, str]:
    """Load configuration from file."""
    config_path = get_config_path()

    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config: Dict[str, str]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()

    with open(config_path, "w") as f:
        json.dump(config, indent=2, fp=f)


def get_api_key(key_name: str) -> Optional[str]:
    """
    Get an API key from environment or config file.

    Args:
        key_name: Name of the API key

    Returns:
        API key value or None if not found
    """
    # First check environment variable
    env_value = os.getenv(key_name)
    if env_value:
        return env_value

    # Then check config file
    config = load_config()
    return config.get(key_name)


def set_api_key(key_name: str, value: str) -> None:
    """
    Set an API key in the config file.

    Args:
        key_name: Name of the API key
        value: API key value
    """
    config = load_config()
    config[key_name] = value
    save_config(config)


def validate_api_keys() -> Dict[str, bool]:
    """
    Validate all required API keys are set.

    Returns:
        Dictionary mapping key names to whether they are set
    """
    from .defaults import OPTIONAL_API_KEYS, REQUIRED_API_KEYS

    results = {}

    # Check required keys
    for key_name in REQUIRED_API_KEYS:
        value = get_api_key(key_name)
        results[key_name] = bool(value)

    # Check optional keys
    for key_name in OPTIONAL_API_KEYS:
        value = get_api_key(key_name)
        results[f"{key_name} (optional)"] = bool(value)

    return results


def list_api_keys() -> List[str]:
    """
    List all configured API keys.

    Returns:
        List of API key names
    """
    config = load_config()
    env_keys = [k for k in os.environ.keys() if k.endswith("_API_KEY")]

    all_keys = set(list(config.keys()) + env_keys)
    return sorted(all_keys)


def remove_api_key(key_name: str) -> bool:
    """
    Remove an API key from the config file.

    Args:
        key_name: Name of the API key to remove

    Returns:
        True if removed, False if not found
    """
    config = load_config()

    if key_name in config:
        del config[key_name]
        save_config(config)
        return True

    return False
