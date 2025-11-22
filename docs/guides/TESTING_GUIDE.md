# AgentSwarm Tools - Comprehensive Testing Guide

**Complete guide for testing all 101 tools with both mock and live API keys**

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Modes](#testing-modes)
3. [Quick Start](#quick-start)
4. [Tool-by-Tool Testing](#tool-by-tool-testing)
5. [API Key Setup](#api-key-setup)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### Test Status

- **Total Tools**: 101 production-ready tools
- **Tools with Test Blocks**: 83/101 (82%)
- **Tools Missing Test Blocks**: 18 (14 visualization + 4 web_content)
- **Integration Tests**: 18 categories covered
- **Test Coverage**: 23% code coverage (target: 80%)

### Testing Philosophy

Every tool supports **two testing modes**:

1. **Mock Mode**: Tests without real API keys (development/CI)
2. **Live Mode**: Tests with real API keys (verification/integration)

---

## Testing Modes

### Mock Mode (No API Keys Required)

Mock mode allows testing tools without any API credentials. Perfect for:
- Development and debugging
- CI/CD pipelines
- Quick validation
- First-time setup

**Enable Mock Mode**:
```bash
export USE_MOCK_APIS=true
```

**Run a tool in mock mode**:
```bash
USE_MOCK_APIS=true python3 -m tools.search.web_search.web_search
```

### Live Mode (API Keys Required)

Live mode tests tools against real APIs. Use for:
- Production validation
- Integration testing
- Performance benchmarking
- Feature verification

**Enable Live Mode**:
```bash
export USE_MOCK_APIS=false
# OR unset the variable
unset USE_MOCK_APIS
```

**Run a tool in live mode**:
```bash
# Set required API keys first
export SERPAPI_KEY=your_key_here
python3 -m tools.search.web_search.web_search
```

---

## Quick Start

### 1. Test All Tools (Mock Mode)

```bash
# Run all integration tests with mock data
USE_MOCK_APIS=true pytest tests/integration/ -v

# Expected output:
# 18 tests covering all categories
# ~13 passing (72% success rate)
```

### 2. Test Specific Category

```bash
# Test all search tools
USE_MOCK_APIS=true pytest tests/integration/test_search_tools.py -v

# Test all communication tools
USE_MOCK_APIS=true pytest tests/integration/test_communication_tools.py -v
```

### 3. Test Individual Tool (Mock)

```bash
# Using pytest
USE_MOCK_APIS=true pytest -xvs tests/integration/test_search_tools.py::test_web_search

# Using tool's built-in test block
USE_MOCK_APIS=true python3 -m tools.search.web_search.web_search
```

### 4. Test Individual Tool (Live)

```bash
# Set API key
export SERPAPI_KEY=your_actual_key

# Run live test
python3 -m tools.search.web_search.web_search

# Expected output:
# Real search results from SerpAPI
```

---

## Tool-by-Tool Testing

### Search Tools (8 tools)

#### 1. web_search
**API Key**: `SERPAPI_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.search.web_search.web_search

# Live test
export SERPAPI_KEY=your_key
python3 -m tools.search.web_search.web_search
```

#### 2. scholar_search
**API Key**: `SERPAPI_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.search.scholar_search.scholar_search

# Live test
export SERPAPI_KEY=your_key
python3 -m tools.search.scholar_search.scholar_search
```

#### 3. image_search
**API Key**: `SERPAPI_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.search.image_search.image_search

# Live test
export SERPAPI_KEY=your_key
python3 -m tools.search.image_search.image_search
```

#### 4. video_search
**API Key**: `SERPAPI_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.search.video_search.video_search

# Live test
export SERPAPI_KEY=your_key
python3 -m tools.search.video_search.video_search
```

#### 5. product_search
**API Key**: `SERPAPI_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.search.product_search.product_search

# Live test
export SERPAPI_KEY=your_key
python3 -m tools.search.product_search.product_search
```

#### 6. google_product_search
**API Key**: `SERPAPI_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.search.google_product_search.google_product_search

# Live test
export SERPAPI_KEY=your_key
python3 -m tools.search.google_product_search.google_product_search
```

#### 7. financial_report
**API Key**: `SERPAPI_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.search.financial_report.financial_report

# Live test
export SERPAPI_KEY=your_key
python3 -m tools.search.financial_report.financial_report
```

#### 8. stock_price
**API Key**: `SERPAPI_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.search.stock_price.stock_price

# Live test
export SERPAPI_KEY=your_key
python3 -m tools.search.stock_price.stock_price
```

---

### Media Generation Tools (6 tools)

#### 1. image_generation
**API Keys**: `OPENAI_API_KEY` or `STABILITY_API_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.media_generation.image_generation.image_generation

# Live test (OpenAI)
export OPENAI_API_KEY=your_key
python3 -m tools.media_generation.image_generation.image_generation

# Live test (Stability AI)
export STABILITY_API_KEY=your_key
python3 -m tools.media_generation.image_generation.image_generation
```

#### 2. video_generation
**API Key**: `OPENAI_API_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.media_generation.video_generation.video_generation

# Live test
export OPENAI_API_KEY=your_key
python3 -m tools.media_generation.video_generation.video_generation
```

#### 3. audio_generation
**API Keys**: `OPENAI_API_KEY` or `ELEVENLABS_API_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.media_generation.audio_generation.audio_generation

# Live test (OpenAI)
export OPENAI_API_KEY=your_key
python3 -m tools.media_generation.audio_generation.audio_generation

# Live test (ElevenLabs)
export ELEVENLABS_API_KEY=your_key
python3 -m tools.media_generation.audio_generation.audio_generation
```

#### 4. podcast_generator
**API Key**: `OPENAI_API_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.media_generation.podcast_generator.podcast_generator

# Live test
export OPENAI_API_KEY=your_key
python3 -m tools.media_generation.podcast_generator.podcast_generator
```

#### 5. image_style_transfer
**API Key**: `OPENAI_API_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.media_generation.image_style_transfer.image_style_transfer

# Live test
export OPENAI_API_KEY=your_key
python3 -m tools.media_generation.image_style_transfer.image_style_transfer
```

#### 6. text_to_speech_advanced
**API Key**: `ELEVENLABS_API_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.media_generation.text_to_speech_advanced.text_to_speech_advanced

# Live test
export ELEVENLABS_API_KEY=your_key
python3 -m tools.media_generation.text_to_speech_advanced.text_to_speech_advanced
```

---

### Communication Tools (17 tools)

#### Gmail Tools (4 tools)

**API Keys**: Google OAuth credentials
```bash
export GMAIL_CLIENT_ID=your_client_id
export GMAIL_CLIENT_SECRET=your_client_secret
```

**1. gmail_search**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.gmail_search.gmail_search

# Live test
python3 -m tools.communication.gmail_search.gmail_search
```

**2. gmail_read**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.gmail_read.gmail_read

# Live test
python3 -m tools.communication.gmail_read.gmail_read
```

**3. read_email_attachments**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.read_email_attachments.read_email_attachments

# Live test
python3 -m tools.communication.read_email_attachments.read_email_attachments
```

**4. email_draft**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.email_draft.email_draft

# Live test
python3 -m tools.communication.email_draft.email_draft
```

#### Google Calendar Tools (4 tools)

**API Keys**: Google OAuth credentials
```bash
export GOOGLE_CALENDAR_CLIENT_ID=your_client_id
export GOOGLE_CALENDAR_CLIENT_SECRET=your_client_secret
```

**1. google_calendar_list**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.google_calendar_list.google_calendar_list

# Live test
python3 -m tools.communication.google_calendar_list.google_calendar_list
```

**2. google_calendar_create_event_draft**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.google_calendar_create_event_draft.google_calendar_create_event_draft

# Live test
python3 -m tools.communication.google_calendar_create_event_draft.google_calendar_create_event_draft
```

**3. google_calendar_update_event**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.google_calendar_update_event.google_calendar_update_event

# Live test
python3 -m tools.communication.google_calendar_update_event.google_calendar_update_event
```

**4. google_calendar_delete_event**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.google_calendar_delete_event.google_calendar_delete_event

# Live test
python3 -m tools.communication.google_calendar_delete_event.google_calendar_delete_event
```

#### Twilio Tools (2 tools)

**API Keys**:
```bash
export TWILIO_ACCOUNT_SID=your_account_sid
export TWILIO_AUTH_TOKEN=your_auth_token
export TWILIO_PHONE_NUMBER=your_twilio_number
```

**1. twilio_phone_call**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.twilio_phone_call.twilio_phone_call

# Live test
python3 -m tools.communication.twilio_phone_call.twilio_phone_call
```

**2. twilio_call_logs**
```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.communication.twilio_call_logs.twilio_call_logs

# Live test
python3 -m tools.communication.twilio_call_logs.twilio_call_logs
```

#### Other Communication Tools

**phone_call, query_call_logs, slack_*, teams_*, meeting_notes**
- All support mock mode with `USE_MOCK_APIS=true`
- Require respective API credentials for live testing

---

### Storage Tools (4 tools)

#### 1. aidrive_tool
**No API key required** (uses local storage)

```bash
# Test (works in both modes)
python3 -m tools.storage.aidrive_tool.aidrive_tool
```

#### 2. file_format_converter
**No API key required**

```bash
# Test
python3 -m tools.storage.file_format_converter.file_format_converter
```

#### 3. onedrive_search
**API Keys**:
```bash
export ONEDRIVE_CLIENT_ID=your_client_id
export ONEDRIVE_CLIENT_SECRET=your_client_secret
```

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.storage.onedrive_search.onedrive_search

# Live test
python3 -m tools.storage.onedrive_search.onedrive_search
```

#### 4. onedrive_file_read
**API Keys**: Same as onedrive_search

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.storage.onedrive_file_read.onedrive_file_read

# Live test
python3 -m tools.storage.onedrive_file_read.onedrive_file_read
```

---

### Visualization Tools (16 tools)

**Note**: 14/16 visualization tools **missing test blocks** (will be added in next release)

Current testing via integration tests:

```bash
# Test all visualization tools
USE_MOCK_APIS=true pytest tests/integration/test_visualization_tools.py -v
```

**Available tools**:
- generate_line_chart
- generate_bar_chart
- generate_pie_chart
- generate_scatter_chart
- generate_area_chart
- generate_column_chart
- generate_dual_axes_chart
- generate_histogram_chart
- generate_fishbone_diagram
- generate_flow_diagram
- generate_mind_map
- generate_network_graph
- generate_organization_chart
- generate_radar_chart
- generate_treemap_chart
- generate_word_cloud_chart

---

### Workspace Tools (2 tools)

#### 1. notion_search
**API Key**: `NOTION_API_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.workspace.notion_search.notion_search

# Live test
export NOTION_API_KEY=your_key
python3 -m tools.workspace.notion_search.notion_search
```

#### 2. notion_read
**API Key**: `NOTION_API_KEY`

```bash
# Mock test
USE_MOCK_APIS=true python3 -m tools.workspace.notion_read.notion_read

# Live test
export NOTION_API_KEY=your_key
python3 -m tools.workspace.notion_read.notion_read
```

---

### Utilities (8 tools)

**No API keys required** - All work without credentials

```bash
# Test think tool
python3 -m tools.utils.think.think

# Test ask_for_clarification
python3 -m tools.utils.ask_for_clarification.ask_for_clarification

# Test fact_checker
python3 -m tools.utils.fact_checker.fact_checker

# Test translation
python3 -m tools.utils.translation.translation

# Test batch_processor
python3 -m tools.utils.batch_processor.batch_processor

# Test text_formatter
python3 -m tools.utils.text_formatter.text_formatter

# Test json_validator
python3 -m tools.utils.json_validator.json_validator

# Test create_profile
python3 -m tools.utils.create_profile.create_profile
```

---

### Code Execution Tools (5 tools)

**No API keys required** - All work without credentials

```bash
# Test bash_tool
python3 -m tools.code_execution.bash_tool.bash_tool

# Test read_tool
python3 -m tools.code_execution.read_tool.read_tool

# Test write_tool
python3 -m tools.code_execution.write_tool.write_tool

# Test multiedit_tool
python3 -m tools.code_execution.multiedit_tool.multiedit_tool

# Test downloadfilewrapper_tool
python3 -m tools.code_execution.downloadfilewrapper_tool.downloadfilewrapper_tool
```

---

## API Key Setup

### Required Environment Variables

Create a `.env` file or export these variables:

```bash
# Search APIs
export SERPAPI_KEY=your_serpapi_key

# Media Generation
export OPENAI_API_KEY=your_openai_key
export STABILITY_API_KEY=your_stability_key
export ELEVENLABS_API_KEY=your_elevenlabs_key

# Communication - Gmail
export GMAIL_CLIENT_ID=your_gmail_client_id
export GMAIL_CLIENT_SECRET=your_gmail_client_secret

# Communication - Google Calendar
export GOOGLE_CALENDAR_CLIENT_ID=your_calendar_client_id
export GOOGLE_CALENDAR_CLIENT_SECRET=your_calendar_client_secret

# Communication - Twilio
export TWILIO_ACCOUNT_SID=your_twilio_sid
export TWILIO_AUTH_TOKEN=your_twilio_token
export TWILIO_PHONE_NUMBER=your_twilio_number

# Communication - Slack
export SLACK_BOT_TOKEN=your_slack_token

# Communication - Teams
export TEAMS_WEBHOOK_URL=your_teams_webhook

# Storage - OneDrive
export ONEDRIVE_CLIENT_ID=your_onedrive_client_id
export ONEDRIVE_CLIENT_SECRET=your_onedrive_client_secret

# Workspace - Notion
export NOTION_API_KEY=your_notion_key

# Testing
export USE_MOCK_APIS=true  # Enable mock mode
```

### Getting API Keys

1. **SerpAPI**: https://serpapi.com/ (free tier: 100 searches/month)
2. **OpenAI**: https://platform.openai.com/api-keys
3. **Stability AI**: https://platform.stability.ai/
4. **ElevenLabs**: https://elevenlabs.io/
5. **Google OAuth**: https://console.cloud.google.com/
6. **Twilio**: https://www.twilio.com/console
7. **Slack**: https://api.slack.com/apps
8. **Notion**: https://www.notion.so/my-integrations

---

## Troubleshooting

### Common Issues

#### 1. "Missing API key" error

**Solution**:
```bash
# Check if key is set
echo $SERPAPI_KEY

# Set the key
export SERPAPI_KEY=your_key

# Or use mock mode
export USE_MOCK_APIS=true
```

#### 2. "Module not found" error

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Or install in editable mode
pip install -e .
```

#### 3. Test block not found

**18 tools missing test blocks** (will be added soon):
- 14 visualization tools
- 4 web_content tools (crawler, summarize_large_document, url_metadata, webpage_capture_screen)

**Workaround**: Use integration tests instead:
```bash
USE_MOCK_APIS=true pytest tests/integration/ -v -k visualization
```

#### 4. Import errors

**Solution**:
```bash
# Run from repository root
cd /path/to/agentswarm-tools

# Use Python module syntax
python3 -m tools.search.web_search.web_search
```

#### 5. Rate limit errors

**Solution**:
```bash
# Use mock mode for development
export USE_MOCK_APIS=true

# Or wait and retry
# Rate limits reset every 60 seconds
```

---

## Best Practices

### 1. Development Workflow

```bash
# Always start with mock mode
export USE_MOCK_APIS=true
python3 -m tools.search.web_search.web_search

# Verify mock works, then test live
unset USE_MOCK_APIS
export SERPAPI_KEY=your_key
python3 -m tools.search.web_search.web_search
```

### 2. CI/CD Testing

```bash
# Use mock mode in CI
export USE_MOCK_APIS=true
pytest tests/integration/ -v
```

### 3. Production Validation

```bash
# Test critical tools with live APIs
export USE_MOCK_APIS=false
pytest tests/integration/test_search_tools.py -v
pytest tests/integration/test_communication_tools.py -v
```

---

## Test Coverage Goals

| Category | Current | Target |
|----------|---------|--------|
| Tools with test blocks | 82% | 100% |
| Integration test coverage | 100% | 100% |
| Code coverage | 23% | 80% |
| Mock mode support | 100% | 100% |

---

## Summary

✅ **101 tools** production-ready
✅ **83 tools** have test blocks (82%)
✅ **100%** support mock mode
✅ **18 integration tests** covering all categories
⚠️ **18 tools** need test blocks (14 viz + 4 web_content)
⚠️ **23% code coverage** (target: 80%)

**Next steps**:
1. Add test blocks to 18 remaining tools
2. Increase code coverage to 80%
3. Document API key acquisition in detail
4. Add performance benchmarks

---

**Questions?** See [CONTRIBUTING.md](../../CONTRIBUTING.md) or file an issue on GitHub.
