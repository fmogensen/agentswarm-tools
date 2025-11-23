"""
MCP Server Configuration

Manages server configuration including:
- Enabled tool categories
- Server metadata
- Feature flags
"""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class MCPConfig:
    """
    Configuration for MCP Server.

    Attributes:
        server_name: Server name
        server_version: Server version
        enabled_categories: List of tool categories to expose
        max_tools: Maximum number of tools to expose (0 = unlimited)
        enable_analytics: Enable analytics tracking
        enable_caching: Enable response caching
        log_level: Logging level
    """

    server_name: str = "agentswarm-tools"
    server_version: str = "1.0.0"
    enabled_categories: List[str] = None
    max_tools: int = 0
    enable_analytics: bool = True
    enable_caching: bool = True
    log_level: str = "INFO"

    def __post_init__(self):
        """Initialize default categories if not provided."""
        if self.enabled_categories is None:
            # Default: enable all categories
            self.enabled_categories = [
                "data",
                "communication",
                "media",
                "visualization",
                "content",
                "infrastructure",
                "utils"
            ]

    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> "MCPConfig":
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to config file (defaults to mcp_server/config.json)

        Returns:
            MCPConfig instance
        """
        if config_path is None:
            # Default config path
            current_dir = Path(__file__).parent
            config_path = current_dir / "config.json"

        if not os.path.exists(config_path):
            # Return default config
            return cls()

        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)

            return cls(**config_data)

        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
            return cls()

    def save_to_file(self, config_path: Optional[str] = None) -> None:
        """
        Save configuration to JSON file.

        Args:
            config_path: Path to config file (defaults to mcp_server/config.json)
        """
        if config_path is None:
            current_dir = Path(__file__).parent
            config_path = current_dir / "config.json"

        with open(config_path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPConfig":
        """Create config from dictionary."""
        return cls(**data)
