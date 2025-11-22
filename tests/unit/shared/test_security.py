"""
Comprehensive tests for shared.security module.
Target coverage: 95%+
"""

import pytest
import os
import time
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from shared.security import (
    APIKeyManager,
    InputValidator,
    RateLimiter,
    get_rate_limiter,
    require_api_key,
    rate_limit,
    hash_user_id,
    validate_api_keys
)
from shared.errors import (
    AuthenticationError,
    RateLimitError,
    SecurityError,
    ValidationError
)


# Fixtures

@pytest.fixture
def clean_env():
    """Clean environment variables for testing."""
    original = os.environ.copy()
    # Clear any API keys
    for key in list(os.environ.keys()):
        if "API" in key or "KEY" in key or "SECRET" in key:
            os.environ.pop(key, None)
    yield
    os.environ.clear()
    os.environ.update(original)


@pytest.fixture
def rate_limiter():
    """Create fresh rate limiter instance."""
    return RateLimiter()


# Test APIKeyManager

def test_api_key_manager_get_key_present(clean_env):
    """Test getting API key that exists."""
    os.environ["TEST_API_KEY"] = "test_key_value"

    key = APIKeyManager.get_key("TEST_API_KEY")

    assert key == "test_key_value"


def test_api_key_manager_get_key_missing_required(clean_env):
    """Test getting required API key that is missing."""
    with pytest.raises(AuthenticationError) as exc_info:
        APIKeyManager.get_key("MISSING_KEY", required=True)

    assert "Missing required API key: MISSING_KEY" in str(exc_info.value)


def test_api_key_manager_get_key_missing_optional(clean_env):
    """Test getting optional API key that is missing."""
    key = APIKeyManager.get_key("MISSING_KEY", required=False)

    assert key is None


def test_api_key_manager_validate_keys_all_present(clean_env):
    """Test validate_keys when all keys present."""
    os.environ["SERPAPI_KEY"] = "key1"
    os.environ["OPENAI_API_KEY"] = "key2"
    os.environ["GMAIL_CLIENT_ID"] = "key3"
    os.environ["GMAIL_CLIENT_SECRET"] = "key4"
    os.environ["AWS_ACCESS_KEY_ID"] = "key5"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "key6"

    missing = APIKeyManager.validate_keys()

    assert missing == []


def test_api_key_manager_validate_keys_some_missing(clean_env):
    """Test validate_keys when some keys missing."""
    os.environ["SERPAPI_KEY"] = "key1"

    missing = APIKeyManager.validate_keys()

    assert "OPENAI_API_KEY" in missing
    assert "GMAIL_CLIENT_ID" in missing


def test_api_key_manager_validate_keys_category(clean_env):
    """Test validate_keys for specific category."""
    os.environ["OPENAI_API_KEY"] = "key"

    missing = APIKeyManager.validate_keys("media_generation")

    assert missing == []


def test_api_key_manager_validate_keys_category_missing(clean_env):
    """Test validate_keys for category with missing keys."""
    missing = APIKeyManager.validate_keys("search")

    assert "SERPAPI_KEY" in missing


def test_api_key_manager_validate_keys_unknown_category(clean_env):
    """Test validate_keys with unknown category."""
    missing = APIKeyManager.validate_keys("unknown_category")

    assert missing == []


def test_api_key_manager_mask_key():
    """Test masking API key."""
    key = "sk-proj-abcdefghijklmnopqrstuvwxyz"

    masked = APIKeyManager.mask_key(key)

    assert masked == "sk-...wxyz"
    assert "abcdefgh" not in masked


def test_api_key_manager_mask_key_custom_visible():
    """Test masking with custom visible chars."""
    key = "test_key_12345"

    masked = APIKeyManager.mask_key(key, visible_chars=2)

    assert masked == "tes...45"


def test_api_key_manager_mask_key_short():
    """Test masking very short key."""
    key = "abc"

    masked = APIKeyManager.mask_key(key)

    assert masked == "***"


def test_api_key_manager_mask_key_empty():
    """Test masking empty key."""
    masked = APIKeyManager.mask_key("")

    assert masked == "***"


def test_api_key_manager_mask_key_none():
    """Test masking None key."""
    masked = APIKeyManager.mask_key(None)

    assert masked == "***"


# Test InputValidator

def test_input_validator_validate_pattern_email_valid():
    """Test email pattern validation with valid email."""
    assert InputValidator.validate_pattern("test@example.com", "email") is True


def test_input_validator_validate_pattern_email_invalid():
    """Test email pattern validation with invalid email."""
    assert InputValidator.validate_pattern("not-an-email", "email") is False


def test_input_validator_validate_pattern_url_valid():
    """Test URL pattern validation with valid URL."""
    assert InputValidator.validate_pattern("https://example.com", "url") is True
    assert InputValidator.validate_pattern("http://example.com", "url") is True


def test_input_validator_validate_pattern_url_invalid():
    """Test URL pattern validation with invalid URL."""
    assert InputValidator.validate_pattern("not a url", "url") is False


def test_input_validator_validate_pattern_phone_valid():
    """Test phone pattern validation."""
    assert InputValidator.validate_pattern("1234567890", "phone") is True
    assert InputValidator.validate_pattern("+11234567890", "phone") is True


def test_input_validator_validate_pattern_alpha():
    """Test alpha pattern validation."""
    assert InputValidator.validate_pattern("abcABC", "alpha") is True
    assert InputValidator.validate_pattern("abc123", "alpha") is False


def test_input_validator_validate_pattern_alphanumeric():
    """Test alphanumeric pattern validation."""
    assert InputValidator.validate_pattern("abc123", "alphanumeric") is True
    assert InputValidator.validate_pattern("abc-123", "alphanumeric") is False


def test_input_validator_validate_pattern_unknown():
    """Test validation with unknown pattern."""
    assert InputValidator.validate_pattern("test", "unknown") is False


def test_input_validator_sanitize_string():
    """Test string sanitization."""
    result = InputValidator.sanitize_string("  hello world  ")

    assert result == "hello world"


def test_input_validator_sanitize_string_remove_null():
    """Test sanitization removes null bytes."""
    result = InputValidator.sanitize_string("hello\x00world")

    assert result == "helloworld"


def test_input_validator_sanitize_string_max_length():
    """Test sanitization with max length."""
    with pytest.raises(ValidationError) as exc_info:
        InputValidator.sanitize_string("hello world", max_length=5)

    assert "Input too long" in str(exc_info.value)


def test_input_validator_sanitize_string_not_string():
    """Test sanitization with non-string input."""
    with pytest.raises(ValidationError) as exc_info:
        InputValidator.sanitize_string(123)

    assert "Input must be a string" in str(exc_info.value)


def test_input_validator_validate_url_valid():
    """Test URL validation with valid URL."""
    result = InputValidator.validate_url("https://example.com")

    assert result == "https://example.com"


def test_input_validator_validate_url_empty():
    """Test URL validation with empty URL."""
    with pytest.raises(ValidationError) as exc_info:
        InputValidator.validate_url("")

    assert "URL cannot be empty" in str(exc_info.value)


def test_input_validator_validate_url_invalid_scheme():
    """Test URL validation with invalid scheme."""
    with pytest.raises(ValidationError) as exc_info:
        InputValidator.validate_url("ftp://example.com")

    assert "URL must start with" in str(exc_info.value)


def test_input_validator_validate_url_custom_schemes():
    """Test URL validation with custom allowed schemes."""
    result = InputValidator.validate_url(
        "ftp://example.com",
        allowed_schemes=["ftp"]
    )

    assert result == "ftp://example.com"


def test_input_validator_validate_url_invalid_format():
    """Test URL validation with malformed URL."""
    with pytest.raises(ValidationError) as exc_info:
        InputValidator.validate_url("http://")

    assert "Invalid URL format" in str(exc_info.value)


def test_input_validator_validate_file_path():
    """Test file path validation."""
    result = InputValidator.validate_file_path("documents/file.pdf")

    assert result == "documents/file.pdf"


def test_input_validator_validate_file_path_traversal():
    """Test file path validation detects traversal."""
    with pytest.raises(SecurityError) as exc_info:
        InputValidator.validate_file_path("../etc/passwd")

    assert "Path traversal detected" in str(exc_info.value)


def test_input_validator_validate_file_path_absolute():
    """Test file path validation rejects absolute paths."""
    with pytest.raises(SecurityError) as exc_info:
        InputValidator.validate_file_path("/etc/passwd")

    assert "Path traversal detected" in str(exc_info.value)


def test_input_validator_validate_file_path_allowed_extension():
    """Test file path validation with allowed extensions."""
    result = InputValidator.validate_file_path(
        "file.pdf",
        allowed_extensions=["pdf", "txt"]
    )

    assert result == "file.pdf"


def test_input_validator_validate_file_path_disallowed_extension():
    """Test file path validation with disallowed extension."""
    with pytest.raises(ValidationError) as exc_info:
        InputValidator.validate_file_path(
            "file.exe",
            allowed_extensions=["pdf", "txt"]
        )

    assert "File extension .exe not allowed" in str(exc_info.value)


# Test RateLimiter

def test_rate_limiter_init(rate_limiter):
    """Test RateLimiter initialization."""
    assert hasattr(rate_limiter, '_buckets')
    assert hasattr(rate_limiter, '_limits')
    assert rate_limiter._limits["default"] == 60


def test_rate_limiter_set_limit(rate_limiter):
    """Test setting custom rate limit."""
    rate_limiter.set_limit("custom", 100)

    assert rate_limiter._limits["custom"] == 100


def test_rate_limiter_check_rate_limit_first_request(rate_limiter):
    """Test rate limit check for first request."""
    # Should not raise
    rate_limiter.check_rate_limit("user1", "default", cost=1)


def test_rate_limiter_check_rate_limit_within_limit(rate_limiter):
    """Test rate limit check within limit."""
    # Make several requests within limit
    for _ in range(5):
        rate_limiter.check_rate_limit("user1", "default", cost=1)


def test_rate_limiter_check_rate_limit_exceeded(rate_limiter):
    """Test rate limit check when limit exceeded."""
    rate_limiter.set_limit("test", 10)

    # Consume all tokens
    rate_limiter.check_rate_limit("user1", "test", cost=10)

    # Next request should fail
    with pytest.raises(RateLimitError) as exc_info:
        rate_limiter.check_rate_limit("user1", "test", cost=1)

    assert "Rate limit exceeded" in str(exc_info.value)
    assert exc_info.value.retry_after > 0


def test_rate_limiter_check_rate_limit_different_users(rate_limiter):
    """Test rate limiting is per-user."""
    rate_limiter.set_limit("test", 5)

    # User 1 uses all tokens
    rate_limiter.check_rate_limit("user1", "test", cost=5)

    # User 2 should still have tokens
    rate_limiter.check_rate_limit("user2", "test", cost=1)


def test_rate_limiter_check_rate_limit_different_types(rate_limiter):
    """Test different limit types."""
    rate_limiter.set_limit("type1", 10)
    rate_limiter.set_limit("type2", 20)

    # Use all tokens for type1
    rate_limiter.check_rate_limit("user1", "type1", cost=10)

    # type2 should still work
    rate_limiter.check_rate_limit("user1", "type2", cost=1)


def test_rate_limiter_token_refill(rate_limiter):
    """Test that tokens refill over time."""
    rate_limiter.set_limit("test", 60)  # 60 per minute = 1 per second

    # Consume tokens
    rate_limiter.check_rate_limit("user1", "test", cost=5)

    # Wait for refill
    time.sleep(1.1)

    # Should have refilled ~1 token
    rate_limiter.check_rate_limit("user1", "test", cost=1)


def test_rate_limiter_get_remaining(rate_limiter):
    """Test getting remaining tokens."""
    rate_limiter.set_limit("test", 100)

    remaining = rate_limiter.get_remaining("user1", "test")

    assert remaining == 100


def test_rate_limiter_get_remaining_after_consumption(rate_limiter):
    """Test remaining tokens after consumption."""
    rate_limiter.set_limit("test", 100)

    rate_limiter.check_rate_limit("user1", "test", cost=30)
    remaining = rate_limiter.get_remaining("user1", "test")

    assert remaining == 70


def test_rate_limiter_get_remaining_new_key(rate_limiter):
    """Test getting remaining for new key."""
    rate_limiter.set_limit("test", 50)

    remaining = rate_limiter.get_remaining("new_user", "test")

    assert remaining == 50


# Test Global Functions

def test_get_rate_limiter():
    """Test getting global rate limiter."""
    limiter = get_rate_limiter()

    assert isinstance(limiter, RateLimiter)


def test_get_rate_limiter_singleton():
    """Test that get_rate_limiter returns same instance."""
    limiter1 = get_rate_limiter()
    limiter2 = get_rate_limiter()

    assert limiter1 is limiter2


# Test Decorators

def test_require_api_key_decorator(clean_env):
    """Test require_api_key decorator."""
    os.environ["TEST_KEY"] = "value"

    @require_api_key("TEST_KEY")
    def test_func():
        return "success"

    result = test_func()

    assert result == "success"


def test_require_api_key_decorator_missing(clean_env):
    """Test require_api_key decorator with missing key."""
    @require_api_key("MISSING_KEY")
    def test_func():
        return "success"

    with pytest.raises(AuthenticationError):
        test_func()


def test_rate_limit_decorator():
    """Test rate_limit decorator."""
    class TestTool:
        tool_name = "test_tool"

        @rate_limit("default", cost=1)
        def process(self):
            return "success"

    tool = TestTool()
    result = tool.process()

    assert result == "success"


def test_rate_limit_decorator_exceeded():
    """Test rate_limit decorator when limit exceeded."""
    limiter = get_rate_limiter()
    limiter.set_limit("test_limit", 1)

    class TestTool:
        tool_name = "test_tool_limited"

        @rate_limit("test_limit", cost=2)
        def process(self):
            return "success"

    tool = TestTool()

    # First call should fail (cost=2 but limit=1)
    with pytest.raises(RateLimitError):
        tool.process()


# Test Utility Functions

def test_hash_user_id():
    """Test user ID hashing."""
    user_id = "user123"

    hashed = hash_user_id(user_id)

    assert isinstance(hashed, str)
    assert len(hashed) == 16
    assert hashed != user_id


def test_hash_user_id_consistent():
    """Test user ID hashing is consistent."""
    user_id = "user123"

    hash1 = hash_user_id(user_id)
    hash2 = hash_user_id(user_id)

    assert hash1 == hash2


def test_hash_user_id_different_inputs():
    """Test different user IDs produce different hashes."""
    hash1 = hash_user_id("user1")
    hash2 = hash_user_id("user2")

    assert hash1 != hash2


def test_validate_api_keys(clean_env):
    """Test global validate_api_keys function."""
    missing = validate_api_keys()

    assert isinstance(missing, list)
    assert len(missing) > 0  # Should find missing keys


def test_validate_api_keys_category(clean_env):
    """Test validate_api_keys with category."""
    os.environ["SERPAPI_KEY"] = "key"

    missing = validate_api_keys("search")

    assert missing == []


# Test Edge Cases

def test_rate_limiter_high_cost(rate_limiter):
    """Test rate limiter with high cost request."""
    rate_limiter.set_limit("test", 100)

    # Should work
    rate_limiter.check_rate_limit("user1", "test", cost=100)

    # Should fail
    with pytest.raises(RateLimitError):
        rate_limiter.check_rate_limit("user1", "test", cost=1)


def test_rate_limiter_zero_cost(rate_limiter):
    """Test rate limiter with zero cost."""
    # Should not consume tokens
    rate_limiter.check_rate_limit("user1", "default", cost=0)

    remaining = rate_limiter.get_remaining("user1", "default")
    assert remaining == 60  # Default limit


def test_input_validator_patterns_coverage():
    """Test all patterns in PATTERNS dict."""
    patterns = {
        "email": ("test@example.com", True),
        "url": ("http://example.com", True),
        "domain": ("example.com", True),
        "phone": ("1234567890", True),
        "alpha": ("abcABC", True),
        "alphanumeric": ("abc123", True)
    }

    for pattern_name, (value, expected) in patterns.items():
        assert InputValidator.validate_pattern(value, pattern_name) == expected


def test_api_key_manager_required_keys_structure():
    """Test REQUIRED_KEYS dictionary structure."""
    assert "search" in APIKeyManager.REQUIRED_KEYS
    assert "media_generation" in APIKeyManager.REQUIRED_KEYS
    assert "communication" in APIKeyManager.REQUIRED_KEYS
    assert "storage" in APIKeyManager.REQUIRED_KEYS

    for category, keys in APIKeyManager.REQUIRED_KEYS.items():
        assert isinstance(keys, list)
        assert len(keys) > 0


def test_rate_limiter_concurrent_access(rate_limiter):
    """Test rate limiter with concurrent access (thread safety)."""
    import threading

    def make_request():
        try:
            rate_limiter.check_rate_limit("user1", "default", cost=1)
        except RateLimitError:
            pass

    threads = [threading.Thread(target=make_request) for _ in range(10)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    # Should complete without errors


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
