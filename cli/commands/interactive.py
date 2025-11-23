"""
Interactive command implementation

Launches the enhanced interactive mode.
"""

import sys

from ..interactive import launch_interactive_mode


def execute(args) -> int:
    """
    Execute the interactive command.

    Args:
        args: Command arguments

    Returns:
        Exit code
    """
    try:
        launch_interactive_mode()
        return 0
    except Exception as e:
        print(f"Error in interactive mode: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Launch interactive mode")
    args = parser.parse_args()

    sys.exit(execute(args))
