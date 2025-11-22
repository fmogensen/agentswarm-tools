"""
Translation Tool - Multi-language translation with format preservation

This tool provides translation services using Google Translate or DeepL API,
with support for auto-detection, format preservation, and batch translation.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import requests
import re
from html.parser import HTMLParser

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, ConfigurationError


class Translation(BaseTool):
    """
    Translate text between languages with format preservation.

    This tool provides:
    1. Multi-language translation (100+ languages)
    2. Automatic source language detection
    3. Format preservation (markdown, HTML, plain text)
    4. Batch translation support for multiple texts
    5. Support for both Google Translate API and DeepL API

    Args:
        text: Text to translate (required). For batch translation, use list format.
        source_lang: Source language code (auto-detect if None)
        target_lang: Target language code (required, e.g., 'es', 'fr', 'de', 'ja', 'zh')
        preserve_formatting: Whether to preserve markdown/HTML formatting
        api_provider: Which API to use ('google' or 'deepl', default: 'google')

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Dict with:
            - translated_text: The translated text or list of texts
            - detected_language: Source language (if auto-detected)
            - source_lang: Source language code used
            - target_lang: Target language code
            - character_count: Number of characters translated
            - preserved_format: Whether formatting was preserved
        - metadata: Additional information about the translation

    Raises:
        ValidationError: If text is empty, target_lang missing, or invalid language codes
        ConfigurationError: If API credentials are missing
        APIError: If translation API fails

    Example:
        >>> tool = Translation(
        ...     text="Hello, world!",
        ...     target_lang="es",
        ...     preserve_formatting=False
        ... )
        >>> result = tool.run()
        >>> print(result["result"]["translated_text"])
        ¡Hola, mundo!

    Supported Language Codes:
        - English: 'en'
        - Spanish: 'es'
        - French: 'fr'
        - German: 'de'
        - Italian: 'it'
        - Portuguese: 'pt'
        - Russian: 'ru'
        - Japanese: 'ja'
        - Korean: 'ko'
        - Chinese (Simplified): 'zh' or 'zh-CN'
        - Chinese (Traditional): 'zh-TW'
        - Arabic: 'ar'
        - Hindi: 'hi'
        And 100+ more languages
    """

    # Tool metadata
    tool_name: str = "translation"
    tool_category: str = "utils"

    # Parameters
    text: str = Field(
        ..., description="Text to translate (required)", min_length=1, max_length=10000
    )

    source_lang: Optional[str] = Field(
        default=None,
        description="Source language code (auto-detect if None, e.g., 'en', 'es', 'fr')",
    )

    target_lang: str = Field(
        ...,
        description="Target language code (required, e.g., 'es', 'fr', 'de', 'ja', 'zh')",
        min_length=2,
        max_length=10,
    )

    preserve_formatting: bool = Field(
        default=True, description="Whether to preserve markdown/HTML formatting"
    )

    api_provider: str = Field(default="google", description="Which API to use: 'google' or 'deepl'")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the translation tool.

        Returns:
            Dict with translation results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "api_provider": self.api_provider,
                    "source_lang": result.get("source_lang"),
                    "target_lang": self.target_lang,
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.text.strip():
            raise ValidationError(
                "Text cannot be empty", tool_name=self.tool_name, details={"text": self.text}
            )

        if not self.target_lang.strip():
            raise ValidationError(
                "Target language is required",
                tool_name=self.tool_name,
                details={"target_lang": self.target_lang},
            )

        # Validate API provider
        valid_providers = ["google", "deepl"]
        if self.api_provider.lower() not in valid_providers:
            raise ValidationError(
                f"Invalid API provider. Must be one of: {valid_providers}",
                tool_name=self.tool_name,
                details={"api_provider": self.api_provider},
            )

        # Validate language codes (basic check)
        if self.source_lang:
            if not self._is_valid_language_code(self.source_lang):
                raise ValidationError(
                    f"Invalid source language code: {self.source_lang}",
                    tool_name=self.tool_name,
                    details={"source_lang": self.source_lang},
                )

        if not self._is_valid_language_code(self.target_lang):
            raise ValidationError(
                f"Invalid target language code: {self.target_lang}",
                tool_name=self.tool_name,
                details={"target_lang": self.target_lang},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        # Create a simple mock translation
        mock_translations = {
            "es": "¡Hola, mundo!",
            "fr": "Bonjour, le monde!",
            "de": "Hallo, Welt!",
            "ja": "こんにちは、世界！",
            "zh": "你好，世界！",
            "zh-CN": "你好，世界！",
            "zh-TW": "你好，世界！",
            "ru": "Привет, мир!",
            "it": "Ciao, mondo!",
            "pt": "Olá, mundo!",
            "ko": "안녕하세요, 세계!",
            "ar": "مرحبا بالعالم!",
            "hi": "नमस्ते, दुनिया!",
        }

        # Get mock translation or default
        mock_text = mock_translations.get(
            self.target_lang.lower(), f"[Mock translation to {self.target_lang}]: {self.text}"
        )

        detected_lang = self.source_lang or "en"

        return {
            "success": True,
            "result": {
                "translated_text": mock_text,
                "detected_language": detected_lang if not self.source_lang else None,
                "source_lang": detected_lang,
                "target_lang": self.target_lang,
                "character_count": len(self.text),
                "preserved_format": self.preserve_formatting,
            },
            "metadata": {"mock_mode": True, "api_provider": self.api_provider},
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        # Select API based on provider
        if self.api_provider.lower() == "deepl":
            return self._translate_with_deepl()
        else:
            return self._translate_with_google()

    def _translate_with_google(self) -> Dict[str, Any]:
        """Translate using Google Translate API."""
        api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")

        if not api_key:
            raise ConfigurationError(
                "Missing GOOGLE_TRANSLATE_API_KEY environment variable",
                tool_name=self.tool_name,
                config_key="GOOGLE_TRANSLATE_API_KEY",
            )

        try:
            # Prepare text for translation
            text_to_translate = self.text
            format_markers = {}

            # Extract and preserve formatting if needed
            if self.preserve_formatting:
                text_to_translate, format_markers = self._extract_formatting(self.text)

            # Build API request
            url = "https://translation.googleapis.com/language/translate/v2"
            params = {
                "key": api_key,
                "q": text_to_translate,
                "target": self.target_lang,
                "format": "html" if self.preserve_formatting else "text",
            }

            # Add source language if specified
            if self.source_lang:
                params["source"] = self.source_lang

            # Make API request
            response = requests.post(url, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Extract translation
            if "data" not in result or "translations" not in result["data"]:
                raise APIError(
                    "Invalid response from Google Translate API",
                    tool_name=self.tool_name,
                    api_name="Google Translate",
                )

            translation_data = result["data"]["translations"][0]
            translated_text = translation_data.get("translatedText", "")
            detected_lang = translation_data.get("detectedSourceLanguage")

            # Restore formatting if preserved
            if self.preserve_formatting and format_markers:
                translated_text = self._restore_formatting(translated_text, format_markers)

            return {
                "translated_text": translated_text,
                "detected_language": detected_lang,
                "source_lang": self.source_lang or detected_lang,
                "target_lang": self.target_lang,
                "character_count": len(self.text),
                "preserved_format": self.preserve_formatting,
            }

        except requests.RequestException as e:
            raise APIError(
                f"Google Translate API request failed: {e}",
                tool_name=self.tool_name,
                api_name="Google Translate",
            )

    def _translate_with_deepl(self) -> Dict[str, Any]:
        """Translate using DeepL API."""
        api_key = os.getenv("DEEPL_API_KEY")

        if not api_key:
            raise ConfigurationError(
                "Missing DEEPL_API_KEY environment variable",
                tool_name=self.tool_name,
                config_key="DEEPL_API_KEY",
            )

        try:
            # Determine API endpoint (free vs pro)
            if api_key.endswith(":fx"):
                base_url = "https://api-free.deepl.com/v2/translate"
            else:
                base_url = "https://api.deepl.com/v2/translate"

            # Build API request
            headers = {
                "Authorization": f"DeepL-Auth-Key {api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            data = {"text": self.text, "target_lang": self.target_lang.upper()}

            # Add source language if specified
            if self.source_lang:
                data["source_lang"] = self.source_lang.upper()

            # Add formatting option
            if self.preserve_formatting:
                data["tag_handling"] = "html"

            # Make API request
            response = requests.post(base_url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            # Extract translation
            if "translations" not in result or not result["translations"]:
                raise APIError(
                    "Invalid response from DeepL API", tool_name=self.tool_name, api_name="DeepL"
                )

            translation_data = result["translations"][0]
            translated_text = translation_data.get("text", "")
            detected_lang = translation_data.get("detected_source_language", "").lower()

            return {
                "translated_text": translated_text,
                "detected_language": detected_lang if not self.source_lang else None,
                "source_lang": self.source_lang or detected_lang,
                "target_lang": self.target_lang,
                "character_count": len(self.text),
                "preserved_format": self.preserve_formatting,
            }

        except requests.RequestException as e:
            raise APIError(
                f"DeepL API request failed: {e}", tool_name=self.tool_name, api_name="DeepL"
            )

    def _extract_formatting(self, text: str) -> tuple:
        """
        Extract formatting markers (markdown, HTML) from text.
        Returns (cleaned_text, format_markers).
        """
        format_markers = {}
        cleaned_text = text

        # Preserve markdown links [text](url)
        markdown_links = re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", cleaned_text)
        for i, (link_text, url) in enumerate(markdown_links):
            marker = f"__MDLINK_{i}__"
            format_markers[marker] = f"[{link_text}]({url})"
            cleaned_text = cleaned_text.replace(f"[{link_text}]({url})", marker, 1)

        # Preserve markdown bold **text**
        bold_matches = re.findall(r"\*\*([^\*]+)\*\*", cleaned_text)
        for i, bold_text in enumerate(bold_matches):
            marker = f"__BOLD_{i}__"
            format_markers[marker] = f"**{bold_text}**"
            cleaned_text = cleaned_text.replace(f"**{bold_text}**", marker, 1)

        # Preserve markdown italic *text*
        italic_matches = re.findall(r"\*([^\*]+)\*", cleaned_text)
        for i, italic_text in enumerate(italic_matches):
            marker = f"__ITALIC_{i}__"
            format_markers[marker] = f"*{italic_text}*"
            cleaned_text = cleaned_text.replace(f"*{italic_text}*", marker, 1)

        # Preserve code blocks ```code```
        code_blocks = re.findall(r"```([^`]+)```", cleaned_text)
        for i, code in enumerate(code_blocks):
            marker = f"__CODE_{i}__"
            format_markers[marker] = f"```{code}```"
            cleaned_text = cleaned_text.replace(f"```{code}```", marker, 1)

        return cleaned_text, format_markers

    def _restore_formatting(self, text: str, format_markers: Dict[str, str]) -> str:
        """Restore formatting markers back into translated text."""
        restored_text = text

        # Restore in reverse order to handle nested formatting
        for marker, original in format_markers.items():
            restored_text = restored_text.replace(marker, original)

        return restored_text

    def _is_valid_language_code(self, lang_code: str) -> bool:
        """
        Validate language code format.
        Accepts ISO 639-1 (2-letter) and some common variants.
        """
        # Common language codes (not exhaustive, but covers major languages)
        valid_codes = {
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "ru",
            "ja",
            "ko",
            "zh",
            "zh-CN",
            "zh-TW",
            "ar",
            "hi",
            "bn",
            "pa",
            "te",
            "mr",
            "ta",
            "ur",
            "gu",
            "kn",
            "ml",
            "or",
            "nl",
            "sv",
            "pl",
            "tr",
            "vi",
            "th",
            "id",
            "ms",
            "fil",
            "he",
            "fa",
            "uk",
            "ro",
            "hu",
            "cs",
            "el",
            "da",
            "fi",
            "no",
            "sk",
            "bg",
            "hr",
            "sr",
            "sl",
            "lt",
            "lv",
            "et",
            "sq",
            "mk",
            "bs",
            "is",
            "mt",
            "cy",
            "ga",
            "eu",
            "ca",
            "gl",
            "af",
            "sw",
            "zu",
            "xh",
            "so",
            "ha",
            "yo",
            "ig",
            "am",
            "km",
            "lo",
            "my",
            "si",
            "ka",
            "hy",
            "az",
            "kk",
            "uz",
            "ky",
            "tg",
            "mn",
            "ne",
            "ps",
        }

        return lang_code.lower() in valid_codes or len(lang_code) == 2


if __name__ == "__main__":
    # Test the translation tool
    print("Testing Translation tool...")

    # Test with mock mode
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic translation
    print("\n--- Test 1: Basic translation (English to Spanish) ---")
    tool = Translation(
        text="Hello, world! How are you?", target_lang="es", preserve_formatting=False
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Original: {result['metadata']['source_lang']}")
    print(f"Translated: {result['result']['translated_text']}")
    print(f"Target language: {result['result']['target_lang']}")
    print(f"Characters: {result['result']['character_count']}")

    # Test 2: With auto-detection
    print("\n--- Test 2: Auto-detect source language ---")
    tool2 = Translation(
        text="Bonjour, comment allez-vous?", target_lang="en", preserve_formatting=False
    )
    result2 = tool2.run()

    print(f"Success: {result2.get('success')}")
    print(f"Detected language: {result2['result']['detected_language']}")
    print(f"Translated: {result2['result']['translated_text']}")

    # Test 3: With formatting preservation
    print("\n--- Test 3: Preserve markdown formatting ---")
    tool3 = Translation(
        text="**Hello**, this is a *test* with [a link](https://example.com) and ```code```",
        target_lang="fr",
        preserve_formatting=True,
    )
    result3 = tool3.run()

    print(f"Success: {result3.get('success')}")
    print(f"Translated: {result3['result']['translated_text']}")
    print(f"Format preserved: {result3['result']['preserved_format']}")

    # Test 4: DeepL provider
    print("\n--- Test 4: Using DeepL provider ---")
    tool4 = Translation(
        text="Good morning!", target_lang="de", api_provider="deepl", preserve_formatting=False
    )
    result4 = tool4.run()

    print(f"Success: {result4.get('success')}")
    print(f"API Provider: {result4['metadata']['api_provider']}")
    print(f"Translated: {result4['result']['translated_text']}")

    # Test 5: Japanese translation
    print("\n--- Test 5: Translate to Japanese ---")
    tool5 = Translation(
        text="Welcome to the translation tool!", target_lang="ja", preserve_formatting=False
    )
    result5 = tool5.run()

    print(f"Success: {result5.get('success')}")
    print(f"Translated: {result5['result']['translated_text']}")

    # Test 6: Chinese (Simplified)
    print("\n--- Test 6: Translate to Chinese (Simplified) ---")
    tool6 = Translation(text="This is a test message.", target_lang="zh", preserve_formatting=False)
    result6 = tool6.run()

    print(f"Success: {result6.get('success')}")
    print(f"Translated: {result6['result']['translated_text']}")
