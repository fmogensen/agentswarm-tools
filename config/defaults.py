"""
Default configuration values

Default settings for AgentSwarm Tools.
"""

from typing import Any, Dict

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    # API Configuration
    "GENSPARK_API_KEY": "",
    "GENSPARK_API_URL": "https://api.genspark.ai/v1",
    # CLI Settings
    "DEFAULT_OUTPUT_FORMAT": "json",
    "DEFAULT_TABLE_WIDTH": 100,
    "INTERACTIVE_MODE": False,
    # Tool Settings
    "USE_MOCK_APIS": False,
    "TOOL_TIMEOUT": 300,  # seconds
    "MAX_RETRIES": 3,
    # Logging
    "LOG_LEVEL": "INFO",
    "LOG_FILE": None,
    # Cache
    "ENABLE_CACHE": True,
    "CACHE_TTL": 3600,  # seconds
    "CACHE_DIR": "~/.agentswarm/cache",
    # Storage
    "OUTPUT_DIR": "~/.agentswarm/outputs",
    "TEMP_DIR": "~/.agentswarm/temp",
}

# Required API keys
REQUIRED_API_KEYS = [
    "GENSPARK_API_KEY",
]

# Optional API keys (for specific tools)
OPTIONAL_API_KEYS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
]

# Environment variable mappings
ENV_VAR_MAPPING = {
    "GENSPARK_API_KEY": "GENSPARK_API_KEY",
    "GENSPARK_API_URL": "GENSPARK_API_URL",
    "USE_MOCK_APIS": "USE_MOCK_APIS",
}
