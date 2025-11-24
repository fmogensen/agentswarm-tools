"""
Aggregate data from multiple sources with various methods.
"""

import os
import statistics
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class DataAggregator(BaseTool):
    """
    Aggregate data from multiple sources using different statistical methods.

    Args:
        sources: List of data source identifiers or data values
        aggregation_method: Method to use (sum, avg, max, min, count, median)
        filters: Optional filters to apply to data

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Aggregated value and statistics
        - metadata: Source count, method used, and additional info

    Example:
        >>> tool = DataAggregator(
        ...     sources=["10", "20", "30"],
        ...     aggregation_method="sum"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "data_aggregator"
    tool_category: str = "data"

    # Parameters
    sources: List[str] = Field(
        ..., description="Data source identifiers or numeric values as strings", min_length=1
    )
    aggregation_method: str = Field(
        ..., description="Aggregation method: sum, avg, max, min, count, median"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Optional filters to apply (e.g., {'min_value': 10, 'max_value': 100})"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute data aggregation."""

        self._logger.info(f"Executing {self.tool_name} with sources={self.sources}, aggregation_method={self.aggregation_method}, filters={self.filters}")
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
                "metadata": {
                    "tool_name": self.tool_name,
                    "sources_count": len(self.sources),
                    "method": self.aggregation_method,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Aggregation failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        valid_methods = ["sum", "avg", "max", "min", "count", "median"]

        if self.aggregation_method not in valid_methods:
            raise ValidationError(
                f"aggregation_method must be one of {valid_methods}",
                tool_name=self.tool_name,
                field="aggregation_method",
            )

        if not self.sources or len(self.sources) == 0:
            raise ValidationError(
                "sources cannot be empty", tool_name=self.tool_name, field="sources"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        mock_value = {
            "sum": 150.0,
            "avg": 50.0,
            "max": 75.0,
            "min": 25.0,
            "count": 3,
            "median": 50.0,
        }.get(self.aggregation_method, 42.5)

        return {
            "success": True,
            "result": {
                "aggregated_value": mock_value,
                "sources_processed": len(self.sources),
                "method": self.aggregation_method,
                "data_points": len(self.sources),
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "sources_count": len(self.sources),
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Perform aggregation."""
        # Convert sources to numeric values
        numeric_values = []
        for source in self.sources:
            try:
                # Try to convert to float
                value = float(source)
                numeric_values.append(value)
            except (ValueError, TypeError):
                # If conversion fails, skip this source
                continue

        if not numeric_values:
            raise ValidationError(
                "No valid numeric values found in sources",
                tool_name=self.tool_name,
                field="sources",
            )

        # Apply filters if provided
        if self.filters:
            filtered_values = []
            for value in numeric_values:
                if "min_value" in self.filters and value < self.filters["min_value"]:
                    continue
                if "max_value" in self.filters and value > self.filters["max_value"]:
                    continue
                filtered_values.append(value)
            numeric_values = filtered_values

        if not numeric_values:
            raise ValidationError(
                "No values remain after applying filters", tool_name=self.tool_name, field="filters"
            )

        # Perform aggregation
        result_value = None
        if self.aggregation_method == "sum":
            result_value = sum(numeric_values)
        elif self.aggregation_method == "avg":
            result_value = statistics.mean(numeric_values)
        elif self.aggregation_method == "max":
            result_value = max(numeric_values)
        elif self.aggregation_method == "min":
            result_value = min(numeric_values)
        elif self.aggregation_method == "count":
            result_value = len(numeric_values)
        elif self.aggregation_method == "median":
            result_value = statistics.median(numeric_values)

        return {
            "aggregated_value": result_value,
            "sources_processed": len(self.sources),
            "valid_values": len(numeric_values),
            "method": self.aggregation_method,
            "data_points": len(numeric_values),
        }


if __name__ == "__main__":
    print("Testing DataAggregator...")

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    tool = DataAggregator(sources=["10", "20", "30"], aggregation_method="sum")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True
    print("DataAggregator test passed!")
