#!/usr/bin/env python3
"""
Script to convert all print() statements to proper logging calls.

This script:
1. Finds all .py files in tools/ with print() statements
2. Adds logging import and logger setup
3. Replaces print() with appropriate logger calls
4. Preserves print() in docstrings, comments, and test blocks
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class PrintToLoggingConverter:
    """Converts print() statements to logging calls."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.stats = {
            "files_modified": 0,
            "files_skipped": 0,
            "prints_replaced": 0,
            "files_with_errors": [],
            "modified_files": [],
        }

    def should_skip_line(self, line: str, in_test_block: bool) -> bool:
        """Check if line should be skipped (comments, docstrings, test blocks)."""
        stripped = line.strip()

        # Skip comments
        if stripped.startswith("#"):
            return True

        # Skip test blocks
        if in_test_block:
            return True

        # Skip if print is in a string
        if "print(" in line:
            # Check if it's in a docstring or comment
            before_print = line.split("print(")[0]
            if '"""' in before_print or "'''" in before_print or "#" in before_print:
                return True

        return False

    def determine_log_level(self, print_content: str) -> str:
        """Determine appropriate log level based on print content."""
        content_lower = print_content.lower()

        # Error indicators
        if any(
            word in content_lower
            for word in ["error", "exception", "failed", "failure", "critical"]
        ):
            return "error"

        # Warning indicators
        if any(word in content_lower for word in ["warning", "warn", "deprecated", "caution"]):
            return "warning"

        # Debug indicators
        if any(word in content_lower for word in ["debug", "verbose", "trace", "dump"]):
            return "debug"

        # Success/info indicators (default)
        return "info"

    def extract_print_content(self, line: str) -> Tuple[str, str]:
        """Extract content from print() statement."""
        # Match print(...) including multi-line
        match = re.search(r"print\((.*)\)", line)
        if match:
            content = match.group(1)
            return content, line[: match.start()]
        return None, None

    def convert_print_to_logger(self, line: str, indent: str) -> str:
        """Convert a single print() statement to logger call."""
        content, prefix = self.extract_print_content(line)
        if content is None:
            return line

        # Determine log level
        log_level = self.determine_log_level(content)

        # Handle f-strings and regular strings
        if content.strip().startswith('f"') or content.strip().startswith("f'"):
            # Already an f-string
            log_content = content.strip()
        elif "," in content or "%" in content:
            # Multiple args or string formatting - convert to f-string
            # This is a simplified conversion; complex cases may need manual review
            log_content = content.strip()
        else:
            # Simple string
            log_content = content.strip()

        # Create logger call
        return f"{prefix}logger.{log_level}({log_content})\n"

    def has_logging_import(self, content: str) -> bool:
        """Check if file already has logging import."""
        return "from shared.logging import get_logger" in content

    def add_logging_import(self, lines: List[str]) -> List[str]:
        """Add logging import at the top of the file."""
        # Find the right place to insert (after other imports)
        insert_idx = 0
        in_docstring = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track docstrings
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue

            if in_docstring:
                continue

            # Find last import statement
            if stripped.startswith("import ") or stripped.startswith("from "):
                insert_idx = i + 1

        # Insert logging import
        if insert_idx > 0:
            lines.insert(insert_idx, "\nfrom shared.logging import get_logger\n")

        return lines

    def add_logger_setup(self, lines: List[str]) -> List[str]:
        """Add logger = get_logger(__name__) after imports or at module level."""
        # Find where to add logger setup
        insert_idx = 0
        in_docstring = False
        last_import_idx = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track docstrings
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue

            if in_docstring:
                continue

            # Find last import
            if stripped.startswith("import ") or stripped.startswith("from "):
                last_import_idx = i

            # Look for class definition (add logger inside class)
            if stripped.startswith("class ") and "BaseTool" in stripped:
                # Add logger inside class, after docstring
                class_start = i
                for j in range(i + 1, len(lines)):
                    if '"""' in lines[j] and lines[j].count('"""') == 2:
                        # Single-line docstring
                        insert_idx = j + 1
                        break
                    elif '"""' in lines[j]:
                        # Multi-line docstring - find end
                        for k in range(j + 1, len(lines)):
                            if '"""' in lines[k]:
                                insert_idx = k + 1
                                break
                        break
                    elif not lines[j].strip().startswith("#") and lines[j].strip():
                        # First non-comment, non-blank line
                        insert_idx = j
                        break
                break

        # If no class found, add after imports
        if insert_idx == 0:
            insert_idx = last_import_idx + 1

        # Add logger setup with proper indentation
        indent = "    " if "class " in "".join(lines[:insert_idx]) else ""
        lines.insert(insert_idx, f"\n{indent}logger = get_logger(__name__)\n")

        return lines

    def convert_file(self, file_path: Path) -> bool:
        """Convert a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if already has logging
            if self.has_logging_import(content):
                print(f"Skipping {file_path.name} - already has logging import")
                self.stats["files_skipped"] += 1
                return False

            lines = content.split("\n")
            modified = False
            in_test_block = False
            print_count = 0

            # Process each line
            new_lines = []
            for i, line in enumerate(lines):
                # Track test blocks
                if 'if __name__ == "__main__":' in line:
                    in_test_block = True

                # Skip certain lines
                if self.should_skip_line(line, in_test_block):
                    new_lines.append(line)
                    continue

                # Check for print statements
                if "print(" in line and not line.strip().startswith("#"):
                    # Get indentation
                    indent = line[: len(line) - len(line.lstrip())]

                    # Convert print to logger
                    new_line = self.convert_print_to_logger(line, indent)
                    new_lines.append(new_line.rstrip("\n"))
                    modified = True
                    print_count += 1
                else:
                    new_lines.append(line)

            if not modified:
                self.stats["files_skipped"] += 1
                return False

            # Add logging import and logger setup
            new_lines = self.add_logging_import(new_lines)
            new_lines = self.add_logger_setup(new_lines)

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))

            self.stats["files_modified"] += 1
            self.stats["prints_replaced"] += print_count
            self.stats["modified_files"].append(str(file_path))

            print(f"✓ Converted {file_path.name}: {print_count} print statements")
            return True

        except Exception as e:
            print(f"✗ Error processing {file_path.name}: {e}")
            self.stats["files_with_errors"].append(str(file_path))
            return False

    def find_files_with_prints(self) -> List[Path]:
        """Find all Python files in tools/ with print statements."""
        files = []
        tools_dir = self.base_dir / "tools"

        for py_file in tools_dir.rglob("*.py"):
            # Skip __init__.py files
            if py_file.name == "__init__.py":
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if (
                        "print(" in content
                        and "from shared.logging import get_logger" not in content
                    ):
                        files.append(py_file)
            except Exception as e:
                print(f"Error reading {py_file}: {e}")

        return files

    def run(self) -> Dict:
        """Run the conversion process."""
        print("Finding files with print() statements...")
        files = self.find_files_with_prints()

        print(f"\nFound {len(files)} files to process\n")
        print("=" * 70)

        for file_path in files:
            self.convert_file(file_path)

        print("\n" + "=" * 70)
        print("\nConversion Summary:")
        print(f"  Files modified: {self.stats['files_modified']}")
        print(f"  Files skipped: {self.stats['files_skipped']}")
        print(f"  Total print() statements replaced: {self.stats['prints_replaced']}")
        print(f"  Files with errors: {len(self.stats['files_with_errors'])}")

        if self.stats["files_with_errors"]:
            print("\nFiles with errors:")
            for f in self.stats["files_with_errors"]:
                print(f"  - {f}")

        return self.stats


def main():
    """Main entry point."""
    # Get repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    print(f"Repository root: {repo_root}")
    print(f"Converting print() to logging in tools/ directory...\n")

    converter = PrintToLoggingConverter(repo_root)
    stats = converter.run()

    # Exit with error code if there were errors
    if stats["files_with_errors"]:
        sys.exit(1)

    print("\n✓ Conversion complete!")
    sys.exit(0)


if __name__ == "__main__":
    main()
