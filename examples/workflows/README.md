# Workflow Examples

This directory contains example workflows demonstrating the AgentSwarm Workflow Engine.

## Available Workflows

### 1. Research to Document (`research_to_document.json`)

**Purpose**: Research a topic and create a comprehensive document

**Steps**:
1. Search web for content (10 results)
2. Crawl each URL to extract content
3. Summarize the aggregated content
4. Create a document with the summary

**Variables**:
- `topic` - Research topic (default: "AI trends 2024")
- `max_results` - Number of search results (default: 10)

**Usage**:
```bash
python -m cli.workflow_builder --execute examples/workflows/research_to_document.json
```

**Estimated Time**: 5-10 minutes
**Tools Used**: web_search, crawler, summarize_large_document, create_agent

---

### 2. Media Analysis Pipeline (`media_analysis_pipeline.json`)

**Purpose**: Download videos from AI Drive, analyze them, and generate a report

**Steps**:
1. List files in specified folder
2. Download videos using foreach loop
3. Batch analyze video content
4. Transcribe audio from each video
5. Generate comprehensive report

**Variables**:
- `folder_path` - AI Drive folder path (default: "/research/videos")
- `report_title` - Report title (default: "Media Analysis Report")

**Usage**:
```bash
python -m cli.workflow_builder --execute examples/workflows/media_analysis_pipeline.json
```

**Estimated Time**: 15-30 minutes
**Tools Used**: aidrive_tool, batch_understand_videos, audio_transcribe, create_agent

---

### 3. Data Visualization (`data_visualization.json`)

**Purpose**: Load data from CSV and create interactive charts

**Steps**:
1. Read CSV file
2. Parse data to JSON
3. Aggregate by month
4. Generate chart (line or bar based on variable)
5. Save chart to outputs

**Variables**:
- `data_source` - Path to CSV file (default: "sales_data.csv")
- `chart_type` - Type of chart ("line" or "bar")

**Usage**:
```bash
python -m cli.workflow_builder --execute examples/workflows/data_visualization.json
```

**Estimated Time**: 1-2 minutes
**Tools Used**: Read, Bash, generate_line_chart/generate_bar_chart, Write

---

### 4. Batch Processing (`batch_processing.json`)

**Purpose**: Search multiple topics, aggregate results, and export

**Steps**:
1. Search multiple topics using foreach
2. Aggregate all results
3. Filter high-quality results (score > 0.7)
4. Generate summary document
5. Export to AI Drive
6. Create visualization of results

**Variables**:
- `topics` - Array of topics to search (default: ["AI", "ML", "DL", "Neural Networks"])
- `results_per_topic` - Results per topic (default: 5)
- `export_format` - Export format (default: "json")

**Usage**:
```bash
python -m cli.workflow_builder --execute examples/workflows/batch_processing.json
```

**Estimated Time**: 10-15 minutes
**Tools Used**: web_search, create_agent, aidrive_tool, generate_bar_chart

---

### 5. Email Automation (`email_automation.json`)

**Purpose**: Search emails, process attachments, and create summary

**Steps**:
1. Search Gmail with query
2. Read each email using foreach
3. Extract attachments from emails
4. Analyze and summarize content
5. Draft summary email

**Variables**:
- `search_query` - Gmail search query (default: "subject:report date:last_week")
- `max_emails` - Maximum emails to process (default: 20)

**Usage**:
```bash
python -m cli.workflow_builder --execute examples/workflows/email_automation.json
```

**Estimated Time**: 5-10 minutes
**Tools Used**: gmail_search, gmail_read, read_email_attachments, summarize_large_document, email_draft

---

### 6. Content Generation (`content_generation.json`)

**Purpose**: Generate images, video, and podcast about a topic

**Steps**:
1. Research topic with web search
2. Generate images in parallel (hero + thumbnail)
3. Create video with animation
4. Generate podcast script
5. Create podcast episode

**Variables**:
- `theme` - Content theme (default: "Future of AI")
- `aspect_ratio` - Video/image aspect ratio (default: "16:9")
- `duration` - Video duration in seconds (default: 30)

**Usage**:
```bash
python -m cli.workflow_builder --execute examples/workflows/content_generation.json
```

**Estimated Time**: 20-30 minutes
**Tools Used**: web_search, image_generation, video_generation, create_agent

---

## Running Workflows

### Method 1: CLI Workflow Builder

```bash
# Execute workflow
python -m cli.workflow_builder --execute path/to/workflow.json

# List available templates
python -m cli.workflow_builder --list-templates

# Load and modify template
python -m cli.workflow_builder --template research
```

### Method 2: Python API

```python
from shared.workflow import execute_workflow

# Execute from file
result = execute_workflow("examples/workflows/research_to_document.json")

# Or from dict
workflow = {
    "name": "my-workflow",
    "steps": [...]
}
result = execute_workflow(workflow)

print(result['success'])
print(result['results'])
```

### Method 3: WorkflowEngine Class

```python
from shared.workflow import WorkflowEngine

# Load workflow
engine = WorkflowEngine.from_file("workflow.json")

# Execute
result = engine.execute()

# Access results
for step_id, step_result in result['results'].items():
    print(f"{step_id}: {step_result}")
```

## Testing Workflows

### Mock Mode

Test workflows without making real API calls:

```bash
export USE_MOCK_APIS=true
python -m cli.workflow_builder --execute workflow.json
```

### Validation

Validate workflow structure without executing:

```python
from shared.workflow import WorkflowEngine

workflow = {...}
try:
    engine = WorkflowEngine(workflow)
    print("✓ Workflow is valid")
except Exception as e:
    print(f"✗ Validation failed: {e}")
```

## Customizing Workflows

### 1. Modify Variables

Edit the workflow JSON to change variables:

```json
{
  "variables": {
    "topic": "Your Custom Topic",
    "max_results": 20
  }
}
```

### 2. Add Steps

Add new steps to the workflow:

```json
{
  "steps": [
    ...,
    {
      "id": "new_step",
      "tool": "tool_name",
      "params": {...}
    }
  ]
}
```

### 3. Add Conditions

Make steps conditional:

```json
{
  "id": "optional_step",
  "tool": "tool_name",
  "params": {...},
  "condition": "${steps.previous.success}"
}
```

### 4. Modify Error Handling

Adjust retry and error behavior:

```json
{
  "error_handling": {
    "retry_on_failure": true,
    "max_retries": 5,
    "continue_on_error": true
  }
}
```

## Performance Tips

1. **Reduce Foreach Iterations**: Limit items in foreach loops
2. **Use Parallel Steps**: Execute independent steps in parallel
3. **Set Timeouts**: Adjust timeout based on workflow complexity
4. **Enable Caching**: Cache repeated operations

## Troubleshooting

### Workflow Fails to Execute

Check:
- All required tools are available
- Variables are properly defined
- Conditions reference valid steps
- API keys are configured

### Step Skipped

Check:
- Condition is correctly formatted
- Referenced steps exist
- Variable interpolation is correct

### Timeout Errors

Increase timeout:
```json
{
  "timeout": 3600  // 1 hour
}
```

## Creating Custom Workflows

Use the interactive builder:

```bash
python -m cli.workflow_builder
```

Follow the prompts to:
1. Define workflow metadata
2. Add variables
3. Configure steps
4. Set error handling
5. Save and test

## Documentation

- [Workflow Guide](../../docs/guides/WORKFLOWS.md) - Complete workflow documentation
- [Pipeline Guide](../../docs/guides/PIPELINES.md) - Alternative fluent API
- [Tool Reference](../../genspark_tools_documentation.md) - All available tools

## Support

For issues or questions:
1. Check the [documentation](../../docs/guides/WORKFLOWS.md)
2. Review [example workflows](.)
3. Test in mock mode first
4. Validate workflow structure
