"""
Auto documentation generator for AgentSwarm Tools Framework.

Generates comprehensive documentation from tool source code including
parameter tables, examples, and TOOLS_INDEX updates.
"""

import ast
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader


class DocsGenerator:
    """Generate documentation from tool source code"""

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize documentation generator.

        Args:
            project_root: Path to project root
        """
        self.project_root = Path(project_root or ".")
        self.templates_dir = self.project_root / "sdk" / "templates"

        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)), trim_blocks=True, lstrip_blocks=True
        )

    def generate_readme(self, tool_file: Path) -> Path:
        """
        Generate README.md for a tool.

        Args:
            tool_file: Path to tool Python file

        Returns:
            Path to generated README file
        """
        # Parse tool file
        tool_info = self._parse_tool(tool_file)

        # Prepare context
        context = self._prepare_readme_context(tool_info)

        # Render README
        readme_file = tool_file.parent / "README.md"
        self._render_readme(context, readme_file)

        return readme_file

    def update_tools_index(self, tools_dir: Path) -> Path:
        """
        Update TOOLS_INDEX.md with all tools.

        Args:
            tools_dir: Path to tools directory

        Returns:
            Path to TOOLS_INDEX.md
        """
        # Collect all tools
        tools = self._collect_all_tools(tools_dir)

        # Sort alphabetically
        tools.sort(key=lambda x: x["tool_name"])

        # Generate index content
        index_content = self._generate_index_content(tools)

        # Write to file
        index_file = self.project_root / "TOOLS_INDEX.md"
        index_file.write_text(index_content)

        return index_file

    def generate_category_docs(self, category_dir: Path) -> Path:
        """
        Generate category-level documentation.

        Args:
            category_dir: Path to category directory

        Returns:
            Path to category README
        """
        # Collect tools in category
        tools = []

        for subcategory_dir in category_dir.iterdir():
            if not subcategory_dir.is_dir() or subcategory_dir.name.startswith("."):
                continue

            for tool_dir in subcategory_dir.iterdir():
                if not tool_dir.is_dir() or tool_dir.name.startswith("."):
                    continue

                # Skip __pycache__
                if tool_dir.name == "__pycache__":
                    continue

                # Find tool file
                tool_file = self._find_tool_file(tool_dir)
                if tool_file:
                    tool_info = self._parse_tool(tool_file)
                    tools.append(tool_info)

        # Generate category README
        category_readme = self._generate_category_readme(category_dir.name, tools)

        # Write to file
        readme_file = category_dir / "README.md"
        readme_file.write_text(category_readme)

        return readme_file

    def _parse_tool(self, tool_file: Path) -> Dict[str, Any]:
        """Parse tool file to extract information"""

        content = tool_file.read_text()
        tree = ast.parse(content)

        tool_info = {
            "tool_file": tool_file,
            "tool_path": tool_file.parent,
            "class_name": None,
            "tool_name": None,
            "tool_category": None,
            "description": "",
            "long_description": "",
            "parameters": [],
            "requires_api_key": False,
            "api_key_env_var": None,
            "return_type": "Dict[str, Any]",
        }

        # Find tool class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from BaseTool
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "BaseTool":
                        tool_info["class_name"] = node.name

                        # Get docstring
                        docstring = ast.get_docstring(node)
                        if docstring:
                            tool_info["description"] = docstring.split("\n\n")[0].strip()
                            tool_info["long_description"] = docstring

                        # Extract attributes
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign):
                                if isinstance(item.target, ast.Name):
                                    name = item.target.id

                                    # Extract tool_name
                                    if name == "tool_name" and isinstance(item.value, ast.Constant):
                                        tool_info["tool_name"] = item.value.value

                                    # Extract tool_category
                                    elif name == "tool_category" and isinstance(
                                        item.value, ast.Constant
                                    ):
                                        tool_info["tool_category"] = item.value.value

                                    # Extract parameters
                                    elif (
                                        name
                                        not in [
                                            "tool_name",
                                            "tool_category",
                                            "max_retries",
                                            "retry_delay",
                                        ]
                                        and item.annotation
                                    ):
                                        param = self._extract_parameter(name, item)
                                        if param:
                                            tool_info["parameters"].append(param)

                        break

        # Check if requires API key (look for os.getenv in content)
        api_key_pattern = r'os\.getenv\(["\']([^"\']+)["\']'
        matches = re.findall(api_key_pattern, content)
        if matches:
            tool_info["requires_api_key"] = True
            # Use first API key env var found
            tool_info["api_key_env_var"] = matches[0]

        return tool_info

    def _extract_parameter(self, name: str, node: ast.AnnAssign) -> Optional[Dict[str, Any]]:
        """Extract parameter information from AST node"""

        param = {
            "name": name,
            "type": self._get_type_string(node.annotation),
            "required": False,
            "default": None,
            "description": "",
            "example": None,
        }

        # Check if using Field()
        if node.value and isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == "Field":
                # Extract default value
                if node.value.args:
                    default_arg = node.value.args[0]
                    if isinstance(default_arg, ast.Constant):
                        if default_arg.value is ...:
                            param["required"] = True
                        else:
                            param["default"] = repr(default_arg.value)
                    elif isinstance(default_arg, ast.Name):
                        if default_arg.id == "Ellipsis":
                            param["required"] = True

                # Extract description
                for keyword in node.value.keywords:
                    if keyword.arg == "description":
                        if isinstance(keyword.value, ast.Constant):
                            param["description"] = keyword.value.value

        # Generate example
        param["example"] = self._generate_example_value(param)

        return param

    def _get_type_string(self, annotation) -> str:
        """Convert AST annotation to type string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            # Handle List[str], Optional[int], etc.
            if isinstance(annotation.value, ast.Name):
                base = annotation.value.id
                if isinstance(annotation.slice, ast.Name):
                    inner = annotation.slice.id
                    return f"{base}[{inner}]"
                return base
        return "Any"

    def _generate_example_value(self, param: Dict[str, Any]) -> str:
        """Generate example value for parameter"""

        type_name = param["type"]

        # Use default if available
        if param["default"] is not None and param["default"] != "None":
            return param["default"]

        # Generate based on type
        examples = {
            "str": '"example_value"',
            "int": "10",
            "float": "1.5",
            "bool": "True",
            "List[str]": '["item1", "item2"]',
            "Dict[str, Any]": '{"key": "value"}',
        }

        # Check if contains type
        for type_key, example in examples.items():
            if type_key in type_name:
                return example

        return '"value"'

    def _prepare_readme_context(self, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for README template"""

        # Build import path
        tool_file = tool_info["tool_file"]
        parts = tool_file.parts
        tools_idx = parts.index("tools") if "tools" in parts else -1

        if tools_idx >= 0:
            import_parts = parts[tools_idx:-1]
            import_path = ".".join(import_parts + [tool_file.stem])
        else:
            import_path = tool_file.stem

        # Test file path
        test_file_path = f"tests/unit/{tool_info['tool_category']}/test_{tool_info['tool_name']}.py"

        context = {
            **tool_info,
            "import_path": import_path,
            "test_file_path": test_file_path,
            "creation_date": datetime.now().strftime("%Y-%m-%d"),
            "service_name": "External Service",
            "additional_env_vars": [],
            "additional_errors": [],
            "related_tools": [],
        }

        return context

    def _render_readme(self, context: Dict[str, Any], output_file: Path):
        """Render README from template"""

        template = self.jinja_env.get_template("readme_template.md.jinja2")
        content = template.render(**context)

        output_file.write_text(content)

    def _find_tool_file(self, tool_dir: Path) -> Optional[Path]:
        """Find main tool file in directory"""
        # Look for .py file matching directory name
        expected_file = tool_dir / f"{tool_dir.name}.py"
        if expected_file.exists():
            return expected_file

        # Look for any .py file that's not test or __init__
        for file in tool_dir.glob("*.py"):
            if not file.name.startswith("test_") and file.name != "__init__.py":
                return file

        return None

    def _collect_all_tools(self, tools_dir: Path) -> List[Dict[str, Any]]:
        """Collect all tools from tools directory"""

        tools = []

        for category_dir in tools_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            for subcategory_dir in category_dir.iterdir():
                if not subcategory_dir.is_dir() or subcategory_dir.name.startswith("."):
                    continue

                for tool_dir in subcategory_dir.iterdir():
                    if not tool_dir.is_dir() or tool_dir.name.startswith("."):
                        continue

                    # Skip __pycache__
                    if tool_dir.name == "__pycache__":
                        continue

                    # Find tool file
                    tool_file = self._find_tool_file(tool_dir)
                    if tool_file:
                        tool_info = self._parse_tool(tool_file)
                        if tool_info["tool_name"]:
                            tools.append(tool_info)

        return tools

    def _generate_index_content(self, tools: List[Dict[str, Any]]) -> str:
        """Generate TOOLS_INDEX.md content"""

        content = [
            "# Tools Index\n",
            "Complete alphabetical index of all tools in the AgentSwarm Tools Framework.\n",
            f"**Total Tools**: {len(tools)}\n",
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "---\n",
            "## Alphabetical List\n",
        ]

        # Group by first letter
        current_letter = None

        for tool in tools:
            tool_name = tool["tool_name"]
            first_letter = tool_name[0].upper()

            # Add letter header
            if first_letter != current_letter:
                current_letter = first_letter
                content.append(f"\n### {current_letter}\n")

            # Add tool entry
            category = tool.get("tool_category", "unknown")
            description = tool.get("description", "No description")

            # Truncate description
            if len(description) > 100:
                description = description[:97] + "..."

            content.append(f"- **{tool_name}** (`{category}`) - {description}\n")

        # Add category index
        content.append("\n---\n")
        content.append("## By Category\n")

        # Group by category
        by_category = {}
        for tool in tools:
            category = tool.get("tool_category", "unknown")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(tool)

        for category in sorted(by_category.keys()):
            tools_in_category = by_category[category]
            content.append(f"\n### {category.title()} ({len(tools_in_category)} tools)\n")

            for tool in sorted(tools_in_category, key=lambda x: x["tool_name"]):
                description = tool.get("description", "No description")
                if len(description) > 80:
                    description = description[:77] + "..."

                content.append(f"- **{tool['tool_name']}** - {description}\n")

        return "".join(content)

    def _generate_category_readme(self, category_name: str, tools: List[Dict[str, Any]]) -> str:
        """Generate category README content"""

        content = [
            f"# {category_name.title()} Tools\n",
            f"\nTools in the {category_name} category.\n",
            f"\n**Total Tools**: {len(tools)}\n",
            "\n## Tools\n",
        ]

        # Sort by tool name
        tools.sort(key=lambda x: x.get("tool_name", ""))

        for tool in tools:
            tool_name = tool.get("tool_name", "unknown")
            description = tool.get("description", "No description")
            tool_path = tool.get("tool_path", "")

            content.append(f"\n### {tool_name}\n")
            content.append(f"\n{description}\n")
            content.append(f"\n**Path**: `{tool_path}`\n")

            # Parameters
            if tool.get("parameters"):
                content.append("\n**Parameters**:\n")
                for param in tool["parameters"]:
                    content.append(
                        f"- `{param['name']}` ({param['type']}): {param.get('description', 'No description')}\n"
                    )

        return "".join(content)


# Example usage
if __name__ == "__main__":
    from pathlib import Path

    generator = DocsGenerator()

    # Test on web_search tool
    tool_file = Path(__file__).parent.parent / "tools/data/search/web_search/web_search.py"

    if tool_file.exists():
        readme_file = generator.generate_readme(tool_file)
        print(f"Generated README: {readme_file}")

        # Update TOOLS_INDEX
        tools_dir = Path(__file__).parent.parent / "tools"
        if tools_dir.exists():
            index_file = generator.update_tools_index(tools_dir)
            print(f"Updated TOOLS_INDEX: {index_file}")
    else:
        print(f"Tool file not found: {tool_file}")
