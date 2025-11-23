# AgentSwarm Tools SDK Guide

Complete guide to using the AgentSwarm Tools SDK for rapid tool development with scaffolding, validation, and best practices enforcement.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Tool Generation](#tool-generation)
5. [Validation](#validation)
6. [Test Generation](#test-generation)
7. [Documentation Generation](#documentation-generation)
8. [Best Practices](#best-practices)
9. [CLI Reference](#cli-reference)

---

## Overview

The AgentSwarm Tools SDK provides:

- **Interactive tool scaffolding** - Generate complete tool structures with prompts
- **Automatic validation** - Check compliance with Agency Swarm standards
- **Test generation** - Create comprehensive test suites automatically
- **Documentation generation** - Generate README files and API docs
- **Best practices enforcement** - Security checks, code standards, error handling

### Benefits

- **Faster Development**: Create production-ready tools in minutes
- **Consistency**: All tools follow the same structure and standards
- **Quality**: Built-in validation ensures compliance
- **Documentation**: Auto-generated docs reduce manual work

---

## Installation

The SDK is included with AgentSwarm Tools. Install dependencies:

```bash
pip install -r requirements.txt
```

Required dependencies:
- `jinja2>=3.0.0` - Template engine
- `questionary>=1.10.0` - Interactive prompts
- `rich>=13.7.0` - Terminal formatting

---

## Quick Start

### Create Your First Tool (Interactive)

```bash
agentswarm sdk create-tool --interactive
```

This launches an interactive wizard that guides you through:
1. Tool name and description
2. Category selection
3. Parameter definition
4. API requirements

### Create Tool (CLI Mode)

```bash
agentswarm sdk create-tool sentiment_analyzer \
  --category data \
  --description "Analyze sentiment of text"
```

### Quick Start (All-in-One)

Generate tool, tests, docs, and validate in one command:

```bash
agentswarm sdk quick-start my_tool --category data
```

---

## Tool Generation

### Interactive Mode

The interactive wizard provides step-by-step guidance:

```bash
agentswarm sdk create-tool --interactive
```

**Wizard Steps:**

1. **Tool Name**: Enter snake_case name (e.g., `web_sentiment_analyzer`)
2. **Category**: Select from 8 categories (data, communication, media, etc.)
3. **Subcategory**: Choose subcategory within category
4. **Description**: Brief description for AI agents
5. **Parameters**: Add parameters with types and validations
6. **API Requirements**: Specify if tool needs API keys

**Example Session:**

```
🚀 AgentSwarm Tool Generator

Tool name: web_sentiment_analyzer
Category: [data/communication/media/...]: data
Subcategory: [search/business/intelligence]: business
Description: Analyze sentiment of web content

Parameters:
  Parameter 1 name: url
  Parameter 1 type: [str/int/bool/list]: str
  Parameter 1 required: [y/n]: y
  Parameter 1 description: URL to analyze

  Add another parameter? [y/n]: n

API requirements:
  Requires API key? [y/n]: y
  API key environment variable: SENTIMENT_API_KEY

Generating files...
  ✓ tools/data/business/web_sentiment_analyzer/web_sentiment_analyzer.py
  ✓ tools/data/business/web_sentiment_analyzer/test_web_sentiment_analyzer.py
  ✓ tools/data/business/web_sentiment_analyzer/README.md
  ✓ tools/data/business/web_sentiment_analyzer/__init__.py

Done! Next steps:
  1. Implement _process() method in web_sentiment_analyzer.py
  2. Set environment variable: export SENTIMENT_API_KEY=your-key
  3. Add API integration
  4. Run tests: pytest tools/data/business/web_sentiment_analyzer/
```

### CLI Mode

For automation or scripting:

```bash
agentswarm sdk create-tool email_summarizer \
  --category communication \
  --subcategory email \
  --description "Summarize email content" \
  --api-key \
  --api-key-var OPENAI_API_KEY
```

### Generated Files

Each tool gets a complete structure:

```
tools/category/subcategory/tool_name/
├── tool_name.py           # Main tool implementation
├── test_tool_name.py      # Test suite
├── __init__.py            # Package initialization
└── README.md              # Documentation
```

**tool_name.py** includes:
- Complete BaseTool structure
- All 5 required methods
- Parameter definitions with Field()
- Mock mode support
- Error handling
- Test block

---

## Validation

### Validate Single Tool

```bash
agentswarm sdk validate-tool tools/data/search/web_search
```

**Output:**

```
╭─────── Validation: web_search ────────╮
│ ✓ PASSED                               │
│ Score: 95/100                          │
│ Errors: 0 | Warnings: 2                │
╰────────────────────────────────────────╯

┌─── Issues ──────────────────────────────┐
│ Severity │ Category      │ Line │ Message │
├──────────┼───────────────┼──────┼─────────┤
│ WARNING  │ documentation │  42  │ Missing │
│          │               │      │ Args:   │
└──────────┴───────────────┴──────┴─────────┘
```

### Validate All Tools

```bash
agentswarm sdk validate-all
```

With custom minimum score:

```bash
agentswarm sdk validate-all --min-score 80
```

### Validation Checks

The validator performs comprehensive checks:

#### 1. Structure Checks ✓
- Inherits from BaseTool
- Has all 5 required methods:
  - `_execute()`
  - `_validate_parameters()`
  - `_should_use_mock()`
  - `_generate_mock_results()`
  - `_process()`
- Defines `tool_name` and `tool_category`

#### 2. Security Checks ✓
- No hardcoded API keys
- No hardcoded passwords/secrets
- Uses `os.getenv()` for sensitive data
- No SQL injection vulnerabilities

#### 3. Documentation Checks ✓
- Class docstring exists
- Docstring has Args, Returns, Example sections
- Method docstrings present
- README.md exists

#### 4. Parameter Checks ✓
- All parameters use `Field()`
- Field() includes descriptions
- Proper type annotations
- Validation logic present

#### 5. Testing Checks ✓
- `if __name__ == "__main__"` block exists
- Test file exists
- Mock mode enabled in tests

#### 6. Error Handling Checks ✓
- Uses custom error classes
- Proper exception handling
- Error messages are descriptive

### Scoring System

- **100 points**: Perfect score
- **-10 points**: Each error
- **-3 points**: Each warning
- **-1 point**: Each info issue

**Passing Score**: 70+ (configurable)

---

## Test Generation

### Generate Tests for Tool

```bash
agentswarm sdk generate-tests tools/data/search/web_search/web_search.py
```

### Auto-Generated Tests Include:

1. **Basic Execution Test**
   ```python
   def test_basic_execution(self):
       tool = ToolName(param1="value")
       result = tool.run()
       assert result["success"] == True
   ```

2. **Validation Tests**
   ```python
   def test_validation_errors(self):
       with pytest.raises(ValidationError):
           tool = ToolName(param1="")  # Invalid
   ```

3. **Mock Mode Test**
   ```python
   def test_mock_mode(self):
       os.environ["USE_MOCK_APIS"] = "true"
       tool = ToolName(param1="test")
       result = tool.run()
       assert result["metadata"]["mock_mode"] == True
   ```

4. **Edge Case Tests**
   - Empty strings
   - Very long inputs
   - Boundary values
   - Null/None values
   - Special characters

### Test Template

Generated tests follow this pattern:

```python
class TestToolName:
    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_basic_execution(self):
        # Test basic functionality

    def test_validation_errors(self):
        # Test parameter validation

    def test_edge_cases(self):
        # Test boundary conditions
```

---

## Documentation Generation

### Generate README for Tool

```bash
agentswarm sdk generate-docs tools/data/search/web_search/web_search.py
```

### Generate for All Tools

```bash
agentswarm sdk generate-docs --all
```

### Update TOOLS_INDEX.md

```bash
agentswarm sdk generate-docs --index
```

### Generated README Includes:

1. **Overview**
   - Tool name and description
   - Category

2. **Parameters Table**
   | Parameter | Type | Required | Default | Description |
   |-----------|------|----------|---------|-------------|
   | query | str | Yes | - | Search query |

3. **Usage Examples**
   - Basic usage
   - Error handling
   - Advanced usage

4. **Environment Variables**
   - Required API keys
   - Configuration options

5. **Testing Instructions**
   - How to run tests
   - Mock mode usage

6. **Development Guide**
   - File structure
   - Contributing guidelines

---

## Best Practices

### Tool Development Workflow

1. **Generate Tool**
   ```bash
   agentswarm sdk create-tool my_tool --interactive
   ```

2. **Implement Logic**
   - Edit `_process()` method
   - Add API calls
   - Implement business logic

3. **Generate Tests**
   ```bash
   agentswarm sdk generate-tests tools/.../my_tool/my_tool.py
   ```

4. **Run Tests**
   ```bash
   pytest tools/.../my_tool/test_my_tool.py -v
   ```

5. **Validate**
   ```bash
   agentswarm sdk validate-tool tools/.../my_tool
   ```

6. **Fix Issues**
   - Address validation errors
   - Improve documentation
   - Add missing tests

7. **Generate Docs**
   ```bash
   agentswarm sdk generate-docs tools/.../my_tool/
   ```

8. **Update Index**
   ```bash
   agentswarm sdk generate-docs --index
   ```

### Code Quality Checklist

Before committing:
- [ ] All validation checks pass (score 90+)
- [ ] All tests pass
- [ ] README.md generated
- [ ] No hardcoded secrets
- [ ] Proper error handling
- [ ] Mock mode works
- [ ] Docstrings complete

### Security Best Practices

1. **Never Hardcode Secrets**
   ```python
   # WRONG
   api_key = "sk-1234567890"

   # CORRECT
   api_key = os.getenv("OPENAI_API_KEY")
   if not api_key:
       raise APIError("Missing OPENAI_API_KEY")
   ```

2. **Validate API Keys Exist**
   ```python
   def _process(self):
       api_key = os.getenv("MY_API_KEY")
       if not api_key:
           raise APIError("Missing MY_API_KEY", tool_name=self.tool_name)
   ```

3. **Use Custom Exceptions**
   ```python
   from shared.errors import ValidationError, APIError

   if not self.param.strip():
       raise ValidationError("param cannot be empty", tool_name=self.tool_name)
   ```

---

## CLI Reference

### create-tool

Create a new tool with scaffolding.

```bash
agentswarm sdk create-tool [TOOL_NAME] [OPTIONS]
```

**Options:**
- `--interactive, -i`: Use interactive wizard
- `--category, -c`: Tool category
- `--subcategory, -s`: Tool subcategory
- `--description, -d`: Tool description
- `--api-key`: Tool requires API key
- `--api-key-var`: API key environment variable name

**Examples:**
```bash
# Interactive mode
agentswarm sdk create-tool --interactive

# CLI mode
agentswarm sdk create-tool sentiment_tool \
  -c data \
  -d "Analyze sentiment"

# With API key
agentswarm sdk create-tool api_tool \
  -c data \
  --api-key \
  --api-key-var MY_API_KEY
```

### validate-tool

Validate tool against Agency Swarm standards.

```bash
agentswarm sdk validate-tool TOOL_PATH [OPTIONS]
```

**Options:**
- `--verbose, -v`: Show detailed output

**Examples:**
```bash
agentswarm sdk validate-tool tools/data/search/web_search
agentswarm sdk validate-tool tools/data/search/web_search/web_search.py -v
```

### validate-all

Validate all tools in project.

```bash
agentswarm sdk validate-all [OPTIONS]
```

**Options:**
- `--tools-dir, -t`: Tools directory (default: tools)
- `--min-score`: Minimum passing score (default: 70)

**Examples:**
```bash
agentswarm sdk validate-all
agentswarm sdk validate-all --min-score 80
```

### generate-tests

Generate comprehensive test suite.

```bash
agentswarm sdk generate-tests TOOL_PATH
```

**Examples:**
```bash
agentswarm sdk generate-tests tools/data/search/web_search/web_search.py
agentswarm sdk generate-tests tools/data/search/web_search/
```

### generate-docs

Generate documentation.

```bash
agentswarm sdk generate-docs [TOOL_PATH] [OPTIONS]
```

**Options:**
- `--all, -a`: Generate for all tools
- `--index, -i`: Update TOOLS_INDEX.md
- `--category, -c`: Generate category README

**Examples:**
```bash
# Single tool
agentswarm sdk generate-docs tools/data/search/web_search/

# All tools
agentswarm sdk generate-docs --all

# Update index
agentswarm sdk generate-docs --index

# Category
agentswarm sdk generate-docs --category data
```

### quick-start

Create tool, generate tests, docs, and validate.

```bash
agentswarm sdk quick-start TOOL_NAME --category CATEGORY
```

**Examples:**
```bash
agentswarm sdk quick-start my_tool --category data
```

---

## Troubleshooting

### Common Issues

**Issue**: "No module named 'sdk'"
**Solution**: Run from project root directory

**Issue**: "Template not found"
**Solution**: Ensure sdk/templates/ directory exists with .jinja2 files

**Issue**: Validation fails with low score
**Solution**: Run with `--verbose` to see detailed issues

**Issue**: Generated tests don't run
**Solution**: Ensure pytest is installed: `pip install pytest`

### Getting Help

- Check validation output for specific issues
- Review generated code for examples
- Consult [CLAUDE.md](../../CLAUDE.md) for standards
- Open issue on GitHub

---

## Examples

### Example 1: Simple Data Tool

```bash
# Create tool
agentswarm sdk create-tool price_checker \
  --category data \
  --subcategory business \
  --description "Check product prices"

# Implement _process() method
# Edit tools/data/business/price_checker/price_checker.py

# Generate tests
agentswarm sdk generate-tests tools/data/business/price_checker/

# Validate
agentswarm sdk validate-tool tools/data/business/price_checker/

# Generate docs
agentswarm sdk generate-docs tools/data/business/price_checker/
```

### Example 2: Communication Tool with API

```bash
# Create with API key
agentswarm sdk create-tool slack_notifier \
  --category communication \
  --subcategory messaging \
  --description "Send Slack notifications" \
  --api-key \
  --api-key-var SLACK_API_TOKEN

# Set API key
export SLACK_API_TOKEN=xoxb-your-token

# Validate before implementing
agentswarm sdk validate-tool tools/communication/messaging/slack_notifier/
```

### Example 3: Batch Tool Generation

```bash
# Create multiple tools
for tool in sentiment_analyzer trend_predictor data_aggregator; do
  agentswarm sdk quick-start $tool --category data
done

# Validate all
agentswarm sdk validate-all --min-score 85

# Generate docs for all
agentswarm sdk generate-docs --all

# Update index
agentswarm sdk generate-docs --index
```

---

## Advanced Topics

### Custom Templates

Modify templates in `sdk/templates/`:
- `tool_template.py.jinja2` - Tool structure
- `test_template.py.jinja2` - Test structure
- `readme_template.md.jinja2` - README structure

### Validation Customization

Extend `sdk/validator.py` to add custom checks:

```python
class CustomValidator(ToolValidator):
    def _check_custom_rules(self, tree, content):
        issues = []
        # Add custom validation logic
        return issues
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Validate Tools
  run: |
    agentswarm sdk validate-all --min-score 90

- name: Generate Docs
  run: |
    agentswarm sdk generate-docs --all
    agentswarm sdk generate-docs --index
```

---

## Conclusion

The AgentSwarm SDK accelerates tool development while enforcing best practices. Use it to:

1. Generate production-ready tools quickly
2. Maintain consistent code quality
3. Automate testing and documentation
4. Ensure security compliance

**Next Steps:**
- Try the interactive wizard: `agentswarm sdk create-tool --interactive`
- Validate existing tools: `agentswarm sdk validate-all`
- Review [Tool Development Guide](../CONTRIBUTING.md)

---

**Questions or Issues?**
- GitHub: https://github.com/agency-ai-solutions/agentswarm-tools
- Documentation: [README.md](../../README.md)
