"""
HubSpot Integration for AgentSwarm Tools Framework

Complete HubSpot CRM and marketing automation integration providing contact management,
deal tracking, email campaigns, analytics, and calendar synchronization.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Authentication](#authentication)
- [Available Tools](#available-tools)
- [Quick Start](#quick-start)
- [Marketing Automation Workflows](#marketing-automation-workflows)
- [Bulk Operations](#bulk-operations)
- [Rate Limits](#rate-limits)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The HubSpot integration provides 5 powerful tools for CRM and marketing automation:

1. **HubSpotCreateContact** - Create/update contacts with custom properties
2. **HubSpotTrackDeal** - Manage deals, pipelines, and sales forecasting
3. **HubSpotSendEmail** - Send marketing emails with templates
4. **HubSpotGetAnalytics** - Retrieve CRM and marketing analytics
5. **HubSpotSyncCalendar** - Sync meetings with Google Calendar

### Key Features

- Full CRUD operations for contacts and deals
- Batch operations (up to 10 records per request)
- Custom property support
- Pipeline and stage management
- Email campaign management with templates
- Comprehensive analytics and reporting
- Bidirectional calendar sync
- Rate limit handling
- Mock mode for testing

## Installation

### Prerequisites

```bash
# Install required dependencies
pip install requests>=2.31.0
pip install pydantic>=2.0.0
```

### Environment Setup

Create a `.env` file in your project root:

```bash
# HubSpot API Configuration
HUBSPOT_API_KEY=your_hubspot_api_key_here

# Optional: Google Calendar (for calendar sync)
GOOGLE_CALENDAR_CREDENTIALS=your_google_credentials_json

# Optional: Testing
USE_MOCK_APIS=false
```

## Authentication

### Getting Your HubSpot API Key

1. Log in to your HubSpot account
2. Navigate to Settings > Integrations > API Key
3. Click "Show" or "Generate" to get your API key
4. Copy the key to your `.env` file

### API Key Scopes

Ensure your API key has the following scopes:

- `crm.objects.contacts` - Contact management
- `crm.objects.deals` - Deal management
- `crm.objects.companies` - Company associations
- `marketing.email` - Email campaigns
- `analytics` - Analytics data
- `calendar` - Calendar sync

## Available Tools

### 1. HubSpotCreateContact

Create and update contacts in HubSpot CRM.

**Key Features:**
- Create single or batch contacts (up to 10)
- Custom property support
- Contact list assignments
- Update existing contacts
- Lifecycle stage management

**Use Cases:**
- Lead capture from forms
- CRM data enrichment
- Contact list building
- Customer onboarding

[Detailed Documentation](./hubspot_create_contact_README.md)

### 2. HubSpotTrackDeal

Manage deals and sales pipelines.

**Key Features:**
- Create and update deals
- Pipeline and stage management
- Deal associations (contacts, companies)
- Win/loss tracking
- Sales forecasting

**Use Cases:**
- Sales pipeline management
- Revenue forecasting
- Deal tracking
- Sales performance analysis

[Detailed Documentation](./hubspot_track_deal_README.md)

### 3. HubSpotSendEmail

Send marketing emails with templates and personalization.

**Key Features:**
- Template-based emails
- Custom HTML emails
- Personalization tokens
- Scheduling
- Tracking (opens, clicks)
- Batch sending

**Use Cases:**
- Email marketing campaigns
- Automated nurture sequences
- Event notifications
- Product announcements

[Detailed Documentation](./hubspot_send_email_README.md)

### 4. HubSpotGetAnalytics

Retrieve comprehensive CRM and marketing analytics.

**Key Features:**
- Contact metrics
- Deal pipeline analytics
- Email performance
- Conversion tracking
- Revenue reporting
- Custom reports

**Use Cases:**
- Dashboard reporting
- Performance monitoring
- ROI analysis
- Trend analysis

[Detailed Documentation](./hubspot_get_analytics_README.md)

### 5. HubSpotSyncCalendar

Sync HubSpot meetings with Google Calendar.

**Key Features:**
- Bidirectional sync
- Meeting CRUD operations
- Attendee management
- Automated scheduling
- Reminder notifications

**Use Cases:**
- Sales meeting management
- Calendar integration
- Meeting automation
- Schedule coordination

[Detailed Documentation](./hubspot_sync_calendar_README.md)

## Quick Start

### Basic Contact Creation

```python
from tools.integrations.hubspot import HubSpotCreateContact

# Create a contact
tool = HubSpotCreateContact(
    email="john.doe@example.com",
    firstname="John",
    lastname="Doe",
    company="Acme Corp",
    jobtitle="CEO",
    lifecyclestage="lead"
)

result = tool.run()
print(f"Contact created: {result['contact_id']}")
```

### Track a Deal

```python
from tools.integrations.hubspot import HubSpotTrackDeal

# Create a deal
tool = HubSpotTrackDeal(
    dealname="Acme Corp - Q1 Contract",
    amount=50000,
    dealstage="qualifiedtobuy",
    closedate="2024-03-31",
    contact_ids=["12345"]
)

result = tool.run()
print(f"Deal created: {result['deal_id']}")
print(f"Forecast category: {result['forecast_category']}")
```

### Send Marketing Email

```python
from tools.integrations.hubspot import HubSpotSendEmail

# Send email campaign
tool = HubSpotSendEmail(
    subject="Exclusive Offer - 20% Off!",
    body="<h1>Special Offer</h1><p>Get 20% off with code SAVE20</p>",
    list_ids=["111", "222"],
    from_email="marketing@company.com",
    track_opens=True,
    track_clicks=True
)

result = tool.run()
print(f"Email sent to {result['recipients_count']} recipients")
```

### Get Analytics

```python
from tools.integrations.hubspot import HubSpotGetAnalytics

# Get pipeline analytics
tool = HubSpotGetAnalytics(
    report_type="pipeline",
    time_period="this_month",
    group_by="stage"
)

result = tool.run()
print(f"Pipeline value: ${result['metrics']['total_pipeline_value']:,}")
print(f"Win rate: {result['metrics']['win_rate']:.1%}")
```

### Sync Calendar

```python
from tools.integrations.hubspot import HubSpotSyncCalendar

# Create meeting
tool = HubSpotSyncCalendar(
    operation="create_meeting",
    title="Sales Demo - Acme Corp",
    start_time="2024-03-15T14:00:00Z",
    end_time="2024-03-15T15:00:00Z",
    attendee_emails=["john@acme.com"],
    contact_ids=["12345"]
)

result = tool.run()
print(f"Meeting created: {result['meeting_id']}")
```

## Marketing Automation Workflows

### 1. Lead Capture to Nurture Workflow

Complete workflow from lead capture to email nurture:

```python
# Step 1: Capture lead from form submission
contact_tool = HubSpotCreateContact(
    email="newlead@example.com",
    firstname="New",
    lastname="Lead",
    lifecyclestage="subscriber",
    custom_properties={
        "lead_source": "Website Form",
        "interest": "Product Demo"
    },
    lists=["new_leads_list_id"]
)
contact_result = contact_tool.run()
contact_id = contact_result['contact_id']

# Step 2: Create welcome email campaign
email_tool = HubSpotSendEmail(
    template_id="welcome_template_123",
    contact_ids=[contact_id],
    from_email="welcome@company.com",
    personalization_tokens={
        "first_name": "New",
        "interest": "Product Demo"
    },
    track_opens=True
)
email_result = email_tool.run()

# Step 3: Create follow-up task/deal
deal_tool = HubSpotTrackDeal(
    dealname="New Lead - Product Demo",
    amount=0,  # Estimated value TBD
    dealstage="appointmentscheduled",
    contact_ids=[contact_id]
)
deal_result = deal_tool.run()

print(f"Workflow completed for contact {contact_id}")
```

### 2. Sales Pipeline Management Workflow

Track deals through sales pipeline with analytics:

```python
# Step 1: Create qualified deal
deal_tool = HubSpotTrackDeal(
    dealname="Enterprise Deal - BigCo",
    amount=100000,
    dealstage="qualifiedtobuy",
    dealtype="newbusiness",
    priority="high",
    contact_ids=["contact_123"],
    company_ids=["company_456"]
)
deal_result = deal_tool.run()
deal_id = deal_result['deal_id']

# Step 2: Move through stages
stages = [
    "presentationscheduled",
    "decisionmakerboughtin",
    "contractsent"
]

for stage in stages:
    # Update deal stage
    update_tool = HubSpotTrackDeal(
        deal_id=deal_id,
        move_to_stage=stage
    )
    update_tool.run()

    # Send stage-specific email
    email_tool = HubSpotSendEmail(
        template_id=f"{stage}_template",
        contact_ids=["contact_123"],
        from_email="sales@company.com"
    )
    email_tool.run()

# Step 3: Win the deal
win_tool = HubSpotTrackDeal(
    deal_id=deal_id,
    win_deal=True,
    amount=105000  # Final negotiated amount
)
win_result = win_tool.run()

# Step 4: Get updated analytics
analytics_tool = HubSpotGetAnalytics(
    report_type="pipeline",
    time_period="this_month"
)
analytics = analytics_tool.run()
print(f"Win rate: {analytics['metrics']['win_rate']:.1%}")
```

### 3. Email Campaign with Analytics Workflow

Send email campaign and track performance:

```python
# Step 1: Send campaign to segmented lists
campaign_tool = HubSpotSendEmail(
    subject="Q1 Product Launch - Early Access",
    body="""
    <h1>Be the First to Try Our New Product</h1>
    <p>Dear {{first_name}},</p>
    <p>As a valued customer, get early access to our Q1 launch.</p>
    <a href="{{cta_link}}">Get Early Access</a>
    """,
    list_ids=["vip_customers", "beta_testers"],
    from_email="product@company.com",
    campaign_id="q1_launch_campaign",
    track_opens=True,
    track_clicks=True
)
campaign_result = campaign_tool.run()

# Step 2: Wait for campaign to run (in production, use scheduling)
import time
time.sleep(3600)  # Wait 1 hour

# Step 3: Get email analytics
analytics_tool = HubSpotGetAnalytics(
    report_type="emails",
    time_period="today",
    email_campaign_id="q1_launch_campaign"
)
analytics = analytics_tool.run()

# Step 4: Identify engaged contacts (high opens/clicks)
# Create follow-up deal for engaged prospects
if analytics['metrics']['click_rate'] > 0.1:  # 10% click rate
    print(f"Strong engagement! Click rate: {analytics['metrics']['click_rate']:.1%}")
    # Create deals for clicked contacts (pseudo-code)
```

### 4. Meeting Scheduling Workflow

Automate meeting scheduling with calendar sync:

```python
# Step 1: Create contact and deal
contact_tool = HubSpotCreateContact(
    email="prospect@bigcompany.com",
    firstname="Jane",
    lastname="Smith",
    company="Big Company",
    lifecyclestage="salesqualifiedlead"
)
contact_result = contact_tool.run()

# Step 2: Schedule demo meeting
calendar_tool = HubSpotSyncCalendar(
    operation="create_meeting",
    title="Product Demo - Big Company",
    start_time="2024-03-20T14:00:00Z",
    end_time="2024-03-20T15:00:00Z",
    description="Initial product demo and Q&A",
    location="https://zoom.us/j/123456789",
    attendee_emails=["prospect@bigcompany.com"],
    contact_ids=[contact_result['contact_id']],
    meeting_type="demo",
    send_notifications=True,
    reminder_minutes=15
)
meeting_result = calendar_tool.run()

# Step 3: Send pre-meeting email
email_tool = HubSpotSendEmail(
    template_id="pre_demo_template",
    contact_ids=[contact_result['contact_id']],
    from_email="demos@company.com",
    personalization_tokens={
        "meeting_date": "March 20, 2024",
        "meeting_link": "https://zoom.us/j/123456789"
    }
)
email_tool.run()

# Step 4: After meeting, update outcome
# (In production, trigger this after meeting ends)
update_tool = HubSpotSyncCalendar(
    operation="update_meeting",
    meeting_id=meeting_result['meeting_id'],
    outcome="completed",
    description="Demo completed. Next steps: proposal"
)
update_tool.run()
```

## Bulk Operations

### Batch Contact Import

Import multiple contacts efficiently:

```python
from tools.integrations.hubspot import HubSpotCreateContact

# Prepare batch of contacts
contacts = [
    {
        "email": "user1@example.com",
        "firstname": "User",
        "lastname": "One",
        "company": "Company A",
        "lifecyclestage": "lead"
    },
    {
        "email": "user2@example.com",
        "firstname": "User",
        "lastname": "Two",
        "company": "Company B",
        "lifecyclestage": "subscriber"
    },
    # ... up to 10 contacts per batch
]

# Create batch
tool = HubSpotCreateContact(batch_contacts=contacts)
result = tool.run()

print(f"Created {result['contacts_created']} contacts")
print(f"Contact IDs: {result['contact_ids']}")
```

### Batch Deal Creation

Create multiple deals at once:

```python
from tools.integrations.hubspot import HubSpotTrackDeal

deals = [
    {
        "dealname": "Deal 1",
        "amount": 10000,
        "dealstage": "qualifiedtobuy",
        "dealtype": "newbusiness"
    },
    {
        "dealname": "Deal 2",
        "amount": 25000,
        "dealstage": "appointmentscheduled",
        "dealtype": "existingbusiness"
    },
    # ... up to 10 deals per batch
]

tool = HubSpotTrackDeal(batch_deals=deals)
result = tool.run()

print(f"Created {result['deals_created']} deals")
```

### Batch Email Sending

Send multiple email campaigns:

```python
from tools.integrations.hubspot import HubSpotSendEmail

emails = [
    {
        "template_id": "welcome_template",
        "contact_ids": ["123", "456"],
        "from_email": "welcome@company.com"
    },
    {
        "subject": "Newsletter",
        "body": "<p>Newsletter content</p>",
        "list_ids": ["789"],
        "from_email": "news@company.com"
    },
    # ... up to 10 emails per batch
]

tool = HubSpotSendEmail(batch_emails=emails)
result = tool.run()

print(f"Sent {result['emails_sent']} emails")
print(f"Total recipients: {result['total_recipients']}")
```

## Rate Limits

HubSpot API rate limits:

- **Free/Starter**: 100 requests per 10 seconds
- **Professional**: 150 requests per 10 seconds
- **Enterprise**: 200 requests per 10 seconds

### Rate Limit Handling

The tools automatically handle rate limits:

```python
# Tools will automatically retry with exponential backoff
tool = HubSpotCreateContact(
    email="test@example.com",
    firstname="Test"
)

try:
    result = tool.run()
except APIError as e:
    if "rate limit" in str(e).lower():
        print("Rate limit exceeded. Try again in a few seconds.")
```

### Best Practices for Rate Limits

1. **Use Batch Operations**: Reduce API calls by batching up to 10 records
2. **Implement Delays**: Add small delays between large operations
3. **Monitor Usage**: Track your API usage in HubSpot settings
4. **Cache Results**: Cache analytics data to reduce repeated calls

```python
import time

# Process large contact list in batches
all_contacts = [...]  # Large list
batch_size = 10

for i in range(0, len(all_contacts), batch_size):
    batch = all_contacts[i:i+batch_size]

    tool = HubSpotCreateContact(batch_contacts=batch)
    result = tool.run()

    # Small delay between batches
    if i + batch_size < len(all_contacts):
        time.sleep(0.5)
```

## Error Handling

### Common Errors and Solutions

#### Authentication Error

```python
from shared.errors import AuthenticationError

try:
    tool = HubSpotCreateContact(
        email="test@example.com",
        firstname="Test"
    )
    result = tool.run()
except AuthenticationError as e:
    print("Invalid API key. Check HUBSPOT_API_KEY environment variable.")
```

#### Validation Error

```python
from shared.errors import ValidationError

try:
    tool = HubSpotCreateContact(
        # Missing required email
        firstname="Test"
    )
    result = tool.run()
except ValidationError as e:
    print(f"Validation error: {e.message}")
```

#### API Error

```python
from shared.errors import APIError

try:
    tool = HubSpotTrackDeal(
        deal_id="invalid_id",
        move_to_stage="new_stage"
    )
    result = tool.run()
except APIError as e:
    if e.error_code == "RESOURCE_NOT_FOUND":
        print("Deal not found")
```

### Error Response Format

All errors return a structured response:

```python
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "email is required for single contact creation",
        "tool": "hubspot_create_contact",
        "retry_after": None,
        "details": {},
        "request_id": "uuid-here"
    }
}
```

## Best Practices

### 1. Data Validation

Always validate data before sending to HubSpot:

```python
def validate_email(email):
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# Validate before creating contact
email = "user@example.com"
if validate_email(email):
    tool = HubSpotCreateContact(
        email=email,
        firstname="User"
    )
    result = tool.run()
```

### 2. Use Custom Properties Strategically

```python
# Good: Specific, actionable custom properties
tool = HubSpotCreateContact(
    email="user@example.com",
    firstname="User",
    custom_properties={
        "lead_score": "85",
        "industry": "SaaS",
        "company_size": "50-100",
        "product_interest": "Enterprise Plan"
    }
)
```

### 3. Implement Retry Logic

```python
import time

def create_contact_with_retry(email, max_retries=3):
    for attempt in range(max_retries):
        try:
            tool = HubSpotCreateContact(
                email=email,
                firstname="User"
            )
            return tool.run()
        except APIError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

### 4. Monitor Analytics Regularly

```python
# Daily analytics check
def daily_analytics_check():
    # Check pipeline health
    pipeline_tool = HubSpotGetAnalytics(
        report_type="pipeline",
        time_period="this_month"
    )
    pipeline = pipeline_tool.run()

    # Check email performance
    email_tool = HubSpotGetAnalytics(
        report_type="emails",
        time_period="yesterday"
    )
    emails = email_tool.run()

    # Alert if metrics drop
    if emails['metrics']['open_rate'] < 0.15:
        print("⚠️ Email open rate below 15%")

    if pipeline['metrics']['win_rate'] < 0.30:
        print("⚠️ Win rate below 30%")
```

### 5. Clean Data Management

```python
# Update existing contacts instead of creating duplicates
tool = HubSpotCreateContact(
    email="existing@example.com",
    firstname="Updated",
    lastname="Name",
    update_if_exists=True  # Important!
)
result = tool.run()

if result['status'] == 'updated':
    print("Contact updated successfully")
elif result['status'] == 'created':
    print("New contact created")
```

## Examples

### Complete CRM Workflow Example

Full example combining all tools:

```python
from tools.integrations.hubspot import (
    HubSpotCreateContact,
    HubSpotTrackDeal,
    HubSpotSendEmail,
    HubSpotGetAnalytics,
    HubSpotSyncCalendar
)

# 1. Create/update contact
print("Creating contact...")
contact_tool = HubSpotCreateContact(
    email="bigcustomer@acme.com",
    firstname="John",
    lastname="Doe",
    company="Acme Corp",
    jobtitle="VP Sales",
    phone="+1-555-1234",
    lifecyclestage="salesqualifiedlead",
    custom_properties={
        "industry": "Technology",
        "company_size": "200-500",
        "lead_score": "90"
    }
)
contact_result = contact_tool.run()
contact_id = contact_result['contact_id']
print(f"✓ Contact created: {contact_id}")

# 2. Create deal
print("\nCreating deal...")
deal_tool = HubSpotTrackDeal(
    dealname="Acme Corp - Enterprise Plan",
    amount=75000,
    dealstage="qualifiedtobuy",
    closedate="2024-06-30",
    dealtype="newbusiness",
    priority="high",
    contact_ids=[contact_id],
    custom_properties={
        "contract_length": "24 months",
        "mrr": "3125"
    }
)
deal_result = deal_tool.run()
deal_id = deal_result['deal_id']
print(f"✓ Deal created: {deal_id}")
print(f"  Forecast: {deal_result['forecast_category']}")

# 3. Schedule demo meeting
print("\nScheduling meeting...")
meeting_tool = HubSpotSyncCalendar(
    operation="create_meeting",
    title="Enterprise Demo - Acme Corp",
    start_time="2024-03-25T14:00:00Z",
    end_time="2024-03-25T15:30:00Z",
    description="Product demo and technical Q&A",
    location="https://zoom.us/j/123456789",
    attendee_emails=["bigcustomer@acme.com"],
    contact_ids=[contact_id],
    meeting_type="demo",
    send_notifications=True,
    reminder_minutes=30
)
meeting_result = meeting_tool.run()
print(f"✓ Meeting scheduled: {meeting_result['meeting_id']}")

# 4. Send welcome email
print("\nSending email...")
email_tool = HubSpotSendEmail(
    template_id="enterprise_welcome_template",
    contact_ids=[contact_id],
    from_email="sales@yourcompany.com",
    from_name="Sales Team",
    personalization_tokens={
        "first_name": "John",
        "company": "Acme Corp",
        "demo_date": "March 25, 2024"
    },
    track_opens=True,
    track_clicks=True
)
email_result = email_tool.run()
print(f"✓ Email sent: {email_result['email_id']}")

# 5. Get current analytics
print("\nFetching analytics...")
analytics_tool = HubSpotGetAnalytics(
    report_type="pipeline",
    time_period="this_month"
)
analytics = analytics_tool.run()
print(f"✓ Pipeline value: ${analytics['metrics']['total_pipeline_value']:,}")
print(f"  Win rate: {analytics['metrics']['win_rate']:.1%}")

print("\n🎉 Workflow complete!")
```

### Testing Mode Example

Test your integration without making real API calls:

```python
import os

# Enable mock mode
os.environ["USE_MOCK_APIS"] = "true"

# All tools will now return realistic mock data
tool = HubSpotCreateContact(
    email="test@example.com",
    firstname="Test",
    lastname="User"
)

result = tool.run()
print(f"Mock result: {result}")
# Output includes mock_mode: true in metadata
```

## Support

For issues or questions:

- HubSpot API Documentation: https://developers.hubspot.com/docs/api/overview
- GitHub Issues: [Link to your repo]
- HubSpot Community: https://community.hubspot.com/

## License

Part of the AgentSwarm Tools Framework.
"""
