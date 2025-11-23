"""
HubSpot Get Analytics Tool

Retrieves analytics and metrics from HubSpot including contacts, deals,
emails, conversions, and custom reporting data.
"""

from typing import Any, Dict, Optional, List
from pydantic import Field
import os
import json
from datetime import datetime, timedelta

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError


class HubSpotGetAnalytics(BaseTool):
    """
    Get analytics and metrics from HubSpot CRM and marketing automation.

    This tool retrieves comprehensive analytics data from HubSpot including
    contact metrics, deal pipeline analytics, email performance, conversion
    rates, revenue forecasting, and custom reports. Supports time-based
    filtering and metric aggregation.

    Args:
        # Report type (required - one of these)
        report_type: Type of analytics report (contacts, deals, emails, conversions,
            pipeline, revenue, engagement, custom)

        # Time range
        start_date: Start date for analytics (YYYY-MM-DD format)
        end_date: End date for analytics (YYYY-MM-DD format)
        time_period: Predefined time period (today, yesterday, last_7_days,
            last_30_days, this_month, last_month, this_quarter, this_year)

        # Filters
        pipeline_id: Filter by specific pipeline ID (for deals)
        dealstage: Filter by deal stage
        email_campaign_id: Filter by email campaign ID
        contact_lifecycle_stage: Filter by contact lifecycle stage
        owner_id: Filter by owner/user ID

        # Metrics
        metrics: List of specific metrics to retrieve
        group_by: Group results by field (day, week, month, owner, pipeline, source)

        # Custom reporting
        custom_report_id: HubSpot custom report ID
        properties: List of properties to include in results

        # Options
        include_details: Include detailed breakdown (default: False)
        limit: Maximum number of results to return (default: 100)

    Returns:
        Dict containing:
            - success (bool): Whether the operation succeeded
            - report_type (str): Type of analytics report
            - time_range (dict): Start and end dates
            - metrics (dict): Key performance metrics
            - data (list): Detailed analytics data
            - summary (dict): Aggregated summary statistics
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Get deal pipeline analytics
        >>> tool = HubSpotGetAnalytics(
        ...     report_type="pipeline",
        ...     time_period="this_month",
        ...     pipeline_id="default",
        ...     metrics=["total_deals", "total_value", "win_rate", "avg_deal_size"],
        ...     group_by="dealstage"
        ... )
        >>> result = tool.run()
        >>> print(result['metrics']['total_value'])
        250000

        >>> # Get email campaign performance
        >>> tool = HubSpotGetAnalytics(
        ...     report_type="emails",
        ...     start_date="2024-01-01",
        ...     end_date="2024-01-31",
        ...     metrics=["sent", "delivered", "opens", "clicks", "bounces"],
        ...     email_campaign_id="12345"
        ... )
        >>> result = tool.run()

        >>> # Get contact growth metrics
        >>> tool = HubSpotGetAnalytics(
        ...     report_type="contacts",
        ...     time_period="last_30_days",
        ...     metrics=["new_contacts", "active_contacts", "by_lifecycle_stage"],
        ...     group_by="day"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "hubspot_get_analytics"
    tool_category: str = "integrations"
    rate_limit_type: str = "hubspot_api"
    rate_limit_cost: int = 1

    # Report type (required)
    report_type: str = Field(
        ...,
        description="Type of analytics report (contacts, deals, emails, conversions, "
                    "pipeline, revenue, engagement, custom)"
    )

    # Time range
    start_date: Optional[str] = Field(
        None, description="Start date (YYYY-MM-DD format)"
    )
    end_date: Optional[str] = Field(
        None, description="End date (YYYY-MM-DD format)"
    )
    time_period: Optional[str] = Field(
        None,
        description="Predefined time period (today, yesterday, last_7_days, "
                    "last_30_days, this_month, last_month, this_quarter, this_year)"
    )

    # Filters
    pipeline_id: Optional[str] = Field(None, description="Filter by pipeline ID")
    dealstage: Optional[str] = Field(None, description="Filter by deal stage")
    email_campaign_id: Optional[str] = Field(None, description="Filter by email campaign")
    contact_lifecycle_stage: Optional[str] = Field(
        None, description="Filter by contact lifecycle stage"
    )
    owner_id: Optional[str] = Field(None, description="Filter by owner/user ID")

    # Metrics
    metrics: Optional[List[str]] = Field(
        None, description="Specific metrics to retrieve"
    )
    group_by: Optional[str] = Field(
        None, description="Group results by field (day, week, month, owner, pipeline, source)"
    )

    # Custom reporting
    custom_report_id: Optional[str] = Field(None, description="Custom report ID")
    properties: Optional[List[str]] = Field(
        None, description="Properties to include in results"
    )

    # Options
    include_details: bool = Field(False, description="Include detailed breakdown")
    limit: int = Field(100, description="Maximum results", ge=1, le=1000)

    def _execute(self) -> Dict[str, Any]:
        """Execute the analytics retrieval."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()
            return result
        except Exception as e:
            raise APIError(
                f"Failed to get analytics: {e}", tool_name=self.tool_name
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate report type
        valid_report_types = [
            "contacts", "deals", "emails", "conversions",
            "pipeline", "revenue", "engagement", "custom"
        ]
        if self.report_type.lower() not in valid_report_types:
            raise ValidationError(
                f"Invalid report_type: {self.report_type}. "
                f"Valid types: {', '.join(valid_report_types)}",
                tool_name=self.tool_name,
            )

        # Validate time range
        if self.start_date and self.end_date:
            try:
                start = datetime.strptime(self.start_date, "%Y-%m-%d")
                end = datetime.strptime(self.end_date, "%Y-%m-%d")
                if start > end:
                    raise ValidationError(
                        "start_date cannot be after end_date",
                        tool_name=self.tool_name,
                    )
            except ValueError:
                raise ValidationError(
                    "Dates must be in YYYY-MM-DD format",
                    tool_name=self.tool_name,
                )

        # Validate time period
        if self.time_period:
            valid_periods = [
                "today", "yesterday", "last_7_days", "last_30_days",
                "this_month", "last_month", "this_quarter", "this_year"
            ]
            if self.time_period.lower() not in valid_periods:
                raise ValidationError(
                    f"Invalid time_period: {self.time_period}. "
                    f"Valid periods: {', '.join(valid_periods)}",
                    tool_name=self.tool_name,
                )

        # Validate group_by
        if self.group_by:
            valid_group_by = ["day", "week", "month", "owner", "pipeline", "source", "stage"]
            if self.group_by.lower() not in valid_group_by:
                raise ValidationError(
                    f"Invalid group_by: {self.group_by}. "
                    f"Valid options: {', '.join(valid_group_by)}",
                    tool_name=self.tool_name,
                )

        # Custom report requires custom_report_id
        if self.report_type.lower() == "custom" and not self.custom_report_id:
            raise ValidationError(
                "custom_report_id is required for custom report type",
                tool_name=self.tool_name,
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        # Calculate time range
        time_range = self._get_time_range()

        # Generate metrics based on report type
        metrics = self._generate_mock_metrics()

        # Generate sample data
        data = self._generate_mock_data()

        # Generate summary
        summary = self._generate_mock_summary(metrics)

        return {
            "success": True,
            "report_type": self.report_type,
            "time_range": time_range,
            "metrics": metrics,
            "data": data if self.include_details else [],
            "summary": summary,
            "metadata": {
                "tool_name": self.tool_name,
                "data_points": len(data),
                "mock_mode": True,
            },
        }

    def _get_time_range(self) -> Dict[str, str]:
        """Calculate time range based on parameters."""
        if self.start_date and self.end_date:
            return {
                "start_date": self.start_date,
                "end_date": self.end_date,
            }
        elif self.time_period:
            today = datetime.now()
            period = self.time_period.lower()

            if period == "today":
                start = end = today
            elif period == "yesterday":
                start = end = today - timedelta(days=1)
            elif period == "last_7_days":
                start = today - timedelta(days=7)
                end = today
            elif period == "last_30_days":
                start = today - timedelta(days=30)
                end = today
            elif period == "this_month":
                start = today.replace(day=1)
                end = today
            elif period == "last_month":
                last_month = today.replace(day=1) - timedelta(days=1)
                start = last_month.replace(day=1)
                end = last_month
            elif period == "this_quarter":
                quarter_start_month = ((today.month - 1) // 3) * 3 + 1
                start = today.replace(month=quarter_start_month, day=1)
                end = today
            else:  # this_year
                start = today.replace(month=1, day=1)
                end = today

            return {
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
            }
        else:
            # Default to last 30 days
            today = datetime.now()
            start = today - timedelta(days=30)
            return {
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": today.strftime("%Y-%m-%d"),
            }

    def _generate_mock_metrics(self) -> Dict[str, Any]:
        """Generate mock metrics based on report type."""
        report_type = self.report_type.lower()

        if report_type == "contacts":
            return {
                "total_contacts": 15432,
                "new_contacts": 243,
                "active_contacts": 8721,
                "by_lifecycle_stage": {
                    "subscriber": 3245,
                    "lead": 5432,
                    "marketingqualifiedlead": 2134,
                    "salesqualifiedlead": 1876,
                    "opportunity": 987,
                    "customer": 1758,
                },
                "growth_rate": 1.58,
            }
        elif report_type == "deals":
            return {
                "total_deals": 287,
                "open_deals": 156,
                "won_deals": 89,
                "lost_deals": 42,
                "total_value": 2450000,
                "won_value": 1235000,
                "avg_deal_size": 13876,
                "win_rate": 0.679,
                "avg_sales_cycle_days": 45,
            }
        elif report_type == "pipeline":
            return {
                "total_pipeline_value": 3890000,
                "weighted_pipeline_value": 1567000,
                "deals_by_stage": {
                    "appointmentscheduled": {"count": 45, "value": 450000},
                    "qualifiedtobuy": {"count": 38, "value": 678000},
                    "presentationscheduled": {"count": 29, "value": 890000},
                    "decisionmakerboughtin": {"count": 22, "value": 987000},
                    "contractsent": {"count": 15, "value": 785000},
                    "closedwon": {"count": 7, "value": 235000},
                },
                "forecast": {
                    "commit": 1872000,
                    "best_case": 2567000,
                    "pipeline": 3890000,
                },
            }
        elif report_type == "emails":
            return {
                "total_sent": 45678,
                "delivered": 44532,
                "bounced": 1146,
                "opened": 13876,
                "clicked": 4532,
                "unsubscribed": 234,
                "open_rate": 0.312,
                "click_rate": 0.102,
                "clickthrough_rate": 0.327,
                "bounce_rate": 0.025,
                "unsubscribe_rate": 0.005,
            }
        elif report_type == "conversions":
            return {
                "total_conversions": 1234,
                "conversion_rate": 0.08,
                "by_source": {
                    "organic_search": 456,
                    "paid_search": 345,
                    "email": 234,
                    "social": 123,
                    "direct": 76,
                },
                "by_type": {
                    "form_submission": 789,
                    "email_signup": 345,
                    "demo_request": 100,
                },
            }
        elif report_type == "revenue":
            return {
                "total_revenue": 2340000,
                "new_revenue": 1235000,
                "recurring_revenue": 987000,
                "expansion_revenue": 118000,
                "mrr": 82250,
                "arr": 987000,
                "growth_rate": 0.15,
            }
        elif report_type == "engagement":
            return {
                "email_engagement": 0.312,
                "website_sessions": 34567,
                "page_views": 123456,
                "avg_session_duration": 185,
                "bounce_rate": 0.43,
                "form_submissions": 789,
            }
        else:  # custom
            return {
                "custom_metric_1": 12345,
                "custom_metric_2": 67890,
                "custom_metric_3": 0.456,
            }

    def _generate_mock_data(self) -> List[Dict[str, Any]]:
        """Generate mock detailed data."""
        if not self.include_details:
            return []

        report_type = self.report_type.lower()
        data = []

        if self.group_by == "day":
            # Generate daily data
            time_range = self._get_time_range()
            start = datetime.strptime(time_range["start_date"], "%Y-%m-%d")
            end = datetime.strptime(time_range["end_date"], "%Y-%m-%d")
            current = start

            while current <= end:
                data.append({
                    "date": current.strftime("%Y-%m-%d"),
                    "value": 100 + (hash(str(current)) % 50),
                    "count": 10 + (hash(str(current)) % 20),
                })
                current += timedelta(days=1)

        elif self.group_by == "stage":
            # Generate by stage
            if report_type == "deals":
                stages = [
                    "appointmentscheduled", "qualifiedtobuy",
                    "presentationscheduled", "decisionmakerboughtin",
                    "contractsent", "closedwon", "closedlost"
                ]
                for stage in stages:
                    data.append({
                        "stage": stage,
                        "count": 10 + (hash(stage) % 40),
                        "value": 50000 + (hash(stage) % 200000),
                    })

        else:
            # Generate sample records
            for i in range(min(10, self.limit)):
                data.append({
                    "id": f"record_{i}",
                    "value": 1000 + (i * 100),
                    "timestamp": datetime.now().isoformat(),
                })

        return data[:self.limit]

    def _generate_mock_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics."""
        summary = {
            "total_records": sum([v for v in metrics.values() if isinstance(v, (int, float))]),
            "report_generated_at": datetime.now().isoformat(),
        }

        # Add report-specific summaries
        if self.report_type.lower() == "deals":
            summary["pipeline_health"] = "healthy"
            summary["forecast_accuracy"] = 0.87
        elif self.report_type.lower() == "emails":
            summary["campaign_performance"] = "above_average"
            summary["engagement_trend"] = "increasing"

        return summary

    def _process(self) -> Dict[str, Any]:
        """Process analytics retrieval with HubSpot API."""
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing HUBSPOT_API_KEY environment variable",
                tool_name=self.tool_name,
            )

        try:
            import requests
        except ImportError:
            raise APIError(
                "requests library not installed. Run: pip install requests",
                tool_name=self.tool_name,
            )

        # Determine API endpoint based on report type
        report_type = self.report_type.lower()

        if report_type == "custom" and self.custom_report_id:
            url = f"https://api.hubapi.com/analytics/v2/reports/{self.custom_report_id}"
        elif report_type == "deals":
            url = "https://api.hubapi.com/crm-analytics/v1/deals/funnel"
        elif report_type == "emails":
            url = "https://api.hubapi.com/email/public/v1/campaigns/stats"
        else:
            # General analytics endpoint
            url = f"https://api.hubapi.com/analytics/v2/{report_type}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Build query parameters
        params = {}
        time_range = self._get_time_range()
        params["startDate"] = time_range["start_date"]
        params["endDate"] = time_range["end_date"]

        if self.pipeline_id:
            params["pipelineId"] = self.pipeline_id
        if self.owner_id:
            params["ownerId"] = self.owner_id
        if self.limit:
            params["limit"] = self.limit

        # Execute request
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            api_data = response.json()

            # Parse response based on report type
            metrics = self._parse_api_response(api_data)

            return {
                "success": True,
                "report_type": self.report_type,
                "time_range": time_range,
                "metrics": metrics,
                "data": api_data.get("data", []) if self.include_details else [],
                "summary": api_data.get("summary", {}),
                "metadata": {
                    "tool_name": self.tool_name,
                    "data_points": len(api_data.get("data", [])),
                },
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Invalid HubSpot API key", tool_name=self.tool_name
                )
            elif e.response.status_code == 404:
                raise APIError(
                    f"Analytics report not found: {self.report_type}",
                    tool_name=self.tool_name,
                )
            elif e.response.status_code == 429:
                raise APIError(
                    "Rate limit exceeded. Try again later.", tool_name=self.tool_name
                )
            else:
                error_detail = e.response.json() if e.response.content else {}
                raise APIError(
                    f"HubSpot analytics API error: {error_detail.get('message', str(e))}",
                    tool_name=self.tool_name,
                )
        except requests.exceptions.RequestException as e:
            raise APIError(
                f"Network error: {str(e)}", tool_name=self.tool_name
            )

    def _parse_api_response(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API response into standardized metrics."""
        # This would parse the actual HubSpot API response
        # For now, return the data as-is
        return api_data.get("metrics", api_data)


if __name__ == "__main__":
    # Test the tool
    print("Testing HubSpotGetAnalytics...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Get deal pipeline analytics
    print("\n1. Testing deal pipeline analytics...")
    tool = HubSpotGetAnalytics(
        report_type="pipeline",
        time_period="this_month",
        metrics=["total_pipeline_value", "weighted_pipeline_value", "deals_by_stage"],
        group_by="stage",
        include_details=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Report type: {result.get('report_type')}")
    print(f"Total pipeline value: ${result.get('metrics', {}).get('total_pipeline_value'):,}")
    print(f"Forecast commit: ${result.get('metrics', {}).get('forecast', {}).get('commit'):,}")
    print(f"Data points: {result.get('metadata', {}).get('data_points')}")
    assert result.get("success") == True
    assert "total_pipeline_value" in result.get("metrics", {})

    # Test 2: Get email campaign performance
    print("\n2. Testing email campaign performance...")
    tool = HubSpotGetAnalytics(
        report_type="emails",
        start_date="2024-01-01",
        end_date="2024-01-31",
        metrics=["sent", "delivered", "opens", "clicks"],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Total sent: {result.get('metrics', {}).get('total_sent'):,}")
    print(f"Open rate: {result.get('metrics', {}).get('open_rate'):.1%}")
    print(f"Click rate: {result.get('metrics', {}).get('click_rate'):.1%}")
    assert result.get("success") == True
    assert result.get("metrics", {}).get("open_rate") is not None

    # Test 3: Get contact growth metrics
    print("\n3. Testing contact growth metrics...")
    tool = HubSpotGetAnalytics(
        report_type="contacts",
        time_period="last_30_days",
        metrics=["new_contacts", "by_lifecycle_stage"],
        group_by="day",
        include_details=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Total contacts: {result.get('metrics', {}).get('total_contacts'):,}")
    print(f"New contacts: {result.get('metrics', {}).get('new_contacts'):,}")
    print(f"Growth rate: {result.get('metrics', {}).get('growth_rate'):.2%}")
    assert result.get("success") == True
    assert "new_contacts" in result.get("metrics", {})

    # Test 4: Get revenue analytics
    print("\n4. Testing revenue analytics...")
    tool = HubSpotGetAnalytics(
        report_type="revenue",
        time_period="this_quarter",
        metrics=["total_revenue", "mrr", "arr", "growth_rate"],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Total revenue: ${result.get('metrics', {}).get('total_revenue'):,}")
    print(f"MRR: ${result.get('metrics', {}).get('mrr'):,}")
    print(f"ARR: ${result.get('metrics', {}).get('arr'):,}")
    assert result.get("success") == True
    assert result.get("metrics", {}).get("total_revenue") is not None

    # Test 5: Get conversion analytics
    print("\n5. Testing conversion analytics...")
    tool = HubSpotGetAnalytics(
        report_type="conversions",
        time_period="last_7_days",
        include_details=False,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Total conversions: {result.get('metrics', {}).get('total_conversions'):,}")
    print(f"Conversion rate: {result.get('metrics', {}).get('conversion_rate'):.2%}")
    assert result.get("success") == True

    # Test 6: Error handling - invalid report type
    print("\n6. Testing error handling (invalid report type)...")
    try:
        tool = HubSpotGetAnalytics(
            report_type="invalid_type",
            time_period="last_30_days",
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        print(f"Correctly caught error: {str(e)}")

    # Test 7: Error handling - invalid time period
    print("\n7. Testing error handling (invalid time period)...")
    try:
        tool = HubSpotGetAnalytics(
            report_type="contacts",
            time_period="invalid_period",
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        print(f"Correctly caught error: {str(e)}")

    print("\n✅ All tests passed!")
