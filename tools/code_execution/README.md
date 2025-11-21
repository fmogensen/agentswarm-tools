# Code Execution Environment

This directory contains tools for code execution environment.

## Tools in This Category

### bash_tool



### downloadfilewrapper_tool



### multiedit_tool



### read_tool



### write_tool



## Usage

Each tool follows the Agency Swarm BaseTool pattern:

```python
from tools.code_execution.tool_name import ToolName

tool = ToolName(param1="value1", param2="value2")
result = tool.run()
```

## Documentation

See individual tool READMEs for detailed documentation:
- [bash_tool](./bash_tool/README.md)
- [downloadfilewrapper_tool](./downloadfilewrapper_tool/README.md)
- [multiedit_tool](./multiedit_tool/README.md)
- [read_tool](./read_tool/README.md)
- [write_tool](./write_tool/README.md)
