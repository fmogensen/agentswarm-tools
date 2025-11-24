"""
Retrieve current stock price information for a company
"""

import os
from typing import Any, Dict

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


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
    tool_category: str = "data"

    # Parameters
    ticker: str = Field(
        ...,
        description="Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)",
        min_length=1,
        max_length=10,
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the stock_price tool.

        Returns:
            Dict with results
        """

        self._logger.info(f"Executing {self.tool_name} with ticker={self.ticker}")
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
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
            response = requests.get(api_url, timeout=30)
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
            self._logger.error(f"API request failed: {str(e)}", exc_info=True)
            raise APIError(f"API request failed: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the tool
    print("Testing StockPrice...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = StockPrice(ticker="AAPL")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Result: {result.get('result')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("symbol") == "AAPL"
    print("All tests passed!")
