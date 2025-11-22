"""
Tests for Translation Tool
"""

import pytest
import os
from translation import Translation
from shared.errors import ValidationError, ConfigurationError


class TestTranslation:
    """Test suite for Translation tool."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_basic_translation(self):
        """Test basic translation."""
        tool = Translation(text="Hello, world!", target_lang="es", preserve_formatting=False)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert "translated_text" in result["result"]
        assert len(result["result"]["translated_text"]) > 0

    def test_auto_detect_language(self):
        """Test automatic language detection."""
        tool = Translation(
            text="Bonjour, comment allez-vous?", target_lang="en", preserve_formatting=False
        )
        result = tool.run()

        assert result["success"] is True
        assert "source_lang" in result["result"]
        # In mock mode, should detect or default to a language
        assert result["result"]["source_lang"] is not None

    def test_with_formatting_preservation(self):
        """Test translation with formatting preservation."""
        tool = Translation(
            text="**Hello**, this is a *test* message", target_lang="fr", preserve_formatting=True
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["preserved_format"] is True

    def test_google_provider(self):
        """Test using Google Translate provider."""
        tool = Translation(
            text="Good morning!", target_lang="de", api_provider="google", preserve_formatting=False
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["api_provider"] == "google"

    def test_deepl_provider(self):
        """Test using DeepL provider."""
        tool = Translation(
            text="Good morning!", target_lang="de", api_provider="deepl", preserve_formatting=False
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["api_provider"] == "deepl"

    def test_multiple_languages(self):
        """Test translation to various languages."""
        languages = ["es", "fr", "de", "ja", "zh", "ru"]

        for lang in languages:
            tool = Translation(text="Hello", target_lang=lang, preserve_formatting=False)
            result = tool.run()

            assert result["success"] is True
            assert result["result"]["target_lang"] == lang

    def test_character_count(self):
        """Test that character count is tracked."""
        text = "This is a test message"
        tool = Translation(text=text, target_lang="es", preserve_formatting=False)
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["character_count"] == len(text)

    def test_empty_text_validation(self):
        """Test validation of empty text."""
        with pytest.raises(ValidationError):
            tool = Translation(text="", target_lang="es")
            tool.run()

    def test_missing_target_lang_validation(self):
        """Test validation of missing target language."""
        with pytest.raises(ValidationError):
            tool = Translation(text="Hello", target_lang="")
            tool.run()

    def test_invalid_api_provider(self):
        """Test validation of invalid API provider."""
        with pytest.raises(ValidationError):
            tool = Translation(text="Hello", target_lang="es", api_provider="invalid_provider")
            tool.run()

    def test_invalid_language_code(self):
        """Test validation of invalid language codes."""
        with pytest.raises(ValidationError):
            tool = Translation(text="Hello", target_lang="xyz123")  # Invalid language code
            tool.run()

    def test_source_and_target_specified(self):
        """Test with both source and target languages specified."""
        tool = Translation(
            text="Hello", source_lang="en", target_lang="es", preserve_formatting=False
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["source_lang"] == "en"
        assert result["result"]["target_lang"] == "es"

    def test_long_text_translation(self):
        """Test translation of longer text."""
        long_text = "This is a longer text message. " * 20
        tool = Translation(text=long_text, target_lang="fr", preserve_formatting=False)
        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]["translated_text"]) > 0

    def test_mock_mode(self):
        """Test that mock mode works correctly."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = Translation(text="Test message", target_lang="es", preserve_formatting=False)
        result = tool.run()

        assert result["success"] is True
        assert "translated_text" in result["result"]


if __name__ == "__main__":
    # Run tests
    print("Running Translation tests...")

    # Enable mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic translation
    print("\n--- Test 1: Basic translation (English to Spanish) ---")
    try:
        tool = Translation(
            text="Hello, world! How are you?", target_lang="es", preserve_formatting=False
        )
        result = tool.run()
        print(f"✓ Success: {result['success']}")
        print(f"✓ Original text: {tool.text}")
        print(f"✓ Translated: {result['result']['translated_text']}")
        print(f"✓ Target language: {result['result']['target_lang']}")
    except Exception as e:
        print(f"✗ Test failed: {e}")

    # Test 2: Auto-detect source language
    print("\n--- Test 2: Auto-detect source language ---")
    try:
        tool = Translation(
            text="Bonjour, comment allez-vous?", target_lang="en", preserve_formatting=False
        )
        result = tool.run()
        print(f"✓ Success: {result['success']}")
        print(f"✓ Detected language: {result['result']['detected_language']}")
        print(f"✓ Translated: {result['result']['translated_text']}")
    except Exception as e:
        print(f"✗ Test failed: {e}")

    # Test 3: Preserve formatting
    print("\n--- Test 3: Preserve markdown formatting ---")
    try:
        tool = Translation(
            text="**Hello**, this is a *test* with [a link](https://example.com)",
            target_lang="fr",
            preserve_formatting=True,
        )
        result = tool.run()
        print(f"✓ Success: {result['success']}")
        print(f"✓ Translated: {result['result']['translated_text']}")
        print(f"✓ Format preserved: {result['result']['preserved_format']}")
    except Exception as e:
        print(f"✗ Test failed: {e}")

    # Test 4: Multiple languages
    print("\n--- Test 4: Multiple target languages ---")
    languages = ["es", "fr", "de", "ja", "zh"]
    for lang in languages:
        try:
            tool = Translation(text="Welcome", target_lang=lang, preserve_formatting=False)
            result = tool.run()
            print(f"✓ {lang}: {result['result']['translated_text']}")
        except Exception as e:
            print(f"✗ {lang} failed: {e}")

    # Test 5: DeepL provider
    print("\n--- Test 5: Using DeepL provider ---")
    try:
        tool = Translation(
            text="Good morning!", target_lang="de", api_provider="deepl", preserve_formatting=False
        )
        result = tool.run()
        print(f"✓ Success: {result['success']}")
        print(f"✓ API Provider: {result['metadata']['api_provider']}")
        print(f"✓ Translated: {result['result']['translated_text']}")
    except Exception as e:
        print(f"✗ Test failed: {e}")

    # Test 6: Empty text validation
    print("\n--- Test 6: Empty text validation ---")
    try:
        tool = Translation(text="", target_lang="es")
        result = tool.run()
        print(f"✗ Should have raised ValidationError")
    except ValidationError as e:
        print(f"✓ Correctly raised ValidationError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Test 7: Invalid API provider
    print("\n--- Test 7: Invalid API provider validation ---")
    try:
        tool = Translation(text="Hello", target_lang="es", api_provider="invalid")
        result = tool.run()
        print(f"✗ Should have raised ValidationError")
    except ValidationError as e:
        print(f"✓ Correctly raised ValidationError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Test 8: Both source and target specified
    print("\n--- Test 8: Both source and target languages specified ---")
    try:
        tool = Translation(
            text="Hello, world!", source_lang="en", target_lang="es", preserve_formatting=False
        )
        result = tool.run()
        print(f"✓ Success: {result['success']}")
        print(f"✓ Source: {result['result']['source_lang']}")
        print(f"✓ Target: {result['result']['target_lang']}")
    except Exception as e:
        print(f"✗ Test failed: {e}")

    print("\n--- All manual tests completed ---")
