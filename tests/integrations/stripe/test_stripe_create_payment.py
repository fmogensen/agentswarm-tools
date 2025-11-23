"""
Tests for Stripe Create Payment Tool
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

from tools.integrations.stripe.stripe_create_payment import StripeCreatePayment
from shared.errors import ValidationError, APIError, AuthenticationError


@pytest.fixture
def mock_env():
    """Set up mock environment"""
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    os.environ.pop("USE_MOCK_APIS", None)


@pytest.fixture
def valid_payment_params():
    """Valid payment parameters"""
    return {
        "amount": 2000,
        "currency": "usd",
        "customer_email": "customer@example.com",
        "description": "Test payment",
    }


class TestStripeCreatePayment:
    """Test cases for StripeCreatePayment tool"""

    def test_initialization(self, valid_payment_params):
        """Test tool initialization"""
        tool = StripeCreatePayment(**valid_payment_params)
        assert tool.tool_name == "stripe_create_payment"
        assert tool.tool_category == "integrations"
        assert tool.amount == 2000
        assert tool.currency == "usd"
        assert tool.customer_email == "customer@example.com"

    def test_mock_mode_basic_payment(self, mock_env, valid_payment_params):
        """Test basic payment in mock mode"""
        tool = StripeCreatePayment(**valid_payment_params)
        result = tool.run()

        assert result["success"] is True
        assert result["payment_intent_id"].startswith("pi_mock_")
        assert result["status"] == "requires_payment_method"
        assert result["amount"] == 2000
        assert result["currency"] == "usd"
        assert "client_secret" in result
        assert result["metadata"]["mock_mode"] is True

    def test_mock_mode_confirmed_payment(self, mock_env):
        """Test auto-confirmed payment in mock mode"""
        tool = StripeCreatePayment(
            amount=5000,
            currency="usd",
            customer_email="test@example.com",
            confirm=True,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["status"] == "succeeded"
        assert result["amount"] == 5000

    def test_mock_mode_with_metadata(self, mock_env):
        """Test payment with metadata"""
        metadata = {"order_id": "12345", "customer_type": "premium"}
        tool = StripeCreatePayment(
            amount=3000,
            currency="usd",
            customer_email="premium@example.com",
            metadata=metadata,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["payment_intent_id"].startswith("pi_mock_")

    def test_multiple_currencies(self, mock_env):
        """Test support for multiple currencies"""
        currencies = ["usd", "eur", "gbp", "cad", "aud"]

        for currency in currencies:
            tool = StripeCreatePayment(
                amount=1000, currency=currency, customer_email="test@example.com"
            )
            result = tool.run()

            assert result["success"] is True
            assert result["currency"] == currency

    def test_validation_invalid_currency(self):
        """Test validation for invalid currency"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeCreatePayment(
                amount=1000, currency="xyz", customer_email="test@example.com"
            )
            tool.run()

        assert "Unsupported currency" in str(exc_info.value)

    def test_validation_invalid_email(self):
        """Test validation for invalid email"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeCreatePayment(
                amount=1000, currency="usd", customer_email="invalid-email"
            )
            tool.run()

        assert "email" in str(exc_info.value).lower()

    def test_validation_invalid_amount_negative(self):
        """Test validation for negative amount"""
        with pytest.raises(ValueError):
            StripeCreatePayment(
                amount=-100, currency="usd", customer_email="test@example.com"
            )

    def test_validation_invalid_amount_too_large(self):
        """Test validation for amount exceeding maximum"""
        with pytest.raises(ValueError):
            StripeCreatePayment(
                amount=100000000,  # Exceeds max
                currency="usd",
                customer_email="test@example.com",
            )

    def test_validation_invalid_payment_method(self, mock_env):
        """Test validation for invalid payment method type"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeCreatePayment(
                amount=1000,
                currency="usd",
                customer_email="test@example.com",
                payment_method_types=["invalid_method"],
            )
            tool.run()

        assert "Invalid payment method" in str(exc_info.value)

    def test_payment_method_types(self, mock_env):
        """Test various payment method types"""
        methods = ["card", "us_bank_account", "sepa_debit"]

        for method in methods:
            tool = StripeCreatePayment(
                amount=1000,
                currency="usd",
                customer_email="test@example.com",
                payment_method_types=[method],
            )
            result = tool.run()

            assert result["success"] is True

    @patch("tools.integrations.stripe.stripe_create_payment.stripe")
    def test_real_api_success(self, mock_stripe, valid_payment_params):
        """Test successful API call (mocked)"""
        # Configure mock
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        mock_intent = MagicMock()
        mock_intent.__getitem__.side_effect = lambda key: {
            "id": "pi_real_1234567890",
            "client_secret": "pi_real_1234567890_secret",
            "status": "requires_payment_method",
            "amount": 2000,
            "currency": "usd",
        }[key]

        mock_stripe.PaymentIntent.create.return_value = mock_intent

        tool = StripeCreatePayment(**valid_payment_params)
        result = tool.run()

        assert result["success"] is True
        assert result["payment_intent_id"] == "pi_real_1234567890"
        assert mock_stripe.PaymentIntent.create.called

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    @patch("tools.integrations.stripe.stripe_create_payment.stripe")
    def test_real_api_card_error(self, mock_stripe, valid_payment_params):
        """Test card error from API"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        # Import stripe module to access error classes
        import stripe as stripe_module

        mock_stripe.PaymentIntent.create.side_effect = stripe_module.error.CardError(
            message="Card declined",
            param="card",
            code="card_declined",
        )

        with pytest.raises(APIError) as exc_info:
            tool = StripeCreatePayment(**valid_payment_params)
            tool.run()

        assert "Card error" in str(exc_info.value)

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    def test_missing_api_key(self, valid_payment_params):
        """Test error when API key is missing"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ.pop("STRIPE_API_KEY", None)

        with pytest.raises(AuthenticationError) as exc_info:
            tool = StripeCreatePayment(**valid_payment_params)
            tool.run()

        assert "STRIPE_API_KEY" in str(exc_info.value)

    def test_description_length_limit(self, mock_env):
        """Test description length validation"""
        long_description = "x" * 1001  # Exceeds 1000 char limit

        with pytest.raises(ValueError):
            StripeCreatePayment(
                amount=1000,
                currency="usd",
                customer_email="test@example.com",
                description=long_description,
            )

    def test_edge_case_minimum_amount(self, mock_env):
        """Test minimum valid amount"""
        tool = StripeCreatePayment(
            amount=1, currency="usd", customer_email="test@example.com"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["amount"] == 1

    def test_edge_case_maximum_amount(self, mock_env):
        """Test maximum valid amount"""
        tool = StripeCreatePayment(
            amount=99999999,  # Max allowed
            currency="usd",
            customer_email="test@example.com",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["amount"] == 99999999

    def test_metadata_persistence(self, mock_env):
        """Test that metadata is included in result"""
        tool = StripeCreatePayment(
            amount=1000,
            currency="usd",
            customer_email="test@example.com",
            metadata={"custom_field": "value"},
        )
        result = tool.run()

        assert result["success"] is True
        assert "metadata" in result
        assert result["metadata"]["tool_name"] == "stripe_create_payment"

    def test_concurrent_payments(self, mock_env):
        """Test multiple payments can be created"""
        results = []

        for i in range(5):
            tool = StripeCreatePayment(
                amount=1000 * (i + 1),
                currency="usd",
                customer_email=f"customer{i}@example.com",
            )
            result = tool.run()
            results.append(result)

        assert len(results) == 5
        assert all(r["success"] for r in results)
        # Each should have unique payment intent ID
        intent_ids = [r["payment_intent_id"] for r in results]
        assert len(intent_ids) == len(set(intent_ids))  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
