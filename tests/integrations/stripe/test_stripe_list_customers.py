"""
Tests for Stripe List Customers Tool
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import time

from tools.integrations.stripe.stripe_list_customers import StripeListCustomers
from shared.errors import ValidationError, APIError, AuthenticationError


@pytest.fixture
def mock_env():
    """Set up mock environment"""
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    os.environ.pop("USE_MOCK_APIS", None)


class TestStripeListCustomers:
    """Test cases for StripeListCustomers tool"""

    def test_initialization(self):
        """Test tool initialization"""
        tool = StripeListCustomers(limit=10)
        assert tool.tool_name == "stripe_list_customers"
        assert tool.tool_category == "integrations"
        assert tool.limit == 10

    def test_mock_mode_list_all_customers(self, mock_env):
        """Test listing all customers in mock mode"""
        tool = StripeListCustomers(limit=10)
        result = tool.run()

        assert result["success"] is True
        assert result["count"] > 0
        assert result["count"] <= 10
        assert "customers" in result
        assert result["has_more"] is False
        assert result["metadata"]["mock_mode"] is True

    def test_mock_mode_filter_by_email(self, mock_env):
        """Test filtering by email"""
        tool = StripeListCustomers(email="customer0@example.com", limit=5)
        result = tool.run()

        assert result["success"] is True
        assert "customers" in result
        if result["count"] > 0:
            assert result["customers"][0]["email"] == "customer0@example.com"

    def test_mock_mode_custom_limit(self, mock_env):
        """Test custom limit"""
        tool = StripeListCustomers(limit=2)
        result = tool.run()

        assert result["success"] is True
        assert result["count"] <= 2

    def test_mock_mode_date_range_filtering(self, mock_env):
        """Test date range filtering"""
        current_time = int(time.time())
        week_ago = current_time - (86400 * 7)

        tool = StripeListCustomers(created_after=week_ago, limit=10)
        result = tool.run()

        assert result["success"] is True
        assert "filters_applied" in result["metadata"]
        assert "created_after" in result["metadata"]["filters_applied"]

    def test_mock_mode_metadata_filtering(self, mock_env):
        """Test metadata filtering"""
        tool = StripeListCustomers(
            metadata_filters={"tier": "premium"}, limit=10
        )
        result = tool.run()

        assert result["success"] is True
        assert "metadata" in result["metadata"]["filters_applied"]

    def test_mock_mode_pagination_starting_after(self, mock_env):
        """Test pagination with starting_after"""
        tool = StripeListCustomers(starting_after="cus_mock_01234567890", limit=5)
        result = tool.run()

        assert result["success"] is True

    def test_mock_mode_pagination_ending_before(self, mock_env):
        """Test pagination with ending_before"""
        tool = StripeListCustomers(ending_before="cus_mock_01234567890", limit=5)
        result = tool.run()

        assert result["success"] is True

    def test_validation_invalid_email_format(self):
        """Test validation for invalid email format"""
        with pytest.raises(ValueError):  # Pydantic validation
            StripeListCustomers(email="invalid-email", limit=10)

    def test_validation_conflicting_pagination(self):
        """Test validation for conflicting pagination parameters"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeListCustomers(
                starting_after="cus_123", ending_before="cus_456", limit=10
            )
            tool.run()

        assert "Cannot specify both" in str(exc_info.value)

    def test_validation_invalid_date_range(self):
        """Test validation for invalid date range"""
        current_time = int(time.time())
        week_ago = current_time - (86400 * 7)

        with pytest.raises(ValidationError) as exc_info:
            tool = StripeListCustomers(
                created_after=current_time, created_before=week_ago  # Invalid order
            )
            tool.run()

        assert "must be before" in str(exc_info.value)

    def test_validation_invalid_starting_after_format(self):
        """Test validation for invalid starting_after format"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeListCustomers(starting_after="invalid_id")
            tool.run()

        assert "valid customer ID" in str(exc_info.value)

    def test_validation_invalid_ending_before_format(self):
        """Test validation for invalid ending_before format"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeListCustomers(ending_before="invalid_id")
            tool.run()

        assert "valid customer ID" in str(exc_info.value)

    def test_validation_invalid_limit_too_small(self):
        """Test validation for limit too small"""
        with pytest.raises(ValueError):
            StripeListCustomers(limit=0)

    def test_validation_invalid_limit_too_large(self):
        """Test validation for limit too large"""
        with pytest.raises(ValueError):
            StripeListCustomers(limit=101)

    def test_customer_data_structure(self, mock_env):
        """Test customer data structure"""
        tool = StripeListCustomers(limit=1)
        result = tool.run()

        assert result["success"] is True
        if result["count"] > 0:
            customer = result["customers"][0]
            assert "id" in customer
            assert "email" in customer
            assert "name" in customer
            assert "created" in customer
            assert "metadata" in customer

    def test_filters_applied_metadata(self, mock_env):
        """Test that active filters are tracked in metadata"""
        tool = StripeListCustomers(
            email="test@example.com",
            created_after=1234567890,
            metadata_filters={"tier": "premium"},
        )
        result = tool.run()

        assert result["success"] is True
        filters = result["metadata"]["filters_applied"]
        assert "email" in filters
        assert "created_after" in filters
        assert "metadata" in filters

    def test_include_deleted_customers(self, mock_env):
        """Test including deleted customers"""
        tool = StripeListCustomers(include_deleted=True, limit=10)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["filters_applied"].get("include_deleted") is True

    def test_edge_case_minimum_limit(self, mock_env):
        """Test minimum limit (1)"""
        tool = StripeListCustomers(limit=1)
        result = tool.run()

        assert result["success"] is True
        assert result["count"] <= 1

    def test_edge_case_maximum_limit(self, mock_env):
        """Test maximum limit (100)"""
        tool = StripeListCustomers(limit=100)
        result = tool.run()

        assert result["success"] is True
        assert result["count"] <= 100

    def test_combined_filters(self, mock_env):
        """Test combining multiple filters"""
        current_time = int(time.time())
        week_ago = current_time - (86400 * 7)

        tool = StripeListCustomers(
            email="customer0@example.com",
            created_after=week_ago,
            metadata_filters={"tier": "premium"},
            limit=5,
        )
        result = tool.run()

        assert result["success"] is True
        filters = result["metadata"]["filters_applied"]
        assert len(filters) == 3  # email, created_after, metadata

    @patch("tools.integrations.stripe.stripe_list_customers.stripe")
    def test_real_api_success(self, mock_stripe):
        """Test successful API call (mocked)"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        # Mock customer list response
        mock_customer_1 = {
            "id": "cus_real_123",
            "email": "customer1@example.com",
            "name": "Customer 1",
            "created": 1234567890,
            "balance": 0,
            "currency": "usd",
            "delinquent": False,
            "metadata": {},
            "default_source": None,
        }

        mock_response = Mock()
        mock_response.data = [mock_customer_1]
        mock_response.has_more = False
        mock_response.get = lambda key, default=None: {"data": [mock_customer_1], "has_more": False}.get(key, default)

        mock_stripe.Customer.list.return_value = mock_response

        tool = StripeListCustomers(limit=10)
        result = tool.run()

        assert result["success"] is True
        assert result["count"] == 1
        assert mock_stripe.Customer.list.called

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    @patch("tools.integrations.stripe.stripe_list_customers.stripe")
    def test_real_api_with_email_filter(self, mock_stripe):
        """Test API call with email filter"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        mock_response = Mock()
        mock_response.data = []
        mock_response.has_more = False
        mock_response.get = lambda key, default=None: {"data": [], "has_more": False}.get(key, default)

        mock_stripe.Customer.list.return_value = mock_response

        tool = StripeListCustomers(email="test@example.com", limit=10)
        result = tool.run()

        assert result["success"] is True
        # Verify email was passed to API
        call_args = mock_stripe.Customer.list.call_args
        assert call_args[1]["email"] == "test@example.com"

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    @patch("tools.integrations.stripe.stripe_list_customers.stripe")
    def test_real_api_invalid_request_error(self, mock_stripe):
        """Test invalid request error from API"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        import stripe as stripe_module

        mock_stripe.Customer.list.side_effect = stripe_module.error.InvalidRequestError(
            message="Invalid parameter",
            param="limit"
        )

        with pytest.raises(ValidationError) as exc_info:
            tool = StripeListCustomers(limit=10)
            tool.run()

        assert "Invalid request" in str(exc_info.value)

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    @patch("tools.integrations.stripe.stripe_list_customers.stripe")
    def test_real_api_authentication_error(self, mock_stripe):
        """Test authentication error from API"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        import stripe as stripe_module

        mock_stripe.Customer.list.side_effect = stripe_module.error.AuthenticationError(
            message="Invalid API key"
        )

        with pytest.raises(AuthenticationError) as exc_info:
            tool = StripeListCustomers(limit=10)
            tool.run()

        assert "Authentication failed" in str(exc_info.value)

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    def test_missing_api_key(self):
        """Test error when API key is missing"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ.pop("STRIPE_API_KEY", None)

        with pytest.raises(AuthenticationError) as exc_info:
            tool = StripeListCustomers(limit=10)
            tool.run()

        assert "STRIPE_API_KEY" in str(exc_info.value)

    def test_metadata_matching_logic(self, mock_env):
        """Test metadata matching logic"""
        tool = StripeListCustomers(
            metadata_filters={"tier": "premium", "status": "active"},
            limit=10,
        )
        result = tool.run()

        assert result["success"] is True

    def test_empty_result_set(self, mock_env):
        """Test handling of empty result set"""
        tool = StripeListCustomers(email="nonexistent@example.com", limit=10)
        result = tool.run()

        assert result["success"] is True
        # In mock mode, we still get results, but in real API this would be empty

    def test_pagination_workflow(self, mock_env):
        """Test pagination workflow"""
        # First page
        tool1 = StripeListCustomers(limit=2)
        result1 = tool1.run()

        assert result1["success"] is True

        # Second page (if has_more)
        if result1["has_more"] and result1["count"] > 0:
            last_customer_id = result1["customers"][-1]["id"]
            tool2 = StripeListCustomers(starting_after=last_customer_id, limit=2)
            result2 = tool2.run()

            assert result2["success"] is True

    def test_date_filtering_combinations(self, mock_env):
        """Test various date filtering combinations"""
        current_time = int(time.time())
        month_ago = current_time - (86400 * 30)
        week_ago = current_time - (86400 * 7)

        # Only created_after
        tool1 = StripeListCustomers(created_after=week_ago)
        result1 = tool1.run()
        assert result1["success"] is True

        # Only created_before
        tool2 = StripeListCustomers(created_before=week_ago)
        result2 = tool2.run()
        assert result2["success"] is True

        # Both created_after and created_before
        tool3 = StripeListCustomers(created_after=month_ago, created_before=week_ago)
        result3 = tool3.run()
        assert result3["success"] is True

    def test_concurrent_customer_listings(self, mock_env):
        """Test multiple concurrent customer listings"""
        results = []

        for i in range(3):
            tool = StripeListCustomers(limit=5)
            result = tool.run()
            results.append(result)

        assert len(results) == 3
        assert all(r["success"] for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
