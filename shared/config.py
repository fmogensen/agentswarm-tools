"""
Centralized configuration management for AgentSwarm Tools.

This module provides Pydantic BaseSettings classes for loading and validating
configuration from environment variables. Settings are grouped by category
for better organization and type safety.

Usage:
    from shared.config import config

    # Access settings
    api_key = config.search.serpapi_key
    mock_mode = config.features.use_mock_apis

    # Validate required settings
    config.validate_required("search.serpapi_key", "search.google_search_api_key")
"""

from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class FeatureFlagsConfig(BaseSettings):
    """Feature flags for controlling application behavior."""

    use_mock_apis: bool = Field(
        default=False,
        description="Enable mock mode for testing without real API calls",
    )
    analytics_enabled: bool = Field(
        default=True,
        description="Enable/disable analytics tracking",
    )
    analytics_backend: str = Field(
        default="file",
        description="Analytics backend type (file, database, etc.)",
    )
    analytics_log_dir: str = Field(
        default=".analytics",
        description="Directory for analytics logs",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class SearchAPIConfig(BaseSettings):
    """Search API configuration."""

    serpapi_key: Optional[str] = Field(
        default=None,
        description="SerpAPI key for image search",
    )
    google_search_api_key: Optional[str] = Field(
        default=None,
        description="Google Custom Search API key",
    )
    google_search_engine_id: Optional[str] = Field(
        default=None,
        description="Google Custom Search Engine ID",
    )
    google_shopping_api_key: Optional[str] = Field(
        default=None,
        description="Google Shopping API key",
    )
    google_shopping_engine_id: Optional[str] = Field(
        default=None,
        description="Google Shopping Engine ID",
    )
    youtube_api_key: Optional[str] = Field(
        default=None,
        description="YouTube Data API key",
    )
    amazon_api_key: Optional[str] = Field(
        default=None,
        description="Amazon Product API key",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class GoogleServicesConfig(BaseSettings):
    """Google Services configuration."""

    google_service_account_json: Optional[str] = Field(
        default=None,
        description="Google Service Account JSON (for Gmail)",
    )
    google_service_account_file: Optional[str] = Field(
        default=None,
        description="Google Service Account file path",
    )
    google_calendar_service_account_file: Optional[str] = Field(
        default=None,
        description="Google Calendar Service Account file path",
    )
    google_maps_api_key: Optional[str] = Field(
        default=None,
        description="Google Maps API key",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class MicrosoftServicesConfig(BaseSettings):
    """Microsoft Services configuration."""

    ms_graph_token: Optional[str] = Field(
        default=None,
        description="Microsoft Graph API token (for OneDrive)",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class WorkspaceConfig(BaseSettings):
    """Workspace integrations configuration."""

    notion_api_key: Optional[str] = Field(
        default=None,
        description="Notion API key",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class AIConfig(BaseSettings):
    """AI/LLM API configuration."""

    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    database_url: Optional[str] = Field(
        default=None,
        description="PostgreSQL Database URL",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class RedisConfig(BaseSettings):
    """Redis configuration."""

    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection URL",
    )
    redis_host: str = Field(
        default="localhost",
        description="Redis host",
    )
    redis_port: int = Field(
        default=6379,
        description="Redis port",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class WorkerConfig(BaseSettings):
    """Worker configuration."""

    autonomous_mode: bool = Field(
        default=True,
        description="Enable autonomous mode for workers",
    )
    auto_fix: bool = Field(
        default=True,
        description="Enable automatic error fixing",
    )
    auto_merge: bool = Field(
        default=True,
        description="Enable automatic PR merging",
    )
    check_interval: int = Field(
        default=60,
        description="Check interval in seconds",
    )
    retry_attempts: int = Field(
        default=5,
        description="Number of retry attempts for failed operations",
    )
    tools_to_develop: int = Field(
        default=61,
        description="Total number of tools to develop",
    )
    min_test_coverage: int = Field(
        default=80,
        description="Minimum test coverage percentage",
    )
    auto_document: bool = Field(
        default=True,
        description="Enable automatic documentation generation",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class TeamConfig(BaseSettings):
    """Team configuration."""

    team_id: str = Field(
        default="team1",
        description="Team identifier",
    )
    team_name: str = Field(
        default="development",
        description="Team name",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class DashboardConfig(BaseSettings):
    """Dashboard configuration."""

    dashboard_port: int = Field(
        default=8080,
        description="Dashboard server port",
    )
    dashboard_auto_refresh: int = Field(
        default=30,
        description="Dashboard auto-refresh interval in seconds",
    )

    model_config = {
        "env_prefix": "",
        "extra": "ignore",
    }


class AppConfig(BaseSettings):
    """
    Main application configuration.

    Aggregates all configuration categories into a single entry point.
    Access settings via category attributes.

    Example:
        config = AppConfig()
        api_key = config.search.serpapi_key
        mock_mode = config.features.use_mock_apis
    """

    features: FeatureFlagsConfig = Field(default_factory=FeatureFlagsConfig)
    search: SearchAPIConfig = Field(default_factory=SearchAPIConfig)
    google: GoogleServicesConfig = Field(default_factory=GoogleServicesConfig)
    microsoft: MicrosoftServicesConfig = Field(default_factory=MicrosoftServicesConfig)
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)
    ai: AIConfig = Field(default_factory=AIConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    worker: WorkerConfig = Field(default_factory=WorkerConfig)
    team: TeamConfig = Field(default_factory=TeamConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)

    model_config = {
        "extra": "ignore",
    }

    def validate_required(self, *keys: str) -> None:
        """
        Validate that required config keys are set.

        Args:
            *keys: Dot-notation keys to validate (e.g., "search.serpapi_key")

        Raises:
            ValueError: If any required keys are missing or empty

        Example:
            config.validate_required("search.serpapi_key", "ai.openai_api_key")
        """
        missing = []
        for key in keys:
            value = self._get_nested_value(key)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(key)

        if missing:
            raise ValueError(f"Missing required configuration: {missing}")

    def _get_nested_value(self, key: str):
        """
        Get a nested configuration value using dot notation.

        Args:
            key: Dot-notation key (e.g., "search.serpapi_key")

        Returns:
            The configuration value or None if not found
        """
        parts = key.split(".")
        obj = self
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return None
        return obj

    def get(self, key: str, default=None):
        """
        Get a configuration value with optional default.

        Args:
            key: Dot-notation key (e.g., "search.serpapi_key")
            default: Default value if key is not found

        Returns:
            The configuration value or default
        """
        value = self._get_nested_value(key)
        return value if value is not None else default

    def is_mock_mode(self) -> bool:
        """Check if mock mode is enabled."""
        return self.features.use_mock_apis

    def list_configured_apis(self) -> List[str]:
        """
        List all APIs that have valid configuration.

        Returns:
            List of configured API names
        """
        configured = []

        # Search APIs
        if self.search.serpapi_key:
            configured.append("serpapi")
        if self.search.google_search_api_key:
            configured.append("google_search")
        if self.search.youtube_api_key:
            configured.append("youtube")
        if self.search.amazon_api_key:
            configured.append("amazon")

        # Google Services
        if self.google.google_maps_api_key:
            configured.append("google_maps")
        if self.google.google_service_account_file:
            configured.append("google_service_account")

        # Microsoft
        if self.microsoft.ms_graph_token:
            configured.append("microsoft_graph")

        # Workspace
        if self.workspace.notion_api_key:
            configured.append("notion")

        # AI
        if self.ai.openai_api_key:
            configured.append("openai")

        # Database
        if self.database.database_url:
            configured.append("database")
        if self.redis.redis_url:
            configured.append("redis")

        return configured


# Singleton instance for application-wide use
config = AppConfig()


if __name__ == "__main__":
    import os

    print("Testing Configuration Management System...")
    print("=" * 60)

    # Test with mock environment variables
    os.environ["USE_MOCK_APIS"] = "true"
    os.environ["ANALYTICS_ENABLED"] = "false"
    os.environ["SERPAPI_KEY"] = "test_serpapi_key"
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"

    # Create fresh config to pick up test env vars
    test_config = AppConfig()

    # Test feature flags
    print("\n1. Feature Flags:")
    print(f"   use_mock_apis: {test_config.features.use_mock_apis}")
    print(f"   analytics_enabled: {test_config.features.analytics_enabled}")
    assert test_config.features.use_mock_apis == True
    assert test_config.features.analytics_enabled == False
    print("   [PASS] Feature flags loaded correctly")

    # Test search config
    print("\n2. Search API Config:")
    print(
        f"   serpapi_key: {test_config.search.serpapi_key[:10]}..."
        if test_config.search.serpapi_key
        else "   serpapi_key: None"
    )
    assert test_config.search.serpapi_key == "test_serpapi_key"
    print("   [PASS] Search config loaded correctly")

    # Test AI config
    print("\n3. AI Config:")
    print(
        f"   openai_api_key: {test_config.ai.openai_api_key[:10]}..."
        if test_config.ai.openai_api_key
        else "   openai_api_key: None"
    )
    assert test_config.ai.openai_api_key == "test_openai_key"
    print("   [PASS] AI config loaded correctly")

    # Test database config
    print("\n4. Database Config:")
    print(
        f"   database_url: {test_config.database.database_url[:30]}..."
        if test_config.database.database_url
        else "   database_url: None"
    )
    assert test_config.database.database_url is not None
    print("   [PASS] Database config loaded correctly")

    # Test nested value access
    print("\n5. Nested Value Access:")
    value = test_config.get("search.serpapi_key")
    print(
        f"   get('search.serpapi_key'): {value[:10]}..."
        if value
        else "   get('search.serpapi_key'): None"
    )
    assert value == "test_serpapi_key"
    print("   [PASS] Nested access works correctly")

    # Test validation
    print("\n6. Validation:")
    try:
        test_config.validate_required("search.serpapi_key", "ai.openai_api_key")
        print("   [PASS] Valid keys passed validation")
    except ValueError as e:
        print(f"   [FAIL] Unexpected validation error: {e}")

    try:
        test_config.validate_required("search.serpapi_key", "search.amazon_api_key")
        print("   [FAIL] Should have raised ValueError for missing key")
    except ValueError as e:
        print(f"   [PASS] Correctly raised error for missing key")

    # Test mock mode helper
    print("\n7. Mock Mode Helper:")
    print(f"   is_mock_mode(): {test_config.is_mock_mode()}")
    assert test_config.is_mock_mode() == True
    print("   [PASS] Mock mode helper works correctly")

    # Test list configured APIs
    print("\n8. List Configured APIs:")
    configured = test_config.list_configured_apis()
    print(f"   Configured APIs: {configured}")
    assert "serpapi" in configured
    assert "openai" in configured
    assert "database" in configured
    print("   [PASS] API listing works correctly")

    # Test default values
    print("\n9. Default Values:")
    print(f"   redis_host: {test_config.redis.redis_host}")
    print(f"   redis_port: {test_config.redis.redis_port}")
    print(f"   check_interval: {test_config.worker.check_interval}")
    assert test_config.redis.redis_host == "localhost"
    assert test_config.redis.redis_port == 6379
    assert test_config.worker.check_interval == 60
    print("   [PASS] Default values loaded correctly")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("Configuration management system is working correctly.")
