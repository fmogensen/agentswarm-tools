"""
Search and recommend products from Amazon with detailed information
"""

import os
from typing import Any, Dict, List, Optional

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class ProductSearch(BaseTool):
    """
    Search and recommend products from Amazon with detailed information

    Args:
        type: 'product_search' or 'product_detail'
        query: Search query for product_search (optional)
        ASIN: Amazon product ID for product_detail (optional)
        location_domain: Domain ('com' for US, optional)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (product listings or product detail)
        - metadata: Additional information

    Example:
        >>> tool = ProductSearch(type="product_search", query="wireless headphones")
        >>> result = tool.run()

        >>> tool = ProductSearch(type="product_detail", ASIN="B08N5WRWNW")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "product_search"
    tool_category: str = "data"

    # Caching configuration - product search results cached for 1 hour
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_key_params: list = ["type", "query", "ASIN", "location_domain"]

    # Parameters
    type: str = Field(..., description="Type of search: 'product_search' or 'product_detail'")
    query: Optional[str] = Field(None, description="Search query for product_search")
    ASIN: Optional[str] = Field(None, description="Amazon product ID for product_detail")
    location_domain: Optional[str] = Field("com", description="Amazon domain ('com' for US)")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the product_search tool.

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

            metadata = {
                "tool_name": self.tool_name,
                "type": self.type,
            }
            if self.query:
                metadata["query"] = self.query
            if self.ASIN:
                metadata["ASIN"] = self.ASIN
            if self.location_domain:
                metadata["location_domain"] = self.location_domain

            return {
                "success": True,
                "result": result,
                "metadata": metadata,
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if self.type not in ["product_search", "product_detail"]:
            raise ValidationError(
                "Type must be 'product_search' or 'product_detail'",
                tool_name=self.tool_name,
                field="type",
            )

        if self.type == "product_search" and not self.query:
            raise ValidationError(
                "Query is required for product_search", tool_name=self.tool_name, field="query"
            )

        if self.type == "product_detail" and not self.ASIN:
            raise ValidationError(
                "ASIN is required for product_detail", tool_name=self.tool_name, field="ASIN"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        if self.type == "product_search":
            mock_results = {
                "search_query": self.query,
                "products": [
                    {
                        "ASIN": f"B08MOCK{i:03d}",
                        "title": f"Mock Product {i}: {self.query}",
                        "price": f"${29.99 + i * 10}",
                        "rating": 4.5,
                        "review_count": 1000 + i * 100,
                        "images": [f"https://example.com/image{i}.jpg"],
                        "availability": "In Stock",
                        "prime": True,
                    }
                    for i in range(1, 6)
                ],
            }
        else:  # product_detail
            mock_results = {
                "ASIN": self.ASIN,
                "title": f"Mock Product Detail for {self.ASIN}",
                "price": "$49.99",
                "rating": 4.5,
                "review_count": 2500,
                "images": [f"https://example.com/image1.jpg", f"https://example.com/image2.jpg"],
                "availability": "In Stock",
                "prime": True,
                "description": "This is a detailed mock product description with features and specifications.",
                "specifications": {"Brand": "Mock Brand", "Color": "Black", "Weight": "1.5 pounds"},
                "customer_reviews": [
                    {
                        "rating": 5,
                        "title": "Great product!",
                        "text": "This is a mock review. The product works great.",
                        "verified": True,
                    }
                ],
                "related_products": [
                    {"ASIN": "B08RELATED1", "title": "Related Product 1", "price": "$39.99"}
                ],
            }

        metadata = {
            "mock_mode": True,
            "tool_name": self.tool_name,
            "type": self.type,
        }
        if self.query:
            metadata["query"] = self.query
        if self.ASIN:
            metadata["ASIN"] = self.ASIN
        if self.location_domain:
            metadata["location_domain"] = self.location_domain

        return {
            "success": True,
            "result": mock_results,
            "metadata": metadata,
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        try:
            # Get API key from environment
            api_key = os.getenv("AMAZON_API_KEY")
            if not api_key:
                raise APIError("AMAZON_API_KEY not found in environment", tool_name=self.tool_name)

            # Build API request based on type
            if self.type == "product_search":
                return self._search_products(api_key)
            else:  # product_detail
                return self._get_product_detail(api_key)

        except requests.RequestException as e:
            raise APIError(f"API request failed: {e}", tool_name=self.tool_name)

    def _search_products(self, api_key: str) -> Dict[str, Any]:
        """Search for products on Amazon."""
        # Replace with actual Amazon Product API logic
        # This is a placeholder for the actual API implementation
        response = requests.get(
            "https://api.amazon-product-api.example/search",
            params={
                "query": self.query,
                "domain": self.location_domain,
                "api_key": api_key,
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        # Extract and format product listings
        products = []
        for item in data.get("results", []):
            products.append(
                {
                    "ASIN": item.get("asin"),
                    "title": item.get("title"),
                    "price": item.get("price"),
                    "rating": item.get("rating"),
                    "review_count": item.get("reviews_count"),
                    "images": item.get("images", []),
                    "availability": item.get("availability"),
                    "prime": item.get("is_prime", False),
                }
            )

        return {"search_query": self.query, "products": products, "total_results": len(products)}

    def _get_product_detail(self, api_key: str) -> Dict[str, Any]:
        """Get detailed information for a specific product."""
        # Replace with actual Amazon Product API logic
        # This is a placeholder for the actual API implementation
        response = requests.get(
            "https://api.amazon-product-api.example/product",
            params={
                "asin": self.ASIN,
                "domain": self.location_domain,
                "api_key": api_key,
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()

        # Extract and format product detail
        return {
            "ASIN": data.get("asin"),
            "title": data.get("title"),
            "price": data.get("price"),
            "rating": data.get("rating"),
            "review_count": data.get("reviews_count"),
            "images": data.get("images", []),
            "availability": data.get("availability"),
            "prime": data.get("is_prime", False),
            "description": data.get("description"),
            "specifications": data.get("specifications", {}),
            "customer_reviews": data.get("customer_reviews", []),
            "qa": data.get("questions_and_answers", []),
            "related_products": data.get("related_products", []),
            "pricing_history": data.get("pricing_history", []),
        }


if __name__ == "__main__":
    # Test the product_search tool
    print("Testing ProductSearch tool...")
    print()

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    # Test product search
    print("=" * 60)
    print("Test 1: Product Search")
    print("=" * 60)
    tool = ProductSearch(type="product_search", query="wireless headphones")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Search query: {result.get('result', {}).get('search_query')}")
    print(f"Products found: {len(result.get('result', {}).get('products', []))}")
    if result.get("result", {}).get("products"):
        first_product = result["result"]["products"][0]
        print(f"First product ASIN: {first_product.get('ASIN')}")
        print(f"First product title: {first_product.get('title')}")
        print(f"First product price: {first_product.get('price')}")
        print(f"First product rating: {first_product.get('rating')}")
    print()

    # Test product detail
    print("=" * 60)
    print("Test 2: Product Detail")
    print("=" * 60)
    tool = ProductSearch(type="product_detail", ASIN="B08N5WRWNW")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"ASIN: {result.get('result', {}).get('ASIN')}")
    print(f"Title: {result.get('result', {}).get('title')}")
    print(f"Price: {result.get('result', {}).get('price')}")
    print(f"Rating: {result.get('result', {}).get('rating')}")
    print(f"Reviews: {result.get('result', {}).get('review_count')}")
    print(f"Description: {result.get('result', {}).get('description')[:100]}...")
    print(f"Specifications: {list(result.get('result', {}).get('specifications', {}).keys())}")
    print()

    # Test validation error
    print("=" * 60)
    print("Test 3: Validation Error (missing query)")
    print("=" * 60)
    try:
        tool = ProductSearch(type="product_search")
        result = tool.run()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}")
    print()

    # Test validation error
    print("=" * 60)
    print("Test 4: Validation Error (invalid type)")
    print("=" * 60)
    try:
        tool = ProductSearch(type="invalid_type", query="test")
        result = tool.run()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}")
    print()

    print("All tests completed!")
