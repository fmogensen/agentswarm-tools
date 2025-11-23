#!/usr/bin/env python3
"""
Generate README.md files for tools that are missing them
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any


def extract_tool_info(tool_file_path: str) -> Dict[str, Any]:
    """Extract tool information from Python file"""
    with open(tool_file_path, "r") as f:
        content = f.read()

    # Extract class name
    class_match = re.search(r"class\s+(\w+)\(BaseTool\)", content)
    class_name = class_match.group(1) if class_match else "Unknown"

    # Extract docstring
    docstring_match = re.search(r'class\s+\w+\(BaseTool\):\s+"""(.*?)"""', content, re.DOTALL)
    docstring = docstring_match.group(1).strip() if docstring_match else ""

    # Extract tool_name and tool_category
    tool_name_match = re.search(r'tool_name:\s*str\s*=\s*"([^"]+)"', content)
    tool_name = tool_name_match.group(1) if tool_name_match else Path(tool_file_path).stem

    tool_category_match = re.search(r'tool_category:\s*str\s*=\s*"([^"]+)"', content)
    tool_category = tool_category_match.group(1) if tool_category_match else "unknown"

    # Extract parameters with Field descriptions
    parameters = []
    field_pattern = r'(\w+):\s*([^=]+?)\s*=\s*Field\((.*?)\)'

    for match in re.finditer(field_pattern, content, re.DOTALL):
        param_name = match.group(1)
        param_type = match.group(2).strip()
        field_args = match.group(3)

        # Skip tool_name and tool_category
        if param_name in ['tool_name', 'tool_category']:
            continue

        # Extract description
        desc_match = re.search(r'description\s*=\s*"([^"]+)"', field_args)
        description = desc_match.group(1) if desc_match else "No description"

        # Check if required (has ... as first arg)
        is_required = field_args.strip().startswith("...")

        parameters.append({
            'name': param_name,
            'type': param_type,
            'description': description,
            'required': is_required
        })

    # Extract example from docstring or test block
    example = ""
    if "Example:" in docstring:
        example_match = re.search(r'Example:\s*(.+?)(?:\n\s*\n|\Z)', docstring, re.DOTALL)
        example = example_match.group(1).strip() if example_match else ""

    return {
        'class_name': class_name,
        'tool_name': tool_name,
        'category': tool_category,
        'docstring': docstring,
        'parameters': parameters,
        'example': example
    }


def generate_readme_content(tool_info: Dict[str, Any], tool_dir: str) -> str:
    """Generate README.md content from tool info"""

    # Extract brief description from docstring (first line or first paragraph)
    docstring = tool_info['docstring']
    brief_description = ""

    if docstring:
        # Try to get first non-empty line that's not Args/Returns/Example
        lines = docstring.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('Args:', 'Returns:', 'Example:', 'Raises:')):
                brief_description = line
                break

    if not brief_description:
        brief_description = f"Tool for {tool_info['tool_name'].replace('_', ' ')}"

    # Determine category display name
    category_map = {
        'communication': 'Communication & Productivity',
        'data': 'Data & Search',
        'media': 'Media Generation & Analysis',
        'visualization': 'Data Visualization',
        'content': 'Content Creation',
        'infrastructure': 'Infrastructure & Code Execution',
        'utils': 'Utilities',
        'integrations': 'External Integrations'
    }
    category_display = category_map.get(tool_info['category'], tool_info['category'].title())

    # Build README content
    content = f"# {tool_info['tool_name']}\n\n"
    content += f"{brief_description}\n\n"
    content += f"## Category\n\n{category_display}\n\n"

    # Parameters section
    content += "## Parameters\n\n"
    if tool_info['parameters']:
        for param in tool_info['parameters']:
            required_text = "**Required**" if param['required'] else "Optional"
            content += f"- **{param['name']}** ({param['type'].replace('Optional[', '').replace(']', '')}): {param['description']} - {required_text}\n"
    else:
        content += "No parameters.\n"
    content += "\n"

    # Returns section
    content += "## Returns\n\n"
    content += "Returns a dictionary with:\n"
    content += "- `success` (bool): Whether the operation succeeded\n"
    content += "- `result` (dict): Tool-specific results\n"
    content += "- `metadata` (dict): Additional information about the operation\n\n"

    # Usage Example section
    content += "## Usage Example\n\n"
    content += "```python\n"
    content += f"from {get_import_path(tool_dir)} import {tool_info['class_name']}\n\n"
    content += "# Initialize the tool\n"
    content += f"tool = {tool_info['class_name']}(\n"

    if tool_info['parameters']:
        for i, param in enumerate(tool_info['parameters'][:3]):  # Show first 3 params
            comma = "," if i < min(2, len(tool_info['parameters']) - 1) else ""
            if param['required']:
                content += f"    {param['name']}=\"example_value\"{comma}\n"
            else:
                content += f"    {param['name']}=\"example_value\"{comma}  # Optional\n"
    content += ")\n\n"
    content += "# Run the tool\n"
    content += "result = tool.run()\n\n"
    content += "# Check result\n"
    content += "if result[\"success\"]:\n"
    content += "    print(result[\"result\"])\n"
    content += "else:\n"
    content += "    print(f\"Error: {result.get('error')}\")\n"
    content += "```\n\n"

    # Testing section
    content += "## Testing\n\n"
    content += "Run tests with:\n"
    content += "```bash\n"
    content += f"python {tool_info['tool_name']}.py  # Run standalone test\n"
    content += "```\n\n"

    # Documentation links
    content += "## Documentation\n\n"
    content += "- [Tool Index](../../../TOOLS_INDEX.md)\n"
    content += "- [Complete Documentation](../../../genspark_tools_documentation.md)\n"
    content += "- [Examples](../../../tool_examples_complete.md)\n"

    # Add category README if not in root
    depth = get_depth_from_tools_dir(tool_dir)
    if depth > 1:
        content += f"- [Category Overview]({'../' * (depth - 1)}README.md)\n"

    return content


def get_import_path(tool_dir: str) -> str:
    """Generate import path from tool directory"""
    parts = Path(tool_dir).parts
    tools_index = parts.index('tools')
    import_parts = parts[tools_index:]
    return '.'.join(import_parts)


def get_depth_from_tools_dir(tool_dir: str) -> int:
    """Get depth of directory from tools/ directory"""
    parts = Path(tool_dir).parts
    tools_index = parts.index('tools')
    return len(parts) - tools_index - 1


def main():
    base_path = "/Users/frank/Documents/Code/Genspark/agentswarm-tools"

    # Load audit results
    audit_file = Path(base_path) / "tool_readme_audit.json"
    with open(audit_file, 'r') as f:
        audit_data = json.load(f)

    tools_without_readme = audit_data['tools_without_readme']

    print("=" * 80)
    print("README GENERATION REPORT")
    print("=" * 80)
    print()

    created_count = 0
    failed_count = 0

    for tool in tools_without_readme:
        tool_file = tool['file']
        tool_dir = tool['dir']
        readme_path = Path(tool['readme_path'])

        try:
            # Extract tool information
            tool_info = extract_tool_info(tool_file)

            # Generate README content
            readme_content = generate_readme_content(tool_info, tool_dir)

            # Write README file
            with open(readme_path, 'w') as f:
                f.write(readme_content)

            print(f"✓ Created: {readme_path}")
            created_count += 1

        except Exception as e:
            print(f"✗ Failed: {tool['name']} - {e}")
            failed_count += 1

    print()
    print("=" * 80)
    print(f"Created: {created_count} README files")
    print(f"Failed: {failed_count} README files")
    print("=" * 80)


if __name__ == "__main__":
    main()
