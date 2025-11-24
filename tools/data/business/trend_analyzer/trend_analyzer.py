"""
Analyze trends in time-series data.
"""

import os
import statistics
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class TrendAnalyzer(BaseTool):
    """
    Analyze trends in time-series data and identify patterns.

    Args:
        data_points: List of data points (numbers) in chronological order
        time_labels: Optional list of time labels corresponding to data points
        analysis_type: Type of analysis (trend, volatility, seasonality, all)
        window_size: Window size for moving average calculations (default: 3)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Trend analysis including direction, strength, and statistics
        - metadata: Analysis parameters and additional info

    Example:
        >>> tool = TrendAnalyzer(
        ...     data_points=[10, 12, 15, 14, 18, 20, 22],
        ...     analysis_type="trend"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "trend_analyzer"
    tool_category: str = "data"

    # Parameters
    data_points: List[float] = Field(
        ..., description="List of numeric data points in chronological order", min_length=2
    )
    time_labels: Optional[List[str]] = Field(
        None, description="Optional time labels (e.g., dates) for each data point"
    )
    analysis_type: str = Field(
        "trend", description="Type of analysis: trend, volatility, seasonality, all"
    )
    window_size: int = Field(
        3, description="Window size for moving average calculations", ge=2, le=10
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute trend analysis."""

        self._logger.info(f"Executing {self.tool_name} with data_points={self.data_points}, time_labels={self.time_labels}, analysis_type={self.analysis_type}, window_size={self.window_size}")
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
                    "analysis_type": self.analysis_type,
                    "data_points_count": len(self.data_points),
                    "window_size": self.window_size,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Trend analysis failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        valid_types = ["trend", "volatility", "seasonality", "all"]

        if self.analysis_type not in valid_types:
            raise ValidationError(
                f"analysis_type must be one of {valid_types}",
                tool_name=self.tool_name,
                field="analysis_type",
            )

        if len(self.data_points) < 2:
            raise ValidationError(
                "data_points must contain at least 2 values",
                tool_name=self.tool_name,
                field="data_points",
            )

        if self.time_labels and len(self.time_labels) != len(self.data_points):
            raise ValidationError(
                "time_labels length must match data_points length",
                tool_name=self.tool_name,
                field="time_labels",
            )

        if self.window_size > len(self.data_points):
            raise ValidationError(
                "window_size cannot be larger than number of data points",
                tool_name=self.tool_name,
                field="window_size",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        return {
            "success": True,
            "result": {
                "trend_direction": "upward",
                "trend_strength": "strong",
                "percent_change": 25.5,
                "volatility": "moderate",
                "moving_average": [10.5, 12.0, 15.5, 18.0],
                "statistics": {
                    "mean": 15.0,
                    "median": 14.5,
                    "std_dev": 4.2,
                    "min": 10.0,
                    "max": 22.0,
                },
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "data_points_count": len(self.data_points),
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Perform trend analysis."""
        results = {}

        # Perform requested analysis
        if self.analysis_type in ["trend", "all"]:
            results["trend_analysis"] = self._analyze_trend()

        if self.analysis_type in ["volatility", "all"]:
            results["volatility_analysis"] = self._analyze_volatility()

        if self.analysis_type in ["seasonality", "all"]:
            results["seasonality_analysis"] = self._analyze_seasonality()

        # Always include basic statistics
        results["statistics"] = self._calculate_statistics()

        # Calculate moving average
        results["moving_average"] = self._calculate_moving_average()

        return results

    def _analyze_trend(self) -> Dict[str, Any]:
        """Analyze overall trend direction and strength."""
        # Calculate simple linear trend
        n = len(self.data_points)
        x_values = list(range(n))

        # Calculate slope (simple linear regression)
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(self.data_points)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, self.data_points))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        slope = numerator / denominator if denominator != 0 else 0

        # Determine trend direction
        if slope > 0.5:
            direction = "upward"
            strength = "strong" if abs(slope) > 2 else "moderate"
        elif slope < -0.5:
            direction = "downward"
            strength = "strong" if abs(slope) > 2 else "moderate"
        else:
            direction = "stable"
            strength = "weak"

        # Calculate percent change
        first_value = self.data_points[0]
        last_value = self.data_points[-1]
        percent_change = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0

        return {
            "direction": direction,
            "strength": strength,
            "slope": round(slope, 4),
            "percent_change": round(percent_change, 2),
            "first_value": first_value,
            "last_value": last_value,
        }

    def _analyze_volatility(self) -> Dict[str, Any]:
        """Analyze data volatility."""
        # Calculate standard deviation
        std_dev = statistics.stdev(self.data_points) if len(self.data_points) > 1 else 0
        mean = statistics.mean(self.data_points)

        # Coefficient of variation
        cv = (std_dev / mean * 100) if mean != 0 else 0

        # Determine volatility level
        if cv < 10:
            level = "low"
        elif cv < 25:
            level = "moderate"
        else:
            level = "high"

        # Calculate range
        data_range = max(self.data_points) - min(self.data_points)

        return {
            "level": level,
            "standard_deviation": round(std_dev, 4),
            "coefficient_of_variation": round(cv, 2),
            "range": round(data_range, 4),
            "min": min(self.data_points),
            "max": max(self.data_points),
        }

    def _analyze_seasonality(self) -> Dict[str, Any]:
        """Analyze potential seasonality patterns."""
        # Simple seasonality check using autocorrelation-like approach
        # For more sophisticated analysis, would need more data points

        if len(self.data_points) < 4:
            return {
                "detected": False,
                "message": "Insufficient data points for seasonality analysis (need at least 4)",
            }

        # Check for repeating patterns
        # Simple approach: check if values repeat in similar positions
        patterns_detected = []

        # Check for pairs of similar values
        for i in range(len(self.data_points) - 1):
            for j in range(i + 1, len(self.data_points)):
                diff = abs(self.data_points[i] - self.data_points[j])
                avg = (self.data_points[i] + self.data_points[j]) / 2
                if avg != 0 and diff / avg < 0.1:  # Within 10% similarity
                    patterns_detected.append(
                        {
                            "position_1": i,
                            "position_2": j,
                            "interval": j - i,
                            "value": round(avg, 2),
                        }
                    )

        detected = len(patterns_detected) > 0

        return {
            "detected": detected,
            "pattern_count": len(patterns_detected),
            "patterns": patterns_detected[:5] if detected else [],  # Limit to first 5
            "message": (
                "Potential seasonal patterns detected"
                if detected
                else "No clear seasonal patterns found"
            ),
        }

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate basic statistics."""
        return {
            "count": len(self.data_points),
            "mean": round(statistics.mean(self.data_points), 4),
            "median": round(statistics.median(self.data_points), 4),
            "std_dev": (
                round(statistics.stdev(self.data_points), 4) if len(self.data_points) > 1 else 0
            ),
            "min": min(self.data_points),
            "max": max(self.data_points),
            "sum": sum(self.data_points),
        }

    def _calculate_moving_average(self) -> List[float]:
        """Calculate moving average."""
        if len(self.data_points) < self.window_size:
            return []

        moving_avg = []
        for i in range(len(self.data_points) - self.window_size + 1):
            window = self.data_points[i : i + self.window_size]
            avg = statistics.mean(window)
            moving_avg.append(round(avg, 4))

        return moving_avg


if __name__ == "__main__":
    print("Testing TrendAnalyzer...")

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    tool = TrendAnalyzer(data_points=[10, 12, 15, 14, 18, 20, 22], analysis_type="all")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True
    print("TrendAnalyzer test passed!")
