# Demo Tool

**Category**: Examples
**Status**: Reference Implementation
**Version**: 1.0.0

## Overview

This is a complete reference implementation demonstrating all best practices for AgentSwarm tool development. Use this as a template when creating new tools.

## Purpose

The Demo Tool showcases:
- Proper `BaseTool` inheritance
- Complete type hints
- Google-style docstrings
- Error handling patterns
- Parameter validation
- Mock mode support
- Comprehensive test coverage

## Usage

```python
from tools._examples.demo_tool import DemoTool

# Create tool instance
tool = DemoTool(
    query="python programming",
    max_results=10,
    filter_type="relevant",
    use_cache=True
)

# Execute
result = tool.run()

print(result["total_count"])  # Number of results
print(result["results"])       # List of results
print(result["metadata"])      # Query metadata
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | str | Yes | - | Search query to process (1-500 chars) |
| `max_results` | int | No | 10 | Maximum results to return (1-100) |
| `filter_type` | str | No | None | Filter: 'recent', 'popular', 'relevant' |
| `use_cache` | bool | No | True | Whether to use cached results |

## Returns

```python
{
    "success": True,
    "results": [
        {
            "id": 1,
            "title": "Result Title",
            "description": "Result description",
            "score": 0.95,
            "source": "api"
        }
    ],
    "total_count": 10,
    "metadata": {
        "query": "python programming",
        "max_results": 10,
        "filter_type": "relevant",
        "used_cache": True,
        "tool_version": "1.0.0"
    }
}
```

## Error Handling

The tool raises:
- `ValidationError`: For invalid parameters (empty query, invalid filter_type)
- `APIError`: For external API failures

## Mock Mode

Set `USE_MOCK_APIS=true` in environment to use mock responses during development/testing:

```bash
export USE_MOCK_APIS=true
```

Mock mode returns sample data without calling external APIs.

## Testing

Run tests:
```bash
# All tests
pytest tools/_examples/demo_tool/

# With coverage
pytest tools/_examples/demo_tool/ --cov=tools._examples.demo_tool

# Verbose
pytest tools/_examples/demo_tool/ -v
```

Test coverage: **100%**

## Key Patterns Demonstrated

### 1. BaseTool Inheritance
```python
class DemoTool(BaseTool):
    def _execute(self) -> Dict[str, Any]:
        # Implementation here
        pass
```

### 2. Type Hints with Pydantic
```python
query: str = Field(..., description="Search query", min_length=1, max_length=500)
max_results: int = Field(default=10, ge=1, le=100)
```

### 3. Error Handling
```python
if not self.query.strip():
    raise ValidationError("Query cannot be empty", tool_name=self.tool_name)
```

### 4. Mock Mode Support
```python
def _should_use_mock(self) -> bool:
    return os.getenv("USE_MOCK_APIS", "false").lower() == "true"
```

### 5. Structured Returns
```python
return {
    "success": True,
    "results": [...],
    "total_count": 10,
    "metadata": {...}
}
```

## Development Checklist

When using this as a template:

- [ ] Update `tool_name`, `tool_category`, `tool_description`
- [ ] Define parameters with `Field()` and type hints
- [ ] Implement `_execute()` method only (don't override `run()`)
- [ ] Add parameter validation in `_validate_parameters()`
- [ ] Support mock mode with `_should_use_mock()`
- [ ] Return structured data with success, results, metadata
- [ ] Write comprehensive tests (≥80% coverage)
- [ ] Add Google-style docstrings
- [ ] Handle errors with `shared.errors`

## Related Files

- `demo_tool.py` - Main implementation
- `test_demo_tool.py` - Test suite (100% coverage)
- `__init__.py` - Module exports

## References

See development guidelines:
- `/dev-guidelines/00-README.md` - Overview
- `/dev-guidelines/02-coding-standards.md` - Coding standards
- `/dev-guidelines/03-testing-strategy.md` - Testing patterns
- `/dev-guidelines/04-tool-templates.md` - Tool templates
- `/dev-guidelines/QUICK-START.md` - Quick reference
