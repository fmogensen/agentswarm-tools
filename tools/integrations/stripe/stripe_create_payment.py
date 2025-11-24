"""
Stripe Create Payment Tool

Creates a one-time payment using Stripe's Payment Intent API.
Supports multiple currencies, payment methods, and automatic confirmation.
"""

import hashlib
import json
import os
import time
import uuid
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError

# Stripe SDK import
try:
    import stripe
except ImportError:
    stripe = None


class StripeCreatePayment(BaseTool):
    """
    Create a one-time payment using Stripe Payment Intent API.

    This tool creates and optionally confirms a payment intent, supporting
    multiple currencies, payment methods, and automatic confirmation.

    Args:
        amount: Payment amount in smallest currency unit (e.g., cents for USD)
        currency: Three-letter ISO currency code (e.g., 'usd', 'eur', 'gbp')
        customer_email: Customer's email address for receipt
        description: Description of the payment (optional)
        payment_method_types: List of payment method types (default: ['card'])
        confirm: Whether to automatically confirm the payment (default: False)
        metadata: Additional metadata as key-value pairs (optional)

    Returns:
        Dict containing:
            - success (bool): Whether the payment was created successfully
            - payment_intent_id (str): Stripe Payment Intent ID
            - client_secret (str): Client secret for confirming payment
            - status (str): Payment status (requires_payment_method, requires_confirmation, succeeded, etc.)
            - amount (int): Payment amount
            - currency (str): Currency code
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = StripeCreatePayment(
        ...     amount=2000,  # $20.00
        ...     currency="usd",
        ...     customer_email="customer@example.com",
        ...     description="Product purchase",
        ...     confirm=False
        ... )
        >>> result = tool.run()
        >>> print(result['payment_intent_id'])
        'pi_1234567890abcdef'
    """

    # Tool metadata
    tool_name: str = "stripe_create_payment"
    tool_category: str = "integrations"

    # Required parameters
    amount: int = Field(
        ...,
        description="Payment amount in smallest currency unit (cents for USD)",
        ge=1,
        le=99999999,  # Stripe max amount
    )
    currency: str = Field(
        ...,
        description="Three-letter ISO currency code (e.g., 'usd', 'eur')",
        min_length=3,
        max_length=3,
    )
    customer_email: str = Field(
        ..., description="Customer's email address", pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$"
    )

    # Optional parameters
    description: Optional[str] = Field(
        None, description="Description of the payment", max_length=1000
    )
    payment_method_types: List[str] = Field(
        default=["card"],
        description="Payment method types (card, us_bank_account, etc.)",
    )
    confirm: bool = Field(False, description="Whether to automatically confirm the payment")
    metadata: Optional[Dict[str, str]] = Field(
        None, description="Additional metadata as key-value pairs"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the payment creation."""
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
                "payment_intent_id": result["id"],
                "client_secret": result["client_secret"],
                "status": result["status"],
                "amount": result["amount"],
                "currency": result["currency"],
                "metadata": {
                    "tool_name": self.tool_name,
                    "customer_email": self.customer_email,
                },
            }
        except (AuthenticationError, ValidationError):
            # Let these pass through unchanged
            raise
        except Exception as e:
            # Only wrap unexpected errors
            raise APIError(f"Failed to create payment: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate currency code
        supported_currencies = [
            "usd",
            "eur",
            "gbp",
            "cad",
            "aud",
            "jpy",
            "cny",
            "inr",
            "sgd",
            "hkd",
        ]
        if self.currency.lower() not in supported_currencies:
            raise ValidationError(
                f"Unsupported currency: {self.currency}. Supported: {', '.join(supported_currencies)}",
                tool_name=self.tool_name,
            )

        # Validate payment method types
        valid_methods = [
            "card",
            "us_bank_account",
            "sepa_debit",
            "ideal",
            "alipay",
            "wechat_pay",
        ]
        for method in self.payment_method_types:
            if method not in valid_methods:
                raise ValidationError(
                    f"Invalid payment method: {method}. Valid: {', '.join(valid_methods)}",
                    tool_name=self.tool_name,
                )

        # Validate email format
        if not self.customer_email or "@" not in self.customer_email:
            raise ValidationError("Invalid customer email format", tool_name=self.tool_name)

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        # Generate unique ID
        unique_data = f"{self.amount}{self.currency}{time.time()}{uuid.uuid4()}"
        unique_id = hashlib.sha256(unique_data.encode()).hexdigest()[:16]

        return {
            "success": True,
            "payment_intent_id": f"pi_mock_{unique_id}",
            "client_secret": f"pi_mock_{unique_id}_secret_mock",
            "status": "requires_payment_method" if not self.confirm else "succeeded",
            "amount": self.amount,
            "currency": self.currency.lower(),
            "metadata": {
                "tool_name": self.tool_name,
                "customer_email": self.customer_email,
                "mock_mode": True,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Process the payment creation with Stripe API."""
        # Get API key
        api_key = os.getenv("STRIPE_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing STRIPE_API_KEY environment variable", tool_name=self.tool_name
            )

        # Check Stripe SDK
        if stripe is None:
            raise APIError(
                "Stripe SDK not installed. Run: pip install stripe",
                tool_name=self.tool_name,
            )

        # Configure Stripe
        stripe.api_key = api_key

        # Prepare payment intent data
        intent_data = {
            "amount": self.amount,
            "currency": self.currency.lower(),
            "payment_method_types": self.payment_method_types,
            "receipt_email": self.customer_email,
        }

        # Add optional fields
        if self.description:
            intent_data["description"] = self.description

        if self.metadata:
            intent_data["metadata"] = self.metadata

        if self.confirm:
            intent_data["confirm"] = True

        # Create payment intent
        try:
            payment_intent = stripe.PaymentIntent.create(**intent_data)
            return payment_intent
        except stripe.error.CardError as e:
            raise APIError(f"Card error: {e.user_message}", tool_name=self.tool_name)
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(f"Invalid request: {str(e)}", tool_name=self.tool_name)
        except stripe.error.AuthenticationError as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}", tool_name=self.tool_name)
        except stripe.error.APIConnectionError as e:
            raise APIError(f"Network error: {str(e)}", tool_name=self.tool_name)
        except stripe.error.StripeError as e:
            raise APIError(f"Stripe error: {str(e)}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the tool
    print("Testing StripeCreatePayment...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic payment
    print("\n1. Testing basic payment...")
    tool = StripeCreatePayment(
        amount=2000,  # $20.00
        currency="usd",
        customer_email="customer@example.com",
        description="Test product purchase",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Payment Intent ID: {result.get('payment_intent_id')}")
    print(f"Status: {result.get('status')}")
    print(f"Amount: ${result.get('amount') / 100:.2f}")
    assert result.get("success") == True
    assert result.get("payment_intent_id").startswith("pi_")
    assert result.get("status") in ["requires_payment_method", "succeeded"]

    # Test 2: Auto-confirmed payment
    print("\n2. Testing auto-confirmed payment...")
    tool = StripeCreatePayment(
        amount=5000,  # $50.00
        currency="usd",
        customer_email="test@example.com",
        description="Premium subscription",
        confirm=True,
        metadata={"order_id": "12345", "customer_type": "premium"},
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    assert result.get("success") == True
    assert result.get("status") == "succeeded"

    # Test 3: EUR payment
    print("\n3. Testing EUR payment...")
    tool = StripeCreatePayment(
        amount=1500,  # €15.00
        currency="eur",
        customer_email="european@example.com",
        description="EU product purchase",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Currency: {result.get('currency')}")
    assert result.get("success") == True
    assert result.get("currency") == "eur"

    # Test 4: Error handling - invalid currency
    print("\n4. Testing error handling (invalid currency)...")
    try:
        tool = StripeCreatePayment(amount=1000, currency="xyz", customer_email="test@example.com")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    print("\n✅ All tests passed!")
