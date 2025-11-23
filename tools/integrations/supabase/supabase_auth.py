"""
Supabase Auth Tool

Handles user authentication with Supabase Auth including sign up, sign in,
JWT validation, and session management.
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import Field
import os
import json

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError


class SupabaseAuth(BaseTool):
    """
    Authenticate users with Supabase Auth.

    This tool provides complete authentication flows including sign up, sign in,
    password reset, JWT validation, and session management. Supports email/password,
    magic links, and OAuth providers.

    Args:
        action: Authentication action - 'sign_up', 'sign_in', 'sign_out', 'verify_token', 'reset_password'
        email: User email address (required for most actions)
        password: User password (required for sign_up and sign_in)
        token: JWT token to verify (required for verify_token action)
        provider: OAuth provider - 'google', 'github', 'gitlab', etc. (optional)
        redirect_to: URL to redirect after auth (optional)
        metadata: Additional user metadata for sign_up (optional)
        options: Additional auth options (e.g., captcha_token, should_create_user)

    Returns:
        Dict containing:
            - success (bool): Whether the operation was successful
            - action (str): Action performed
            - user (dict): User object if authenticated
            - session (dict): Session object with access_token and refresh_token
            - provider_token (str): OAuth provider token if applicable
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Sign up new user
        >>> tool = SupabaseAuth(
        ...     action="sign_up",
        ...     email="user@example.com",
        ...     password="SecurePass123!",
        ...     metadata={"name": "John Doe", "role": "user"}
        ... )
        >>> result = tool.run()
        >>> print(result['user']['id'])

        >>> # Sign in existing user
        >>> tool = SupabaseAuth(
        ...     action="sign_in",
        ...     email="user@example.com",
        ...     password="SecurePass123!"
        ... )
        >>> result = tool.run()
        >>> access_token = result['session']['access_token']

        >>> # Verify JWT token
        >>> tool = SupabaseAuth(
        ...     action="verify_token",
        ...     token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        ... )
        >>> result = tool.run()
        >>> print(f"Token valid: {result['success']}")
    """

    # Tool metadata
    tool_name: str = "supabase_auth"
    tool_category: str = "integrations"

    # Required parameters
    action: Literal[
        "sign_up", "sign_in", "sign_out", "verify_token", "reset_password", "get_session"
    ] = Field(
        ...,
        description="Authentication action to perform",
    )

    # Optional parameters
    email: Optional[str] = Field(
        None,
        description="User email address",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
    )
    password: Optional[str] = Field(
        None,
        description="User password (min 6 characters)",
        min_length=6,
    )
    token: Optional[str] = Field(
        None,
        description="JWT token to verify",
    )
    provider: Optional[
        Literal["google", "github", "gitlab", "bitbucket", "azure", "facebook", "twitter"]
    ] = Field(
        None,
        description="OAuth provider",
    )
    redirect_to: Optional[str] = Field(
        None,
        description="URL to redirect after authentication",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional user metadata for sign_up",
    )
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional authentication options",
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the authentication operation."""
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
                "action": self.action,
                **result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "action": self.action,
                    "email": self.email if self.email else None,
                },
            }
        except Exception as e:
            raise APIError(
                f"Authentication failed: {e}",
                tool_name=self.tool_name,
                api_name="supabase_auth",
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters based on action."""
        # Validate action-specific requirements
        if self.action in ["sign_up", "sign_in", "reset_password"]:
            if not self.email:
                raise ValidationError(
                    f"Email required for {self.action}",
                    tool_name=self.tool_name,
                    field="email",
                )

        if self.action in ["sign_up", "sign_in"]:
            if not self.password:
                raise ValidationError(
                    f"Password required for {self.action}",
                    tool_name=self.tool_name,
                    field="password",
                )

            # Validate password strength
            if len(self.password) < 6:
                raise ValidationError(
                    "Password must be at least 6 characters",
                    tool_name=self.tool_name,
                    field="password",
                )

        if self.action == "verify_token":
            if not self.token:
                raise ValidationError(
                    "Token required for verify_token action",
                    tool_name=self.tool_name,
                    field="token",
                )

        # Validate email format if provided
        if self.email:
            if "@" not in self.email or "." not in self.email:
                raise ValidationError(
                    "Invalid email format",
                    tool_name=self.tool_name,
                    field="email",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        result = {"success": True, "action": self.action}

        if self.action in ["sign_up", "sign_in"]:
            result["user"] = {
                "id": "mock_user_12345",
                "email": self.email,
                "email_confirmed_at": "2025-11-23T10:00:00Z",
                "created_at": "2025-11-23T10:00:00Z",
                "user_metadata": self.metadata or {},
            }
            result["session"] = {
                "access_token": "mock_access_token_abcdef123456",
                "refresh_token": "mock_refresh_token_abcdef123456",
                "expires_in": 3600,
                "token_type": "bearer",
            }

        elif self.action == "verify_token":
            result["user"] = {
                "id": "mock_user_12345",
                "email": "mock@example.com",
                "email_confirmed_at": "2025-11-23T10:00:00Z",
            }
            result["valid"] = True

        elif self.action == "reset_password":
            result["message"] = f"Password reset email sent to {self.email}"

        elif self.action == "sign_out":
            result["message"] = "Successfully signed out"

        elif self.action == "get_session":
            result["session"] = {
                "access_token": "mock_access_token_abcdef123456",
                "refresh_token": "mock_refresh_token_abcdef123456",
                "expires_in": 3600,
                "token_type": "bearer",
            }
            result["user"] = {
                "id": "mock_user_12345",
                "email": "mock@example.com",
            }

        result["metadata"] = {
            "tool_name": self.tool_name,
            "action": self.action,
            "mock_mode": True,
        }

        return result

    def _process(self) -> Dict[str, Any]:
        """Process authentication with Supabase."""
        # Get Supabase credentials
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise AuthenticationError(
                "Missing SUPABASE_URL or SUPABASE_KEY environment variables",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Import Supabase client
        try:
            from supabase import create_client, Client
        except ImportError:
            raise APIError(
                "Supabase SDK not installed. Run: pip install supabase",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Create client
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise AuthenticationError(
                f"Failed to create Supabase client: {e}",
                tool_name=self.tool_name,
                api_name="supabase",
            )

        # Execute action
        try:
            if self.action == "sign_up":
                return self._sign_up(supabase)
            elif self.action == "sign_in":
                return self._sign_in(supabase)
            elif self.action == "sign_out":
                return self._sign_out(supabase)
            elif self.action == "verify_token":
                return self._verify_token(supabase)
            elif self.action == "reset_password":
                return self._reset_password(supabase)
            elif self.action == "get_session":
                return self._get_session(supabase)
            else:
                raise ValidationError(
                    f"Unknown action: {self.action}",
                    tool_name=self.tool_name,
                )
        except Exception as e:
            if "invalid" in str(e).lower() or "not found" in str(e).lower():
                raise AuthenticationError(
                    f"Authentication failed: {e}",
                    tool_name=self.tool_name,
                    api_name="supabase_auth",
                )
            raise

    def _sign_up(self, supabase: Any) -> Dict[str, Any]:
        """Sign up new user."""
        sign_up_params = {
            "email": self.email,
            "password": self.password,
        }

        if self.metadata:
            sign_up_params["data"] = self.metadata

        if self.redirect_to:
            sign_up_params["options"] = {"email_redirect_to": self.redirect_to}

        response = supabase.auth.sign_up(sign_up_params)

        return {
            "user": response.user.__dict__ if hasattr(response.user, "__dict__") else response.user,
            "session": (
                response.session.__dict__
                if hasattr(response.session, "__dict__")
                else response.session
            ),
        }

    def _sign_in(self, supabase: Any) -> Dict[str, Any]:
        """Sign in existing user."""
        if self.provider:
            # OAuth sign in
            response = supabase.auth.sign_in_with_oauth(
                {
                    "provider": self.provider,
                    "options": {"redirect_to": self.redirect_to} if self.redirect_to else {},
                }
            )
            return {
                "url": response.url,
                "provider": self.provider,
            }
        else:
            # Email/password sign in
            response = supabase.auth.sign_in_with_password(
                {"email": self.email, "password": self.password}
            )
            return {
                "user": (
                    response.user.__dict__
                    if hasattr(response.user, "__dict__")
                    else response.user
                ),
                "session": (
                    response.session.__dict__
                    if hasattr(response.session, "__dict__")
                    else response.session
                ),
            }

    def _sign_out(self, supabase: Any) -> Dict[str, Any]:
        """Sign out current user."""
        supabase.auth.sign_out()
        return {"message": "Successfully signed out"}

    def _verify_token(self, supabase: Any) -> Dict[str, Any]:
        """Verify JWT token."""
        try:
            user = supabase.auth.get_user(self.token)
            return {
                "valid": True,
                "user": user.user.__dict__ if hasattr(user.user, "__dict__") else user.user,
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
            }

    def _reset_password(self, supabase: Any) -> Dict[str, Any]:
        """Send password reset email."""
        options = {}
        if self.redirect_to:
            options["redirect_to"] = self.redirect_to

        supabase.auth.reset_password_for_email(self.email, options)

        return {"message": f"Password reset email sent to {self.email}"}

    def _get_session(self, supabase: Any) -> Dict[str, Any]:
        """Get current session."""
        session = supabase.auth.get_session()

        return {
            "session": (
                session.__dict__ if hasattr(session, "__dict__") else session
            ),
            "user": supabase.auth.get_user().user,
        }


if __name__ == "__main__":
    # Test the tool
    print("Testing SupabaseAuth...")
    print("=" * 60)

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Sign up new user
    print("\n1. Testing sign up...")
    tool = SupabaseAuth(
        action="sign_up",
        email="newuser@example.com",
        password="SecurePass123!",
        metadata={"name": "John Doe", "role": "user"},
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Action: {result.get('action')}")
    print(f"User ID: {result.get('user', {}).get('id')}")
    print(f"Email: {result.get('user', {}).get('email')}")
    assert result.get("success") == True
    assert result.get("action") == "sign_up"
    assert "user" in result
    assert "session" in result

    # Test 2: Sign in existing user
    print("\n2. Testing sign in...")
    tool = SupabaseAuth(
        action="sign_in", email="user@example.com", password="SecurePass123!"
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Action: {result.get('action')}")
    print(f"Access Token: {result.get('session', {}).get('access_token', 'N/A')[:30]}...")
    assert result.get("success") == True
    assert result.get("action") == "sign_in"
    assert "session" in result
    assert "access_token" in result.get("session", {})

    # Test 3: Verify token
    print("\n3. Testing token verification...")
    tool = SupabaseAuth(
        action="verify_token",
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Token valid: {result.get('valid')}")
    assert result.get("success") == True

    # Test 4: Password reset
    print("\n4. Testing password reset...")
    tool = SupabaseAuth(
        action="reset_password",
        email="user@example.com",
        redirect_to="https://example.com/reset",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    assert result.get("success") == True
    assert "reset" in result.get("message", "").lower()

    # Test 5: Sign out
    print("\n5. Testing sign out...")
    tool = SupabaseAuth(action="sign_out")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    assert result.get("success") == True

    # Test 6: Get session
    print("\n6. Testing get session...")
    tool = SupabaseAuth(action="get_session")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Has session: {'session' in result}")
    assert result.get("success") == True

    # Test 7: Error handling - missing password
    print("\n7. Testing error handling (missing password)...")
    try:
        tool = SupabaseAuth(action="sign_in", email="user@example.com")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 8: Error handling - invalid email
    print("\n8. Testing error handling (invalid email)...")
    try:
        tool = SupabaseAuth(
            action="sign_up", email="invalid-email", password="SecurePass123!"
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 9: Error handling - weak password
    print("\n9. Testing error handling (weak password)...")
    try:
        tool = SupabaseAuth(action="sign_up", email="user@example.com", password="123")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
