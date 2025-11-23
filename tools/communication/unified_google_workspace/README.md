# unified_google_workspace

Unified Google Workspace operations for Docs, Sheets, and Slides.

## Category

Communication & Productivity

## Parameters

- **workspace_type** (Literal["docs", "sheets", "slides"): Type of Google Workspace resource: 'docs', 'sheets', or 'slides' - **Required**
- **mode** (Literal["create", "modify"): Operation mode: 'create' to create new resource or 'modify' to update existing - **Required**
- **title** (str): No description - Optional
- **share_with** (List[str): List of email addresses to share the resource with - Optional
- **document_id** (str): No description - Optional
- **content** (str): No description - Optional
- **modify_action** (str): No description - Optional
- **insert_index** (int): No description - Optional
- **folder_id** (str): No description - Optional
- **spreadsheet_id** (str): No description - Optional
- **data** (List[List[Any): No description - Optional
- **sheet_name** (str): No description - Optional
- **formulas** (Dict[str, str): No description - Optional
- **formatting** (Dict[str, Any): No description - Optional
- **presentation_id** (str): No description - Optional
- **slides** (List[Dict[str, Any): No description - Optional
- **theme** (str): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

# Initialize the tool
tool = UnifiedGoogleWorkspace(
    workspace_type="example_value",
    mode="example_value",
    title="example_value"  # Optional
)

# Run the tool
result = tool.run()

# Check result
if result["success"]:
    print(result["result"])
else:
    print(f"Error: {result.get('error')}")
```

## Testing

Run tests with:
```bash
python unified_google_workspace.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
