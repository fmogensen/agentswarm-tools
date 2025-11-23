#!/usr/bin/env python3
"""
AgentSwarm Tools CLI

Main entry point for the command-line interface.
"""

import argparse
import sys
from typing import Optional

from .commands import (
    completion_tool,
    config_tool,
    history_tool,
    info_tool,
    interactive_tool,
    list_tools,
)
from .commands import performance as performance_cmd
from .commands import (
    run_tool,
    test_tool,
    validate_tool,
    workflow_tool,
)
from .version import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="agentswarm",
        description="AgentSwarm Tools CLI - Manage and run AgentSwarm tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentswarm interactive                   # Launch interactive mode
  agentswarm list                          # List all available tools
  agentswarm list --category search        # List tools in search category
  agentswarm info web_search               # Show detailed info about a tool
  agentswarm run web_search                # Run a tool interactively
  agentswarm test web_search               # Test a tool with mock data
  agentswarm workflow create               # Create new workflow
  agentswarm workflow run research         # Run workflow named 'research'
  agentswarm history list                  # Show command history
  agentswarm history replay 42             # Replay command #42
  agentswarm completion install            # Install shell auto-completion
  agentswarm config --show                 # Show current configuration
  agentswarm performance                   # Show performance overview

For more information, visit: https://github.com/agency-ai-solutions/agentswarm-tools
        """,
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Interactive command
    interactive_parser = subparsers.add_parser(
        "interactive", help="Launch interactive mode with menu-driven interface"
    )

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

    # Workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Manage workflows")
    workflow_parser.add_argument(
        "action", choices=["create", "run", "list", "delete"], help="Workflow action"
    )
    workflow_parser.add_argument("name", nargs="?", help="Workflow name")
    workflow_parser.add_argument("-p", "--params", help="Input parameters as JSON or @file.json")
    workflow_parser.add_argument("-o", "--output", help="Output file for results")

    # History command
    history_parser = subparsers.add_parser("history", help="View and manage command history")
    history_parser.add_argument(
        "action", choices=["list", "replay", "clear", "stats"], help="History action"
    )
    history_parser.add_argument("id", nargs="?", help="Entry ID (for replay)")
    history_parser.add_argument(
        "-l", "--limit", type=int, default=20, help="Number of entries to show"
    )
    history_parser.add_argument("-f", "--filter", help="Filter by command type")

    # Completion command
    completion_parser = subparsers.add_parser("completion", help="Manage shell auto-completion")
    completion_parser.add_argument("action", choices=["install", "show"], help="Completion action")
    completion_parser.add_argument(
        "--shell", choices=["bash", "zsh", "fish"], help="Shell type (auto-detect if not specified)"
    )

    # Performance command
    perf_parser = subparsers.add_parser("performance", help="Show performance metrics and reports")
    perf_subparsers = perf_parser.add_subparsers(dest="subcommand", help="Performance subcommands")

    # performance report
    report_parser = perf_subparsers.add_parser("report", help="Show detailed performance report")
    report_parser.add_argument(
        "-d", "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )

    # performance slowest
    slowest_parser = perf_subparsers.add_parser("slowest", help="Show slowest tools")
    slowest_parser.add_argument(
        "-d", "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )
    slowest_parser.add_argument(
        "-n", "--limit", type=int, default=10, help="Number of tools to show (default: 10)"
    )

    # performance most-used
    most_used_parser = perf_subparsers.add_parser("most-used", help="Show most used tools")
    most_used_parser.add_argument(
        "-d", "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )
    most_used_parser.add_argument(
        "-n", "--limit", type=int, default=10, help="Number of tools to show (default: 10)"
    )

    # performance tool
    tool_parser = perf_subparsers.add_parser("tool", help="Show metrics for a specific tool")
    tool_parser.add_argument("tool", help="Tool name")
    tool_parser.add_argument(
        "-d", "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )

    # performance alerts
    alerts_parser = perf_subparsers.add_parser("alerts", help="Show performance alerts")
    alerts_parser.add_argument(
        "-d", "--days", type=int, default=1, help="Number of days to analyze (default: 1)"
    )

    # performance export
    export_parser = perf_subparsers.add_parser("export", help="Export metrics to file")
    export_parser.add_argument(
        "-d", "--days", type=int, default=7, help="Number of days to export (default: 7)"
    )
    export_parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv", "prometheus"],
        default="json",
        help="Export format (default: json)",
    )
    export_parser.add_argument("-o", "--output", help="Output file path")

    # performance dashboard
    dashboard_parser = perf_subparsers.add_parser("dashboard", help="Generate HTML dashboard")
    dashboard_parser.add_argument(
        "-d", "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )
    dashboard_parser.add_argument(
        "-o",
        "--output",
        default="dashboard.html",
        help="Output file path (default: dashboard.html)",
    )

    # Default args for performance (show overview)
    perf_parser.add_argument(
        "-d", "--days", type=int, default=7, help="Number of days to analyze (default: 7)"
    )

    return parser


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "interactive":
            return interactive_tool.execute(args)
        elif args.command == "list":
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
        elif args.command == "workflow":
            return workflow_tool.execute(args)
        elif args.command == "history":
            return history_tool.execute(args)
        elif args.command == "completion":
            return completion_tool.execute(args)
        elif args.command == "performance":
            return performance_cmd.execute(args)
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
