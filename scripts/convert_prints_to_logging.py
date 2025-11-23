#!/usr/bin/env python3
"""
Automated script to convert print() statements to logging calls across the tools/ directory.

This script:
1. Finds all Python files with print() statements (excluding test blocks)
2. Adds logging import and logger setup if not present
3. Replaces print() calls with appropriate logger.{level}() calls
4. Preserves print() in docstrings, comments, and test blocks

Usage:
    python scripts/convert_prints_to_logging.py [--dry-run] [--verbose]
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PrintToLoggingConverter:
    """Converts print() statements to proper logging calls."""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        """
        Initialize converter.

        Args:
            dry_run: If True, show changes without modifying files
            verbose: If True, show detailed progress
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "files_skipped": 0,
            "prints_replaced": 0,
            "errors": [],
            "modified_files": [],
        }

    def log(self, message: str, level: str = "INFO") -> None:
        """Print log message if verbose mode enabled."""
        if self.verbose or level == "ERROR":
            prefix = "  " if level == "INFO" else ""
            print(f"{prefix}{message}")

    def determine_log_level(self, content: str) -> str:
        """
        Determine appropriate log level based on print content.

        Args:
            content: The content being printed

        Returns:
            Log level string (info, debug, warning, error)
        """
        content_lower = content.lower()

        # Error indicators
        error_keywords = [
            "error",
            "exception",
            "failed",
            "failure",
            "critical",
            "fatal",
        ]
        if any(keyword in content_lower for keyword in error_keywords):
            return "error"

        # Warning indicators
        warning_keywords = ["warning", "warn", "deprecated", "caution", "alert"]
        if any(keyword in content_lower for keyword in warning_keywords):
            return "warning"

        # Debug indicators
        debug_keywords = ["debug", "verbose", "trace", "dump", "inspect"]
        if any(keyword in content_lower for keyword in debug_keywords):
            return "debug"

        # Default to info for general messages
        return "info"

    def is_in_test_block(self, lines: List[str], line_idx: int) -> bool:
        """
        Check if a line is within a test block (if __name__ == "__main__":).

        Args:
            lines: All lines in the file
            line_idx: Index of current line

        Returns:
            True if line is in test block
        """
        # Search backwards for test block marker
        for i in range(line_idx, -1, -1):
            line = lines[i].strip()
            if 'if __name__ == "__main__":' in line or "if __name__ == '__main__':" in line:
                return True
            # If we hit a class or function definition, we're not in test block
            if line.startswith("class ") or (line.startswith("def ") and i < line_idx):
                return False
        return False

    def should_skip_line(self, line: str, stripped_line: str) -> bool:
        """
        Check if line should be skipped (comments, docstrings).

        Args:
            line: Full line with whitespace
            stripped_line: Stripped line

        Returns:
            True if line should be skipped
        """
        # Skip comments
        if stripped_line.startswith("#"):
            return True

        # Skip if print is in a docstring or string literal
        # Simple heuristic: check if there are quotes before print
        before_print = line.split("print(")[0] if "print(" in line else line
        if '"""' in before_print or "'''" in before_print or '"print' in line or "'print" in line:
            return True

        return False

    def extract_print_arguments(self, line: str) -> Optional[str]:
        """
        Extract arguments from print() statement.

        Handles simple cases. Complex multi-line prints are preserved.

        Args:
            line: Line containing print()

        Returns:
            Print arguments or None if can't parse
        """
        # Match print(...) - handle simple single-line cases
        match = re.search(r"print\((.*)\)\s*$", line)
        if match:
            return match.group(1)
        return None

    def convert_print_to_logger(self, line: str, indent: str, content: str) -> str:
        """
        Convert a print() statement to logger call.

        Args:
            line: Original line
            indent: Leading whitespace
            content: Content extracted from print()

        Returns:
            Converted line with logger call
        """
        # Determine log level
        log_level = self.determine_log_level(content)

        # Build logger call
        return f"{indent}logger.{log_level}({content})\n"

    def has_logging_import(self, content: str) -> bool:
        """Check if file already has logging import."""
        return "from shared.logging import get_logger" in content

    def find_import_insertion_point(self, lines: List[str]) -> int:
        """
        Find the best place to insert logging import.

        Args:
            lines: All file lines

        Returns:
            Line index where import should be inserted
        """
        last_import_idx = 0
        in_docstring = False
        docstring_marker = None

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track module-level docstrings
            if i == 0 or (i > 0 and lines[i - 1].strip() == ""):
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    if not in_docstring:
                        docstring_marker = stripped[:3]
                        in_docstring = True
                        # Single-line docstring
                        if stripped.count(docstring_marker) >= 2:
                            in_docstring = False
                    elif docstring_marker in stripped:
                        in_docstring = False
                    continue

            if in_docstring:
                continue

            # Find last import statement
            if stripped.startswith("import ") or stripped.startswith("from "):
                last_import_idx = i

        # Insert after last import, or after docstring if no imports
        return last_import_idx + 1 if last_import_idx > 0 else (1 if lines else 0)

    def add_logging_import(self, lines: List[str]) -> List[str]:
        """
        Add logging import to file.

        Args:
            lines: File lines

        Returns:
            Modified lines with import added
        """
        insert_idx = self.find_import_insertion_point(lines)

        # Add blank line before if needed
        if insert_idx > 0 and lines[insert_idx - 1].strip() != "":
            lines.insert(insert_idx, "\n")
            insert_idx += 1

        # Add import
        lines.insert(insert_idx, "from shared.logging import get_logger\n")

        return lines

    def add_logger_declaration(self, lines: List[str]) -> List[str]:
        """
        Add logger = get_logger(__name__) declaration.

        Adds after imports at module level.

        Args:
            lines: File lines

        Returns:
            Modified lines with logger declaration
        """
        # Find insertion point (after imports, before any code)
        insert_idx = self.find_import_insertion_point(lines)

        # Move past the logging import we just added
        for i in range(insert_idx, len(lines)):
            if "from shared.logging import get_logger" in lines[i]:
                insert_idx = i + 1
                break

        # Add blank line and logger declaration
        if insert_idx < len(lines) and lines[insert_idx].strip() != "":
            lines.insert(insert_idx, "\n")
            insert_idx += 1

        lines.insert(insert_idx, "logger = get_logger(__name__)\n")

        return lines

    def convert_file(self, file_path: Path) -> bool:
        """
        Convert a single file.

        Args:
            file_path: Path to Python file

        Returns:
            True if file was modified
        """
        try:
            self.log(f"Processing {file_path.relative_to(file_path.parents[3])}...")

            # Read file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Skip if already has logging import
            if self.has_logging_import(content):
                self.log(f"  Skipping - already has logging", "INFO")
                self.stats["files_skipped"] += 1
                return False

            lines = content.split("\n")
            new_lines = []
            modified = False
            print_count = 0

            # Process each line
            for i, line in enumerate(lines):
                stripped = line.strip()

                # Check if in test block
                if self.is_in_test_block(lines, i):
                    new_lines.append(line)
                    continue

                # Check if should skip
                if self.should_skip_line(line, stripped):
                    new_lines.append(line)
                    continue

                # Check for print statement
                if "print(" in line and stripped.startswith("print("):
                    # Extract print arguments
                    args = self.extract_print_arguments(line)
                    if args is not None:
                        # Get indentation
                        indent = line[: len(line) - len(line.lstrip())]

                        # Convert to logger call
                        new_line = self.convert_print_to_logger(line, indent, args)
                        new_lines.append(new_line.rstrip("\n"))

                        modified = True
                        print_count += 1
                        self.log(f"    Converted: {stripped[:60]}...", "INFO")
                    else:
                        # Keep complex prints as-is
                        new_lines.append(line)
                else:
                    new_lines.append(line)

            if not modified:
                self.log(f"  No changes needed", "INFO")
                self.stats["files_skipped"] += 1
                return False

            # Add logging infrastructure
            new_lines = self.add_logging_import(new_lines)
            new_lines = self.add_logger_declaration(new_lines)

            # Write back (unless dry run)
            if not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))

            self.stats["files_modified"] += 1
            self.stats["prints_replaced"] += print_count
            self.stats["modified_files"].append(str(file_path))

            self.log(f"  ✓ Converted {print_count} print statements", "INFO")
            return True

        except Exception as e:
            self.log(f"  ✗ Error: {e}", "ERROR")
            self.stats["errors"].append({"file": str(file_path), "error": str(e)})
            return False

    def find_files_with_prints(self, tools_dir: Path) -> List[Path]:
        """
        Find all Python files with print statements (outside test blocks).

        Args:
            tools_dir: Path to tools directory

        Returns:
            List of file paths
        """
        files = []

        for py_file in tools_dir.rglob("*.py"):
            # Skip __init__.py files
            if py_file.name == "__init__.py":
                continue

            # Skip test files (test_*.py, *_test.py, test*.py)
            if (
                py_file.name.startswith("test_")
                or py_file.name.startswith("test")
                or py_file.name.endswith("_test.py")
                or "test" in py_file.parent.name
            ):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check if file has prints and doesn't already have logging
                if (
                    "print(" in content
                    and "from shared.logging import get_logger" not in content
                ):
                    files.append(py_file)

            except Exception as e:
                self.log(f"Error reading {py_file}: {e}", "ERROR")

        return sorted(files)

    def run(self, tools_dir: Path) -> Dict:
        """
        Run the conversion process.

        Args:
            tools_dir: Path to tools directory

        Returns:
            Statistics dictionary
        """
        print("\n" + "=" * 70)
        print("PRINT TO LOGGING CONVERTER")
        print("=" * 70)

        if self.dry_run:
            print("DRY RUN MODE - No files will be modified\n")

        # Find files
        print("Finding files with print() statements...")
        files = self.find_files_with_prints(tools_dir)
        print(f"Found {len(files)} files to process\n")

        if not files:
            print("No files to convert!")
            return self.stats

        # Process each file
        for file_path in files:
            self.stats["files_processed"] += 1
            self.convert_file(file_path)

        # Print summary
        print("\n" + "=" * 70)
        print("CONVERSION SUMMARY")
        print("=" * 70)
        print(f"Files processed:       {self.stats['files_processed']}")
        print(f"Files modified:        {self.stats['files_modified']}")
        print(f"Files skipped:         {self.stats['files_skipped']}")
        print(f"Print statements:      {self.stats['prints_replaced']}")
        print(f"Errors:                {len(self.stats['errors'])}")

        if self.stats["errors"]:
            print("\nFiles with errors:")
            for error in self.stats["errors"]:
                print(f"  • {error['file']}")
                print(f"    {error['error']}")

        if self.dry_run:
            print("\nDRY RUN COMPLETE - Run without --dry-run to apply changes")
        else:
            print("\n✓ CONVERSION COMPLETE")

        return self.stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert print() statements to logging calls"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without modifying files"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed progress"
    )
    args = parser.parse_args()

    # Get repository root (assuming script is in scripts/)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    tools_dir = repo_root / "tools"

    if not tools_dir.exists():
        print(f"Error: tools/ directory not found at {tools_dir}")
        sys.exit(1)

    # Run converter
    converter = PrintToLoggingConverter(dry_run=args.dry_run, verbose=args.verbose)
    stats = converter.run(tools_dir)

    # Exit with error if there were errors
    sys.exit(1 if stats["errors"] else 0)


if __name__ == "__main__":
    main()
