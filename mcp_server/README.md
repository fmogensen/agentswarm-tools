# MCP Server for AgentSwarm Tools

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
USE_MOCK_APIS=false
CACHE_BACKEND=memory
```

### 3. Test the Server

```bash
# Test MCP server
python -m mcp_server
```

### 4. Configure Claude Desktop

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "agentswarm-tools": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/absolute/path/to/agentswarm-tools"
    }
  }
}
```

### 5. Restart Claude Desktop

Look for the hammer icon (🔨) to see available tools.

## Files

- `server.py` - Main MCP server implementation
- `tools.py` - Tool discovery and adaptation
- `config.py` - Configuration management
- `config.json` - Server configuration
- `__init__.py` - Package entry point

## Configuration

Edit `config.json`:

```json
{
  "enabled_categories": ["data", "communication", "media"],
  "max_tools": 0,
  "enable_analytics": true,
  "enable_caching": true,
  "log_level": "INFO"
}
```

## Testing

```bash
# Run MCP server tests
pytest tests/unit/mcp_server/ -v

# Test specific functionality
pytest tests/unit/mcp_server/test_server.py -v
```

## Logs

Server logs are written to:
- `/tmp/agentswarm_mcp_server.log`

## Documentation

See [MCP_SERVER.md](../docs/guides/MCP_SERVER.md) for complete documentation.
