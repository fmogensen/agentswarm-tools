# MCP Server Quick Start Guide

## 5-Minute Setup for Claude Desktop

### Step 1: Verify Installation
```bash
cd /path/to/agentswarm-tools
pip install -r requirements.txt
```

### Step 2: Test Server
```bash
python3 mcp_server/test_mcp.py
```

Expected output:
```
All tests passed! ✓
```

### Step 3: Configure Claude Desktop

**macOS**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Linux**: Edit `~/.config/Claude/claude_desktop_config.json`

**Windows**: Edit `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:
```json
{
  "mcpServers": {
    "agentswarm-tools": {
      "command": "python3",
      "args": ["-m", "mcp_server"],
      "cwd": "/ABSOLUTE/PATH/TO/agentswarm-tools"
    }
  }
}
```

**IMPORTANT**: Replace `/ABSOLUTE/PATH/TO/agentswarm-tools` with your actual path!

### Step 4: Add API Keys (Optional)

For tools that need API keys, add them to the `env` section:

```json
{
  "mcpServers": {
    "agentswarm-tools": {
      "command": "python3",
      "args": ["-m", "mcp_server"],
      "cwd": "/ABSOLUTE/PATH/TO/agentswarm-tools",
      "env": {
        "GOOGLE_SEARCH_API_KEY": "your_google_api_key",
        "GOOGLE_SEARCH_ENGINE_ID": "your_search_engine_id",
        "OPENAI_API_KEY": "your_openai_key"
      }
    }
  }
}
```

### Step 5: Restart Claude Desktop

Completely quit and restart Claude Desktop.

### Step 6: Verify Integration

1. Open Claude Desktop
2. Look for the hammer icon (🔨) at the bottom
3. Click it to see available tools
4. You should see 50+ AgentSwarm tools listed

## Quick Test

Ask Claude:
```
Can you list the available tools?
```

Claude should show you all the MCP tools available.

## Troubleshooting

### Tools not showing?

**Check server runs:**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"ping","params":{}}' | python3 -m mcp_server
```

Should return:
```json
{"jsonrpc": "2.0", "id": 1, "result": {"status": "ok", "timestamp": "..."}}
```

**Check config syntax:**
```bash
python3 -c "import json; print(json.load(open('claude_desktop_config.json')))"
```

**Check logs:**
```bash
tail -f /tmp/agentswarm_mcp_server.log
```

### Common Issues

1. **Path issues**: Use absolute paths, not relative
2. **Python command**: Try `python3` instead of `python`
3. **Restart**: Completely quit Claude Desktop (not just close window)
4. **Permissions**: Ensure Python can read the project directory

## Example Usage

### Web Search
```
Search for "Python machine learning tutorials"
```

### Chart Generation
```
Create a line chart showing: Jan=100, Feb=150, Mar=200
```

### File Operations
```
List files in /Users/yourname/Documents
```

## Next Steps

- Read full documentation: `/docs/guides/MCP_SERVER.md`
- Explore tool categories in config: `mcp_server/config.json`
- Run unit tests: `pytest tests/unit/mcp_server/ -v`
- Check implementation report: `MCP_IMPLEMENTATION_REPORT.md`

## Support

- Logs: `/tmp/agentswarm_mcp_server.log`
- Documentation: `docs/guides/MCP_SERVER.md`
- Test script: `mcp_server/test_mcp.py`
