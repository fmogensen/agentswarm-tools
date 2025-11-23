# MCP Server for AgentSwarm Tools

## Overview

The MCP (Model Context Protocol) Server enables Claude Desktop and other MCP-compatible clients to access all 100+ AgentSwarm tools. This integration allows Claude to directly execute tools like web search, media generation, file operations, and data visualization within conversations.

## Features

- **100+ Tools**: Access to all AgentSwarm tools across 7 categories
- **Auto-Discovery**: Automatically discovers and registers all available tools
- **Schema Generation**: Converts Pydantic models to JSON Schema for MCP
- **Error Handling**: Comprehensive error handling per MCP specification
- **Caching**: Optional result caching for improved performance
- **Analytics**: Built-in usage tracking and analytics

## Architecture

```
Claude Desktop (MCP Client)
    ↓
stdio (JSON-RPC 2.0)
    ↓
MCP Server (mcp_server/server.py)
    ↓
Tool Registry (mcp_server/tools.py)
    ↓
AgentSwarm Tools (100+ tools)
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Mock mode (for testing without API keys)
USE_MOCK_APIS=false

# Caching
CACHE_BACKEND=memory  # or 'redis' or 'none'
REDIS_URL=redis://localhost:6379

# API Keys (as needed for specific tools)
GOOGLE_SEARCH_API_KEY=your_key_here
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
OPENAI_API_KEY=your_key_here
# ... add other API keys as needed
```

### 3. Test MCP Server

Test the server standalone:

```bash
# Start the server
python -m mcp_server

# In another terminal, send a test request
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python -m mcp_server
```

## Claude Desktop Configuration

### macOS/Linux

1. Locate Claude Desktop config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add AgentSwarm Tools MCP server configuration:

```json
{
  "mcpServers": {
    "agentswarm-tools": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/absolute/path/to/agentswarm-tools",
      "env": {
        "USE_MOCK_APIS": "false",
        "CACHE_BACKEND": "memory",
        "GOOGLE_SEARCH_API_KEY": "your_key_here",
        "GOOGLE_SEARCH_ENGINE_ID": "your_engine_id"
      }
    }
  }
}
```

3. Restart Claude Desktop

4. Verify connection:
   - Look for the hammer icon (🔨) in Claude Desktop
   - Click it to see available tools
   - You should see all AgentSwarm tools listed

### Windows

1. Locate config file: `%APPDATA%\Claude\claude_desktop_config.json`

2. Use the same configuration as above but with Windows-style path:

```json
{
  "mcpServers": {
    "agentswarm-tools": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "C:\\Users\\YourName\\path\\to\\agentswarm-tools",
      "env": {
        "USE_MOCK_APIS": "false"
      }
    }
  }
}
```

## Configuration

### Server Configuration

Edit `mcp_server/config.json`:

```json
{
  "server_name": "agentswarm-tools",
  "server_version": "1.0.0",
  "enabled_categories": [
    "data",
    "communication",
    "media",
    "visualization",
    "content",
    "infrastructure",
    "utils"
  ],
  "max_tools": 0,
  "enable_analytics": true,
  "enable_caching": true,
  "log_level": "INFO"
}
```

**Configuration Options:**

- `enabled_categories`: List of tool categories to expose (remove unwanted categories)
- `max_tools`: Maximum number of tools to expose (0 = unlimited)
- `enable_analytics`: Enable usage tracking
- `enable_caching`: Enable result caching
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Category-Specific Configuration

To expose only specific categories:

```json
{
  "enabled_categories": ["data", "visualization"]
}
```

This would only expose search tools and chart generation tools.

## Usage Examples

### Example 1: Web Search via Claude Desktop

In Claude Desktop:

```
User: Search for "Python machine learning tutorials"

Claude: I'll search for that using the web_search tool.
[Executes web_search tool via MCP]

Here are the top results for Python machine learning tutorials:
1. "Complete Guide to Machine Learning in Python"
   https://example.com/ml-guide
   A comprehensive tutorial covering...
...
```

### Example 2: Generate Chart

```
User: Create a line chart showing sales data for Q1 2024

Claude: I'll create a line chart with that data.
[Executes generate_line_chart tool via MCP]

I've created a line chart showing your Q1 2024 sales data.
[Returns chart visualization]
```

### Example 3: Tool Chaining

```
User: Search for "climate change data", then create a visualization

Claude:
1. First, I'll search for climate change data
   [Executes web_search]

2. Now I'll create a visualization with this data
   [Executes generate_line_chart]

Here's a chart showing climate change trends based on the search results.
```

## MCP Protocol Details

### Request Format

All requests follow JSON-RPC 2.0 format:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "web_search",
    "arguments": {
      "query": "Python tutorials",
      "max_results": 5
    }
  }
}
```

### Response Format

Success response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"result\": [...], \"metadata\": {...}}"
      }
    ]
  }
}
```

Error response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Tool execution failed: Missing API key"
  }
}
```

### Supported Methods

| Method | Description |
|--------|-------------|
| `initialize` | Initialize connection and get server capabilities |
| `tools/list` | List all available tools with schemas |
| `tools/call` | Execute a tool with parameters |
| `ping` | Health check |

## Tool Categories

The MCP server exposes tools from these categories:

1. **Data** (13 tools)
   - Search: web_search, scholar_search, image_search, video_search, product_search
   - Business: data_aggregator, report_generator, trend_analyzer
   - Intelligence: rag_pipeline, deep_research

2. **Communication** (23 tools)
   - Email: gmail_search, gmail_read, email_draft
   - Calendar: google_calendar_list, google_calendar_create_event_draft
   - Workspace: notion_search, notion_read, slack integration
   - Phone: phone_call, query_call_logs

3. **Media** (20 tools)
   - Generation: image_generation, video_generation, audio_generation
   - Analysis: understand_images, understand_video, audio_transcribe
   - Processing: merge_audio, extract_audio_from_video

4. **Visualization** (16 tools)
   - Charts: line, bar, pie, scatter, area, column, dual axes
   - Diagrams: fishbone, flow diagram, mind map, network graph
   - Advanced: radar, treemap, word cloud, histogram

5. **Content** (10 tools)
   - Documents: create_agent (docs, slides, sheets)
   - Web: crawler, summarize_large_document, webpage_capture_screen

6. **Infrastructure** (11 tools)
   - Execution: Bash, Read, Write, MultiEdit
   - Storage: aidrive_tool, file_format_converter, onedrive tools

7. **Utils** (8 tools)
   - think, ask_for_clarification, create_profile

## Troubleshooting

### Server Not Starting

1. Check Python version (3.8+):
   ```bash
   python --version
   ```

2. Verify dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check logs:
   ```bash
   tail -f /tmp/agentswarm_mcp_server.log
   ```

### Tools Not Appearing in Claude Desktop

1. Verify MCP server is running:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"ping","params":{}}' | python -m mcp_server
   ```

2. Check Claude Desktop config:
   - Correct path in `cwd`
   - Proper JSON formatting
   - No syntax errors

3. Restart Claude Desktop completely

4. Check Claude Desktop logs (Help → View Logs)

### Tool Execution Errors

1. **Missing API Keys**
   - Add required API keys to Claude Desktop config `env` section
   - Or add to `.env` file in project root

2. **Tool Not Found**
   - Check tool name spelling
   - Verify category is enabled in `config.json`

3. **Permission Errors**
   - Ensure Python has read/write permissions
   - Check file ownership

### Performance Issues

1. **Enable Caching**
   ```json
   "env": {
     "CACHE_BACKEND": "redis",
     "REDIS_URL": "redis://localhost:6379"
   }
   ```

2. **Reduce Tool Count**
   - Limit `enabled_categories` in config
   - Set `max_tools` limit

3. **Optimize Logging**
   - Set `log_level` to "WARNING" or "ERROR"

## Development

### Adding New Tools

New tools are automatically discovered by the MCP server. Just create a tool following the AgentSwarm pattern:

```python
from shared.base import BaseTool
from pydantic import Field

class MyTool(BaseTool):
    """Tool description for MCP schema"""

    tool_name: str = "my_tool"
    tool_category: str = "utils"

    param1: str = Field(..., description="Parameter description")

    def _execute(self):
        return {"result": "success"}
```

The tool will automatically appear in `tools/list` after server restart.

### Testing Tools via MCP

```bash
# List all tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python -m mcp_server

# Call a tool
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"web_search","arguments":{"query":"test","max_results":3}}}' | python -m mcp_server
```

### Custom MCP Server

Create a custom MCP server with specific tools:

```python
from mcp_server import MCPServer, MCPConfig

# Custom configuration
config = MCPConfig(
    enabled_categories=["data", "visualization"],
    max_tools=20,
    enable_caching=True
)

# Create and run server
server = MCPServer(config)
server.run()
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
   - Use environment variables
   - Use Claude Desktop config `env` section
   - Use `.env` file (gitignored)

2. **Rate Limiting**: Built-in rate limiting prevents API abuse
   - Configure in individual tools
   - Monitor via analytics

3. **Input Validation**: All tool inputs are validated via Pydantic
   - Type checking
   - Constraint validation
   - Sanitization

4. **Sandboxing**: Code execution tools (Bash) should be used cautiously
   - Review commands before execution
   - Use read-only mode when possible

## Advanced Features

### Custom Tool Discovery

Modify `mcp_server/tools.py` to customize tool discovery:

```python
def _discover_category_tools(self, category: str):
    # Custom logic for filtering tools
    tools = super()._discover_category_tools(category)

    # Filter by name pattern
    return {k: v for k, v in tools.items() if k.startswith("my_")}
```

### Analytics Integration

Enable analytics to track tool usage:

```python
# In config.json
{
  "enable_analytics": true
}

# Analytics events are recorded automatically
# Query via shared.analytics module
```

### Caching Strategies

Configure caching per tool category:

```python
# In tool class
class MyTool(BaseTool):
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_key_params: list = ["query"]  # Cache key based on query param
```

## MCP Ecosystem Integration

The MCP server can be used alongside other MCP servers:

```json
{
  "mcpServers": {
    "agentswarm-tools": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/agentswarm-tools"
    },
    "other-mcp-server": {
      "command": "node",
      "args": ["/path/to/other-server/index.js"]
    }
  }
}
```

This allows Claude to access tools from multiple sources simultaneously.

## Performance Benchmarks

Typical performance metrics:

- **Tool Discovery**: ~2-3 seconds for 100+ tools
- **Schema Generation**: ~50ms per tool
- **Tool Execution**: Varies by tool (API-dependent)
- **Request/Response**: ~10-20ms overhead

## Roadmap

Future enhancements:

- [ ] Tool permissions and access control
- [ ] Tool usage quotas
- [ ] Streaming responses for long-running tools
- [ ] Tool composition/chaining
- [ ] Web UI for configuration
- [ ] Tool marketplace integration

## Resources

- [MCP Specification](https://modelcontextprotocol.io/docs/specification)
- [Claude Desktop Documentation](https://claude.ai/docs)
- [AgentSwarm Tools Documentation](../../README.md)
- [Agency Swarm Framework](https://github.com/VRSEN/agency-swarm)

## Support

For issues and questions:

1. Check logs: `/tmp/agentswarm_mcp_server.log`
2. Review troubleshooting section
3. Check GitHub issues
4. Contact support

## License

Same license as AgentSwarm Tools Framework.
