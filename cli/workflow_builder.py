#!/usr/bin/env python3
"""
Interactive Workflow Builder CLI for AgentSwarm Tools Framework.

Provides step-by-step wizard for creating, validating, and saving workflows.

Usage:
    python -m cli.workflow_builder
    python -m cli.workflow_builder --template research
    python -m cli.workflow_builder --load my_workflow.json
"""

import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.registry import tool_registry, discover_tools
from shared.workflow import WorkflowEngine, WorkflowContext


class WorkflowBuilder:
    """Interactive workflow builder."""

    def __init__(self):
        """Initialize workflow builder."""
        self.workflow: Dict[str, Any] = {
            "name": "",
            "description": "",
            "variables": {},
            "steps": [],
            "error_handling": {
                "retry_on_failure": True,
                "max_retries": 3,
                "continue_on_error": False
            },
            "timeout": 1800
        }

        # Discover tools
        if not tool_registry.is_discovered:
            discover_tools()

    def run(self) -> None:
        """Run interactive workflow builder."""
        print("=" * 60)
        print("AgentSwarm Workflow Builder")
        print("=" * 60)
        print()

        # Get workflow metadata
        self._get_workflow_metadata()

        # Get variables
        self._get_variables()

        # Add steps
        self._add_steps()

        # Configure error handling
        self._configure_error_handling()

        # Review and save
        self._review_and_save()

    def _get_workflow_metadata(self) -> None:
        """Get workflow name and description."""
        print("Workflow Information")
        print("-" * 60)

        self.workflow["name"] = input("Workflow name: ").strip() or "unnamed-workflow"
        self.workflow["description"] = input("Description: ").strip() or ""
        print()

    def _get_variables(self) -> None:
        """Get workflow variables."""
        print("Variables (optional)")
        print("-" * 60)
        print("Enter variable definitions. Press Enter with empty name to continue.")
        print()

        while True:
            var_name = input("Variable name: ").strip()
            if not var_name:
                break

            var_value = input(f"Value for '{var_name}': ").strip()

            # Try to parse as JSON for complex types
            try:
                var_value = json.loads(var_value)
            except json.JSONDecodeError:
                # Keep as string
                pass

            self.workflow["variables"][var_name] = var_value
            print(f"✓ Added variable: {var_name}")
            print()

    def _add_steps(self) -> None:
        """Add workflow steps."""
        print("Workflow Steps")
        print("-" * 60)
        print("Add steps to your workflow. Press Enter with empty ID to finish.")
        print()

        while True:
            print(f"\nStep {len(self.workflow['steps']) + 1}")
            print("-" * 40)

            step_id = input("Step ID: ").strip()
            if not step_id:
                if len(self.workflow['steps']) == 0:
                    print("⚠ Workflow must have at least one step!")
                    continue
                break

            step_type = self._select_step_type()

            if step_type == "tool":
                step = self._create_tool_step(step_id)
            elif step_type == "foreach":
                step = self._create_foreach_step(step_id)
            elif step_type == "condition":
                step = self._create_condition_step(step_id)
            elif step_type == "parallel":
                step = self._create_parallel_step(step_id)
            else:
                continue

            # Add condition if needed
            condition = input("Condition (optional, e.g., ${steps.search.success}): ").strip()
            if condition:
                step["condition"] = condition

            self.workflow["steps"].append(step)
            print(f"✓ Added step: {step_id}")

    def _select_step_type(self) -> str:
        """Select step type."""
        print("\nStep Types:")
        print("  1. tool      - Execute a single tool")
        print("  2. foreach   - Loop over items")
        print("  3. condition - Conditional execution (if/else)")
        print("  4. parallel  - Execute steps in parallel")

        while True:
            choice = input("Select type (1-4): ").strip()
            if choice == "1":
                return "tool"
            elif choice == "2":
                return "foreach"
            elif choice == "3":
                return "condition"
            elif choice == "4":
                return "parallel"
            else:
                print("Invalid choice. Please enter 1-4.")

    def _create_tool_step(self, step_id: str) -> Dict[str, Any]:
        """Create a tool execution step."""
        # Show available tools
        print("\nAvailable tools:")
        tools = tool_registry.list_tools()

        # Group by category
        by_category: Dict[str, List[Dict]] = {}
        for tool in tools:
            category = tool['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(tool)

        # Display
        for category, cat_tools in sorted(by_category.items()):
            print(f"\n{category.upper()}:")
            for tool in cat_tools[:5]:  # Show first 5 per category
                print(f"  - {tool['name']}")
            if len(cat_tools) > 5:
                print(f"  ... and {len(cat_tools) - 5} more")

        # Get tool name
        tool_name = input("\nTool name: ").strip()

        # Validate tool exists
        if not tool_registry.has_tool(tool_name):
            print(f"⚠ Warning: Tool '{tool_name}' not found in registry")

        # Get tool metadata
        metadata = tool_registry.get_tool_metadata(tool_name)

        # Get parameters
        params = {}
        if metadata:
            print(f"\nParameters for {tool_name}:")
            for field_name, field_info in metadata.get('fields', {}).items():
                required = field_info.get('required', False)
                description = field_info.get('description', '')
                default = field_info.get('default')

                prompt = f"  {field_name}"
                if required:
                    prompt += " (required)"
                if description:
                    prompt += f" - {description}"
                prompt += ": "

                value = input(prompt).strip()

                if not value and not required:
                    if default is not None:
                        value = default
                    else:
                        continue

                # Try to parse as JSON
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass

                params[field_name] = value
        else:
            # Manual parameter entry
            print("\nParameters (JSON format or key=value):")
            while True:
                param_input = input("  Parameter (or Enter to finish): ").strip()
                if not param_input:
                    break

                if "=" in param_input:
                    key, value = param_input.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Try to parse value as JSON
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass

                    params[key] = value

        return {
            "id": step_id,
            "tool": tool_name,
            "params": params
        }

    def _create_foreach_step(self, step_id: str) -> Dict[str, Any]:
        """Create a foreach loop step."""
        items = input("Items to iterate (e.g., ${steps.search.result}): ").strip()

        print("\nDefine the step to execute for each item:")
        inner_step_id = input("Inner step ID: ").strip()
        inner_step = self._create_tool_step(inner_step_id)

        return {
            "id": step_id,
            "type": "foreach",
            "items": items,
            "step": inner_step
        }

    def _create_condition_step(self, step_id: str) -> Dict[str, Any]:
        """Create a conditional step."""
        condition = input("Condition (e.g., ${steps.search.success}): ").strip()

        print("\nDefine the 'then' step:")
        then_step = self._create_tool_step("then")

        else_step = None
        has_else = input("Add 'else' step? (y/n): ").strip().lower() == 'y'
        if has_else:
            print("\nDefine the 'else' step:")
            else_step = self._create_tool_step("else")

        step = {
            "id": step_id,
            "type": "condition",
            "condition": condition,
            "then": then_step
        }

        if else_step:
            step["else"] = else_step

        return step

    def _create_parallel_step(self, step_id: str) -> Dict[str, Any]:
        """Create parallel execution step."""
        print("\nDefine steps to execute in parallel:")

        steps = []
        while True:
            parallel_id = input(f"Parallel step ID (or Enter to finish): ").strip()
            if not parallel_id:
                if len(steps) == 0:
                    print("⚠ Need at least one parallel step!")
                    continue
                break

            step = self._create_tool_step(parallel_id)
            steps.append(step)

        return {
            "id": step_id,
            "type": "parallel",
            "steps": steps
        }

    def _configure_error_handling(self) -> None:
        """Configure error handling."""
        print("\nError Handling")
        print("-" * 60)

        retry = input("Retry on failure? (y/n) [y]: ").strip().lower()
        self.workflow["error_handling"]["retry_on_failure"] = retry != 'n'

        if self.workflow["error_handling"]["retry_on_failure"]:
            max_retries = input("Max retries [3]: ").strip()
            self.workflow["error_handling"]["max_retries"] = int(max_retries) if max_retries else 3

        continue_on_error = input("Continue on error? (y/n) [n]: ").strip().lower()
        self.workflow["error_handling"]["continue_on_error"] = continue_on_error == 'y'

        timeout = input("Timeout in seconds [1800]: ").strip()
        self.workflow["timeout"] = int(timeout) if timeout else 1800

        print()

    def _review_and_save(self) -> None:
        """Review workflow and save."""
        print("\nWorkflow Summary")
        print("=" * 60)
        print(json.dumps(self.workflow, indent=2))
        print("=" * 60)
        print()

        # Validate
        try:
            engine = WorkflowEngine(self.workflow)
            print("✓ Workflow validation passed")
        except Exception as e:
            print(f"⚠ Validation warning: {e}")

        # Save
        save = input("\nSave workflow? (y/n) [y]: ").strip().lower()
        if save != 'n':
            filename = input(f"Filename [{self.workflow['name']}.json]: ").strip()
            if not filename:
                filename = f"{self.workflow['name']}.json"

            if not filename.endswith('.json'):
                filename += '.json'

            # Create examples/workflows directory if not exists
            workflows_dir = Path(__file__).parent.parent / "examples" / "workflows"
            workflows_dir.mkdir(parents=True, exist_ok=True)

            filepath = workflows_dir / filename

            with open(filepath, 'w') as f:
                json.dump(self.workflow, f, indent=2)

            print(f"✓ Workflow saved to: {filepath}")

            # Test execution?
            test = input("\nTest execution in mock mode? (y/n) [n]: ").strip().lower()
            if test == 'y':
                os.environ["USE_MOCK_APIS"] = "true"
                try:
                    print("\nExecuting workflow...")
                    result = engine.execute()
                    print("\nExecution Result:")
                    print(json.dumps(result, indent=2))
                except Exception as e:
                    print(f"⚠ Execution failed: {e}")


def load_template(template_name: str) -> Optional[Dict[str, Any]]:
    """Load a workflow template."""
    templates_dir = Path(__file__).parent.parent / "examples" / "workflows"
    template_file = templates_dir / f"{template_name}.json"

    if template_file.exists():
        with open(template_file, 'r') as f:
            return json.load(f)
    return None


def list_templates() -> List[str]:
    """List available workflow templates."""
    templates_dir = Path(__file__).parent.parent / "examples" / "workflows"
    if not templates_dir.exists():
        return []

    return [f.stem for f in templates_dir.glob("*.json")]


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AgentSwarm Workflow Builder")
    parser.add_argument("--template", help="Load template workflow")
    parser.add_argument("--load", help="Load existing workflow file")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")
    parser.add_argument("--execute", help="Execute a workflow file")

    args = parser.parse_args()

    if args.list_templates:
        print("Available workflow templates:")
        for template in list_templates():
            print(f"  - {template}")
        return

    if args.execute:
        # Execute workflow
        filepath = Path(args.execute)
        if not filepath.exists():
            print(f"Error: Workflow file not found: {filepath}")
            sys.exit(1)

        print(f"Executing workflow: {filepath}")
        engine = WorkflowEngine.from_file(filepath)
        result = engine.execute()

        print("\nExecution Result:")
        print(json.dumps(result, indent=2))
        return

    # Interactive builder
    builder = WorkflowBuilder()

    if args.template:
        template = load_template(args.template)
        if template:
            builder.workflow = template
            print(f"Loaded template: {args.template}")
        else:
            print(f"Template not found: {args.template}")
            print(f"Available templates: {', '.join(list_templates())}")
            sys.exit(1)
    elif args.load:
        filepath = Path(args.load)
        if filepath.exists():
            with open(filepath, 'r') as f:
                builder.workflow = json.load(f)
            print(f"Loaded workflow: {filepath}")
        else:
            print(f"File not found: {filepath}")
            sys.exit(1)

    builder.run()


if __name__ == "__main__":
    main()
