"""
Command History Tracking for AgentSwarm CLI

Tracks all CLI commands for replay and analysis.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich import box
from rich.console import Console
from rich.table import Table

console = Console()


class CommandHistory:
    """Manage command history for AgentSwarm CLI."""

    def __init__(self):
        """Initialize command history."""
        self.history_dir = Path.home() / ".agentswarm"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "history.json"

        # Load existing history
        self.history = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load command history from file."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_history(self):
        """Save command history to file."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving history: {e}[/red]")

    def add_command(
        self,
        command: str,
        tool: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error: Optional[str] = None,
        duration: Optional[float] = None,
    ):
        """
        Add a command to history.

        Args:
            command: Command type (run, test, list, etc.)
            tool: Tool name if applicable
            params: Command parameters
            success: Whether command succeeded
            error: Error message if failed
            duration: Execution duration in seconds
        """
        entry = {
            "id": len(self.history) + 1,
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "tool": tool,
            "params": params or {},
            "success": success,
            "error": error,
            "duration": duration,
        }

        self.history.append(entry)

        # Keep only last 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        self._save_history()

    def get_history(
        self,
        limit: Optional[int] = None,
        command_filter: Optional[str] = None,
        tool_filter: Optional[str] = None,
        success_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get command history with filters.

        Args:
            limit: Maximum number of entries to return
            command_filter: Filter by command type
            tool_filter: Filter by tool name
            success_only: Only return successful commands

        Returns:
            List of history entries
        """
        filtered = self.history

        # Apply filters
        if command_filter:
            filtered = [e for e in filtered if e.get("command") == command_filter]

        if tool_filter:
            filtered = [e for e in filtered if e.get("tool") == tool_filter]

        if success_only:
            filtered = [e for e in filtered if e.get("success")]

        # Sort by timestamp (newest first)
        filtered = sorted(filtered, key=lambda x: x.get("timestamp", ""), reverse=True)

        # Apply limit
        if limit:
            filtered = filtered[:limit]

        return filtered

    def get_by_id(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get history entry by ID.

        Args:
            entry_id: Entry ID

        Returns:
            History entry or None if not found
        """
        for entry in self.history:
            if entry.get("id") == entry_id:
                return entry

        return None

    def clear(self):
        """Clear all command history."""
        self.history = []
        self._save_history()

    def replay_command(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get command details for replay.

        Args:
            entry_id: History entry ID

        Returns:
            Command details for replay
        """
        entry = self.get_by_id(entry_id)

        if not entry:
            return None

        return {
            "command": entry.get("command"),
            "tool": entry.get("tool"),
            "params": entry.get("params"),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get usage statistics from history.

        Returns:
            Statistics dictionary
        """
        if not self.history:
            return {
                "total_commands": 0,
                "success_rate": 0.0,
                "most_used_tools": [],
                "most_used_commands": [],
            }

        total = len(self.history)
        successful = sum(1 for e in self.history if e.get("success"))

        # Count tool usage
        tool_counts = {}
        for entry in self.history:
            tool = entry.get("tool")
            if tool:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1

        # Count command usage
        command_counts = {}
        for entry in self.history:
            cmd = entry.get("command")
            if cmd:
                command_counts[cmd] = command_counts.get(cmd, 0) + 1

        # Sort by usage
        most_used_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        most_used_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_commands": total,
            "successful_commands": successful,
            "failed_commands": total - successful,
            "success_rate": (successful / total * 100) if total > 0 else 0.0,
            "most_used_tools": [{"tool": t, "count": c} for t, c in most_used_tools],
            "most_used_commands": [{"command": c, "count": n} for c, n in most_used_commands],
        }

    def display_history(
        self,
        limit: int = 20,
        command_filter: Optional[str] = None,
        tool_filter: Optional[str] = None,
    ):
        """
        Display command history in a table.

        Args:
            limit: Maximum entries to display
            command_filter: Filter by command type
            tool_filter: Filter by tool name
        """
        entries = self.get_history(
            limit=limit, command_filter=command_filter, tool_filter=tool_filter
        )

        if not entries:
            console.print("[yellow]No command history found.[/yellow]")
            return

        table = Table(
            title=f"Command History (Last {len(entries)} commands)",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
        )

        table.add_column("ID", style="dim", width=6)
        table.add_column("Time", style="cyan", width=20)
        table.add_column("Command", style="yellow", width=12)
        table.add_column("Tool", style="green", width=20)
        table.add_column("Status", style="white", width=10)
        table.add_column("Duration", style="blue", width=10)

        for entry in entries:
            entry_id = str(entry.get("id", ""))
            timestamp = entry.get("timestamp", "")

            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                time_str = timestamp[:19] if timestamp else ""

            command = entry.get("command", "")
            tool = entry.get("tool", "-")
            success = entry.get("success", False)
            status = "[green]Success[/green]" if success else "[red]Failed[/red]"

            duration = entry.get("duration")
            duration_str = f"{duration:.2f}s" if duration else "-"

            table.add_row(entry_id, time_str, command, tool, status, duration_str)

        console.print(table)

    def display_statistics(self):
        """Display usage statistics."""
        stats = self.get_statistics()

        console.print("\n[bold cyan]Command History Statistics[/bold cyan]")
        console.print("=" * 60)

        console.print(f"\nTotal Commands: [bold]{stats['total_commands']}[/bold]")
        console.print(f"Successful: [green]{stats['successful_commands']}[/green]")
        console.print(f"Failed: [red]{stats['failed_commands']}[/red]")
        console.print(f"Success Rate: [cyan]{stats['success_rate']:.1f}%[/cyan]")

        if stats["most_used_commands"]:
            console.print("\n[bold]Most Used Commands:[/bold]")
            table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
            table.add_column("Command", style="cyan")
            table.add_column("Count", justify="right", style="green")

            for cmd_info in stats["most_used_commands"]:
                table.add_row(cmd_info["command"], str(cmd_info["count"]))

            console.print(table)

        if stats["most_used_tools"]:
            console.print("\n[bold]Most Used Tools:[/bold]")
            table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
            table.add_column("Tool", style="cyan")
            table.add_column("Count", justify="right", style="green")

            for tool_info in stats["most_used_tools"]:
                table.add_row(tool_info["tool"], str(tool_info["count"]))

            console.print(table)

    def export_history(self, output_file: Path, format: str = "json"):
        """
        Export history to file.

        Args:
            output_file: Output file path
            format: Export format (json, csv)
        """
        if format == "json":
            with open(output_file, "w") as f:
                json.dump(self.history, f, indent=2)
        elif format == "csv":
            import csv

            with open(output_file, "w", newline="") as f:
                if not self.history:
                    return

                fieldnames = self.history[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.history)

        console.print(f"[green]History exported to {output_file}[/green]")


def get_history_instance() -> CommandHistory:
    """Get singleton history instance."""
    if not hasattr(get_history_instance, "_instance"):
        get_history_instance._instance = CommandHistory()
    return get_history_instance._instance


if __name__ == "__main__":
    # Example usage
    history = CommandHistory()

    # Add some example commands
    history.add_command(
        command="run", tool="web_search", params={"query": "test"}, success=True, duration=1.5
    )

    history.add_command(
        command="test", tool="image_generation", params={}, success=False, error="API key not found"
    )

    # Display history
    history.display_history()

    # Display statistics
    history.display_statistics()
