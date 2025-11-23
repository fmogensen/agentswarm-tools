"""
Tool scaffolding generator for AgentSwarm Tools Framework.

Provides interactive wizard and CLI commands to generate complete tool structures
with templates, tests, and documentation.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import questionary
from jinja2 import Environment, FileSystemLoader, Template
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class ToolGenerator:
    """Generate complete tool structures with templates"""

    # Category metadata
    CATEGORIES = {
        "data": {
            "name": "Data & Search",
            "subcategories": ["search", "business", "intelligence"],
            "description": "Search, business analytics, AI intelligence",
        },
        "communication": {
            "name": "Communication & Collaboration",
            "subcategories": ["email", "calendar", "workspace", "messaging", "phone"],
            "description": "Email, calendar, workspace integration",
        },
        "media": {
            "name": "Media Operations",
            "subcategories": ["generation", "analysis", "processing"],
            "description": "Media generation, analysis, and processing",
        },
        "visualization": {
            "name": "Data Visualization",
            "subcategories": ["charts", "diagrams", "graphs"],
            "description": "Charts, diagrams, and graphs",
        },
        "content": {
            "name": "Content Creation",
            "subcategories": ["documents", "web"],
            "description": "Documents and web content",
        },
        "infrastructure": {
            "name": "Infrastructure",
            "subcategories": ["execution", "storage", "management"],
            "description": "Code execution and storage",
        },
        "utils": {
            "name": "Utilities",
            "subcategories": ["helpers", "transformers", "validators"],
            "description": "Utility tools and helpers",
        },
        "integrations": {
            "name": "Integrations",
            "subcategories": ["external_services"],
            "description": "External service connectors",
        },
    }

    # Parameter type mappings
    TYPE_MAPPINGS = {
        "str": {"python": "str", "default": '""', "example": '"example"'},
        "int": {"python": "int", "default": "0", "example": "10"},
        "float": {"python": "float", "default": "0.0", "example": "1.5"},
        "bool": {"python": "bool", "default": "False", "example": "True"},
        "list": {"python": "List[str]", "default": "[]", "example": '["item1", "item2"]'},
        "dict": {"python": "Dict[str, Any]", "default": "{}", "example": '{"key": "value"}'},
        "optional_str": {"python": "Optional[str]", "default": "None", "example": '"value"'},
    }

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize tool generator.

        Args:
            project_root: Path to project root (defaults to current directory)
        """
        self.project_root = Path(project_root or os.getcwd())
        self.templates_dir = self.project_root / "sdk" / "templates"

        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)), trim_blocks=True, lstrip_blocks=True
        )

    def generate_tool_interactive(self) -> Dict[str, Any]:
        """
        Interactive wizard for tool generation.

        Returns:
            Dict with generated file paths and metadata
        """
        console.print(
            Panel.fit(
                "[bold cyan]AgentSwarm Tool Generator[/bold cyan]\n"
                "[dim]Create production-ready tools with best practices[/dim]",
                border_style="cyan",
            )
        )

        # Collect tool information
        tool_config = self._collect_tool_info()

        # Generate files
        generated_files = self._generate_files(tool_config)

        # Display success
        self._display_success(tool_config, generated_files)

        return {
            "tool_name": tool_config["tool_name"],
            "tool_path": tool_config["tool_path"],
            "generated_files": generated_files,
            "config": tool_config,
        }

    def generate_tool_cli(
        self,
        tool_name: str,
        category: str,
        description: str,
        subcategory: Optional[str] = None,
        parameters: Optional[List[Dict]] = None,
        requires_api_key: bool = False,
        api_key_env_var: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate tool from CLI arguments.

        Args:
            tool_name: Name of the tool
            category: Tool category
            description: Tool description
            subcategory: Optional subcategory
            parameters: List of parameter configs
            requires_api_key: Whether tool requires API key
            api_key_env_var: Environment variable name for API key

        Returns:
            Dict with generated file paths and metadata
        """
        # Build tool config
        tool_config = {
            "tool_name": self._to_snake_case(tool_name),
            "class_name": self._to_class_name(tool_name),
            "category": category,
            "subcategory": subcategory or self.CATEGORIES[category]["subcategories"][0],
            "description": description,
            "long_description": description,
            "parameters": parameters or [],
            "requires_api_key": requires_api_key,
            "api_key_env_var": api_key_env_var or f"{tool_name.upper()}_API_KEY",
        }

        # Generate file paths
        tool_config["tool_path"] = self._get_tool_path(tool_config)

        # Generate files
        generated_files = self._generate_files(tool_config)

        return {
            "tool_name": tool_config["tool_name"],
            "tool_path": tool_config["tool_path"],
            "generated_files": generated_files,
            "config": tool_config,
        }

    def _collect_tool_info(self) -> Dict[str, Any]:
        """Collect tool information via interactive prompts"""

        # Tool name
        tool_name = questionary.text(
            "Tool name (snake_case):",
            validate=lambda x: len(x) > 0 and x.replace("_", "").isalnum(),
        ).ask()

        tool_name = self._to_snake_case(tool_name)
        class_name = self._to_class_name(tool_name)

        # Category selection
        category_choices = [
            f"{key}: {meta['name']} - {meta['description']}"
            for key, meta in self.CATEGORIES.items()
        ]

        category_answer = questionary.select("Select category:", choices=category_choices).ask()

        category = category_answer.split(":")[0]

        # Subcategory
        subcategory_choices = self.CATEGORIES[category]["subcategories"]
        subcategory = questionary.select("Select subcategory:", choices=subcategory_choices).ask()

        # Description
        description = questionary.text("Tool description:", validate=lambda x: len(x) > 10).ask()

        long_description = questionary.text(
            "Detailed description (optional, press Enter to skip):", default=description
        ).ask()

        # Parameters
        parameters = []
        add_params = questionary.confirm("Add parameters?", default=True).ask()

        while add_params:
            param = self._collect_parameter()
            parameters.append(param)

            add_params = questionary.confirm("Add another parameter?", default=False).ask()

        # API requirements
        requires_api_key = questionary.confirm("Requires API key?", default=False).ask()

        api_key_env_var = None
        service_name = None
        if requires_api_key:
            service_name = questionary.text("Service name (e.g., OpenAI, Google):").ask()

            api_key_env_var = questionary.text(
                "API key environment variable:", default=f"{tool_name.upper()}_API_KEY"
            ).ask()

        # Build config
        tool_config = {
            "tool_name": tool_name,
            "class_name": class_name,
            "category": category,
            "subcategory": subcategory,
            "description": description,
            "long_description": long_description,
            "parameters": parameters,
            "requires_api_key": requires_api_key,
            "api_key_env_var": api_key_env_var,
            "service_name": service_name or "External Service",
            "creation_date": datetime.now().strftime("%Y-%m-%d"),
        }

        # Get tool path
        tool_config["tool_path"] = self._get_tool_path(tool_config)

        return tool_config

    def _collect_parameter(self) -> Dict[str, Any]:
        """Collect parameter information"""

        param_name = questionary.text("Parameter name:", validate=lambda x: x.isidentifier()).ask()

        param_type = questionary.select(
            "Parameter type:", choices=list(self.TYPE_MAPPINGS.keys())
        ).ask()

        param_required = questionary.confirm("Required?", default=True).ask()

        param_description = questionary.text("Parameter description:").ask()

        # Get type info
        type_info = self.TYPE_MAPPINGS[param_type]

        # Build parameter config
        param = {
            "name": param_name,
            "type": type_info["python"],
            "required": param_required,
            "default": "..." if param_required else type_info["default"],
            "description": param_description,
            "example": type_info["example"],
            "test_value": type_info["example"],
        }

        # Add constraints for certain types
        if param_type == "str" and param_required:
            param["constraints"] = "min_length=1"
            param["validation"] = (
                f'if not self.{param_name}.strip():\n            raise ValidationError("{param_name} cannot be empty", tool_name=self.tool_name)'
            )
        elif param_type == "int":
            min_val = questionary.text("Minimum value (optional):", default="").ask()
            max_val = questionary.text("Maximum value (optional):", default="").ask()

            constraints = []
            if min_val:
                constraints.append(f"ge={min_val}")
            if max_val:
                constraints.append(f"le={max_val}")

            if constraints:
                param["constraints"] = ", ".join(constraints)

        return param

    def _get_tool_path(self, config: Dict[str, Any]) -> Path:
        """Get tool directory path"""
        return (
            self.project_root
            / "tools"
            / config["category"]
            / config["subcategory"]
            / config["tool_name"]
        )

    def _generate_files(self, config: Dict[str, Any]) -> List[str]:
        """Generate all tool files"""

        tool_path = Path(config["tool_path"])
        tool_path.mkdir(parents=True, exist_ok=True)

        generated_files = []

        # Prepare template context
        context = self._prepare_template_context(config)

        # Generate tool file
        tool_file = tool_path / f"{config['tool_name']}.py"
        self._render_template("tool_template.py.jinja2", tool_file, context)
        generated_files.append(str(tool_file))

        # Generate test file
        test_file = tool_path / f"test_{config['tool_name']}.py"
        self._render_template("test_template.py.jinja2", test_file, context)
        generated_files.append(str(test_file))

        # Generate README
        readme_file = tool_path / "README.md"
        self._render_template("readme_template.md.jinja2", readme_file, context)
        generated_files.append(str(readme_file))

        # Generate __init__.py
        init_file = tool_path / "__init__.py"
        init_content = f'"""Tool: {config["tool_name"]}"""\n\nfrom .{config["tool_name"]} import {config["class_name"]}\n\n__all__ = ["{config["class_name"]}"]\n'
        init_file.write_text(init_content)
        generated_files.append(str(init_file))

        return generated_files

    def _prepare_template_context(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for template rendering"""

        # Determine if we need certain imports
        has_list_param = any(p["type"].startswith("List") for p in config.get("parameters", []))
        has_optional_params = any(
            p["type"].startswith("Optional") for p in config.get("parameters", [])
        )

        # Build import path
        import_path = f"tools.{config['category']}.{config['subcategory']}.{config['tool_name']}"

        # Mock result
        mock_result = '{"mock": True, "data": "sample result"}'

        # Return type
        return_type = "Dict[str, Any]"

        context = {
            **config,
            "has_list_param": has_list_param,
            "has_optional_params": has_optional_params,
            "requires_requests": True,  # Most tools use requests
            "import_path": import_path,
            "test_file_path": f"tests/unit/{config['category']}/{config['subcategory']}/test_{config['tool_name']}.py",
            "mock_result": mock_result,
            "return_type": return_type,
            "has_assertions": True,
            "edge_case_tests": [],
            "related_tools": [],
            "additional_env_vars": [],
            "additional_errors": [],
        }

        return context

    def _render_template(self, template_name: str, output_file: Path, context: Dict[str, Any]):
        """Render Jinja2 template to file"""

        template = self.jinja_env.get_template(template_name)
        content = template.render(**context)

        output_file.write_text(content)

    def _display_success(self, config: Dict[str, Any], generated_files: List[str]):
        """Display success message with next steps"""

        console.print("\n[bold green]✓ Tool generated successfully![/bold green]\n")

        # Files table
        table = Table(title="Generated Files", show_header=True, header_style="bold magenta")
        table.add_column("File", style="cyan")
        table.add_column("Description", style="white")

        for file in generated_files:
            filename = Path(file).name
            if filename.endswith(".py") and not filename.startswith("test_"):
                desc = "Main tool implementation"
            elif filename.startswith("test_"):
                desc = "Test suite"
            elif filename == "README.md":
                desc = "Documentation"
            elif filename == "__init__.py":
                desc = "Package initialization"
            else:
                desc = "Support file"

            table.add_row(filename, desc)

        console.print(table)

        # Next steps
        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print(f"  1. Implement _process() method in {config['tool_name']}.py")
        if config.get("requires_api_key"):
            console.print(
                f"  2. Set environment variable: export {config['api_key_env_var']}=your-key"
            )
            console.print("  3. Add API integration")
            console.print(f"  4. Run tests: pytest {config['tool_path']}/")
        else:
            console.print("  2. Add business logic")
            console.print(f"  3. Run tests: pytest {config['tool_path']}/")

        console.print(f"  5. Update TOOLS_INDEX.md: agentswarm generate-docs\n")

    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case"""
        # Replace hyphens and spaces with underscores
        name = re.sub(r"[-\s]+", "_", name)
        # Insert underscores before uppercase letters
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        return name.lower()

    def _to_class_name(self, snake_case: str) -> str:
        """Convert snake_case to ClassName"""
        parts = snake_case.split("_")
        return "".join(word.capitalize() for word in parts)


# Example usage
if __name__ == "__main__":
    # Test the generator
    generator = ToolGenerator()

    # Example CLI generation
    result = generator.generate_tool_cli(
        tool_name="example_tool",
        category="data",
        description="Example tool for testing",
        subcategory="search",
        parameters=[
            {
                "name": "query",
                "type": "str",
                "required": True,
                "default": "...",
                "description": "Search query",
                "example": '"test query"',
                "test_value": '"test"',
                "constraints": "min_length=1",
            }
        ],
        requires_api_key=True,
        api_key_env_var="EXAMPLE_API_KEY",
    )

    print(f"Generated tool: {result['tool_name']}")
    print(f"Files: {result['generated_files']}")
