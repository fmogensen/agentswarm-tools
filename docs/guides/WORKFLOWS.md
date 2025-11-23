# Workflow Engine Guide

Complete guide to creating and executing multi-step workflows in AgentSwarm Tools Framework.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Workflow Structure](#workflow-structure)
- [Step Types](#step-types)
- [Variable Interpolation](#variable-interpolation)
- [Conditional Execution](#conditional-execution)
- [Loops and Iteration](#loops-and-iteration)
- [Error Handling](#error-handling)
- [Example Workflows](#example-workflows)
- [Best Practices](#best-practices)
- [CLI Workflow Builder](#cli-workflow-builder)

## Overview

The Workflow Engine enables you to compose multiple tools into automated, multi-step workflows with:

- **Sequential Execution**: Run tools in order, passing data between steps
- **Conditional Logic**: Execute steps based on conditions (if/else)
- **Loops**: Iterate over collections with foreach
- **Parallel Execution**: Run multiple steps simultaneously
- **Error Handling**: Automatic retries and error recovery
- **Variable Interpolation**: Dynamic values from variables, environment, and previous steps

## Getting Started

### Basic Workflow

```python
from shared.workflow import WorkflowEngine

# Define workflow
workflow = {
    "name": "simple-search",
    "description": "Search and analyze results",
    "variables": {
        "topic": "AI trends 2024"
    },
    "steps": [
        {
            "id": "search",
            "tool": "web_search",
            "params": {
                "query": "${vars.topic}",
                "max_results": 10
            }
        },
        {
            "id": "analyze",
            "tool": "summarize_large_document",
            "params": {
                "content": "${steps.search.result}",
                "max_length": 500
            }
        }
    ]
}

# Execute
engine = WorkflowEngine(workflow)
result = engine.execute()

print(result['success'])  # True/False
print(result['results'])  # Dict of step results
```

### Loading from File

```python
# Load workflow from JSON file
engine = WorkflowEngine.from_file("workflows/research.json")
result = engine.execute()

# Or use convenience function
from shared.workflow import execute_workflow
result = execute_workflow("workflows/research.json")
```

## Workflow Structure

Every workflow has this structure:

```json
{
  "name": "workflow-name",
  "description": "What this workflow does",
  "variables": {
    "var_name": "value"
  },
  "steps": [
    {
      "id": "step_id",
      "tool": "tool_name",
      "params": {},
      "condition": "optional condition"
    }
  ],
  "error_handling": {
    "retry_on_failure": true,
    "max_retries": 3,
    "continue_on_error": false
  },
  "timeout": 1800
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Workflow identifier |
| `description` | string | No | Human-readable description |
| `variables` | object | No | Initial variables |
| `steps` | array | Yes | Workflow steps (min 1) |
| `error_handling` | object | No | Error handling configuration |
| `timeout` | number | No | Max execution time in seconds (default: 1800) |

## Step Types

### 1. Tool Step

Execute a single tool:

```json
{
  "id": "search",
  "tool": "web_search",
  "params": {
    "query": "AI news",
    "max_results": 10
  }
}
```

### 2. Foreach Step

Iterate over a collection:

```json
{
  "id": "process_urls",
  "type": "foreach",
  "items": "${steps.search.result.urls}",
  "step": {
    "tool": "crawler",
    "params": {
      "url": "${item.url}",
      "max_depth": 1
    }
  }
}
```

Inside foreach loops, you can use:
- `${item}` - Current item
- `${index}` - Current index (0-based)

### 3. Parallel Step

Execute multiple steps simultaneously:

```json
{
  "id": "parallel_search",
  "type": "parallel",
  "steps": [
    {
      "id": "web",
      "tool": "web_search",
      "params": {"query": "AI"}
    },
    {
      "id": "scholar",
      "tool": "scholar_search",
      "params": {"query": "AI"}
    }
  ]
}
```

Note: Currently executes sequentially. True parallel execution coming soon.

### 4. Condition Step

Conditional execution (if/else):

```json
{
  "id": "check_results",
  "type": "condition",
  "condition": "${steps.search.success}",
  "then": {
    "tool": "crawler",
    "params": {"url": "${steps.search.result.url}"}
  },
  "else": {
    "tool": "fallback_tool",
    "params": {}
  }
}
```

## Variable Interpolation

Access dynamic values using `${...}` syntax:

### Variables

```json
{
  "variables": {"topic": "AI", "count": 10},
  "steps": [{
    "tool": "web_search",
    "params": {
      "query": "${vars.topic}",
      "max_results": "${vars.count}"
    }
  }]
}
```

### Previous Step Results

```json
{
  "steps": [
    {
      "id": "search",
      "tool": "web_search",
      "params": {"query": "AI"}
    },
    {
      "id": "analyze",
      "tool": "crawler",
      "params": {
        "urls": "${steps.search.result.urls}",
        "success": "${steps.search.success}"
      }
    }
  ]
}
```

### Environment Variables

```json
{
  "steps": [{
    "tool": "some_tool",
    "params": {
      "api_key": "${env.MY_API_KEY}"
    }
  }]
}
```

### Nested Access

```json
{
  "params": {
    "url": "${steps.search.result[0].url}",
    "all_urls": "${steps.search.result[*].url}"
  }
}
```

## Conditional Execution

### Step-Level Conditions

Add a condition to any step:

```json
{
  "id": "optional_step",
  "tool": "some_tool",
  "params": {},
  "condition": "${steps.previous.success}"
}
```

### Condition Syntax

Boolean values:
```json
"condition": "${steps.search.success}"
```

Comparisons:
```json
"condition": "${vars.count} > 5"
"condition": "${steps.search.result.length} >= 10"
"condition": "${vars.mode} == 'production'"
```

Supported operators: `>`, `<`, `>=`, `<=`, `==`, `!=`

### Condition Step Type

Use `condition` step type for if/else logic:

```json
{
  "id": "decision",
  "type": "condition",
  "condition": "${vars.use_advanced} == true",
  "then": {
    "tool": "advanced_tool",
    "params": {}
  },
  "else": {
    "tool": "basic_tool",
    "params": {}
  }
}
```

## Loops and Iteration

### Foreach Loop

Iterate over arrays:

```json
{
  "id": "process_items",
  "type": "foreach",
  "items": "${steps.search.result}",
  "step": {
    "tool": "process_item",
    "params": {
      "data": "${item}",
      "index": "${index}"
    }
  }
}
```

### Nested Loops

```json
{
  "steps": [
    {
      "id": "outer_loop",
      "type": "foreach",
      "items": "${vars.categories}",
      "step": {
        "id": "search_category",
        "tool": "web_search",
        "params": {"query": "${item}"}
      }
    },
    {
      "id": "inner_loop",
      "type": "foreach",
      "items": "${steps.outer_loop.result}",
      "step": {
        "tool": "crawler",
        "params": {"url": "${item.url}"}
      }
    }
  ]
}
```

## Error Handling

### Global Error Handling

Configure at workflow level:

```json
{
  "error_handling": {
    "retry_on_failure": true,
    "max_retries": 3,
    "continue_on_error": false
  }
}
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `retry_on_failure` | boolean | true | Retry failed steps |
| `max_retries` | number | 3 | Maximum retry attempts |
| `continue_on_error` | boolean | false | Continue workflow on step failure |

### Retry Logic

Failed steps are automatically retried with exponential backoff:
- Attempt 1: Immediate
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds
- Attempt N: Wait 2^(N-1) seconds

### Continue on Error

When `continue_on_error` is true:
- Failed steps are marked as failed
- Workflow continues to next step
- Final result includes all errors
- Overall success is false if any step failed

## Example Workflows

### 1. Research to Document

Research a topic and create a comprehensive document:

```json
{
  "name": "research-to-document",
  "variables": {
    "topic": "AI trends 2024",
    "max_results": 10
  },
  "steps": [
    {
      "id": "search",
      "tool": "web_search",
      "params": {
        "query": "${vars.topic}",
        "max_results": "${vars.max_results}"
      }
    },
    {
      "id": "crawl",
      "type": "foreach",
      "items": "${steps.search.result.results}",
      "step": {
        "tool": "crawler",
        "params": {"url": "${item.url}"}
      },
      "condition": "${steps.search.success}"
    },
    {
      "id": "document",
      "tool": "create_agent",
      "params": {
        "agent_type": "docs",
        "title": "Research: ${vars.topic}",
        "content": "${steps.crawl.result}"
      }
    }
  ]
}
```

### 2. Media Analysis Pipeline

Analyze videos and generate report:

```json
{
  "name": "media-analysis",
  "variables": {
    "folder": "/videos"
  },
  "steps": [
    {
      "id": "list",
      "tool": "aidrive_tool",
      "params": {
        "action": "list_directory",
        "path": "${vars.folder}"
      }
    },
    {
      "id": "analyze",
      "tool": "batch_understand_videos",
      "params": {
        "video_urls": "${steps.list.result.files}",
        "instruction": "Analyze content"
      }
    },
    {
      "id": "report",
      "tool": "create_agent",
      "params": {
        "agent_type": "docs",
        "content": "${steps.analyze.result}"
      }
    }
  ]
}
```

### 3. Data Visualization

Load data and create charts:

```json
{
  "name": "data-viz",
  "variables": {
    "data_file": "sales.csv"
  },
  "steps": [
    {
      "id": "read",
      "tool": "Read",
      "params": {
        "file_path": "${vars.data_file}"
      }
    },
    {
      "id": "chart",
      "tool": "generate_line_chart",
      "params": {
        "data": "${steps.read.result}",
        "title": "Sales Trends"
      }
    }
  ]
}
```

### 4. Email Automation

Process emails and create summary:

```json
{
  "name": "email-summary",
  "variables": {
    "query": "subject:report"
  },
  "steps": [
    {
      "id": "search",
      "tool": "gmail_search",
      "params": {"query": "${vars.query}"}
    },
    {
      "id": "read",
      "type": "foreach",
      "items": "${steps.search.result.emails}",
      "step": {
        "tool": "gmail_read",
        "params": {"message_id": "${item.id}"}
      }
    },
    {
      "id": "draft",
      "tool": "email_draft",
      "params": {
        "to": "manager@company.com",
        "subject": "Email Summary",
        "body": "${steps.read.result}"
      }
    }
  ]
}
```

### 5. Content Generation

Generate multimedia content:

```json
{
  "name": "content-gen",
  "variables": {
    "theme": "Future of AI"
  },
  "steps": [
    {
      "id": "research",
      "tool": "web_search",
      "params": {"query": "${vars.theme}"}
    },
    {
      "id": "images",
      "type": "parallel",
      "steps": [
        {
          "tool": "image_generation",
          "params": {"query": "${vars.theme}"}
        },
        {
          "tool": "image_generation",
          "params": {"query": "${vars.theme} icon"}
        }
      ]
    },
    {
      "id": "video",
      "tool": "video_generation",
      "params": {
        "query": "${vars.theme} visualization"
      }
    },
    {
      "id": "podcast",
      "tool": "create_agent",
      "params": {
        "agent_type": "podcast",
        "content": "${steps.research.result}"
      }
    }
  ]
}
```

## Best Practices

### 1. Use Descriptive IDs

```json
// Good
{"id": "search_ai_news", "tool": "web_search"}

// Bad
{"id": "step1", "tool": "web_search"}
```

### 2. Add Conditions for Dependent Steps

```json
{
  "id": "crawl",
  "tool": "crawler",
  "params": {"url": "${steps.search.result.url}"},
  "condition": "${steps.search.success}"
}
```

### 3. Use Variables for Reusability

```json
{
  "variables": {
    "topic": "AI",
    "max_results": 10,
    "language": "en"
  }
}
```

### 4. Handle Errors Gracefully

```json
{
  "error_handling": {
    "retry_on_failure": true,
    "max_retries": 3,
    "continue_on_error": true
  }
}
```

### 5. Set Reasonable Timeouts

```json
{
  "timeout": 1800  // 30 minutes for long workflows
}
```

### 6. Test in Mock Mode

```bash
# Set environment variable
export USE_MOCK_APIS=true

# Run workflow
python -c "
from shared.workflow import execute_workflow
result = execute_workflow('my_workflow.json')
print(result)
"
```

### 7. Use Foreach for Batch Operations

```json
{
  "type": "foreach",
  "items": "${steps.search.result}",
  "step": {
    "tool": "process",
    "params": {"data": "${item}"}
  }
}
```

### 8. Validate Before Production

```python
from shared.workflow import WorkflowEngine

# Validate workflow structure
workflow = {...}
engine = WorkflowEngine(workflow)

# Check all tools exist
for step in workflow['steps']:
    tool_name = step.get('tool')
    if tool_name and not tool_registry.has_tool(tool_name):
        print(f"Warning: Tool '{tool_name}' not found")
```

## CLI Workflow Builder

Interactive wizard for creating workflows:

```bash
# Start interactive builder
python -m cli.workflow_builder

# Load template
python -m cli.workflow_builder --template research

# Edit existing workflow
python -m cli.workflow_builder --load my_workflow.json

# List templates
python -m cli.workflow_builder --list-templates

# Execute workflow
python -m cli.workflow_builder --execute my_workflow.json
```

### Interactive Builder Steps

1. **Workflow Information**: Name and description
2. **Variables**: Define initial variables
3. **Steps**: Add tool, foreach, condition, or parallel steps
4. **Error Handling**: Configure retry and error behavior
5. **Review**: Validate and save workflow
6. **Test**: Optional test execution in mock mode

## Performance Tips

### 1. Use Parallel Steps

Execute independent steps in parallel:

```json
{
  "type": "parallel",
  "steps": [
    {"tool": "web_search"},
    {"tool": "scholar_search"},
    {"tool": "image_search"}
  ]
}
```

### 2. Limit Foreach Iterations

```json
{
  "type": "foreach",
  "items": "${steps.search.result[0:10]}",  // First 10 only
  "step": {...}
}
```

### 3. Set Appropriate Timeouts

```json
{
  "timeout": 600  // 10 minutes for fast workflows
}
```

### 4. Use Caching

Enable caching for repeated operations:

```python
# In tool configuration
enable_cache = True
cache_ttl = 3600  # 1 hour
```

## Troubleshooting

### Workflow Validation Errors

```python
try:
    engine = WorkflowEngine(workflow)
    result = engine.execute()
except ValidationError as e:
    print(f"Invalid workflow: {e}")
```

### Step Failures

Check step status in result:

```python
result = engine.execute()
for step_id, status in result['step_status'].items():
    if status == 'failed':
        error = result['results'][step_id].get('error')
        print(f"Step {step_id} failed: {error}")
```

### Timeout Issues

Increase timeout or split into smaller workflows:

```json
{
  "timeout": 3600  // 1 hour
}
```

### Variable Interpolation Errors

Validate variables exist:

```python
context = WorkflowContext(workflow['variables'])
try:
    value = context.interpolate("${vars.topic}")
except ValidationError as e:
    print(f"Variable error: {e}")
```

## Next Steps

- See [PIPELINES.md](./PIPELINES.md) for fluent pipeline API
- Check [example workflows](../../examples/workflows/) for more examples
- Read [API Reference](../api/workflow.md) for detailed API docs
