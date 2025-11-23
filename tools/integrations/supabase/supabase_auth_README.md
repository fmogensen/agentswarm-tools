# SupabaseAuth

Complete user authentication and session management for Supabase.

## Overview

Handle user authentication including sign up, sign in, password reset, JWT validation, and OAuth integration.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | str | Yes | sign_up, sign_in, sign_out, verify_token, reset_password, get_session |
| `email` | str | Optional | User email address |
| `password` | str | Optional | User password (min 6 characters) |
| `token` | str | Optional | JWT token to verify |
| `provider` | str | Optional | OAuth provider (google, github, gitlab, etc.) |
| `redirect_to` | str | Optional | URL to redirect after auth |
| `metadata` | dict | Optional | User metadata for sign_up |
| `options` | dict | Optional | Additional auth options |

## Examples

### Sign Up

```python
from tools.integrations.supabase import SupabaseAuth

# Create new user
tool = SupabaseAuth(
    action="sign_up",
    email="user@example.com",
    password="SecurePass123!",
    metadata={"name": "John Doe", "role": "user", "department": "engineering"}
)
result = tool.run()

user_id = result['user']['id']
access_token = result['session']['access_token']
```

### Sign In

```python
# Email/password sign in
tool = SupabaseAuth(
    action="sign_in",
    email="user@example.com",
    password="SecurePass123!"
)
result = tool.run()

# OAuth sign in
tool = SupabaseAuth(
    action="sign_in",
    provider="google",
    redirect_to="https://yourapp.com/callback"
)
result = tool.run()
# User will be redirected to result['url']
```

### Verify Token

```python
# Validate JWT token
tool = SupabaseAuth(
    action="verify_token",
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)
result = tool.run()

if result['valid']:
    user = result['user']
    print(f"Token valid for user: {user['email']}")
else:
    print(f"Invalid token: {result.get('error')}")
```

### Password Reset

```python
# Send password reset email
tool = SupabaseAuth(
    action="reset_password",
    email="user@example.com",
    redirect_to="https://yourapp.com/reset-password"
)
result = tool.run()
print(result['message'])
```

## Authentication Flows

### Email Confirmation

```python
# 1. Sign up (sends confirmation email)
signup = SupabaseAuth(
    action="sign_up",
    email="new@example.com",
    password="Pass123!",
    redirect_to="https://yourapp.com/confirm"
)
result = signup.run()

# 2. User clicks link in email, gets redirected with token

# 3. Verify the token
verify = SupabaseAuth(
    action="verify_token",
    token=token_from_url
)
verification = verify.run()
```

### Session Management

```python
# Get current session
tool = SupabaseAuth(action="get_session")
result = tool.run()

if result.get('session'):
    access_token = result['session']['access_token']
    # Use token for authenticated requests
else:
    # No active session, user needs to sign in
    pass
```

## Best Practices

```python
# ✅ Good: Strong password requirements
tool = SupabaseAuth(
    action="sign_up",
    email="user@example.com",
    password="StrongP@ssw0rd123!"  # Min 6 chars
)

# ✅ Good: Include user metadata
tool = SupabaseAuth(
    action="sign_up",
    email="user@example.com",
    password="Pass123!",
    metadata={
        "full_name": "John Doe",
        "avatar_url": "https://...",
        "preferences": {"theme": "dark"}
    }
)

# ❌ Bad: Weak password
tool = SupabaseAuth(
    action="sign_up",
    password="123"  # Too short, will fail
)
```

---

**Version:** 1.0.0
