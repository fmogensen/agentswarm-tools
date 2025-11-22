# Agency Swarm Integration Guide

**Complete Integration Documentation for AgentSwarm.ai Platform**

## Overview

This document provides complete integration guidance for using the AgentSwarm Tools Framework with the Agency Swarm platform (https://agency-swarm.ai). All 61 tools are designed to be **100% compatible** with Agency Swarm's `BaseTool` interface while adding enhanced features like analytics, security, and error handling.

## ✅ Compatibility Status

**FULLY COMPATIBLE** - No modifications required to Agency Swarm framework.

Our `BaseTool` inherits from `agency_swarm.BaseTool` and follows all Agency Swarm conventions:

```python
from agency_swarm import BaseTool as AgencyBaseTool

class BaseTool(AgencyBaseTool):
    """Enhanced base tool with built-in features."""
    # All Agency Swarm features preserved
    # Additional features added transparently
```

## Quick Start

### 1. Installation

```bash
# Install Agency Swarm
pip install agency-swarm

# Install AgentSwarm Tools
pip install agentswarm-tools

# Or install from source
cd agentswarm-tools
pip install -e .
```

### 2. Basic Usage with Agency Swarm

```python
from agency_swarm import Agent, Agency
from agentswarm_tools.search import WebSearchTool
from agentswarm_tools.media_generation import ImageGenerationTool

# Create agent with tools (standard Agency Swarm pattern)
researcher = Agent(
    name="Researcher",
    description="Research agent with web search capabilities",
    instructions="Search the web and provide comprehensive research",
    tools=[WebSearchTool],  # Just add the tool class
    model="gpt-4o"
)

# Tools work exactly like standard Agency Swarm tools
# No special configuration needed!
```

### 3. Using Tools in Agency

```python
from agency_swarm import Agency
from agentswarm_tools.search import WebSearchTool, ScholarSearchTool
from agentswarm_tools.web_content import CrawlerTool
from agentswarm_tools.document_creation import CreateAgentTool

# Define agents
ceo = Agent(
    name="CEO",
    description="Manages research projects",
    tools=[CreateAgentTool],
    model="gpt-4o"
)

researcher = Agent(
    name="Researcher",
    description="Conducts web research",
    tools=[WebSearchTool, ScholarSearchTool, CrawlerTool],
    model="gpt-4o"
)

# Create agency (standard Agency Swarm pattern)
agency = Agency(
    ceo, researcher,
    communication_flows=[
        ceo > researcher,
    ],
    shared_instructions="Focus on thorough research with citations"
)

# Run agency
agency.copilot_demo()  # Web UI
# or
await agency.get_completion_stream("Research AI developments in 2024")
```

##  Core Compatibility Features

### 1. Tool Interface

Our tools use the **exact same interface** as Agency Swarm:

```python
# Standard Agency Swarm tool
from agency_swarm import BaseTool
from pydantic import Field

class StandardTool(BaseTool):
    """Tool description."""
    param: str = Field(..., description="Parameter")

    def run(self):
        return "result"

# AgentSwarm tool (identical interface!)
from agentswarm_tools.shared.base import BaseTool
from pydantic import Field

class AgentSwarmTool(BaseTool):
    """Tool description."""
    param: str = Field(..., description="Parameter")
    tool_name = "my_tool"

    def _execute(self):  # Internal method name different
        return "result"

    # run() is provided by BaseTool and calls _execute()
```

**Key Difference**:
- Agency Swarm tools implement `run()`
- AgentSwarm tools implement `_execute()` (called by enhanced `run()`)
- This allows us to add error handling, analytics, etc. transparently

### 2. Pydantic Validation

Full Pydantic support (Agency Swarm requirement):

```python
from agentswarm_tools.shared.base import BaseTool
from pydantic import Field, validator

class MyTool(BaseTool):
    """Tool with validation."""

    query: str = Field(
        ...,
        description="Search query",
        min_length=1,
        max_length=200
    )

    num_results: int = Field(
        default=10,
        description="Number of results",
        ge=1,
        le=100
    )

    @validator('query')
    def validate_query(cls, v):
        if '\n' in v:
            raise ValueError("Query cannot contain newlines")
        return v.strip()

    tool_name = "my_tool"

    def _execute(self):
        # Implementation
        pass
```

### 3. Type Safety

All tools are fully type-safe (Agency Swarm requirement):

```python
from typing import List, Dict, Optional
from agentswarm_tools.shared.base import BaseTool
from pydantic import Field

class TypeSafeTool(BaseTool):
    """Type-safe tool."""

    urls: List[str] = Field(..., description="List of URLs")
    options: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional configuration"
    )

    tool_name = "type_safe_tool"

    def _execute(self) -> Dict[str, any]:
        """Returns dictionary with results."""
        return {
            "processed": len(self.urls),
            "results": []
        }
```

## 🚀 Enhanced Features (Optional)

While fully compatible with Agency Swarm, our tools provide optional enhancements:

### 1. Built-in Analytics

```python
from agentswarm_tools.shared.analytics import get_metrics

# Get metrics for any tool
metrics = get_metrics("web_search", days=7)
print(f"Total requests: {metrics.total_requests}")
print(f"Success rate: {metrics.success_rate}%")
print(f"Avg latency: {metrics.avg_duration_ms}ms")
```

### 2. Rate Limiting

```python
# Automatic rate limiting (transparent to agents)
# No configuration needed - works out of the box

# Optional: Custom rate limits
from agentswarm_tools.shared.security import get_rate_limiter

limiter = get_rate_limiter()
limiter.set_limit("web_search", 100)  # 100 requests/minute
```

### 3. Error Handling

```python
# Errors are automatically handled and formatted
# Agents receive structured error responses:
{
    "success": false,
    "error": {
        "code": "RATE_LIMIT",
        "message": "Rate limit exceeded",
        "retry_after": 60,
        "request_id": "abc-123"
    }
}
```

### 4. Request Tracing

```python
# Every request gets a unique ID for debugging
# Check logs for: [request_id=abc-123-def-456]

# Enable detailed logging
import logging
logging.getLogger("agentswarm.tools").setLevel(logging.DEBUG)
```

## 🔌 SuperAgentSwarm Integration

For the default SuperAgentSwarm that greets users on AgentSwarm.ai:

```python
from agency_swarm import Agent, Agency
from agentswarm_tools.search import WebSearchTool, ScholarSearchTool, ImageSearchTool
from agentswarm_tools.web_content import CrawlerTool, SummarizeLargeDocumentTool
from agentswarm_tools.media_generation import ImageGenerationTool, VideoGenerationTool
from agentswarm_tools.media_analysis import UnderstandImagesTool, AudioTranscribeTool
from agentswarm_tools.communication import GmailSearchTool, EmailDraftTool
from agentswarm_tools.visualization import GenerateLineChartTool, GeneratePieChartTool
from agentswarm_tools.document_creation import CreateAgentTool
from agentswarm_tools.utils import ThinkTool, AskForClarificationTool

# SuperAgent - The main agent users interact with
super_agent = Agent(
    name="SuperAgent",
    description="Universal AI assistant with comprehensive capabilities",
    instructions="""You are SuperAgent, the flagship AI assistant for AgentSwarm.ai.

    You have access to 61 powerful tools across 12 categories:
    - Search & Research (web, academic, images, videos)
    - Content Creation (images, videos, audio, documents)
    - Content Analysis (images, videos, audio)
    - Communication (email, calendar, phone)
    - Data Visualization (15 chart types)
    - File Management (cloud storage, OneDrive)
    - Code Execution (bash, file operations)
    - Workspace Integration (Notion, OneDrive)

    Approach:
    1. Understand the user's request fully
    2. Break down complex tasks into steps
    3. Use the most appropriate tools
    4. Provide clear, helpful responses
    5. Ask for clarification when needed

    Always prioritize:
    - Accuracy and reliability
    - User privacy and security
    - Efficient tool usage
    - Clear communication
    """,
    tools=[
        # Search & Information
        WebSearchTool,
        ScholarSearchTool,
        ImageSearchTool,

        # Content Tools
        CrawlerTool,
        SummarizeLargeDocumentTool,

        # Media Generation
        ImageGenerationTool,

        # Media Analysis
        UnderstandImagesTool,
        AudioTranscribeTool,

        # Communication
        GmailSearchTool,
        EmailDraftTool,

        # Visualization
        GenerateLineChartTool,
        GeneratePieChartTool,

        # Document Creation
        CreateAgentTool,

        # Utilities
        ThinkTool,
        AskForClarificationTool,
    ],
    model="gpt-4o",
    temperature=0.7
)

# Create SuperAgentSwarm
super_swarm = Agency(
    super_agent,  # Entry point
    communication_flows=[],  # Single agent for now
    shared_instructions="""AgentSwarm.ai Platform Guidelines:

    1. Privacy First: Never log or store user PII
    2. Cost Awareness: Use appropriate models for tasks
    3. Error Handling: Gracefully handle all errors
    4. User Experience: Provide helpful, clear responses
    5. Security: Validate all inputs and API keys
    """
)

# Run the swarm
super_swarm.copilot_demo()
```

## 📊 Configuration

### Environment Variables

```bash
# Required for different tool categories
# Search
SERPAPI_KEY=your_key
SEMANTIC_SCHOLAR_KEY=your_key

# Media Generation
OPENAI_API_KEY=your_key
STABILITY_API_KEY=your_key
ELEVENLABS_API_KEY=your_key

# Communication
GMAIL_CLIENT_ID=your_id
GMAIL_CLIENT_SECRET=your_secret

# Storage
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Analytics (Optional)
ANALYTICS_ENABLED=true
ANALYTICS_BACKEND=file  # or 'memory' or 'postgresql'
```

### Tool Configuration

```python
# Optional: Configure tools globally
from agentswarm_tools.shared.security import get_rate_limiter

# Set custom rate limits
limiter = get_rate_limiter()
limiter.set_limit("search", 100)          # 100 req/min
limiter.set_limit("media_generation", 10) # 10 req/min

# Disable analytics for specific environments
import os
os.environ["ANALYTICS_ENABLED"] = "false"
```

## 🧪 Testing Tools with Agency Swarm

### Unit Testing

```python
import pytest
from agentswarm_tools.search import WebSearchTool

def test_web_search():
    """Test web search tool."""
    tool = WebSearchTool(query="Python programming")
    result = tool.run()

    assert "organic_results" in result
    assert len(result["organic_results"]) > 0
    assert result["organic_results"][0]["title"]
    assert result["organic_results"][0]["link"]
```

### Integration Testing with Agents

```python
import pytest
from agency_swarm import Agent
from agentswarm_tools.search import WebSearchTool

@pytest.mark.asyncio
async def test_agent_with_tool():
    """Test agent using web search tool."""
    agent = Agent(
        name="TestAgent",
        description="Test agent",
        tools=[WebSearchTool],
        model="gpt-4o"
    )

    # Test that agent can use the tool
    # (requires actual API call)
    response = await agent.get_completion("Search for Python tutorials")
    assert response
```

## 🛠️ Debugging

### Enable Debug Logging

```python
import logging

# Enable debug logging for tools
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agentswarm.tools")
logger.setLevel(logging.DEBUG)

# Now all tool operations will log detailed information
```

### Check Tool Health

```bash
# Using CLI
agentswarm-tools health web_search

# Or programmatically
from agentswarm_tools.search import WebSearchTool

tool = WebSearchTool(query="test")
try:
    result = tool.run()
    print("✅ Tool is healthy")
except Exception as e:
    print(f"❌ Tool error: {e}")
```

### View Analytics

```bash
# View metrics for a tool
agentswarm-tools analytics web_search --days 7

# Or programmatically
from agentswarm_tools.shared.analytics import print_metrics

print_metrics("web_search", days=7)
```

## 🔐 Security Best Practices

### 1. API Key Management

```python
# ✅ GOOD - Use environment variables
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ❌ BAD - Hardcoded keys
OPENAI_API_KEY = "sk-..."  # Never do this!
```

### 2. Input Validation

```python
from agentswarm_tools.shared.base import BaseTool
from pydantic import Field, validator

class SecureTool(BaseTool):
    """Tool with input validation."""

    url: str = Field(..., description="URL to process")

    @validator('url')
    def validate_url(cls, v):
        # Input validation happens automatically
        # Pydantic + our security layer
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Invalid URL scheme")
        return v

    tool_name = "secure_tool"

    def _execute(self):
        # Input is already validated
        pass
```

### 3. Rate Limiting

```python
# Rate limiting is automatic
# But you can customize per-agent:

from agency_swarm import Agent
from agentswarm_tools.search import WebSearchTool

# High-priority agent
priority_agent = Agent(
    name="Priority",
    tools=[WebSearchTool],
    # Tools will respect rate limits per-agent
)
```

## 📝 Migration from Standard Agency Swarm Tools

If you have existing Agency Swarm tools:

### Before (Standard Agency Swarm)

```python
from agency_swarm import BaseTool
from pydantic import Field

class MyTool(BaseTool):
    """My custom tool."""
    param: str = Field(...)

    def run(self):
        result = do_something(self.param)
        return result
```

### After (AgentSwarm Tools)

```python
from agentswarm_tools.shared.base import BaseTool
from pydantic import Field

class MyTool(BaseTool):
    """My custom tool."""
    param: str = Field(...)
    tool_name = "my_tool"  # Add this

    def _execute(self):  # Rename run() to _execute()
        result = do_something(self.param)
        return result
```

**Benefits of migration:**
- ✅ Automatic error handling
- ✅ Analytics and monitoring
- ✅ Rate limiting
- ✅ Request tracing
- ✅ Security features
- ✅ Still 100% compatible with Agency Swarm!

## 🚨 Troubleshooting

### Issue: "Missing API key" error

**Solution:**
```bash
# Check which keys are missing
agentswarm-tools validate-keys

# Set missing keys
export SERPAPI_KEY=your_key
export OPENAI_API_KEY=your_key
```

### Issue: Rate limit errors

**Solution:**
```python
# Check current limits
from agentswarm_tools.shared.security import get_rate_limiter

limiter = get_rate_limiter()
remaining = limiter.get_remaining("web_search")
print(f"Remaining requests: {remaining}")

# Increase limit if needed
limiter.set_limit("web_search", 200)  # 200 req/min
```

### Issue: Tool not working with agent

**Solution:**
```python
# Test tool in isolation first
from agentswarm_tools.search import WebSearchTool

tool = WebSearchTool(query="test")
result = tool.run()
print(result)  # Should work

# If tool works but agent doesn't use it:
# 1. Check tool description is clear
# 2. Check agent instructions mention the tool
# 3. Enable debug logging to see agent's tool selection
```

## 📚 Additional Resources

- **Agency Swarm Docs**: https://agency-swarm.ai
- **AgentSwarm Tools API**: [docs/api/README.md](../api/README.md)
- **Tool Development Guide**: [guides/development.md](../guides/development.md)
- **Examples**: [examples/](../examples/)

## ✅ Validation Checklist

Before deploying to production:

- [ ] All required API keys are set
- [ ] Rate limits are configured appropriately
- [ ] Analytics backend is configured (file/database)
- [ ] Logging level is set correctly
- [ ] Error handling is tested
- [ ] Tools work with Agency Swarm agents
- [ ] Security settings are reviewed
- [ ] Backup/monitoring is in place

## 🎯 Summary

**No modifications needed to Agency Swarm framework!**

Our tools:
✅ Inherit from `agency_swarm.BaseTool`
✅ Follow Pydantic validation patterns
✅ Work with `@function_tool` decorator
✅ Compatible with all Agency Swarm features
✅ Add optional enhancements transparently

Just install and use - it's that simple!

---

**Questions or issues?** Create an issue on GitHub or contact support@agentswarm.ai
