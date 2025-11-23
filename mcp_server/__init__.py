"""
MCP Server for AgentSwarm Tools Framework

Entry point for running the MCP server.

Usage:
    python -m mcp_server

Or programmatically:
    from mcp_server import MCPServer
    server = MCPServer()
    server.run()
"""

from .config import MCPConfig
from .server import MCPServer, main
from .tools import ToolRegistry

__version__ = "1.0.0"
__all__ = ["MCPServer", "MCPConfig", "ToolRegistry", "main"]


if __name__ == "__main__":
    main()
