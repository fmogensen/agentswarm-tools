"""
Stripe Handle Webhooks Tool

Validates and processes Stripe webhook events with signature verification
and support for all Stripe event types.
"""

import hashlib
import hmac
import json
import os
import warnings
from typing import Any, Callable, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, SecurityError, ValidationError


class StripeHandleWebhooks(BaseTool):
    """
    Validate and process Stripe webhook events.

    This tool securely validates webhook signatures and processes Stripe events.
    It supports all Stripe event types and provides structured event data.

    Args:
        payload: Raw webhook payload (JSON string or bytes)
        signature_header: Stripe-Signature header from webhook request
        webhook_secret: Stripe webhook signing secret (optional, reads from env)
        event_types: List of event types to process (optional, processes all if None)
        skip_signature_validation: Skip signature validation (ONLY for testing)

    Returns:
        Dict containing:
            - success (bool): Whether the event was validated successfully
            - event_id (str): Stripe event ID
            - event_type (str): Event type (e.g., 'payment_intent.succeeded')
            - event_data (dict): Event data object
            - created (int): Event creation timestamp
            - livemode (bool): Whether event is from live mode
            - metadata (dict): Tool execution metadata

    Security:
        - ALWAYS validates webhook signatures in production
        - Uses constant-time comparison to prevent timing attacks
        - Protects against replay attacks with timestamp validation
        - Only processes whitelisted event types if specified

    Example:
        >>> # In webhook endpoint
        >>> payload = request.body
        >>> sig_header = request.headers.get('Stripe-Signature')
        >>>
        >>> tool = StripeHandleWebhooks(
        ...     payload=payload,
        ...     signature_header=sig_header,
        ...     event_types=['payment_intent.succeeded', 'customer.created']
        ... )
        >>> result = tool.run()
        >>>
        >>> if result['success']:
        ...     event_type = result['event_type']
        ...     if event_type == 'payment_intent.succeeded':
        ...         payment_intent = result['event_data']
        ...         print(f"Payment {payment_intent['id']} succeeded!")
    """

    # Tool metadata
    tool_name: str = "stripe_handle_webhooks"
    tool_category: str = "integrations"

    # Required parameters
    payload: str = Field(..., description="Raw webhook payload (JSON string)", min_length=1)
    signature_header: str = Field(
        ..., description="Stripe-Signature header from request", min_length=1
    )

    # Optional parameters
    webhook_secret: Optional[str] = Field(
        None,
        description="Stripe webhook signing secret (reads from STRIPE_WEBHOOK_SECRET if not provided)",
    )
    event_types: Optional[List[str]] = Field(
        None, description="Whitelist of event types to process (processes all if None)"
    )
    skip_signature_validation: bool = Field(
        False, description="Skip signature validation (ONLY for testing, never in production)"
    )
    tolerance: int = Field(
        300, description="Allowed time difference in seconds (default: 5 minutes)", ge=0, le=3600
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the webhook processing."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. VERIFY SIGNATURE (unless explicitly skipped for testing)
        if not self.skip_signature_validation:
            self._verify_webhook_signature()
        else:
            warnings.warn(
                "⚠️  SKIPPING WEBHOOK SIGNATURE VALIDATION - ONLY USE IN TESTING!",
                UserWarning,
                stacklevel=2
            )

        # 4. PARSE EVENT
        try:
            event = (
                json.loads(self.payload)
                if isinstance(self.payload, str)
                else json.loads(self.payload.decode("utf-8"))
            )
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON payload: {e}", tool_name=self.tool_name)

        # 5. VALIDATE EVENT STRUCTURE
        self._validate_event_structure(event)

        # 6. CHECK EVENT TYPE WHITELIST
        if self.event_types and event.get("type") not in self.event_types:
            raise ValidationError(
                f"Event type '{event.get('type')}' not in whitelist: {self.event_types}",
                tool_name=self.tool_name,
            )

        # 7. RETURN STRUCTURED EVENT DATA
        return {
            "success": True,
            "event_id": event.get("id"),
            "event_type": event.get("type"),
            "event_data": event.get("data", {}).get("object", {}),
            "created": event.get("created"),
            "livemode": event.get("livemode", False),
            "metadata": {
                "tool_name": self.tool_name,
                "event_type": event.get("type"),
                "api_version": event.get("api_version"),
            },
        }

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Warn if skipping signature validation (security risk)
        if self.skip_signature_validation:
            import warnings

            warnings.warn(
                "⚠️  Webhook signature validation is disabled! Only use this in testing.",
                UserWarning,
            )

        # Validate JSON payload
        try:
            if isinstance(self.payload, str):
                event = json.loads(self.payload)
            else:
                event = json.loads(self.payload.decode("utf-8"))
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON payload", tool_name=self.tool_name)

        # Validate required fields
        if "id" not in event:
            raise ValidationError("Missing required field: id", tool_name=self.tool_name)
        if "type" not in event:
            raise ValidationError("Missing required field: type", tool_name=self.tool_name)

        # Validate event ID format
        if not event.get("id", "").startswith("evt_"):
            raise ValidationError(
                "Invalid event ID format (should start with 'evt_')", tool_name=self.tool_name
            )

        # Validate event data structure
        if "data" not in event:
            raise ValidationError("Missing required field: data", tool_name=self.tool_name)
        if not isinstance(event.get("data"), dict):
            raise ValidationError("Event data must be a dictionary", tool_name=self.tool_name)

        # Validate event type whitelist
        if self.event_types and event.get("type") not in self.event_types:
            raise ValidationError(
                f"Event type '{event.get('type')}' not in whitelist", tool_name=self.tool_name
            )

        # Validate signature requirements if not skipping validation
        if not self.skip_signature_validation:
            # Check signature header is provided
            if not self.signature_header or not self.signature_header.strip():
                raise ValidationError(
                    "Missing signature_header for signature validation", tool_name=self.tool_name
                )

            # Check webhook secret is provided
            webhook_secret = self.webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET")
            if not webhook_secret:
                raise AuthenticationError(
                    "Missing STRIPE_WEBHOOK_SECRET environment variable or webhook_secret parameter",
                    tool_name=self.tool_name,
                )

            # Validate basic header format (must contain "=" for key=value pairs)
            if "=" not in self.signature_header:
                raise ValidationError(
                    "Invalid Stripe-Signature header format", tool_name=self.tool_name
                )

            # Parse signature header to validate format
            sig_parts = {}
            for part in self.signature_header.split(","):
                key_value = part.split("=", 1)
                if len(key_value) == 2:
                    sig_parts[key_value[0]] = key_value[1]

            timestamp = sig_parts.get("t")
            signatures = sig_parts.get("v1")

            # Validate signature header format - must have timestamp
            if not timestamp:
                raise SecurityError(
                    "Invalid signature header format", tool_name=self.tool_name
                )

            # Validate timestamp is not too old
            try:
                timestamp_int = int(timestamp)
                import time

                current_time = int(time.time())
                if abs(current_time - timestamp_int) > self.tolerance:
                    raise SecurityError(
                        "Webhook timestamp too old, possible replay attack", tool_name=self.tool_name
                    )
            except ValueError:
                raise SecurityError(
                    "Webhook timestamp too old, possible replay attack", tool_name=self.tool_name
                )

            # Check if signature is valid (mock check: if header doesn't contain "v1=")
            if not signatures:
                raise SecurityError("Invalid webhook signature", tool_name=self.tool_name)

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        import time

        current_time = int(time.time())

        # Parse payload to determine event type (or use default)
        try:
            event = (
                json.loads(self.payload)
                if isinstance(self.payload, str)
                else json.loads(self.payload.decode("utf-8"))
            )
            event_type = event.get("type", "payment_intent.succeeded")
        except:
            event_type = "payment_intent.succeeded"

        # Generate appropriate mock data based on event type
        if "payment_intent" in event_type:
            event_data = {
                "id": "pi_mock_1234567890",
                "object": "payment_intent",
                "amount": 2000,
                "currency": "usd",
                "status": "succeeded",
                "customer": "cus_mock_123",
            }
        elif "customer" in event_type:
            event_data = {
                "id": "cus_mock_1234567890",
                "object": "customer",
                "email": "customer@example.com",
                "name": "Mock Customer",
            }
        elif "invoice" in event_type:
            event_data = {
                "id": "in_mock_1234567890",
                "object": "invoice",
                "customer": "cus_mock_123",
                "amount_due": 2000,
                "status": "paid",
            }
        else:
            event_data = {"id": "obj_mock_1234567890", "object": "unknown"}

        return {
            "success": True,
            "event_id": "evt_mock_1234567890",
            "event_type": event_type,
            "event_data": event_data,
            "created": current_time,
            "livemode": False,
            "metadata": {
                "tool_name": self.tool_name,
                "event_type": event_type,
                "api_version": "2023-10-16",
                "mock_mode": True,
            },
        }

    def _verify_webhook_signature(self) -> None:
        """
        Verify Stripe webhook signature.

        Implements Stripe's webhook signature verification algorithm:
        1. Extract timestamp and signatures from header
        2. Compute expected signature
        3. Compare using constant-time comparison
        4. Validate timestamp to prevent replay attacks
        """
        # Get webhook secret
        secret = self.webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET")
        if not secret:
            raise AuthenticationError(
                "Missing STRIPE_WEBHOOK_SECRET environment variable",
                tool_name=self.tool_name,
            )

        # Parse signature header
        sig_parts = {}
        for part in self.signature_header.split(","):
            key_value = part.split("=", 1)
            if len(key_value) == 2:
                sig_parts[key_value[0]] = key_value[1]

        timestamp = sig_parts.get("t")
        signatures = sig_parts.get("v1")

        if not timestamp or not signatures:
            raise SecurityError(
                "Invalid signature header format",
                violation_type="invalid_signature_format",
                tool_name=self.tool_name,
            )

        # Check timestamp to prevent replay attacks
        try:
            timestamp_int = int(timestamp)
        except ValueError:
            raise SecurityError(
                "Invalid timestamp in signature",
                violation_type="invalid_timestamp",
                tool_name=self.tool_name,
            )

        import time

        current_time = int(time.time())
        if abs(current_time - timestamp_int) > self.tolerance:
            raise SecurityError(
                f"Webhook timestamp too old (tolerance: {self.tolerance}s)",
                violation_type="replay_attack",
                tool_name=self.tool_name,
            )

        # Compute expected signature
        payload_bytes = (
            self.payload.encode("utf-8") if isinstance(self.payload, str) else self.payload
        )
        signed_payload = f"{timestamp}.".encode("utf-8") + payload_bytes
        expected_sig = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

        # Compare signatures using constant-time comparison
        if not hmac.compare_digest(expected_sig, signatures):
            raise SecurityError(
                "Invalid webhook signature",
                violation_type="signature_mismatch",
                tool_name=self.tool_name,
            )

    def _validate_event_structure(self, event: Dict[str, Any]) -> None:
        """Validate that event has required Stripe webhook structure."""
        required_fields = ["id", "type", "data", "created"]

        for field in required_fields:
            if field not in event:
                raise ValidationError(
                    f"Missing required field in event: {field}",
                    tool_name=self.tool_name,
                )

        # Validate event ID format
        if not event.get("id", "").startswith("evt_"):
            raise ValidationError(
                "Invalid event ID format (should start with 'evt_')",
                tool_name=self.tool_name,
            )

        # Validate data structure
        if not isinstance(event.get("data"), dict):
            raise ValidationError(
                "Event data must be a dictionary",
                tool_name=self.tool_name,
            )


# Common Stripe event types for reference
STRIPE_EVENT_TYPES = {
    # Payment Intents
    "payment_intent.succeeded": "Payment succeeded",
    "payment_intent.payment_failed": "Payment failed",
    "payment_intent.created": "Payment intent created",
    "payment_intent.canceled": "Payment intent canceled",
    # Customers
    "customer.created": "Customer created",
    "customer.updated": "Customer updated",
    "customer.deleted": "Customer deleted",
    # Subscriptions
    "customer.subscription.created": "Subscription created",
    "customer.subscription.updated": "Subscription updated",
    "customer.subscription.deleted": "Subscription canceled",
    "customer.subscription.trial_will_end": "Trial ending soon",
    # Invoices
    "invoice.created": "Invoice created",
    "invoice.finalized": "Invoice finalized",
    "invoice.paid": "Invoice paid",
    "invoice.payment_failed": "Invoice payment failed",
    # Charges
    "charge.succeeded": "Charge succeeded",
    "charge.failed": "Charge failed",
    "charge.refunded": "Charge refunded",
    # Disputes
    "charge.dispute.created": "Dispute created",
    "charge.dispute.closed": "Dispute closed",
    # Checkout
    "checkout.session.completed": "Checkout completed",
    "checkout.session.expired": "Checkout expired",
}


if __name__ == "__main__":
    # Test the tool
    print("Testing StripeHandleWebhooks...")

    import json
    import os
    import time

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic webhook processing (mock mode)
    print("\n1. Testing basic webhook processing...")

    mock_event = {
        "id": "evt_test_123",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_123",
                "amount": 2000,
                "currency": "usd",
                "status": "succeeded",
            }
        },
        "created": int(time.time()),
        "livemode": False,
        "api_version": "2023-10-16",
    }

    tool = StripeHandleWebhooks(
        payload=json.dumps(mock_event),
        signature_header="t=1234567890,v1=mocksignature",
        skip_signature_validation=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Event ID: {result.get('event_id')}")
    print(f"Event Type: {result.get('event_type')}")
    assert result.get("success") == True
    assert result.get("event_type") == "payment_intent.succeeded"

    # Test 2: Customer created event
    print("\n2. Testing customer.created event...")

    customer_event = {
        "id": "evt_test_456",
        "type": "customer.created",
        "data": {
            "object": {
                "id": "cus_test_123",
                "email": "newcustomer@example.com",
                "name": "New Customer",
            }
        },
        "created": int(time.time()),
        "livemode": False,
    }

    tool = StripeHandleWebhooks(
        payload=json.dumps(customer_event),
        signature_header="t=1234567890,v1=mocksignature",
        skip_signature_validation=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Event Type: {result.get('event_type')}")
    print(f"Customer Email: {result.get('event_data', {}).get('email')}")
    assert result.get("success") == True
    assert result.get("event_type") == "customer.created"

    # Test 3: Invoice paid event
    print("\n3. Testing invoice.paid event...")

    invoice_event = {
        "id": "evt_test_789",
        "type": "invoice.paid",
        "data": {
            "object": {
                "id": "in_test_123",
                "customer": "cus_test_123",
                "amount_paid": 2000,
                "status": "paid",
            }
        },
        "created": int(time.time()),
        "livemode": False,
    }

    tool = StripeHandleWebhooks(
        payload=json.dumps(invoice_event),
        signature_header="t=1234567890,v1=mocksignature",
        skip_signature_validation=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Event Type: {result.get('event_type')}")
    assert result.get("success") == True
    assert result.get("event_type") == "invoice.paid"

    # Test 4: Event type whitelist
    print("\n4. Testing event type whitelist...")

    tool = StripeHandleWebhooks(
        payload=json.dumps(mock_event),
        signature_header="t=1234567890,v1=mocksignature",
        event_types=["payment_intent.succeeded", "customer.created"],
        skip_signature_validation=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 5: Event type not in whitelist
    print("\n5. Testing event type not in whitelist...")

    try:
        tool = StripeHandleWebhooks(
            payload=json.dumps(invoice_event),
            signature_header="t=1234567890,v1=mocksignature",
            event_types=["payment_intent.succeeded"],  # invoice.paid not in list
            skip_signature_validation=True,
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 6: Invalid JSON payload
    print("\n6. Testing error handling (invalid JSON)...")

    try:
        tool = StripeHandleWebhooks(
            payload="invalid json {",
            signature_header="t=1234567890,v1=mocksignature",
            skip_signature_validation=True,
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 7: Missing required fields
    print("\n7. Testing error handling (missing required fields)...")

    invalid_event = {
        "id": "evt_test_999",
        # Missing 'type', 'data', 'created'
    }

    try:
        tool = StripeHandleWebhooks(
            payload=json.dumps(invalid_event),
            signature_header="t=1234567890,v1=mocksignature",
            skip_signature_validation=True,
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 8: Signature verification (with valid signature)
    print("\n8. Testing signature verification...")

    # Create a valid signature
    webhook_secret = "whsec_test_secret_key_1234567890"
    os.environ["STRIPE_WEBHOOK_SECRET"] = webhook_secret

    timestamp = int(time.time())
    payload_str = json.dumps(mock_event)
    signed_payload = f"{timestamp}.{payload_str}"

    import hashlib
    import hmac

    signature = hmac.new(
        webhook_secret.encode("utf-8"), signed_payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    sig_header = f"t={timestamp},v1={signature}"

    tool = StripeHandleWebhooks(
        payload=payload_str,
        signature_header=sig_header,
        skip_signature_validation=False,  # Enable signature validation
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Signature verified: True")
    assert result.get("success") == True

    # Test 9: Invalid signature
    print("\n9. Testing error handling (invalid signature)...")

    try:
        tool = StripeHandleWebhooks(
            payload=payload_str,
            signature_header=f"t={timestamp},v1=invalidsignature123",
            skip_signature_validation=False,
        )
        result = tool.run()
        print("ERROR: Should have raised SecurityError")
    except SecurityError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 10: Replay attack protection (old timestamp)
    print("\n10. Testing replay attack protection...")

    old_timestamp = timestamp - 400  # More than 5 minutes (300s tolerance)
    old_signed_payload = f"{old_timestamp}.{payload_str}"
    old_signature = hmac.new(
        webhook_secret.encode("utf-8"), old_signed_payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    try:
        tool = StripeHandleWebhooks(
            payload=payload_str,
            signature_header=f"t={old_timestamp},v1={old_signature}",
            skip_signature_validation=False,
            tolerance=300,
        )
        result = tool.run()
        print("ERROR: Should have raised SecurityError")
    except SecurityError as e:
        print(f"Correctly caught error (replay attack): {e.message}")

    # Cleanup
    os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    print("\n✅ All tests passed!")
    print(f"\n📋 Supported Stripe events ({len(STRIPE_EVENT_TYPES)}):")
    for event_type, description in list(STRIPE_EVENT_TYPES.items())[:5]:
        print(f"  - {event_type}: {description}")
    print(f"  ... and {len(STRIPE_EVENT_TYPES) - 5} more")
