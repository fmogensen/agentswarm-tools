# Translation Tool

Multi-language translation with automatic language detection and format preservation.

## Overview

The Translation tool provides professional translation services with:
- Support for 100+ languages via Google Translate or DeepL API
- Automatic source language detection
- Markdown and HTML formatting preservation
- Batch translation support
- Character count tracking

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | str | Yes | - | Text to translate (1-10,000 characters) |
| `source_lang` | str | No | None | Source language code (auto-detect if None) |
| `target_lang` | str | Yes | - | Target language code (e.g., 'es', 'fr', 'de') |
| `preserve_formatting` | bool | No | True | Whether to preserve markdown/HTML formatting |
| `api_provider` | str | No | 'google' | API provider: 'google' or 'deepl' |

## Supported Languages

Common language codes (100+ total):

- **English**: `en`
- **Spanish**: `es`
- **French**: `fr`
- **German**: `de`
- **Italian**: `it`
- **Portuguese**: `pt`
- **Russian**: `ru`
- **Japanese**: `ja`
- **Korean**: `ko`
- **Chinese (Simplified)**: `zh` or `zh-CN`
- **Chinese (Traditional)**: `zh-TW`
- **Arabic**: `ar`
- **Hindi**: `hi`

See code for full list of supported languages.

## Returns

```python
{
    "success": True,
    "result": {
        "translated_text": "¡Hola, mundo!",
        "detected_language": "en",  # If auto-detected
        "source_lang": "en",
        "target_lang": "es",
        "character_count": 13,
        "preserved_format": True
    },
    "metadata": {
        "tool_name": "translation",
        "api_provider": "google",
        "source_lang": "en",
        "target_lang": "es"
    }
}
```

## Environment Variables

Choose one provider (not needed in mock mode):

### Google Translate API

```bash
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key
```

### DeepL API

```bash
DEEPL_API_KEY=your_deepl_api_key
```

## Usage Examples

### Basic Translation

```python
from tools.utils.translation import Translation

tool = Translation(
    text="Hello, world! How are you?",
    target_lang="es",
    preserve_formatting=False
)
result = tool.run()

print(f"Translated: {result['result']['translated_text']}")
# Output: ¡Hola, mundo! ¿Cómo estás?
```

### Auto-Detect Source Language

```python
tool = Translation(
    text="Bonjour, comment allez-vous?",
    target_lang="en"
)
result = tool.run()

print(f"Detected: {result['result']['detected_language']}")
print(f"Translated: {result['result']['translated_text']}")
# Output: Detected: fr
#         Translated: Hello, how are you?
```

### Preserve Markdown Formatting

```python
tool = Translation(
    text="**Hello**, this is a *test* with [a link](https://example.com) and ```code```",
    target_lang="fr",
    preserve_formatting=True
)
result = tool.run()

print(result['result']['translated_text'])
# Markdown formatting is preserved in translation
```

### Using DeepL Provider

```python
tool = Translation(
    text="Good morning!",
    target_lang="de",
    api_provider="deepl"
)
result = tool.run()

print(f"Translated: {result['result']['translated_text']}")
# Output: Guten Morgen!
```

### Specify Both Languages

```python
tool = Translation(
    text="Hello",
    source_lang="en",
    target_lang="ja"
)
result = tool.run()

print(result['result']['translated_text'])
# Output: こんにちは
```

## Format Preservation

When `preserve_formatting=True`, the tool preserves:

- **Markdown bold**: `**text**`
- **Markdown italic**: `*text*`
- **Markdown links**: `[text](url)`
- **Code blocks**: `` `code` ``
- **HTML tags**: Basic HTML structure

The tool extracts formatting markers before translation and restores them afterward.

## API Provider Comparison

| Feature | Google Translate | DeepL |
|---------|-----------------|-------|
| Languages | 100+ | 30+ |
| Free Tier | Yes (limited) | Yes (500k chars/month) |
| Quality | Good | Excellent (esp. European) |
| Formatting | HTML support | HTML tag handling |
| Speed | Fast | Fast |

### When to Use Google Translate
- Need support for rare languages
- High volume translations
- Cost-sensitive applications

### When to Use DeepL
- European language translations
- Need highest quality output
- Professional/business content

## Testing

Run tests with mock mode (no API keys required):

```bash
# Unit tests
pytest tools/utils/translation/test_translation.py

# Manual test
python3 tools/utils/translation/test_translation.py
```

## Implementation Details

### Required Methods

All 5 Agency Swarm required methods are implemented:

1. `_execute()` - Main orchestration
2. `_validate_parameters()` - Input validation
3. `_should_use_mock()` - Mock mode check
4. `_generate_mock_results()` - Test data generation
5. `_process()` - Core translation logic

### Security

- No hardcoded API keys (uses `os.getenv()`)
- Language code validation
- Input length limits (10,000 characters)
- Proper error handling

### Error Handling

Raises appropriate errors:
- `ValidationError` - Invalid text, language codes, or API provider
- `ConfigurationError` - Missing API credentials
- `APIError` - Translation API failures

## Character Limits

- **Maximum text length**: 10,000 characters per request
- **Google Translate**: ~15,000 characters per request
- **DeepL Free**: 500,000 characters per month
- **DeepL Pro**: Unlimited

For larger documents, consider:
1. Splitting text into chunks
2. Using batch translation
3. Upgrading to DeepL Pro

## Supported Formats

### Text Formats
- Plain text
- Markdown
- HTML
- JSON strings (as text)

### Not Supported
- Binary files (PDF, DOCX, etc.) - use file_format_converter first
- Images with text - use OCR tools first
- Audio transcripts - use audio_transcribe first

## Best Practices

1. **Use Auto-Detection**: Omit `source_lang` for automatic detection
2. **Preserve Formatting**: Enable for rich text, disable for plain text
3. **Choose Right Provider**: DeepL for quality, Google for coverage
4. **Batch Small Texts**: Combine short texts to reduce API calls
5. **Cache Translations**: Store results for frequently translated content

## Limitations

1. **Context**: Translations are sentence-level, may lack broader context
2. **Idioms**: May translate literally rather than idiomatically
3. **Technical Terms**: May not recognize domain-specific jargon
4. **Formatting Complexity**: Complex nested formatting may not fully preserve

## Future Enhancements

- Batch translation support (multiple texts at once)
- Translation memory/glossary support
- Custom terminology dictionaries
- Context-aware translation with LLMs
- Support for more formatting types (LaTeX, reStructuredText)
- Translation quality scoring

## License

Part of the AgentSwarm Tools Framework.
