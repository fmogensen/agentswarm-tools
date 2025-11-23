# AgentSwarm CLI Guide

Complete reference for the AgentSwarm Tools CLI - an interactive, feature-rich command-line interface for managing and running 101+ tools.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Interactive Mode](#interactive-mode)
- [Core Commands](#core-commands)
- [Workflow Management](#workflow-management)
- [Command History](#command-history)
- [Shell Auto-Completion](#shell-auto-completion)
- [Configuration](#configuration)
- [Advanced Usage](#advanced-usage)
- [Examples](#examples)

## Installation

### Install AgentSwarm Tools

```bash
pip install agentswarm-tools
```

### Verify Installation

```bash
agentswarm --version
```

### Install Shell Completion (Optional)

```bash
agentswarm completion install
```

## Quick Start

### Launch Interactive Mode

The easiest way to get started:

```bash
agentswarm interactive
```

This launches a menu-driven interface where you can:
- Browse tools by category
- Search for tools
- Access recent tools
- Run tools with guided parameter input
- View command history

### List All Tools

```bash
agentswarm list
```

### Run a Tool

```bash
# Interactive mode (guided prompts)
agentswarm run web_search --interactive

# With parameters
agentswarm run web_search --params '{"query": "AI news", "max_results": 10}'

# From file
agentswarm run web_search --params @params.json
```

### Get Tool Information

```bash
agentswarm info web_search
```

## Interactive Mode

The interactive mode provides a rich, menu-driven experience with:

### Main Menu

1. **Browse by Category** - Navigate tools organized by 8 categories
2. **Search for Tools** - Quick search by name or keyword
3. **Recent Tools** - Access your 5 most recently used tools
4. **Quick Actions** - List tools, view history, manage workflows
5. **Settings** - Configure API keys, clear history, install completion

### Features

- **Rich Tables** - Beautiful formatted output with colors
- **Interactive Prompts** - Guided parameter input with validation
- **Tool Suggestions** - Smart recommendations based on usage
- **Error Handling** - Clear error messages with recovery options

### Launching Interactive Mode

```bash
agentswarm interactive
```

### Navigation

- Use number keys to select options
- Type 'b' to go back to previous menu
- Press Ctrl+C to cancel current operation
- Press Ctrl+D or 'q' to quit

## Core Commands

### list - List Available Tools

```bash
# List all tools
agentswarm list

# List by category
agentswarm list --category media

# List all categories
agentswarm list --categories

# Output as JSON
agentswarm list --format json

# Output as YAML
agentswarm list --format yaml
```

**Options:**
- `-c, --category <name>` - Filter by category
- `-f, --format <format>` - Output format (table, json, yaml)
- `--categories` - List all categories

**Categories:**
- `data` - Search and information retrieval
- `communication` - Email, calendar, messaging
- `media` - Image, video, audio generation/analysis
- `visualization` - Charts, diagrams, graphs
- `content` - Documents and web content
- `infrastructure` - Code execution and storage
- `utils` - Utility tools and helpers
- `integrations` - External service connectors

### info - Show Tool Information

```bash
# Text format (default)
agentswarm info web_search

# JSON format
agentswarm info web_search --format json

# YAML format
agentswarm info web_search --format yaml
```

**Output Includes:**
- Tool name and category
- Description
- Parameters and types
- Return value structure
- Usage examples

### run - Run a Tool

```bash
# Interactive mode with prompts
agentswarm run web_search --interactive

# With JSON parameters
agentswarm run web_search --params '{"query": "AI news", "max_results": 10}'

# Load parameters from file
agentswarm run web_search --params @params.json

# Save output to file
agentswarm run web_search --params '{"query": "AI"}' --output results.json

# Output as YAML
agentswarm run web_search --params '{"query": "AI"}' --format yaml
```

**Options:**
- `-p, --params <json|@file>` - Parameters as JSON or from file
- `-i, --interactive` - Interactive mode with prompts
- `-o, --output <file>` - Save output to file
- `-f, --format <format>` - Output format (json, yaml, text)

### test - Test a Tool

```bash
# Test specific tool with mock data
agentswarm test web_search

# Test with verbose output
agentswarm test web_search --verbose

# Test all tools
agentswarm test

# Test without mock mode (use real APIs)
agentswarm test web_search --no-mock
```

**Options:**
- `-m, --mock` - Use mock mode (default: true)
- `-v, --verbose` - Verbose output

### validate - Validate Tools

```bash
# Validate all tools
agentswarm validate

# Validate specific tool
agentswarm validate web_search

# Strict validation mode
agentswarm validate --strict
```

**Options:**
- `--strict` - Strict validation mode

### config - Manage Configuration

```bash
# Show current configuration
agentswarm config --show

# Set API key
agentswarm config --set GENSPARK_API_KEY=your_key_here

# Get specific value
agentswarm config --get GENSPARK_API_KEY

# Validate configuration
agentswarm config --validate

# Reset to defaults
agentswarm config --reset
```

**Options:**
- `--show` - Show current configuration
- `--set <KEY=VALUE>` - Set configuration value
- `--get <KEY>` - Get configuration value
- `--validate` - Validate configuration
- `--reset` - Reset to default configuration

## Workflow Management

Workflows allow you to chain multiple tools together for complex tasks.

### Create a Workflow

```bash
agentswarm workflow create
```

**Interactive Workflow Builder:**
1. Enter workflow name and description
2. Add steps (tool + parameters)
3. Define input variables
4. Configure error handling
5. Workflow saved to `~/.agentswarm/workflows/`

**Workflow Structure:**

```json
{
  "name": "research-workflow",
  "description": "Search web and create document",
  "variables": {
    "query": {
      "type": "string",
      "description": "Search query",
      "required": true
    }
  },
  "steps": [
    {
      "tool": "web_search",
      "params": {
        "query": "${input.query}",
        "max_results": 10
      }
    },
    {
      "tool": "create_agent",
      "params": {
        "agent_type": "docs",
        "content": "${steps[0].result}"
      },
      "on_error": "continue"
    }
  ]
}
```

### Run a Workflow

```bash
# Run with input parameters
agentswarm workflow run research-workflow --params '{"query": "AI trends 2024"}'

# Load parameters from file
agentswarm workflow run research-workflow --params @input.json

# Save results to file
agentswarm workflow run research-workflow --params '{"query": "AI"}' --output results.json
```

### List Workflows

```bash
agentswarm workflow list
```

**Output:**
- Workflow name
- Description
- Number of steps
- Created date

### Delete a Workflow

```bash
agentswarm workflow delete research-workflow
```

### Variable Substitution

Workflows support variable substitution:

- `${input.variable_name}` - Input variable
- `${steps[N].result}` - Result from step N
- `${steps[N].success}` - Success status from step N

### Error Handling

Configure error handling per step:

- `stop` - Stop workflow on error (default)
- `continue` - Continue to next step
- `retry` - Retry the step once

### Conditional Steps

Add conditions to steps:

```json
{
  "tool": "email_draft",
  "params": {...},
  "condition": "${steps[0].success}"
}
```

## Command History

The CLI tracks all commands for replay and analysis.

### View History

```bash
# Show last 20 commands
agentswarm history list

# Show last 50 commands
agentswarm history list --limit 50

# Filter by command type
agentswarm history list --filter run
```

**History Includes:**
- Command ID
- Timestamp
- Command type
- Tool name
- Success/failure status
- Execution duration

### Replay a Command

```bash
# Replay command by ID
agentswarm history replay 42
```

**Replay Process:**
1. Shows command details
2. Asks for confirmation
3. Executes the command
4. Displays results

### Show Statistics

```bash
agentswarm history stats
```

**Statistics Include:**
- Total commands executed
- Success rate
- Most used tools
- Most used commands

### Clear History

```bash
agentswarm history clear
```

**Warning:** This permanently deletes all command history.

### History Storage

History is stored in: `~/.agentswarm/history.json`

- Maximum 1000 entries
- Automatic cleanup of old entries
- JSON format for easy export

## Shell Auto-Completion

Auto-completion speeds up CLI usage with tab completion.

### Install Completion

```bash
# Auto-detect shell and install
agentswarm completion install

# Install for specific shell
agentswarm completion install --shell bash
agentswarm completion install --shell zsh
agentswarm completion install --shell fish
```

### Supported Shells

- **Bash** - Installed to `~/.bash_completion.d/`
- **Zsh** - Installed to `~/.zsh/completion/`
- **Fish** - Installed to `~/.config/fish/completions/`

### What Gets Completed

- Main commands (list, run, test, workflow, etc.)
- Tool names
- Category names
- Workflow names
- Command options and flags
- Output formats

### Show Completion Script

```bash
# Show script for current shell
agentswarm completion show

# Show script for specific shell
agentswarm completion show --shell bash
```

### Reload Completion

After installation:

**Bash:**
```bash
source ~/.bashrc
```

**Zsh:**
```bash
source ~/.zshrc
```

**Fish:**
```bash
source ~/.config/fish/config.fish
```

Or start a new terminal session.

## Configuration

### Configuration File

Located at: `~/.agentswarm/config.json`

### API Keys

Set API keys for external services:

```bash
# Genspark API
agentswarm config --set GENSPARK_API_KEY=your_key

# OpenAI API
agentswarm config --set OPENAI_API_KEY=your_key

# Google Search API
agentswarm config --set GOOGLE_SEARCH_API_KEY=your_key
agentswarm config --set GOOGLE_SEARCH_ENGINE_ID=your_id
```

### Environment Variables

API keys can also be set via environment variables:

```bash
export GENSPARK_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

### Default Settings

```json
{
  "default_format": "json",
  "mock_mode": false,
  "history_enabled": true,
  "history_max_entries": 1000,
  "auto_save_results": false
}
```

## Advanced Usage

### Chaining Commands

Use shell pipes to chain commands:

```bash
# Run tool and save to file
agentswarm run web_search --params '{"query": "AI"}' | jq '.results' > results.json

# List tools in JSON and filter
agentswarm list --format json | jq '.[] | select(.Category == "media")'
```

### Batch Processing

Process multiple tools:

```bash
# Run multiple tools in sequence
for tool in web_search scholar_search image_search; do
  agentswarm run $tool --params @params.json
done
```

### Scripting

Use in shell scripts:

```bash
#!/bin/bash

# Run workflow and check result
result=$(agentswarm workflow run research --params '{"query": "AI"}')

if [ $? -eq 0 ]; then
  echo "Workflow completed successfully"
  echo $result | jq '.steps'
else
  echo "Workflow failed"
  exit 1
fi
```

### Continuous Integration

Use in CI/CD pipelines:

```yaml
# .github/workflows/test-tools.yml
steps:
  - name: Test Tools
    run: |
      agentswarm test --all --verbose
      agentswarm validate --strict
```

## Examples

### Example 1: Simple Web Search

```bash
# Interactive mode
agentswarm run web_search --interactive

# Direct execution
agentswarm run web_search --params '{"query": "latest AI news", "max_results": 5}'
```

### Example 2: Create Research Workflow

```bash
# Create workflow
agentswarm workflow create

# Name: research-workflow
# Step 1: web_search with ${input.query}
# Step 2: create_agent with docs type using ${steps[0].result}

# Run workflow
agentswarm workflow run research-workflow --params '{"query": "quantum computing"}'
```

### Example 3: Generate and Analyze Image

```bash
# Generate image
agentswarm run image_generation --params '{
  "model": "flux-pro",
  "query": "futuristic cityscape",
  "aspect_ratio": "16:9"
}' --output image_result.json

# Extract URL and analyze
image_url=$(cat image_result.json | jq -r '.result.url')
agentswarm run understand_images --params "{\"media_urls\": [\"$image_url\"], \"instruction\": \"Describe this image\"}"
```

### Example 4: Batch Search and Summarize

```bash
# Create workflow for batch processing
agentswarm workflow create

# Name: batch-research
# Steps:
# 1. web_search
# 2. crawler (for each result)
# 3. summarize_large_document
# 4. create_agent (compile into document)

# Run workflow
agentswarm workflow run batch-research --params '{
  "query": "climate change solutions",
  "max_results": 10
}'
```

### Example 5: Monitor Command Performance

```bash
# View command history
agentswarm history list --limit 100

# Show statistics
agentswarm history stats

# Find slow commands
agentswarm history list --limit 50 | grep "duration"

# Replay successful command
agentswarm history replay 42
```

### Example 6: Email Workflow

```bash
# Search Gmail
agentswarm run gmail_search --params '{"query": "from:boss@company.com", "max_results": 5}'

# Read specific email
agentswarm run gmail_read --params '{"message_id": "abc123"}'

# Draft response
agentswarm run email_draft --params '{
  "to": "boss@company.com",
  "subject": "Re: Project Update",
  "body": "Here is the update..."
}'
```

### Example 7: Data Visualization Pipeline

```bash
# Workflow: data -> analysis -> chart
agentswarm workflow create

# Steps:
# 1. aidrive_tool - fetch data
# 2. Bash - process with pandas
# 3. generate_line_chart - visualize

agentswarm workflow run data-viz --params '{
  "data_file": "/mnt/aidrive/sales_data.csv"
}'
```

## Tips and Best Practices

### Performance

1. **Use Mock Mode for Testing** - Test tools without API calls:
   ```bash
   agentswarm test web_search --mock
   ```

2. **Batch Operations** - Use workflows for multiple tools:
   ```bash
   agentswarm workflow run batch-process
   ```

3. **Cache Results** - Save outputs for reuse:
   ```bash
   agentswarm run tool --output cache.json
   ```

### Security

1. **Never Commit API Keys** - Use environment variables
2. **Validate Configuration** - Regular checks:
   ```bash
   agentswarm config --validate
   ```

3. **Clear Sensitive History**:
   ```bash
   agentswarm history clear
   ```

### Workflow Design

1. **Use Input Variables** - Make workflows reusable
2. **Handle Errors** - Set `on_error` for critical steps
3. **Add Conditions** - Skip unnecessary steps
4. **Test Incrementally** - Build workflows step by step

### Debugging

1. **Verbose Mode**:
   ```bash
   agentswarm test tool --verbose
   ```

2. **View Raw Output**:
   ```bash
   agentswarm run tool --format json | jq '.'
   ```

3. **Check History**:
   ```bash
   agentswarm history list --filter run
   ```

## Troubleshooting

### Command Not Found

```bash
# Ensure AgentSwarm is installed
pip install agentswarm-tools

# Check PATH
echo $PATH
```

### Auto-Completion Not Working

```bash
# Reinstall completion
agentswarm completion install

# Reload shell
source ~/.bashrc  # or ~/.zshrc
```

### Tool Execution Fails

```bash
# Validate tool
agentswarm validate tool_name

# Check configuration
agentswarm config --show

# Test with mock mode
agentswarm test tool_name --mock
```

### Workflow Errors

```bash
# View workflow definition
cat ~/.agentswarm/workflows/workflow_name.json

# Check execution logs
ls ~/.agentswarm/workflows/logs/
```

## Getting Help

### CLI Help

```bash
# General help
agentswarm --help

# Command help
agentswarm run --help
agentswarm workflow --help
```

### Tool Information

```bash
# View tool details
agentswarm info tool_name
```

### Documentation

- **GitHub**: https://github.com/agency-ai-solutions/agentswarm-tools
- **Guides**: `/docs/guides/`
- **Examples**: `/docs/examples/`

### Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@agentswarm.ai

## Version History

- **v1.2.0** - Added interactive mode, workflows, history, auto-completion
- **v1.1.0** - Added performance monitoring
- **v1.0.0** - Initial release with core commands

## License

MIT License - See LICENSE file for details.
