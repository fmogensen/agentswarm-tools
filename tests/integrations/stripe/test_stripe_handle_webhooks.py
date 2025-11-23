"""
Tests for Stripe Handle Webhooks Tool
"""

import pytest
import os
import json
import time
import hmac
import hashlib
from unittest.mock import Mock, patch

from tools.integrations.stripe.stripe_handle_webhooks import StripeHandleWebhooks, STRIPE_EVENT_TYPES
from shared.errors import ValidationError, APIError, AuthenticationError, SecurityError


@pytest.fixture
def mock_env():
    """Set up mock environment"""
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    os.environ.pop("USE_MOCK_APIS", None)


@pytest.fixture
def valid_webhook_event():
    """Generate a valid webhook event"""
    return {
        "id": "evt_test_123",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_123",
                "amount": 2000,
                "currency": "usd",
                "status": "succeeded"
            }
        },
        "created": int(time.time()),
        "livemode": False,
        "api_version": "2023-10-16"
    }


@pytest.fixture
def webhook_secret():
    """Webhook secret for testing"""
    return "whsec_test_secret_1234567890"


def create_valid_signature(payload: str, secret: str, timestamp: int = None) -> str:
    """Helper to create valid Stripe webhook signature"""
    if timestamp is None:
        timestamp = int(time.time())

    signed_payload = f"{timestamp}.{payload}"
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return f"t={timestamp},v1={signature}"


class TestStripeHandleWebhooks:
    """Test cases for StripeHandleWebhooks tool"""

    def test_initialization(self, valid_webhook_event):
        """Test tool initialization"""
        tool = StripeHandleWebhooks(
            payload=json.dumps(valid_webhook_event),
            signature_header="t=123,v1=sig",
            skip_signature_validation=True
        )
        assert tool.tool_name == "stripe_handle_webhooks"
        assert tool.tool_category == "integrations"

    def test_mock_mode_payment_intent_succeeded(self, mock_env, valid_webhook_event):
        """Test payment intent succeeded event in mock mode"""
        tool = StripeHandleWebhooks(
            payload=json.dumps(valid_webhook_event),
            signature_header="t=123,v1=sig",
            skip_signature_validation=True
        )
        result = tool.run()

        assert result["success"] is True
        assert result["event_type"] == "payment_intent.succeeded"
        assert result["event_id"] == "evt_mock_1234567890"
        assert "event_data" in result
        assert result["metadata"]["mock_mode"] is True

    def test_mock_mode_customer_created(self, mock_env):
        """Test customer created event"""
        event = {
            "id": "evt_test_456",
            "type": "customer.created",
            "data": {
                "object": {
                    "id": "cus_test_123",
                    "email": "newcustomer@example.com"
                }
            },
            "created": int(time.time()),
            "livemode": False
        }

        tool = StripeHandleWebhooks(
            payload=json.dumps(event),
            signature_header="t=123,v1=sig",
            skip_signature_validation=True
        )
        result = tool.run()

        assert result["success"] is True
        assert result["event_type"] == "customer.created"

    def test_mock_mode_invoice_paid(self, mock_env):
        """Test invoice paid event"""
        event = {
            "id": "evt_test_789",
            "type": "invoice.paid",
            "data": {
                "object": {
                    "id": "in_test_123",
                    "amount_paid": 2000
                }
            },
            "created": int(time.time()),
            "livemode": False
        }

        tool = StripeHandleWebhooks(
            payload=json.dumps(event),
            signature_header="t=123,v1=sig",
            skip_signature_validation=True
        )
        result = tool.run()

        assert result["success"] is True
        assert result["event_type"] == "invoice.paid"

    def test_event_type_whitelist_allowed(self, valid_webhook_event):
        """Test event type whitelist - allowed event"""
        tool = StripeHandleWebhooks(
            payload=json.dumps(valid_webhook_event),
            signature_header="t=123,v1=sig",
            event_types=["payment_intent.succeeded", "customer.created"],
            skip_signature_validation=True
        )
        result = tool.run()

        assert result["success"] is True

    def test_event_type_whitelist_blocked(self):
        """Test event type whitelist - blocked event"""
        event = {
            "id": "evt_test_789",
            "type": "invoice.paid",
            "data": {"object": {}},
            "created": int(time.time()),
            "livemode": False
        }

        with pytest.raises(ValidationError) as exc_info:
            tool = StripeHandleWebhooks(
                payload=json.dumps(event),
                signature_header="t=123,v1=sig",
                event_types=["payment_intent.succeeded"],  # invoice.paid not allowed
                skip_signature_validation=True
            )
            tool.run()

        assert "not in whitelist" in str(exc_info.value)

    def test_validation_invalid_json(self):
        """Test validation for invalid JSON payload"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeHandleWebhooks(
                payload="invalid json {",
                signature_header="t=123,v1=sig",
                skip_signature_validation=True
            )
            tool.run()

        assert "Invalid JSON" in str(exc_info.value)

    def test_validation_missing_required_fields(self):
        """Test validation for missing required fields"""
        invalid_event = {
            "id": "evt_test_999",
            # Missing 'type', 'data', 'created'
        }

        with pytest.raises(ValidationError) as exc_info:
            tool = StripeHandleWebhooks(
                payload=json.dumps(invalid_event),
                signature_header="t=123,v1=sig",
                skip_signature_validation=True
            )
            tool.run()

        assert "Missing required field" in str(exc_info.value)

    def test_validation_invalid_event_id_format(self):
        """Test validation for invalid event ID format"""
        invalid_event = {
            "id": "invalid_id",  # Should start with evt_
            "type": "payment_intent.succeeded",
            "data": {"object": {}},
            "created": int(time.time())
        }

        with pytest.raises(ValidationError) as exc_info:
            tool = StripeHandleWebhooks(
                payload=json.dumps(invalid_event),
                signature_header="t=123,v1=sig",
                skip_signature_validation=True
            )
            tool.run()

        assert "Invalid event ID format" in str(exc_info.value)

    def test_validation_invalid_data_structure(self):
        """Test validation for invalid data structure"""
        invalid_event = {
            "id": "evt_test_999",
            "type": "payment_intent.succeeded",
            "data": "not_a_dict",  # Should be a dict
            "created": int(time.time())
        }

        with pytest.raises(ValidationError) as exc_info:
            tool = StripeHandleWebhooks(
                payload=json.dumps(invalid_event),
                signature_header="t=123,v1=sig",
                skip_signature_validation=True
            )
            tool.run()

        assert "data must be a dictionary" in str(exc_info.value)

    def test_signature_verification_valid(self, valid_webhook_event, webhook_secret):
        """Test valid signature verification"""
        os.environ["STRIPE_WEBHOOK_SECRET"] = webhook_secret

        timestamp = int(time.time())
        payload_str = json.dumps(valid_webhook_event)
        sig_header = create_valid_signature(payload_str, webhook_secret, timestamp)

        tool = StripeHandleWebhooks(
            payload=payload_str,
            signature_header=sig_header,
            skip_signature_validation=False
        )
        result = tool.run()

        assert result["success"] is True

        # Cleanup
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_signature_verification_invalid_signature(self, valid_webhook_event, webhook_secret):
        """Test invalid signature rejection"""
        os.environ["STRIPE_WEBHOOK_SECRET"] = webhook_secret

        timestamp = int(time.time())
        payload_str = json.dumps(valid_webhook_event)
        invalid_sig_header = f"t={timestamp},v1=invalidsignature123"

        with pytest.raises(SecurityError) as exc_info:
            tool = StripeHandleWebhooks(
                payload=payload_str,
                signature_header=invalid_sig_header,
                skip_signature_validation=False
            )
            tool.run()

        assert "Invalid webhook signature" in str(exc_info.value)

        # Cleanup
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_signature_verification_replay_attack_protection(self, valid_webhook_event, webhook_secret):
        """Test replay attack protection (old timestamp)"""
        os.environ["STRIPE_WEBHOOK_SECRET"] = webhook_secret

        old_timestamp = int(time.time()) - 400  # More than 5 minutes old
        payload_str = json.dumps(valid_webhook_event)
        sig_header = create_valid_signature(payload_str, webhook_secret, old_timestamp)

        with pytest.raises(SecurityError) as exc_info:
            tool = StripeHandleWebhooks(
                payload=payload_str,
                signature_header=sig_header,
                skip_signature_validation=False,
                tolerance=300
            )
            tool.run()

        assert "timestamp too old" in str(exc_info.value).lower()

        # Cleanup
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_signature_verification_custom_tolerance(self, valid_webhook_event, webhook_secret):
        """Test custom tolerance for timestamp validation"""
        os.environ["STRIPE_WEBHOOK_SECRET"] = webhook_secret

        old_timestamp = int(time.time()) - 500  # 500 seconds old
        payload_str = json.dumps(valid_webhook_event)
        sig_header = create_valid_signature(payload_str, webhook_secret, old_timestamp)

        # Should fail with 300s tolerance
        with pytest.raises(SecurityError):
            tool = StripeHandleWebhooks(
                payload=payload_str,
                signature_header=sig_header,
                skip_signature_validation=False,
                tolerance=300
            )
            tool.run()

        # Should pass with 600s tolerance
        tool = StripeHandleWebhooks(
            payload=payload_str,
            signature_header=sig_header,
            skip_signature_validation=False,
            tolerance=600
        )
        result = tool.run()
        assert result["success"] is True

        # Cleanup
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_signature_verification_invalid_header_format(self, valid_webhook_event, webhook_secret):
        """Test invalid signature header format"""
        os.environ["STRIPE_WEBHOOK_SECRET"] = webhook_secret

        payload_str = json.dumps(valid_webhook_event)

        with pytest.raises(ValidationError) as exc_info:
            tool = StripeHandleWebhooks(
                payload=payload_str,
                signature_header="invalid_format",
                skip_signature_validation=False
            )
            tool.run()

        assert "Invalid Stripe-Signature header format" in str(exc_info.value)

        # Cleanup
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_signature_verification_missing_timestamp(self, valid_webhook_event, webhook_secret):
        """Test signature verification with missing timestamp"""
        os.environ["STRIPE_WEBHOOK_SECRET"] = webhook_secret

        payload_str = json.dumps(valid_webhook_event)
        invalid_sig_header = "v1=somesignature"  # Missing t=

        with pytest.raises(SecurityError) as exc_info:
            tool = StripeHandleWebhooks(
                payload=payload_str,
                signature_header=invalid_sig_header,
                skip_signature_validation=False
            )
            tool.run()

        assert "Invalid signature header format" in str(exc_info.value)

        # Cleanup
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_missing_webhook_secret(self, valid_webhook_event):
        """Test error when webhook secret is missing"""
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

        payload_str = json.dumps(valid_webhook_event)

        with pytest.raises(AuthenticationError) as exc_info:
            tool = StripeHandleWebhooks(
                payload=payload_str,
                signature_header="t=123,v1=sig",
                skip_signature_validation=False
            )
            tool.run()

        assert "STRIPE_WEBHOOK_SECRET" in str(exc_info.value)

    def test_webhook_secret_parameter(self, valid_webhook_event):
        """Test providing webhook secret as parameter"""
        secret = "whsec_custom_secret"
        timestamp = int(time.time())
        payload_str = json.dumps(valid_webhook_event)
        sig_header = create_valid_signature(payload_str, secret, timestamp)

        tool = StripeHandleWebhooks(
            payload=payload_str,
            signature_header=sig_header,
            webhook_secret=secret,
            skip_signature_validation=False
        )
        result = tool.run()

        assert result["success"] is True

    def test_event_data_extraction(self, valid_webhook_event):
        """Test event data extraction"""
        tool = StripeHandleWebhooks(
            payload=json.dumps(valid_webhook_event),
            signature_header="t=123,v1=sig",
            skip_signature_validation=True
        )
        result = tool.run()

        assert result["success"] is True
        assert result["event_id"] == "evt_test_123"
        assert result["event_type"] == "payment_intent.succeeded"
        assert result["event_data"]["id"] == "pi_test_123"
        assert result["created"] == valid_webhook_event["created"]
        assert result["livemode"] is False

    def test_all_common_event_types(self):
        """Test that common event types are defined"""
        assert "payment_intent.succeeded" in STRIPE_EVENT_TYPES
        assert "customer.created" in STRIPE_EVENT_TYPES
        assert "invoice.paid" in STRIPE_EVENT_TYPES
        assert "charge.succeeded" in STRIPE_EVENT_TYPES
        assert len(STRIPE_EVENT_TYPES) >= 20

    def test_bytes_payload(self, valid_webhook_event):
        """Test handling bytes payload"""
        payload_bytes = json.dumps(valid_webhook_event).encode('utf-8')

        tool = StripeHandleWebhooks(
            payload=payload_bytes.decode('utf-8'),
            signature_header="t=123,v1=sig",
            skip_signature_validation=True
        )
        result = tool.run()

        assert result["success"] is True

    def test_skip_validation_warning(self, valid_webhook_event):
        """Test that skipping validation produces warning"""
        with pytest.warns(Warning):
            tool = StripeHandleWebhooks(
                payload=json.dumps(valid_webhook_event),
                signature_header="t=123,v1=sig",
                skip_signature_validation=True
            )

    def test_tolerance_edge_cases(self, valid_webhook_event, webhook_secret):
        """Test tolerance edge cases"""
        os.environ["STRIPE_WEBHOOK_SECRET"] = webhook_secret

        # Test minimum tolerance (0)
        timestamp = int(time.time())
        payload_str = json.dumps(valid_webhook_event)
        sig_header = create_valid_signature(payload_str, webhook_secret, timestamp)

        tool = StripeHandleWebhooks(
            payload=payload_str,
            signature_header=sig_header,
            skip_signature_validation=False,
            tolerance=0
        )
        result = tool.run()
        assert result["success"] is True

        # Cleanup
        os.environ.pop("STRIPE_WEBHOOK_SECRET", None)

    def test_validation_invalid_tolerance(self):
        """Test validation for invalid tolerance values"""
        event = {"id": "evt_123", "type": "test", "data": {"object": {}}, "created": 123}

        with pytest.raises(ValueError):
            StripeHandleWebhooks(
                payload=json.dumps(event),
                signature_header="t=123,v1=sig",
                tolerance=-1  # Negative
            )

        with pytest.raises(ValueError):
            StripeHandleWebhooks(
                payload=json.dumps(event),
                signature_header="t=123,v1=sig",
                tolerance=3601  # Too large
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
