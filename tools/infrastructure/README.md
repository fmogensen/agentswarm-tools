# Infrastructure Tools

Tools for code execution, storage management, and agent/task orchestration.

## Subcategories

### Execution (`execution/`)
Code execution and environment interaction tools.

**Tools:**
- `bash_tool` - Execute shell commands in sandbox environment
- `read_tool` - Read files from filesystem
- `write_tool` - Write files to filesystem
- `multiedit_tool` - Edit multiple files simultaneously
- `downloadfilewrapper_tool` - Download files from URLs

### Storage (`storage/`)
File storage and cloud storage management.

**Tools:**
- `aidrive_tool` - Interact with AI Drive cloud storage
- `file_format_converter` - Convert between file formats
- `onedrive_search` - Search OneDrive files
- `onedrive_file_read` - Read files from OneDrive

### Management (`management/`)
Agent and task management tools.

**Tools:**
- `agent_status` - Check agent status and health
- `task_queue_manager` - Manage task queues and scheduling

## Category Identifier

All tools in this category have:
```python
tool_category: str = "infrastructure"
```

## Usage Examples

### Execute a command:
```python
from tools.infrastructure.execution.bash_tool import BashTool

tool = BashTool(
    command="python script.py",
    working_directory="/mnt/user-data"
)
result = tool.run()
```

### Read a file:
```python
from tools.infrastructure.execution.read_tool import ReadTool

tool = ReadTool(
    file_path="/mnt/aidrive/data.json"
)
result = tool.run()
```

### Access AI Drive:
```python
from tools.infrastructure.storage.aidrive_tool import AIDriveTool

tool = AIDriveTool(
    action="list",
    path="/documents"
)
result = tool.run()
```

### Convert file format:
```python
from tools.infrastructure.storage.file_format_converter import FileFormatConverter

tool = FileFormatConverter(
    input_path="document.docx",
    output_format="pdf"
)
result = tool.run()
```

### Check agent status:
```python
from tools.infrastructure.management.agent_status import AgentStatus

tool = AgentStatus(
    agent_id="agent-123"
)
result = tool.run()
```
