# Web Content & Data Access

This directory contains tools for web content & data access.

## Tools in This Category

### crawler



### summarize_large_document



### url_metadata



### webpage_capture_screen



## Usage

Each tool follows the Agency Swarm BaseTool pattern:

```python
from tools.web_content.tool_name import ToolName

tool = ToolName(param1="value1", param2="value2")
result = tool.run()
```

## Documentation

See individual tool READMEs for detailed documentation:
- [crawler](./crawler/README.md)
- [summarize_large_document](./summarize_large_document/README.md)
- [url_metadata](./url_metadata/README.md)
- [webpage_capture_screen](./webpage_capture_screen/README.md)
