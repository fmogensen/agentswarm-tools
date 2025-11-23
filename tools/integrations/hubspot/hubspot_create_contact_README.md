# HubSpot Create Contact Tool

Complete documentation for the HubSpotCreateContact tool - create and manage contacts in HubSpot CRM with custom properties, list management, and bulk operations.

## Table of Contents

- [Overview](#overview)
- [Parameters](#parameters)
- [Returns](#returns)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Error Handling](#error-handling)

## Overview

The HubSpotCreateContact tool provides comprehensive contact management capabilities including:

- Single and batch contact creation (up to 10 per batch)
- Custom property support for any HubSpot field
- Contact list assignments
- Automatic update if contact exists
- Lifecycle stage management
- Email validation

### Use Cases

- **Lead Capture**: Capture leads from web forms, landing pages, chatbots
- **CRM Import**: Bulk import contacts from external systems
- **Data Enrichment**: Add custom properties and update existing contacts
- **List Building**: Build targeted contact lists for marketing campaigns
- **Customer Onboarding**: Create customer records with onboarding data

## Parameters

### Required Parameters

#### Single Contact Mode

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `email` | str | Contact's email address (primary identifier) | Valid email format, required in single mode |

#### Batch Mode

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `batch_contacts` | List[Dict] | List of contact dictionaries | Max 10 contacts, each must have email |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `firstname` | str | None | Contact's first name (max 100 chars) |
| `lastname` | str | None | Contact's last name (max 100 chars) |
| `phone` | str | None | Contact's phone number (max 50 chars) |
| `company` | str | None | Company name (max 200 chars) |
| `website` | str | None | Website URL (max 500 chars) |
| `jobtitle` | str | None | Job title (max 100 chars) |
| `lifecyclestage` | str | None | Lifecycle stage (see valid values below) |
| `custom_properties` | Dict | None | Custom property key-value pairs |
| `lists` | List[str] | None | Contact list IDs to add contact to |
| `update_if_exists` | bool | True | Update contact if email exists |

### Lifecycle Stages

Valid `lifecyclestage` values:
- `subscriber` - Newsletter/blog subscriber
- `lead` - Identified lead
- `marketingqualifiedlead` - MQL (marketing qualified)
- `salesqualifiedlead` - SQL (sales qualified)
- `opportunity` - Active opportunity
- `customer` - Paying customer
- `evangelist` - Brand advocate
- `other` - Other status

## Returns

### Success Response

```python
{
    "success": True,
    "contact_id": "12345",              # HubSpot contact VID
    "email": "john@example.com",
    "status": "created",                 # or "updated"
    "properties": {                      # All properties set
        "email": "john@example.com",
        "firstname": "John",
        "lastname": "Doe",
        ...
    },
    "lists_added": ["123", "456"],      # List IDs contact was added to
    "metadata": {
        "tool_name": "hubspot_create_contact",
        "update_if_exists": True
    }
}
```

### Batch Response

```python
{
    "success": True,
    "status": "batch_processed",
    "contact_ids": ["123", "456", "789"],
    "contacts_created": 3,
    "contacts_updated": 0,
    "metadata": {
        "tool_name": "hubspot_create_contact",
        "batch_size": 3
    }
}
```

## Examples

### Basic Contact Creation

```python
from tools.integrations.hubspot import HubSpotCreateContact

tool = HubSpotCreateContact(
    email="john.doe@acme.com",
    firstname="John",
    lastname="Doe",
    company="Acme Corp"
)
result = tool.run()

print(f"Created contact: {result['contact_id']}")
```

### Complete Contact with Custom Properties

```python
tool = HubSpotCreateContact(
    email="jane.smith@tech.com",
    firstname="Jane",
    lastname="Smith",
    company="TechCorp Inc",
    jobtitle="VP of Sales",
    phone="+1-555-0123",
    website="https://techcorp.com",
    lifecyclestage="salesqualifiedlead",
    custom_properties={
        "industry": "Technology",
        "employee_count": "500-1000",
        "annual_revenue": "10000000",
        "lead_source": "Trade Show",
        "lead_score": "85",
        "preferred_contact_method": "email"
    },
    lists=["hot_leads_list", "tech_industry_list"]
)
result = tool.run()

if result['status'] == 'created':
    print(f"New contact created: {result['contact_id']}")
elif result['status'] == 'updated':
    print(f"Existing contact updated: {result['contact_id']}")

print(f"Added to {len(result['lists_added'])} lists")
```

### Batch Contact Creation

```python
# Prepare batch of contacts
contacts = [
    {
        "email": "alice@company-a.com",
        "firstname": "Alice",
        "lastname": "Anderson",
        "company": "Company A",
        "lifecyclestage": "lead"
    },
    {
        "email": "bob@company-b.com",
        "firstname": "Bob",
        "lastname": "Brown",
        "company": "Company B",
        "lifecyclestage": "subscriber",
        "custom_properties": {
            "industry": "Finance"
        }
    },
    {
        "email": "carol@company-c.com",
        "firstname": "Carol",
        "lastname": "Chen",
        "company": "Company C",
        "phone": "+1-555-9999"
    }
]

tool = HubSpotCreateContact(batch_contacts=contacts)
result = tool.run()

print(f"Batch complete!")
print(f"Contacts created: {result['contacts_created']}")
print(f"Contact IDs: {result['contact_ids']}")
```

### Update Existing Contact

```python
# Update contact with new information
tool = HubSpotCreateContact(
    email="existing@customer.com",
    firstname="Updated",
    lastname="Name",
    lifecyclestage="customer",  # Promote to customer
    custom_properties={
        "customer_since": "2024-01-15",
        "plan_type": "Enterprise"
    },
    update_if_exists=True  # This is default behavior
)
result = tool.run()

if result['status'] == 'updated':
    print("Contact successfully updated")
```

## Best Practices

### 1. Email Validation

Always validate emails before creating contacts:

```python
import re

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

email = "user@example.com"
if is_valid_email(email):
    tool = HubSpotCreateContact(email=email, firstname="User")
    result = tool.run()
else:
    print("Invalid email format")
```

### 2. Use Batch Operations for Bulk Imports

```python
# Process large list in batches of 10
all_contacts = [...]  # Your contact list
batch_size = 10

for i in range(0, len(all_contacts), batch_size):
    batch = all_contacts[i:i+batch_size]

    tool = HubSpotCreateContact(batch_contacts=batch)
    result = tool.run()

    print(f"Batch {i//batch_size + 1}: {result['contacts_created']} contacts")
```

### 3. Standardize Custom Properties

```python
# Define standard custom properties
STANDARD_PROPERTIES = {
    "lead_source": ["Website", "Referral", "Trade Show", "Social Media"],
    "industry": ["Technology", "Finance", "Healthcare", "Retail"],
    "company_size": ["1-10", "11-50", "51-200", "201-500", "500+"]
}

def create_lead(email, firstname, lastname, lead_source, industry):
    tool = HubSpotCreateContact(
        email=email,
        firstname=firstname,
        lastname=lastname,
        custom_properties={
            "lead_source": lead_source,
            "industry": industry,
            "created_date": datetime.now().isoformat()
        }
    )
    return tool.run()
```

### 4. Error Handling

```python
from shared.errors import ValidationError, APIError

def safe_create_contact(email, **kwargs):
    try:
        tool = HubSpotCreateContact(email=email, **kwargs)
        result = tool.run()
        return result
    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return None
    except APIError as e:
        print(f"API error: {e.message}")
        return None
```

### 5. Progressive Enrichment

```python
# Create minimal contact first
tool = HubSpotCreateContact(
    email="new@lead.com",
    firstname="New",
    lifecyclestage="subscriber"
)
result = tool.run()
contact_id = result['contact_id']

# Later, enrich with more data
tool = HubSpotCreateContact(
    email="new@lead.com",
    lastname="Lead",
    company="Lead Company",
    custom_properties={
        "enriched_date": datetime.now().isoformat(),
        "data_source": "Email Interaction"
    },
    update_if_exists=True
)
enriched_result = tool.run()
```

## Error Handling

### Common Errors

#### Missing Email Error
```python
# Error: email is required for single contact creation
tool = HubSpotCreateContact(firstname="John", lastname="Doe")
result = tool.run()
# Returns: {"success": False, "error": {"code": "VALIDATION_ERROR", ...}}
```

#### Invalid Lifecycle Stage
```python
# Error: Invalid lifecycle stage
tool = HubSpotCreateContact(
    email="test@example.com",
    lifecyclestage="invalid_stage"
)
# Raises ValidationError
```

#### Batch Too Large
```python
# Error: Cannot exceed 10 contacts per batch
contacts = [{"email": f"user{i}@example.com"} for i in range(11)]
tool = HubSpotCreateContact(batch_contacts=contacts)
# Raises ValidationError
```

### Error Response Format

```python
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Detailed error message",
        "tool": "hubspot_create_contact",
        "retry_after": None,
        "details": {},
        "request_id": "uuid"
    }
}
```

## Advanced Usage

### Contact Deduplication

```python
def create_or_update_contact(email, **properties):
    """Create contact or update if exists."""
    tool = HubSpotCreateContact(
        email=email,
        update_if_exists=True,
        **properties
    )
    result = tool.run()

    if result['status'] == 'created':
        print(f"New contact: {email}")
    else:
        print(f"Updated contact: {email}")

    return result['contact_id']
```

### Lead Scoring Integration

```python
def calculate_lead_score(properties):
    """Calculate lead score based on properties."""
    score = 0

    if properties.get('jobtitle') and 'VP' in properties['jobtitle']:
        score += 20
    if properties.get('company_size') in ['201-500', '500+']:
        score += 15
    if properties.get('industry') == 'Technology':
        score += 10

    return str(score)

# Create contact with calculated score
tool = HubSpotCreateContact(
    email="qualified@lead.com",
    firstname="Qualified",
    jobtitle="VP Sales",
    custom_properties={
        "company_size": "500+",
        "industry": "Technology",
        "lead_score": calculate_lead_score({
            "jobtitle": "VP Sales",
            "company_size": "500+",
            "industry": "Technology"
        })
    }
)
result = tool.run()
```

## Related Tools

- **HubSpotTrackDeal**: Create deals associated with contacts
- **HubSpotSendEmail**: Send emails to contacts
- **HubSpotGetAnalytics**: Analyze contact metrics
- **HubSpotSyncCalendar**: Schedule meetings with contacts

## API Reference

For complete HubSpot Contacts API documentation:
https://developers.hubspot.com/docs/api/crm/contacts
