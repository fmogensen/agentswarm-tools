"""
MCP Server for AgentSwarm Tools Framework

Implements the Model Context Protocol (MCP) to enable Claude Desktop integration
and access to 100+ AgentSwarm tools.

Protocol: JSON-RPC 2.0 over stdio transport
Spec: https://modelcontextprotocol.io/docs/specification
"""

import sys
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import traceback

from .tools import ToolRegistry
from .config import MCPConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/agentswarm_mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server implementation for AgentSwarm Tools.

    Handles:
    - tools/list: List all available tools
    - tools/call: Execute a tool with parameters
    - Error handling per MCP specification
    - Request/response formatting
    """

    VERSION = "1.0.0"
    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self, config: Optional[MCPConfig] = None):
        """
        Initialize MCP server.

        Args:
            config: Optional MCP configuration
        """
        self.config = config or MCPConfig()
        self.tool_registry = ToolRegistry(self.config)
        self.request_counter = 0

        logger.info(f"MCP Server v{self.VERSION} initializing...")
        logger.info(f"Tool categories enabled: {self.config.enabled_categories}")

        # Load tools
        self.tools = self.tool_registry.discover_tools()
        logger.info(f"Loaded {len(self.tools)} tools from {len(self.config.enabled_categories)} categories")

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming MCP request.

        Args:
            request: JSON-RPC 2.0 request

        Returns:
            JSON-RPC 2.0 response
        """
        self.request_counter += 1
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        logger.info(f"Request #{self.request_counter}: {method} (id={request_id})")

        try:
            # Route request to appropriate handler
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_list_tools(params)
            elif method == "tools/call":
                result = self._handle_call_tool(params)
            elif method == "ping":
                result = {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
            else:
                return self._error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )

            return self._success_response(request_id, result)

        except Exception as e:
            logger.error(f"Error handling request: {e}\n{traceback.format_exc()}")
            return self._error_response(
                request_id,
                -32603,
                f"Internal error: {str(e)}"
            )

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle initialize request.

        Returns server capabilities and metadata.
        """
        return {
            "protocolVersion": self.PROTOCOL_VERSION,
            "serverInfo": {
                "name": "agentswarm-tools",
                "version": self.VERSION
            },
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            }
        }

    def _handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/list request.

        Returns list of all available tools with their schemas.
        """
        tools = []

        for tool_name, tool_class in self.tools.items():
            try:
                tool_schema = self.tool_registry.generate_tool_schema(tool_class)
                tools.append(tool_schema)
            except Exception as e:
                logger.error(f"Error generating schema for {tool_name}: {e}")
                continue

        logger.info(f"Listing {len(tools)} tools")
        return {"tools": tools}

    def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tools/call request.

        Executes a tool with provided arguments.

        Args:
            params: Must contain 'name' and 'arguments'

        Returns:
            Tool execution result
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            raise ValueError("Missing required parameter: name")

        logger.info(f"Calling tool: {tool_name} with args: {list(arguments.keys())}")

        # Get tool class
        tool_class = self.tools.get(tool_name)
        if not tool_class:
            raise ValueError(f"Tool not found: {tool_name}")

        # Execute tool
        try:
            result = self.tool_registry.execute_tool(tool_class, arguments)

            # Format response per MCP spec
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, default=str)
                    }
                ]
            }

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}\n{traceback.format_exc()}")

            # Return error in content
            error_result = {
                "success": False,
                "error": {
                    "code": "EXECUTION_ERROR",
                    "message": str(e),
                    "tool": tool_name
                }
            }

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(error_result, indent=2)
                    }
                ],
                "isError": True
            }

    def _success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """
        Create JSON-RPC 2.0 success response.

        Args:
            request_id: Request ID
            result: Response result

        Returns:
            JSON-RPC 2.0 response
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """
        Create JSON-RPC 2.0 error response.

        Args:
            request_id: Request ID
            code: Error code
            message: Error message

        Returns:
            JSON-RPC 2.0 error response
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    def run(self):
        """
        Run MCP server with stdio transport.

        Reads JSON-RPC requests from stdin and writes responses to stdout.
        """
        logger.info(f"MCP Server v{self.VERSION} started")
        logger.info(f"Ready to serve {len(self.tools)} tools")

        # Send ready signal
        sys.stderr.write("MCP Server ready\n")
        sys.stderr.flush()

        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse request
                    request = json.loads(line)

                    # Handle request
                    response = self.handle_request(request)

                    # Send response
                    output = json.dumps(response)
                    print(output)
                    sys.stdout.flush()

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    error_response = self._error_response(
                        None,
                        -32700,
                        "Parse error: Invalid JSON"
                    )
                    print(json.dumps(error_response))
                    sys.stdout.flush()

                except Exception as e:
                    logger.error(f"Error processing request: {e}\n{traceback.format_exc()}")
                    error_response = self._error_response(
                        None,
                        -32603,
                        f"Internal error: {str(e)}"
                    )
                    print(json.dumps(error_response))
                    sys.stdout.flush()

        except KeyboardInterrupt:
            logger.info("MCP Server shutting down (keyboard interrupt)")
        except Exception as e:
            logger.error(f"Fatal error: {e}\n{traceback.format_exc()}")
            sys.exit(1)


def main():
    """Main entry point for MCP server."""
    try:
        # Load configuration
        config = MCPConfig.load_from_file()

        # Create and run server
        server = MCPServer(config)
        server.run()

    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
