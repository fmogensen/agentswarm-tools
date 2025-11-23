"""
Unit tests for MCP Server
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from mcp_server.server import MCPServer
from mcp_server.config import MCPConfig


class TestMCPServer:
    """Test MCP Server core functionality."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return MCPConfig(
            enabled_categories=["data"],
            max_tools=10,
            enable_analytics=False,
            enable_caching=False,
            log_level="ERROR"
        )

    @pytest.fixture
    def server(self, config):
        """Create test server instance."""
        with patch('mcp_server.server.ToolRegistry') as mock_registry:
            # Mock tool registry
            mock_registry_instance = MagicMock()
            mock_registry_instance.discover_tools.return_value = {
                "test_tool": Mock(tool_name="test_tool", __doc__="Test tool")
            }
            mock_registry.return_value = mock_registry_instance

            server = MCPServer(config)
            return server

    def test_server_initialization(self, server):
        """Test server initializes correctly."""
        assert server.VERSION == "1.0.0"
        assert server.config is not None
        assert server.tool_registry is not None
        assert server.request_counter == 0

    def test_handle_initialize(self, server):
        """Test initialize request handling."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }

        response = server.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["protocolVersion"] == server.PROTOCOL_VERSION
        assert response["result"]["serverInfo"]["name"] == "agentswarm-tools"

    def test_handle_ping(self, server):
        """Test ping request handling."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "ping",
            "params": {}
        }

        response = server.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "result" in response
        assert response["result"]["status"] == "ok"
        assert "timestamp" in response["result"]

    def test_handle_list_tools(self, server):
        """Test tools/list request handling."""
        # Mock generate_tool_schema
        server.tool_registry.generate_tool_schema = Mock(return_value={
            "name": "test_tool",
            "description": "Test tool",
            "inputSchema": {"type": "object", "properties": {}}
        })

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list",
            "params": {}
        }

        response = server.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0

    def test_handle_call_tool_success(self, server):
        """Test successful tool execution."""
        # Mock tool execution
        server.tool_registry.execute_tool = Mock(return_value={
            "success": True,
            "result": "Tool executed successfully"
        })

        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {"param1": "value1"}
            }
        }

        response = server.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 4
        assert "result" in response
        assert "content" in response["result"]
        assert len(response["result"]["content"]) > 0
        assert response["result"]["content"][0]["type"] == "text"

    def test_handle_call_tool_not_found(self, server):
        """Test tool not found error."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            }
        }

        response = server.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 5
        # Should return error in content
        assert "result" in response
        assert "content" in response["result"]

    def test_handle_call_tool_error(self, server):
        """Test tool execution error."""
        # Mock tool execution error
        server.tool_registry.execute_tool = Mock(
            side_effect=ValueError("Tool execution failed")
        )

        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {}
            }
        }

        response = server.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 6
        assert "result" in response
        assert "isError" in response["result"]
        assert response["result"]["isError"] is True

    def test_handle_method_not_found(self, server):
        """Test unknown method handling."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "unknown/method",
            "params": {}
        }

        response = server.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 7
        assert "error" in response
        assert response["error"]["code"] == -32601

    def test_success_response(self, server):
        """Test success response formatting."""
        response = server._success_response(1, {"data": "test"})

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert response["result"] == {"data": "test"}

    def test_error_response(self, server):
        """Test error response formatting."""
        response = server._error_response(1, -32600, "Invalid request")

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32600
        assert response["error"]["message"] == "Invalid request"

    def test_request_counter(self, server):
        """Test request counter increments."""
        initial_count = server.request_counter

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "ping",
            "params": {}
        }

        server.handle_request(request)
        assert server.request_counter == initial_count + 1

        server.handle_request(request)
        assert server.request_counter == initial_count + 2


class TestMCPServerIntegration:
    """Integration tests for MCP Server."""

    @pytest.fixture
    def real_server(self):
        """Create server with real configuration."""
        config = MCPConfig(
            enabled_categories=["utils"],  # Small category for testing
            enable_analytics=False,
            enable_caching=False
        )
        return MCPServer(config)

    def test_full_request_response_cycle(self, real_server):
        """Test full request/response cycle."""
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }

        init_response = real_server.handle_request(init_request)
        assert "result" in init_response

        # List tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }

        list_response = real_server.handle_request(list_request)
        assert "result" in list_response
        assert "tools" in list_response["result"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
