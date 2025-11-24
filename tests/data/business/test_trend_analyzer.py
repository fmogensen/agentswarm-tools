"""Comprehensive tests for trend_analyzer tool."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, ValidationError
from tools.data.business.trend_analyzer.trend_analyzer import TrendAnalyzer


class TestTrendAnalyzer:
    """Test suite for TrendAnalyzer."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_data_points(self) -> list:
        """Valid test data points."""
        return [10.0, 12.0, 15.0, 14.0, 18.0, 20.0, 22.0]

    @pytest.fixture
    def tool(self, valid_data_points: list) -> TrendAnalyzer:
        """Create TrendAnalyzer instance with valid parameters."""
        return TrendAnalyzer(data_points=valid_data_points, analysis_type="trend")

    # ========== HAPPY PATH ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, valid_data_points: list):
        """Test successful execution."""
        tool = TrendAnalyzer(data_points=valid_data_points, analysis_type="trend")
        result = tool.run()
        assert result["success"] is True
        assert "result" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_all_analysis_types(self, valid_data_points: list):
        """Test all valid analysis types."""
        analysis_types = ["trend", "volatility", "seasonality", "all"]
        for analysis_type in analysis_types:
            tool = TrendAnalyzer(data_points=valid_data_points, analysis_type=analysis_type)
            result = tool.run()
            assert result["success"] is True
            assert result["metadata"]["analysis_type"] == analysis_type

    # ========== DATA POINTS VALIDATION ==========

    def test_empty_data_points_rejected(self):
        """Test that empty data points list is rejected."""
        with pytest.raises(PydanticValidationError):
            TrendAnalyzer(data_points=[], analysis_type="trend")

    def test_single_data_point_rejected(self):
        """Test that single data point is rejected."""
        with pytest.raises(PydanticValidationError):
            TrendAnalyzer(data_points=[10.0], analysis_type="trend")

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_minimum_two_data_points(self):
        """Test minimum of two data points."""
        tool = TrendAnalyzer(data_points=[10.0, 20.0], analysis_type="trend")
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_many_data_points(self):
        """Test with many data points."""
        data_points = [float(i) for i in range(1, 101)]  # 100 data points
        tool = TrendAnalyzer(data_points=data_points, analysis_type="trend")
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["data_points_count"] == 100

    # ========== ANALYSIS TYPE VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_invalid_analysis_type_rejected(self, valid_data_points: list):
        """Test that invalid analysis type is rejected."""
        tool = TrendAnalyzer(data_points=valid_data_points, analysis_type="invalid")
        with pytest.raises(ValidationError, match="analysis_type must be one of"):
            tool.run()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_case_sensitive_analysis_type(self, valid_data_points: list):
        """Test that analysis type is case sensitive."""
        tool = TrendAnalyzer(data_points=valid_data_points, analysis_type="TREND")
        with pytest.raises(ValidationError):
            tool.run()

    # ========== TIME LABELS VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_time_labels_optional(self, valid_data_points: list):
        """Test that time labels are optional."""
        tool = TrendAnalyzer(data_points=valid_data_points, analysis_type="trend")
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_time_labels_with_data(self, valid_data_points: list):
        """Test time labels with matching length."""
        time_labels = ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06", "2024-07"]
        tool = TrendAnalyzer(
            data_points=valid_data_points, time_labels=time_labels, analysis_type="trend"
        )
        result = tool.run()
        assert result["success"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_time_labels_length_mismatch_rejected(self, valid_data_points: list):
        """Test that mismatched time labels length is rejected."""
        time_labels = ["2024-01", "2024-02"]  # Only 2 labels for 7 data points
        tool = TrendAnalyzer(
            data_points=valid_data_points, time_labels=time_labels, analysis_type="trend"
        )
        with pytest.raises(ValidationError, match="time_labels length must match"):
            tool.run()

    # ========== WINDOW SIZE VALIDATION ==========

    def test_window_size_min_boundary(self, valid_data_points: list):
        """Test minimum window size (2)."""
        tool = TrendAnalyzer(data_points=valid_data_points, analysis_type="trend", window_size=2)
        assert tool.window_size == 2

    def test_window_size_max_boundary(self, valid_data_points: list):
        """Test maximum window size (10)."""
        tool = TrendAnalyzer(data_points=valid_data_points, analysis_type="trend", window_size=10)
        assert tool.window_size == 10

    def test_window_size_below_min_rejected(self, valid_data_points: list):
        """Test that window size below 2 is rejected."""
        with pytest.raises(PydanticValidationError):
            TrendAnalyzer(data_points=valid_data_points, analysis_type="trend", window_size=1)

    def test_window_size_above_max_rejected(self, valid_data_points: list):
        """Test that window size above 10 is rejected."""
        with pytest.raises(PydanticValidationError):
            TrendAnalyzer(data_points=valid_data_points, analysis_type="trend", window_size=11)

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_window_size_larger_than_data_rejected(self):
        """Test that window size larger than data points is rejected."""
        tool = TrendAnalyzer(data_points=[10.0, 20.0], analysis_type="trend", window_size=5)
        with pytest.raises(ValidationError, match="window_size cannot be larger"):
            tool.run()

    # ========== TREND ANALYSIS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_upward_trend_detection(self):
        """Test detection of upward trend."""
        data_points = [10.0, 20.0, 30.0, 40.0, 50.0]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="trend")
        result = tool.run()
        assert result["success"] is True
        assert "trend_analysis" in result["result"]
        assert result["result"]["trend_analysis"]["direction"] == "upward"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_downward_trend_detection(self):
        """Test detection of downward trend."""
        data_points = [50.0, 40.0, 30.0, 20.0, 10.0]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="trend")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["trend_analysis"]["direction"] == "downward"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_stable_trend_detection(self):
        """Test detection of stable trend."""
        data_points = [10.0, 10.5, 10.2, 10.3, 10.1]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="trend")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["trend_analysis"]["direction"] == "stable"

    # ========== VOLATILITY ANALYSIS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_volatility_analysis(self):
        """Test volatility analysis."""
        data_points = [10.0, 50.0, 15.0, 45.0, 20.0]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="volatility")
        result = tool.run()
        assert result["success"] is True
        assert "volatility_analysis" in result["result"]
        assert "level" in result["result"]["volatility_analysis"]
        assert "standard_deviation" in result["result"]["volatility_analysis"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_low_volatility(self):
        """Test low volatility detection."""
        data_points = [10.0, 10.5, 10.2, 10.3, 10.1]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="volatility")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["volatility_analysis"]["level"] == "low"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_high_volatility(self):
        """Test high volatility detection."""
        data_points = [10.0, 100.0, 20.0, 90.0, 30.0]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="volatility")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["volatility_analysis"]["level"] == "high"

    # ========== SEASONALITY ANALYSIS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_seasonality_analysis(self):
        """Test seasonality analysis."""
        data_points = [10.0, 20.0, 10.0, 20.0, 10.0, 20.0]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="seasonality")
        result = tool.run()
        assert result["success"] is True
        assert "seasonality_analysis" in result["result"]
        assert "detected" in result["result"]["seasonality_analysis"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_seasonality_insufficient_data(self):
        """Test seasonality with insufficient data."""
        data_points = [10.0, 20.0, 30.0]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="seasonality")
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["seasonality_analysis"]["detected"] is False

    # ========== ALL ANALYSIS TYPE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_all_analysis_includes_all_types(self):
        """Test that 'all' analysis includes all analysis types."""
        data_points = [10.0, 15.0, 20.0, 25.0, 30.0, 35.0]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="all")
        result = tool.run()
        assert result["success"] is True
        assert "trend_analysis" in result["result"]
        assert "volatility_analysis" in result["result"]
        assert "seasonality_analysis" in result["result"]
        assert "statistics" in result["result"]
        assert "moving_average" in result["result"]

    # ========== STATISTICS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_statistics_calculation(self):
        """Test statistics calculation."""
        data_points = [10.0, 20.0, 30.0, 40.0, 50.0]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="trend")
        result = tool.run()
        assert result["success"] is True
        stats = result["result"]["statistics"]
        assert stats["count"] == 5
        assert stats["mean"] == 30.0
        assert stats["median"] == 30.0
        assert stats["min"] == 10.0
        assert stats["max"] == 50.0

    # ========== MOVING AVERAGE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_moving_average_calculation(self):
        """Test moving average calculation."""
        data_points = [10.0, 20.0, 30.0, 40.0, 50.0]
        tool = TrendAnalyzer(data_points=data_points, analysis_type="trend", window_size=3)
        result = tool.run()
        assert result["success"] is True
        assert "moving_average" in result["result"]
        # Should have 3 values: avg of [10,20,30], [20,30,40], [30,40,50]
        assert len(result["result"]["moving_average"]) == 3

    # ========== ERROR HANDLING ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_error_handling(self, valid_data_points: list):
        """Test general error handling."""
        tool = TrendAnalyzer(data_points=valid_data_points, analysis_type="trend")
        with patch.object(tool, "_process", side_effect=Exception("Processing error")):
            with pytest.raises(APIError, match="Trend analysis failed"):
                tool.run()

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_enabled(self, valid_data_points: list):
        """Test that mock mode returns mock data."""
        tool = TrendAnalyzer(data_points=valid_data_points, analysis_type="trend")
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    # ========== RESULT FORMAT VALIDATION ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_result_format(self, valid_data_points: list):
        """Test that results have correct format."""
        tool = TrendAnalyzer(data_points=valid_data_points, analysis_type="all")
        result = tool.run()

        assert "success" in result
        assert "result" in result
        assert "metadata" in result

        # Check metadata
        metadata = result["metadata"]
        assert "tool_name" in metadata
        assert "analysis_type" in metadata
        assert "data_points_count" in metadata
        assert "window_size" in metadata

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "data_points,analysis_type,window_size,expected_valid",
        [
            ([10.0, 20.0, 30.0], "trend", 3, True),
            ([10.0, 20.0, 30.0], "volatility", 3, True),
            ([10.0, 20.0, 30.0], "seasonality", 3, True),
            ([10.0, 20.0, 30.0], "all", 3, True),
            ([10.0, 20.0], "trend", 2, True),  # Minimum data points
            ([10.0], "trend", 2, False),  # Too few data points
            ([], "trend", 3, False),  # Empty data points
            ([10.0, 20.0, 30.0], "invalid", 3, False),  # Invalid analysis type
            ([10.0, 20.0], "trend", 5, False),  # Window size > data points
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_parameter_combinations(
        self, data_points: list, analysis_type: str, window_size: int, expected_valid: bool
    ):
        """Test various parameter combinations."""
        if expected_valid:
            tool = TrendAnalyzer(
                data_points=data_points, analysis_type=analysis_type, window_size=window_size
            )
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = TrendAnalyzer(
                    data_points=data_points, analysis_type=analysis_type, window_size=window_size
                )
                tool.run()

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_full_workflow(self):
        """Test complete workflow for trend analysis."""
        # Create tool with time series data
        data_points = [100.0, 110.0, 105.0, 115.0, 120.0, 118.0, 125.0]
        time_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
        tool = TrendAnalyzer(
            data_points=data_points, time_labels=time_labels, analysis_type="all", window_size=3
        )

        # Verify parameters
        assert tool.data_points == data_points
        assert tool.time_labels == time_labels
        assert tool.analysis_type == "all"
        assert tool.window_size == 3
        assert tool.tool_name == "trend_analyzer"
        assert tool.tool_category == "data"

        # Execute
        result = tool.run()

        # Verify results
        assert result["success"] is True
        assert "trend_analysis" in result["result"]
        assert "volatility_analysis" in result["result"]
        assert "seasonality_analysis" in result["result"]
        assert "statistics" in result["result"]
        assert "moving_average" in result["result"]

    # ========== TOOL METADATA TESTS ==========

    def test_tool_category(self, tool: TrendAnalyzer):
        """Test tool category is correct."""
        assert tool.tool_category == "data"

    def test_tool_name(self, tool: TrendAnalyzer):
        """Test tool name is correct."""
        assert tool.tool_name == "trend_analyzer"
