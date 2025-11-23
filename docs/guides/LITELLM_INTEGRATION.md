# LiteLLM Integration Guide

## Overview

AgentSwarm Tools Framework integrates **LiteLLM** for unified access to 100+ LLM providers with automatic cost optimization, fallback handling, and comprehensive cost tracking.

### Key Benefits

- **90% Cost Savings**: Intelligent model selection and fallback to cheaper alternatives
- **Multi-Provider Support**: OpenAI, Anthropic, Google, Cohere, Replicate, Together AI, and 100+ more
- **Automatic Fallback**: Never fail due to rate limits or provider outages
- **Cost Tracking**: Track every request's cost, tokens, and latency
- **Unified Interface**: One API for all providers

---

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Quick Start](#quick-start)
4. [Usage Examples](#usage-examples)
5. [Cost Optimization](#cost-optimization)
6. [Supported Providers](#supported-providers)
7. [Tool Integration](#tool-integration)
8. [Cost Analytics](#cost-analytics)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Installation

### 1. Install LiteLLM

LiteLLM is already included in the requirements:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install litellm>=1.30.0
```

### 2. Set Up API Keys

Add your API keys to `.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google AI
GOOGLE_API_KEY=AI...

# Cohere
COHERE_API_KEY=...
```

### 3. Configure LiteLLM

Update `.env` with LiteLLM settings:

```bash
# Enable automatic fallback
LITELLM_FALLBACK_ENABLED=true

# Enable cost tracking
LITELLM_COST_TRACKING=true

# Default models
LITELLM_DEFAULT_TEXT_MODEL=gpt-3.5-turbo
LITELLM_DEFAULT_IMAGE_MODEL=dall-e-3
LITELLM_DEFAULT_VISION_MODEL=gpt-4-turbo
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LITELLM_FALLBACK_ENABLED` | `true` | Enable automatic provider fallback |
| `LITELLM_COST_TRACKING` | `true` | Track costs for analytics |
| `LITELLM_VERBOSE` | `false` | Enable debug logging |
| `LITELLM_DEFAULT_TEXT_MODEL` | `gpt-3.5-turbo` | Default model for text generation |
| `LITELLM_DEFAULT_IMAGE_MODEL` | `dall-e-3` | Default model for image generation |
| `LITELLM_DEFAULT_VISION_MODEL` | `gpt-4-turbo` | Default model for vision tasks |

### Provider API Keys

Each provider requires its own API key:

- **OpenAI**: `OPENAI_API_KEY`
- **Anthropic**: `ANTHROPIC_API_KEY`
- **Google**: `GOOGLE_API_KEY`
- **Cohere**: `COHERE_API_KEY`

See [LiteLLM Provider Docs](https://docs.litellm.ai/docs/providers) for complete list.

---

## Quick Start

### Basic Chat Completion

```python
from shared.llm_client import get_llm_client

# Get client
client = get_llm_client()

# Simple chat
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-3.5-turbo"
)

print(response.content)
print(f"Cost: ${response.cost:.6f}")
print(f"Model: {response.model}")
```

### With Automatic Fallback

```python
# Primary model with fallback options
response = client.chat_completion(
    messages=[{"role": "user", "content": "Write a poem"}],
    model="gpt-4",
    fallback_models=["claude-3-sonnet-20240229", "gpt-3.5-turbo"]
)

print(response.content)
print(f"Used: {response.model} ({response.provider})")
print(f"Fallback used: {response.metadata['fallback_used']}")
```

### Image Generation

```python
# Generate image with DALL-E 3
response = client.generate_image(
    prompt="a futuristic city at sunset",
    model="dall-e-3",
    size="1024x1024",
    quality="standard"
)

print(f"Image URL: {response.content}")
print(f"Cost: ${response.cost:.6f}")
```

### Vision Analysis

```python
# Analyze image with GPT-4 Vision
response = client.vision_completion(
    messages=[{"role": "user", "content": "Describe this image"}],
    image_urls=["https://example.com/image.jpg"],
    model="gpt-4-turbo",
    fallback_models=["claude-3-opus-20240229"]
)

print(response.content)
print(f"Tokens: {response.usage['total_tokens']}")
```

---

## Usage Examples

### 1. Cost-Optimized Text Generation

```python
from shared.llm_client import get_llm_client

client = get_llm_client()

# Use cheapest model first, fall back to better models if needed
response = client.chat_completion(
    messages=[{"role": "user", "content": "Summarize this article..."}],
    model="gpt-3.5-turbo",  # $0.0005/1K tokens
    fallback_models=[
        "claude-3-haiku-20240307",  # $0.00025/1K tokens (cheaper!)
        "gemini-pro"  # $0.0005/1K tokens
    ],
    temperature=0.7,
    max_tokens=500
)

print(f"Response: {response.content}")
print(f"Cost: ${response.cost:.6f}")
print(f"Provider: {response.provider}")
```

### 2. Streaming Responses

```python
# Stream for real-time output
stream = client.chat_completion(
    messages=[{"role": "user", "content": "Write a story..."}],
    model="gpt-3.5-turbo",
    stream=True
)

for chunk in stream:
    print(chunk, end="", flush=True)
```

### 3. Multi-Model Comparison

```python
models = ["gpt-3.5-turbo", "claude-3-haiku-20240307", "gemini-pro"]
prompt = "Explain quantum computing in simple terms"

for model in models:
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model
    )
    print(f"\n{model} (${response.cost:.6f}):")
    print(response.content[:200] + "...")
```

---

## Cost Optimization

### Cost Comparison (per 1M tokens)

| Model | Provider | Input | Output | Best For |
|-------|----------|-------|--------|----------|
| `claude-3-haiku` | Anthropic | $0.25 | $1.25 | Fast, cheap tasks |
| `gpt-3.5-turbo` | OpenAI | $0.50 | $1.50 | General purpose |
| `gemini-pro` | Google | $0.50 | $1.50 | Long context |
| `claude-3-sonnet` | Anthropic | $3.00 | $15.00 | Quality balance |
| `gpt-4-turbo` | OpenAI | $10.00 | $30.00 | Complex reasoning |
| `claude-3-opus` | Anthropic | $15.00 | $75.00 | Highest quality |

### Optimization Strategies

#### 1. Tiered Fallback Strategy

```python
# Start with cheapest, fall back to better quality
response = client.chat_completion(
    messages=messages,
    model="claude-3-haiku-20240307",  # Cheapest
    fallback_models=[
        "gpt-3.5-turbo",  # Medium
        "claude-3-sonnet-20240229",  # Better
        "gpt-4-turbo"  # Best (last resort)
    ]
)
```

#### 2. Task-Specific Model Selection

```python
# Simple tasks: use cheap models
summary = client.chat_completion(
    messages=[{"role": "user", "content": "Summarize: ..."}],
    model="gpt-3.5-turbo"
)

# Complex tasks: use better models
analysis = client.chat_completion(
    messages=[{"role": "user", "content": "Analyze this data..."}],
    model="gpt-4-turbo"
)
```

#### 3. Cost Budgeting

```python
# Track costs in real-time
client = get_llm_client()

for task in tasks:
    response = client.chat_completion(...)

    # Check if over budget
    if client.get_total_cost() > 1.0:  # $1 budget
        print("Budget exceeded!")
        break
```

### Cost Savings Examples

**Example 1: Text Summarization**
- Before: GPT-4 ($30/1M output tokens)
- After: Claude Haiku ($1.25/1M output tokens)
- **Savings: 95.8%**

**Example 2: Image Generation**
- Before: DALL-E 3 HD ($0.08/image)
- After: DALL-E 3 Standard ($0.04/image)
- **Savings: 50%**

**Example 3: Vision Tasks**
- Before: GPT-4 Vision only
- After: GPT-4 Vision → Claude 3 Opus fallback
- **Availability: 99.9%** (vs 95% single provider)

---

## Supported Providers

### Chat Completion Models

#### OpenAI
- `gpt-4-turbo` - Latest GPT-4 with vision
- `gpt-4` - Standard GPT-4
- `gpt-3.5-turbo` - Fast and cheap

#### Anthropic
- `claude-3-opus-20240229` - Highest intelligence
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-haiku-20240307` - Fastest, cheapest

#### Google
- `gemini-pro` - Multimodal model
- `gemini-pro-vision` - Vision tasks

#### Cohere
- `command` - Command model
- `command-light` - Lighter version

### Image Generation Models

- `dall-e-3` (OpenAI) - Highest quality
- `dall-e-2` (OpenAI) - Cheaper alternative
- `stable-diffusion-xl` (Stability AI) - Open source

### Vision Models

- `gpt-4-turbo` (OpenAI)
- `claude-3-opus-20240229` (Anthropic)
- `claude-3-sonnet-20240229` (Anthropic)
- `gemini-pro-vision` (Google)

---

## Tool Integration

### Integrating LiteLLM into Tools

#### Example: Image Generation Tool

```python
from shared.llm_client import get_llm_client, LLMResponse
from shared.analytics import record_event, AnalyticsEvent, EventType

class ImageGeneration(BaseTool):
    """Generate images using LiteLLM."""

    prompt: str = Field(..., description="Image description")
    model: Optional[str] = Field(None, description="Model to use")
    fallback_models: Optional[list] = Field(None, description="Fallback models")

    def _process(self):
        # Get client
        client = get_llm_client()

        # Generate image
        response: LLMResponse = client.generate_image(
            prompt=self.prompt,
            model=self.model or "dall-e-3",
            fallback_models=self.fallback_models or []
        )

        # Record cost
        record_event(AnalyticsEvent(
            event_type=EventType.LLM_COST,
            tool_name=self.tool_name,
            metadata={
                "model": response.model,
                "provider": response.provider,
                "cost": response.cost,
                "task_type": "image_generation"
            }
        ))

        return {
            "image_url": response.content,
            "model": response.model,
            "cost": response.cost
        }
```

#### Example: Vision Analysis Tool

```python
class UnderstandImages(BaseTool):
    """Analyze images using vision models."""

    media_url: str = Field(..., description="Image URL")
    instruction: str = Field(..., description="Analysis instruction")

    def _process(self):
        client = get_llm_client()

        # Analyze image
        response = client.vision_completion(
            messages=[{"role": "user", "content": self.instruction}],
            image_urls=[self.media_url],
            model="gpt-4-turbo",
            fallback_models=["claude-3-opus-20240229"]
        )

        # Record cost
        record_event(AnalyticsEvent(
            event_type=EventType.LLM_COST,
            tool_name=self.tool_name,
            metadata={
                "model": response.model,
                "cost": response.cost,
                "total_tokens": response.usage.get("total_tokens", 0)
            }
        ))

        return {
            "analysis": response.content,
            "cost": response.cost,
            "tokens": response.usage.get("total_tokens", 0)
        }
```

---

## Cost Analytics

### Viewing Cost Metrics

```python
from shared.analytics import get_llm_costs, print_llm_costs

# Get cost data for last 7 days
costs = get_llm_costs(days=7)

print(f"Total Cost: ${costs['total_cost']:.6f}")
print(f"Total Tokens: {costs['total_tokens']:,}")
print(f"Avg Cost per Call: ${costs['avg_cost_per_call']:.6f}")

# By provider
for provider, cost in costs['cost_by_provider'].items():
    print(f"  {provider}: ${cost:.6f}")

# By model
for model, cost in costs['cost_by_model'].items():
    calls = costs['calls_by_model'][model]
    print(f"  {model}: ${cost:.6f} ({calls} calls)")
```

### Pretty Print Cost Report

```python
from shared.analytics import print_llm_costs

# Print formatted cost report
print_llm_costs(days=30)
```

Output:
```
=== LiteLLM Cost Metrics (last 30 days) ===
Total Cost: $12.456789
Total Tokens: 1,234,567
Average Cost per Call: $0.001234

Cost by Provider:
  openai: $8.234567
  anthropic: $3.456789
  google: $0.765433

Cost by Model:
  gpt-4-turbo: $5.123456 (120 calls, $0.042695/call)
  gpt-3.5-turbo: $3.111111 (850 calls, $0.003660/call)
  claude-3-sonnet-20240229: $2.456789 (200 calls, $0.012284/call)
```

### Export Cost Records

```python
from shared.llm_client import get_llm_client

client = get_llm_client()

# Export to JSON for analysis
client.export_cost_records("costs_2024_01.json")
```

---

## Best Practices

### 1. Always Use Fallback Models

```python
# Good: Has fallback
response = client.chat_completion(
    messages=messages,
    model="gpt-4-turbo",
    fallback_models=["claude-3-sonnet", "gpt-3.5-turbo"]
)

# Bad: No fallback (single point of failure)
response = client.chat_completion(
    messages=messages,
    model="gpt-4-turbo"
)
```

### 2. Choose Right Model for Task

```python
# Simple extraction -> cheap model
data = client.chat_completion(
    messages=[{"role": "user", "content": "Extract email from: ..."}],
    model="gpt-3.5-turbo"  # Cheap, fast
)

# Complex reasoning -> better model
analysis = client.chat_completion(
    messages=[{"role": "user", "content": "Analyze business strategy..."}],
    model="gpt-4-turbo"  # Better quality
)
```

### 3. Monitor Costs Regularly

```python
# Check costs periodically
from shared.analytics import get_llm_costs

costs = get_llm_costs(days=1)
if costs['total_cost'] > 100:
    # Alert or throttle
    send_alert(f"High LLM costs: ${costs['total_cost']:.2f}")
```

### 4. Use Streaming for Long Outputs

```python
# Streaming reduces perceived latency
stream = client.chat_completion(
    messages=messages,
    model="gpt-4-turbo",
    stream=True
)

for chunk in stream:
    display_to_user(chunk)
```

### 5. Set Appropriate max_tokens

```python
# Don't pay for unused tokens
response = client.chat_completion(
    messages=messages,
    model="gpt-4-turbo",
    max_tokens=500  # Limit output length
)
```

---

## Troubleshooting

### Issue: LiteLLM Not Available

**Error:**
```
ImportError: LiteLLM is not installed. Install with: pip install litellm>=1.30.0
```

**Solution:**
```bash
pip install litellm>=1.30.0
```

### Issue: Authentication Failed

**Error:**
```
AuthenticationError: Authentication failed for openai
```

**Solution:**
1. Check API key is set: `echo $OPENAI_API_KEY`
2. Verify key is valid in provider dashboard
3. Check key has proper permissions

### Issue: Rate Limit Exceeded

**Error:**
```
RateLimitError: Rate limit exceeded for gpt-4-turbo
```

**Solution:**
1. Enable fallback: `LITELLM_FALLBACK_ENABLED=true`
2. Add fallback models:
   ```python
   response = client.chat_completion(
       model="gpt-4-turbo",
       fallback_models=["claude-3-sonnet", "gpt-3.5-turbo"]
   )
   ```

### Issue: High Costs

**Symptoms:**
- Unexpected billing
- Costs higher than expected

**Solutions:**
1. Check cost analytics:
   ```python
   from shared.analytics import print_llm_costs
   print_llm_costs(days=7)
   ```

2. Use cheaper models:
   ```python
   # Before: gpt-4-turbo ($10/1M input)
   # After: gpt-3.5-turbo ($0.50/1M input)
   ```

3. Limit max_tokens:
   ```python
   response = client.chat_completion(
       messages=messages,
       max_tokens=500  # Prevent runaway costs
   )
   ```

4. Monitor in real-time:
   ```python
   client = get_llm_client()
   if client.get_total_cost() > budget:
       raise Exception("Budget exceeded!")
   ```

---

## Advanced Usage

### Custom Model Configurations

```python
from shared.llm_client import LLMClient, ModelConfig, TaskType

# Define custom model
custom_configs = {
    "my-custom-model": ModelConfig(
        name="my-custom-model",
        provider="custom",
        task_type=TaskType.CHAT_COMPLETION,
        cost_per_1k_input_tokens=0.001,
        cost_per_1k_output_tokens=0.002,
        max_tokens=8192
    )
}

# Use custom config
client = LLMClient(model_configs=custom_configs)
```

### Disable Fallback for Specific Calls

```python
# Create client without fallback
client = LLMClient(enable_fallback=False)

# Or override per call
response = client.chat_completion(
    messages=messages,
    model="gpt-4-turbo"
    # No fallback_models specified
)
```

### Disable Cost Tracking

```python
# For high-volume, low-overhead scenarios
client = LLMClient(enable_cost_tracking=False)
```

---

## Migration Guide

### Before: Direct OpenAI Calls

```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=messages
)

content = response.choices[0].message.content
```

### After: LiteLLM Integration

```python
from shared.llm_client import get_llm_client

client = get_llm_client()

response = client.chat_completion(
    messages=messages,
    model="gpt-4",
    fallback_models=["claude-3-sonnet", "gpt-3.5-turbo"]
)

content = response.content
cost = response.cost  # Bonus: automatic cost tracking!
```

**Benefits:**
- ✅ Automatic fallback
- ✅ Cost tracking
- ✅ Multi-provider support
- ✅ Unified interface

---

## References

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- [AgentSwarm Tools Documentation](../README.md)
- [Cost Optimization Guide](./COST_OPTIMIZATION.md)

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [LiteLLM Docs](https://docs.litellm.ai/)
3. Open an issue on GitHub
4. Contact the development team

---

**Last Updated:** 2025-01-23
