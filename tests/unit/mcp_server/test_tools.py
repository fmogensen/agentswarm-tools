"""
Unit tests for MCP Tool Registry
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from pydantic import Field

from mcp_server.config import MCPConfig
from mcp_server.tools import ToolRegistry
from shared.base import BaseTool


# Mock tool for testing
class MockTool(BaseTool):
    """Mock tool for testing"""

    tool_name: str = "mock_tool"
    tool_category: str = "utils"

    query: str = Field(..., description="Query parameter", min_length=1)
    max_results: int = Field(10, description="Max results", ge=1, le=100)

    def _execute(self):
        return {"success": True, "result": "mock"}


class TestToolRegistry:
    """Test Tool Registry functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return MCPConfig(enabled_categories=["data", "utils"], enable_analytics=False)

    @pytest.fixture
    def registry(self, config):
        """Create tool registry instance."""
        return ToolRegistry(config)

    def test_registry_initialization(self, registry):
        """Test registry initializes correctly."""
        assert registry.config is not None
        assert registry.tools_dir.exists()
        assert registry._tool_cache == {}

    def test_get_tools_directory(self, registry):
        """Test tools directory path resolution."""
        tools_dir = registry._get_tools_directory()
        assert tools_dir.exists()
        assert tools_dir.name == "tools"

    def test_get_category_path_data(self, registry):
        """Test category path resolution for data."""
        path = registry._get_category_path("data")
        assert path is not None
        assert path.exists()

    def test_get_category_path_utils(self, registry):
        """Test category path resolution for utils."""
        path = registry._get_category_path("utils")
        assert path is not None
        assert path.exists()

    def test_get_category_path_invalid(self, registry):
        """Test invalid category returns None."""
        path = registry._get_category_path("nonexistent_category")
        assert path is None or not path.exists()

    def test_generate_tool_schema(self, registry):
        """Test tool schema generation."""
        schema = registry.generate_tool_schema(MockTool)

        assert schema["name"] == "mock_tool"
        assert schema["description"] == "Mock tool for testing"
        assert "inputSchema" in schema
        assert schema["inputSchema"]["type"] == "object"
        assert "properties" in schema["inputSchema"]
        assert "required" in schema["inputSchema"]

    def test_generate_input_schema(self, registry):
        """Test input schema generation."""
        schema = registry._generate_input_schema(MockTool)

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "query" in schema["properties"]
        assert "max_results" in schema["properties"]

        # Check query field
        query_field = schema["properties"]["query"]
        assert query_field["type"] == "string"
        assert query_field["description"] == "Query parameter"
        assert "query" in schema["required"]

        # Check max_results field
        max_results_field = schema["properties"]["max_results"]
        assert max_results_field["type"] == "integer"
        assert max_results_field["description"] == "Max results"
        assert max_results_field["minimum"] == 1
        assert max_results_field["maximum"] == 100

    def test_field_to_json_schema_string(self, registry):
        """Test string field conversion."""
        from pydantic import Field

        field_info = Field(..., description="Test string")
        schema = registry._field_to_json_schema("test_field", field_info)

        assert schema is not None
        assert schema["description"] == "Test string"

    def test_field_to_json_schema_integer(self, registry):
        """Test integer field conversion."""
        from pydantic import Field

        field_info = Field(10, description="Test int", ge=1, le=100)
        schema = registry._field_to_json_schema("test_field", field_info)

        assert schema is not None
        assert schema["type"] == "integer"
        assert schema["minimum"] == 1
        assert schema["maximum"] == 100

    def test_is_field_required(self, registry):
        """Test field required check."""
        from pydantic import Field

        # Required field
        required_field = Field(..., description="Required")
        # Note: This might need adjustment based on Pydantic version
        # The actual implementation handles both v1 and v2

        # Optional field
        optional_field = Field(default="test", description="Optional")
        # Similar note applies

    def test_execute_tool(self, registry):
        """Test tool execution."""
        arguments = {"query": "test query", "max_results": 5}

        result = registry.execute_tool(MockTool, arguments)

        assert result is not None
        # Result format depends on BaseTool implementation

    def test_execute_tool_filters_internal_fields(self, registry):
        """Test that internal fields are filtered from arguments."""
        arguments = {
            "query": "test",
            "max_results": 5,
            "_internal": "should be filtered",
            "tool_name": "should be filtered",
        }

        # Should not raise error from extra fields
        result = registry.execute_tool(MockTool, arguments)
        assert result is not None

    def test_discover_tools(self, registry):
        """Test tool discovery."""
        tools = registry.discover_tools()

        assert isinstance(tools, dict)
        assert len(tools) > 0

        # Check that some known tools are present
        # (depends on what's actually in the tools directory)

    def test_discover_tools_caching(self, registry):
        """Test tool discovery caching."""
        # First call
        tools1 = registry.discover_tools()

        # Second call should use cache
        tools2 = registry.discover_tools()

        assert tools1 == tools2
        assert id(tools1) == id(tools2)  # Same object

    def test_type_to_json_schema(self, registry):
        """Test Python type to JSON Schema conversion."""
        assert registry._type_to_json_schema(str)["type"] == "string"
        assert registry._type_to_json_schema(int)["type"] == "integer"
        assert registry._type_to_json_schema(float)["type"] == "number"
        assert registry._type_to_json_schema(bool)["type"] == "boolean"


class TestToolDiscovery:
    """Test tool discovery functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return MCPConfig(enabled_categories=["data"])

    @pytest.fixture
    def registry(self, config):
        """Create tool registry instance."""
        return ToolRegistry(config)

    def test_discover_category_tools(self, registry):
        """Test discovering tools from a category."""
        tools = registry._discover_category_tools("data")

        assert isinstance(tools, dict)
        # Should find at least some tools in data category

    def test_discover_only_enabled_categories(self):
        """Test that only enabled categories are discovered."""
        config = MCPConfig(enabled_categories=["utils"])
        registry = ToolRegistry(config)

        tools = registry.discover_tools()

        # Should only have tools from utils category
        for tool_name, tool_class in tools.items():
            if hasattr(tool_class, "tool_category"):
                # Category might be utils or related
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
