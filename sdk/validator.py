"""
Tool validation for AgentSwarm Tools Framework.

Validates tools against Agency Swarm standards and best practices.
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class ValidationIssue:
    """Represents a validation issue"""

    severity: str  # "error", "warning", "info"
    category: str  # e.g., "structure", "security", "documentation"
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of tool validation"""

    tool_path: Path
    passed: bool
    issues: List[ValidationIssue]
    score: int  # 0-100

    @property
    def errors(self) -> List[ValidationIssue]:
        """Get all errors"""
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        """Get all warnings"""
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def has_errors(self) -> bool:
        """Check if has any errors"""
        return len(self.errors) > 0


class ToolValidator:
    """Validates tools against Agency Swarm standards"""

    # Required methods for all tools
    REQUIRED_METHODS = [
        "_execute",
        "_validate_parameters",
        "_should_use_mock",
        "_generate_mock_results",
        "_process",
    ]

    # Forbidden patterns (security)
    FORBIDDEN_PATTERNS = [
        (r'api[_-]?key\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded API key detected"),
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
        (r'secret\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded secret detected"),
        (r'token\s*=\s*["\'][^"\']{10,}["\']', "Hardcoded token detected"),
    ]

    # Required patterns
    REQUIRED_PATTERNS = [
        (r"from shared\.base import BaseTool", "Must import BaseTool"),
        (r"from shared\.errors import", "Must import error classes"),
        (r'tool_name:\s*str\s*=\s*["\']', "Must define tool_name"),
        (r'tool_category:\s*str\s*=\s*["\']', "Must define tool_category"),
    ]

    def validate_tool(self, tool_path: Path) -> ValidationResult:
        """
        Validate a tool.

        Args:
            tool_path: Path to tool directory or file

        Returns:
            ValidationResult with issues and score
        """
        issues = []

        # Find tool file
        if tool_path.is_dir():
            # Find main tool file
            tool_file = self._find_tool_file(tool_path)
            if not tool_file:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        category="structure",
                        message=f"No tool file found in {tool_path}",
                    )
                )
                return ValidationResult(tool_path=tool_path, passed=False, issues=issues, score=0)
        else:
            tool_file = tool_path

        # Read file content
        try:
            content = tool_file.read_text()
        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity="error", category="structure", message=f"Cannot read file: {e}"
                )
            )
            return ValidationResult(tool_path=tool_path, passed=False, issues=issues, score=0)

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="syntax",
                    message=f"Syntax error: {e}",
                    line_number=e.lineno,
                )
            )
            return ValidationResult(tool_path=tool_path, passed=False, issues=issues, score=0)

        # Run validation checks
        issues.extend(self._check_structure(tree, content))
        issues.extend(self._check_security(content))
        issues.extend(self._check_documentation(tree, content))
        issues.extend(self._check_parameters(tree))
        issues.extend(self._check_test_block(content))
        issues.extend(self._check_error_handling(tree, content))

        # Check for supporting files
        if tool_path.is_dir():
            issues.extend(self._check_supporting_files(tool_path))

        # Calculate score
        score = self._calculate_score(issues)

        # Determine pass/fail
        passed = not any(i.severity == "error" for i in issues)

        return ValidationResult(tool_path=tool_path, passed=passed, issues=issues, score=score)

    def validate_all_tools(self, tools_dir: Path) -> Dict[str, ValidationResult]:
        """
        Validate all tools in a directory.

        Args:
            tools_dir: Path to tools directory

        Returns:
            Dict mapping tool names to validation results
        """
        results = {}

        # Find all tool directories
        for category_dir in tools_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            for subcategory_dir in category_dir.iterdir():
                if not subcategory_dir.is_dir() or subcategory_dir.name.startswith("."):
                    continue

                for tool_dir in subcategory_dir.iterdir():
                    if not tool_dir.is_dir() or tool_dir.name.startswith("."):
                        continue

                    # Skip if __pycache__
                    if tool_dir.name == "__pycache__":
                        continue

                    # Validate tool
                    result = self.validate_tool(tool_dir)
                    results[tool_dir.name] = result

        return results

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

    def _check_structure(self, tree: ast.AST, content: str) -> List[ValidationIssue]:
        """Check tool structure"""
        issues = []

        # Find tool class
        tool_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from BaseTool
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "BaseTool":
                        tool_class = node
                        break

        if not tool_class:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="structure",
                    message="No class inheriting from BaseTool found",
                    suggestion="Class must inherit from BaseTool",
                )
            )
            return issues

        # Check required methods
        methods = {m.name for m in tool_class.body if isinstance(m, ast.FunctionDef)}

        for required_method in self.REQUIRED_METHODS:
            if required_method not in methods:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        category="structure",
                        message=f"Missing required method: {required_method}()",
                        suggestion=f"Add {required_method}() method to tool class",
                    )
                )

        # Check tool_name and tool_category
        has_tool_name = False
        has_tool_category = False

        for node in tool_class.body:
            if isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    if node.target.id == "tool_name":
                        has_tool_name = True
                    elif node.target.id == "tool_category":
                        has_tool_category = True

        if not has_tool_name:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="structure",
                    message="Missing tool_name attribute",
                    suggestion='Add: tool_name: str = "your_tool_name"',
                )
            )

        if not has_tool_category:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="structure",
                    message="Missing tool_category attribute",
                    suggestion='Add: tool_category: str = "category_name"',
                )
            )

        return issues

    def _check_security(self, content: str) -> List[ValidationIssue]:
        """Check for security issues"""
        issues = []

        # Check for hardcoded secrets
        for pattern, message in self.FORBIDDEN_PATTERNS:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                line_number = content[: match.start()].count("\n") + 1
                issues.append(
                    ValidationIssue(
                        severity="error",
                        category="security",
                        message=message,
                        line_number=line_number,
                        suggestion="Use os.getenv() to load from environment variables",
                    )
                )

        # Check if os.getenv is used when needed
        if any(keyword in content.lower() for keyword in ["api", "key", "token", "secret"]):
            if "os.getenv" not in content:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="security",
                        message="Tool may require API keys but doesn't use os.getenv()",
                        suggestion="Use os.getenv() to load API keys from environment",
                    )
                )

        return issues

    def _check_documentation(self, tree: ast.AST, content: str) -> List[ValidationIssue]:
        """Check documentation completeness"""
        issues = []

        # Find tool class
        tool_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "BaseTool":
                        tool_class = node
                        break

        if not tool_class:
            return issues

        # Check class docstring
        docstring = ast.get_docstring(tool_class)
        if not docstring:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="documentation",
                    message="Missing class docstring",
                    line_number=tool_class.lineno,
                    suggestion="Add comprehensive docstring with Args, Returns, and Example sections",
                )
            )
        else:
            # Check docstring sections
            required_sections = ["Args:", "Returns:", "Example:"]
            for section in required_sections:
                if section not in docstring:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            category="documentation",
                            message=f"Docstring missing {section} section",
                            line_number=tool_class.lineno,
                            suggestion=f"Add {section} section to docstring",
                        )
                    )

        # Check method docstrings
        for node in tool_class.body:
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith("_"):  # Private/protected methods
                    method_docstring = ast.get_docstring(node)
                    if not method_docstring:
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                category="documentation",
                                message=f"Method {node.name}() missing docstring",
                                line_number=node.lineno,
                                suggestion="Add docstring describing method purpose",
                            )
                        )

        return issues

    def _check_parameters(self, tree: ast.AST) -> List[ValidationIssue]:
        """Check parameter definitions"""
        issues = []

        # Find tool class
        tool_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "BaseTool":
                        tool_class = node
                        break

        if not tool_class:
            return issues

        # Check parameters have Field() with descriptions
        for node in tool_class.body:
            if isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    param_name = node.target.id

                    # Skip metadata fields
                    if param_name in [
                        "tool_name",
                        "tool_category",
                        "max_retries",
                        "retry_delay",
                    ]:
                        continue

                    # Check if uses Field()
                    if node.value:
                        has_field = False
                        has_description = False

                        if isinstance(node.value, ast.Call):
                            if isinstance(node.value.func, ast.Name):
                                if node.value.func.id == "Field":
                                    has_field = True

                                    # Check for description
                                    for keyword in node.value.keywords:
                                        if keyword.arg == "description":
                                            has_description = True

                        if not has_field:
                            issues.append(
                                ValidationIssue(
                                    severity="warning",
                                    category="parameters",
                                    message=f"Parameter '{param_name}' not using Field()",
                                    line_number=node.lineno,
                                    suggestion="Use Field() for all parameters with descriptions",
                                )
                            )
                        elif not has_description:
                            issues.append(
                                ValidationIssue(
                                    severity="warning",
                                    category="parameters",
                                    message=f"Parameter '{param_name}' missing description",
                                    line_number=node.lineno,
                                    suggestion='Add description: Field(..., description="...")',
                                )
                            )

        return issues

    def _check_test_block(self, content: str) -> List[ValidationIssue]:
        """Check for test block"""
        issues = []

        if 'if __name__ == "__main__"' not in content:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="testing",
                    message='Missing test block: if __name__ == "__main__"',
                    suggestion="Add test block at end of file for manual testing",
                )
            )
        else:
            # Check if mock mode is set in test block
            test_block_start = content.find('if __name__ == "__main__"')
            test_block = content[test_block_start:]

            if "USE_MOCK_APIS" not in test_block:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="testing",
                        message="Test block doesn't set USE_MOCK_APIS",
                        suggestion='Add: os.environ["USE_MOCK_APIS"] = "true"',
                    )
                )

        return issues

    def _check_error_handling(self, tree: ast.AST, content: str) -> List[ValidationIssue]:
        """Check error handling"""
        issues = []

        # Check if custom exceptions are used
        uses_custom_errors = any(
            error in content
            for error in ["ValidationError", "APIError", "ToolError", "RateLimitError"]
        )

        if not uses_custom_errors:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="error_handling",
                    message="Not using custom error classes",
                    suggestion="Use ValidationError, APIError, etc. from shared.errors",
                )
            )

        return issues

    def _check_supporting_files(self, tool_dir: Path) -> List[ValidationIssue]:
        """Check for supporting files"""
        issues = []

        # Check for test file
        test_files = list(tool_dir.glob("test_*.py"))
        if not test_files:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="testing",
                    message="Missing test file",
                    suggestion=f"Add test_{tool_dir.name}.py",
                )
            )

        # Check for README
        readme_file = tool_dir / "README.md"
        if not readme_file.exists():
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="documentation",
                    message="Missing README.md",
                    suggestion="Add README.md with usage examples",
                )
            )

        # Check for __init__.py
        init_file = tool_dir / "__init__.py"
        if not init_file.exists():
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="structure",
                    message="Missing __init__.py",
                    suggestion="Add __init__.py to make it a proper package",
                )
            )

        return issues

    def _calculate_score(self, issues: List[ValidationIssue]) -> int:
        """Calculate validation score (0-100)"""
        # Start with perfect score
        score = 100

        # Deduct points for issues
        for issue in issues:
            if issue.severity == "error":
                score -= 10
            elif issue.severity == "warning":
                score -= 3
            elif issue.severity == "info":
                score -= 1

        return max(0, score)

    def display_results(self, result: ValidationResult):
        """Display validation results"""

        # Status
        if result.passed:
            status = "[bold green]✓ PASSED[/bold green]"
            status_color = "green"
        else:
            status = "[bold red]✗ FAILED[/bold red]"
            status_color = "red"

        # Summary
        console.print(
            Panel.fit(
                f"{status}\n"
                f"Score: [bold]{result.score}/100[/bold]\n"
                f"Errors: [red]{len(result.errors)}[/red] | "
                f"Warnings: [yellow]{len(result.warnings)}[/yellow]",
                title=f"Validation: {result.tool_path.name}",
                border_style=status_color,
            )
        )

        # Issues table
        if result.issues:
            table = Table(title="Issues", show_header=True, header_style="bold magenta")
            table.add_column("Severity", style="white", width=10)
            table.add_column("Category", style="cyan", width=15)
            table.add_column("Line", style="white", width=6)
            table.add_column("Message", style="white")

            for issue in result.issues:
                severity_style = {
                    "error": "[red]ERROR[/red]",
                    "warning": "[yellow]WARNING[/yellow]",
                    "info": "[blue]INFO[/blue]",
                }.get(issue.severity, issue.severity)

                line_str = str(issue.line_number) if issue.line_number else "-"

                table.add_row(severity_style, issue.category, line_str, issue.message)

                # Show suggestion if available
                if issue.suggestion:
                    table.add_row("", "", "", f"[dim]→ {issue.suggestion}[/dim]")

            console.print(table)

    def display_summary(self, results: Dict[str, ValidationResult]):
        """Display validation summary for multiple tools"""

        total_tools = len(results)
        passed_tools = sum(1 for r in results.values() if r.passed)
        failed_tools = total_tools - passed_tools
        avg_score = sum(r.score for r in results.values()) / total_tools if total_tools > 0 else 0

        console.print(
            Panel.fit(
                f"[bold]Total Tools:[/bold] {total_tools}\n"
                f"[bold green]Passed:[/bold green] {passed_tools}\n"
                f"[bold red]Failed:[/bold red] {failed_tools}\n"
                f"[bold]Average Score:[/bold] {avg_score:.1f}/100",
                title="Validation Summary",
                border_style="cyan",
            )
        )

        # Failed tools
        if failed_tools > 0:
            console.print("\n[bold red]Failed Tools:[/bold red]")
            for name, result in results.items():
                if not result.passed:
                    console.print(
                        f"  • {name}: {len(result.errors)} errors, {len(result.warnings)} warnings"
                    )


# Example usage
if __name__ == "__main__":
    validator = ToolValidator()

    # Test validation on web_search tool
    from pathlib import Path

    tool_path = Path(__file__).parent.parent / "tools/data/search/web_search"

    if tool_path.exists():
        result = validator.validate_tool(tool_path)
        validator.display_results(result)
    else:
        print(f"Tool path not found: {tool_path}")
