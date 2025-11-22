"""
Tool registry for AgentSwarm Tools Framework.
Provides centralized discovery, registration, and management of tools.
"""

import os
import importlib
import pkgutil
import inspect
import logging
from typing import Dict, List, Optional, Type, Any
from pathlib import Path

from .base import BaseTool

# Configure logging
logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for discovering and managing tools.

    This singleton class provides centralized access to all tools in the framework.
    It supports both manual registration and automatic discovery from the tools/ directory.

    Features:
    - Singleton pattern for global access
    - Auto-discovery of tools from directory structure
    - Filter tools by category
    - Get tool metadata

    Example:
        ```python
        from shared.registry import tool_registry

        # Discover all tools
        tool_registry.discover_tools()

        # Get a specific tool
        WebSearchTool = tool_registry.get_tool('web_search')
        tool = WebSearchTool(query="python tutorial")
        result = tool.run()

        # List all tools in a category
        search_tools = tool_registry.list_tools(category='search')
        ```
    """

    _instance = None
    _tools: Dict[str, Type[BaseTool]] = {}
    _discovered: bool = False

    def __new__(cls):
        """Singleton pattern - ensure only one registry instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
            cls._instance._discovered = False
        return cls._instance

    def register(self, tool_class: Type[BaseTool]) -> None:
        """
        Register a tool class.

        Args:
            tool_class: Tool class to register (must inherit from BaseTool)

        Raises:
            ValueError: If tool_class doesn't inherit from BaseTool
        """
        if not inspect.isclass(tool_class):
            raise ValueError(f"Expected a class, got {type(tool_class)}")

        # Get tool name from class attribute or class name
        name = getattr(tool_class, "tool_name", None)
        if name is None or name == "base_tool":
            # Use class name converted to snake_case
            name = self._to_snake_case(tool_class.__name__)

        if name in self._tools:
            logger.warning(f"Tool '{name}' already registered, overwriting")

        self._tools[name] = tool_class
        logger.debug(f"Registered tool: {name}")

    def unregister(self, name: str) -> bool:
        """
        Unregister a tool by name.

        Args:
            name: Name of the tool to unregister

        Returns:
            True if tool was removed, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            logger.debug(f"Unregistered tool: {name}")
            return True
        return False

    def get_tool(self, name: str) -> Optional[Type[BaseTool]]:
        """
        Get a tool class by name.

        Args:
            name: Name of the tool

        Returns:
            Tool class or None if not found
        """
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            name: Name of the tool

        Returns:
            True if tool exists
        """
        return name in self._tools

    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered tools with metadata.

        Args:
            category: Optional category filter

        Returns:
            List of tool metadata dictionaries containing:
            - name: Tool name
            - category: Tool category
            - description: Tool docstring
            - class: Tool class reference
        """
        tools = []
        for name, tool_class in sorted(self._tools.items()):
            tool_category = getattr(tool_class, "tool_category", "unknown")

            if category is None or tool_category == category:
                tools.append(
                    {
                        "name": name,
                        "category": tool_category,
                        "description": self._get_description(tool_class),
                        "class": tool_class,
                    }
                )
        return tools

    def list_categories(self) -> List[str]:
        """
        List all unique tool categories.

        Returns:
            Sorted list of category names
        """
        categories = set()
        for tool_class in self._tools.values():
            category = getattr(tool_class, "tool_category", "unknown")
            categories.add(category)
        return sorted(categories)

    def get_tool_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed metadata for a specific tool.

        Args:
            name: Tool name

        Returns:
            Metadata dictionary or None if not found
        """
        tool_class = self._tools.get(name)
        if tool_class is None:
            return None

        return {
            "name": name,
            "category": getattr(tool_class, "tool_category", "unknown"),
            "description": self._get_description(tool_class),
            "rate_limit_type": getattr(tool_class, "rate_limit_type", "default"),
            "class": tool_class,
            "module": tool_class.__module__,
            "fields": self._get_fields(tool_class),
        }

    def discover_tools(self, tools_path: Optional[str] = None) -> int:
        """
        Auto-discover and register tools from directory.

        Walks the tools/ directory structure and imports all tool classes
        that inherit from BaseTool.

        Args:
            tools_path: Path to tools directory. If None, uses default location.

        Returns:
            Number of tools discovered
        """
        if tools_path is None:
            # Default to tools/ directory relative to this file
            base_dir = Path(__file__).parent.parent
            tools_path = str(base_dir / "tools")

        tools_path = Path(tools_path)
        if not tools_path.exists():
            logger.warning(f"Tools directory not found: {tools_path}")
            return 0

        initial_count = len(self._tools)

        # Walk through all subdirectories
        for category_dir in tools_path.iterdir():
            if not category_dir.is_dir():
                continue
            if category_dir.name.startswith("_"):
                continue

            # Process each Python file in the category
            for py_file in category_dir.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                if py_file.name.startswith("test_"):
                    continue

                self._import_tools_from_file(py_file, tools_path)

        discovered = len(self._tools) - initial_count
        self._discovered = True
        logger.info(f"Discovered {discovered} tools from {tools_path}")
        return discovered

    def _import_tools_from_file(self, file_path: Path, tools_root: Path) -> None:
        """Import tool classes from a Python file."""
        try:
            # Calculate module path
            relative_path = file_path.relative_to(tools_root.parent)
            module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")

            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find all BaseTool subclasses in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if not inspect.isclass(attr):
                    continue
                if attr is BaseTool:
                    continue
                if not issubclass(attr, BaseTool):
                    continue
                if attr.__module__ != module.__name__:
                    # Skip imported classes
                    continue

                # Register the tool
                self.register(attr)

        except Exception as e:
            logger.warning(f"Failed to import tools from {file_path}: {e}")

    def _get_description(self, tool_class: Type[BaseTool]) -> str:
        """Extract description from tool class docstring."""
        doc = tool_class.__doc__
        if doc:
            # Return first paragraph of docstring
            paragraphs = doc.strip().split("\n\n")
            return paragraphs[0].strip().replace("\n", " ")
        return ""

    def _get_fields(self, tool_class: Type[BaseTool]) -> Dict[str, Dict[str, Any]]:
        """Extract Pydantic field information from tool class."""
        fields = {}

        if hasattr(tool_class, "model_fields"):
            # Pydantic v2
            for name, field_info in tool_class.model_fields.items():
                if name.startswith("_"):
                    continue
                # Skip base class fields
                if name in (
                    "tool_name",
                    "tool_category",
                    "rate_limit_type",
                    "rate_limit_cost",
                    "max_retries",
                    "retry_delay",
                ):
                    continue

                fields[name] = {
                    "type": str(field_info.annotation) if field_info.annotation else "Any",
                    "description": field_info.description or "",
                    "required": field_info.is_required(),
                    "default": field_info.default if not field_info.is_required() else None,
                }
        elif hasattr(tool_class, "__fields__"):
            # Pydantic v1
            for name, field in tool_class.__fields__.items():
                if name.startswith("_"):
                    continue
                if name in (
                    "tool_name",
                    "tool_category",
                    "rate_limit_type",
                    "rate_limit_cost",
                    "max_retries",
                    "retry_delay",
                ):
                    continue

                fields[name] = {
                    "type": str(field.outer_type_),
                    "description": field.field_info.description or "",
                    "required": field.required,
                    "default": field.default if not field.required else None,
                }

        return fields

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("_")
            result.append(char.lower())
        return "".join(result)

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._discovered = False
        logger.debug("Cleared all registered tools")

    @property
    def tool_count(self) -> int:
        """Get the number of registered tools."""
        return len(self._tools)

    @property
    def is_discovered(self) -> bool:
        """Check if tools have been discovered."""
        return self._discovered

    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self._tools

    def __iter__(self):
        """Iterate over tool names."""
        return iter(self._tools)


# Singleton instance
tool_registry = ToolRegistry()


def get_tool(name: str) -> Optional[Type[BaseTool]]:
    """
    Convenience function to get a tool by name.

    Args:
        name: Tool name

    Returns:
        Tool class or None
    """
    return tool_registry.get_tool(name)


def list_tools(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to list all tools.

    Args:
        category: Optional category filter

    Returns:
        List of tool metadata
    """
    return tool_registry.list_tools(category)


def discover_tools(tools_path: Optional[str] = None) -> int:
    """
    Convenience function to discover tools.

    Args:
        tools_path: Path to tools directory

    Returns:
        Number of tools discovered
    """
    return tool_registry.discover_tools(tools_path)


if __name__ == "__main__":
    # Test the registry
    print("Testing ToolRegistry...")

    # Create a test tool class
    class TestSearchTool(BaseTool):
        """A test search tool for demonstration."""

        tool_name: str = "test_search"
        tool_category: str = "search"

        def _execute(self):
            return {"success": True, "results": []}

    # Test registration
    registry = ToolRegistry()
    registry.register(TestSearchTool)

    print(f"Registered tools: {registry.tool_count}")
    assert registry.has_tool("test_search"), "Tool should be registered"

    # Test get_tool
    tool_class = registry.get_tool("test_search")
    assert tool_class is TestSearchTool, "Should return correct class"

    # Test list_tools
    tools = registry.list_tools()
    assert len(tools) >= 1, "Should have at least one tool"
    print(f"Tools: {[t['name'] for t in tools]}")

    # Test list_tools with category filter
    search_tools = registry.list_tools(category="search")
    assert len(search_tools) >= 1, "Should have at least one search tool"

    # Test get_tool_metadata
    metadata = registry.get_tool_metadata("test_search")
    assert metadata is not None, "Should return metadata"
    assert metadata["category"] == "search", "Category should be search"
    print(f"Metadata: {metadata}")

    # Test list_categories
    categories = registry.list_categories()
    assert "search" in categories, "Should include search category"
    print(f"Categories: {categories}")

    # Test unregister
    assert registry.unregister("test_search"), "Should unregister successfully"
    assert not registry.has_tool("test_search"), "Tool should be gone"

    # Test discovery (if tools directory exists)
    registry.clear()
    discovered = registry.discover_tools()
    print(f"Discovered {discovered} tools from tools/ directory")

    if discovered > 0:
        print(f"Categories after discovery: {registry.list_categories()}")
        print(f"Total tools: {registry.tool_count}")

    print("\nAll tests passed!")
