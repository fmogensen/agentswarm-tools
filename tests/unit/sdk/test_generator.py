"""
Tests for ToolGenerator
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from sdk.generator import ToolGenerator


class TestToolGenerator:
    """Test cases for ToolGenerator"""

    def setup_method(self):
        """Set up test environment"""
        # Create temp directory for testing
        self.test_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test environment"""
        # Remove temp directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_generator_initialization(self):
        """Test generator can be initialized"""
        generator = ToolGenerator(project_root=str(self.test_dir))
        assert generator is not None
        assert generator.project_root == self.test_dir

    def test_to_snake_case(self):
        """Test snake_case conversion"""
        generator = ToolGenerator()

        assert generator._to_snake_case("MyTool") == "my_tool"
        assert generator._to_snake_case("my-tool") == "my_tool"
        assert generator._to_snake_case("my tool") == "my_tool"
        assert generator._to_snake_case("WebSearchTool") == "web_search_tool"

    def test_to_class_name(self):
        """Test class name conversion"""
        generator = ToolGenerator()

        assert generator._to_class_name("my_tool") == "MyTool"
        assert generator._to_class_name("web_search") == "WebSearch"
        assert generator._to_class_name("api_client_tool") == "ApiClientTool"

    def test_generate_tool_cli(self):
        """Test CLI tool generation"""
        # Create test structure
        tools_dir = self.test_dir / "tools"
        tools_dir.mkdir()
        (tools_dir / "data").mkdir()
        (tools_dir / "data" / "search").mkdir()

        # Copy templates to test directory
        templates_dir = Path(__file__).parent.parent.parent.parent / "sdk" / "templates"
        test_templates_dir = self.test_dir / "sdk" / "templates"
        test_templates_dir.mkdir(parents=True)

        for template_file in templates_dir.glob("*.jinja2"):
            shutil.copy(template_file, test_templates_dir)

        generator = ToolGenerator(project_root=str(self.test_dir))

        result = generator.generate_tool_cli(
            tool_name="test_tool",
            category="data",
            description="Test tool for testing",
            subcategory="search",
            parameters=[
                {
                    "name": "query",
                    "type": "str",
                    "required": True,
                    "default": "...",
                    "description": "Search query",
                    "example": '"test query"',
                    "test_value": '"test"',
                    "constraints": "min_length=1",
                }
            ],
            requires_api_key=False,
        )

        assert result is not None
        assert result["tool_name"] == "test_tool"
        assert len(result["generated_files"]) > 0

        # Check generated files exist
        tool_path = Path(result["tool_path"])
        assert (tool_path / "test_tool.py").exists()
        assert (tool_path / "test_test_tool.py").exists()
        assert (tool_path / "README.md").exists()
        assert (tool_path / "__init__.py").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
