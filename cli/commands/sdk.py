"""
SDK commands for tool development.

Provides commands for creating, validating, and documenting tools.
"""

from pathlib import Path
from rich.console import Console
from rich.progress import Progress

from sdk.generator import ToolGenerator
from sdk.validator import ToolValidator
from sdk.test_generator import TestGenerator
from sdk.docs_generator import DocsGenerator

console = Console()


def execute(args):
    """Execute SDK commands based on args"""

    if args.sdk_command == "create-tool":
        return create_tool(args)
    elif args.sdk_command == "validate-tool":
        return validate_tool(args)
    elif args.sdk_command == "validate-all":
        return validate_all(args)
    elif args.sdk_command == "generate-tests":
        return generate_tests(args)
    elif args.sdk_command == "generate-docs":
        return generate_docs(args)
    elif args.sdk_command == "quick-start":
        return quick_start(args)
    else:
        console.print("[red]Unknown SDK command[/red]")
        return 1


def create_tool(args):
    """Create a new tool with scaffolding"""
    generator = ToolGenerator()

    if args.interactive or not args.tool_name:
        # Interactive mode
        result = generator.generate_tool_interactive()
    else:
        # CLI mode
        if not args.category or not args.description:
            console.print("[red]Error: --category and --description required in CLI mode[/red]")
            console.print("Use --interactive flag for interactive wizard")
            return 1

        result = generator.generate_tool_cli(
            tool_name=args.tool_name,
            category=args.category,
            description=args.description,
            subcategory=getattr(args, 'subcategory', None),
            requires_api_key=getattr(args, 'api_key', False),
            api_key_env_var=getattr(args, 'api_key_var', None),
        )

    console.print(f"\n[green]✓ Tool created: {result['tool_name']}[/green]")
    console.print(f"Location: {result['tool_path']}")
    return 0


def validate_tool(args):
    """Validate a tool against Agency Swarm standards"""
    validator = ToolValidator()
    tool_path = Path(args.tool_path)

    result = validator.validate_tool(tool_path)
    validator.display_results(result)

    if args.verbose and result.issues:
        console.print("\n[bold]Detailed Issues:[/bold]")
        for issue in result.issues:
            console.print(f"\n[{issue.severity.upper()}] {issue.category}:")
            console.print(f"  {issue.message}")
            if issue.suggestion:
                console.print(f"  → {issue.suggestion}")

    return 0 if result.passed else 1


def validate_all(args):
    """Validate all tools in the tools directory"""
    validator = ToolValidator()
    tools_dir = Path(getattr(args, 'tools_dir', 'tools'))
    min_score = getattr(args, 'min_score', 70)

    console.print(f"[bold]Validating all tools in {tools_dir}...[/bold]\n")

    results = validator.validate_all_tools(tools_dir)

    # Display summary
    validator.display_summary(results)

    # Show tools below minimum score
    below_min = {name: r for name, r in results.items() if r.score < min_score}

    if below_min:
        console.print(f"\n[yellow]Tools below minimum score ({min_score}):[/yellow]")
        for name, result in below_min.items():
            console.print(f"  • {name}: {result.score}/100")

    return 0


def generate_tests(args):
    """Generate comprehensive tests for a tool"""
    generator = TestGenerator()
    tool_path = Path(args.tool_path)

    # If directory, find tool file
    if tool_path.is_dir():
        tool_file = None
        for file in tool_path.glob("*.py"):
            if not file.name.startswith("test_") and file.name != "__init__.py":
                tool_file = file
                break

        if not tool_file:
            console.print(f"[red]No tool file found in {tool_path}[/red]")
            return 1

        tool_path = tool_file

    test_file = generator.generate_tests(tool_path)
    console.print(f"[green]✓ Generated test file: {test_file}[/green]")
    return 0


def generate_docs(args):
    """Generate documentation for tools"""
    generator = DocsGenerator()

    if getattr(args, 'index', False):
        # Update TOOLS_INDEX.md
        tools_dir = Path("tools")
        index_file = generator.update_tools_index(tools_dir)
        console.print(f"[green]✓ Updated TOOLS_INDEX: {index_file}[/green]")

    elif getattr(args, 'category', None):
        # Generate category README
        category_dir = Path("tools") / args.category
        if not category_dir.exists():
            console.print(f"[red]Category directory not found: {category_dir}[/red]")
            return 1

        readme_file = generator.generate_category_docs(category_dir)
        console.print(f"[green]✓ Generated category README: {readme_file}[/green]")

    elif getattr(args, 'all_tools', False):
        # Generate for all tools
        tools_dir = Path("tools")
        count = 0

        for category_dir in tools_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("."):
                continue

            for subcategory_dir in category_dir.iterdir():
                if not subcategory_dir.is_dir() or subcategory_dir.name.startswith("."):
                    continue

                for tool_dir in subcategory_dir.iterdir():
                    if not tool_dir.is_dir() or tool_dir.name.startswith("."):
                        continue

                    # Find tool file
                    tool_file = None
                    for file in tool_dir.glob("*.py"):
                        if not file.name.startswith("test_") and file.name != "__init__.py":
                            tool_file = file
                            break

                    if tool_file:
                        readme_file = generator.generate_readme(tool_file)
                        count += 1

        console.print(f"[green]✓ Generated {count} README files[/green]")

    elif args.tool_path:
        # Generate for specific tool
        tool_path = Path(args.tool_path)

        # If directory, find tool file
        if tool_path.is_dir():
            tool_file = None
            for file in tool_path.glob("*.py"):
                if not file.name.startswith("test_") and file.name != "__init__.py":
                    tool_file = file
                    break

            if not tool_file:
                console.print(f"[red]No tool file found in {tool_path}[/red]")
                return 1

            tool_path = tool_file

        readme_file = generator.generate_readme(tool_path)
        console.print(f"[green]✓ Generated README: {readme_file}[/green]")

    else:
        console.print("[yellow]Please specify a tool path or use --all/--index[/yellow]")
        console.print("Examples:")
        console.print("  agentswarm sdk generate-docs tools/data/search/web_search/")
        console.print("  agentswarm sdk generate-docs --all")
        console.print("  agentswarm sdk generate-docs --index")

    return 0


def quick_start(args):
    """Quick start: Create tool, generate tests, and validate"""

    with Progress() as progress:
        task = progress.add_task("[cyan]Creating tool...", total=4)

        # 1. Create tool
        generator = ToolGenerator()
        result = generator.generate_tool_cli(
            tool_name=args.tool_name,
            category=args.category,
            description=f"Auto-generated tool: {args.tool_name}",
        )
        progress.update(task, advance=1)

        # 2. Generate tests
        test_gen = TestGenerator()
        tool_file = Path(result["tool_path"]) / f"{result['tool_name']}.py"
        test_gen.generate_tests(tool_file)
        progress.update(task, advance=1)

        # 3. Generate docs
        docs_gen = DocsGenerator()
        docs_gen.generate_readme(tool_file)
        progress.update(task, advance=1)

        # 4. Validate
        validator = ToolValidator()
        validation_result = validator.validate_tool(Path(result["tool_path"]))
        progress.update(task, advance=1)

    console.print(f"\n[green]✓ Tool {args.tool_name} created and validated![/green]")
    console.print(f"Location: {result['tool_path']}")
    console.print(f"Validation Score: {validation_result.score}/100")

    if not validation_result.passed:
        console.print("\n[yellow]Validation issues:[/yellow]")
        for issue in validation_result.errors[:3]:
            console.print(f"  • {issue.message}")

    return 0
