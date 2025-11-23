# Pipeline Builder Guide

Complete guide to building fluent tool pipelines in AgentSwarm Tools Framework.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Pipeline API](#pipeline-api)
- [Data Transformation](#data-transformation)
- [Error Handling](#error-handling)
- [Pipeline Decorator](#pipeline-decorator)
- [Parallel Pipelines](#parallel-pipelines)
- [Example Pipelines](#example-pipelines)
- [Best Practices](#best-practices)

## Overview

The Pipeline Builder provides a fluent, chainable API for composing tools:

- **Method Chaining**: Readable, expressive pipeline definitions
- **Automatic Data Flow**: Results automatically pass between steps
- **Transformation Functions**: Map, filter, reduce operations
- **Error Handling**: Catch and handle errors gracefully
- **Conditional Logic**: Execute steps conditionally
- **Parallel Execution**: Run multiple pipelines simultaneously

## Getting Started

### Basic Pipeline

```python
from shared.pipeline import Pipeline

# Create and execute pipeline
result = (
    Pipeline("research-pipeline")
    .add_step("search", web_search, query="AI trends")
    .add_step("process", lambda data: process_results(data))
    .add_step("save", save_to_file, filename="results.json")
    .execute()
)

print(result['success'])  # True/False
print(result['result'])   # Final result
```

### Step-by-Step Construction

```python
pipeline = Pipeline("data-pipeline")

# Add steps
pipeline.add_step("fetch", fetch_data, source="api")
pipeline.add_step("clean", clean_data)
pipeline.add_step("visualize", generate_chart)

# Execute
result = pipeline.execute()
```

## Pipeline API

### Creating Pipelines

```python
from shared.pipeline import Pipeline

# Create named pipeline
pipeline = Pipeline("my-pipeline")

# Or use default name
pipeline = Pipeline()
```

### Adding Steps

#### add_step()

Add any callable (function, tool class, or tool name):

```python
# Function
pipeline.add_step("process", process_function, param1="value")

# Tool class
from tools.search.web_search import WebSearch
pipeline.add_step("search", WebSearch, query="AI")

# Tool name (from registry)
pipeline.add_step("search", "web_search", query="AI")
```

#### add_tool()

Add tool by name from registry:

```python
pipeline.add_tool("search", "web_search", query="AI trends")
pipeline.add_tool("analyze", "crawler", url="https://example.com")
```

#### add_function()

Add a regular Python function:

```python
def process_data(data, threshold=0.5):
    return [item for item in data if item['score'] > threshold]

pipeline.add_function("filter", process_data, threshold=0.7)
```

### Executing Pipelines

```python
# Execute with no initial data
result = pipeline.execute()

# Execute with initial data
result = pipeline.execute(initial_data={"key": "value"})

# Or use pipeline as callable
result = pipeline(initial_data)
```

### Pipeline Result

```python
{
    "success": True,
    "pipeline_name": "my-pipeline",
    "result": <final result>,
    "error": None,  # or error message
    "steps": [
        {
            "name": "search",
            "success": True,
            "duration_ms": 123.45
        },
        ...
    ],
    "total_steps": 3,
    "steps_completed": 3,
    "duration_ms": 456.78,
    "timestamp": "2024-11-23T12:00:00Z"
}
```

## Data Transformation

### Map

Transform each item in a collection:

```python
pipeline = (
    Pipeline("transform")
    .add_step("search", web_search, query="AI")
    .add_function("extract", lambda data: data['results'])
    .map("get_urls", lambda item: item['url'])
)

# Results flow:
# search -> [{url: "..."}, ...]
# extract -> [{url: "..."}, ...]
# map -> ["url1", "url2", ...]
```

### Filter

Keep only items matching a condition:

```python
pipeline = (
    Pipeline("filter")
    .add_step("search", web_search, query="AI")
    .add_function("extract", lambda data: data['results'])
    .filter("high_score", lambda item: item['score'] > 0.8)
)

# Only items with score > 0.8 remain
```

### Reduce

Combine items into a single value:

```python
pipeline = (
    Pipeline("aggregate")
    .add_step("search", web_search, query="AI")
    .add_function("extract", lambda data: data['results'])
    .map("scores", lambda item: item['score'])
    .reduce("sum", lambda acc, score: acc + score, initial=0)
)

# Results: sum of all scores
```

### Conditional Steps

Execute step only if condition is true:

```python
pipeline = (
    Pipeline("conditional")
    .add_step("search", web_search, query="AI")
    .conditional(
        "check_results",
        condition=lambda data: len(data['results']) > 0,
        then_step=lambda data: process_results(data),
        else_step=lambda data: "No results found"
    )
)
```

### Transform Functions

Apply custom transformations:

```python
# Add transform to any step
pipeline.add_step(
    "search",
    web_search,
    transform=lambda result: result['results'][:10],  # Take first 10
    query="AI"
)
```

## Error Handling

### Error Handlers

Add error handlers to catch and handle exceptions:

```python
def handle_error(error):
    print(f"Pipeline failed: {error}")
    # Log, notify, etc.

pipeline = (
    Pipeline("robust")
    .add_step("risky", risky_operation)
    .on_error(handle_error)
    .execute()
)
```

### Multiple Error Handlers

```python
pipeline = (
    Pipeline("multi-error")
    .on_error(lambda e: logger.error(e))
    .on_error(lambda e: send_notification(e))
    .on_error(lambda e: save_error_to_db(e))
)
```

### Continue on Error

Continue executing even if a step fails:

```python
pipeline = (
    Pipeline("resilient")
    .continue_on_error_mode(True)
    .add_step("step1", might_fail)
    .add_step("step2", will_run_anyway)
    .execute()
)

# Both steps execute even if step1 fails
```

### Error Recovery

```python
def safe_search(query):
    try:
        return web_search(query)
    except Exception:
        return {"results": []}  # Fallback

pipeline = (
    Pipeline("safe")
    .add_step("search", safe_search, query="AI")
    .execute()
)
```

## Pipeline Decorator

Convert functions into pipelines:

```python
from shared.pipeline import pipeline_builder

@pipeline_builder
def research_workflow(topic: str):
    # Search for content
    results = web_search(query=topic)

    # Extract URLs
    urls = [item['url'] for item in results['results']]

    # Crawl content
    content = crawler(urls=urls)

    # Create document
    document = create_agent(
        agent_type="docs",
        title=f"Research: {topic}",
        content=content
    )

    return document

# Execute as pipeline
result = research_workflow("AI trends")
print(result['success'])
print(result['result'])
```

### Benefits

- Automatic error handling
- Performance tracking
- Consistent result format
- Easy to test and debug

## Parallel Pipelines

Execute multiple pipelines simultaneously:

```python
from shared.pipeline import ParallelPipeline

# Create pipelines
web_pipeline = (
    Pipeline("web")
    .add_tool("search", "web_search", query="AI")
)

scholar_pipeline = (
    Pipeline("scholar")
    .add_tool("search", "scholar_search", query="AI")
)

image_pipeline = (
    Pipeline("images")
    .add_tool("search", "image_search", query="AI")
)

# Execute in parallel
parallel = (
    ParallelPipeline("multi-search")
    .add_pipeline(web_pipeline)
    .add_pipeline(scholar_pipeline)
    .add_pipeline(image_pipeline)
)

result = parallel.execute()

# Access results from each pipeline
for pipeline_result in result['results']:
    print(f"{pipeline_result['pipeline_name']}: {pipeline_result['success']}")
```

Note: Currently simulates parallel execution. True parallel execution (threading/async) coming soon.

## Example Pipelines

### 1. Research Pipeline

Search, crawl, and create document:

```python
research_pipeline = (
    Pipeline("research")
    .add_tool("search", "web_search", query="AI trends 2024", max_results=10)
    .add_function("extract_urls", lambda data: [r['url'] for r in data['results']])
    .add_tool("crawl", "crawler", urls="${data}")  # Uses previous result
    .add_tool("summarize", "summarize_large_document", content="${data}")
    .add_tool("document", "create_agent",
        agent_type="docs",
        title="AI Trends Report",
        content="${data}")
    .on_error(lambda e: print(f"Failed: {e}"))
    .execute()
)
```

### 2. Data Processing Pipeline

Load, clean, and visualize data:

```python
data_pipeline = (
    Pipeline("data-viz")
    .add_function("load", load_csv_file, filepath="sales.csv")
    .filter("valid_rows", lambda row: row.get('amount') is not None)
    .map("parse_amounts", lambda row: {**row, 'amount': float(row['amount'])})
    .add_function("aggregate", aggregate_by_month)
    .add_tool("chart", "generate_line_chart",
        title="Monthly Sales",
        axisXTitle="Month",
        axisYTitle="Sales ($)")
    .execute()
)
```

### 3. Media Analysis Pipeline

Download and analyze videos:

```python
media_pipeline = (
    Pipeline("media-analysis")
    .add_tool("list", "aidrive_tool", action="list_directory", path="/videos")
    .add_function("extract_files", lambda data: data['files'])
    .filter("videos_only", lambda file: file['name'].endswith('.mp4'))
    .map("get_urls", lambda file: file['url'])
    .add_tool("analyze", "batch_understand_videos",
        video_urls="${data}",
        instruction="Identify key themes")
    .add_tool("transcribe", "audio_transcribe", audio_url="${data}")
    .add_tool("report", "create_agent",
        agent_type="docs",
        title="Media Analysis Report",
        content="${data}")
    .execute()
)
```

### 4. Email Processing Pipeline

Search, read, and summarize emails:

```python
email_pipeline = (
    Pipeline("email-summary")
    .add_tool("search", "gmail_search",
        query="subject:report date:last_week",
        max_results=20)
    .add_function("extract_ids", lambda data: [e['id'] for e in data['emails']])
    .map("read_email", lambda msg_id: gmail_read(message_id=msg_id))
    .map("get_content", lambda email: email['body'])
    .add_tool("summarize", "summarize_large_document",
        content="${data}",
        max_length=500)
    .add_tool("draft", "email_draft",
        to="manager@company.com",
        subject="Weekly Email Summary",
        body="${data}")
    .execute()
)
```

### 5. Content Generation Pipeline

Generate multi-modal content:

```python
content_pipeline = (
    Pipeline("content-gen")
    .add_tool("research", "web_search", query="Future of AI", max_results=10)
    .add_function("extract_insights", extract_key_insights)

    # Generate images
    .add_tool("hero_image", "image_generation",
        model="flux-pro",
        query="Future of AI visualization",
        aspect_ratio="16:9")

    # Generate video
    .add_tool("video", "video_generation",
        model="gemini/veo3",
        query="AI technology animation",
        duration=30)

    # Create podcast
    .add_tool("podcast", "create_agent",
        agent_type="podcast",
        title="Future of AI Discussion",
        content="${data}")

    .on_error(lambda e: logger.error(f"Content generation failed: {e}"))
    .execute()
)
```

### 6. Batch Processing Pipeline

Process multiple items:

```python
topics = ["AI", "Machine Learning", "Deep Learning"]

batch_pipeline = (
    Pipeline("batch-search")
    .add_function("set_topics", lambda: topics)
    .map("search_topic", lambda topic: web_search(query=topic, max_results=5))
    .add_function("flatten_results",
        lambda results: [item for sublist in results for item in sublist])
    .filter("high_quality", lambda item: item.get('score', 0) > 0.7)
    .add_function("aggregate", aggregate_results)
    .add_tool("visualize", "generate_bar_chart",
        title="Results by Topic",
        data="${data}")
    .execute()
)
```

### 7. Testing Pipeline

Validate data processing:

```python
test_pipeline = (
    Pipeline("testing")
    .add_function("load_test_data", load_test_dataset)
    .add_function("validate_schema", validate_data_schema)
    .conditional(
        "check_valid",
        condition=lambda data: data['valid'],
        then_step=lambda data: process_data(data),
        else_step=lambda data: {"error": "Invalid schema"}
    )
    .add_function("assert_results", assert_expected_output)
    .execute()
)
```

## Best Practices

### 1. Use Descriptive Names

```python
# Good
Pipeline("user-registration")
    .add_step("validate_email", validate_email)
    .add_step("check_existing", check_user_exists)
    .add_step("create_account", create_user)

# Bad
Pipeline("pipeline")
    .add_step("step1", validate_email)
    .add_step("step2", check_user_exists)
```

### 2. Keep Steps Small and Focused

```python
# Good - Single responsibility per step
Pipeline("data-processing")
    .add_step("load", load_data)
    .add_step("clean", clean_data)
    .add_step("transform", transform_data)
    .add_step("save", save_data)

# Bad - Too much in one step
Pipeline("data-processing")
    .add_step("do_everything", load_clean_transform_save)
```

### 3. Handle Errors Explicitly

```python
pipeline = (
    Pipeline("robust")
    .add_step("risky", risky_operation)
    .on_error(lambda e: logger.error(e))
    .on_error(lambda e: send_alert(e))
    .continue_on_error_mode(True)
)
```

### 4. Use Transformations for Data Shaping

```python
pipeline = (
    Pipeline("transform")
    .add_step("search", web_search)
    .add_function("extract", lambda data: data['results'])  # Extract
    .filter("valid", lambda item: item.get('url'))          # Filter
    .map("urls", lambda item: item['url'])                  # Map
    .reduce("join", lambda acc, url: acc + "\n" + url)      # Reduce
)
```

### 5. Test Pipelines in Isolation

```python
# Test individual steps
def test_search_step():
    result = web_search(query="test")
    assert result['success']

# Test full pipeline
def test_full_pipeline():
    os.environ["USE_MOCK_APIS"] = "true"
    result = my_pipeline.execute()
    assert result['success']
```

### 6. Use Pipeline Decorator for Readability

```python
@pipeline_builder
def user_onboarding(email: str):
    # Clear, sequential logic
    user = validate_email(email)
    existing = check_database(user['email'])
    if existing:
        return {"error": "User exists"}

    account = create_account(user)
    send_welcome_email(account)
    return account
```

### 7. Leverage Parallel Execution

```python
# Run independent searches in parallel
parallel = (
    ParallelPipeline("multi-source")
    .add_pipeline(web_search_pipeline)
    .add_pipeline(scholar_search_pipeline)
    .add_pipeline(image_search_pipeline)
)
```

### 8. Add Logging and Monitoring

```python
def log_step(step_name):
    def logger(data):
        print(f"Step {step_name}: {len(data)} items")
        return data
    return logger

pipeline = (
    Pipeline("monitored")
    .add_step("search", web_search)
    .add_function("log1", log_step("after_search"))
    .add_function("filter", filter_data)
    .add_function("log2", log_step("after_filter"))
)
```

## Performance Tips

### 1. Use Caching

Enable caching for repeated operations:

```python
# In tool definition
class MyTool(BaseTool):
    enable_cache = True
    cache_ttl = 3600  # 1 hour
```

### 2. Limit Data Size

Filter early to reduce processing:

```python
pipeline = (
    Pipeline("efficient")
    .add_step("search", web_search, max_results=100)
    .filter("relevant", lambda item: item['score'] > 0.8)  # Early filter
    .add_step("process", expensive_processing)  # Process less data
)
```

### 3. Use Parallel Pipelines

```python
# Parallel > Sequential for independent operations
parallel.execute()  # Faster
```

### 4. Profile Pipeline Performance

```python
result = pipeline.execute()

print(f"Total: {result['duration_ms']}ms")
for step in result['steps']:
    print(f"  {step['name']}: {step['duration_ms']}ms")
```

## Comparison: Pipelines vs Workflows

| Feature | Pipeline | Workflow |
|---------|----------|----------|
| **API Style** | Fluent/Chainable | JSON/Dict |
| **Use Case** | Code-first | Configuration-first |
| **Readability** | High (code) | High (config) |
| **Flexibility** | Very High | High |
| **Complexity** | Simple-Medium | Medium-Complex |
| **Conditionals** | Method-based | JSON-based |
| **Loops** | map/filter/reduce | foreach |
| **Error Handling** | on_error() | error_handling config |
| **Best For** | Python developers | Workflow designers |

### When to Use Pipelines

- Building tools in Python code
- Need maximum flexibility
- Complex data transformations
- Rapid prototyping
- Code review and version control

### When to Use Workflows

- Configuration-driven automation
- Non-developers creating workflows
- Complex multi-step processes
- Need workflow visualization
- Dynamic workflow loading

## Next Steps

- See [WORKFLOWS.md](./WORKFLOWS.md) for workflow engine guide
- Check [pipeline examples](../../examples/pipelines/) for more examples
- Read [API Reference](../api/pipeline.md) for detailed API docs
