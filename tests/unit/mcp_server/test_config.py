"""
Unit tests for MCP Configuration
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from mcp_server.config import MCPConfig


class TestMCPConfig:
    """Test MCP Configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MCPConfig()

        assert config.server_name == "agentswarm-tools"
        assert config.server_version == "1.0.0"
        assert config.enabled_categories is not None
        assert len(config.enabled_categories) > 0
        assert config.max_tools == 0
        assert config.enable_analytics is True
        assert config.enable_caching is True
        assert config.log_level == "INFO"

    def test_custom_config(self):
        """Test custom configuration values."""
        config = MCPConfig(
            server_name="custom-server",
            server_version="2.0.0",
            enabled_categories=["data"],
            max_tools=50,
            enable_analytics=False,
            enable_caching=False,
            log_level="DEBUG"
        )

        assert config.server_name == "custom-server"
        assert config.server_version == "2.0.0"
        assert config.enabled_categories == ["data"]
        assert config.max_tools == 50
        assert config.enable_analytics is False
        assert config.enable_caching is False
        assert config.log_level == "DEBUG"

    def test_default_categories(self):
        """Test default categories are set."""
        config = MCPConfig()

        assert "data" in config.enabled_categories
        assert "communication" in config.enabled_categories
        assert "media" in config.enabled_categories
        assert "visualization" in config.enabled_categories
        assert "content" in config.enabled_categories
        assert "infrastructure" in config.enabled_categories
        assert "utils" in config.enabled_categories

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = MCPConfig()
        data = config.to_dict()

        assert isinstance(data, dict)
        assert data["server_name"] == "agentswarm-tools"
        assert data["server_version"] == "1.0.0"
        assert "enabled_categories" in data

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "server_name": "test-server",
            "server_version": "1.5.0",
            "enabled_categories": ["data", "utils"],
            "max_tools": 25,
            "enable_analytics": False,
            "enable_caching": True,
            "log_level": "WARNING"
        }

        config = MCPConfig.from_dict(data)

        assert config.server_name == "test-server"
        assert config.server_version == "1.5.0"
        assert config.enabled_categories == ["data", "utils"]
        assert config.max_tools == 25

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name

        try:
            # Create and save config
            config1 = MCPConfig(
                server_name="test-server",
                enabled_categories=["data"],
                max_tools=10
            )
            config1.save_to_file(config_path)

            # Load config
            config2 = MCPConfig.load_from_file(config_path)

            assert config2.server_name == "test-server"
            assert config2.enabled_categories == ["data"]
            assert config2.max_tools == 10

        finally:
            # Clean up
            if os.path.exists(config_path):
                os.unlink(config_path)

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file returns default config."""
        config = MCPConfig.load_from_file("/nonexistent/path/config.json")

        # Should return default config
        assert config.server_name == "agentswarm-tools"
        assert config.server_version == "1.0.0"

    def test_load_invalid_json(self):
        """Test loading invalid JSON returns default config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {{{")
            config_path = f.name

        try:
            config = MCPConfig.load_from_file(config_path)

            # Should return default config
            assert config.server_name == "agentswarm-tools"

        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
