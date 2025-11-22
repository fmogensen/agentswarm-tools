# FactChecker Tool

Verify claims using web search and academic sources with credibility analysis.

## Overview

The FactChecker tool performs automated fact-checking by:
- Searching for evidence using Google Search and optional Scholar search
- Analyzing source credibility based on domain reputation
- Categorizing sources as supporting, contradicting, or neutral
- Computing a confidence score (0-100) based on evidence strength
- Providing a clear verdict and analysis summary

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `claim` | str | Yes | - | The claim or statement to verify (5-500 characters) |
| `sources` | List[str] | No | None | Optional list of specific source URLs to check |
| `use_scholar` | bool | No | False | Whether to include academic sources via scholar search |
| `max_sources` | int | No | 10 | Maximum number of sources to analyze (1-50) |

## Returns

```python
{
    "success": True,
    "result": {
        "confidence_score": 85,  # 0-100
        "verdict": "SUPPORTED",  # SUPPORTED, CONTRADICTED, or INSUFFICIENT_EVIDENCE
        "supporting_sources": [...],
        "contradicting_sources": [...],
        "neutral_sources": [...],
        "analysis_summary": "..."
    },
    "metadata": {
        "tool_name": "fact_checker",
        "claim": "...",
        "sources_analyzed": 8
    }
}
```

## Environment Variables

Required for production use (not needed in mock mode):

```bash
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

## Usage Examples

### Basic Fact Check

```python
from tools.utils.fact_checker import FactChecker

tool = FactChecker(
    claim="The Earth is round",
    use_scholar=False,
    max_sources=10
)
result = tool.run()

print(f"Verdict: {result['result']['verdict']}")
print(f"Confidence: {result['result']['confidence_score']}/100")
print(f"Analysis: {result['result']['analysis_summary']}")
```

### With Academic Sources

```python
tool = FactChecker(
    claim="Climate change is real",
    use_scholar=True,  # Include .edu and .gov sources
    max_sources=15
)
result = tool.run()

print(f"Supporting sources: {len(result['result']['supporting_sources'])}")
print(f"Contradicting sources: {len(result['result']['contradicting_sources'])}")
```

### With Specific Sources

```python
tool = FactChecker(
    claim="Water boils at 100°C at sea level",
    sources=[
        "https://www.nasa.gov",
        "https://www.noaa.gov",
        "https://en.wikipedia.org"
    ],
    max_sources=5
)
result = tool.run()
```

## Source Credibility Scoring

Sources are scored 0-100 based on domain type:

- **95**: Fact-checking sites (snopes.com, factcheck.org, politifact.com, etc.)
- **85**: Academic/government (.edu, .gov)
- **70**: Commercial/general (.com, .net)
- **60**: Other domains

Academic sources get a +20 bonus when `use_scholar=True`.

## Verdict Determination

- **SUPPORTED**: Confidence score ≥ 70
- **CONTRADICTED**: Confidence score ≤ 30
- **INSUFFICIENT_EVIDENCE**: Confidence score 31-69

## Testing

Run tests with mock mode (no API keys required):

```bash
# Unit tests
pytest tools/utils/fact_checker/test_fact_checker.py

# Manual test
python3 tools/utils/fact_checker/test_fact_checker.py
```

## Implementation Details

### Required Methods

All 5 Agency Swarm required methods are implemented:

1. `_execute()` - Main orchestration
2. `_validate_parameters()` - Input validation
3. `_should_use_mock()` - Mock mode check
4. `_generate_mock_results()` - Test data generation
5. `_process()` - Core fact-checking logic

### Security

- No hardcoded API keys (uses `os.getenv()`)
- URL validation for user-provided sources
- Proper error handling with structured exceptions

### Error Handling

Raises appropriate errors:
- `ValidationError` - Invalid claim or source URLs
- `APIError` - Search API failures
- `ConfigurationError` - Missing API credentials

## Limitations

1. **Language**: Currently optimized for English claims
2. **Heuristic Analysis**: Source categorization uses keyword matching (not NLP/LLM)
3. **Credibility Scoring**: Based on domain reputation, not deep content analysis
4. **API Dependency**: Requires Google Search API for production use

## Future Enhancements

- Integration with dedicated fact-checking APIs (FactCheckAPI, ClaimBuster)
- NLP-based source analysis using LLMs
- Multi-language support
- Historical claim tracking
- Source verification depth scoring

## License

Part of the AgentSwarm Tools Framework.
