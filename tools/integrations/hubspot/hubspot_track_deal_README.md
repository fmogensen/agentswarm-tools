# HubSpot Track Deal Tool

Comprehensive guide for the HubSpotTrackDeal tool - manage deals, track sales pipelines, forecast revenue, and win/lose deals in HubSpot CRM.

## Table of Contents

- [Overview](#overview)
- [Parameters](#parameters)
- [Returns](#returns)
- [Deal Stages & Forecasting](#deal-stages--forecasting)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

The HubSpotTrackDeal tool provides complete deal lifecycle management:

- Create, update, win, and lose deals
- Multi-pipeline support
- Stage progression tracking
- Revenue forecasting with categories
- Deal associations (contacts, companies)
- Batch deal operations (up to 10)
- Custom deal properties

### Use Cases

- **Sales Pipeline Management**: Track deals through stages
- **Revenue Forecasting**: Categorize deals by likelihood
- **Deal Tracking**: Monitor deal progress and values
- **Sales Performance**: Analyze win rates and deal cycles
- **Opportunity Management**: Create and track opportunities

## Parameters

### Required for Creation

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `dealname` | str | Name of the deal | Required for creation, max 200 chars |

### Deal Properties

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `amount` | float | None | Deal value (0-999999999) |
| `dealstage` | str | None | Deal stage ID or name |
| `pipeline` | str | None | Pipeline ID (default uses account default) |
| `closedate` | str | None | Expected close date (YYYY-MM-DD or Unix ms) |
| `dealtype` | str | None | Deal type (newbusiness, existingbusiness, renewal) |
| `description` | str | None | Deal description (max 2000 chars) |
| `priority` | str | None | Deal priority (low, medium, high) |

### Associations

| Parameter | Type | Description |
|-----------|------|-------------|
| `contact_ids` | List[str] | Contact IDs to associate with deal |
| `company_ids` | List[str] | Company IDs to associate with deal |

### Deal Operations

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `deal_id` | str | None | Deal ID for update/win/lose operations |
| `move_to_stage` | str | None | Move deal to specified stage |
| `win_deal` | bool | False | Mark deal as won (closedwon) |
| `lose_deal` | bool | False | Mark deal as lost (closedlost) |
| `loss_reason` | str | None | Reason for losing deal |

### Batch Operations

| Parameter | Type | Description |
|-----------|------|-------------|
| `batch_deals` | List[Dict] | List of deal dictionaries (max 10) |
| `custom_properties` | Dict | Custom property key-value pairs |

## Returns

### Create/Update Response

```python
{
    "success": True,
    "deal_id": "987654321",
    "dealname": "Acme Corp - Q1 Contract",
    "amount": 50000.0,
    "dealstage": "qualifiedtobuy",
    "pipeline": "default",
    "status": "created",  # or "updated", "won", "lost"
    "closedate": "1711929600000",  # Unix timestamp ms
    "associations": {
        "contacts": ["12345"],
        "companies": ["67890"]
    },
    "forecast_category": "best_case",
    "metadata": {
        "tool_name": "hubspot_track_deal"
    }
}
```

### Batch Response

```python
{
    "success": True,
    "status": "batch_processed",
    "deal_ids": ["123", "456", "789"],
    "deals_created": 3,
    "metadata": {
        "tool_name": "hubspot_track_deal",
        "batch_size": 3
    }
}
```

## Deal Stages & Forecasting

### Standard Deal Stages

| Stage | Description | Forecast Category |
|-------|-------------|-------------------|
| `appointmentscheduled` | Initial meeting scheduled | Pipeline |
| `qualifiedtobuy` | Buyer qualified | Best Case |
| `presentationscheduled` | Demo/presentation scheduled | Best Case |
| `decisionmakerboughtin` | Decision maker engaged | Commit |
| `contractsent` | Contract sent to buyer | Commit |
| `closedwon` | Deal won | Closed Won |
| `closedlost` | Deal lost | Closed Lost |

### Forecast Categories

- **Pipeline**: Early stage, low confidence (appointmentscheduled)
- **Best Case**: Qualified, medium confidence (qualifiedtobuy, presentationscheduled)
- **Commit**: High confidence, late stage (decisionmakerboughtin, contractsent)
- **Closed Won**: Deal won
- **Closed Lost**: Deal lost
- **Omitted**: Not forecasted

## Examples

### Create Deal

```python
from tools.integrations.hubspot import HubSpotTrackDeal

tool = HubSpotTrackDeal(
    dealname="Acme Corp - Enterprise Contract",
    amount=75000,
    dealstage="qualifiedtobuy",
    closedate="2024-06-30",
    dealtype="newbusiness",
    priority="high",
    description="Enterprise plan with 24-month commitment",
    contact_ids=["12345"],
    company_ids=["67890"],
    custom_properties={
        "contract_term": "24 months",
        "mrr": "3125",
        "implementation_fee": "15000"
    }
)

result = tool.run()
print(f"Deal created: {result['deal_id']}")
print(f"Forecast: {result['forecast_category']}")
```

### Update Deal Stage

```python
# Move deal through pipeline
tool = HubSpotTrackDeal(
    deal_id="987654321",
    move_to_stage="presentationscheduled",
    amount=80000  # Updated amount
)

result = tool.run()
print(f"Deal moved to: {result['dealstage']}")
```

### Win Deal

```python
# Close deal as won
tool = HubSpotTrackDeal(
    deal_id="987654321",
    win_deal=True,
    amount=82500,  # Final negotiated amount
    custom_properties={
        "won_date": "2024-03-15",
        "sales_rep": "John Smith"
    }
)

result = tool.run()
print(f"Deal won! Status: {result['status']}")
print(f"Final value: ${result['amount']:,}")
```

### Lose Deal

```python
# Close deal as lost
tool = HubSpotTrackDeal(
    deal_id="123456789",
    lose_deal=True,
    loss_reason="Budget constraints - postponed to Q3"
)

result = tool.run()
print(f"Deal lost. Reason: {result.get('loss_reason', 'Not specified')}")
```

### Batch Deal Creation

```python
deals = [
    {
        "dealname": "Small Biz - Starter Plan",
        "amount": 5000,
        "dealstage": "appointmentscheduled",
        "dealtype": "newbusiness"
    },
    {
        "dealname": "MidMarket - Professional",
        "amount": 25000,
        "dealstage": "qualifiedtobuy",
        "dealtype": "newbusiness"
    },
    {
        "dealname": "Enterprise - Renewal",
        "amount": 100000,
        "dealstage": "contractsent",
        "dealtype": "renewal"
    }
]

tool = HubSpotTrackDeal(batch_deals=deals)
result = tool.run()

print(f"Created {result['deals_created']} deals")
print(f"Deal IDs: {result['deal_ids']}")
```

### Deal with Multiple Associations

```python
tool = HubSpotTrackDeal(
    dealname="Multi-Stakeholder Deal",
    amount=150000,
    dealstage="decisionmakerboughtin",
    contact_ids=["123", "456", "789"],  # Multiple decision makers
    company_ids=["company_1"],
    custom_properties={
        "decision_makers_count": "3",
        "buying_committee": "CFO, CTO, CEO"
    }
)

result = tool.run()
print(f"Associated with {len(result['associations']['contacts'])} contacts")
```

## Best Practices

### 1. Track Deal Progression

```python
def move_deal_through_pipeline(deal_id, stages):
    """Move deal through multiple stages with validation."""
    current_stage = None

    for stage in stages:
        tool = HubSpotTrackDeal(
            deal_id=deal_id,
            move_to_stage=stage
        )
        result = tool.run()

        if result['success']:
            print(f"Moved to {stage}")
            current_stage = stage
        else:
            print(f"Failed to move to {stage}")
            break

    return current_stage

# Usage
stages = ["qualifiedtobuy", "presentationscheduled", "contractsent"]
final_stage = move_deal_through_pipeline("deal_123", stages)
```

### 2. Revenue Forecasting

```python
from tools.integrations.hubspot import HubSpotGetAnalytics

def get_weighted_pipeline():
    """Calculate weighted pipeline value by forecast category."""
    tool = HubSpotGetAnalytics(
        report_type="pipeline",
        time_period="this_quarter"
    )
    result = tool.run()

    forecast = result['metrics']['forecast']

    # Apply probability weights
    weighted_value = (
        forecast['commit'] * 0.90 +
        forecast['best_case'] * 0.50 +
        forecast['pipeline'] * 0.25
    )

    print(f"Weighted pipeline: ${weighted_value:,.0f}")
    return weighted_value
```

### 3. Deal Qualification

```python
def create_qualified_deal(contact_id, company_id, budget, timeline):
    """Create deal with qualification criteria."""

    # Determine initial stage based on qualification
    if budget >= 50000 and timeline <= "Q2 2024":
        stage = "qualifiedtobuy"
        priority = "high"
    elif budget >= 20000:
        stage = "appointmentscheduled"
        priority = "medium"
    else:
        stage = "appointmentscheduled"
        priority = "low"

    tool = HubSpotTrackDeal(
        dealname=f"Opportunity - {company_id}",
        amount=budget,
        dealstage=stage,
        priority=priority,
        closedate=timeline,
        contact_ids=[contact_id],
        company_ids=[company_id],
        custom_properties={
            "budget_confirmed": "true",
            "timeline_confirmed": "true"
        }
    )

    return tool.run()
```

### 4. Deal Stages Automation

```python
def auto_progress_deal(deal_id, trigger_event):
    """Automatically progress deal based on events."""

    stage_mapping = {
        "demo_completed": "presentationscheduled",
        "proposal_sent": "decisionmakerboughtin",
        "contract_sent": "contractsent",
        "payment_received": "closedwon"
    }

    if trigger_event in stage_mapping:
        tool = HubSpotTrackDeal(
            deal_id=deal_id,
            move_to_stage=stage_mapping[trigger_event]
        )
        return tool.run()
```

### 5. Lost Deal Analysis

```python
def analyze_lost_deals(time_period="this_quarter"):
    """Analyze reasons for lost deals."""
    from tools.integrations.hubspot import HubSpotGetAnalytics

    tool = HubSpotGetAnalytics(
        report_type="deals",
        time_period=time_period
    )
    result = tool.run()

    lost_deals = result['metrics']['lost_deals']
    total_deals = result['metrics']['total_deals']
    loss_rate = lost_deals / total_deals if total_deals > 0 else 0

    print(f"Lost {lost_deals} deals ({loss_rate:.1%} loss rate)")
    return {
        "lost_deals": lost_deals,
        "loss_rate": loss_rate
    }
```

## Advanced Usage

### Multi-Pipeline Management

```python
# Create deal in custom pipeline
tool = HubSpotTrackDeal(
    dealname="Enterprise Deal",
    amount=200000,
    dealstage="discovery",
    pipeline="enterprise_pipeline_123",
    closedate="2024-12-31"
)
result = tool.run()
```

### Deal Stage Validation

```python
def validate_stage_transition(current_stage, new_stage):
    """Validate stage transitions."""
    valid_progressions = {
        "appointmentscheduled": ["qualifiedtobuy", "closedlost"],
        "qualifiedtobuy": ["presentationscheduled", "closedlost"],
        "presentationscheduled": ["decisionmakerboughtin", "closedlost"],
        "decisionmakerboughtin": ["contractsent", "closedlost"],
        "contractsent": ["closedwon", "closedlost"]
    }

    return new_stage in valid_progressions.get(current_stage, [])
```

### Deal Velocity Tracking

```python
from datetime import datetime

def calculate_deal_velocity(deal_created_date, current_stage):
    """Calculate how long deal has been in current stage."""
    created = datetime.fromisoformat(deal_created_date)
    now = datetime.now()
    days_in_stage = (now - created).days

    # Alert if stuck too long
    if current_stage == "qualifiedtobuy" and days_in_stage > 30:
        print("⚠️ Deal stuck in qualified stage for >30 days")

    return days_in_stage
```

## Related Tools

- **HubSpotCreateContact**: Create contacts to associate with deals
- **HubSpotGetAnalytics**: Analyze deal pipeline and performance
- **HubSpotSyncCalendar**: Schedule sales meetings for deals
- **HubSpotSendEmail**: Send deal-related communications

## API Reference

HubSpot Deals API: https://developers.hubspot.com/docs/api/crm/deals
