"""
Tool Discovery and Adaptation for MCP Server

Discovers all AgentSwarm tools and adapts them to MCP format.
Handles:
- Auto-discovery from tool directories
- Pydantic schema to JSON Schema conversion
- Tool execution and parameter mapping
"""

import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import Field
from pydantic.fields import FieldInfo

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for discovering and managing AgentSwarm tools.

    Handles:
    - Tool discovery from filesystem
    - Schema generation (Pydantic -> JSON Schema)
    - Tool execution
    - Parameter validation
    """

    def __init__(self, config):
        """
        Initialize tool registry.

        Args:
            config: MCP configuration object
        """
        self.config = config
        self.tools_dir = self._get_tools_directory()
        self._tool_cache = {}

    def _get_tools_directory(self) -> Path:
        """Get absolute path to tools directory."""
        current_dir = Path(__file__).parent.parent
        tools_dir = current_dir / "tools"

        if not tools_dir.exists():
            raise RuntimeError(f"Tools directory not found: {tools_dir}")

        return tools_dir

    def discover_tools(self) -> Dict[str, Type[BaseTool]]:
        """
        Discover all available tools from enabled categories.

        Returns:
            Dict mapping tool_name -> tool_class
        """
        if self._tool_cache:
            return self._tool_cache

        tools = {}

        for category in self.config.enabled_categories:
            category_tools = self._discover_category_tools(category)
            tools.update(category_tools)

        self._tool_cache = tools
        return tools

    def _discover_category_tools(self, category: str) -> Dict[str, Type[BaseTool]]:
        """
        Discover tools from a specific category.

        Args:
            category: Category name (e.g., 'data', 'communication')

        Returns:
            Dict of tools in this category
        """
        tools = {}

        # Map category to directory structure
        category_path = self._get_category_path(category)
        if not category_path or not category_path.exists():
            logger.warning(f"Category path not found: {category}")
            return tools

        logger.info(f"Discovering tools in category: {category} ({category_path})")

        # Walk through category directory
        for tool_dir in category_path.rglob("*"):
            if not tool_dir.is_dir():
                continue

            # Skip __pycache__ and hidden directories
            if tool_dir.name.startswith("__") or tool_dir.name.startswith("."):
                continue

            # Look for __init__.py
            init_file = tool_dir / "__init__.py"
            if not init_file.exists():
                continue

            # Try to load tool
            try:
                tool_class = self._load_tool_from_directory(tool_dir)
                if tool_class:
                    tool_name = getattr(tool_class, "tool_name", tool_dir.name)
                    tools[tool_name] = tool_class
                    logger.info(f"  Loaded tool: {tool_name}")

            except Exception as e:
                logger.error(f"  Failed to load tool from {tool_dir}: {e}")
                continue

        return tools

    def _get_category_path(self, category: str) -> Optional[Path]:
        """
        Get filesystem path for a category.

        Args:
            category: Category name

        Returns:
            Path to category directory or None
        """
        # Map category names to directory paths
        category_map = {
            "data": ["data/search", "data/business", "data/intelligence"],
            "communication": ["communication"],
            "media": ["media/generation", "media/analysis", "media/processing"],
            "visualization": ["visualization"],
            "content": ["content/documents", "content/web"],
            "infrastructure": [
                "infrastructure/execution",
                "infrastructure/storage",
                "infrastructure/management",
            ],
            "utils": ["utils"],
            "integrations": ["integrations"],
        }

        paths = category_map.get(category, [])
        if not paths:
            # Try direct mapping
            direct_path = self.tools_dir / category
            if direct_path.exists():
                return direct_path
            return None

        # Return first valid path
        for rel_path in paths:
            full_path = self.tools_dir / rel_path
            if full_path.exists():
                return full_path

        return None

    def _load_tool_from_directory(self, tool_dir: Path) -> Optional[Type[BaseTool]]:
        """
        Load tool class from directory.

        Args:
            tool_dir: Path to tool directory

        Returns:
            Tool class or None
        """
        # Build import path
        rel_path = tool_dir.relative_to(self.tools_dir.parent)
        module_path = str(rel_path).replace(os.sep, ".")

        try:
            # Import module
            module = importlib.import_module(module_path)

            # Find BaseTool subclass
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, BaseTool)
                    and obj is not BaseTool
                    and not name.startswith("_")
                ):
                    return obj

        except Exception as e:
            logger.debug(f"Could not import {module_path}: {e}")
            return None

        return None

    def generate_tool_schema(self, tool_class: Type[BaseTool]) -> Dict[str, Any]:
        """
        Generate MCP tool schema from AgentSwarm tool.

        Converts Pydantic model to JSON Schema format per MCP spec.

        Args:
            tool_class: Tool class

        Returns:
            MCP tool schema dict
        """
        # Get tool metadata
        tool_name = getattr(tool_class, "tool_name", tool_class.__name__)
        description = tool_class.__doc__ or f"AgentSwarm tool: {tool_name}"

        # Clean up description (first line only)
        description = description.strip().split("\n")[0]

        # Generate input schema from Pydantic model
        input_schema = self._generate_input_schema(tool_class)

        return {"name": tool_name, "description": description, "inputSchema": input_schema}

    def _generate_input_schema(self, tool_class: Type[BaseTool]) -> Dict[str, Any]:
        """
        Generate JSON Schema for tool input parameters.

        Args:
            tool_class: Tool class

        Returns:
            JSON Schema dict
        """
        schema = {"type": "object", "properties": {}, "required": []}

        # Get model fields
        try:
            # Pydantic v2
            model_fields = tool_class.model_fields
        except AttributeError:
            # Pydantic v1
            model_fields = tool_class.__fields__

        for field_name, field_info in model_fields.items():
            # Skip internal fields
            if field_name.startswith("_"):
                continue

            # Skip tool metadata fields
            if field_name in [
                "tool_name",
                "tool_category",
                "rate_limit_type",
                "rate_limit_cost",
                "max_retries",
                "retry_delay",
                "enable_cache",
                "cache_ttl",
                "cache_key_params",
            ]:
                continue

            # Generate field schema
            field_schema = self._field_to_json_schema(field_name, field_info)
            if field_schema:
                schema["properties"][field_name] = field_schema

                # Check if required
                if self._is_field_required(field_info):
                    schema["required"].append(field_name)

        return schema

    def _field_to_json_schema(
        self, field_name: str, field_info: FieldInfo
    ) -> Optional[Dict[str, Any]]:
        """
        Convert Pydantic field to JSON Schema.

        Args:
            field_name: Field name
            field_info: Pydantic FieldInfo

        Returns:
            JSON Schema for field or None
        """
        try:
            # Get field annotation (type)
            field_type = field_info.annotation

            # Handle Optional types
            origin = getattr(field_type, "__origin__", None)
            if origin is None or str(origin) == "typing.Union":
                # Extract actual type from Optional
                args = getattr(field_type, "__args__", ())
                if args:
                    # Filter out NoneType
                    non_none_types = [t for t in args if t is not type(None)]
                    if non_none_types:
                        field_type = non_none_types[0]

            # Map Python types to JSON Schema types
            schema = {}

            if field_type == str or field_type == "str":
                schema["type"] = "string"
            elif field_type == int or field_type == "int":
                schema["type"] = "integer"
            elif field_type == float or field_type == "float":
                schema["type"] = "number"
            elif field_type == bool or field_type == "bool":
                schema["type"] = "boolean"
            elif origin == list or field_type == list:
                schema["type"] = "array"
                # Try to get item type
                args = getattr(field_type, "__args__", ())
                if args:
                    schema["items"] = self._type_to_json_schema(args[0])
            elif origin == dict or field_type == dict:
                schema["type"] = "object"
            else:
                # Default to string for unknown types
                schema["type"] = "string"

            # Add description from Field
            if hasattr(field_info, "description") and field_info.description:
                schema["description"] = field_info.description

            # Add constraints
            if hasattr(field_info, "ge") and field_info.ge is not None:
                schema["minimum"] = field_info.ge
            if hasattr(field_info, "le") and field_info.le is not None:
                schema["maximum"] = field_info.le
            if hasattr(field_info, "min_length") and field_info.min_length is not None:
                schema["minLength"] = field_info.min_length
            if hasattr(field_info, "max_length") and field_info.max_length is not None:
                schema["maxLength"] = field_info.max_length

            return schema

        except Exception as e:
            logger.warning(f"Could not generate schema for field {field_name}: {e}")
            return {"type": "string", "description": f"Parameter: {field_name}"}

    def _type_to_json_schema(self, python_type: Any) -> Dict[str, Any]:
        """Convert Python type to JSON Schema type."""
        if python_type == str:
            return {"type": "string"}
        elif python_type == int:
            return {"type": "integer"}
        elif python_type == float:
            return {"type": "number"}
        elif python_type == bool:
            return {"type": "boolean"}
        else:
            return {"type": "string"}

    def _is_field_required(self, field_info: FieldInfo) -> bool:
        """Check if field is required."""
        # In Pydantic v2
        if hasattr(field_info, "is_required"):
            return field_info.is_required()

        # In Pydantic v1
        if hasattr(field_info, "required"):
            return field_info.required

        # Check if has default
        if hasattr(field_info, "default"):
            return field_info.default is ...

        return False

    def execute_tool(self, tool_class: Type[BaseTool], arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool with given arguments.

        Args:
            tool_class: Tool class to execute
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            Exception: On execution error
        """
        # Filter out internal fields from arguments
        filtered_args = {
            k: v
            for k, v in arguments.items()
            if not k.startswith("_")
            and k
            not in [
                "tool_name",
                "tool_category",
                "rate_limit_type",
                "rate_limit_cost",
                "max_retries",
                "retry_delay",
                "enable_cache",
                "cache_ttl",
                "cache_key_params",
            ]
        }

        # Create tool instance
        tool_instance = tool_class(**filtered_args)

        # Execute tool
        result = tool_instance.run()

        return result
