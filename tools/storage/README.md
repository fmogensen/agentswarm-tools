# File & Storage Management

This directory contains tools for file & storage management.

## Tools in This Category

### aidrive_tool



### file_format_converter



### onedrive_file_read

Read and process OneDrive/SharePoint files, answer questions about content

### onedrive_search



## Usage

Each tool follows the Agency Swarm BaseTool pattern:

```python
from tools.storage.tool_name import ToolName

tool = ToolName(param1="value1", param2="value2")
result = tool.run()
```

## Documentation

See individual tool READMEs for detailed documentation:
- [aidrive_tool](./aidrive_tool/README.md)
- [file_format_converter](./file_format_converter/README.md)
- [onedrive_file_read](./onedrive_file_read/README.md)
- [onedrive_search](./onedrive_search/README.md)
