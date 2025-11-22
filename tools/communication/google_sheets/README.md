# Google Sheets Tool

Create and modify Google Sheets using the Google Sheets API v4.

## Features

- **Create Mode**: Create new Google Spreadsheets with data, formulas, and formatting
- **Modify Mode**: Update existing spreadsheets with new data
- **Formulas**: Apply Excel-like formulas to cells
- **Formatting**: Apply cell formatting (bold, colors, number formats)
- **Sharing**: Share spreadsheets with specific users via email
- **Mock Mode**: Test without real API calls

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mode` | str | Yes | Operation mode: "create" or "modify" |
| `data` | List[List[Any]] | Yes | List of lists representing rows and columns |
| `title` | str | Conditional | Spreadsheet title (required for create mode) |
| `spreadsheet_id` | str | Conditional | Google Sheets ID (required for modify mode) |
| `sheet_name` | str | No | Worksheet name (default: "Sheet1") |
| `formulas` | Dict[str, str] | No | Cell formulas mapping (e.g., {"A1": "=SUM(B1:B10)"}) |
| `formatting` | Dict[str, Any] | No | Formatting options (colors, bold, etc.) |
| `share_with` | List[str] | No | Email addresses to share with |

## Setup

### 1. Install Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Create Service Account Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sheets API and Google Drive API
4. Create Service Account credentials
5. Download JSON credentials file

### 3. Set Environment Variable

```bash
export GOOGLE_SHEETS_CREDENTIALS=/path/to/credentials.json
```

## Usage Examples

### Create New Spreadsheet

```python
from tools.communication.google_sheets import GoogleSheets

tool = GoogleSheets(
    mode="create",
    title="Sales Report Q4 2024",
    data=[
        ["Product", "Q1", "Q2", "Q3", "Q4"],
        ["Widget A", 1000, 1200, 1100, 1500],
        ["Widget B", 800, 900, 950, 1000]
    ],
    sheet_name="Sales Data",
    formulas={"F2": "=SUM(B2:E2)", "F3": "=SUM(B3:E3)"},
    formatting={"bold_header": True},
    share_with=["manager@company.com"]
)

result = tool.run()
print(f"Spreadsheet URL: {result['result']['spreadsheet_url']}")
```

### Modify Existing Spreadsheet

```python
tool = GoogleSheets(
    mode="modify",
    spreadsheet_id="1ABC123XYZ...",
    data=[
        ["Updated Product", "New Value"],
        ["Widget C", 2000]
    ],
    sheet_name="Sheet1",
    formulas={"C1": "=SUM(B2:B3)"}
)

result = tool.run()
```

### Complex Formatting Example

```python
tool = GoogleSheets(
    mode="create",
    title="Formatted Report",
    data=[["Header1", "Header2"], ["Data1", "Data2"]],
    formatting={
        "bold_header": True,
        "background_color": {
            "red": 1.0,
            "green": 0.9,
            "blue": 0.9,
            "alpha": 1.0
        },
        "range": {
            "startRow": 0,
            "endRow": 1,
            "startCol": 0,
            "endCol": 2
        }
    }
)

result = tool.run()
```

## Return Value

```python
{
    "success": True,
    "result": {
        "spreadsheet_id": "1ABC...",
        "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1ABC.../edit",
        "title": "Sales Report Q4 2024",  # create mode only
        "mode": "create",  # or "modify"
        "status": "created",  # or "modified"
        "rows_written": 4,
        "columns_written": 5,
        "sheet_name": "Sales Data",
        "formulas_applied": 2,
        "shared_with": ["manager@company.com"]
    },
    "metadata": {
        "tool_name": "google_sheets",
        "mode": "create",
        "mock_mode": False
    }
}
```

## Formula Examples

```python
# Sum formula
formulas = {"C1": "=SUM(A1:B1)"}

# Average formula
formulas = {"C1": "=AVERAGE(A1:A10)"}

# Complex formula
formulas = {
    "D2": "=SUM(B2:C2)",
    "D3": "=SUM(B3:C3)",
    "D4": "=AVERAGE(D2:D3)"
}
```

## Formatting Options

### Bold Header Row

```python
formatting = {"bold_header": True}
```

### Background Color

```python
formatting = {
    "background_color": {
        "red": 1.0,    # 0.0 - 1.0
        "green": 0.9,  # 0.0 - 1.0
        "blue": 0.9,   # 0.0 - 1.0
        "alpha": 1.0   # 0.0 - 1.0
    },
    "range": {
        "startRow": 0,
        "endRow": 1,
        "startCol": 0,
        "endCol": 3
    }
}
```

## Testing

### Mock Mode

```bash
export USE_MOCK_APIS=true
python google_sheets.py
```

### Run Unit Tests

```bash
pytest test_google_sheets.py -v
```

### Run All Tests

```bash
pytest test_google_sheets.py -v --cov=google_sheets
```

## Error Handling

The tool handles various error scenarios:

- **ValidationError**: Invalid parameters (wrong mode, missing required fields)
- **ConfigurationError**: Missing or invalid credentials
- **APIError**: Google Sheets API failures

Example error response:

```python
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Title is required for create mode",
        "tool": "google_sheets",
        "details": {...},
        "request_id": "..."
    }
}
```

## Common Issues

### Credentials Not Found

```
ConfigurationError: Missing environment variable: GOOGLE_SHEETS_CREDENTIALS
```

**Solution**: Set the environment variable to point to your credentials file.

### Permission Denied

```
APIError: Google Sheets API error: 403
```

**Solution**: Ensure the Google Sheets API and Google Drive API are enabled in your Google Cloud project.

### Invalid Spreadsheet ID

```
APIError: Google Sheets API error: 404
```

**Solution**: Verify the spreadsheet ID is correct and the service account has access.

## API Scopes Required

The tool requires these OAuth scopes:

- `https://www.googleapis.com/auth/spreadsheets` - Read/write spreadsheets
- `https://www.googleapis.com/auth/drive.file` - Access Drive files created by the app

## Best Practices

1. **Use Service Account**: For automated tools, use service account credentials
2. **Share Spreadsheets**: If users need access, use the `share_with` parameter
3. **Batch Operations**: Combine multiple updates in a single call when possible
4. **Error Handling**: Always check the `success` field in the response
5. **Test First**: Use mock mode to test before making real API calls

## Limitations

- Maximum 10 million cells per spreadsheet
- Maximum 200 sheets per spreadsheet
- Rate limits apply (100 requests per 100 seconds per user)
- Formulas must use English function names

## Related Tools

- `gmail_search`: Search Gmail messages
- `gmail_read`: Read email content
- `google_calendar_create_event_draft`: Create calendar events
- `google_calendar_list`: List calendar events

## License

Part of the AgentSwarm Tools Framework.
