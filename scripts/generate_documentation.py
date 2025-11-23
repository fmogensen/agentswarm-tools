#!/usr/bin/env python3
"""
Generate comprehensive documentation for all AgentSwarm tools.

This script creates:
1. Root-level documentation (TOOLS_INDEX.md, TOOLS_DOCUMENTATION.md, TOOL_EXAMPLES.md)
2. Category-level README files
3. Individual tool README files

Sources:
- Reference documentation from Genspark/ directory
- Tool Python code and docstrings
- Existing examples
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
GENSPARK_REF = PROJECT_ROOT.parent / "Genspark"
TOOLS_DIR = PROJECT_ROOT / "tools"

# Tool categories
CATEGORIES = {
    "search": "Search & Information Retrieval",
    "web_content": "Web Content & Data Access",
    "web": "Web Content & Data Access",
    "media_generation": "Media Generation",
    "media_analysis": "Media Analysis & Processing",
    "storage": "File & Storage Management",
    "communication": "Communication & Productivity",
    "visualization": "Data Visualization",
    "location": "Location Services",
    "code_execution": "Code Execution Environment",
    "document_creation": "Document & Content Creation",
    "workspace": "Workspace Integration",
    "utils": "Utility Tools",
}

# All 101 tools
ALL_TOOLS = [
    ("web_search", "search"),
    ("scholar_search", "search"),
    ("image_search", "search"),
    ("video_search", "search"),
    ("product_search", "search"),
    ("google_product_search", "search"),
    ("financial_report", "search"),
    ("stock_price", "search"),
    ("crawler", "web_content"),
    ("summarize_large_document", "web_content"),
    ("url_metadata", "web_content"),
    ("webpage_capture_screen", "web_content"),
    ("resource_discovery", "web"),
    ("image_generation", "media_generation"),
    ("video_generation", "media_generation"),
    ("audio_generation", "media_generation"),
    ("understand_images", "media_analysis"),
    ("understand_video", "media_analysis"),
    ("batch_understand_videos", "media_analysis"),
    ("analyze_media_content", "media_analysis"),
    ("audio_transcribe", "media_analysis"),
    ("merge_audio", "media_analysis"),
    ("extract_audio_from_video", "media_analysis"),
    ("aidrive_tool", "storage"),
    ("file_format_converter", "storage"),
    ("onedrive_search", "storage"),
    ("onedrive_file_read", "storage"),
    ("gmail_search", "communication"),
    ("gmail_read", "communication"),
    ("read_email_attachments", "communication"),
    ("email_draft", "communication"),
    ("google_calendar_list", "communication"),
    ("google_calendar_create_event_draft", "communication"),
    ("phone_call", "communication"),
    ("query_call_logs", "communication"),
    ("generate_line_chart", "visualization"),
    ("generate_bar_chart", "visualization"),
    ("generate_column_chart", "visualization"),
    ("generate_pie_chart", "visualization"),
    ("generate_area_chart", "visualization"),
    ("generate_scatter_chart", "visualization"),
    ("generate_dual_axes_chart", "visualization"),
    ("generate_histogram_chart", "visualization"),
    ("generate_radar_chart", "visualization"),
    ("generate_treemap_chart", "visualization"),
    ("generate_word_cloud_chart", "visualization"),
    ("generate_fishbone_diagram", "visualization"),
    ("generate_flow_diagram", "visualization"),
    ("generate_mind_map", "visualization"),
    ("generate_network_graph", "visualization"),
    ("maps_search", "location"),
    ("bash_tool", "code_execution"),
    ("read_tool", "code_execution"),
    ("write_tool", "code_execution"),
    ("multiedit_tool", "code_execution"),
    ("downloadfilewrapper_tool", "code_execution"),
    ("create_agent", "document_creation"),
    ("notion_search", "workspace"),
    ("notion_read", "workspace"),
    ("think", "utils"),
    ("ask_for_clarification", "utils"),
]


def extract_tool_info(tool_path: Path) -> Dict:
    """Extract tool information from Python file."""
    try:
        with open(tool_path, "r") as f:
            content = f.read()

        # Extract class docstring
        docstring_match = re.search(r'class \w+\(BaseTool\):\s+"""([^"]+)"""', content, re.DOTALL)
        description = docstring_match.group(1).strip() if docstring_match else ""

        # Extract tool_name and tool_category
        tool_name_match = re.search(r'tool_name:\s*str\s*=\s*"([^"]+)"', content)
        tool_category_match = re.search(r'tool_category:\s*str\s*=\s*"([^"]+)"', content)

        tool_name = tool_name_match.group(1) if tool_name_match else ""
        tool_category = tool_category_match.group(1) if tool_category_match else ""

        # Extract parameters
        params = []
        param_pattern = r"(\w+):\s*\w+\s*=\s*Field\(([^)]+)\)"
        for match in re.finditer(param_pattern, content):
            param_name = match.group(1)
            param_def = match.group(2)
            desc_match = re.search(r'description="([^"]+)"', param_def)
            param_desc = desc_match.group(1) if desc_match else ""
            params.append((param_name, param_desc))

        return {
            "name": tool_name,
            "category": tool_category,
            "description": description.split("\n")[0] if description else "",
            "full_description": description,
            "parameters": params,
        }
    except Exception as e:
        print(f"Warning: Could not parse {tool_path}: {e}")
        return {}


def copy_reference_docs():
    """Copy reference documentation to agentswarm-tools root."""
    print("📋 Copying reference documentation...")

    ref_files = [
        ("TOOLS_INDEX.md", "TOOLS_INDEX.md"),
        ("genspark_tools_documentation.md", "TOOLS_DOCUMENTATION.md"),
        ("tool_examples_complete.md", "TOOL_EXAMPLES.md"),
    ]

    for src_name, dst_name in ref_files:
        src = GENSPARK_REF / src_name
        dst = PROJECT_ROOT / dst_name

        if src.exists():
            with open(src, "r") as f:
                content = f.read()
            with open(dst, "w") as f:
                f.write(content)
            print(f"  ✅ Created {dst_name}")
        else:
            print(f"  ⚠️  Source not found: {src}")


def generate_category_readmes():
    """Generate README.md for each category directory."""
    print("\n📁 Generating category README files...")

    # Group tools by category
    category_tools = {}
    for tool_name, category in ALL_TOOLS:
        if category not in category_tools:
            category_tools[category] = []
        category_tools[category].append(tool_name)

    for category, tools in category_tools.items():
        category_path = TOOLS_DIR / category
        if not category_path.exists():
            continue

        readme_path = category_path / "README.md"
        category_title = CATEGORIES.get(category, category.replace("_", " ").title())

        content = f"""# {category_title}

This directory contains tools for {category_title.lower()}.

## Tools in This Category

"""

        for tool_name in sorted(tools):
            # Find tool file
            tool_dir = category_path / tool_name
            tool_file = tool_dir / f"{tool_name}.py"

            if tool_file.exists():
                info = extract_tool_info(tool_file)
                desc = info.get("description", "No description available")
                content += f"### {tool_name}\n\n{desc}\n\n"

        content += f"""## Usage

Each tool follows the Agency Swarm BaseTool pattern:

```python
from tools.{category}.tool_name import ToolName

tool = ToolName(param1="value1", param2="value2")
result = tool.run()
```

## Documentation

See individual tool READMEs for detailed documentation:
"""

        for tool_name in sorted(tools):
            content += f"- [{tool_name}](./{tool_name}/README.md)\n"

        with open(readme_path, "w") as f:
            f.write(content)

        print(f"  ✅ Created {category}/README.md ({len(tools)} tools)")


def generate_tool_readmes():
    """Generate README.md for each individual tool."""
    print("\n🔧 Generating individual tool README files...")

    count = 0
    for tool_name, category in ALL_TOOLS:
        category_path = TOOLS_DIR / category
        tool_dir = category_path / tool_name
        tool_file = tool_dir / f"{tool_name}.py"

        if not tool_file.exists():
            print(f"  ⚠️  Tool file not found: {tool_file}")
            continue

        # Extract tool information
        info = extract_tool_info(tool_file)

        # Generate README
        readme_path = tool_dir / "README.md"

        content = f"""# {tool_name}

{info.get('full_description', info.get('description', 'No description available'))}

## Category

{CATEGORIES.get(category, category.replace('_', ' ').title())}

## Parameters

"""

        if info.get("parameters"):
            for param_name, param_desc in info["parameters"]:
                content += f"- **{param_name}**: {param_desc}\n"
        else:
            content += "No parameters documented.\n"

        content += f"""

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.{category}.{tool_name} import {tool_name.replace('_', ' ').title().replace(' ', '')}

# Initialize the tool
tool = {tool_name.replace('_', ' ').title().replace(' ', '')}(
"""

        if info.get("parameters"):
            for i, (param_name, _) in enumerate(info["parameters"][:2]):
                content += f'    {param_name}="example_value"'
                if i < min(len(info["parameters"]), 2) - 1:
                    content += ","
                content += "\n"

        content += f""")

# Run the tool
result = tool.run()

# Check result
if result["success"]:
    print(result["result"])
else:
    print(f"Error: {{result.get('error')}}")
```

## Testing

Run tests with:
```bash
pytest tools/{category}/{tool_name}/test_{tool_name}.py -v
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../TOOLS_DOCUMENTATION.md)
- [Examples](../../../TOOL_EXAMPLES.md)
- [Category Overview](../README.md)
"""

        with open(readme_path, "w") as f:
            f.write(content)

        count += 1

    print(f"  ✅ Created {count} tool README files")


def main():
    """Main documentation generation function."""
    print("🚀 AgentSwarm Tools - Documentation Generation")
    print("=" * 70)

    # Phase 1: Copy reference docs to root
    copy_reference_docs()

    # Phase 2: Generate category READMEs
    generate_category_readmes()

    # Phase 3: Generate individual tool READMEs
    generate_tool_readmes()

    print("\n" + "=" * 70)
    print("✅ Documentation generation complete!")
    print(f"\n📊 Summary:")
    print(f"   - 3 root-level documentation files")
    print(f"   - {len(set(cat for _, cat in ALL_TOOLS))} category README files")
    print(f"   - {len(ALL_TOOLS)} individual tool README files")
    print(
        f"\n📁 Total: ~{3 + len(set(cat for _, cat in ALL_TOOLS)) + len(ALL_TOOLS)} documentation files created"
    )


if __name__ == "__main__":
    main()
