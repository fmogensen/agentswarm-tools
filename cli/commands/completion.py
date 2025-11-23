"""
Completion command implementation

Manages shell auto-completion installation and display.
"""

import sys

from rich.console import Console

from ..completion import CompletionManager

console = Console()


def execute(args) -> int:
    """
    Execute the completion command.

    Args:
        args: Command arguments with:
            - action: Completion action (install, show)
            - shell: Shell type (bash, zsh, fish)

    Returns:
        Exit code
    """
    try:
        manager = CompletionManager()

        if args.action == "install":
            return _install_completion(manager, args)
        elif args.action == "show":
            return _show_completion(manager, args)
        else:
            console.print(f"[red]Unknown action: {args.action}[/red]")
            return 1

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


def _install_completion(manager: CompletionManager, args) -> int:
    """Install shell completion."""
    shell = getattr(args, "shell", None)

    console.print("\n[bold cyan]Installing AgentSwarm CLI Auto-Completion[/bold cyan]")

    if manager.install_completion(shell):
        return 0
    else:
        return 1


def _show_completion(manager: CompletionManager, args) -> int:
    """Show completion script."""
    shell = getattr(args, "shell", None)

    if not shell:
        shell = manager.detect_shell()

    if not shell:
        console.print("[red]Could not detect shell type.[/red]")
        console.print("Please specify shell with --shell option (bash, zsh, or fish)")
        return 1

    if shell not in manager.supported_shells:
        console.print(f"[red]Unsupported shell: {shell}[/red]")
        return 1

    try:
        script = manager.get_completion_script(shell)

        console.print(f"\n[bold cyan]Completion Script for {shell}[/bold cyan]")
        console.print("=" * 60)
        console.print(script)

        return 0

    except Exception as e:
        console.print(f"[red]Error generating completion script: {e}[/red]")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage shell completion")
    parser.add_argument("action", choices=["install", "show"], help="Completion action")
    parser.add_argument(
        "--shell", choices=["bash", "zsh", "fish"], help="Shell type (auto-detect if not specified)"
    )

    args = parser.parse_args()
    sys.exit(execute(args))
