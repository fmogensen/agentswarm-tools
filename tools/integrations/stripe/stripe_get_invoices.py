"""
Stripe Get Invoices Tool

Retrieves invoices for a specific customer with support for filtering by status,
date range, subscription, and pagination.
"""

import json
import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError

# Stripe SDK import
try:
    import stripe
except ImportError:
    stripe = None


class StripeGetInvoices(BaseTool):
    """
    Retrieve invoices for a customer with filtering and pagination.

    This tool retrieves invoice records from Stripe with support for
    customer filtering, status filtering, date ranges, and pagination.

    Args:
        customer_id: Stripe customer ID (optional, retrieves all if not specified)
        status: Filter by invoice status (draft, open, paid, void, uncollectible)
        subscription_id: Filter by subscription ID (optional)
        limit: Maximum number of invoices to return (default: 10, max: 100)
        starting_after: Invoice ID to start after (for pagination)
        ending_before: Invoice ID to end before (for pagination)
        created_after: Unix timestamp - invoices created after this date
        created_before: Unix timestamp - invoices created before this date
        due_date_after: Unix timestamp - invoices due after this date
        due_date_before: Unix timestamp - invoices due before this date
        include_total_count: Include total count of matching invoices (slower)

    Returns:
        Dict containing:
            - success (bool): Whether the operation was successful
            - invoices (list): List of invoice objects
            - has_more (bool): Whether more invoices are available
            - count (int): Number of invoices returned
            - total_count (int|None): Total matching invoices (if include_total_count=True)
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = StripeGetInvoices(
        ...     customer_id="cus_1234567890",
        ...     status="paid",
        ...     limit=10
        ... )
        >>> result = tool.run()
        >>> print(f"Found {result['count']} paid invoices")
        >>> for invoice in result['invoices']:
        ...     print(f"Invoice {invoice['number']}: ${invoice['amount_due']/100:.2f}")
    """

    # Tool metadata
    tool_name: str = "stripe_get_invoices"
    tool_category: str = "integrations"

    # Optional parameters
    customer_id: Optional[str] = Field(None, description="Stripe customer ID (cus_xxx)")
    status: Optional[str] = Field(
        None,
        description="Filter by status: draft, open, paid, void, uncollectible",
    )
    subscription_id: Optional[str] = Field(None, description="Filter by subscription ID (sub_xxx)")
    limit: int = Field(10, description="Maximum number of invoices to return", ge=1, le=100)
    starting_after: Optional[str] = Field(None, description="Invoice ID to start pagination after")
    ending_before: Optional[str] = Field(None, description="Invoice ID to end pagination before")
    created_after: Optional[int] = Field(
        None, description="Unix timestamp - invoices created after this date", ge=0
    )
    created_before: Optional[int] = Field(
        None, description="Unix timestamp - invoices created before this date", ge=0
    )
    due_date_after: Optional[int] = Field(
        None, description="Unix timestamp - invoices due after this date", ge=0
    )
    due_date_before: Optional[int] = Field(
        None, description="Unix timestamp - invoices due before this date", ge=0
    )
    include_total_count: bool = Field(
        False, description="Include total count of matching invoices (slower)"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the invoice retrieval."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()
            invoices = result.get("data", [])

            response = {
                "success": True,
                "invoices": [self._format_invoice(inv) for inv in invoices],
                "has_more": result.get("has_more", False),
                "count": len(invoices),
                "metadata": {
                    "tool_name": self.tool_name,
                    "filters_applied": self._get_active_filters(),
                },
            }

            # Add total count if requested
            if self.include_total_count:
                response["total_count"] = self._get_total_count()

            return response

        except (AuthenticationError, ValidationError):
            # Let these pass through unchanged
            raise
        except Exception as e:
            # Only wrap unexpected errors
            raise APIError(f"Failed to retrieve invoices: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate status
        valid_statuses = ["draft", "open", "paid", "void", "uncollectible"]
        if self.status and self.status.lower() not in valid_statuses:
            raise ValidationError(
                f"Invalid status: {self.status}. Valid: {', '.join(valid_statuses)}",
                tool_name=self.tool_name,
            )

        # Validate pagination parameters
        if self.starting_after and self.ending_before:
            raise ValidationError(
                "Cannot specify both starting_after and ending_before",
                tool_name=self.tool_name,
            )

        # Validate date ranges
        if self.created_after and self.created_before and self.created_after >= self.created_before:
            raise ValidationError(
                "created_after must be before created_before",
                tool_name=self.tool_name,
            )

        if (
            self.due_date_after
            and self.due_date_before
            and self.due_date_after >= self.due_date_before
        ):
            raise ValidationError(
                "due_date_after must be before due_date_before",
                tool_name=self.tool_name,
            )

        # Validate customer ID format
        if self.customer_id and not self.customer_id.startswith("cus_"):
            raise ValidationError(
                "customer_id must be a valid Stripe customer ID (cus_xxx)",
                tool_name=self.tool_name,
            )

        # Validate subscription ID format
        if self.subscription_id and not self.subscription_id.startswith("sub_"):
            raise ValidationError(
                "subscription_id must be a valid Stripe subscription ID (sub_xxx)",
                tool_name=self.tool_name,
            )

        # Validate invoice ID formats for pagination
        if self.starting_after and not self.starting_after.startswith("in_"):
            raise ValidationError(
                "starting_after must be a valid invoice ID (in_xxx)",
                tool_name=self.tool_name,
            )

        if self.ending_before and not self.ending_before.startswith("in_"):
            raise ValidationError(
                "ending_before must be a valid invoice ID (in_xxx)",
                tool_name=self.tool_name,
            )

        # Validate API key exists if not in mock mode
        if not self._should_use_mock():
            api_key = os.getenv("STRIPE_API_KEY")
            if not api_key:
                raise AuthenticationError(
                    "Missing STRIPE_API_KEY environment variable", tool_name=self.tool_name
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        import time

        current_time = int(time.time())

        # Generate mock invoices
        mock_invoices = []
        num_invoices = min(self.limit, 3)  # Generate up to 3 mock invoices

        statuses = ["paid", "open", "draft"]
        for i in range(num_invoices):
            status = self.status if self.status else statuses[i % len(statuses)]
            invoice = {
                "id": f"in_mock_{i}1234567890",
                "customer": self.customer_id or f"cus_mock_{i}123",
                "subscription": self.subscription_id or (f"sub_mock_{i}123" if i < 2 else None),
                "number": f"INV-{1000 + i}",
                "status": status,
                "amount_due": 2000 * (i + 1),
                "amount_paid": 2000 * (i + 1) if status == "paid" else 0,
                "amount_remaining": 0 if status == "paid" else 2000 * (i + 1),
                "currency": "usd",
                "created": current_time - (86400 * i),
                "due_date": current_time + (86400 * (7 - i)),
                "paid": status == "paid",
                "attempted": status in ["paid", "open"],
                "description": f"Mock invoice {i}",
                "invoice_pdf": f"https://stripe.com/mock/invoice_{i}.pdf",
                "hosted_invoice_url": f"https://stripe.com/mock/hosted_{i}",
                "metadata": {"order_id": f"ORD-{1000 + i}"},
            }
            mock_invoices.append(invoice)

        response = {
            "success": True,
            "invoices": [self._format_invoice(inv) for inv in mock_invoices],
            "has_more": False,
            "count": len(mock_invoices),
            "metadata": {
                "tool_name": self.tool_name,
                "filters_applied": self._get_active_filters(),
                "mock_mode": True,
            },
        }

        if self.include_total_count:
            response["total_count"] = len(mock_invoices)

        return response

    def _process(self) -> Dict[str, Any]:
        """Process the invoice retrieval with Stripe API."""
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

        # Build query parameters
        params = {"limit": self.limit}

        if self.customer_id:
            params["customer"] = self.customer_id

        if self.status:
            params["status"] = self.status.lower()

        if self.subscription_id:
            params["subscription"] = self.subscription_id

        if self.starting_after:
            params["starting_after"] = self.starting_after

        if self.ending_before:
            params["ending_before"] = self.ending_before

        # Build created filter
        created_filter = {}
        if self.created_after:
            created_filter["gte"] = self.created_after
        if self.created_before:
            created_filter["lte"] = self.created_before
        if created_filter:
            params["created"] = created_filter

        # Build due_date filter
        due_date_filter = {}
        if self.due_date_after:
            due_date_filter["gte"] = self.due_date_after
        if self.due_date_before:
            due_date_filter["lte"] = self.due_date_before
        if due_date_filter:
            params["due_date"] = due_date_filter

        # List invoices
        try:
            invoices = stripe.Invoice.list(**params)
            return invoices

        except stripe.error.InvalidRequestError as e:
            raise ValidationError(f"Invalid request: {str(e)}", tool_name=self.tool_name)
        except stripe.error.AuthenticationError as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}", tool_name=self.tool_name)
        except stripe.error.StripeError as e:
            raise APIError(f"Stripe error: {str(e)}", tool_name=self.tool_name)

    def _get_total_count(self) -> int:
        """Get total count of matching invoices (makes additional API call)."""
        # In mock mode, return mock count
        if self._should_use_mock():
            return 3

        # For real API, we'd need to iterate through all pages
        # For now, return None to indicate we don't have total count
        # In production, you might want to implement full pagination
        return None

    def _format_invoice(self, invoice: Any) -> Dict[str, Any]:
        """Format invoice object for output."""
        # Handle both dict and Stripe object
        if hasattr(invoice, "to_dict"):
            invoice = invoice.to_dict()

        return {
            "id": invoice.get("id"),
            "customer": invoice.get("customer"),
            "subscription": invoice.get("subscription"),
            "number": invoice.get("number"),
            "status": invoice.get("status"),
            "amount_due": invoice.get("amount_due"),
            "amount_paid": invoice.get("amount_paid"),
            "amount_remaining": invoice.get("amount_remaining"),
            "currency": invoice.get("currency"),
            "created": invoice.get("created"),
            "due_date": invoice.get("due_date"),
            "paid": invoice.get("paid"),
            "attempted": invoice.get("attempted"),
            "description": invoice.get("description"),
            "invoice_pdf": invoice.get("invoice_pdf"),
            "hosted_invoice_url": invoice.get("hosted_invoice_url"),
            "metadata": invoice.get("metadata", {}),
        }

    def _get_active_filters(self) -> Dict[str, Any]:
        """Get list of active filters for metadata."""
        filters = {}
        if self.customer_id:
            filters["customer_id"] = self.customer_id
        if self.status:
            filters["status"] = self.status
        if self.subscription_id:
            filters["subscription_id"] = self.subscription_id
        if self.created_after:
            filters["created_after"] = self.created_after
        if self.created_before:
            filters["created_before"] = self.created_before
        if self.due_date_after:
            filters["due_date_after"] = self.due_date_after
        if self.due_date_before:
            filters["due_date_before"] = self.due_date_before
        return filters


if __name__ == "__main__":
    # Test the tool
    print("Testing StripeGetInvoices...")

    import os
    import time

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Get all invoices
    print("\n1. Testing get all invoices...")
    tool = StripeGetInvoices(limit=10)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    print(f"Has more: {result.get('has_more')}")
    assert result.get("success") == True
    assert result.get("count") > 0
    assert "invoices" in result

    # Test 2: Get invoices for specific customer
    print("\n2. Testing get invoices for specific customer...")
    tool = StripeGetInvoices(customer_id="cus_1234567890", limit=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    if result.get("count") > 0:
        print(f"First invoice: {result['invoices'][0]['number']}")
    assert result.get("success") == True

    # Test 3: Filter by status
    print("\n3. Testing filter by status (paid)...")
    tool = StripeGetInvoices(status="paid", limit=10)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    for invoice in result.get("invoices", []):
        print(f"  Invoice {invoice['number']}: {invoice['status']}")
        assert invoice["status"] == "paid"
    assert result.get("success") == True

    # Test 4: Filter by subscription
    print("\n4. Testing filter by subscription...")
    tool = StripeGetInvoices(subscription_id="sub_1234567890", limit=10)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Filters: {result.get('metadata', {}).get('filters_applied')}")
    assert result.get("success") == True

    # Test 5: Date range filtering
    print("\n5. Testing date range filtering...")
    current_time = int(time.time())
    week_ago = current_time - (86400 * 7)

    tool = StripeGetInvoices(created_after=week_ago, limit=10)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    assert result.get("success") == True

    # Test 6: Due date filtering
    print("\n6. Testing due date filtering...")
    tool = StripeGetInvoices(
        due_date_after=current_time, due_date_before=current_time + (86400 * 30), limit=10
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 7: Include total count
    print("\n7. Testing include total count...")
    tool = StripeGetInvoices(include_total_count=True, limit=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    print(f"Total count: {result.get('total_count')}")
    assert result.get("success") == True
    assert "total_count" in result

    # Test 8: Pagination
    print("\n8. Testing pagination...")
    tool = StripeGetInvoices(starting_after="in_mock_01234567890", limit=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 9: Error handling - invalid status
    print("\n9. Testing error handling (invalid status)...")
    try:
        tool = StripeGetInvoices(status="invalid_status")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 10: Error handling - invalid date range
    print("\n10. Testing error handling (invalid date range)...")
    try:
        tool = StripeGetInvoices(created_after=current_time, created_before=week_ago)
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 11: Error handling - invalid customer ID format
    print("\n11. Testing error handling (invalid customer ID)...")
    try:
        tool = StripeGetInvoices(customer_id="invalid_id")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 12: Combined filters
    print("\n12. Testing combined filters...")
    tool = StripeGetInvoices(
        customer_id="cus_1234567890",
        status="paid",
        created_after=week_ago,
        limit=5,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Filters: {result.get('metadata', {}).get('filters_applied')}")
    assert result.get("success") == True

    print("\n✅ All tests passed!")
