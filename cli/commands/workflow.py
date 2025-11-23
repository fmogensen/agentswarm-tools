"""
Workflow command implementation

Manages workflow creation, execution, and management.
"""

import json
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Confirm

from ..workflow import WorkflowManager

console = Console()


def execute(args) -> int:
    """
    Execute the workflow command.

    Args:
        args: Command arguments with:
            - action: Workflow action (create, run, list, delete)
            - name: Workflow name (for run/delete)
            - params: Input parameters as JSON (for run)
            - output: Output file (for run)

    Returns:
        Exit code
    """
    try:
        manager = WorkflowManager()

        if args.action == "create":
            return _create_workflow(manager, args)
        elif args.action == "run":
            return _run_workflow(manager, args)
        elif args.action == "list":
            return _list_workflows(manager)
        elif args.action == "delete":
            return _delete_workflow(manager, args)
        else:
            console.print(f"[red]Unknown action: {args.action}[/red]")
            return 1

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


def _create_workflow(manager: WorkflowManager, args) -> int:
    """Create a new workflow."""
    workflow = manager.create_workflow(interactive=True)

    console.print(f"\n[green]Workflow '{workflow['name']}' created successfully![/green]")

    # Display workflow
    manager.display_workflow(workflow)

    return 0


def _run_workflow(manager: WorkflowManager, args) -> int:
    """Run a workflow."""
    if not args.name:
        console.print("[red]Workflow name is required for 'run' action[/red]")
        console.print("Usage: agentswarm workflow run <name> [--params '{...}']")
        return 1

    # Parse input parameters
    input_vars = {}
    if args.params:
        try:
            if args.params.startswith("@"):
                # Load from file
                params_file = Path(args.params[1:])
                with open(params_file, "r") as f:
                    input_vars = json.load(f)
            else:
                # Parse JSON string
                input_vars = json.loads(args.params)
        except Exception as e:
            console.print(f"[red]Error parsing parameters: {e}[/red]")
            return 1

    # Load workflow to check for required variables
    workflow = manager.load_workflow(args.name)
    if not workflow:
        console.print(f"[red]Workflow '{args.name}' not found[/red]")
        return 1

    # Check for missing required variables
    required_vars = {
        name: info
        for name, info in workflow.get("variables", {}).items()
        if info.get("required", False)
    }

    missing_vars = [name for name in required_vars if name not in input_vars]

    if missing_vars:
        console.print("[yellow]Missing required input variables:[/yellow]")
        for var_name in missing_vars:
            var_info = required_vars[var_name]
            var_type = var_info.get("type", "string")
            var_desc = var_info.get("description", "")

            from rich.prompt import Prompt

            value = Prompt.ask(f"{var_name} ({var_type}): {var_desc}")

            # Simple type conversion
            if var_type == "int":
                input_vars[var_name] = int(value)
            elif var_type == "float":
                input_vars[var_name] = float(value)
            elif var_type == "bool":
                input_vars[var_name] = value.lower() in ("true", "yes", "1")
            else:
                input_vars[var_name] = value

    # Run workflow
    results = manager.run_workflow(args.name, input_vars)

    # Display results
    console.print("\n" + "=" * 60)
    if results["success"]:
        console.print("[bold green]Workflow completed successfully![/bold green]")
    else:
        console.print("[bold red]Workflow failed![/bold red]")

    console.print(f"\nSteps completed: {len(results['steps'])}")

    if results.get("errors"):
        console.print("\n[bold red]Errors:[/bold red]")
        for error in results["errors"]:
            console.print(f"  - {error}")

    # Save results if output file specified
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"\n[green]Results saved to {output_path}[/green]")

    return 0 if results["success"] else 1


def _list_workflows(manager: WorkflowManager) -> int:
    """List all workflows."""
    workflows = manager.list_workflows()

    if not workflows:
        console.print("[yellow]No workflows found.[/yellow]")
        console.print("\nCreate a workflow with: agentswarm workflow create")
        return 0

    from rich import box
    from rich.table import Table

    table = Table(
        title=f"Workflows ({len(workflows)} total)",
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
    )

    table.add_column("Name", style="cyan", width=25)
    table.add_column("Description", style="white", width=40)
    table.add_column("Steps", justify="center", style="green", width=8)
    table.add_column("Created", style="dim", width=20)

    for workflow in workflows:
        name = workflow["name"]
        description = workflow.get("description", "")
        if len(description) > 40:
            description = description[:37] + "..."

        steps = str(workflow.get("steps", 0))

        created = workflow.get("created_at", "")
        # Format timestamp
        try:
            from datetime import datetime

            dt = datetime.fromisoformat(created)
            created = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            created = created[:16] if created else ""

        table.add_row(name, description, steps, created)

    console.print(table)

    console.print("\n[dim]Run a workflow with: agentswarm workflow run <name>[/dim]")

    return 0


def _delete_workflow(manager: WorkflowManager, args) -> int:
    """Delete a workflow."""
    if not args.name:
        console.print("[red]Workflow name is required for 'delete' action[/red]")
        return 1

    # Confirm deletion
    if not Confirm.ask(f"Are you sure you want to delete workflow '{args.name}'?"):
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return 0

    if manager.delete_workflow(args.name):
        console.print(f"[green]Workflow '{args.name}' deleted successfully.[/green]")
        return 0
    else:
        console.print(f"[red]Workflow '{args.name}' not found.[/red]")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage workflows")
    parser.add_argument(
        "action", choices=["create", "run", "list", "delete"], help="Workflow action"
    )
    parser.add_argument("name", nargs="?", help="Workflow name")
    parser.add_argument("-p", "--params", help="Input parameters as JSON or @file.json")
    parser.add_argument("-o", "--output", help="Output file for results")

    args = parser.parse_args()
    sys.exit(execute(args))
