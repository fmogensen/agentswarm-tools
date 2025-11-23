"""
Workflow Management for AgentSwarm CLI

Allows creation, management, and execution of multi-step tool workflows.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich import box


console = Console()


class WorkflowManager:
    """Manage workflows for AgentSwarm tools."""

    def __init__(self):
        """Initialize workflow manager."""
        self.workflows_dir = Path.home() / ".agentswarm" / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

    def create_workflow(self, name: Optional[str] = None, interactive: bool = True) -> Dict[str, Any]:
        """
        Create a new workflow.

        Args:
            name: Workflow name
            interactive: Whether to use interactive mode

        Returns:
            Created workflow definition
        """
        if interactive:
            return self._create_workflow_interactive()

        workflow = {
            "name": name or f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "",
            "created_at": datetime.now().isoformat(),
            "steps": []
        }

        return workflow

    def _create_workflow_interactive(self) -> Dict[str, Any]:
        """Create workflow interactively."""
        console.print("\n[bold cyan]Create New Workflow[/bold cyan]")
        console.print("=" * 60)

        # Get workflow metadata
        name = Prompt.ask("Workflow name")
        description = Prompt.ask("Description", default="")

        workflow = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "steps": [],
            "variables": {}
        }

        console.print("\n[bold yellow]Add workflow steps[/bold yellow]")
        console.print("You can reference previous step results using ${steps[N].result}")
        console.print("You can use input variables using ${input.variable_name}\n")

        step_num = 1
        while True:
            console.print(f"\n[bold]Step {step_num}[/bold]")

            tool_name = Prompt.ask("Tool name (or 'done' to finish)")

            if tool_name.lower() == "done":
                break

            # Get parameters
            console.print("\nEnter parameters as JSON or individual key=value pairs")
            params_input = Prompt.ask("Parameters", default="{}")

            try:
                if params_input.startswith("{"):
                    params = json.loads(params_input)
                else:
                    # Parse key=value pairs
                    params = {}
                    for pair in params_input.split(","):
                        if "=" in pair:
                            key, value = pair.split("=", 1)
                            params[key.strip()] = value.strip()
            except json.JSONDecodeError:
                console.print("[red]Invalid JSON format. Step skipped.[/red]")
                continue

            # Optional step configuration
            condition = Prompt.ask("Condition (optional, e.g., ${steps[0].success})", default="")
            error_handling = Prompt.ask(
                "Error handling",
                choices=["stop", "continue", "retry"],
                default="stop"
            )

            step = {
                "tool": tool_name,
                "params": params,
            }

            if condition:
                step["condition"] = condition

            if error_handling != "stop":
                step["on_error"] = error_handling

            workflow["steps"].append(step)
            step_num += 1

        # Get input variables
        if Confirm.ask("\nDoes this workflow need input variables?"):
            console.print("\nDefine input variables (one per line, format: name:type:description)")
            console.print("Example: query:string:Search query")
            console.print("Press Enter on empty line to finish")

            while True:
                var_def = Prompt.ask("Variable", default="")
                if not var_def:
                    break

                parts = var_def.split(":", 2)
                if len(parts) >= 2:
                    var_name = parts[0].strip()
                    var_type = parts[1].strip()
                    var_desc = parts[2].strip() if len(parts) > 2 else ""

                    workflow["variables"][var_name] = {
                        "type": var_type,
                        "description": var_desc,
                        "required": True
                    }

        # Save workflow
        self.save_workflow(workflow)

        console.print(f"\n[green]Workflow '{name}' created successfully![/green]")

        return workflow

    def save_workflow(self, workflow: Dict[str, Any]) -> Path:
        """
        Save workflow to file.

        Args:
            workflow: Workflow definition

        Returns:
            Path to saved workflow file
        """
        name = workflow["name"]
        workflow_file = self.workflows_dir / f"{name}.json"

        with open(workflow_file, "w") as f:
            json.dump(workflow, f, indent=2)

        return workflow_file

    def load_workflow(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load workflow by name.

        Args:
            name: Workflow name

        Returns:
            Workflow definition or None if not found
        """
        workflow_file = self.workflows_dir / f"{name}.json"

        if not workflow_file.exists():
            return None

        with open(workflow_file, "r") as f:
            return json.load(f)

    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all workflows.

        Returns:
            List of workflow metadata
        """
        workflows = []

        for workflow_file in self.workflows_dir.glob("*.json"):
            try:
                with open(workflow_file, "r") as f:
                    workflow = json.load(f)
                    workflows.append({
                        "name": workflow["name"],
                        "description": workflow.get("description", ""),
                        "steps": len(workflow.get("steps", [])),
                        "created_at": workflow.get("created_at", ""),
                        "file": str(workflow_file)
                    })
            except Exception:
                continue

        return sorted(workflows, key=lambda w: w.get("created_at", ""), reverse=True)

    def delete_workflow(self, name: str) -> bool:
        """
        Delete a workflow.

        Args:
            name: Workflow name

        Returns:
            True if deleted, False if not found
        """
        workflow_file = self.workflows_dir / f"{name}.json"

        if workflow_file.exists():
            workflow_file.unlink()
            return True

        return False

    def run_workflow(self, name: str, input_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            name: Workflow name
            input_vars: Input variables for the workflow

        Returns:
            Workflow execution results
        """
        workflow = self.load_workflow(name)

        if not workflow:
            raise ValueError(f"Workflow '{name}' not found")

        console.print(f"\n[bold cyan]Executing workflow: {workflow['name']}[/bold cyan]")

        if workflow.get("description"):
            console.print(f"[dim]{workflow['description']}[/dim]\n")

        # Prepare context
        context = {
            "input": input_vars or {},
            "steps": [],
            "variables": {}
        }

        results = {
            "workflow": name,
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "success": True,
            "errors": []
        }

        # Execute each step
        for i, step in enumerate(workflow["steps"]):
            console.print(f"\n[bold]Step {i + 1}/{len(workflow['steps'])}:[/bold] {step['tool']}")

            # Check condition if present
            if "condition" in step:
                if not self._evaluate_condition(step["condition"], context):
                    console.print("[yellow]Condition not met, skipping step[/yellow]")
                    continue

            # Resolve parameters
            try:
                resolved_params = self._resolve_parameters(step["params"], context)
            except Exception as e:
                console.print(f"[red]Error resolving parameters: {e}[/red]")
                results["errors"].append(f"Step {i + 1}: {str(e)}")

                if step.get("on_error") == "continue":
                    continue
                elif step.get("on_error") == "retry":
                    # Simple retry logic
                    try:
                        resolved_params = self._resolve_parameters(step["params"], context)
                    except Exception as retry_error:
                        results["success"] = False
                        results["errors"].append(f"Step {i + 1} retry failed: {str(retry_error)}")
                        break
                else:
                    results["success"] = False
                    break

            # Execute step
            try:
                step_result = self._execute_step(step["tool"], resolved_params)
                context["steps"].append(step_result)

                results["steps"].append({
                    "step": i + 1,
                    "tool": step["tool"],
                    "success": step_result.get("success", False),
                    "result": step_result
                })

                if step_result.get("success"):
                    console.print("[green]Step completed successfully[/green]")
                else:
                    console.print("[red]Step failed[/red]")

                    if step.get("on_error") != "continue":
                        results["success"] = False
                        results["errors"].append(f"Step {i + 1}: {step['tool']} failed")
                        break

            except Exception as e:
                console.print(f"[red]Step execution error: {e}[/red]")
                results["errors"].append(f"Step {i + 1}: {str(e)}")
                results["success"] = False

                if step.get("on_error") != "continue":
                    break

        results["completed_at"] = datetime.now().isoformat()

        # Save execution log
        self._save_execution_log(name, results)

        return results

    def _resolve_parameters(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve parameter values with variable substitution.

        Args:
            params: Parameter dictionary
            context: Execution context

        Returns:
            Resolved parameters
        """
        resolved = {}

        for key, value in params.items():
            if isinstance(value, str) and "${" in value:
                # Variable substitution
                resolved_value = value

                # Replace ${input.var}
                import re
                for match in re.finditer(r'\$\{input\.(\w+)\}', value):
                    var_name = match.group(1)
                    if var_name in context["input"]:
                        resolved_value = resolved_value.replace(
                            match.group(0),
                            str(context["input"][var_name])
                        )

                # Replace ${steps[N].result}
                for match in re.finditer(r'\$\{steps\[(\d+)\]\.(\w+)\}', value):
                    step_idx = int(match.group(1))
                    field = match.group(2)

                    if step_idx < len(context["steps"]):
                        step_data = context["steps"][step_idx]
                        if field in step_data:
                            resolved_value = resolved_value.replace(
                                match.group(0),
                                str(step_data[field])
                            )

                resolved[key] = resolved_value
            else:
                resolved[key] = value

        return resolved

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression.

        Args:
            condition: Condition expression
            context: Execution context

        Returns:
            True if condition is met
        """
        # Simple condition evaluation (can be enhanced)
        # For now, just check if the referenced value is truthy
        import re

        # Check ${steps[N].success}
        match = re.search(r'\$\{steps\[(\d+)\]\.success\}', condition)
        if match:
            step_idx = int(match.group(1))
            if step_idx < len(context["steps"]):
                return context["steps"][step_idx].get("success", False)

        return True

    def _execute_step(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow step.

        Args:
            tool_name: Tool to execute
            params: Tool parameters

        Returns:
            Step execution result
        """
        from .commands.run import run_tool_by_name

        try:
            result = run_tool_by_name(tool_name, params)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _save_execution_log(self, workflow_name: str, results: Dict[str, Any]):
        """Save workflow execution log."""
        logs_dir = self.workflows_dir / "logs"
        logs_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"{workflow_name}_{timestamp}.json"

        with open(log_file, "w") as f:
            json.dump(results, f, indent=2)

    def display_workflow(self, workflow: Dict[str, Any]):
        """Display workflow details."""
        from rich.tree import Tree

        console.print(f"\n[bold cyan]Workflow: {workflow['name']}[/bold cyan]")

        if workflow.get("description"):
            console.print(f"[dim]{workflow['description']}[/dim]")

        # Show input variables
        if workflow.get("variables"):
            console.print("\n[bold]Input Variables:[/bold]")
            for var_name, var_info in workflow["variables"].items():
                var_type = var_info.get("type", "string")
                var_desc = var_info.get("description", "")
                console.print(f"  - {var_name} ({var_type}): {var_desc}")

        # Show steps as tree
        console.print("\n[bold]Workflow Steps:[/bold]")
        tree = Tree("[bold]Execution Flow[/bold]")

        for i, step in enumerate(workflow["steps"], 1):
            step_label = f"Step {i}: {step['tool']}"

            if step.get("condition"):
                step_label += f" [dim](if {step['condition']})[/dim]"

            step_node = tree.add(step_label)

            # Add parameters
            if step.get("params"):
                params_str = json.dumps(step["params"], indent=2)
                step_node.add(f"[dim]Params: {params_str}[/dim]")

        console.print(tree)


if __name__ == "__main__":
    # Example usage
    manager = WorkflowManager()

    # Create example workflow
    example_workflow = {
        "name": "research-workflow",
        "description": "Search web and create document",
        "created_at": datetime.now().isoformat(),
        "variables": {
            "query": {
                "type": "string",
                "description": "Search query",
                "required": True
            }
        },
        "steps": [
            {
                "tool": "web_search",
                "params": {
                    "query": "${input.query}",
                    "max_results": 10
                }
            },
            {
                "tool": "create_agent",
                "params": {
                    "agent_type": "docs",
                    "content": "${steps[0].result}"
                }
            }
        ]
    }

    print("Example workflow created.")
