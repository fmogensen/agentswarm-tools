"""
Enhanced Interactive Mode for AgentSwarm CLI

Provides a rich, menu-driven interface for tool selection and execution.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.tree import Tree

console = Console()


class InteractiveMode:
    """Interactive mode handler for AgentSwarm CLI."""

    def __init__(self):
        """Initialize interactive mode."""
        self.console = Console()
        self.recent_tools = self._load_recent_tools()

    def _load_recent_tools(self) -> List[str]:
        """Load recently used tools from history."""
        try:
            from .history import CommandHistory

            history = CommandHistory()
            commands = history.get_history(limit=10)

            # Extract tool names from run commands
            tools = []
            for cmd in commands:
                if cmd.get("command") == "run" and "tool" in cmd:
                    tool_name = cmd["tool"]
                    if tool_name not in tools:
                        tools.append(tool_name)

            return tools[:5]  # Top 5 recent tools
        except Exception:
            return []

    def run(self):
        """Run interactive mode."""
        self.console.clear()
        self._show_welcome()

        while True:
            try:
                choice = self._show_main_menu()

                if choice == "1":
                    self._browse_by_category()
                elif choice == "2":
                    self._search_tools()
                elif choice == "3":
                    self._recent_tools_menu()
                elif choice == "4":
                    self._quick_actions()
                elif choice == "5":
                    self._settings()
                elif choice == "q":
                    self.console.print("\n[bold green]Goodbye![/bold green]\n")
                    break
                else:
                    self.console.print("[red]Invalid choice. Please try again.[/red]")

            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Use 'q' to quit or Ctrl+D to exit[/yellow]")
            except EOFError:
                self.console.print("\n[bold green]Goodbye![/bold green]\n")
                break

    def _show_welcome(self):
        """Display welcome banner."""
        welcome_text = """
[bold blue]AgentSwarm Tools - Interactive Mode[/bold blue]

Welcome to the interactive tool launcher!
Navigate using number keys and follow the prompts.
        """
        panel = Panel(welcome_text, box=box.ROUNDED, border_style="blue")
        self.console.print(panel)

    def _show_main_menu(self) -> str:
        """Show main menu and get user choice."""
        self.console.print("\n[bold cyan]Main Menu[/bold cyan]")
        self.console.print("=" * 50)
        self.console.print("  1. Browse tools by category")
        self.console.print("  2. Search for tools")
        self.console.print("  3. Recent tools")
        self.console.print("  4. Quick actions")
        self.console.print("  5. Settings")
        self.console.print("  q. Quit")
        self.console.print("=" * 50)

        return Prompt.ask("\nSelect an option", default="1")

    def _browse_by_category(self):
        """Browse tools by category."""
        from .commands.list import get_all_tools

        categories = get_all_tools()

        if not categories:
            self.console.print("[red]No tools found.[/red]")
            return

        # Show categories
        self.console.print("\n[bold cyan]Tool Categories[/bold cyan]")

        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("#", style="dim", width=6)
        table.add_column("Category", style="cyan")
        table.add_column("Tools", justify="right", style="green")
        table.add_column("Description", style="white")

        category_list = sorted(categories.keys())
        category_descriptions = {
            "data": "Search and information retrieval",
            "communication": "Email, calendar, and messaging",
            "media": "Image, video, and audio generation/analysis",
            "visualization": "Charts, diagrams, and graphs",
            "content": "Documents and web content",
            "infrastructure": "Code execution and storage",
            "utils": "Utility tools and helpers",
            "integrations": "External service connectors",
        }

        for i, category in enumerate(category_list, 1):
            tool_count = len(categories[category])
            desc = category_descriptions.get(category, "")
            table.add_row(str(i), category, str(tool_count), desc)

        self.console.print(table)

        # Get category selection
        choice = Prompt.ask("\nSelect category (number or 'b' to go back)", default="b")

        if choice.lower() == "b":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(category_list):
                selected_category = category_list[idx]
                self._show_category_tools(selected_category, categories[selected_category])
        except ValueError:
            self.console.print("[red]Invalid selection.[/red]")

    def _show_category_tools(self, category: str, tools: List[Dict[str, Any]]):
        """Show tools in a category."""
        self.console.print(f"\n[bold cyan]Tools in '{category}' category[/bold cyan]")

        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("#", style="dim", width=6)
        table.add_column("Tool Name", style="cyan")
        table.add_column("Status", style="green")

        for i, tool in enumerate(tools, 1):
            table.add_row(str(i), tool["name"], "Ready")

        self.console.print(table)

        # Get tool selection
        choice = Prompt.ask("\nSelect tool to run (number or 'b' to go back)", default="b")

        if choice.lower() == "b":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(tools):
                selected_tool = tools[idx]
                self._run_tool_interactive(selected_tool["name"])
        except ValueError:
            self.console.print("[red]Invalid selection.[/red]")

    def _search_tools(self):
        """Search for tools by name or description."""
        from .commands.list import get_all_tools

        search_query = Prompt.ask("\n[cyan]Enter search term[/cyan]")

        if not search_query:
            return

        categories = get_all_tools()
        all_tools = []

        for category, tools in categories.items():
            for tool in tools:
                tool["category"] = category
                all_tools.append(tool)

        # Search in tool names
        results = [tool for tool in all_tools if search_query.lower() in tool["name"].lower()]

        if not results:
            self.console.print(f"[yellow]No tools found matching '{search_query}'[/yellow]")
            return

        # Display results
        self.console.print(f"\n[bold green]Found {len(results)} tool(s)[/bold green]")

        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("#", style="dim", width=6)
        table.add_column("Tool Name", style="cyan")
        table.add_column("Category", style="yellow")

        for i, tool in enumerate(results, 1):
            table.add_row(str(i), tool["name"], tool["category"])

        self.console.print(table)

        # Get selection
        choice = Prompt.ask("\nSelect tool to run (number or 'b' to go back)", default="b")

        if choice.lower() == "b":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                selected_tool = results[idx]
                self._run_tool_interactive(selected_tool["name"])
        except ValueError:
            self.console.print("[red]Invalid selection.[/red]")

    def _recent_tools_menu(self):
        """Show recently used tools."""
        if not self.recent_tools:
            self.console.print("[yellow]No recent tools found.[/yellow]")
            return

        self.console.print("\n[bold cyan]Recently Used Tools[/bold cyan]")

        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("#", style="dim", width=6)
        table.add_column("Tool Name", style="cyan")

        for i, tool in enumerate(self.recent_tools, 1):
            table.add_row(str(i), tool)

        self.console.print(table)

        choice = Prompt.ask("\nSelect tool to run (number or 'b' to go back)", default="b")

        if choice.lower() == "b":
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(self.recent_tools):
                tool_name = self.recent_tools[idx]
                self._run_tool_interactive(tool_name)
        except ValueError:
            self.console.print("[red]Invalid selection.[/red]")

    def _quick_actions(self):
        """Quick actions menu."""
        self.console.print("\n[bold cyan]Quick Actions[/bold cyan]")
        self.console.print("=" * 50)
        self.console.print("  1. List all tools")
        self.console.print("  2. Show command history")
        self.console.print("  3. List workflows")
        self.console.print("  4. Validate configuration")
        self.console.print("  b. Back to main menu")
        self.console.print("=" * 50)

        choice = Prompt.ask("\nSelect action", default="b")

        if choice == "1":
            from argparse import Namespace

            from .commands.list import execute as list_execute

            args = Namespace(category=None, format="table", categories=False)
            list_execute(args)
        elif choice == "2":
            from argparse import Namespace

            from .commands.history import execute as history_execute

            args = Namespace(action="list", limit=20, filter=None, id=None)
            history_execute(args)
        elif choice == "3":
            from argparse import Namespace

            from .commands.workflow import execute as workflow_execute

            args = Namespace(action="list", name=None, params=None, output=None)
            workflow_execute(args)
        elif choice == "4":
            from argparse import Namespace

            from .commands.config import execute as config_execute

            args = Namespace(show=False, set=None, get=None, reset=False, validate=True)
            config_execute(args)

    def _settings(self):
        """Settings menu."""
        self.console.print("\n[bold cyan]Settings[/bold cyan]")
        self.console.print("=" * 50)
        self.console.print("  1. Show configuration")
        self.console.print("  2. Set API key")
        self.console.print("  3. Clear history")
        self.console.print("  4. Install shell completion")
        self.console.print("  b. Back to main menu")
        self.console.print("=" * 50)

        choice = Prompt.ask("\nSelect option", default="b")

        if choice == "1":
            from argparse import Namespace

            from .commands.config import execute as config_execute

            args = Namespace(show=True, set=None, get=None, reset=False, validate=False)
            config_execute(args)
        elif choice == "2":
            key_name = Prompt.ask("Enter API key name (e.g., GENSPARK_API_KEY)")
            key_value = Prompt.ask("Enter API key value", password=True)

            from argparse import Namespace

            from .commands.config import execute as config_execute

            args = Namespace(
                show=False, set=f"{key_name}={key_value}", get=None, reset=False, validate=False
            )
            config_execute(args)
        elif choice == "3":
            if Confirm.ask("Are you sure you want to clear command history?"):
                from .history import CommandHistory

                history = CommandHistory()
                history.clear()
                self.console.print("[green]History cleared successfully.[/green]")
        elif choice == "4":
            from argparse import Namespace

            from .commands.completion import execute as completion_execute

            args = Namespace(action="install", shell=None)
            completion_execute(args)

    def _run_tool_interactive(self, tool_name: str):
        """Run a tool interactively."""
        self.console.print(f"\n[bold cyan]Running tool: {tool_name}[/bold cyan]")

        from argparse import Namespace

        from .commands.run import execute as run_execute

        args = Namespace(tool=tool_name, params=None, interactive=True, output=None, format="json")

        try:
            run_execute(args)

            # Update recent tools
            if tool_name not in self.recent_tools:
                self.recent_tools.insert(0, tool_name)
                self.recent_tools = self.recent_tools[:5]

        except Exception as e:
            self.console.print(f"[red]Error running tool: {e}[/red]")

        # Pause before returning to menu
        Prompt.ask("\nPress Enter to continue")


def launch_interactive_mode():
    """Launch interactive mode."""
    mode = InteractiveMode()
    mode.run()


if __name__ == "__main__":
    launch_interactive_mode()
