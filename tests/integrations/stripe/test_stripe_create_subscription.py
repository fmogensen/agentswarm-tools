"""
Tests for Stripe Create Subscription Tool
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import time

from tools.integrations.stripe.stripe_create_subscription import StripeCreateSubscription
from shared.errors import ValidationError, APIError, AuthenticationError


@pytest.fixture
def mock_env():
    """Set up mock environment"""
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    os.environ.pop("USE_MOCK_APIS", None)


@pytest.fixture
def valid_subscription_params():
    """Valid subscription parameters"""
    return {
        "customer_id": "cus_1234567890",
        "price_id": "price_monthly_premium",
    }


class TestStripeCreateSubscription:
    """Test cases for StripeCreateSubscription tool"""

    def test_initialization(self, valid_subscription_params):
        """Test tool initialization"""
        tool = StripeCreateSubscription(**valid_subscription_params)
        assert tool.tool_name == "stripe_create_subscription"
        assert tool.tool_category == "integrations"
        assert tool.customer_id == "cus_1234567890"
        assert tool.price_id == "price_monthly_premium"

    def test_mock_mode_basic_subscription(self, mock_env, valid_subscription_params):
        """Test basic subscription creation in mock mode"""
        tool = StripeCreateSubscription(**valid_subscription_params)
        result = tool.run()

        assert result["success"] is True
        assert result["subscription_id"].startswith("sub_mock_")
        assert result["customer_id"] == "cus_1234567890"
        assert result["status"] == "active"
        assert "current_period_end" in result
        assert result["metadata"]["mock_mode"] is True

    def test_mock_mode_subscription_with_trial(self, mock_env):
        """Test subscription with trial period"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            trial_period_days=14,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["status"] == "trialing"
        assert result["trial_end"] is not None
        assert result["trial_end"] > int(time.time())

    def test_mock_mode_yearly_subscription(self, mock_env):
        """Test yearly subscription"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_yearly_enterprise",
            billing_interval="yearly",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["billing_interval"] == "yearly"

    def test_mock_mode_subscription_with_quantity(self, mock_env):
        """Test subscription with quantity"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            quantity=5,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["subscription_id"].startswith("sub_mock_")

    def test_mock_mode_subscription_with_payment_method(self, mock_env):
        """Test subscription with payment method"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            payment_method_id="pm_1234567890",
        )
        result = tool.run()

        assert result["success"] is True

    def test_mock_mode_subscription_with_metadata(self, mock_env):
        """Test subscription with metadata"""
        metadata = {"team": "engineering", "seats": "5"}
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            metadata=metadata,
        )
        result = tool.run()

        assert result["success"] is True

    def test_mock_mode_create_customer_from_email(self, mock_env):
        """Test creating customer from email"""
        tool = StripeCreateSubscription(
            customer_id="newcustomer@example.com",  # Email instead of ID
            price_id="price_monthly_basic",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["customer_id"].startswith("cus_")
        assert result["customer_id"] != "newcustomer@example.com"

    def test_validation_invalid_billing_interval(self):
        """Test validation for invalid billing interval"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeCreateSubscription(
                customer_id="cus_1234567890",
                price_id="price_monthly_premium",
                billing_interval="invalid",
            )
            tool.run()

        assert "Invalid billing interval" in str(exc_info.value)

    def test_validation_invalid_customer_id_format(self):
        """Test validation for invalid customer ID format"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeCreateSubscription(
                customer_id="cus_123",  # Too short
                price_id="price_monthly_premium",
            )
            tool.run()

        assert "Invalid customer ID" in str(exc_info.value)

    def test_validation_invalid_price_id_format(self):
        """Test validation for invalid price ID format"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeCreateSubscription(
                customer_id="cus_1234567890",
                price_id="invalid_format",  # Doesn't start with price_ or plan_
            )
            tool.run()

        assert "Invalid price ID" in str(exc_info.value)

    def test_validation_invalid_trial_period_negative(self):
        """Test validation for negative trial period"""
        with pytest.raises(ValueError):
            StripeCreateSubscription(
                customer_id="cus_1234567890",
                price_id="price_monthly_premium",
                trial_period_days=-1,
            )

    def test_validation_invalid_trial_period_too_large(self):
        """Test validation for trial period exceeding maximum"""
        with pytest.raises(ValueError):
            StripeCreateSubscription(
                customer_id="cus_1234567890",
                price_id="price_monthly_premium",
                trial_period_days=1000,  # Exceeds 730 max
            )

    def test_validation_invalid_quantity_zero(self):
        """Test validation for quantity of zero"""
        with pytest.raises(ValueError):
            StripeCreateSubscription(
                customer_id="cus_1234567890",
                price_id="price_monthly_premium",
                quantity=0,
            )

    def test_validation_invalid_quantity_too_large(self):
        """Test validation for quantity exceeding maximum"""
        with pytest.raises(ValueError):
            StripeCreateSubscription(
                customer_id="cus_1234567890",
                price_id="price_monthly_premium",
                quantity=101,  # Exceeds 100 max
            )

    def test_billing_intervals(self, mock_env):
        """Test all valid billing intervals"""
        intervals = ["monthly", "yearly", "weekly", "daily"]

        for interval in intervals:
            tool = StripeCreateSubscription(
                customer_id="cus_1234567890",
                price_id="price_premium",
                billing_interval=interval,
            )
            result = tool.run()

            assert result["success"] is True
            assert result["metadata"]["billing_interval"] == interval

    def test_trial_periods(self, mock_env):
        """Test various trial period lengths"""
        trial_periods = [0, 7, 14, 30, 90, 365]

        for days in trial_periods:
            tool = StripeCreateSubscription(
                customer_id="cus_1234567890",
                price_id="price_monthly_premium",
                trial_period_days=days,
            )
            result = tool.run()

            assert result["success"] is True
            if days > 0:
                assert result["status"] == "trialing"
                assert result["trial_end"] is not None
            else:
                assert result["status"] == "active"
                assert result["trial_end"] is None

    def test_current_period_end_calculation(self, mock_env):
        """Test that current_period_end is in the future"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["current_period_end"] > int(time.time())

    @patch("tools.integrations.stripe.stripe_create_subscription.stripe")
    def test_real_api_success(self, mock_stripe, valid_subscription_params):
        """Test successful API call (mocked)"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        current_time = int(time.time())
        mock_subscription = MagicMock()
        mock_subscription.__getitem__.side_effect = lambda key: {
            "id": "sub_real_1234567890",
            "customer": "cus_1234567890",
            "status": "active",
            "current_period_end": current_time + 2592000,
            "trial_end": None,
        }[key]
        mock_subscription.get = lambda key, default=None: {
            "id": "sub_real_1234567890",
            "customer": "cus_1234567890",
            "status": "active",
            "current_period_end": current_time + 2592000,
            "trial_end": None,
        }.get(key, default)

        mock_stripe.Subscription.create.return_value = mock_subscription

        tool = StripeCreateSubscription(**valid_subscription_params)
        result = tool.run()

        assert result["success"] is True
        assert result["subscription_id"] == "sub_real_1234567890"
        assert mock_stripe.Subscription.create.called

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    @patch("tools.integrations.stripe.stripe_create_subscription.stripe")
    def test_real_api_create_customer(self, mock_stripe, valid_subscription_params):
        """Test creating customer from email via API"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        # Mock customer creation
        mock_customer = Mock()
        mock_customer.id = "cus_new_1234567890"
        mock_stripe.Customer.create.return_value = mock_customer

        # Mock subscription creation
        current_time = int(time.time())
        mock_subscription = MagicMock()
        mock_subscription.__getitem__.side_effect = lambda key: {
            "id": "sub_new_1234567890",
            "customer": "cus_new_1234567890",
            "status": "active",
            "current_period_end": current_time + 2592000,
            "trial_end": None,
        }[key]
        mock_subscription.get = lambda key, default=None: {
            "id": "sub_new_1234567890",
            "customer": "cus_new_1234567890",
            "status": "active",
            "current_period_end": current_time + 2592000,
            "trial_end": None,
        }.get(key, default)

        mock_stripe.Subscription.create.return_value = mock_subscription

        tool = StripeCreateSubscription(
            customer_id="newcustomer@example.com",
            price_id="price_monthly_premium",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["customer_id"] == "cus_new_1234567890"
        assert mock_stripe.Customer.create.called
        assert mock_stripe.Subscription.create.called

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    @patch("tools.integrations.stripe.stripe_create_subscription.stripe")
    def test_real_api_invalid_request_error(self, mock_stripe, valid_subscription_params):
        """Test invalid request error from API"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        import stripe as stripe_module

        mock_stripe.Subscription.create.side_effect = stripe_module.error.InvalidRequestError(
            message="Invalid price",
            param="price"
        )

        with pytest.raises(ValidationError) as exc_info:
            tool = StripeCreateSubscription(**valid_subscription_params)
            tool.run()

        assert "Invalid request" in str(exc_info.value)

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    @patch("tools.integrations.stripe.stripe_create_subscription.stripe")
    def test_real_api_authentication_error(self, mock_stripe, valid_subscription_params):
        """Test authentication error from API"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        import stripe as stripe_module

        mock_stripe.Subscription.create.side_effect = stripe_module.error.AuthenticationError(
            message="Invalid API key"
        )

        with pytest.raises(AuthenticationError) as exc_info:
            tool = StripeCreateSubscription(**valid_subscription_params)
            tool.run()

        assert "Authentication failed" in str(exc_info.value)

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    def test_missing_api_key(self, valid_subscription_params):
        """Test error when API key is missing"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ.pop("STRIPE_API_KEY", None)

        with pytest.raises(AuthenticationError) as exc_info:
            tool = StripeCreateSubscription(**valid_subscription_params)
            tool.run()

        assert "STRIPE_API_KEY" in str(exc_info.value)

    def test_price_id_with_plan_prefix(self, mock_env):
        """Test price ID starting with 'plan_' (legacy format)"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="plan_legacy_premium",  # Legacy format
        )
        result = tool.run()

        assert result["success"] is True

    def test_metadata_persistence(self, mock_env):
        """Test that metadata is included in result"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            metadata={"custom_field": "value"},
        )
        result = tool.run()

        assert result["success"] is True
        assert "metadata" in result
        assert result["metadata"]["tool_name"] == "stripe_create_subscription"
        assert result["metadata"]["price_id"] == "price_monthly_premium"

    def test_concurrent_subscriptions(self, mock_env):
        """Test creating multiple subscriptions"""
        results = []

        for i in range(3):
            tool = StripeCreateSubscription(
                customer_id=f"cus_{i}234567890",
                price_id="price_monthly_premium",
            )
            result = tool.run()
            results.append(result)

        assert len(results) == 3
        assert all(r["success"] for r in results)
        # Each should have unique subscription ID
        sub_ids = [r["subscription_id"] for r in results]
        assert len(sub_ids) == len(set(sub_ids))  # All unique

    def test_edge_case_minimum_trial_period(self, mock_env):
        """Test minimum trial period (0 days)"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            trial_period_days=0,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["status"] == "active"
        assert result["trial_end"] is None

    def test_edge_case_maximum_trial_period(self, mock_env):
        """Test maximum trial period (730 days)"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            trial_period_days=730,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["status"] == "trialing"
        assert result["trial_end"] is not None

    def test_edge_case_minimum_quantity(self, mock_env):
        """Test minimum quantity (1)"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            quantity=1,
        )
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_maximum_quantity(self, mock_env):
        """Test maximum quantity (100)"""
        tool = StripeCreateSubscription(
            customer_id="cus_1234567890",
            price_id="price_monthly_premium",
            quantity=100,
        )
        result = tool.run()

        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
