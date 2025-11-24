"""
Stripe List Customers Tool

Lists and searches Stripe customers with support for filtering by email,
metadata, creation date, and pagination.
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


class StripeListCustomers(BaseTool):
    """
    List and search Stripe customers with filtering and pagination.

    This tool retrieves customer records from Stripe with support for
    email search, metadata filtering, date ranges, and pagination.

    Args:
        email: Filter by customer email address (optional)
        limit: Maximum number of customers to return (default: 10, max: 100)
        starting_after: Customer ID to start after (for pagination)
        ending_before: Customer ID to end before (for pagination)
        created_after: Unix timestamp - customers created after this date
        created_before: Unix timestamp - customers created before this date
        metadata_filters: Dict of metadata key-value pairs to filter by
        include_deleted: Include deleted customers in results (default: False)

    Returns:
        Dict containing:
            - success (bool): Whether the operation was successful
            - customers (list): List of customer objects
            - has_more (bool): Whether more customers are available
            - count (int): Number of customers returned
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = StripeListCustomers(
        ...     email="customer@example.com",
        ...     limit=10
        ... )
        >>> result = tool.run()
        >>> print(f"Found {result['count']} customers")
        >>> for customer in result['customers']:
        ...     print(customer['email'])
    """

    # Tool metadata
    tool_name: str = "stripe_list_customers"
    tool_category: str = "integrations"

    # Optional parameters
    email: Optional[str] = Field(
        None,
        description="Filter by customer email address",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
    )
    limit: int = Field(10, description="Maximum number of customers to return", ge=1, le=100)
    starting_after: Optional[str] = Field(None, description="Customer ID to start pagination after")
    ending_before: Optional[str] = Field(None, description="Customer ID to end pagination before")
    created_after: Optional[int] = Field(
        None, description="Unix timestamp - customers created after this date", ge=0
    )
    created_before: Optional[int] = Field(
        None, description="Unix timestamp - customers created before this date", ge=0
    )
    metadata_filters: Optional[Dict[str, str]] = Field(
        None, description="Metadata key-value pairs to filter by"
    )
    include_deleted: bool = Field(False, description="Include deleted customers in results")

    def _execute(self) -> Dict[str, Any]:
        """Execute the customer listing."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()
            customers = result.get("data", [])

            return {
                "success": True,
                "customers": [self._format_customer(c) for c in customers],
                "has_more": result.get("has_more", False),
                "count": len(customers),
                "metadata": {
                    "tool_name": self.tool_name,
                    "filters_applied": self._get_active_filters(),
                },
            }
        except (AuthenticationError, ValidationError):
            # Let these pass through unchanged
            raise
        except Exception as e:
            # Only wrap unexpected errors
            raise APIError(f"Failed to list customers: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate pagination parameters
        if self.starting_after and self.ending_before:
            raise ValidationError(
                "Cannot specify both starting_after and ending_before",
                tool_name=self.tool_name,
            )

        # Validate date range
        if self.created_after and self.created_before and self.created_after >= self.created_before:
            raise ValidationError(
                "created_after must be before created_before",
                tool_name=self.tool_name,
            )

        # Validate customer ID formats for pagination
        if self.starting_after and not self.starting_after.startswith("cus_"):
            raise ValidationError(
                "starting_after must be a valid customer ID (cus_xxx)",
                tool_name=self.tool_name,
            )

        if self.ending_before and not self.ending_before.startswith("cus_"):
            raise ValidationError(
                "ending_before must be a valid customer ID (cus_xxx)",
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

        # Generate mock customers
        mock_customers = []
        num_customers = min(self.limit, 3)  # Generate up to 3 mock customers

        for i in range(num_customers):
            customer = {
                "id": f"cus_mock_{i}1234567890",
                "email": self.email if self.email and i == 0 else f"customer{i}@example.com",
                "name": f"Mock Customer {i}",
                "description": f"Mock customer for testing",
                "created": current_time - (86400 * i),
                "balance": 0,
                "currency": "usd",
                "delinquent": False,
                "metadata": {"tier": "premium" if i == 0 else "standard", "test": "true"},
                "default_source": None,
                "invoice_settings": {"default_payment_method": None},
            }
            mock_customers.append(customer)

        return {
            "success": True,
            "customers": [self._format_customer(c) for c in mock_customers],
            "has_more": False,
            "count": len(mock_customers),
            "metadata": {
                "tool_name": self.tool_name,
                "filters_applied": self._get_active_filters(),
                "mock_mode": True,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Process the customer listing with Stripe API."""
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

        if self.email:
            params["email"] = self.email

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

        # List customers
        try:
            customers = stripe.Customer.list(**params)

            # Filter by metadata if specified
            if self.metadata_filters:
                filtered_customers = []
                for customer in customers.data:
                    if self._matches_metadata(customer.metadata, self.metadata_filters):
                        filtered_customers.append(customer)
                customers.data = filtered_customers

            # Filter deleted customers if not included
            if not self.include_deleted:
                customers.data = [c for c in customers.data if not c.get("deleted", False)]

            return customers

        except Exception as e:
            # Handle Stripe errors by checking the error type name
            error_type = type(e).__name__

            if error_type == "InvalidRequestError":
                raise ValidationError(f"Invalid request: {str(e)}", tool_name=self.tool_name)
            elif error_type == "AuthenticationError":
                raise AuthenticationError(
                    f"Authentication failed: {str(e)}", tool_name=self.tool_name
                )
            elif (
                "StripeError" in error_type or hasattr(e, "__module__") and "stripe" in e.__module__
            ):
                raise APIError(f"Stripe error: {str(e)}", tool_name=self.tool_name)
            else:
                # Unknown error
                raise

    def _format_customer(self, customer: Any) -> Dict[str, Any]:
        """Format customer object for output."""
        # Handle both dict and Stripe object
        if hasattr(customer, "to_dict"):
            customer = customer.to_dict()

        return {
            "id": customer.get("id"),
            "email": customer.get("email"),
            "name": customer.get("name"),
            "description": customer.get("description"),
            "created": customer.get("created"),
            "balance": customer.get("balance"),
            "currency": customer.get("currency"),
            "delinquent": customer.get("delinquent"),
            "metadata": customer.get("metadata", {}),
            "default_source": customer.get("default_source"),
        }

    def _matches_metadata(self, customer_metadata: Dict[str, str], filters: Dict[str, str]) -> bool:
        """Check if customer metadata matches all filter criteria."""
        for key, value in filters.items():
            if customer_metadata.get(key) != value:
                return False
        return True

    def _get_active_filters(self) -> Dict[str, Any]:
        """Get list of active filters for metadata."""
        filters = {}
        if self.email:
            filters["email"] = self.email
        if self.created_after:
            filters["created_after"] = self.created_after
        if self.created_before:
            filters["created_before"] = self.created_before
        if self.metadata_filters:
            filters["metadata"] = self.metadata_filters
        if self.include_deleted:
            filters["include_deleted"] = True
        return filters


if __name__ == "__main__":
    # Test the tool
    print("Testing StripeListCustomers...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: List all customers
    print("\n1. Testing list all customers...")
    tool = StripeListCustomers(limit=10)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    print(f"Has more: {result.get('has_more')}")
    assert result.get("success") == True
    assert result.get("count") > 0
    assert "customers" in result

    # Test 2: Filter by email
    print("\n2. Testing filter by email...")
    tool = StripeListCustomers(email="customer0@example.com", limit=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    if result.get("count") > 0:
        print(f"First customer email: {result['customers'][0]['email']}")
    assert result.get("success") == True

    # Test 3: Date range filtering
    print("\n3. Testing date range filtering...")
    import time

    current_time = int(time.time())
    week_ago = current_time - (86400 * 7)

    tool = StripeListCustomers(created_after=week_ago, limit=10)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    assert result.get("success") == True

    # Test 4: Metadata filtering
    print("\n4. Testing metadata filtering...")
    tool = StripeListCustomers(metadata_filters={"tier": "premium"}, limit=10)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Filters applied: {result.get('metadata', {}).get('filters_applied')}")
    assert result.get("success") == True

    # Test 5: Pagination
    print("\n5. Testing pagination with starting_after...")
    tool = StripeListCustomers(starting_after="cus_mock_01234567890", limit=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 6: Error handling - invalid date range
    print("\n6. Testing error handling (invalid date range)...")
    try:
        tool = StripeListCustomers(
            created_after=current_time, created_before=week_ago  # Invalid: after > before
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 7: Error handling - conflicting pagination
    print("\n7. Testing error handling (conflicting pagination)...")
    try:
        tool = StripeListCustomers(starting_after="cus_123", ending_before="cus_456")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except ValidationError as e:
        print(f"Correctly caught error: {e.message}")

    # Test 8: Limit boundary
    print("\n8. Testing limit boundary...")
    tool = StripeListCustomers(limit=1)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    assert result.get("success") == True
    assert result.get("count") <= 1

    print("\n✅ All tests passed!")
