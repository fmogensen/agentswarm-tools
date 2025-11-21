"""
Retrieve current stock price information for a company
"""

from typing import Any, Dict
from pydantic import Field
import os
import requests

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class StockPrice(BaseTool):
    """
    Retrieve current stock price information for a company

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (symbol, price, currency, etc.)
        - metadata: Additional information

    Example:
        >>> tool = StockPrice(ticker="AAPL")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "stock_price"
    tool_category: str = "search"

    # Parameters
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)", min_length=1, max_length=10)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the stock_price tool.

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
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.ticker or not self.ticker.strip():
            raise ValidationError(
                "Ticker cannot be empty",
                tool_name=self.tool_name,
                details={"ticker": self.ticker},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "symbol": self.ticker.upper(),
                "price": 150.00,
                "change": +2.50,
                "change_percent": +1.69,
                "currency": "USD",
                "mock": True,
            },
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        try:
            # This is a placeholder for an actual API call
            # In production, use APIs like Alpha Vantage, Yahoo Finance, IEX Cloud, etc.
            api_url = f"https://api.example.com/stock/{self.ticker.upper()}/price"
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            return {
                "symbol": self.ticker.upper(),
                "price": data.get("price"),
                "change": data.get("change"),
                "change_percent": data.get("change_percent"),
                "currency": data.get("currency", "USD"),
            }
        except requests.RequestException as e:
            raise APIError(f"API request failed: {e}", tool_name=self.tool_name)
