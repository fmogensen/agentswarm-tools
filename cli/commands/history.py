"""
History command implementation

Manages command history viewing, replay, and analysis.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

from ..history import CommandHistory


console = Console()


def execute(args) -> int:
    """
    Execute the history command.

    Args:
        args: Command arguments with:
            - action: History action (list, replay, clear, stats)
            - id: Entry ID (for replay)
            - limit: Number of entries to show
            - filter: Filter by command type

    Returns:
        Exit code
    """
    try:
        history = CommandHistory()

        if args.action == "list":
            return _list_history(history, args)
        elif args.action == "replay":
            return _replay_command(history, args)
        elif args.action == "clear":
            return _clear_history(history)
        elif args.action == "stats":
            return _show_statistics(history)
        else:
            console.print(f"[red]Unknown action: {args.action}[/red]")
            return 1

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


def _list_history(history: CommandHistory, args) -> int:
    """List command history."""
    limit = getattr(args, "limit", 20)
    command_filter = getattr(args, "filter", None)

    history.display_history(limit=limit, command_filter=command_filter)

    return 0


def _replay_command(history: CommandHistory, args) -> int:
    """Replay a command from history."""
    if not args.id:
        console.print("[red]Entry ID is required for 'replay' action[/red]")
        console.print("Usage: agentswarm history replay <id>")
        return 1

    try:
        entry_id = int(args.id)
    except ValueError:
        console.print("[red]Invalid entry ID. Must be a number.[/red]")
        return 1

    command_info = history.replay_command(entry_id)

    if not command_info:
        console.print(f"[red]History entry {entry_id} not found.[/red]")
        return 1

    console.print(f"\n[bold cyan]Replaying command from history entry #{entry_id}[/bold cyan]")
    console.print(f"Command: {command_info['command']}")

    if command_info.get("tool"):
        console.print(f"Tool: {command_info['tool']}")

    if command_info.get("params"):
        import json
        console.print(f"Parameters: {json.dumps(command_info['params'], indent=2)}")

    # Confirm replay
    if not Confirm.ask("\nExecute this command?"):
        console.print("[yellow]Replay cancelled.[/yellow]")
        return 0

    # Execute the command
    command = command_info["command"]

    if command == "run":
        from .run import run_tool_by_name
        tool_name = command_info["tool"]
        params = command_info.get("params", {})

        console.print(f"\n[bold]Running tool: {tool_name}[/bold]")

        try:
            result = run_tool_by_name(tool_name, params)

            if result.get("success"):
                console.print("[green]Tool executed successfully![/green]")
                console.print(f"\nResult: {result}")
                return 0
            else:
                console.print("[red]Tool execution failed.[/red]")
                return 1

        except Exception as e:
            console.print(f"[red]Error executing tool: {e}[/red]")
            return 1

    elif command == "workflow":
        from .workflow import execute as workflow_execute
        from argparse import Namespace

        workflow_args = Namespace(
            action="run",
            name=command_info["tool"],
            params=command_info.get("params"),
            output=None
        )

        return workflow_execute(workflow_args)

    else:
        console.print(f"[yellow]Replay not supported for '{command}' command.[/yellow]")
        return 1


def _clear_history(history: CommandHistory) -> int:
    """Clear command history."""
    if not Confirm.ask("Are you sure you want to clear all command history?"):
        console.print("[yellow]Clear cancelled.[/yellow]")
        return 0

    history.clear()
    console.print("[green]Command history cleared successfully.[/green]")

    return 0


def _show_statistics(history: CommandHistory) -> int:
    """Show usage statistics."""
    history.display_statistics()
    return 0


# Helper function for run.py to use
def run_tool_by_name(tool_name: str, params: dict):
    """
    Run a tool by name with parameters.

    Args:
        tool_name: Tool name
        params: Tool parameters

    Returns:
        Tool execution result
    """
    # This is a placeholder - actual implementation would load and run the tool
    # For now, we'll import from run.py if it exists
    try:
        from .run import execute as run_execute
        from argparse import Namespace
        import json

        args = Namespace(
            tool=tool_name,
            params=json.dumps(params),
            interactive=False,
            output=None,
            format="json"
        )

        run_execute(args)

        return {"success": True, "result": "Tool executed"}

    except Exception as e:
        raise Exception(f"Failed to run tool: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage command history")
    parser.add_argument(
        "action",
        choices=["list", "replay", "clear", "stats"],
        help="History action"
    )
    parser.add_argument("id", nargs="?", help="Entry ID (for replay)")
    parser.add_argument("-l", "--limit", type=int, default=20, help="Number of entries to show")
    parser.add_argument("-f", "--filter", help="Filter by command type")

    args = parser.parse_args()
    sys.exit(execute(args))
