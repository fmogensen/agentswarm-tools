"""
Search official financial reports, earnings, statements for public companies
"""

import os
from typing import Any, Dict

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class FinancialReport(BaseTool):
    """
    Search official financial reports, earnings, statements for public companies

    Args:
        ticker: Stock ticker symbol (e.g., AAPL, GOOGL)
        report_type: Type of financial report (income_statement, balance_sheet, cash_flow)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = FinancialReport(ticker="AAPL", report_type="income_statement")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "financial_report"
    tool_category: str = "data"
    tool_description: str = (
        "Search official financial reports, earnings, statements for public companies"
    )

    # Parameters
    ticker: str = Field(
        ..., description="Stock ticker symbol (e.g., AAPL, GOOGL)", min_length=1, max_length=10
    )
    report_type: str = Field(
        "income_statement",
        description="Type of financial report: income_statement, balance_sheet, cash_flow, or earnings",
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the financial_report tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid parameters
            APIError: For external API failures
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
                "metadata": {"tool_name": self.tool_name, "tool_version": "1.0.0"},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters.

        Raises:
            ValidationError: If ticker is invalid
        """
        if not self.ticker or not self.ticker.strip():
            raise ValidationError(
                "Ticker cannot be empty",
                tool_name=self.tool_name,
                details={"ticker": self.ticker},
            )

        valid_report_types = ["income_statement", "balance_sheet", "cash_flow", "earnings"]
        if self.report_type not in valid_report_types:
            raise ValidationError(
                f"Report type must be one of: {', '.join(valid_report_types)}",
                tool_name=self.tool_name,
                details={"report_type": self.report_type},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_results = {
            "ticker": self.ticker,
            "company": f"Mock Company ({self.ticker})",
            "report_type": self.report_type,
            "report": f"Mock {self.report_type.replace('_', ' ').title()}",
            "year": 2023,
            "data": {"revenue": 1000000, "expenses": 600000, "net_income": 400000},
        }

        return {
            "success": True,
            "result": mock_results,
            "metadata": {"mock_mode": True, "tool_version": "1.0.0"},
        }

    def _process(self) -> Any:
        """Main processing logic.

        Returns:
            Processed results from the external API or data source

        Raises:
            APIError: If external API call fails
        """
        # In a real implementation, this would call a financial data API like Alpha Vantage,
        # Yahoo Finance, or SEC EDGAR
        try:
            results = {
                "ticker": self.ticker,
                "company": f"Example Corp ({self.ticker})",
                "report_type": self.report_type,
                "report": f"{self.report_type.replace('_', ' ').title()}",
                "year": 2023,
                "data": {"revenue": 1000000, "expenses": 600000, "net_income": 400000},
            }
            return results
        except Exception as e:
            raise APIError(f"Error fetching financial report: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the tool
    print("Testing FinancialReport...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = FinancialReport(ticker="AAPL", report_type="income_statement")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Result: {result.get('result')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("ticker") == "AAPL"
    assert result.get("result", {}).get("report_type") == "income_statement"
    print("All tests passed!")
