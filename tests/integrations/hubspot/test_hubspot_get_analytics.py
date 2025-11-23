"""
Tests for HubSpot Get Analytics Tool

Comprehensive test suite covering analytics retrieval for contacts, deals,
emails, conversions, pipeline, revenue, and custom reports.
"""

import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from shared.errors import APIError, ValidationError
from tools.integrations.hubspot.hubspot_get_analytics import HubSpotGetAnalytics


class TestHubSpotGetAnalytics:
    """Test suite for HubSpotGetAnalytics tool."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"
        yield
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_contacts_analytics(self):
        """Test retrieving contact analytics."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="last_30_days",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["report_type"] == "contacts"
        assert "metrics" in result
        assert "total_contacts" in result["metrics"]
        assert "new_contacts" in result["metrics"]
        assert "by_lifecycle_stage" in result["metrics"]

    def test_deals_analytics(self):
        """Test retrieving deal analytics."""
        tool = HubSpotGetAnalytics(
            report_type="deals",
            time_period="this_month",
        )
        result = tool.run()

        assert result["success"] == True
        assert "total_deals" in result["metrics"]
        assert "won_deals" in result["metrics"]
        assert "win_rate" in result["metrics"]
        assert result["metrics"]["win_rate"] > 0

    def test_pipeline_analytics(self):
        """Test retrieving pipeline analytics."""
        tool = HubSpotGetAnalytics(
            report_type="pipeline",
            time_period="this_quarter",
            pipeline_id="default",
        )
        result = tool.run()

        assert result["success"] == True
        assert "total_pipeline_value" in result["metrics"]
        assert "deals_by_stage" in result["metrics"]
        assert "forecast" in result["metrics"]
        assert "commit" in result["metrics"]["forecast"]

    def test_email_analytics(self):
        """Test retrieving email campaign analytics."""
        tool = HubSpotGetAnalytics(
            report_type="emails",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        result = tool.run()

        assert result["success"] == True
        assert "total_sent" in result["metrics"]
        assert "open_rate" in result["metrics"]
        assert "click_rate" in result["metrics"]
        assert 0 <= result["metrics"]["open_rate"] <= 1

    def test_conversions_analytics(self):
        """Test retrieving conversion analytics."""
        tool = HubSpotGetAnalytics(
            report_type="conversions",
            time_period="last_7_days",
        )
        result = tool.run()

        assert result["success"] == True
        assert "total_conversions" in result["metrics"]
        assert "conversion_rate" in result["metrics"]
        assert "by_source" in result["metrics"]

    def test_revenue_analytics(self):
        """Test retrieving revenue analytics."""
        tool = HubSpotGetAnalytics(
            report_type="revenue",
            time_period="this_year",
        )
        result = tool.run()

        assert result["success"] == True
        assert "total_revenue" in result["metrics"]
        assert "mrr" in result["metrics"]
        assert "arr" in result["metrics"]
        assert result["metrics"]["total_revenue"] > 0

    def test_engagement_analytics(self):
        """Test retrieving engagement analytics."""
        tool = HubSpotGetAnalytics(
            report_type="engagement",
            time_period="last_30_days",
        )
        result = tool.run()

        assert result["success"] == True
        assert "email_engagement" in result["metrics"]
        assert "website_sessions" in result["metrics"]

    def test_analytics_with_metrics_filter(self):
        """Test requesting specific metrics."""
        tool = HubSpotGetAnalytics(
            report_type="pipeline",
            time_period="this_month",
            metrics=["total_pipeline_value", "weighted_pipeline_value"],
        )
        result = tool.run()

        assert result["success"] == True
        assert "metrics" in result

    def test_analytics_grouped_by_day(self):
        """Test analytics grouped by day."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="last_7_days",
            group_by="day",
            include_details=True,
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["data"]) > 0
        # Check that data points have date field
        if result["data"]:
            assert "date" in result["data"][0]

    def test_analytics_grouped_by_stage(self):
        """Test analytics grouped by stage."""
        tool = HubSpotGetAnalytics(
            report_type="deals",
            time_period="this_month",
            group_by="stage",
            include_details=True,
        )
        result = tool.run()

        assert result["success"] == True
        if result["data"]:
            assert "stage" in result["data"][0]

    def test_time_range_calculation_today(self):
        """Test time range for 'today' period."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="today",
        )
        result = tool.run()

        assert result["success"] == True
        time_range = result["time_range"]
        today = datetime.now().strftime("%Y-%m-%d")
        assert time_range["start_date"] == today
        assert time_range["end_date"] == today

    def test_time_range_calculation_last_7_days(self):
        """Test time range for 'last_7_days' period."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="last_7_days",
        )
        result = tool.run()

        assert result["success"] == True
        time_range = result["time_range"]
        start = datetime.strptime(time_range["start_date"], "%Y-%m-%d")
        end = datetime.strptime(time_range["end_date"], "%Y-%m-%d")
        assert (end - start).days == 7

    def test_custom_date_range(self):
        """Test custom date range."""
        tool = HubSpotGetAnalytics(
            report_type="deals",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["time_range"]["start_date"] == "2024-01-01"
        assert result["time_range"]["end_date"] == "2024-01-31"

    def test_analytics_with_owner_filter(self):
        """Test filtering by owner."""
        tool = HubSpotGetAnalytics(
            report_type="deals",
            time_period="this_month",
            owner_id="owner_123",
        )
        result = tool.run()

        assert result["success"] == True

    def test_analytics_with_pipeline_filter(self):
        """Test filtering by pipeline."""
        tool = HubSpotGetAnalytics(
            report_type="pipeline",
            time_period="this_quarter",
            pipeline_id="sales_pipeline_1",
        )
        result = tool.run()

        assert result["success"] == True

    def test_analytics_with_limit(self):
        """Test limiting result count."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="last_30_days",
            include_details=True,
            limit=5,
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["data"]) <= 5

    def test_analytics_summary(self):
        """Test analytics summary statistics."""
        tool = HubSpotGetAnalytics(
            report_type="deals",
            time_period="this_month",
        )
        result = tool.run()

        assert result["success"] == True
        assert "summary" in result
        assert "total_records" in result["summary"]

    def test_invalid_report_type(self):
        """Test validation of report type."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotGetAnalytics(
                report_type="invalid_type",
                time_period="last_30_days",
            )
            tool.run()
        assert "Invalid report_type" in str(exc_info.value)

    def test_invalid_time_period(self):
        """Test validation of time period."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotGetAnalytics(
                report_type="contacts",
                time_period="invalid_period",
            )
            tool.run()
        assert "Invalid time_period" in str(exc_info.value)

    def test_invalid_group_by(self):
        """Test validation of group_by parameter."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotGetAnalytics(
                report_type="contacts",
                time_period="last_30_days",
                group_by="invalid_grouping",
            )
            tool.run()
        assert "Invalid group_by" in str(exc_info.value)

    def test_invalid_date_format(self):
        """Test validation of date format."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotGetAnalytics(
                report_type="contacts",
                start_date="invalid-date",
                end_date="2024-01-31",
            )
            tool.run()
        assert "YYYY-MM-DD format" in str(exc_info.value)

    def test_start_date_after_end_date(self):
        """Test validation that start_date must be before end_date."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotGetAnalytics(
                report_type="contacts",
                start_date="2024-12-31",
                end_date="2024-01-01",
            )
            tool.run()
        assert "cannot be after end_date" in str(exc_info.value)

    def test_custom_report_requires_id(self):
        """Test that custom report requires custom_report_id."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotGetAnalytics(
                report_type="custom",
                time_period="last_30_days",
            )
            tool.run()
        assert "custom_report_id is required" in str(exc_info.value)

    def test_custom_report_with_id(self):
        """Test custom report with ID."""
        tool = HubSpotGetAnalytics(
            report_type="custom",
            custom_report_id="report_12345",
            time_period="last_30_days",
        )
        result = tool.run()

        assert result["success"] == True

    def test_analytics_with_properties(self):
        """Test requesting specific properties."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="last_30_days",
            properties=["email", "firstname", "lastname", "company"],
        )
        result = tool.run()

        assert result["success"] == True

    def test_analytics_include_details_false(self):
        """Test that include_details=False doesn't return detailed data."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="last_30_days",
            include_details=False,
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["data"]) == 0

    def test_time_period_this_month(self):
        """Test time period for this_month."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="this_month",
        )
        result = tool.run()

        assert result["success"] == True
        time_range = result["time_range"]
        today = datetime.now()
        assert time_range["start_date"] == today.replace(day=1).strftime("%Y-%m-%d")

    def test_tool_metadata(self):
        """Test tool metadata."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="last_30_days",
        )

        assert tool.tool_name == "hubspot_get_analytics"
        assert tool.tool_category == "integrations"

    def test_metadata_in_result(self):
        """Test that result includes metadata."""
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="last_30_days",
            include_details=True,
        )
        result = tool.run()

        assert "metadata" in result
        assert "tool_name" in result["metadata"]
        assert "data_points" in result["metadata"]

    @patch("tools.integrations.hubspot.hubspot_get_analytics.requests")
    def test_api_call_structure(self, mock_requests):
        """Test API call structure (mocked)."""
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ["HUBSPOT_API_KEY"] = "test_key"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metrics": {"total_contacts": 1000},
            "data": [],
            "summary": {},
        }
        mock_requests.get.return_value = mock_response

        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="last_30_days",
        )
        result = tool.run()

        mock_requests.get.assert_called_once()

        os.environ.pop("HUBSPOT_API_KEY")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
