# Agency Swarm Framework Features Guide

**What the Framework Already Provides - Don't Build These!**

This guide helps you leverage Agency Swarm's built-in capabilities and avoid rebuilding functionality that already exists in the framework.

---

## Table of Contents

1. [What Agency Swarm Provides (DON'T BUILD)](#what-agency-swarm-provides-dont-build)
2. [Built-in Tools](#built-in-tools)
3. [What to Build vs What to Avoid](#what-to-build-vs-what-to-avoid)
4. [Migration Guide from Other Frameworks](#migration-guide-from-other-frameworks)
5. [Best Practices](#best-practices)
6. [Code Examples](#code-examples)

---

## What Agency Swarm Provides (DON'T BUILD)

### 1. Thread & Memory Management

**What's Included:**
- Persistent conversation threads
- Automatic state management
- Thread history and retrieval
- Cross-agent communication
- Message persistence

**Built-in Callbacks:**
```python
from agency_swarm import Agency

# Thread persistence is built-in
agency = Agency(
    load_threads_callback=load_custom_threads,  # Optional custom loader
    save_threads_callback=save_custom_threads,  # Optional custom saver
    threads_callbacks={
        "load": load_threads,
        "save": save_threads
    }
)
```

**DON'T BUILD:**
- Custom thread management systems
- Message history databases
- Conversation state handlers
- Thread persistence layers

**DO THIS INSTEAD:**
```python
# Use built-in thread management
from agency_swarm import Agency, Agent

agency = Agency(
    [researcher, writer],
    shared_instructions="Project context here"
)

# Threads are automatically managed
response = agency.run("Research topic X")
```

---

### 2. Context Management

**What's Included:**
- Agent-level context storage
- Cross-agent context sharing
- Automatic context injection
- Context lifecycle management

**Built-in Methods:**
```python
class MyAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def custom_method(self):
        # Built-in context access
        user_data = self.context.get("user_preferences")
        self.context.set("last_query", "example")
```

**DON'T BUILD:**
- Custom context managers
- State storage systems
- Session management tools
- Context databases

**DO THIS INSTEAD:**
```python
# Leverage built-in context
from agency_swarm import Agent

class ResearchAgent(Agent):
    def setup(self):
        # Use framework's context system
        self.context.set("research_sources", [])

    def add_source(self, source):
        sources = self.context.get("research_sources", [])
        sources.append(source)
        self.context.set("research_sources", sources)
```

---

### 3. Code Execution

**What's Included:**
- IPython interpreter with sandboxing
- Persistent shell environment
- File system operations
- Safe code execution

**Built-in Tools:**
```python
from agency_swarm.tools import IPythonInterpreter, PersistentShellTool

# Already available - don't recreate
IPythonInterpreter  # Python code execution
PersistentShellTool # Shell command execution
```

**DON'T BUILD:**
- Python code execution tools
- Shell command wrappers
- File manipulation tools (basic ones)
- Code sandboxing systems

**DO THIS INSTEAD:**
```python
from agency_swarm import Agent
from agency_swarm.tools import IPythonInterpreter, PersistentShellTool

# Use built-in tools
data_analyst = Agent(
    name="DataAnalyst",
    tools=[IPythonInterpreter, PersistentShellTool],
    instructions="Analyze data using Python"
)
```

---

### 4. Observability & Tracing

**What's Included:**
- OpenAI native tracing
- Langfuse integration
- AgentOps integration
- Request logging
- Performance metrics

**Built-in Configuration:**
```python
# Automatic OpenAI tracing
import os
os.environ["OPENAI_LOG_LEVEL"] = "debug"

# Langfuse integration (built-in)
os.environ["LANGFUSE_PUBLIC_KEY"] = "your_key"
os.environ["LANGFUSE_SECRET_KEY"] = "your_secret"

# AgentOps integration (built-in)
os.environ["AGENTOPS_API_KEY"] = "your_key"
```

**DON'T BUILD:**
- Custom logging systems for LLM calls
- Request tracing middleware
- Performance monitoring dashboards
- Analytics pipelines for agent behavior

**DO THIS INSTEAD:**
```python
# Use built-in observability
from agency_swarm import Agency
import os

# Enable built-in tracing
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk_..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk_..."

agency = Agency([agent1, agent2])
# All interactions automatically traced
```

---

### 5. MCP (Model Context Protocol) Integration

**What's Included:**
- Full MCP server support
- 100+ pre-built MCP integrations
- Dynamic tool loading
- Protocol handling

**Built-in MCP Support:**
```python
from agency_swarm import Agent

# MCP tools auto-discovered and loaded
agent = Agent(
    name="MCPAgent",
    mcp_servers=["filesystem", "github", "postgres"],
    tools=[]  # MCP tools added automatically
)
```

**DON'T BUILD:**
- MCP protocol implementations
- MCP server connectors
- Tool discovery systems for MCP
- MCP configuration managers

**DO THIS INSTEAD:**
```python
# Leverage built-in MCP support
from agency_swarm import Agent

agent = Agent(
    name="Developer",
    mcp_servers=[
        "filesystem",  # File operations
        "github",      # GitHub integration
        "postgres"     # Database access
    ]
)
```

---

### 6. LLM Routing

**What's Included:**
- LiteLLM integration (100+ LLM providers)
- Automatic model routing
- Fallback handling
- Cost optimization

**Built-in Router:**
```python
from agency_swarm import Agent

# LiteLLM built-in - supports all providers
agent = Agent(
    name="MultiModelAgent",
    model="gpt-4o",              # OpenAI
    # OR
    model="claude-3-5-sonnet",   # Anthropic
    # OR
    model="gemini/gemini-pro"    # Google
)
```

**DON'T BUILD:**
- Multi-LLM routing systems
- Provider abstraction layers
- Model fallback logic
- Cost calculation systems

**DO THIS INSTEAD:**
```python
# Use LiteLLM's built-in routing
from agency_swarm import Agent

# Automatic routing with fallback
primary_agent = Agent(
    name="Primary",
    model="gpt-4o",
    fallback_models=["claude-3-5-sonnet", "gemini-pro"]
)
```

---

### 7. Async & Batch Processing

**What's Included:**
- Async agent execution
- Batch request handling
- Parallel tool execution
- Queue management

**Built-in Async:**
```python
from agency_swarm import Agency
import asyncio

async def run_parallel():
    agency = Agency([agent1, agent2])

    # Built-in async support
    results = await asyncio.gather(
        agency.run_async("Task 1"),
        agency.run_async("Task 2"),
        agency.run_async("Task 3")
    )
    return results
```

**DON'T BUILD:**
- Async execution wrappers
- Batch processing queues
- Parallel task managers
- Job scheduling systems (basic)

**DO THIS INSTEAD:**
```python
# Use framework's async capabilities
from agency_swarm import Agency

agency = Agency([researcher, writer])

# Batch processing built-in
tasks = ["Research A", "Research B", "Research C"]
results = [agency.run(task) for task in tasks]
```

---

## Built-in Tools

### Agency Swarm Native Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| **IPythonInterpreter** | Execute Python code | Data analysis, calculations, scripting |
| **PersistentShellTool** | Run shell commands | System operations, file management |
| **LoadFileAttachment** | Load file attachments | Process user-uploaded files |

**Example Usage:**
```python
from agency_swarm import Agent
from agency_swarm.tools import IPythonInterpreter, PersistentShellTool, LoadFileAttachment

# Code execution agent
coder = Agent(
    name="Coder",
    tools=[IPythonInterpreter],
    instructions="Execute Python code for data analysis"
)

# System operations agent
sysadmin = Agent(
    name="SysAdmin",
    tools=[PersistentShellTool],
    instructions="Manage system operations via shell"
)

# File processing agent
file_processor = Agent(
    name="FileProcessor",
    tools=[LoadFileAttachment],
    instructions="Process uploaded files"
)
```

---

## What to Build vs What to Avoid

### DO BUILD (Missing from Framework)

| Category | Build These | Why |
|----------|-------------|-----|
| **Domain-Specific Tools** | Web search, email, calendar, media generation | Framework is domain-agnostic |
| **API Integrations** | Google APIs, Twilio, Stripe, etc. | External service connectors |
| **Data Processing** | CSV parsers, PDF extractors, image analyzers | Specialized data handling |
| **Business Logic** | Industry-specific workflows | Custom business requirements |
| **UI Components** | Custom dashboards, visualizations | User-facing features |

### DON'T BUILD (Already in Framework)

| Category | Don't Build | Use Instead |
|----------|-------------|-------------|
| **Memory** | Thread managers, conversation history | Built-in thread persistence |
| **Context** | Session storage, state management | `self.context.get/set()` |
| **Execution** | Python runners, shell wrappers | IPythonInterpreter, PersistentShellTool |
| **Observability** | LLM loggers, trace collectors | Langfuse/AgentOps integration |
| **MCP** | Protocol handlers, server connectors | Built-in MCP support |
| **Routing** | Multi-LLM switches, fallback logic | LiteLLM integration |
| **Async** | Task queues, parallel executors | Built-in async methods |

---

## Migration Guide from Other Frameworks

### From LangChain

| LangChain | Agency Swarm Equivalent |
|-----------|------------------------|
| `ConversationBufferMemory` | Built-in thread management |
| `ConversationSummaryMemory` | Agent context + summarization tool |
| `PythonREPL` | IPythonInterpreter |
| `BashProcess` | PersistentShellTool |
| `LangSmith` | Langfuse integration |
| Custom tools | BaseTool from agentswarm-tools |

**Migration Example:**
```python
# LangChain (OLD)
from langchain.memory import ConversationBufferMemory
from langchain.tools import PythonREPLTool

memory = ConversationBufferMemory()
python_tool = PythonREPLTool()

# Agency Swarm (NEW)
from agency_swarm import Agent
from agency_swarm.tools import IPythonInterpreter

agent = Agent(
    name="Agent",
    tools=[IPythonInterpreter]
    # Memory built-in, no setup needed
)
```

### From CrewAI

| CrewAI | Agency Swarm Equivalent |
|--------|------------------------|
| `Task` | Agent instructions |
| `Process` | Agency configuration |
| `Memory` | Built-in threads |
| Custom tools | BaseTool |

**Migration Example:**
```python
# CrewAI (OLD)
from crewai import Agent, Task, Crew

task = Task(
    description="Research topic",
    agent=researcher
)
crew = Crew(agents=[researcher], tasks=[task])

# Agency Swarm (NEW)
from agency_swarm import Agency, Agent

agency = Agency(
    [researcher],
    shared_instructions="Research topics thoroughly"
)
agency.run("Research topic")
```

### From AutoGen

| AutoGen | Agency Swarm Equivalent |
|---------|------------------------|
| `ConversableAgent` | Agent |
| `GroupChat` | Agency with multiple agents |
| `UserProxyAgent` | Built-in human-in-the-loop |
| Code execution | IPythonInterpreter |

**Migration Example:**
```python
# AutoGen (OLD)
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent("assistant")
user_proxy = UserProxyAgent("user", code_execution_config={"work_dir": "."})

# Agency Swarm (NEW)
from agency_swarm import Agent, Agency
from agency_swarm.tools import IPythonInterpreter

assistant = Agent(
    name="Assistant",
    tools=[IPythonInterpreter]
)
agency = Agency([assistant])
```

---

## Best Practices

### 1. Use Built-in Features First

**GOOD:**
```python
# Leverage framework capabilities
from agency_swarm import Agent

agent = Agent(
    name="Analyst",
    tools=[IPythonInterpreter],
    model="gpt-4o",
    # Context managed automatically
    # Threads persisted automatically
    # Observability enabled via env vars
)
```

**BAD:**
```python
# Don't recreate framework features
class CustomThreadManager:
    def __init__(self):
        self.threads = {}  # DON'T DO THIS

class CustomContextStore:
    def __init__(self):
        self.context = {}  # DON'T DO THIS
```

### 2. Build Domain-Specific Tools

**GOOD:**
```python
# Build what's missing
from shared.base import BaseTool
from pydantic import Field

class WebSearchTool(BaseTool):
    """Custom web search - not in framework"""
    query: str = Field(..., description="Search query")

    def _execute(self):
        # Domain-specific implementation
        return self._search_web()
```

**BAD:**
```python
# Don't rebuild framework tools
class CustomPythonExecutor(BaseTool):
    """DON'T - use IPythonInterpreter instead"""
    code: str = Field(..., description="Python code")

    def _execute(self):
        exec(self.code)  # BAD - already exists
```

### 3. Configure, Don't Customize Core

**GOOD:**
```python
# Configure built-in features
import os

# Enable observability
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk_..."
os.environ["AGENTOPS_API_KEY"] = "key_..."

# Use configuration
from agency_swarm import Agency

agency = Agency(
    agents=[agent1, agent2],
    shared_instructions="Context here"
    # Tracing automatically enabled
)
```

**BAD:**
```python
# Don't wrap or replace core features
class CustomAgency:
    """DON'T - use Agency configuration instead"""
    def __init__(self):
        self.custom_logging = CustomLogger()  # BAD
        self.custom_threads = CustomThreads()  # BAD
```

### 4. Extend, Don't Replace

**GOOD:**
```python
# Extend base classes
from agency_swarm import Agent
from shared.base import BaseTool

class SpecializedAgent(Agent):
    """Add domain-specific methods"""

    def custom_workflow(self):
        # Build on top of framework
        result = self.run("Step 1")
        # Custom logic here
        return self.run(f"Step 2: {result}")
```

**BAD:**
```python
# Don't replace framework components
class ReplacementAgent:
    """DON'T - extend Agent instead"""
    def __init__(self):
        # Reimplementing framework logic
        self.messages = []  # BAD
        self.tools = []     # BAD
```

---

## Code Examples

### Example 1: Leveraging Thread Management

**DON'T:**
```python
# Custom thread management (WRONG)
class ConversationManager:
    def __init__(self):
        self.conversations = {}

    def save_message(self, thread_id, message):
        if thread_id not in self.conversations:
            self.conversations[thread_id] = []
        self.conversations[thread_id].append(message)
```

**DO:**
```python
# Use built-in threads (CORRECT)
from agency_swarm import Agency

agency = Agency([researcher, writer])

# Threads managed automatically
response1 = agency.run("First query")
response2 = agency.run("Follow-up query")
# Context preserved automatically
```

### Example 2: Using Context System

**DON'T:**
```python
# Custom context storage (WRONG)
class ContextStore:
    def __init__(self):
        self.data = {}

    def set_context(self, key, value):
        self.data[key] = value
```

**DO:**
```python
# Use built-in context (CORRECT)
from agency_swarm import Agent

class ResearchAgent(Agent):
    def research_workflow(self):
        # Store in context
        self.context.set("sources", ["source1", "source2"])

        # Retrieve from context
        sources = self.context.get("sources")
        return sources
```

### Example 3: Code Execution

**DON'T:**
```python
# Custom Python executor (WRONG)
from pydantic import Field
from shared.base import BaseTool

class PythonRunner(BaseTool):
    """DON'T - use IPythonInterpreter"""
    code: str = Field(..., description="Python code")

    def _execute(self):
        exec(self.code)  # Dangerous and redundant
```

**DO:**
```python
# Use built-in tool (CORRECT)
from agency_swarm import Agent
from agency_swarm.tools import IPythonInterpreter

analyst = Agent(
    name="DataAnalyst",
    tools=[IPythonInterpreter],
    instructions="Analyze data using Python"
)

# Agent can execute Python automatically
```

### Example 4: Multi-Model Routing

**DON'T:**
```python
# Custom LLM router (WRONG)
class ModelRouter:
    def __init__(self):
        self.models = {
            "fast": "gpt-3.5-turbo",
            "smart": "gpt-4o",
            "cheap": "claude-instant"
        }

    def route(self, task_type):
        # Custom routing logic
        pass
```

**DO:**
```python
# Use built-in routing (CORRECT)
from agency_swarm import Agent

# LiteLLM handles routing
fast_agent = Agent(name="Fast", model="gpt-3.5-turbo")
smart_agent = Agent(name="Smart", model="gpt-4o")
cheap_agent = Agent(name="Cheap", model="claude-instant-1.2")

# Framework handles model switching
```

### Example 5: Observability

**DON'T:**
```python
# Custom tracing (WRONG)
class LLMTracer:
    def __init__(self):
        self.logs = []

    def log_request(self, request):
        self.logs.append({
            "timestamp": time.time(),
            "request": request
        })
```

**DO:**
```python
# Use built-in observability (CORRECT)
import os

# Enable Langfuse tracing
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk_..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk_..."

# Enable AgentOps
os.environ["AGENTOPS_API_KEY"] = "key_..."

from agency_swarm import Agency

# All requests automatically traced
agency = Agency([agent1, agent2])
```

### Example 6: Async Execution

**DON'T:**
```python
# Custom async manager (WRONG)
import asyncio

class AsyncTaskManager:
    def __init__(self):
        self.tasks = []

    async def run_parallel(self, tasks):
        return await asyncio.gather(*tasks)
```

**DO:**
```python
# Use built-in async (CORRECT)
from agency_swarm import Agency
import asyncio

async def run_multiple():
    agency = Agency([researcher])

    # Built-in async support
    results = await asyncio.gather(
        agency.run_async("Task 1"),
        agency.run_async("Task 2"),
        agency.run_async("Task 3")
    )
    return results
```

### Example 7: MCP Integration

**DON'T:**
```python
# Custom MCP client (WRONG)
class MCPClient:
    def __init__(self, server_url):
        self.server = server_url

    def connect(self):
        # Custom MCP implementation
        pass
```

**DO:**
```python
# Use built-in MCP (CORRECT)
from agency_swarm import Agent

# MCP servers auto-configured
agent = Agent(
    name="Developer",
    mcp_servers=[
        "filesystem",  # File operations
        "github",      # GitHub API
        "postgres"     # Database
    ]
)
# Tools loaded automatically
```

---

## Quick Reference Checklist

Before building a new tool or feature, ask:

- [ ] Does Agency Swarm already provide this?
- [ ] Is this available as an MCP server?
- [ ] Can I configure existing features instead?
- [ ] Am I rebuilding thread/context management?
- [ ] Am I creating a custom code executor?
- [ ] Am I building observability from scratch?
- [ ] Can LiteLLM already route to this model?
- [ ] Does IPythonInterpreter/PersistentShellTool cover this?

**If you answered YES to any question, use the built-in feature instead of building new.**

---

## Summary

### Framework Provides (USE THESE)

1. **Thread & Memory Management** - Automatic persistence
2. **Context System** - `self.context.get/set()`
3. **Code Execution** - IPythonInterpreter, PersistentShellTool
4. **Observability** - Langfuse, AgentOps, OpenAI tracing
5. **MCP Integration** - 100+ servers ready
6. **LLM Routing** - LiteLLM for all providers
7. **Async Execution** - Built-in async methods
8. **File Operations** - LoadFileAttachment

### You Should Build (CUSTOM TOOLS)

1. **Domain-Specific APIs** - Google, Twilio, Stripe, etc.
2. **Data Processing** - CSV, PDF, media analysis
3. **Business Logic** - Industry workflows
4. **UI Components** - Dashboards, visualizations
5. **Specialized Tools** - Search, generation, communication

### Golden Rule

**If it's about agent infrastructure (memory, threads, execution, observability), the framework has it. If it's about domain logic (APIs, data, business rules), build it as a tool.**

---

**Last Updated:** 2025-01-22
**Framework Version:** Agency Swarm 2.x
**Maintained By:** AgentSwarm Tools Team
