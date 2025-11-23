"""
Unit tests for CreateProfile tool
"""

import os

import pytest

from shared.errors import ValidationError

from .create_profile import CreateProfile


@pytest.fixture(autouse=True)
def setup_mock_mode():
    """Enable mock mode for all tests."""
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    os.environ.pop("USE_MOCK_APIS", None)


class TestCreateProfile:
    """Test suite for CreateProfile tool."""

    def test_basic_user_profile(self):
        """Test creating a basic user profile."""
        tool = CreateProfile(name="John Doe", profile_type="user")
        result = tool.run()

        assert result["success"] is True
        assert "profile_id" in result["result"]
        assert result["result"]["name"] == "John Doe"
        assert result["result"]["profile_type"] == "user"
        assert result["result"]["status"] == "active"

    def test_agent_profile_with_attributes(self):
        """Test creating an agent profile with custom attributes."""
        tool = CreateProfile(
            name="DataAnalyst",
            profile_type="agent",
            role="Data analysis specialist",
            attributes={"specialty": "ML", "level": "expert"},
            tags=["AI", "data-science"],
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["profile_type"] == "agent"
        assert result["result"]["role"] == "Data analysis specialist"
        assert result["result"]["attributes"]["specialty"] == "ML"
        assert "AI" in result["result"]["tags"]

    def test_full_profile_with_all_fields(self):
        """Test creating a profile with all optional fields."""
        tool = CreateProfile(
            name="SystemAdmin",
            profile_type="system",
            role="System administrator",
            description="Manages system operations",
            attributes={"permissions": "admin", "level": 5},
            tags=["system", "admin", "ops"],
            metadata={"department": "IT", "location": "HQ"},
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["description"] == "Manages system operations"
        assert result["result"]["metadata"]["department"] == "IT"
        assert len(result["result"]["tags"]) == 3

    def test_empty_name_validation_error(self):
        """Test that empty name raises ValidationError."""
        with pytest.raises(Exception) as exc_info:
            tool = CreateProfile(name="   ", profile_type="user")
            tool.run()

        assert "empty" in str(exc_info.value).lower() or "whitespace" in str(exc_info.value).lower()

    def test_invalid_profile_type(self):
        """Test that invalid profile type raises ValidationError."""
        with pytest.raises(Exception) as exc_info:
            tool = CreateProfile(name="Test", profile_type="invalid_type")
            tool.run()

        assert (
            "profile type" in str(exc_info.value).lower()
            or "invalid" in str(exc_info.value).lower()
        )

    def test_valid_profile_types(self):
        """Test all valid profile types."""
        valid_types = ["user", "agent", "system", "custom"]

        for profile_type in valid_types:
            tool = CreateProfile(name=f"Test_{profile_type}", profile_type=profile_type)
            result = tool.run()

            assert result["success"] is True
            assert result["result"]["profile_type"] == profile_type

    def test_profile_with_complex_attributes(self):
        """Test profile with nested attributes."""
        tool = CreateProfile(
            name="ComplexAgent",
            profile_type="agent",
            attributes={
                "config": {"model": "gpt-4", "temperature": 0.7, "max_tokens": 1000},
                "capabilities": ["search", "analysis", "generation"],
                "limits": {"daily_requests": 1000, "rate_per_minute": 60},
            },
        )
        result = tool.run()

        assert result["success"] is True
        assert "config" in result["result"]["attributes"]
        assert result["result"]["attributes"]["config"]["model"] == "gpt-4"
        assert len(result["result"]["attributes"]["capabilities"]) == 3

    def test_profile_timestamps(self):
        """Test that profile includes creation timestamps."""
        tool = CreateProfile(name="TestUser", profile_type="user")
        result = tool.run()

        assert "created_at" in result["result"]
        assert "updated_at" in result["result"]
        assert result["result"]["created_at"] is not None
        assert result["result"]["updated_at"] is not None

    def test_profile_id_generation(self):
        """Test that unique profile IDs are generated."""
        tool1 = CreateProfile(name="User1", profile_type="user")
        tool2 = CreateProfile(name="User2", profile_type="user")

        result1 = tool1.run()
        result2 = tool2.run()

        # Profile IDs should be unique
        assert result1["result"]["profile_id"] != result2["result"]["profile_id"]

    def test_mock_mode_indicator(self):
        """Test that mock mode is indicated in results."""
        tool = CreateProfile(name="TestUser", profile_type="user")
        result = tool.run()

        # Check for mock mode indicator in metadata
        assert result["metadata"]["mock_mode"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
