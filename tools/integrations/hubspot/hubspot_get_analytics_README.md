# HubSpot Get Analytics Tool

Comprehensive analytics and reporting for HubSpot CRM and marketing data.

## Overview

Retrieve detailed analytics across:
- Contact metrics and growth
- Deal pipeline analytics
- Email campaign performance
- Conversion tracking
- Revenue reporting
- Engagement metrics
- Custom reports

## Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `report_type` | str | Analytics type (contacts, deals, emails, conversions, pipeline, revenue, engagement, custom) |

### Time Range (One Required)

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` + `end_date` | str | Custom date range (YYYY-MM-DD) |
| `time_period` | str | Predefined period (today, yesterday, last_7_days, last_30_days, this_month, last_month, this_quarter, this_year) |

### Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `pipeline_id` | str | Filter by pipeline |
| `dealstage` | str | Filter by deal stage |
| `email_campaign_id` | str | Filter by campaign |
| `owner_id` | str | Filter by owner/user |

### Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `metrics` | List[str] | None | Specific metrics to retrieve |
| `group_by` | str | None | Group by (day, week, month, owner, pipeline, source) |
| `include_details` | bool | False | Include detailed breakdown |
| `limit` | int | 100 | Max results (1-1000) |

## Report Types

### Contacts Analytics

```python
tool = HubSpotGetAnalytics(
    report_type="contacts",
    time_period="last_30_days",
    metrics=["new_contacts", "by_lifecycle_stage"],
    group_by="day"
)
result = tool.run()

print(f"Total contacts: {result['metrics']['total_contacts']:,}")
print(f"New: {result['metrics']['new_contacts']:,}")
print(f"Growth rate: {result['metrics']['growth_rate']:.1%}")
```

**Metrics:** total_contacts, new_contacts, active_contacts, by_lifecycle_stage, growth_rate

### Pipeline Analytics

```python
tool = HubSpotGetAnalytics(
    report_type="pipeline",
    time_period="this_month",
    pipeline_id="default",
    group_by="stage"
)
result = tool.run()

print(f"Pipeline value: ${result['metrics']['total_pipeline_value']:,}")
print(f"Weighted: ${result['metrics']['weighted_pipeline_value']:,}")
print(f"Forecast commit: ${result['metrics']['forecast']['commit']:,}")
```

**Metrics:** total_pipeline_value, weighted_pipeline_value, deals_by_stage, forecast

### Email Analytics

```python
tool = HubSpotGetAnalytics(
    report_type="emails",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
result = tool.run()

print(f"Sent: {result['metrics']['total_sent']:,}")
print(f"Open rate: {result['metrics']['open_rate']:.1%}")
print(f"Click rate: {result['metrics']['click_rate']:.1%}")
```

**Metrics:** total_sent, delivered, opened, clicked, bounced, unsubscribed, open_rate, click_rate

### Revenue Analytics

```python
tool = HubSpotGetAnalytics(
    report_type="revenue",
    time_period="this_quarter"
)
result = tool.run()

print(f"Revenue: ${result['metrics']['total_revenue']:,}")
print(f"MRR: ${result['metrics']['mrr']:,}")
print(f"ARR: ${result['metrics']['arr']:,}")
```

**Metrics:** total_revenue, new_revenue, recurring_revenue, mrr, arr, growth_rate

## Examples

### Dashboard Metrics

```python
def get_dashboard_metrics():
    """Get key metrics for executive dashboard."""
    from tools.integrations.hubspot import HubSpotGetAnalytics

    # Pipeline
    pipeline = HubSpotGetAnalytics(
        report_type="pipeline",
        time_period="this_month"
    ).run()

    # Revenue
    revenue = HubSpotGetAnalytics(
        report_type="revenue",
        time_period="this_month"
    ).run()

    # Contacts
    contacts = HubSpotGetAnalytics(
        report_type="contacts",
        time_period="this_month"
    ).run()

    return {
        "pipeline_value": pipeline['metrics']['total_pipeline_value'],
        "win_rate": pipeline['metrics']['deals_by_stage'],
        "monthly_revenue": revenue['metrics']['total_revenue'],
        "new_contacts": contacts['metrics']['new_contacts']
    }
```

### Trend Analysis

```python
def analyze_trends(report_type, days=30):
    """Analyze trends over time period."""
    tool = HubSpotGetAnalytics(
        report_type=report_type,
        time_period=f"last_{days}_days",
        group_by="day",
        include_details=True
    )
    result = tool.run()

    # Calculate trend
    data = result['data']
    if len(data) >= 2:
        first_value = data[0]['value']
        last_value = data[-1]['value']
        trend = ((last_value - first_value) / first_value) * 100
        print(f"Trend: {trend:+.1f}%")

    return result
```

## Best Practices

### 1. Cache Analytics Data

```python
import json
from datetime import datetime, timedelta

class AnalyticsCache:
    def __init__(self, ttl_minutes=60):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def get_analytics(self, report_type, time_period):
        key = f"{report_type}_{time_period}"

        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data

        # Fetch fresh data
        tool = HubSpotGetAnalytics(
            report_type=report_type,
            time_period=time_period
        )
        data = tool.run()

        self.cache[key] = (data, datetime.now())
        return data
```

### 2. Alert on Anomalies

```python
def check_for_anomalies():
    """Alert on unusual metrics."""
    tool = HubSpotGetAnalytics(
        report_type="emails",
        time_period="today"
    )
    result = tool.run()

    # Check thresholds
    if result['metrics']['open_rate'] < 0.10:
        send_alert("Low open rate: {:.1%}".format(result['metrics']['open_rate']))

    if result['metrics']['bounce_rate'] > 0.05:
        send_alert("High bounce rate: {:.1%}".format(result['metrics']['bounce_rate']))
```

## Related Tools

- **HubSpotCreateContact**: Create contacts to analyze
- **HubSpotTrackDeal**: Create deals to track
- **HubSpotSendEmail**: Send emails to measure

## API Reference

HubSpot Analytics API: https://developers.hubspot.com/docs/api/analytics
