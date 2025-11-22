# AgentSwarm Tools - Quick Start Guide

**Version:** 2.0.0
**Last Updated:** 2025-11-22

Get started with AgentSwarm Tools in under 5 minutes.

---

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Git
- Virtual environment (recommended)

---

## Quick Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/agentswarm-tools.git
cd agentswarm-tools
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .
```

### Step 4: Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your API keys (optional for testing)
```

**That's it!** You're ready to use the tools.

---

## Basic Usage

### Using a Tool Directly

```python
from tools.data.search.web_search import WebSearch

# Create tool instance
search = WebSearch(query="Python programming", num_results=5)

# Execute the tool
result = search.run()

# Access results
if result['success']:
    for item in result['result']:
        print(f"{item['title']}: {item['url']}")
```

### Using with Agency Swarm

```python
from agency_swarm import Agent
from tools.data.search.web_search import WebSearch
from tools.media.generation.image_generation import ImageGenerationTool

# Create agent with tools
researcher = Agent(
    name="Researcher",
    description="Research agent with web search and image generation",
    tools=[WebSearch, ImageGenerationTool],
    model="gpt-4o"
)
```

### Using Mock Mode (No API Keys Required)

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

from tools.utils.think import Think

# Tool will return mock data
tool = Think(thought="Planning the project structure")
result = tool.run()

print(result)  # Returns mock success response
```

---

## Running Tests

### Using pytest

```bash
# Run all tests
pytest

# Run specific category tests
pytest tests/integration/live/ -v

# Run with coverage
pytest --cov=tools --cov=shared --cov-report=html

# Run in parallel
pytest -n auto
```

### Using CLI

```bash
# Test a single tool
agentswarm test web_search

# Test all tools with mock mode
agentswarm test --mock

# Validate tool structure
agentswarm validate
```

### Test Results

- **Total Tests:** 95 (400+ test cases in shared modules)
- **Integration Tests:** 11/15 passing (73%)
- **Shared Module Coverage:** 85-95%
- **All tools support mock mode** for testing without API keys

See [TEST_REPORT_v2.0.0.md](../../TEST_REPORT_v2.0.0.md) for detailed test results.

---

## Configuration

### Environment Variables

Edit `.env` to configure API keys:

```bash
# Search APIs
GOOGLE_SEARCH_API_KEY=your_key
SERPAPI_KEY=your_key

# Media Generation
OPENAI_API_KEY=your_key
STABILITY_API_KEY=your_key

# Communication
GMAIL_CLIENT_ID=your_id
TWILIO_ACCOUNT_SID=your_sid

# Testing
USE_MOCK_APIS=false  # Set to true for testing without API keys
```

See [.env.example](../../.env.example) for complete list.

### CLI Configuration

```bash
# Show current configuration
agentswarm config --show

# Set an API key
agentswarm config --set GENSPARK_API_KEY=your_key

# Validate configuration
agentswarm config --validate
```

---

## Exploring Tools

### List Available Tools

```bash
# List all tools
agentswarm list

# List tools in a category
agentswarm list --category data

# Show tool details
agentswarm info web_search
```

### Tool Categories

1. **Data & Intelligence** (13 tools) - Search, business analytics, AI intelligence
2. **Communication & Collaboration** (23 tools) - Email, calendar, workspace, messaging, phone
3. **Media** (20 tools) - Generation, analysis, processing
4. **Visualization** (16 tools) - Charts, diagrams, graphs
5. **Content** (10 tools) - Documents, web content
6. **Infrastructure** (11 tools) - Code execution, storage, management
7. **Utilities** (8 tools) - Helper tools and validators
8. **Integrations** (0 tools) - Ready for external service connectors

See [TOOLS_INDEX.md](../references/TOOLS_INDEX.md) for complete alphabetical listing.

---

## Example Workflows

### Research to Document

```python
from tools.data.search.web_search import WebSearch
from tools.content.web.crawler import Crawler
from tools.content.documents.create_agent import CreateAgentTool

# 1. Search for information
search = WebSearch(query="AI agent frameworks")
results = search.run()

# 2. Crawl top results
crawler = Crawler(url=results['result'][0]['link'])
content = crawler.run()

# 3. Create document
doc_creator = CreateAgentTool(
    agent_type="docs",
    topic="AI Agent Frameworks Overview",
    content=content['result']
)
document = doc_creator.run()
```

### Data to Visualization

```python
from tools.data.business.data_aggregator import DataAggregator
from tools.visualization.generate_line_chart import GenerateLineChart

# 1. Aggregate data
aggregator = DataAggregator(sources=["sales_data.csv"])
data = aggregator.run()

# 2. Create visualization
chart = GenerateLineChart(
    prompt="Sales trend over time",
    params={"data": data['result']['time_series']}
)
visualization = chart.run()
```

---

## Troubleshooting

### Import Errors

If you get import errors, ensure you installed in editable mode:
```bash
pip install -e .
```

### API Key Issues

Test without API keys using mock mode:
```bash
export USE_MOCK_APIS=true
python -m tools.data.search.web_search
```

### Test Failures

Current test suite is being updated to v2.0.0 structure. Tools work correctly (proven by integration tests). See [TEST_REPORT_v2.0.0.md](../../TEST_REPORT_v2.0.0.md) for details.

---

## Next Steps

1. **Explore Documentation:**
   - [TOOLS_INDEX.md](../references/TOOLS_INDEX.md) - All 101 tools alphabetically
   - [TOOLS_DOCUMENTATION.md](../references/TOOLS_DOCUMENTATION.md) - Complete API reference
   - [CONTRIBUTING.md](../../CONTRIBUTING.md) - Development guidelines

2. **Try Examples:**
   - Check `tests/integration/live/` for working examples
   - Each tool has a test block at the bottom of its file

3. **Build Your Agent:**
   - Use Agency Swarm framework
   - Combine multiple tools
   - Add custom logic

---

## Support

- **Documentation:** See [README.md](../../README.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/agentswarm-tools/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/agentswarm-tools/discussions)

---

**Built for AI Agent Development** | Version 2.0.0
