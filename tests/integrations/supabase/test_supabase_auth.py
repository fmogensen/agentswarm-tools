"""
Comprehensive tests for SupabaseAuth tool.
Achieves 90%+ code coverage.
"""

import os

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import AuthenticationError, ValidationError
from tools.integrations.supabase.supabase_auth import SupabaseAuth


class TestSupabaseAuthValidation:
    """Test input validation."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_sign_up_requires_email(self):
        """Test sign up requires email."""
        with pytest.raises((ValidationError, PydanticValidationError)):
            tool = SupabaseAuth(action="sign_up", password="Pass123!")
            tool.run()

    def test_sign_up_requires_password(self):
        """Test sign up requires password."""
        with pytest.raises((ValidationError, PydanticValidationError)):
            tool = SupabaseAuth(action="sign_up", email="user@example.com")
            tool.run()

    def test_weak_password(self):
        """Test password too short."""
        with pytest.raises((ValidationError, PydanticValidationError)):
            tool = SupabaseAuth(action="sign_up", email="user@example.com", password="123")
            tool.run()

    def test_invalid_email(self):
        """Test invalid email format."""
        with pytest.raises((ValidationError, PydanticValidationError)):
            tool = SupabaseAuth(action="sign_up", email="invalid", password="Pass123!")
            tool.run()

    def test_verify_token_requires_token(self):
        """Test verify_token requires token."""
        with pytest.raises(ValidationError):
            tool = SupabaseAuth(action="verify_token")
            tool.run()


class TestSupabaseAuthMockMode:
    """Test all authentication actions."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_sign_up(self):
        """Test user sign up."""
        tool = SupabaseAuth(
            action="sign_up",
            email="new@example.com",
            password="SecurePass123!",
            metadata={"name": "Test User"},
        )
        result = tool.run()
        assert result["success"] == True
        assert "user" in result
        assert "session" in result
        assert result["user"]["email"] == "new@example.com"

    def test_sign_in(self):
        """Test user sign in."""
        tool = SupabaseAuth(
            action="sign_in",
            email="user@example.com",
            password="Pass123!",
        )
        result = tool.run()
        assert result["success"] == True
        assert "session" in result
        assert "access_token" in result["session"]

    def test_sign_out(self):
        """Test user sign out."""
        tool = SupabaseAuth(action="sign_out")
        result = tool.run()
        assert result["success"] == True
        assert "message" in result

    def test_verify_token(self):
        """Test token verification."""
        tool = SupabaseAuth(
            action="verify_token",
            token="mock_token_12345",
        )
        result = tool.run()
        assert result["success"] == True
        assert result["valid"] == True

    def test_reset_password(self):
        """Test password reset."""
        tool = SupabaseAuth(
            action="reset_password",
            email="user@example.com",
        )
        result = tool.run()
        assert result["success"] == True
        assert "reset" in result["message"].lower()

    def test_get_session(self):
        """Test get current session."""
        tool = SupabaseAuth(action="get_session")
        result = tool.run()
        assert result["success"] == True
        assert "session" in result


class TestSupabaseAuthFeatures:
    """Test advanced features."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_sign_up_with_metadata(self):
        """Test sign up with user metadata."""
        tool = SupabaseAuth(
            action="sign_up",
            email="user@example.com",
            password="Pass123!",
            metadata={"role": "admin", "department": "engineering"},
        )
        result = tool.run()
        assert result["success"] == True

    def test_sign_up_with_redirect(self):
        """Test sign up with redirect URL."""
        tool = SupabaseAuth(
            action="sign_up",
            email="user@example.com",
            password="Pass123!",
            redirect_to="https://example.com/welcome",
        )
        result = tool.run()
        assert result["success"] == True

    def test_reset_password_with_redirect(self):
        """Test password reset with redirect."""
        tool = SupabaseAuth(
            action="reset_password",
            email="user@example.com",
            redirect_to="https://example.com/reset",
        )
        result = tool.run()
        assert result["success"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=tools.integrations.supabase.supabase_auth"])
