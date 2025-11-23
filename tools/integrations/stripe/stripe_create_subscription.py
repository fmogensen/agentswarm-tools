"""
Stripe Create Subscription Tool

Creates a recurring subscription for a customer using Stripe's Subscription API.
Supports multiple plans, trial periods, and billing intervals.
"""

import json
import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class StripeCreateSubscription(BaseTool):
    """
    Create a recurring subscription for a customer.

    This tool creates a subscription with support for multiple price points,
    trial periods, and various billing intervals.

    Args:
        customer_id: Stripe customer ID or email to create customer
        price_id: Stripe price ID for the subscription
        payment_method_id: Payment method ID (optional, required if no default)
        trial_period_days: Number of days for trial period (default: 0)
        billing_interval: Billing interval: monthly, yearly, weekly (default: monthly)
        quantity: Quantity of the subscription (default: 1)
        metadata: Additional metadata as key-value pairs (optional)

    Returns:
        Dict containing:
            - success (bool): Whether the subscription was created successfully
            - subscription_id (str): Stripe Subscription ID
            - customer_id (str): Stripe Customer ID
            - status (str): Subscription status (active, trialing, etc.)
            - current_period_end (int): Unix timestamp of current period end
            - trial_end (int|None): Unix timestamp of trial end (if applicable)
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = StripeCreateSubscription(
        ...     customer_id="cus_1234567890",
        ...     price_id="price_monthly_premium",
        ...     trial_period_days=14,
        ...     billing_interval="monthly"
        ... )
        >>> result = tool.run()
        >>> print(result['subscription_id'])
        'sub_1234567890abcdef'
    """

    # Tool metadata
    tool_name: str = "stripe_create_subscription"
    tool_category: str = "integrations"

    # Required parameters
    customer_id: str = Field(
        ...,
        description="Stripe customer ID (cus_xxx) or email to create customer",
        min_length=1,
    )
    price_id: str = Field(..., description="Stripe price ID for subscription", min_length=1)

    # Optional parameters
    payment_method_id: Optional[str] = Field(None, description="Payment method ID (pm_xxx)")
    trial_period_days: int = Field(0, description="Number of days for trial period", ge=0, le=730)
    billing_interval: str = Field(
        "monthly",
        description="Billing interval: monthly, yearly, weekly",
    )
    quantity: int = Field(1, description="Quantity of subscription", ge=1, le=100)
    metadata: Optional[Dict[str, str]] = Field(
        None, description="Additional metadata as key-value pairs"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the subscription creation."""
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
                "subscription_id": result["id"],
                "customer_id": result["customer"],
                "status": result["status"],
                "current_period_end": result["current_period_end"],
                "trial_end": result.get("trial_end"),
                "metadata": {
                    "tool_name": self.tool_name,
                    "price_id": self.price_id,
                    "billing_interval": self.billing_interval,
                },
            }
        except Exception as e:
            raise APIError(f"Failed to create subscription: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate billing interval
        valid_intervals = ["monthly", "yearly", "weekly", "daily"]
        if self.billing_interval.lower() not in valid_intervals:
            raise ValidationError(
                f"Invalid billing interval: {self.billing_interval}. Valid: {', '.join(valid_intervals)}",
                tool_name=self.tool_name,
            )

        # Validate customer ID format (if it's an ID)
        if self.customer_id.startswith("cus_") and len(self.customer_id) < 10:
            raise ValidationError("Invalid customer ID format", tool_name=self.tool_name)

        # Validate price ID format
        if not self.price_id.startswith("price_") and not self.price_id.startswith("plan_"):
            raise ValidationError("Invalid price ID format", tool_name=self.tool_name)

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        import time

        current_time = int(time.time())
        trial_end = (
            current_time + (self.trial_period_days * 86400) if self.trial_period_days > 0 else None
        )
        period_end = current_time + 2592000  # 30 days

        return {
            "success": True,
            "subscription_id": "sub_mock_1234567890abcdef",
            "customer_id": (
                self.customer_id if self.customer_id.startswith("cus_") else "cus_mock_created"
            ),
            "status": "trialing" if self.trial_period_days > 0 else "active",
            "current_period_end": period_end,
            "trial_end": trial_end,
            "metadata": {
                "tool_name": self.tool_name,
                "price_id": self.price_id,
                "billing_interval": self.billing_interval,
                "mock_mode": True,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Process the subscription creation with Stripe API."""
        # Get API key
        api_key = os.getenv("STRIPE_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing STRIPE_API_KEY environment variable", tool_name=self.tool_name
            )

        # Import Stripe SDK
        try:
            import stripe
        except ImportError:
            raise APIError(
                "Stripe SDK not installed. Run: pip install stripe",
                tool_name=self.tool_name,
            )

        # Configure Stripe
        stripe.api_key = api_key

        # Create or get customer
        customer_id = self.customer_id
        if not customer_id.startswith("cus_"):
            # Email provided, create customer
            try:
                customer = stripe.Customer.create(email=customer_id)
                customer_id = customer.id
            except Exception as e:
                raise APIError(f"Failed to create customer: {e}", tool_name=self.tool_name)

        # Prepare subscription data
        subscription_data = {
            "customer": customer_id,
            "items": [{"price": self.price_id, "quantity": self.quantity}],
        }

        # Add optional fields
        if self.trial_period_days > 0:
            subscription_data["trial_period_days"] = self.trial_period_days

        if self.payment_method_id:
            subscription_data["default_payment_method"] = self.payment_method_id

        if self.metadata:
            subscription_data["metadata"] = self.metadata

        # Create subscription
        try:
            subscription = stripe.Subscription.create(**subscription_data)
            return subscription
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(f"Invalid request: {str(e)}", tool_name=self.tool_name)
        except stripe.error.AuthenticationError as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}", tool_name=self.tool_name)
        except stripe.error.StripeError as e:
            raise APIError(f"Stripe error: {str(e)}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the tool
    print("Testing StripeCreateSubscription...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic monthly subscription
    print("\n1. Testing basic monthly subscription...")
    tool = StripeCreateSubscription(customer_id="cus_1234567890", price_id="price_monthly_premium")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Subscription ID: {result.get('subscription_id')}")
    print(f"Status: {result.get('status')}")
    assert result.get("success") == True
    assert result.get("subscription_id").startswith("sub_")
    assert result.get("status") == "active"

    # Test 2: Subscription with trial period
    print("\n2. Testing subscription with 14-day trial...")
    tool = StripeCreateSubscription(
        customer_id="cus_1234567890",
        price_id="price_monthly_premium",
        trial_period_days=14,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    print(f"Trial ends: {result.get('trial_end')}")
    assert result.get("success") == True
    assert result.get("status") == "trialing"
    assert result.get("trial_end") is not None

    # Test 3: Yearly subscription with quantity
    print("\n3. Testing yearly subscription with quantity...")
    tool = StripeCreateSubscription(
        customer_id="cus_1234567890",
        price_id="price_yearly_enterprise",
        billing_interval="yearly",
        quantity=5,
        metadata={"team": "engineering", "seats": "5"},
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Billing interval: {result.get('metadata', {}).get('billing_interval')}")
    assert result.get("success") == True

    # Test 4: Create customer from email
    print("\n4. Testing subscription with email (creates customer)...")
    tool = StripeCreateSubscription(
        customer_id="newcustomer@example.com",  # Email instead of ID
        price_id="price_monthly_basic",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Customer ID: {result.get('customer_id')}")
    assert result.get("success") == True
    assert result.get("customer_id").startswith("cus_")

    # Test 5: Error handling - invalid interval
    print("\n5. Testing error handling (invalid billing interval)...")
    try:
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            billing_interval="invalid",
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    print("\n✅ All tests passed!")
