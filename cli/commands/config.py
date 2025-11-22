"""
Config command implementation

Manages CLI configuration and API keys.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional


def get_config_path() -> Path:
    """Get the path to the config file."""
    config_dir = Path.home() / '.agentswarm'
    config_dir.mkdir(exist_ok=True)
    return config_dir / 'config.json'


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    config_path = get_config_path()

    if not config_path.exists():
        return {}

    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load config: {e}", file=sys.stderr)
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()

    try:
        with open(config_path, 'w') as f:
            json.dump(config, indent=2, fp=f)
    except Exception as e:
        raise Exception(f"Could not save config: {e}")


def show_config() -> None:
    """Display current configuration."""
    config = load_config()

    if not config:
        print("No configuration found.")
        print(f"Config file: {get_config_path()}")
        return

    print(f"\nConfiguration ({get_config_path()}):")
    print("=" * 60)

    for key, value in sorted(config.items()):
        # Mask sensitive values
        if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'token']):
            if value:
                masked = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
                print(f"{key:30} = {masked}")
            else:
                print(f"{key:30} = (not set)")
        else:
            print(f"{key:30} = {value}")

    print()


def get_config_value(key: str) -> Optional[str]:
    """Get a specific configuration value."""
    config = load_config()
    return config.get(key)


def set_config_value(key: str, value: str) -> None:
    """Set a specific configuration value."""
    config = load_config()
    config[key] = value
    save_config(config)


def reset_config() -> None:
    """Reset configuration to defaults."""
    config_path = get_config_path()
    if config_path.exists():
        config_path.unlink()
    print("Configuration reset to defaults.")


def validate_config() -> bool:
    """Validate current configuration."""
    config = load_config()

    required_keys = [
        'GENSPARK_API_KEY',
    ]

    valid = True
    for key in required_keys:
        if key not in config or not config[key]:
            print(f"✗ Missing required configuration: {key}")
            valid = False
        else:
            print(f"✓ {key} is set")

    return valid


def execute(args) -> int:
    """Execute the config command."""
    try:
        if args.show:
            show_config()
            return 0

        if args.get:
            value = get_config_value(args.get)
            if value is None:
                print(f"Configuration key '{args.get}' not found", file=sys.stderr)
                return 1
            print(value)
            return 0

        if args.set:
            if '=' not in args.set:
                print("Invalid format. Use: --set KEY=VALUE", file=sys.stderr)
                return 1

            key, value = args.set.split('=', 1)
            set_config_value(key.strip(), value.strip())
            print(f"Configuration updated: {key}")
            return 0

        if args.reset:
            reset_config()
            return 0

        if args.validate:
            valid = validate_config()
            return 0 if valid else 1

        # Default: show config
        show_config()
        return 0

    except Exception as e:
        print(f"Error managing configuration: {e}", file=sys.stderr)
        return 1
