"""
Automatic test generation for AgentSwarm Tools Framework.

Generates comprehensive test suites with edge cases and mock data.
"""

import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader


class TestGenerator:
    """Generate comprehensive test suites for tools"""

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize test generator.

        Args:
            project_root: Path to project root
        """
        self.project_root = Path(project_root or ".")
        self.templates_dir = self.project_root / "sdk" / "templates"

        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)), trim_blocks=True, lstrip_blocks=True
        )

    def generate_tests(self, tool_file: Path) -> Path:
        """
        Generate comprehensive tests for a tool.

        Args:
            tool_file: Path to tool Python file

        Returns:
            Path to generated test file
        """
        # Parse tool file
        tool_info = self._parse_tool(tool_file)

        # Generate test context
        test_context = self._prepare_test_context(tool_info)

        # Render test template
        test_file = tool_file.parent / f"test_{tool_file.stem}.py"
        self._render_test_file(test_context, test_file)

        return test_file

    def _parse_tool(self, tool_file: Path) -> Dict[str, Any]:
        """Parse tool file to extract information"""

        content = tool_file.read_text()
        tree = ast.parse(content)

        tool_info = {
            "tool_file": tool_file,
            "class_name": None,
            "tool_name": None,
            "parameters": [],
            "methods": [],
        }

        # Find tool class
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from BaseTool
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "BaseTool":
                        tool_info["class_name"] = node.name

                        # Extract parameters and metadata
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign):
                                if isinstance(item.target, ast.Name):
                                    name = item.target.id

                                    # Extract tool_name
                                    if name == "tool_name" and isinstance(item.value, ast.Constant):
                                        tool_info["tool_name"] = item.value.value

                                    # Extract parameters
                                    if (
                                        name
                                        not in ["tool_name", "tool_category", "max_retries", "retry_delay"]
                                        and item.annotation
                                    ):
                                        param = self._extract_parameter(name, item)
                                        if param:
                                            tool_info["parameters"].append(param)

                            # Extract methods
                            elif isinstance(item, ast.FunctionDef):
                                tool_info["methods"].append(item.name)

                        break

        return tool_info

    def _extract_parameter(self, name: str, node: ast.AnnAssign) -> Optional[Dict[str, Any]]:
        """Extract parameter information from AST node"""

        param = {
            "name": name,
            "type": self._get_type_string(node.annotation),
            "required": False,
            "default": None,
            "description": "",
            "test_value": None,
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
                            param["default"] = default_arg.value
                    elif isinstance(default_arg, ast.Name):
                        if default_arg.id == "Ellipsis":
                            param["required"] = True

                # Extract description
                for keyword in node.value.keywords:
                    if keyword.arg == "description":
                        if isinstance(keyword.value, ast.Constant):
                            param["description"] = keyword.value.value

        # Generate test value based on type
        param["test_value"] = self._generate_test_value(param)

        return param

    def _get_type_string(self, annotation) -> str:
        """Convert AST annotation to type string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            # Handle List[str], Optional[int], etc.
            if isinstance(annotation.value, ast.Name):
                return annotation.value.id
        return "Any"

    def _generate_test_value(self, param: Dict[str, Any]) -> str:
        """Generate test value based on parameter type"""

        type_name = param["type"]

        # Use default if available
        if param["default"] is not None:
            if isinstance(param["default"], str):
                return f'"{param["default"]}"'
            else:
                return str(param["default"])

        # Generate based on type
        test_values = {
            "str": '"test_value"',
            "int": "10",
            "float": "1.5",
            "bool": "True",
            "List": '["item1", "item2"]',
            "Dict": '{"key": "value"}',
            "Optional": "None",
        }

        return test_values.get(type_name, '"test"')

    def _prepare_test_context(self, tool_info: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for test template"""

        # Build import path
        tool_file = tool_info["tool_file"]
        parts = tool_file.parts
        tools_idx = parts.index("tools") if "tools" in parts else -1

        if tools_idx >= 0:
            import_parts = parts[tools_idx:-1]
            import_path = ".".join(import_parts + [tool_file.stem])
        else:
            import_path = tool_file.stem

        # Generate edge case tests
        edge_case_tests = self._generate_edge_case_tests(tool_info)

        context = {
            "class_name": tool_info["class_name"],
            "tool_name": tool_info["tool_name"],
            "import_path": import_path,
            "parameters": tool_info["parameters"],
            "edge_case_tests": edge_case_tests,
        }

        return context

    def _generate_edge_case_tests(self, tool_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate edge case tests"""

        edge_cases = []

        # For each parameter, generate edge cases
        for param in tool_info["parameters"]:
            if param["type"] == "str":
                # Empty string test
                edge_cases.append(
                    {
                        "name": f"{param['name']}_empty_string",
                        "description": f"Test {param['name']} with empty string",
                        "code": f'with pytest.raises(Exception):\n            tool = {tool_info["class_name"]}({param["name"]}="")',
                    }
                )

                # Very long string test
                edge_cases.append(
                    {
                        "name": f"{param['name']}_long_string",
                        "description": f"Test {param['name']} with very long string",
                        "code": f'tool = {tool_info["class_name"]}({param["name"]}="x" * 10000)\n        result = tool.run()\n        assert result is not None',
                    }
                )

            elif param["type"] == "int":
                # Negative number test
                edge_cases.append(
                    {
                        "name": f"{param['name']}_negative",
                        "description": f"Test {param['name']} with negative value",
                        "code": f'# May raise validation error depending on constraints\n        # tool = {tool_info["class_name"]}({param["name"]}=-1)',
                    }
                )

                # Zero test
                edge_cases.append(
                    {
                        "name": f"{param['name']}_zero",
                        "description": f"Test {param['name']} with zero",
                        "code": f'# May raise validation error depending on constraints\n        # tool = {tool_info["class_name"]}({param["name"]}=0)',
                    }
                )

            elif param["type"] == "List":
                # Empty list test
                edge_cases.append(
                    {
                        "name": f"{param['name']}_empty_list",
                        "description": f"Test {param['name']} with empty list",
                        "code": f'tool = {tool_info["class_name"]}({param["name"]}=[])\n        result = tool.run()\n        assert result is not None',
                    }
                )

        return edge_cases

    def _render_test_file(self, context: Dict[str, Any], output_file: Path):
        """Render test file from template"""

        template = self.jinja_env.get_template("test_template.py.jinja2")
        content = template.render(**context)

        output_file.write_text(content)


# Example usage
if __name__ == "__main__":
    from pathlib import Path

    generator = TestGenerator()

    # Test on web_search tool
    tool_file = Path(__file__).parent.parent / "tools/data/search/web_search/web_search.py"

    if tool_file.exists():
        test_file = generator.generate_tests(tool_file)
        print(f"Generated test file: {test_file}")
    else:
        print(f"Tool file not found: {tool_file}")
