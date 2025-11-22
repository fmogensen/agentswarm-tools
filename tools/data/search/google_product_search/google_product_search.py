"""
Search products using Google Shopping for price comparison
"""

from typing import Any, Dict, List
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GoogleProductSearch(BaseTool):
    """
    Search products using Google Shopping for price comparison

    Args:
        query: Product search query
        num: Number of results to return (default: 100, max: 100)
        page: Page number for pagination (default: 0)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: List of product results from multiple retailers
        - metadata: Additional information

    Example:
        >>> tool = GoogleProductSearch(query="laptop", num=10, page=0)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "google_product_search"
    tool_category: str = "data"

    # Parameters
    query: str = Field(..., description="Product search query", min_length=1)
    num: int = Field(
        100, description="Number of results to return", ge=1, le=100
    )
    page: int = Field(
        0, description="Page number for pagination", ge=0
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the google_product_search tool.

        Returns:
            Dict with results
        """
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
                "result": result,
                "metadata": {"tool_name": self.tool_name, "page": self.page},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.query.strip():
            raise ValidationError("Query cannot be empty", tool_name=self.tool_name)

        if self.num < 1 or self.num > 100:
            raise ValidationError("Number of results must be between 1 and 100", tool_name=self.tool_name)

        if self.page < 0:
            raise ValidationError("Page number must be non-negative", tool_name=self.tool_name)

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_products = [
            {
                "product_name": f"Mock Product {i}",
                "price": f"${99 + i}.99",
                "merchant": f"Mock Store {i % 3 + 1}",
                "product_url": f"https://example.com/product/{i}",
                "image": f"https://example.com/images/product{i}.jpg",
                "shipping": "Free shipping" if i % 2 == 0 else "$5.99",
                "rating": round(4.0 + (i % 10) / 10, 1),
                "review_count": (i + 1) * 100,
            }
            for i in range(1, min(self.num + 1, 11))
        ]

        return {
            "success": True,
            "result": {
                "products": mock_products,
                "total_results": self.num,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "page": self.page,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        try:
            # Get API credentials from environment
            api_key = os.getenv("GOOGLE_SHOPPING_API_KEY")
            search_engine_id = os.getenv("GOOGLE_SHOPPING_ENGINE_ID")

            if not api_key or not search_engine_id:
                raise APIError(
                    "Missing API credentials. Set GOOGLE_SHOPPING_API_KEY and GOOGLE_SHOPPING_ENGINE_ID",
                    tool_name=self.tool_name
                )

            # Calculate start index based on page
            start_index = self.page * self.num + 1

            # Call Google Custom Search API
            # Note: Shopping search type requires CSE configured for shopping
            # Try with shopping first, fallback to regular search if not supported
            search_params = {
                "q": self.query,
                "num": min(self.num, 10),  # Google API max is 10 per request
                "start": start_index,
                "key": api_key,
                "cx": search_engine_id,
            }

            # Try with shopping search type first
            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={**search_params, "searchType": "shopping"},
                timeout=30,
            )

            # If 400 error (shopping not supported), try regular search
            if response.status_code == 400:
                response = requests.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params=search_params,
                    timeout=30,
                )
            response.raise_for_status()
            data = response.json()

            # Extract product results
            products = []
            for item in data.get("items", []):
                product = {
                    "product_name": item.get("title", ""),
                    "price": item.get("pagemap", {}).get("offer", [{}])[0].get("price", "N/A"),
                    "merchant": item.get("displayLink", ""),
                    "product_url": item.get("link", ""),
                    "image": item.get("pagemap", {}).get("cse_image", [{}])[0].get("src", ""),
                    "snippet": item.get("snippet", ""),
                }

                # Extract additional product details if available
                product_details = item.get("pagemap", {}).get("product", [{}])
                if product_details:
                    product_detail = product_details[0]
                    product["rating"] = product_detail.get("ratingValue")
                    product["review_count"] = product_detail.get("reviewCount")
                    product["availability"] = product_detail.get("availability")

                # Extract offer details if available
                offer_details = item.get("pagemap", {}).get("offer", [{}])
                if offer_details:
                    offer = offer_details[0]
                    product["price"] = offer.get("price", product.get("price", "N/A"))
                    product["currency"] = offer.get("pricecurrency", "USD")
                    product["shipping"] = offer.get("shipping")

                products.append(product)

            return {
                "products": products,
                "total_results": data.get("searchInformation", {}).get("totalResults", 0),
                "search_time": data.get("searchInformation", {}).get("searchTime", 0),
                "query": self.query,
                "page": self.page,
            }

        except requests.RequestException as e:
            raise APIError(f"API request failed: {e}", tool_name=self.tool_name)
        except Exception as e:
            raise APIError(f"Failed to process results: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the google_product_search tool
    print("Testing GoogleProductSearch tool...")
    print("=" * 60)

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic search
    print("\nTest 1: Basic product search")
    print("-" * 60)
    tool = GoogleProductSearch(query="wireless headphones", num=5)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Total results: {len(result.get('result', {}).get('products', []))} items")
    if result.get('result', {}).get('products'):
        first_product = result['result']['products'][0]
        print(f"\nFirst product:")
        print(f"  Name: {first_product.get('product_name')}")
        print(f"  Price: {first_product.get('price')}")
        print(f"  Merchant: {first_product.get('merchant')}")
        print(f"  Rating: {first_product.get('rating')}")

    # Test 2: Search with pagination
    print("\n\nTest 2: Search with pagination")
    print("-" * 60)
    tool = GoogleProductSearch(query="laptop", num=10, page=1)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Page: {result.get('metadata', {}).get('page')}")
    print(f"Results: {len(result.get('result', {}).get('products', []))} items")

    # Test 3: Different number of results
    print("\n\nTest 3: Custom number of results")
    print("-" * 60)
    tool = GoogleProductSearch(query="gaming mouse", num=3)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Results: {len(result.get('result', {}).get('products', []))} items")

    # Test 4: Error handling - empty query
    print("\n\nTest 4: Error handling - empty query")
    print("-" * 60)
    try:
        tool = GoogleProductSearch(query="", num=5)
        result = tool.run()
        print(f"Success: {result.get('success')}")
        if not result.get('success'):
            print(f"Error: {result.get('error', {}).get('message')}")
    except Exception as e:
        print(f"Exception caught: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("All tests completed!")
