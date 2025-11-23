#!/usr/bin/env python3
"""
Simple test script for MCP Server

Tests basic functionality without requiring full MCP client setup.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.config import MCPConfig
from mcp_server.server import MCPServer


def test_config():
    """Test configuration."""
    print("Testing Configuration...")
    config = MCPConfig(
        enabled_categories=["data", "utils"],
        enable_analytics=False,
        enable_caching=False
    )
    print(f"  ✓ Config created: {config.server_name} v{config.server_version}")
    print(f"  ✓ Categories: {config.enabled_categories}")
    return config


def test_server_init(config):
    """Test server initialization."""
    print("\nTesting Server Initialization...")
    server = MCPServer(config)
    print(f"  ✓ Server initialized")
    print(f"  ✓ Protocol version: {server.PROTOCOL_VERSION}")
    print(f"  ✓ Tools loaded: {len(server.tools)}")
    return server


def test_initialize_request(server):
    """Test initialize request."""
    print("\nTesting Initialize Request...")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    response = server.handle_request(request)
    print(f"  ✓ Response: {json.dumps(response, indent=2)[:200]}...")
    return response


def test_tools_list_request(server):
    """Test tools/list request."""
    print("\nTesting Tools List Request...")
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    response = server.handle_request(request)
    tools = response.get("result", {}).get("tools", [])
    print(f"  ✓ Tools available: {len(tools)}")

    if tools:
        print(f"\nFirst 5 tools:")
        for i, tool in enumerate(tools[:5]):
            print(f"    {i+1}. {tool['name']} - {tool['description'][:60]}...")

    return response


def test_ping_request(server):
    """Test ping request."""
    print("\nTesting Ping Request...")
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "ping",
        "params": {}
    }
    response = server.handle_request(request)
    print(f"  ✓ Ping response: {response.get('result', {}).get('status')}")
    return response


def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Server Test Suite")
    print("=" * 60)

    try:
        # Run tests
        config = test_config()
        server = test_server_init(config)
        test_initialize_request(server)
        test_tools_list_request(server)
        test_ping_request(server)

        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
