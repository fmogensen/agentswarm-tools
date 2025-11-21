# Workspace Integration

This directory contains tools for workspace integration.

## Tools in This Category

### notion_read



### notion_search



## Usage

Each tool follows the Agency Swarm BaseTool pattern:

```python
from tools.workspace.tool_name import ToolName

tool = ToolName(param1="value1", param2="value2")
result = tool.run()
```

## Documentation

See individual tool READMEs for detailed documentation:
- [notion_read](./notion_read/README.md)
- [notion_search](./notion_search/README.md)
