"""
Tests for Stripe Get Invoices Tool
"""

import os
import time
from unittest.mock import Mock, patch

import pytest

from shared.errors import APIError, AuthenticationError, ValidationError
from tools.integrations.stripe.stripe_get_invoices import StripeGetInvoices


@pytest.fixture
def mock_env():
    """Set up mock environment"""
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    os.environ.pop("USE_MOCK_APIS", None)


class TestStripeGetInvoices:
    """Test cases for StripeGetInvoices tool"""

    def test_initialization(self):
        """Test tool initialization"""
        tool = StripeGetInvoices(limit=10)
        assert tool.tool_name == "stripe_get_invoices"
        assert tool.tool_category == "integrations"
        assert tool.limit == 10

    def test_mock_mode_get_all_invoices(self, mock_env):
        """Test getting all invoices in mock mode"""
        tool = StripeGetInvoices(limit=10)
        result = tool.run()

        assert result["success"] is True
        assert result["count"] > 0
        assert "invoices" in result
        assert result["has_more"] is False

    def test_mock_mode_filter_by_customer(self, mock_env):
        """Test filtering by customer"""
        tool = StripeGetInvoices(customer_id="cus_1234567890", limit=5)
        result = tool.run()

        assert result["success"] is True
        assert "invoices" in result

    def test_mock_mode_filter_by_status_paid(self, mock_env):
        """Test filtering by paid status"""
        tool = StripeGetInvoices(status="paid", limit=10)
        result = tool.run()

        assert result["success"] is True
        for invoice in result["invoices"]:
            assert invoice["status"] == "paid"

    def test_mock_mode_filter_by_status_open(self, mock_env):
        """Test filtering by open status"""
        tool = StripeGetInvoices(status="open", limit=10)
        result = tool.run()

        assert result["success"] is True

    def test_mock_mode_filter_by_subscription(self, mock_env):
        """Test filtering by subscription"""
        tool = StripeGetInvoices(subscription_id="sub_1234567890", limit=10)
        result = tool.run()

        assert result["success"] is True
        filters = result["metadata"]["filters_applied"]
        assert "subscription_id" in filters

    def test_mock_mode_include_total_count(self, mock_env):
        """Test including total count"""
        tool = StripeGetInvoices(include_total_count=True, limit=5)
        result = tool.run()

        assert result["success"] is True
        assert "total_count" in result
        assert result["total_count"] is not None

    def test_invoice_data_structure(self, mock_env):
        """Test invoice data structure"""
        tool = StripeGetInvoices(limit=1)
        result = tool.run()

        assert result["success"] is True
        if result["count"] > 0:
            invoice = result["invoices"][0]
            assert "id" in invoice
            assert "customer" in invoice
            assert "status" in invoice
            assert "amount_due" in invoice
            assert "number" in invoice
            assert "invoice_pdf" in invoice

    def test_validation_invalid_status(self):
        """Test validation for invalid status"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeGetInvoices(status="invalid_status")
            tool.run()

        assert "Invalid status" in str(exc_info.value)

    def test_validation_all_valid_statuses(self, mock_env):
        """Test all valid invoice statuses"""
        statuses = ["draft", "open", "paid", "void", "uncollectible"]

        for status in statuses:
            tool = StripeGetInvoices(status=status, limit=5)
            result = tool.run()
            assert result["success"] is True

    def test_validation_conflicting_pagination(self):
        """Test validation for conflicting pagination"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeGetInvoices(starting_after="in_123", ending_before="in_456")
            tool.run()

        assert "Cannot specify both" in str(exc_info.value)

    def test_validation_invalid_date_ranges(self):
        """Test validation for invalid date ranges"""
        current_time = int(time.time())
        week_ago = current_time - (86400 * 7)

        # Invalid created range
        with pytest.raises(ValidationError):
            tool = StripeGetInvoices(created_after=current_time, created_before=week_ago)
            tool.run()

        # Invalid due_date range
        with pytest.raises(ValidationError):
            tool = StripeGetInvoices(due_date_after=current_time, due_date_before=week_ago)
            tool.run()

    def test_validation_invalid_customer_id(self):
        """Test validation for invalid customer ID"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeGetInvoices(customer_id="invalid_id")
            tool.run()

        assert "valid Stripe customer ID" in str(exc_info.value)

    def test_validation_invalid_subscription_id(self):
        """Test validation for invalid subscription ID"""
        with pytest.raises(ValidationError) as exc_info:
            tool = StripeGetInvoices(subscription_id="invalid_id")
            tool.run()

        assert "valid Stripe subscription ID" in str(exc_info.value)

    def test_validation_invalid_invoice_id_formats(self):
        """Test validation for invalid invoice ID formats in pagination"""
        with pytest.raises(ValidationError):
            tool = StripeGetInvoices(starting_after="invalid_id")
            tool.run()

        with pytest.raises(ValidationError):
            tool = StripeGetInvoices(ending_before="invalid_id")
            tool.run()

    def test_date_range_filtering(self, mock_env):
        """Test date range filtering"""
        current_time = int(time.time())
        week_ago = current_time - (86400 * 7)

        tool = StripeGetInvoices(created_after=week_ago, limit=10)
        result = tool.run()

        assert result["success"] is True
        assert "created_after" in result["metadata"]["filters_applied"]

    def test_due_date_filtering(self, mock_env):
        """Test due date filtering"""
        current_time = int(time.time())
        month_from_now = current_time + (86400 * 30)

        tool = StripeGetInvoices(due_date_after=current_time, due_date_before=month_from_now)
        result = tool.run()

        assert result["success"] is True
        filters = result["metadata"]["filters_applied"]
        assert "due_date_after" in filters
        assert "due_date_before" in filters

    def test_combined_filters(self, mock_env):
        """Test combining multiple filters"""
        current_time = int(time.time())
        week_ago = current_time - (86400 * 7)

        tool = StripeGetInvoices(
            customer_id="cus_1234567890",
            status="paid",
            created_after=week_ago,
            limit=5,
        )
        result = tool.run()

        assert result["success"] is True
        filters = result["metadata"]["filters_applied"]
        assert len(filters) >= 3

    def test_pagination_workflow(self, mock_env):
        """Test pagination workflow"""
        # First page
        tool1 = StripeGetInvoices(limit=2)
        result1 = tool1.run()

        assert result1["success"] is True

        # Second page using starting_after
        if result1["has_more"] and result1["count"] > 0:
            last_invoice_id = result1["invoices"][-1]["id"]
            tool2 = StripeGetInvoices(starting_after=last_invoice_id, limit=2)
            result2 = tool2.run()

            assert result2["success"] is True

    def test_edge_case_minimum_limit(self, mock_env):
        """Test minimum limit (1)"""
        tool = StripeGetInvoices(limit=1)
        result = tool.run()

        assert result["success"] is True
        assert result["count"] <= 1

    def test_edge_case_maximum_limit(self, mock_env):
        """Test maximum limit (100)"""
        tool = StripeGetInvoices(limit=100)
        result = tool.run()

        assert result["success"] is True
        assert result["count"] <= 100

    def test_validation_invalid_limit_values(self):
        """Test validation for invalid limit values"""
        with pytest.raises(ValueError):
            StripeGetInvoices(limit=0)

        with pytest.raises(ValueError):
            StripeGetInvoices(limit=101)

    @patch("tools.integrations.stripe.stripe_get_invoices.stripe")
    def test_real_api_success(self, mock_stripe):
        """Test successful API call (mocked)"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        mock_invoice = {
            "id": "in_real_123",
            "customer": "cus_123",
            "status": "paid",
            "amount_due": 2000,
            "number": "INV-001",
        }

        mock_response = Mock()
        mock_response.data = [mock_invoice]
        mock_response.has_more = False
        mock_response.get = lambda key, default=None: {
            "data": [mock_invoice],
            "has_more": False,
        }.get(key, default)

        mock_stripe.Invoice.list.return_value = mock_response

        tool = StripeGetInvoices(limit=10)
        result = tool.run()

        assert result["success"] is True
        assert result["count"] == 1
        assert mock_stripe.Invoice.list.called

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    @patch("tools.integrations.stripe.stripe_get_invoices.stripe")
    def test_real_api_with_filters(self, mock_stripe):
        """Test API call with multiple filters"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["STRIPE_API_KEY"] = "sk_test_mock_key"

        mock_response = Mock()
        mock_response.data = []
        mock_response.has_more = False
        mock_response.get = lambda key, default=None: {"data": [], "has_more": False}.get(
            key, default
        )

        mock_stripe.Invoice.list.return_value = mock_response

        tool = StripeGetInvoices(customer_id="cus_123", status="paid", limit=10)
        result = tool.run()

        assert result["success"] is True
        call_args = mock_stripe.Invoice.list.call_args[1]
        assert call_args["customer"] == "cus_123"
        assert call_args["status"] == "paid"

        # Cleanup
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ.pop("STRIPE_API_KEY", None)

    def test_missing_api_key(self):
        """Test error when API key is missing"""
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ.pop("STRIPE_API_KEY", None)

        with pytest.raises(AuthenticationError) as exc_info:
            tool = StripeGetInvoices(limit=10)
            tool.run()

        assert "STRIPE_API_KEY" in str(exc_info.value)

    def test_concurrent_invoice_retrievals(self, mock_env):
        """Test multiple concurrent invoice retrievals"""
        results = []

        for i in range(3):
            tool = StripeGetInvoices(limit=5)
            result = tool.run()
            results.append(result)

        assert len(results) == 3
        assert all(r["success"] for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
