#!/usr/bin/env python3
"""
AgentSwarm Tools CLI

Main entry point for the command-line interface.
"""

import sys
import argparse
from typing import Optional
from .version import __version__
from .commands import list_tools, run_tool, test_tool, validate_tool, config_tool, info_tool


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="agentswarm",
        description="AgentSwarm Tools CLI - Manage and run AgentSwarm tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentswarm list                          # List all available tools
  agentswarm list --category search        # List tools in search category
  agentswarm info web_search               # Show detailed info about a tool
  agentswarm run web_search                # Run a tool interactively
  agentswarm test web_search               # Test a tool with mock data
  agentswarm validate                      # Validate all tools
  agentswarm config --show                 # Show current configuration
  agentswarm config --set GENSPARK_API_KEY=your_key  # Set API key

For more information, visit: https://github.com/agency-ai-solutions/agentswarm-tools
        """,
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List available tools")
    list_parser.add_argument("-c", "--category", help="Filter by category")
    list_parser.add_argument(
        "-f", "--format", choices=["table", "json", "yaml"], default="table", help="Output format"
    )
    list_parser.add_argument("--categories", action="store_true", help="List all categories")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show tool information")
    info_parser.add_argument("tool", help="Tool name")
    info_parser.add_argument(
        "-f", "--format", choices=["text", "json", "yaml"], default="text", help="Output format"
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a tool")
    run_parser.add_argument("tool", help="Tool name")
    run_parser.add_argument("-p", "--params", help="Parameters as JSON string or @file.json")
    run_parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive mode with prompts"
    )
    run_parser.add_argument("-o", "--output", help="Save output to file")
    run_parser.add_argument(
        "-f", "--format", choices=["json", "yaml", "text"], default="json", help="Output format"
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Test a tool")
    test_parser.add_argument("tool", nargs="?", help="Tool name (optional, tests all if omitted)")
    test_parser.add_argument(
        "-m", "--mock", action="store_true", default=True, help="Use mock mode (default: True)"
    )
    test_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate tools")
    validate_parser.add_argument(
        "tool", nargs="?", help="Tool name (optional, validates all if omitted)"
    )
    validate_parser.add_argument("--strict", action="store_true", help="Strict validation mode")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")
    config_parser.add_argument("--set", metavar="KEY=VALUE", help="Set configuration value")
    config_parser.add_argument("--get", metavar="KEY", help="Get configuration value")
    config_parser.add_argument(
        "--reset", action="store_true", help="Reset to default configuration"
    )
    config_parser.add_argument("--validate", action="store_true", help="Validate configuration")

    return parser


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "list":
            return list_tools.execute(args)
        elif args.command == "info":
            return info_tool.execute(args)
        elif args.command == "run":
            return run_tool.execute(args)
        elif args.command == "test":
            return test_tool.execute(args)
        elif args.command == "validate":
            return validate_tool.execute(args)
        elif args.command == "config":
            return config_tool.execute(args)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
