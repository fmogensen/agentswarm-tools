"""
Unit tests for LiteLLM client integration.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from shared.llm_client import (
    LLMClient,
    get_llm_client,
    reset_client,
    LLMResponse,
    TaskType,
    ModelConfig,
    CostTrackingRecord,
)
from shared.errors import APIError, RateLimitError, AuthenticationError


class TestModelConfig:
    """Test ModelConfig dataclass."""

    def test_model_config_creation(self):
        """Test creating a model config."""
        config = ModelConfig(
            name="gpt-3.5-turbo",
            provider="openai",
            task_type=TaskType.CHAT_COMPLETION,
            cost_per_1k_input_tokens=0.0005,
            cost_per_1k_output_tokens=0.0015,
            max_tokens=4096,
        )

        assert config.name == "gpt-3.5-turbo"
        assert config.provider == "openai"
        assert config.task_type == TaskType.CHAT_COMPLETION
        assert config.cost_per_1k_input_tokens == 0.0005


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_llm_response_creation(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Hello, world!",
            model="gpt-3.5-turbo",
            provider="openai",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            cost=0.00003,
            latency_ms=150.0,
        )

        assert response.content == "Hello, world!"
        assert response.model == "gpt-3.5-turbo"
        assert response.cost == 0.00003
        assert response.usage["total_tokens"] == 15


class TestCostTrackingRecord:
    """Test CostTrackingRecord dataclass."""

    def test_cost_record_creation(self):
        """Test creating a cost tracking record."""
        record = CostTrackingRecord(
            timestamp=datetime.utcnow(),
            model="gpt-4",
            provider="openai",
            task_type=TaskType.CHAT_COMPLETION,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            cost=0.0045,
            latency_ms=500.0,
            success=True,
        )

        assert record.model == "gpt-4"
        assert record.total_tokens == 150
        assert record.cost == 0.0045
        assert record.success is True


@pytest.fixture
def mock_litellm():
    """Mock LiteLLM library."""
    with patch("shared.llm_client.LITELLM_AVAILABLE", True):
        with patch("shared.llm_client.litellm") as mock_lib:
            mock_lib.set_verbose = False
            mock_lib.drop_params = True
            yield mock_lib


@pytest.fixture
def llm_client(mock_litellm):
    """Create LLM client for testing."""
    reset_client()
    client = LLMClient(enable_fallback=True, enable_cost_tracking=True)
    return client


class TestLLMClient:
    """Test LLMClient class."""

    def test_client_initialization(self, llm_client):
        """Test client initialization."""
        assert llm_client.enable_fallback is True
        assert llm_client.enable_cost_tracking is True
        assert llm_client.max_retries == 3
        assert llm_client.timeout == 60

    def test_calculate_cost_chat(self, llm_client):
        """Test cost calculation for chat completion."""
        cost = llm_client._calculate_cost(
            model="gpt-3.5-turbo",
            task_type=TaskType.CHAT_COMPLETION,
            input_tokens=1000,
            output_tokens=500,
        )

        # 1000 * 0.0005/1000 + 500 * 0.0015/1000 = 0.0005 + 0.00075 = 0.00125
        assert cost == pytest.approx(0.00125, rel=1e-6)

    def test_calculate_cost_image(self, llm_client):
        """Test cost calculation for image generation."""
        cost = llm_client._calculate_cost(
            model="dall-e-3", task_type=TaskType.IMAGE_GENERATION, images_generated=1
        )

        # dall-e-3 standard: $0.04/image
        assert cost == 0.04

    def test_get_provider(self, llm_client):
        """Test getting provider for a model."""
        provider = llm_client._get_provider("gpt-4")
        assert provider == "openai"

        provider = llm_client._get_provider("claude-3-opus-20240229")
        assert provider == "anthropic"

        provider = llm_client._get_provider("unknown-model")
        assert provider == "unknown"

    @patch("shared.llm_client.completion")
    def test_chat_completion_success(self, mock_completion, llm_client):
        """Test successful chat completion."""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello!"
        mock_response.usage = Mock()
        mock_response.usage.__dict__ = {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        }
        mock_completion.return_value = mock_response

        # Call chat completion
        response = llm_client.chat_completion(
            messages=[{"role": "user", "content": "Hi"}], model="gpt-3.5-turbo"
        )

        # Verify response
        assert isinstance(response, LLMResponse)
        assert response.content == "Hello!"
        assert response.model == "gpt-3.5-turbo"
        assert response.provider == "openai"
        assert response.cost > 0

        # Verify cost tracking
        assert len(llm_client.cost_records) == 1
        assert llm_client.cost_records[0].model == "gpt-3.5-turbo"
        assert llm_client.cost_records[0].success is True

    @patch("shared.llm_client.completion")
    def test_chat_completion_with_fallback(self, mock_completion, llm_client):
        """Test chat completion with fallback on error."""
        # First call fails, second succeeds
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello from fallback!"
        mock_response.usage = Mock()
        mock_response.usage.__dict__ = {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        }

        from shared.llm_client import LiteLLMRateLimitError

        mock_completion.side_effect = [
            LiteLLMRateLimitError("Rate limit exceeded"),
            mock_response,
        ]

        # Call with fallback
        response = llm_client.chat_completion(
            messages=[{"role": "user", "content": "Hi"}],
            model="gpt-4",
            fallback_models=["gpt-3.5-turbo"],
        )

        # Should succeed with fallback model
        assert response.content == "Hello from fallback!"
        assert response.metadata["fallback_used"] is True

    @patch("shared.llm_client.image_generation")
    def test_generate_image_success(self, mock_image_gen, llm_client):
        """Test successful image generation."""
        # Mock response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].url = "https://example.com/image.png"
        mock_image_gen.return_value = mock_response

        # Generate image
        response = llm_client.generate_image(
            prompt="a beautiful sunset", model="dall-e-3", size="1024x1024"
        )

        # Verify response
        assert isinstance(response, LLMResponse)
        assert response.content == "https://example.com/image.png"
        assert response.model == "dall-e-3"
        assert response.cost == 0.04  # dall-e-3 standard cost

    def test_get_total_cost(self, llm_client):
        """Test getting total cost."""
        llm_client._record_cost(
            model="gpt-3.5-turbo",
            task_type=TaskType.CHAT_COMPLETION,
            input_tokens=1000,
            output_tokens=500,
            cost=0.00125,
        )
        llm_client._record_cost(
            model="gpt-4",
            task_type=TaskType.CHAT_COMPLETION,
            input_tokens=500,
            output_tokens=250,
            cost=0.025,
        )

        total = llm_client.get_total_cost()
        assert total == pytest.approx(0.02625, rel=1e-6)

    def test_get_cost_by_model(self, llm_client):
        """Test getting costs grouped by model."""
        llm_client._record_cost(
            model="gpt-3.5-turbo",
            task_type=TaskType.CHAT_COMPLETION,
            cost=0.001,
        )
        llm_client._record_cost(
            model="gpt-3.5-turbo",
            task_type=TaskType.CHAT_COMPLETION,
            cost=0.002,
        )
        llm_client._record_cost(
            model="gpt-4",
            task_type=TaskType.CHAT_COMPLETION,
            cost=0.05,
        )

        costs = llm_client.get_cost_by_model()
        assert costs["gpt-3.5-turbo"] == pytest.approx(0.003)
        assert costs["gpt-4"] == pytest.approx(0.05)

    def test_get_cost_by_provider(self, llm_client):
        """Test getting costs grouped by provider."""
        llm_client._record_cost(
            model="gpt-3.5-turbo",
            task_type=TaskType.CHAT_COMPLETION,
            cost=0.001,
        )
        llm_client._record_cost(
            model="gpt-4",
            task_type=TaskType.CHAT_COMPLETION,
            cost=0.05,
        )
        llm_client._record_cost(
            model="claude-3-haiku-20240307",
            task_type=TaskType.CHAT_COMPLETION,
            cost=0.0001,
        )

        costs = llm_client.get_cost_by_provider()
        assert costs["openai"] == pytest.approx(0.051)
        assert costs["anthropic"] == pytest.approx(0.0001)

    def test_export_cost_records(self, llm_client, tmp_path):
        """Test exporting cost records to JSON."""
        llm_client._record_cost(
            model="gpt-3.5-turbo",
            task_type=TaskType.CHAT_COMPLETION,
            input_tokens=100,
            output_tokens=50,
            cost=0.0001,
            latency_ms=150.0,
        )

        # Export to temp file
        filepath = tmp_path / "costs.json"
        llm_client.export_cost_records(str(filepath))

        # Verify file exists and has content
        assert filepath.exists()
        import json

        with open(filepath) as f:
            records = json.load(f)

        assert len(records) == 1
        assert records[0]["model"] == "gpt-3.5-turbo"
        assert records[0]["cost"] == 0.0001


class TestGlobalClient:
    """Test global client singleton."""

    def test_get_llm_client(self, mock_litellm):
        """Test getting global client."""
        reset_client()
        client1 = get_llm_client()
        client2 = get_llm_client()

        # Should return same instance
        assert client1 is client2

    def test_reset_client(self, mock_litellm):
        """Test resetting global client."""
        client1 = get_llm_client()
        reset_client()
        client2 = get_llm_client()

        # Should return different instance
        assert client1 is not client2

    def test_get_client_with_env_config(self, mock_litellm):
        """Test client respects environment configuration."""
        reset_client()

        with patch.dict(os.environ, {"LITELLM_FALLBACK_ENABLED": "false"}):
            client = get_llm_client()
            assert client.enable_fallback is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
