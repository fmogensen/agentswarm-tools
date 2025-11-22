# LiteLLM Cost Optimization Guide for Agency Swarm

**Achieve 90% Cost Savings Through Strategic Model Assignment**

---

## Table of Contents

1. [What is LiteLLM?](#what-is-litellm)
2. [Why LiteLLM is Built Into Agency Swarm](#why-litellm-is-built-into-agency-swarm)
3. [The Three-Tier Model Strategy](#the-three-tier-model-strategy)
4. [Setup and Configuration](#setup-and-configuration)
5. [100+ Providers Supported](#100-providers-supported)
6. [Auto-Routing Strategies](#auto-routing-strategies)
7. [Cost Tracking and Optimization](#cost-tracking-and-optimization)
8. [Real-World Examples](#real-world-examples)
9. [Why NOT to Use RouteLLM](#why-not-to-use-routellm)
10. [Best Practices](#best-practices)

---

## What is LiteLLM?

**LiteLLM** is a unified interface for calling 100+ LLM providers (OpenAI, Anthropic, Google, AWS, Azure, Hugging Face, etc.) with a single, consistent API. It translates your requests into provider-specific formats automatically.

### Key Features

- **Unified API**: Same code works across all providers
- **Automatic Retry**: Built-in retry logic and fallbacks
- **Cost Tracking**: Automatic token usage and cost calculation
- **Load Balancing**: Distribute requests across multiple deployments
- **Caching**: Response caching to reduce API calls
- **Provider Fallbacks**: Automatic fallback to alternative providers

### Why It Matters for Agency Swarm

Agency Swarm already uses LiteLLM under the hood, which means you can:

1. **Mix and match models** across agents without changing code
2. **Route simple tasks to cheap models** (90% cost reduction)
3. **Reserve premium models for complex reasoning** (strategic allocation)
4. **Track costs per agent** to optimize spending
5. **Implement automatic fallbacks** for reliability

---

## Why LiteLLM is Built Into Agency Swarm

Agency Swarm is designed for **multi-agent systems** where different agents have different complexity requirements. LiteLLM enables:

### 1. Heterogeneous Agent Teams

```python
from agency_swarm import Agent, Agency

# Simple data entry agent - uses cheap model
data_clerk = Agent(
    name="DataClerk",
    description="Extracts structured data from documents",
    model="gemini/gemini-2.0-flash",  # $0.075/1M tokens
    tools=[ExtractData, ValidateFormat]
)

# Complex reasoning agent - uses premium model
strategist = Agent(
    name="Strategist",
    description="Analyzes market trends and creates strategies",
    model="anthropic/claude-3-5-sonnet",  # $3/1M tokens
    tools=[WebSearch, AnalyzeData, GenerateReport]
)

# Coordinator - uses mid-tier model
coordinator = Agent(
    name="Coordinator",
    description="Routes tasks between agents",
    model="anthropic/claude-3-haiku",  # $1/1M tokens
    tools=[AssignTask, TrackProgress]
)
```

### 2. No Code Changes Required

LiteLLM's unified interface means switching models is as simple as changing a string:

```python
# Change from OpenAI to Google
agent.model = "gpt-4o"  # Before
agent.model = "gemini/gemini-2.0-flash"  # After - 40x cheaper!

# Change from Anthropic to AWS Bedrock
agent.model = "anthropic/claude-3-5-sonnet"  # Before
agent.model = "bedrock/anthropic.claude-3-5-sonnet"  # After - same model, different provider
```

### 3. Built-in Cost Tracking

```python
import litellm

# Enable detailed logging
litellm.set_verbose = True

# Track costs automatically
response = litellm.completion(
    model="gemini/gemini-2.0-flash",
    messages=[{"role": "user", "content": "Summarize this text..."}]
)

print(f"Tokens used: {response.usage.total_tokens}")
print(f"Cost: ${response._hidden_params.get('response_cost', 0):.6f}")
```

---

## The Three-Tier Model Strategy

Optimize costs by assigning the **right model to the right agent** based on task complexity.

### Tier 1: CHEAP Models (80% of Agents)

**Model**: `gemini/gemini-2.0-flash`
**Cost**: $0.075 per 1M tokens (input/output combined)
**Use For**: Simple, repetitive tasks with clear structure

#### Ideal Agent Types

- **Data Entry Clerks**: Extract structured data from documents
- **Format Validators**: Check data against schemas
- **Simple Classifiers**: Categorize items into predefined buckets
- **Content Moderators**: Flag inappropriate content
- **Basic Summarizers**: Create bullet-point summaries
- **Template Fillers**: Populate predefined templates
- **Simple Routers**: Direct requests to appropriate agents

#### Example: Data Extraction Agent

```python
from agency_swarm import Agent
from tools.document_processing import ExtractData, ValidateSchema

data_extractor = Agent(
    name="DataExtractor",
    description="""
    Extracts structured information from invoices, receipts, and forms.
    Outputs JSON following predefined schemas. Validates all extracted data.
    """,
    instructions="""
    1. Read the document carefully
    2. Extract all fields from the schema
    3. Validate data types and formats
    4. Return JSON with extracted data
    5. Flag any missing or invalid fields
    """,
    model="gemini/gemini-2.0-flash",  # 40x cheaper than GPT-4
    tools=[ExtractData, ValidateSchema],
    temperature=0.1  # Low temperature for consistent output
)

# Cost comparison for 1M tokens
# GPT-4: $30
# Gemini Flash: $0.075
# Savings: 99.75%
```

### Tier 2: MID Models (15% of Agents)

**Model**: `anthropic/claude-3-haiku`
**Cost**: $1 per 1M tokens (input/output combined)
**Use For**: Moderate complexity, some reasoning required

#### Ideal Agent Types

- **Coordinators**: Route complex tasks between multiple agents
- **Quality Reviewers**: Check work quality with nuanced judgment
- **Content Editors**: Improve writing while maintaining voice
- **Customer Support**: Handle common issues with empathy
- **Meeting Schedulers**: Navigate calendars with conflict resolution
- **Report Compilers**: Combine data from multiple sources
- **Code Reviewers**: Check for common bugs and style issues

#### Example: Customer Support Agent

```python
from agency_swarm import Agent
from tools.communication import GmailSearch, GmailRead, EmailDraft

support_agent = Agent(
    name="SupportAgent",
    description="""
    Handles customer inquiries, troubleshoots common issues,
    and escalates complex problems to human agents.
    """,
    instructions="""
    1. Read customer email carefully
    2. Check knowledge base for solutions
    3. If found: Draft helpful, empathetic response
    4. If not found: Escalate to human with context
    5. Track resolution time and customer satisfaction
    """,
    model="anthropic/claude-3-haiku",  # 3x cheaper than Sonnet
    tools=[GmailSearch, GmailRead, EmailDraft],
    temperature=0.7  # Balanced for natural responses
)

# Cost comparison for 1M tokens
# Claude Sonnet: $3
# Claude Haiku: $1
# Savings: 66%
```

### Tier 3: PREMIUM Models (5% of Agents)

**Model**: `anthropic/claude-3-5-sonnet`
**Cost**: $3 per 1M tokens (input/output combined)
**Use For**: Complex reasoning, strategic decisions, creative work

#### Ideal Agent Types

- **Strategists**: Analyze data and create complex plans
- **Researchers**: Deep analysis requiring multi-step reasoning
- **Code Architects**: Design complex system architectures
- **Content Creators**: Write high-quality, creative content
- **Financial Advisors**: Complex financial modeling and advice
- **Legal Analysts**: Interpret complex legal documents
- **Medical Assistants**: Analyze symptoms with careful reasoning

#### Example: Market Research Agent

```python
from agency_swarm import Agent
from tools.search import WebSearch, ScholarSearch
from tools.analysis import AnalyzeData, GenerateReport

research_agent = Agent(
    name="MarketResearcher",
    description="""
    Conducts comprehensive market research, competitive analysis,
    and strategic recommendations for new product launches.
    """,
    instructions="""
    1. Gather data from multiple sources (web, academic, financial)
    2. Analyze competitive landscape and identify gaps
    3. Synthesize findings into strategic insights
    4. Predict market trends using historical data
    5. Create detailed report with recommendations
    6. Justify all recommendations with evidence
    """,
    model="anthropic/claude-3-5-sonnet",  # Best reasoning ability
    tools=[WebSearch, ScholarSearch, AnalyzeData, GenerateReport],
    temperature=0.3  # Low enough for accuracy, high enough for creativity
)

# This agent uses premium model because:
# - Requires complex reasoning across multiple data sources
# - Strategic recommendations need high-quality thinking
# - Cost of wrong decision >> cost of premium model
```

### Cost Breakdown: Three-Tier Strategy

Assume an agency with **20 agents** processing **100M tokens/month**:

| Tier | Agents | % | Tokens | Model | Cost/1M | Total Cost |
|------|--------|---|--------|-------|---------|------------|
| **CHEAP** | 16 | 80% | 80M | Gemini Flash | $0.075 | **$6.00** |
| **MID** | 3 | 15% | 15M | Claude Haiku | $1.00 | **$15.00** |
| **PREMIUM** | 1 | 5% | 5M | Claude Sonnet | $3.00 | **$15.00** |
| **TOTAL** | 20 | 100% | 100M | Mixed | - | **$36.00** |

**Compare to all-premium approach**:
- All agents using Claude Sonnet: 100M tokens × $3 = **$300**
- **Savings: $264/month (88% reduction)**

**Compare to all GPT-4**:
- All agents using GPT-4: 100M tokens × $30 = **$3,000**
- **Savings: $2,964/month (98.8% reduction)**

---

## Setup and Configuration

### Basic Setup

LiteLLM is already included in Agency Swarm. No additional installation needed!

```bash
# If you need to update or install manually
pip install litellm
```

### Environment Variables

Set API keys for providers you want to use:

```bash
# .env file
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google
GEMINI_API_KEY=...

# AWS Bedrock
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=us-east-1

# Azure
AZURE_API_KEY=...
AZURE_API_BASE=https://...
AZURE_API_VERSION=2024-02-15-preview

# Vertex AI (Google Cloud)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
VERTEX_PROJECT=your-project-id
VERTEX_LOCATION=us-central1
```

### Agent Configuration

#### Method 1: Direct Model Assignment (Simplest)

```python
from agency_swarm import Agent

agent = Agent(
    name="MyAgent",
    description="Agent description",
    model="gemini/gemini-2.0-flash",  # Just specify the model
    tools=[...]
)
```

#### Method 2: Environment-Based Configuration

```python
import os
from agency_swarm import Agent

# Set default model via environment
os.environ["DEFAULT_MODEL"] = "gemini/gemini-2.0-flash"

# All agents use this model unless overridden
agent = Agent(
    name="MyAgent",
    description="Agent description",
    tools=[...]
)
```

#### Method 3: Configuration File

```python
# config/models.yaml
agents:
  data_extractor:
    model: "gemini/gemini-2.0-flash"
    temperature: 0.1
    max_tokens: 1000

  support_agent:
    model: "anthropic/claude-3-haiku"
    temperature: 0.7
    max_tokens: 2000

  research_agent:
    model: "anthropic/claude-3-5-sonnet"
    temperature: 0.3
    max_tokens: 4000
```

```python
# Load configuration
import yaml
from agency_swarm import Agent

with open("config/models.yaml") as f:
    config = yaml.safe_load(f)

# Create agents from config
agents = {}
for agent_name, agent_config in config["agents"].items():
    agents[agent_name] = Agent(
        name=agent_name,
        model=agent_config["model"],
        temperature=agent_config.get("temperature", 0.5),
        max_tokens=agent_config.get("max_tokens", 2000),
        tools=[...]  # Load tools separately
    )
```

### Advanced Configuration: Model Fallbacks

```python
import litellm
from litellm import Router

# Configure fallback routing
model_list = [
    {
        "model_name": "primary",
        "litellm_params": {
            "model": "anthropic/claude-3-5-sonnet",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
        },
    },
    {
        "model_name": "fallback",
        "litellm_params": {
            "model": "gpt-4o",
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
    },
]

router = Router(
    model_list=model_list,
    fallbacks=[{"primary": ["fallback"]}],  # If primary fails, use fallback
    retry_after=5,  # Wait 5 seconds before retry
)

# Use with Agency Swarm
agent = Agent(
    name="RobustAgent",
    description="Agent with automatic fallbacks",
    llm=router,  # Pass router instead of model string
    tools=[...]
)
```

---

## 100+ Providers Supported

LiteLLM supports **100+ providers** with the same API. Just change the model string!

### Major Providers

#### 1. Anthropic (Claude)

```python
# Claude 3.5 Sonnet (best reasoning)
model="anthropic/claude-3-5-sonnet"

# Claude 3 Haiku (fast and cheap)
model="anthropic/claude-3-haiku"

# Claude 3 Opus (most capable)
model="anthropic/claude-3-opus"
```

**Pricing**:
- Haiku: $1/1M tokens
- Sonnet: $3/1M tokens
- Opus: $15/1M tokens

#### 2. Google (Gemini)

```python
# Gemini 2.0 Flash (cheapest, fastest)
model="gemini/gemini-2.0-flash"

# Gemini 1.5 Pro (balanced)
model="gemini/gemini-1.5-pro"

# Gemini 2.0 Pro (most capable)
model="gemini/gemini-2.0-pro"
```

**Pricing**:
- Flash: $0.075/1M tokens
- Pro 1.5: $3.50/1M tokens
- Pro 2.0: $7/1M tokens

#### 3. OpenAI (GPT)

```python
# GPT-4o (balanced, multimodal)
model="gpt-4o"

# GPT-4o-mini (cheap)
model="gpt-4o-mini"

# GPT-4 Turbo
model="gpt-4-turbo"
```

**Pricing**:
- GPT-4o-mini: $0.15/1M input, $0.60/1M output
- GPT-4o: $2.50/1M input, $10/1M output
- GPT-4 Turbo: $10/1M input, $30/1M output

#### 4. AWS Bedrock (Enterprise)

```python
# Claude on Bedrock (data stays in AWS)
model="bedrock/anthropic.claude-3-5-sonnet"

# Llama on Bedrock
model="bedrock/meta.llama3-70b"

# Mistral on Bedrock
model="bedrock/mistral.mistral-large"
```

**Benefits**:
- Data residency control
- AWS IAM integration
- VPC deployment
- Custom fine-tuning

#### 5. Azure OpenAI (Enterprise)

```python
# GPT-4 on Azure
model="azure/gpt-4"

# Set deployment name
litellm.set_azure_deployment("your-deployment-name")
```

**Benefits**:
- Microsoft enterprise SLA
- Data residency in Azure regions
- Compliance certifications
- Volume discounts

#### 6. Vertex AI (Google Cloud)

```python
# Gemini on Vertex AI
model="vertex_ai/gemini-2.0-flash"

# Claude on Vertex AI (via Model Garden)
model="vertex_ai/claude-3-5-sonnet"
```

**Benefits**:
- Google Cloud integration
- Data residency control
- Custom model deployment
- Enterprise support

#### 7. Open Source Models

```python
# Hugging Face (hosted inference)
model="huggingface/meta-llama/Llama-3-70b"

# Together AI (fast inference)
model="together_ai/meta-llama/Llama-3-70b-chat"

# Replicate (pay per use)
model="replicate/meta/llama-3-70b"

# Groq (blazing fast)
model="groq/llama-3-70b"
```

**Pricing** (approximate):
- Llama 3 70B: $0.50-$1/1M tokens
- Mixtral 8x7B: $0.20-$0.50/1M tokens
- Much cheaper than proprietary models!

#### 8. Specialized Providers

```python
# Cohere (search-optimized)
model="cohere/command-r-plus"

# AI21 (Jamba models)
model="ai21/jamba-instruct"

# Perplexity (with web search)
model="perplexity/llama-3-sonar-large"

# OpenRouter (aggregator)
model="openrouter/anthropic/claude-3-5-sonnet"
```

### Provider Comparison

| Provider | Best For | Pricing | Data Residency |
|----------|----------|---------|----------------|
| **Anthropic** | Complex reasoning | $$$ | US |
| **Google** | Cost optimization | $ | US/EU |
| **OpenAI** | General purpose | $$ | US |
| **AWS Bedrock** | Enterprise compliance | $$$ | Your AWS region |
| **Azure** | Microsoft ecosystem | $$$ | Global regions |
| **Vertex AI** | Google Cloud apps | $$ | Your GCP region |
| **Open Source** | Budget projects | $ | Self-hosted |

---

## Auto-Routing Strategies

LiteLLM provides multiple routing strategies to optimize **cost, latency, and reliability**.

### Strategy 1: Latency-Based Routing

Route requests to the **fastest available model** in real-time.

```python
from litellm import Router

# Configure multiple deployments
model_list = [
    {
        "model_name": "fast-model",
        "litellm_params": {
            "model": "gemini/gemini-2.0-flash",
            "api_key": os.getenv("GEMINI_API_KEY"),
        },
    },
    {
        "model_name": "fast-model",  # Same name = load balanced
        "litellm_params": {
            "model": "groq/llama-3-70b",
            "api_key": os.getenv("GROQ_API_KEY"),
        },
    },
]

router = Router(
    model_list=model_list,
    routing_strategy="latency-based-routing",  # Choose fastest
    num_retries=2,
)

# Automatically routes to fastest provider
response = router.completion(
    model="fast-model",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Use Case**: Real-time chatbots where response time matters more than model choice.

### Strategy 2: Usage-Based Routing

Distribute load evenly across providers to **maximize throughput and avoid rate limits**.

```python
from litellm import Router

model_list = [
    {"model_name": "gpt-4o", "litellm_params": {"model": "gpt-4o"}},
    {"model_name": "gpt-4o", "litellm_params": {"model": "azure/gpt-4o"}},
    {"model_name": "gpt-4o", "litellm_params": {"model": "bedrock/anthropic.claude-3-5-sonnet"}},
]

router = Router(
    model_list=model_list,
    routing_strategy="usage-based-routing",  # Round-robin
)

# Requests distributed evenly across all three
for i in range(100):
    response = router.completion(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Request {i}"}]
    )
```

**Use Case**: High-volume applications where you need to exceed single-provider rate limits.

### Strategy 3: Cost-Based Routing

Automatically route to the **cheapest model that meets quality requirements**.

```python
from litellm import Router

model_list = [
    {
        "model_name": "cheap",
        "litellm_params": {"model": "gemini/gemini-2.0-flash"},
        "cost_per_token": 0.000000075,  # $0.075/1M tokens
    },
    {
        "model_name": "mid",
        "litellm_params": {"model": "anthropic/claude-3-haiku"},
        "cost_per_token": 0.000001,  # $1/1M tokens
    },
    {
        "model_name": "premium",
        "litellm_params": {"model": "anthropic/claude-3-5-sonnet"},
        "cost_per_token": 0.000003,  # $3/1M tokens
    },
]

router = Router(
    model_list=model_list,
    routing_strategy="cost-based-routing",  # Choose cheapest
)

# Always uses cheapest model first
response = router.completion(
    model="cheap",
    messages=[{"role": "user", "content": "Extract data from invoice"}]
)
```

**Use Case**: Cost-sensitive applications where you want to minimize spend automatically.

### Strategy 4: Fallback Routing

Automatically **fallback to alternative models** if primary fails.

```python
from litellm import Router

model_list = [
    {
        "model_name": "primary",
        "litellm_params": {"model": "anthropic/claude-3-5-sonnet"},
    },
    {
        "model_name": "fallback-1",
        "litellm_params": {"model": "gpt-4o"},
    },
    {
        "model_name": "fallback-2",
        "litellm_params": {"model": "gemini/gemini-2.0-flash"},
    },
]

router = Router(
    model_list=model_list,
    fallbacks=[
        {"primary": ["fallback-1"]},
        {"fallback-1": ["fallback-2"]},
    ],
    retry_after=3,  # Wait 3 seconds between retries
)

# If Claude fails, tries GPT-4o, then Gemini
response = router.completion(
    model="primary",
    messages=[{"role": "user", "content": "Complex analysis"}]
)
```

**Use Case**: Mission-critical applications requiring maximum uptime.

### Strategy 5: Intelligent Routing (Custom Logic)

Implement **custom routing based on request content**:

```python
from litellm import completion

def intelligent_router(prompt: str):
    """Route based on prompt complexity."""

    # Simple keyword extraction
    if len(prompt.split()) < 50:
        return "gemini/gemini-2.0-flash"  # Simple = cheap

    # Check if requires reasoning
    reasoning_keywords = ["analyze", "compare", "strategy", "recommend"]
    if any(kw in prompt.lower() for kw in reasoning_keywords):
        return "anthropic/claude-3-5-sonnet"  # Complex = premium

    # Default to mid-tier
    return "anthropic/claude-3-haiku"

# Use intelligent routing
prompt = "Analyze market trends and recommend investment strategy"
model = intelligent_router(prompt)

response = completion(
    model=model,
    messages=[{"role": "user", "content": prompt}]
)
```

**Use Case**: Optimize costs by automatically using the right model for each task.

### Strategy 6: A/B Testing Models

Compare performance of different models on the same workload:

```python
import random
from litellm import completion

def ab_test_router():
    """Randomly assign requests to different models for testing."""
    models = [
        "gemini/gemini-2.0-flash",
        "anthropic/claude-3-haiku",
    ]
    return random.choice(models)

# Track performance metrics
metrics = {"gemini": [], "haiku": []}

for i in range(100):
    model = ab_test_router()

    start = time.time()
    response = completion(
        model=model,
        messages=[{"role": "user", "content": f"Test {i}"}]
    )
    latency = time.time() - start

    model_name = "gemini" if "gemini" in model else "haiku"
    metrics[model_name].append({
        "latency": latency,
        "cost": response._hidden_params.get("response_cost", 0),
        "quality": evaluate_quality(response),  # Custom function
    })

# Analyze results
for model_name, results in metrics.items():
    avg_latency = sum(r["latency"] for r in results) / len(results)
    avg_cost = sum(r["cost"] for r in results) / len(results)
    avg_quality = sum(r["quality"] for r in results) / len(results)

    print(f"{model_name}: {avg_latency:.2f}s, ${avg_cost:.6f}, quality={avg_quality:.2f}")
```

**Use Case**: Determine which model offers best cost/performance for your workload.

---

## Cost Tracking and Optimization

### Built-in Cost Tracking

LiteLLM automatically calculates costs for every request:

```python
import litellm

# Enable detailed logging
litellm.set_verbose = True

response = litellm.completion(
    model="gemini/gemini-2.0-flash",
    messages=[{"role": "user", "content": "Hello world"}]
)

# Access cost data
print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")
print(f"Total tokens: {response.usage.total_tokens}")
print(f"Cost: ${response._hidden_params.get('response_cost', 0):.6f}")
```

### Custom Cost Tracking

Implement comprehensive cost tracking across your agency:

```python
import json
from datetime import datetime
from typing import Dict, List
import litellm

class CostTracker:
    """Track costs across all agents and models."""

    def __init__(self, log_file: str = "costs.jsonl"):
        self.log_file = log_file

    def log_request(self, agent_name: str, model: str, response):
        """Log a single request."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "model": model,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "cost": response._hidden_params.get("response_cost", 0),
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(record) + "\n")

    def get_summary(self, days: int = 30) -> Dict:
        """Get cost summary."""
        records = []
        with open(self.log_file, "r") as f:
            for line in f:
                records.append(json.loads(line))

        # Filter by date
        cutoff = datetime.now().timestamp() - (days * 86400)
        recent = [r for r in records if datetime.fromisoformat(r["timestamp"]).timestamp() > cutoff]

        # Calculate totals
        total_cost = sum(r["cost"] for r in recent)
        total_tokens = sum(r["total_tokens"] for r in recent)

        # By agent
        by_agent = {}
        for r in recent:
            agent = r["agent"]
            if agent not in by_agent:
                by_agent[agent] = {"cost": 0, "tokens": 0, "requests": 0}
            by_agent[agent]["cost"] += r["cost"]
            by_agent[agent]["tokens"] += r["total_tokens"]
            by_agent[agent]["requests"] += 1

        # By model
        by_model = {}
        for r in recent:
            model = r["model"]
            if model not in by_model:
                by_model[model] = {"cost": 0, "tokens": 0, "requests": 0}
            by_model[model]["cost"] += r["cost"]
            by_model[model]["tokens"] += r["total_tokens"]
            by_model[model]["requests"] += 1

        return {
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "total_requests": len(recent),
            "by_agent": by_agent,
            "by_model": by_model,
            "avg_cost_per_request": total_cost / len(recent) if recent else 0,
        }

# Usage
tracker = CostTracker()

# Wrap agent calls
def tracked_completion(agent_name: str, model: str, messages: List):
    response = litellm.completion(model=model, messages=messages)
    tracker.log_request(agent_name, model, response)
    return response

# Get cost report
summary = tracker.get_summary(days=7)
print(f"Total cost (7 days): ${summary['total_cost']:.2f}")
print(f"Total tokens: {summary['total_tokens']:,}")
print(f"Avg cost/request: ${summary['avg_cost_per_request']:.6f}")

print("\nCost by agent:")
for agent, stats in summary["by_agent"].items():
    print(f"  {agent}: ${stats['cost']:.2f} ({stats['requests']} requests)")

print("\nCost by model:")
for model, stats in summary["by_model"].items():
    print(f"  {model}: ${stats['cost']:.2f} ({stats['requests']} requests)")
```

### Cost Optimization Strategies

#### 1. Token Reduction

Reduce token usage without sacrificing quality:

```python
# BEFORE: Verbose prompt
prompt = """
Please analyze the following document and extract all relevant information
including names, dates, amounts, and any other important details. Make sure
to provide a comprehensive summary of the key points and highlight anything
that seems unusual or requires attention.
"""

# AFTER: Concise prompt (50% fewer tokens)
prompt = """
Extract: names, dates, amounts. Summarize key points. Flag anomalies.
"""

# Both achieve similar results, but second costs 50% less
```

#### 2. Response Length Control

Limit output tokens to reduce costs:

```python
response = litellm.completion(
    model="gemini/gemini-2.0-flash",
    messages=[{"role": "user", "content": "Summarize this article"}],
    max_tokens=500,  # Limit output to 500 tokens
)

# Prevents runaway costs from unexpectedly long responses
```

#### 3. Caching Responses

Cache common queries to avoid redundant API calls:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_completion(prompt_hash: str, model: str):
    """Cache completions by prompt hash."""
    # This is a placeholder - in real implementation,
    # you'd need to pass the actual prompt
    pass

def get_completion(prompt: str, model: str):
    """Get completion with caching."""
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()

    # Check cache first
    cached = cached_completion(prompt_hash, model)
    if cached:
        return cached

    # If not cached, call API
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    # Update cache
    cached_completion(prompt_hash, model)  # Store in cache
    return response
```

#### 4. Batch Processing

Process multiple items in a single request:

```python
# BEFORE: Individual requests (expensive)
results = []
for item in items:  # 100 items
    response = litellm.completion(
        model="gemini/gemini-2.0-flash",
        messages=[{"role": "user", "content": f"Classify: {item}"}]
    )
    results.append(response)
# Cost: 100 requests × overhead

# AFTER: Batch request (efficient)
batch_prompt = "Classify each item:\n" + "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
response = litellm.completion(
    model="gemini/gemini-2.0-flash",
    messages=[{"role": "user", "content": batch_prompt}]
)
# Cost: 1 request, minimal overhead
```

#### 5. Smart Model Selection

Use cheap models for validation, premium for final output:

```python
def process_document(doc: str):
    """Two-stage processing with cost optimization."""

    # Stage 1: Quick validation with cheap model
    validation_result = litellm.completion(
        model="gemini/gemini-2.0-flash",  # $0.075/1M tokens
        messages=[{
            "role": "user",
            "content": f"Is this document valid? Answer yes/no: {doc[:500]}"
        }]
    )

    if "no" in validation_result.choices[0].message.content.lower():
        return {"error": "Invalid document"}

    # Stage 2: Full processing with premium model (only if valid)
    final_result = litellm.completion(
        model="anthropic/claude-3-5-sonnet",  # $3/1M tokens
        messages=[{
            "role": "user",
            "content": f"Analyze this document thoroughly: {doc}"
        }]
    )

    return final_result

# Saves money by filtering out invalid docs with cheap model
```

---

## Real-World Examples

### Example 1: Customer Support Agency

**Scenario**: Handle 10,000 customer emails/month with 3-tier agent system.

#### Agency Structure

```python
from agency_swarm import Agent, Agency

# Tier 1: Email Router (CHEAP - 70% of volume)
router = Agent(
    name="EmailRouter",
    description="Routes customer emails to appropriate department",
    instructions="""
    1. Read email subject and first paragraph
    2. Classify into: sales, support, billing, other
    3. Extract urgency level: low, medium, high
    4. Route to appropriate agent
    """,
    model="gemini/gemini-2.0-flash",  # $0.075/1M tokens
    tools=[GmailRead, ClassifyEmail]
)

# Tier 2: Support Agent (MID - 25% of volume)
support = Agent(
    name="SupportAgent",
    description="Handles common support issues",
    instructions="""
    1. Search knowledge base for solution
    2. If found: Draft helpful response
    3. If not found: Escalate to specialist
    4. Track resolution time
    """,
    model="anthropic/claude-3-haiku",  # $1/1M tokens
    tools=[GmailRead, EmailDraft, SearchKnowledgeBase]
)

# Tier 3: Specialist (PREMIUM - 5% of volume)
specialist = Agent(
    name="TechnicalSpecialist",
    description="Handles complex technical issues",
    instructions="""
    1. Analyze technical problem deeply
    2. Research solutions across docs/forums
    3. Provide detailed troubleshooting steps
    4. Create new KB article if needed
    """,
    model="anthropic/claude-3-5-sonnet",  # $3/1M tokens
    tools=[GmailRead, EmailDraft, WebSearch, CreateKBArticle]
)

# Create agency
agency = Agency(
    agents=[router, support, specialist],
    shared_instructions="Prioritize customer satisfaction and response quality"
)
```

#### Cost Analysis

| Agent | Volume | Avg Tokens | Model | Cost/Token | Total Cost |
|-------|--------|------------|-------|------------|------------|
| **Router** | 7,000 | 500 | Gemini Flash | $0.075/1M | **$0.26** |
| **Support** | 2,500 | 1,200 | Claude Haiku | $1/1M | **$3.00** |
| **Specialist** | 500 | 3,000 | Claude Sonnet | $3/1M | **$4.50** |
| **TOTAL** | 10,000 | - | Mixed | - | **$7.76** |

**Compare to single-model approaches**:
- All Claude Sonnet: 10,000 emails × 1,500 avg tokens × $3/1M = **$45**
- All GPT-4: 10,000 emails × 1,500 avg tokens × $30/1M = **$450**

**Savings**:
- vs Claude Sonnet: $37.24/month (83% reduction)
- vs GPT-4: $442.24/month (98% reduction)

### Example 2: Content Creation Pipeline

**Scenario**: Generate 100 blog articles/month with multi-agent system.

#### Agency Structure

```python
# Agent 1: Topic Researcher (CHEAP)
researcher = Agent(
    name="TopicResearcher",
    description="Researches trending topics and creates outlines",
    model="gemini/gemini-2.0-flash",
    tools=[WebSearch, TrendAnalysis]
)

# Agent 2: Draft Writer (MID)
writer = Agent(
    name="DraftWriter",
    description="Writes first draft from outline",
    model="anthropic/claude-3-haiku",
    tools=[WriteArticle, CheckGrammar]
)

# Agent 3: Editor (PREMIUM)
editor = Agent(
    name="SeniorEditor",
    description="Polishes draft into publication-ready article",
    model="anthropic/claude-3-5-sonnet",
    tools=[EditContent, OptimizeSEO, AddMetadata]
)
```

#### Cost Analysis

| Agent | Articles | Tokens/Article | Model | Cost/1M | Total Cost |
|-------|----------|----------------|-------|---------|------------|
| **Researcher** | 100 | 2,000 | Gemini Flash | $0.075 | **$0.015** |
| **Writer** | 100 | 5,000 | Haiku | $1.00 | **$0.50** |
| **Editor** | 100 | 6,000 | Sonnet | $3.00 | **$1.80** |
| **TOTAL** | 100 | 13,000/article | Mixed | - | **$2.315** |

**Compare to alternatives**:
- Single GPT-4 agent: 100 × 13,000 × $30/1M = **$39**
- Single Claude Sonnet: 100 × 13,000 × $3/1M = **$3.90**

**Savings**:
- vs GPT-4: $36.685 (94% reduction)
- vs Claude Sonnet: $1.585 (41% reduction)

**Quality benefit**: Premium editor ensures final quality while saving on research/drafting.

### Example 3: Data Processing Pipeline

**Scenario**: Process 1M documents/month for data extraction.

#### Agency Structure

```python
# Agent 1: Document Classifier (CHEAP - processes all)
classifier = Agent(
    name="DocumentClassifier",
    description="Classifies document type and quality",
    model="gemini/gemini-2.0-flash",
    tools=[ReadDocument, ClassifyType]
)

# Agent 2: Data Extractor (CHEAP - processes valid docs only)
extractor = Agent(
    name="DataExtractor",
    description="Extracts structured data from documents",
    model="gemini/gemini-2.0-flash",
    tools=[ExtractData, ValidateSchema]
)

# Agent 3: Quality Checker (MID - spot checks 10%)
checker = Agent(
    name="QualityChecker",
    description="Validates extraction accuracy",
    model="anthropic/claude-3-haiku",
    tools=[CompareData, FlagErrors]
)
```

#### Cost Analysis

| Agent | Documents | Tokens/Doc | Model | Cost/1M | Total Cost |
|-------|-----------|------------|-------|---------|------------|
| **Classifier** | 1,000,000 | 200 | Gemini Flash | $0.075 | **$15.00** |
| **Extractor** | 800,000 | 500 | Gemini Flash | $0.075 | **$30.00** |
| **Checker** | 100,000 | 800 | Haiku | $1.00 | **$80.00** |
| **TOTAL** | 1,000,000 | - | Mixed | - | **$125.00** |

**Compare to alternatives**:
- All GPT-4: 1M × 500 avg × $30/1M = **$15,000**
- All Claude Sonnet: 1M × 500 avg × $3/1M = **$1,500**

**Savings**:
- vs GPT-4: $14,875 (99.2% reduction)
- vs Claude Sonnet: $1,375 (91.7% reduction)

**ROI**: Quality checking catches 95%+ errors while only processing 10% with premium model.

---

## Why NOT to Use RouteLLM

**RouteLLM** is a model router that uses ML to decide which LLM to use for each request. While it sounds appealing, it's **NOT recommended** for Agency Swarm users.

### What is RouteLLM?

RouteLLM trains a classifier to predict whether a "strong" model (GPT-4) or "weak" model (GPT-3.5) is needed for a given prompt. It claims to:
- Maintain 95% quality of strong model
- Reduce costs by routing 80% of requests to weak model
- Work as a drop-in replacement

### Why It Adds Unnecessary Complexity

#### 1. Agency Swarm Already Optimizes

**Agency Swarm's multi-agent architecture IS the optimization**:

```python
# RouteLLM approach (single agent, auto-routing)
agent = Agent(
    name="GenericAgent",
    model="routellm/smart-router",  # Black box routing
    tools=[...all tools...]
)

# Agency Swarm approach (explicit agent assignment)
simple_agent = Agent(
    name="SimpleTaskAgent",
    model="gemini/gemini-2.0-flash",  # Explicit cheap model
    tools=[ExtractData, ValidateFormat]
)

complex_agent = Agent(
    name="ComplexTaskAgent",
    model="anthropic/claude-3-5-sonnet",  # Explicit premium model
    tools=[AnalyzeData, GenerateStrategy]
)
```

**Agency Swarm is better because**:
- Agent assignment is **explicit and deterministic** (no ML black box)
- You **control** which tasks get which models
- Agent specialization improves quality AND reduces costs
- No training data or classifier needed

#### 2. Loss of Control

RouteLLM makes routing decisions automatically:

```python
# RouteLLM: You don't know which model will be used
response = routellm.completion(prompt="Analyze this data...")
# Could use GPT-4 or GPT-3.5 - you won't know until after!

# Agency Swarm: You explicitly control model choice
response = analysis_agent.run()  # Always uses Claude Sonnet
```

**Problems with auto-routing**:
- Can't guarantee which model handles sensitive tasks
- Hard to debug when quality issues arise
- Compliance/audit trails are unclear

#### 3. Hidden Costs

RouteLLM requires:
- **Training data**: Need labeled examples of "simple" vs "complex"
- **Classifier inference**: Every request pays for routing decision
- **Monitoring**: Track routing accuracy and quality
- **Maintenance**: Retrain as your workload changes

**Agency Swarm approach**: Zero overhead - agent assignment is configuration.

#### 4. Worse Quality Guarantees

RouteLLM claims "95% quality of strong model" but:
- 95% is an average - some tasks will be much worse
- No control over which 5% of tasks get degraded
- Mission-critical tasks might be routed to weak model

**Agency Swarm approach**: Guarantee quality by assigning premium model to critical agents.

#### 5. Limited Model Selection

RouteLLM typically supports only 2 models (strong/weak):

```python
# RouteLLM: Binary choice
routellm.configure(
    strong_model="gpt-4",
    weak_model="gpt-3.5-turbo"
)
```

**Agency Swarm**: Use **any combination** of models across agents:

```python
# 5 agents, 5 different models optimized for each use case
agents = [
    Agent(name="A1", model="gemini/gemini-2.0-flash"),
    Agent(name="A2", model="anthropic/claude-3-haiku"),
    Agent(name="A3", model="anthropic/claude-3-5-sonnet"),
    Agent(name="A4", model="gpt-4o"),
    Agent(name="A5", model="groq/llama-3-70b"),
]
```

#### 6. Debuggability

When something goes wrong:

**With RouteLLM**:
- "Why did quality drop?" → Check routing decisions
- "Why is this slow?" → Check if routed to slow model
- "Why did cost spike?" → Check routing accuracy drift
- Need separate monitoring for router itself

**With Agency Swarm**:
- "Why did quality drop?" → Check specific agent's prompt/tools
- "Why is this slow?" → Check specific agent's model
- "Why did cost spike?" → Check which agents are being called
- Standard agent monitoring is sufficient

### When RouteLLM Might Make Sense

RouteLLM only makes sense if:
1. You have a **single-agent system** (not using Agency Swarm)
2. Your workload has **highly variable complexity** that's hard to predict
3. You have **lots of training data** for the classifier
4. You're willing to accept **95% quality vs 100%**

**But**: If you're already using Agency Swarm, you get better results with explicit agent assignment.

### The Right Way: Explicit Agent Assignment

```python
from agency_swarm import Agency, Agent

# Define agents with appropriate models
data_entry = Agent(
    name="DataEntry",
    description="Extract structured data",
    model="gemini/gemini-2.0-flash",  # Cheap, perfect for this task
    tools=[ExtractData]
)

analyst = Agent(
    name="Analyst",
    description="Complex data analysis",
    model="anthropic/claude-3-5-sonnet",  # Premium, needed for quality
    tools=[AnalyzeData, GenerateInsights]
)

coordinator = Agent(
    name="Coordinator",
    description="Routes tasks to appropriate agent",
    model="anthropic/claude-3-haiku",  # Mid-tier for routing logic
    tools=[AssignTask]
)

agency = Agency(
    agents=[data_entry, analyst, coordinator],
    shared_instructions="Optimize for quality and cost"
)

# Coordinator explicitly decides which agent to use
# Much clearer than RouteLLM's black box
```

**Benefits over RouteLLM**:
- Explicit control over model assignment
- Better quality guarantees
- Easier to debug and optimize
- No training data needed
- No classifier overhead
- Works with any LiteLLM-supported model

---

## Best Practices

### 1. Start with Cost Analysis

Before optimizing, understand your current costs:

```python
# Audit current usage
total_tokens = 50_000_000  # 50M tokens/month
current_model = "gpt-4"
cost_per_token = 0.00003  # $30/1M tokens

current_cost = total_tokens * cost_per_token
print(f"Current monthly cost: ${current_cost:,.2f}")

# Calculate optimized cost
cheap_tokens = total_tokens * 0.80  # 80% to cheap model
mid_tokens = total_tokens * 0.15    # 15% to mid model
premium_tokens = total_tokens * 0.05  # 5% to premium model

optimized_cost = (
    cheap_tokens * 0.000000075 +  # Gemini Flash
    mid_tokens * 0.000001 +         # Claude Haiku
    premium_tokens * 0.000003       # Claude Sonnet
)

print(f"Optimized monthly cost: ${optimized_cost:,.2f}")
print(f"Savings: ${current_cost - optimized_cost:,.2f} ({((current_cost - optimized_cost) / current_cost * 100):.1f}%)")
```

### 2. Categorize Your Agents

Classify each agent by complexity requirements:

```python
# Agent complexity matrix
agents = {
    # CHEAP tier (simple, structured tasks)
    "data_extractor": {
        "complexity": "low",
        "model": "gemini/gemini-2.0-flash",
        "reasoning": "Extraction follows clear rules",
    },
    "format_validator": {
        "complexity": "low",
        "model": "gemini/gemini-2.0-flash",
        "reasoning": "Schema validation is deterministic",
    },

    # MID tier (moderate reasoning)
    "support_agent": {
        "complexity": "medium",
        "model": "anthropic/claude-3-haiku",
        "reasoning": "Needs empathy and problem-solving",
    },
    "content_editor": {
        "complexity": "medium",
        "model": "anthropic/claude-3-haiku",
        "reasoning": "Improves writing quality",
    },

    # PREMIUM tier (complex reasoning)
    "strategist": {
        "complexity": "high",
        "model": "anthropic/claude-3-5-sonnet",
        "reasoning": "Multi-step strategic analysis",
    },
    "researcher": {
        "complexity": "high",
        "model": "anthropic/claude-3-5-sonnet",
        "reasoning": "Synthesizes complex information",
    },
}
```

### 3. Implement Fallback Logic

Always have fallback models for reliability:

```python
from litellm import Router

def create_robust_router(primary_model: str):
    """Create router with fallbacks."""
    return Router(
        model_list=[
            {
                "model_name": "primary",
                "litellm_params": {"model": primary_model},
            },
            {
                "model_name": "fallback-1",
                "litellm_params": {"model": "gpt-4o"},
            },
            {
                "model_name": "fallback-2",
                "litellm_params": {"model": "gemini/gemini-2.0-flash"},
            },
        ],
        fallbacks=[
            {"primary": ["fallback-1"]},
            {"fallback-1": ["fallback-2"]},
        ],
        retry_after=3,
    )

# Use with agents
strategist = Agent(
    name="Strategist",
    llm=create_robust_router("anthropic/claude-3-5-sonnet"),
    tools=[...]
)
```

### 4. Monitor Quality Metrics

Track quality alongside costs:

```python
class QualityTracker:
    """Track quality metrics per agent."""

    def __init__(self):
        self.metrics = []

    def log_result(self, agent: str, model: str, quality_score: float, cost: float):
        """Log a single result."""
        self.metrics.append({
            "agent": agent,
            "model": model,
            "quality": quality_score,
            "cost": cost,
        })

    def get_efficiency(self, agent: str):
        """Calculate quality per dollar."""
        agent_metrics = [m for m in self.metrics if m["agent"] == agent]
        if not agent_metrics:
            return 0

        avg_quality = sum(m["quality"] for m in agent_metrics) / len(agent_metrics)
        avg_cost = sum(m["cost"] for m in agent_metrics) / len(agent_metrics)

        return avg_quality / avg_cost if avg_cost > 0 else 0

# Usage
tracker = QualityTracker()

# After each agent run
result = agent.run()
quality = evaluate_quality(result)  # Your quality function
tracker.log_result(agent.name, agent.model, quality, result.cost)

# Find most efficient agents
for agent_name in set(m["agent"] for m in tracker.metrics):
    efficiency = tracker.get_efficiency(agent_name)
    print(f"{agent_name}: {efficiency:.2f} quality per dollar")
```

### 5. Use Environment-Based Configuration

Make it easy to switch models:

```python
# config.py
import os

MODEL_CONFIG = {
    "development": {
        "cheap": "gemini/gemini-2.0-flash",
        "mid": "anthropic/claude-3-haiku",
        "premium": "anthropic/claude-3-5-sonnet",
    },
    "production": {
        "cheap": "gemini/gemini-2.0-flash",
        "mid": "anthropic/claude-3-haiku",
        "premium": "anthropic/claude-3-5-sonnet",
    },
    "testing": {
        # Use cheap models for all tiers in testing
        "cheap": "gemini/gemini-2.0-flash",
        "mid": "gemini/gemini-2.0-flash",
        "premium": "gemini/gemini-2.0-flash",
    },
}

def get_model(tier: str) -> str:
    """Get model for tier based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    return MODEL_CONFIG[env][tier]

# Usage
data_agent = Agent(
    name="DataAgent",
    model=get_model("cheap"),  # Uses correct model for environment
    tools=[...]
)
```

### 6. Optimize Prompts

Better prompts = fewer tokens = lower costs:

```python
# BAD: Verbose, wasteful
bad_prompt = """
I need you to carefully analyze the following document and extract all of the
important information that you can find. Please make sure to include names,
dates, amounts, and any other relevant details that might be useful. After
extracting the data, please format it nicely in JSON format so that it can be
easily processed by downstream systems.
"""

# GOOD: Concise, specific
good_prompt = """
Extract from document:
- Names, dates, amounts
- Return JSON format
- Include all fields from schema
"""

# Savings: ~70% fewer tokens, same result
```

### 7. Batch When Possible

Process multiple items together:

```python
# BAD: Individual processing
for email in emails:  # 100 emails
    summary = agent.run(email)  # 100 API calls

# GOOD: Batch processing
batch_prompt = f"Summarize each email:\n" + "\n---\n".join(emails)
summaries = agent.run(batch_prompt)  # 1 API call

# Savings: Eliminate per-request overhead
```

### 8. Set Token Limits

Prevent runaway costs:

```python
agent = Agent(
    name="DataAgent",
    model="gemini/gemini-2.0-flash",
    max_tokens=500,  # Limit output length
    tools=[...]
)

# Or per-request
response = litellm.completion(
    model="gemini/gemini-2.0-flash",
    messages=[...],
    max_tokens=500,
)
```

### 9. A/B Test Model Changes

Before switching models, validate quality:

```python
def ab_test_models(prompts: List[str], model_a: str, model_b: str):
    """Compare two models on same prompts."""
    results = {"model_a": [], "model_b": []}

    for prompt in prompts:
        # Test model A
        response_a = litellm.completion(model=model_a, messages=[{"role": "user", "content": prompt}])
        results["model_a"].append({
            "response": response_a.choices[0].message.content,
            "cost": response_a._hidden_params.get("response_cost", 0),
            "tokens": response_a.usage.total_tokens,
        })

        # Test model B
        response_b = litellm.completion(model=model_b, messages=[{"role": "user", "content": prompt}])
        results["model_b"].append({
            "response": response_b.choices[0].message.content,
            "cost": response_b._hidden_params.get("response_cost", 0),
            "tokens": response_b.usage.total_tokens,
        })

    # Compare
    print("Model A:")
    print(f"  Avg cost: ${sum(r['cost'] for r in results['model_a']) / len(prompts):.6f}")
    print(f"  Avg tokens: {sum(r['tokens'] for r in results['model_a']) / len(prompts):.0f}")

    print("Model B:")
    print(f"  Avg cost: ${sum(r['cost'] for r in results['model_b']) / len(prompts):.6f}")
    print(f"  Avg tokens: {sum(r['tokens'] for r in results['model_b']) / len(prompts):.0f}")

    return results

# Test switching from Haiku to Gemini Flash
test_prompts = [
    "Summarize this article...",
    "Extract data from invoice...",
    # ... more test cases
]

results = ab_test_models(
    test_prompts,
    model_a="anthropic/claude-3-haiku",
    model_b="gemini/gemini-2.0-flash"
)
```

### 10. Document Model Choices

Keep a record of why each agent uses its model:

```python
# agents/config.yaml
agents:
  data_extractor:
    model: "gemini/gemini-2.0-flash"
    reasoning: |
      Extraction is deterministic and follows clear schema.
      Tested on 1,000 samples with 99.5% accuracy.
      Cost: $0.075/1M tokens vs $1/1M for Haiku (13x cheaper).

  support_agent:
    model: "anthropic/claude-3-haiku"
    reasoning: |
      Requires empathy and nuanced problem-solving.
      Gemini Flash tested at 85% quality vs Haiku at 95%.
      Cost difference ($1 vs $0.075) justified by quality gain.

  strategist:
    model: "anthropic/claude-3-5-sonnet"
    reasoning: |
      Complex multi-step reasoning required.
      Tested: Sonnet 98% vs Haiku 75% on strategic tasks.
      Premium cost justified by critical nature of output.
```

---

## Summary

### Key Takeaways

1. **LiteLLM is built into Agency Swarm** - No additional setup required
2. **90% cost savings achievable** through strategic model assignment
3. **Three-tier strategy works**:
   - 80% cheap models for simple tasks
   - 15% mid-tier for moderate complexity
   - 5% premium for critical reasoning
4. **100+ providers supported** - Use any model from any provider
5. **Auto-routing available** but explicit assignment is better for Agency Swarm
6. **RouteLLM adds complexity** - Agency Swarm's multi-agent design already optimizes
7. **Track costs and quality** - Optimize continuously based on data

### Next Steps

1. **Audit your current costs** - Understand baseline
2. **Categorize your agents** - Assign to cheap/mid/premium tiers
3. **Update model assignments** - Switch to appropriate models
4. **Implement cost tracking** - Monitor spend per agent
5. **A/B test changes** - Validate quality before full rollout
6. **Optimize continuously** - Review metrics monthly

### Quick Reference: Model Recommendations

| Task Type | Recommended Model | Cost/1M | Use Case |
|-----------|------------------|---------|----------|
| **Data extraction** | Gemini Flash | $0.075 | Structured output |
| **Classification** | Gemini Flash | $0.075 | Categorization |
| **Simple QA** | Gemini Flash | $0.075 | FAQ responses |
| **Content editing** | Claude Haiku | $1.00 | Writing improvement |
| **Customer support** | Claude Haiku | $1.00 | Empathetic responses |
| **Code review** | Claude Haiku | $1.00 | Bug detection |
| **Strategy** | Claude Sonnet | $3.00 | Complex planning |
| **Research** | Claude Sonnet | $3.00 | Deep analysis |
| **Creative writing** | Claude Sonnet | $3.00 | High-quality content |

---

## Additional Resources

- **LiteLLM Documentation**: https://docs.litellm.ai
- **Agency Swarm Documentation**: https://github.com/VRSEN/agency-swarm
- **Model Pricing**: https://litellm.vercel.app/docs/proxy/cost_tracking
- **Provider Docs**: https://docs.litellm.ai/docs/providers

---

**Ready to save 90% on LLM costs?** Start by categorizing your agents into the three tiers and update their model assignments. Track costs for one week to validate savings, then optimize further based on data.
