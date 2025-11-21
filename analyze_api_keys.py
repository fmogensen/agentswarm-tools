#!/usr/bin/env python3
"""
Analyze all tools to identify required API keys for testing.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def extract_api_keys_from_file(file_path):
    """Extract API key environment variable names from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match patterns like os.getenv("KEY_NAME") or os.environ.get("KEY_NAME")
    patterns = [
        r'os\.getenv\(["\']([A-Z_]+)["\']',
        r'os\.environ\.get\(["\']([A-Z_]+)["\']',
        r'os\.environ\[["\']([A-Z_]+)["\']\]',
    ]

    keys = set()
    for pattern in patterns:
        matches = re.findall(pattern, content)
        keys.update(matches)

    # Filter to likely API keys (exclude common env vars)
    excluded = {'USE_MOCK_APIS', 'DEBUG', 'ENV', 'ENVIRONMENT', 'LOG_LEVEL',
                'PORT', 'HOST', 'DATABASE_URL', 'REDIS_URL'}

    return {k for k in keys if k not in excluded and not k.startswith('TEST_')}

def main():
    """Analyze all tools and categorize by API key requirements."""
    tools_dir = Path("tools")

    # Category -> Tool -> API Keys
    results = defaultdict(lambda: defaultdict(set))

    # All unique API keys needed
    all_keys = set()

    for tool_file in tools_dir.rglob("*.py"):
        # Skip test files, __init__, and examples
        if (tool_file.name.startswith("test_") or
            tool_file.name.startswith("__") or
            "_examples" in str(tool_file)):
            continue

        # Extract category and tool name
        parts = tool_file.parts
        if len(parts) >= 3:
            category = parts[1]
            tool_name = parts[2]

            keys = extract_api_keys_from_file(tool_file)
            if keys:
                results[category][tool_name].update(keys)
                all_keys.update(keys)

    # Print results
    print("=" * 80)
    print("API KEYS NEEDED FOR LIVE TESTING")
    print("=" * 80)
    print()

    # Summary of all unique keys
    print("📋 ALL REQUIRED API KEYS:")
    print("-" * 80)
    for key in sorted(all_keys):
        print(f"  • {key}")
    print()
    print(f"Total: {len(all_keys)} unique API keys")
    print()

    # Breakdown by category
    print("=" * 80)
    print("BREAKDOWN BY CATEGORY")
    print("=" * 80)
    print()

    for category in sorted(results.keys()):
        tools = results[category]
        print(f"📁 {category.upper()}")
        print("-" * 80)

        for tool_name in sorted(tools.keys()):
            keys = tools[tool_name]
            print(f"  {tool_name}:")
            for key in sorted(keys):
                print(f"    • {key}")
        print()

    # Group tools by API key
    print("=" * 80)
    print("TOOLS GROUPED BY API KEY")
    print("=" * 80)
    print()

    key_to_tools = defaultdict(list)
    for category, tools in results.items():
        for tool_name, keys in tools.items():
            for key in keys:
                key_to_tools[key].append(f"{category}/{tool_name}")

    for key in sorted(key_to_tools.keys()):
        tools = key_to_tools[key]
        print(f"🔑 {key}")
        print(f"   Used by {len(tools)} tool(s):")
        for tool in sorted(tools):
            print(f"     - {tool}")
        print()

if __name__ == "__main__":
    main()
