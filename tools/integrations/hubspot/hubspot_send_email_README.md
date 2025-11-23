# HubSpot Send Email Tool

Complete guide for HubSpotSendEmail - send marketing emails with templates, personalization, tracking, and campaign management in HubSpot.

## Overview

Send professional marketing emails with:
- Template-based or custom HTML emails
- Contact/list targeting
- Personalization tokens
- Email tracking (opens, clicks)
- Scheduled sending
- Campaign management
- A/B testing support
- Batch sending (up to 10)

## Parameters

### Email Content (Required - One Of)

| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | str | HubSpot email template ID |
| `subject` + `body` | str | Custom subject and HTML body (both required if not using template) |

### Recipients (Required - One Of)

| Parameter | Type | Description |
|-----------|------|-------------|
| `contact_ids` | List[str] | Specific contact IDs |
| `list_ids` | List[str] | Contact list IDs |
| `recipient_email` | str | Single recipient email |

### Sender (Required)

| Parameter | Type | Description |
|-----------|------|-------------|
| `from_email` | str | Sender email (must be verified in HubSpot) |
| `from_name` | str | Sender display name |
| `reply_to` | str | Reply-to email address |

### Personalization

| Parameter | Type | Description |
|-----------|------|-------------|
| `personalization_tokens` | Dict | Token name-value pairs for merge fields |
| `contact_properties` | List[str] | Contact properties to use in email |

### Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_opens` | bool | True | Track email opens |
| `track_clicks` | bool | True | Track link clicks |
| `subscription_type_id` | str | None | Subscription type for unsubscribe |
| `campaign_id` | str | None | Campaign to associate email with |
| `send_immediately` | bool | True | Send now or schedule |
| `scheduled_time` | str | None | ISO 8601 or Unix timestamp |

## Examples

### Template Email to Contacts

```python
from tools.integrations.hubspot import HubSpotSendEmail

tool = HubSpotSendEmail(
    template_id="12345678",
    contact_ids=["contact1", "contact2"],
    from_email="marketing@company.com",
    from_name="Marketing Team",
    personalization_tokens={
        "first_name": "John",
        "discount_code": "SAVE20"
    },
    track_opens=True,
    track_clicks=True
)

result = tool.run()
print(f"Email sent: {result['email_id']}")
print(f"Recipients: {result['recipients_count']}")
```

### Custom HTML Email to List

```python
html_body = """
<h1>Special Offer - 20% Off!</h1>
<p>Dear {{contact.firstname}},</p>
<p>Get 20% off all products this week.</p>
<p>Use code: <strong>SAVE20</strong></p>
<a href="https://shop.company.com">Shop Now</a>
"""

tool = HubSpotSendEmail(
    subject="Exclusive Offer - 20% Off This Week!",
    body=html_body,
    list_ids=["vip_customers_list"],
    from_email="sales@company.com",
    from_name="Sales Team",
    campaign_id="q1_promotion",
    track_opens=True,
    track_clicks=True
)

result = tool.run()
```

### Scheduled Email

```python
tool = HubSpotSendEmail(
    template_id="newsletter_template",
    list_ids=["newsletter_subscribers"],
    from_email="newsletter@company.com",
    send_immediately=False,
    scheduled_time="2024-12-25T10:00:00Z"
)

result = tool.run()
print(f"Email scheduled for: {result['scheduled_time']}")
```

### Batch Email Campaign

```python
campaigns = [
    {
        "template_id": "welcome_template",
        "contact_ids": ["new_user_1", "new_user_2"],
        "from_email": "welcome@company.com",
        "personalization_tokens": {"product": "Premium"}
    },
    {
        "subject": "Weekly Newsletter",
        "body": "<h1>This Week's Updates</h1><p>...</p>",
        "list_ids": ["newsletter_list"],
        "from_email": "news@company.com"
    }
]

tool = HubSpotSendEmail(batch_emails=campaigns)
result = tool.run()
print(f"Sent {result['emails_sent']} emails to {result['total_recipients']} recipients")
```

## Best Practices

### 1. Personalization

```python
def send_personalized_email(contact_id, contact_data):
    tool = HubSpotSendEmail(
        template_id="personalized_template",
        contact_ids=[contact_id],
        from_email="team@company.com",
        personalization_tokens={
            "first_name": contact_data['firstname'],
            "company": contact_data['company'],
            "account_value": f"${contact_data['value']:,}",
            "account_manager": contact_data['owner_name']
        }
    )
    return tool.run()
```

### 2. A/B Testing

```python
# Send variant A to half the list
tool_a = HubSpotSendEmail(
    subject="Subject Variant A",
    body="<h1>Version A</h1>",
    list_ids=["test_list_a"],
    from_email="test@company.com",
    campaign_id="ab_test_campaign",
    ab_test_id="variant_a"
)
result_a = tool_a.run()

# Send variant B to other half
tool_b = HubSpotSendEmail(
    subject="Subject Variant B",
    body="<h1>Version B</h1>",
    list_ids=["test_list_b"],
    from_email="test@company.com",
    campaign_id="ab_test_campaign",
    ab_test_id="variant_b"
)
result_b = tool_b.run()

# Analyze results later with analytics tool
```

### 3. Drip Campaigns

```python
import time

def send_drip_sequence(contact_id):
    """Send 3-email nurture sequence."""

    emails = [
        {
            "template_id": "drip_day1",
            "subject": "Welcome to Our Platform"
        },
        {
            "template_id": "drip_day3",
            "subject": "Getting Started Tips"
        },
        {
            "template_id": "drip_day7",
            "subject": "Advanced Features"
        }
    ]

    for idx, email_config in enumerate(emails):
        # Schedule each email
        send_time = datetime.now() + timedelta(days=idx*2)

        tool = HubSpotSendEmail(
            template_id=email_config['template_id'],
            contact_ids=[contact_id],
            from_email="onboarding@company.com",
            send_immediately=False,
            scheduled_time=send_time.isoformat()
        )
        tool.run()
```

### 4. Email Performance Tracking

```python
def track_campaign_performance(campaign_id):
    """Monitor email campaign metrics."""
    from tools.integrations.hubspot import HubSpotGetAnalytics

    tool = HubSpotGetAnalytics(
        report_type="emails",
        time_period="last_7_days",
        email_campaign_id=campaign_id
    )
    result = tool.run()

    metrics = result['metrics']
    print(f"Sent: {metrics['total_sent']:,}")
    print(f"Open rate: {metrics['open_rate']:.1%}")
    print(f"Click rate: {metrics['click_rate']:.1%}")

    # Alert if performance is low
    if metrics['open_rate'] < 0.15:
        print("⚠️ Low open rate - consider subject line testing")
    if metrics['click_rate'] < 0.05:
        print("⚠️ Low click rate - review CTA placement")

    return metrics
```

## Related Tools

- **HubSpotCreateContact**: Manage email recipients
- **HubSpotGetAnalytics**: Track email performance
- **HubSpotTrackDeal**: Link emails to deals

## API Reference

HubSpot Marketing Email API: https://developers.hubspot.com/docs/api/marketing/marketing-email
