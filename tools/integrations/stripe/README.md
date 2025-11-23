```markdown
# Stripe Integration Tools for AgentSwarm

Complete Stripe payment processing integration for the AgentSwarm Tools Framework. This package provides 5 production-ready tools for managing payments, subscriptions, customers, invoices, and webhook events.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Tools](#tools)
  - [StripeCreatePayment](#1-stripecreatepaym ent)
  - [StripeCreateSubscription](#2-stripecreatesubscription)
  - [StripeListCustomers](#3-stripelistcustomers)
  - [StripeGetInvoices](#4-stripegetinvoices)
  - [StripeHandleWebhooks](#5-stripehandlewebhooks)
- [Common Use Cases](#common-use-cases)
- [Webhook Setup](#webhook-setup)
- [Security Best Practices](#security-best-practices)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [API Reference](#api-reference)

## Overview

The Stripe integration provides comprehensive payment processing capabilities:

- **One-time Payments**: Create payment intents with automatic confirmation
- **Recurring Subscriptions**: Manage subscription billing with trials and multiple plans
- **Customer Management**: Search, filter, and list customer records
- **Invoice Retrieval**: Access invoices with advanced filtering
- **Webhook Processing**: Securely handle Stripe webhook events

### Features

- Full Stripe Payment Intent API support
- Subscription management with trial periods
- Customer search and metadata filtering
- Invoice status tracking and date filtering
- Webhook signature verification (HMAC-SHA256)
- Comprehensive error handling
- Mock mode for testing
- 90%+ test coverage

## Installation

### Prerequisites

- Python 3.8+
- AgentSwarm Tools Framework
- Stripe account (test or live mode)

### Install Dependencies

```bash
pip install stripe
```

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required for payment/subscription/customer/invoice operations
STRIPE_API_KEY=sk_test_your_secret_key_here

# Required for webhook verification
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Optional: Enable mock mode for testing
USE_MOCK_APIS=false
```

**IMPORTANT**: Never commit your `.env` file or hardcode API keys in source code.

## Quick Start

### 1. Create a One-Time Payment

```python
from tools.integrations.stripe import StripeCreatePayment

# Create a $20 payment
tool = StripeCreatePayment(
    amount=2000,  # Amount in cents
    currency="usd",
    customer_email="customer@example.com",
    description="Product purchase",
    confirm=False  # Set to True for automatic confirmation
)

result = tool.run()

if result["success"]:
    print(f"Payment Intent ID: {result['payment_intent_id']}")
    print(f"Client Secret: {result['client_secret']}")
    print(f"Status: {result['status']}")
```

### 2. Create a Subscription

```python
from tools.integrations.stripe import StripeCreateSubscription

# Create monthly subscription with 14-day trial
tool = StripeCreateSubscription(
    customer_id="cus_1234567890",  # Or use email to create customer
    price_id="price_monthly_premium",
    trial_period_days=14,
    billing_interval="monthly"
)

result = tool.run()

if result["success"]:
    print(f"Subscription ID: {result['subscription_id']}")
    print(f"Status: {result['status']}")
    print(f"Trial ends: {result['trial_end']}")
```

### 3. List Customers

```python
from tools.integrations.stripe import StripeListCustomers

# Search customers by email
tool = StripeListCustomers(
    email="customer@example.com",
    limit=10
)

result = tool.run()

if result["success"]:
    print(f"Found {result['count']} customers")
    for customer in result["customers"]:
        print(f"  {customer['email']} - {customer['id']}")
```

### 4. Get Invoices

```python
from tools.integrations.stripe import StripeGetInvoices

# Get paid invoices for a customer
tool = StripeGetInvoices(
    customer_id="cus_1234567890",
    status="paid",
    limit=10
)

result = tool.run()

if result["success"]:
    print(f"Found {result['count']} paid invoices")
    for invoice in result["invoices"]:
        print(f"  {invoice['number']}: ${invoice['amount_due']/100:.2f}")
```

### 5. Handle Webhooks

```python
from tools.integrations.stripe import StripeHandleWebhooks

# In your webhook endpoint (Flask example)
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    tool = StripeHandleWebhooks(
        payload=payload.decode('utf-8'),
        signature_header=sig_header,
        event_types=['payment_intent.succeeded', 'customer.created']
    )

    result = tool.run()

    if result["success"]:
        event_type = result["event_type"]

        if event_type == "payment_intent.succeeded":
            payment = result["event_data"]
            # Process successful payment
            print(f"Payment {payment['id']} succeeded!")

        elif event_type == "customer.created":
            customer = result["event_data"]
            # Handle new customer
            print(f"New customer: {customer['email']}")

    return jsonify({"status": "success"}), 200
```

## Authentication

All tools require proper authentication:

### API Key (Required for Payments, Subscriptions, Customers, Invoices)

Set the `STRIPE_API_KEY` environment variable:

```bash
# Test mode (recommended for development)
export STRIPE_API_KEY=sk_test_51...

# Live mode (production only)
export STRIPE_API_KEY=sk_live_51...
```

**Get your API key from**: [Stripe Dashboard → Developers → API Keys](https://dashboard.stripe.com/apikeys)

### Webhook Secret (Required for Webhook Verification)

Set the `STRIPE_WEBHOOK_SECRET` environment variable:

```bash
export STRIPE_WEBHOOK_SECRET=whsec_...
```

**Get your webhook secret from**: [Stripe Dashboard → Developers → Webhooks](https://dashboard.stripe.com/webhooks)

## Tools

### 1. StripeCreatePayment

Creates one-time payments using Stripe's Payment Intent API.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `amount` | int | Yes | Payment amount in smallest currency unit (cents for USD) |
| `currency` | str | Yes | Three-letter ISO currency code (e.g., 'usd', 'eur') |
| `customer_email` | str | Yes | Customer's email address |
| `description` | str | No | Payment description (max 1000 chars) |
| `payment_method_types` | list | No | Payment method types (default: ['card']) |
| `confirm` | bool | No | Auto-confirm payment (default: False) |
| `metadata` | dict | No | Additional metadata key-value pairs |

#### Returns

```python
{
    "success": True,
    "payment_intent_id": "pi_1234567890abcdef",
    "client_secret": "pi_1234567890abcdef_secret_...",
    "status": "requires_payment_method",  # or "succeeded" if confirmed
    "amount": 2000,
    "currency": "usd",
    "metadata": {...}
}
```

#### Example

```python
tool = StripeCreatePayment(
    amount=5000,  # $50.00
    currency="usd",
    customer_email="premium@example.com",
    description="Premium subscription - Annual",
    confirm=True,
    metadata={"plan": "premium", "period": "yearly"}
)

result = tool.run()
```

[Full Documentation](./stripe_create_payment_README.md)

### 2. StripeCreateSubscription

Creates recurring subscriptions with support for trials and multiple billing intervals.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | str | Yes | Stripe customer ID or email to create customer |
| `price_id` | str | Yes | Stripe price ID for subscription |
| `payment_method_id` | str | No | Payment method ID |
| `trial_period_days` | int | No | Trial period in days (0-730, default: 0) |
| `billing_interval` | str | No | Billing interval: monthly, yearly, weekly (default: monthly) |
| `quantity` | int | No | Subscription quantity (1-100, default: 1) |
| `metadata` | dict | No | Additional metadata |

#### Returns

```python
{
    "success": True,
    "subscription_id": "sub_1234567890abcdef",
    "customer_id": "cus_1234567890",
    "status": "active",  # or "trialing" if trial_period_days > 0
    "current_period_end": 1234567890,
    "trial_end": 1234567890,  # or None
    "metadata": {...}
}
```

#### Example

```python
tool = StripeCreateSubscription(
    customer_id="newuser@example.com",  # Creates customer automatically
    price_id="price_monthly_pro",
    trial_period_days=30,
    billing_interval="monthly",
    metadata={"source": "website", "campaign": "summer2024"}
)

result = tool.run()
```

[Full Documentation](./stripe_create_subscription_README.md)

### 3. StripeListCustomers

Lists and searches customers with advanced filtering.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `email` | str | No | Filter by customer email |
| `limit` | int | No | Max customers to return (1-100, default: 10) |
| `starting_after` | str | No | Customer ID to start pagination after |
| `ending_before` | str | No | Customer ID to end pagination before |
| `created_after` | int | No | Unix timestamp - customers created after |
| `created_before` | int | No | Unix timestamp - customers created before |
| `metadata_filters` | dict | No | Metadata key-value pairs to filter by |
| `include_deleted` | bool | No | Include deleted customers (default: False) |

#### Returns

```python
{
    "success": True,
    "customers": [
        {
            "id": "cus_1234567890",
            "email": "customer@example.com",
            "name": "John Doe",
            "created": 1234567890,
            "metadata": {...}
        }
    ],
    "has_more": False,
    "count": 3,
    "metadata": {...}
}
```

#### Example

```python
import time

# Find customers created in the last 7 days
week_ago = int(time.time()) - (86400 * 7)

tool = StripeListCustomers(
    created_after=week_ago,
    metadata_filters={"plan": "premium"},
    limit=50
)

result = tool.run()
```

[Full Documentation](./stripe_list_customers_README.md)

### 4. StripeGetInvoices

Retrieves invoices with status and date filtering.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `customer_id` | str | No | Filter by customer ID |
| `status` | str | No | Filter by status: draft, open, paid, void, uncollectible |
| `subscription_id` | str | No | Filter by subscription ID |
| `limit` | int | No | Max invoices to return (1-100, default: 10) |
| `starting_after` | str | No | Invoice ID to start pagination after |
| `ending_before` | str | No | Invoice ID to end pagination before |
| `created_after` | int | No | Unix timestamp - invoices created after |
| `created_before` | int | No | Unix timestamp - invoices created before |
| `due_date_after` | int | No | Unix timestamp - invoices due after |
| `due_date_before` | int | No | Unix timestamp - invoices due before |
| `include_total_count` | bool | No | Include total count (slower, default: False) |

#### Returns

```python
{
    "success": True,
    "invoices": [
        {
            "id": "in_1234567890",
            "customer": "cus_1234567890",
            "number": "INV-1234",
            "status": "paid",
            "amount_due": 2000,
            "invoice_pdf": "https://..."
        }
    ],
    "has_more": False,
    "count": 5,
    "total_count": 5,  # if include_total_count=True
    "metadata": {...}
}
```

#### Example

```python
# Get all unpaid invoices for a customer
tool = StripeGetInvoices(
    customer_id="cus_1234567890",
    status="open",
    limit=20
)

result = tool.run()

# Calculate total outstanding
total_due = sum(inv["amount_due"] for inv in result["invoices"])
print(f"Total outstanding: ${total_due/100:.2f}")
```

[Full Documentation](./stripe_get_invoices_README.md)

### 5. StripeHandleWebhooks

Securely validates and processes Stripe webhook events.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `payload` | str | Yes | Raw webhook payload (JSON string) |
| `signature_header` | str | Yes | Stripe-Signature header from request |
| `webhook_secret` | str | No | Webhook signing secret (uses env var if not provided) |
| `event_types` | list | No | Whitelist of event types to process |
| `skip_signature_validation` | bool | No | Skip validation (TESTING ONLY) |
| `tolerance` | int | No | Timestamp tolerance in seconds (default: 300) |

#### Returns

```python
{
    "success": True,
    "event_id": "evt_1234567890",
    "event_type": "payment_intent.succeeded",
    "event_data": {
        "id": "pi_1234567890",
        "amount": 2000,
        "status": "succeeded"
    },
    "created": 1234567890,
    "livemode": False,
    "metadata": {...}
}
```

#### Supported Event Types

```python
from tools.integrations.stripe import STRIPE_EVENT_TYPES

# Common events:
# - payment_intent.succeeded
# - payment_intent.payment_failed
# - customer.created
# - customer.updated
# - customer.subscription.created
# - customer.subscription.deleted
# - invoice.paid
# - invoice.payment_failed
# - charge.succeeded
# - charge.refunded
# ... and 20+ more
```

#### Example

```python
# Django webhook handler
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stripe_webhook(request):
    payload = request.body.decode('utf-8')
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    tool = StripeHandleWebhooks(
        payload=payload,
        signature_header=sig_header,
        event_types=[
            'payment_intent.succeeded',
            'customer.subscription.deleted',
            'invoice.payment_failed'
        ]
    )

    try:
        result = tool.run()

        if result["success"]:
            event_type = result["event_type"]
            event_data = result["event_data"]

            # Route to appropriate handler
            if event_type == "payment_intent.succeeded":
                handle_successful_payment(event_data)
            elif event_type == "customer.subscription.deleted":
                handle_cancelled_subscription(event_data)
            elif event_type == "invoice.payment_failed":
                handle_failed_payment(event_data)

        return HttpResponse(status=200)

    except SecurityError as e:
        logger.error(f"Webhook signature validation failed: {e}")
        return HttpResponse(status=400)
```

[Full Documentation](./stripe_handle_webhooks_README.md)

## Common Use Cases

### Use Case 1: Complete Payment Flow

```python
from tools.integrations.stripe import StripeCreatePayment, StripeListCustomers

# 1. Check if customer exists
customer_search = StripeListCustomers(
    email="customer@example.com",
    limit=1
)
customer_result = customer_search.run()

# 2. Create payment
payment = StripeCreatePayment(
    amount=9900,  # $99.00
    currency="usd",
    customer_email="customer@example.com",
    description="Annual Pro Plan",
    metadata={"plan": "pro", "period": "yearly"}
)
payment_result = payment.run()

if payment_result["success"]:
    # 3. Return client secret to frontend for confirmation
    return {
        "client_secret": payment_result["client_secret"],
        "payment_intent_id": payment_result["payment_intent_id"]
    }
```

### Use Case 2: Subscription Management

```python
from tools.integrations.stripe import (
    StripeCreateSubscription,
    StripeGetInvoices,
    StripeListCustomers
)

# 1. Create subscription with trial
subscription = StripeCreateSubscription(
    customer_id="newuser@startup.com",  # Auto-creates customer
    price_id="price_startup_monthly",
    trial_period_days=14,
    metadata={"signup_source": "landing_page"}
)
sub_result = subscription.run()

# 2. Monitor invoices during trial
invoices = StripeGetInvoices(
    customer_id=sub_result["customer_id"],
    subscription_id=sub_result["subscription_id"],
    status="draft",
    limit=10
)
invoice_result = invoices.run()

print(f"Subscription created: {sub_result['subscription_id']}")
print(f"Trial ends: {sub_result['trial_end']}")
print(f"Upcoming invoices: {invoice_result['count']}")
```

### Use Case 3: Customer Reporting

```python
from tools.integrations.stripe import StripeListCustomers, StripeGetInvoices
import time

# Get all premium customers from last month
month_ago = int(time.time()) - (86400 * 30)

customers = StripeListCustomers(
    created_after=month_ago,
    metadata_filters={"tier": "premium"},
    limit=100
)
customer_result = customers.run()

# Get revenue from each customer
total_revenue = 0
for customer in customer_result["customers"]:
    invoices = StripeGetInvoices(
        customer_id=customer["id"],
        status="paid",
        created_after=month_ago,
        limit=100
    )
    invoice_result = invoices.run()

    customer_revenue = sum(inv["amount_paid"] for inv in invoice_result["invoices"])
    total_revenue += customer_revenue

    print(f"{customer['email']}: ${customer_revenue/100:.2f}")

print(f"\nTotal monthly revenue: ${total_revenue/100:.2f}")
```

## Webhook Setup

### Step 1: Create Webhook Endpoint

Create an endpoint in your application to receive webhook events:

```python
# Flask example
from flask import Flask, request, jsonify
from tools.integrations.stripe import StripeHandleWebhooks

app = Flask(__name__)

@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data.decode('utf-8')
    sig_header = request.headers.get('Stripe-Signature')

    tool = StripeHandleWebhooks(
        payload=payload,
        signature_header=sig_header
    )

    result = tool.run()

    if result["success"]:
        # Process event
        process_stripe_event(result["event_type"], result["event_data"])

    return jsonify({"status": "success"}), 200
```

### Step 2: Register Webhook in Stripe Dashboard

1. Go to [Stripe Dashboard → Developers → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter your endpoint URL: `https://yourdomain.com/stripe/webhook`
4. Select events to listen for:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
5. Click "Add endpoint"
6. Copy the "Signing secret" (starts with `whsec_`)

### Step 3: Set Webhook Secret

```bash
export STRIPE_WEBHOOK_SECRET=whsec_your_signing_secret_here
```

### Step 4: Test Webhook

Use Stripe CLI to test:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to localhost
stripe listen --forward-to localhost:5000/stripe/webhook

# Trigger test event
stripe trigger payment_intent.succeeded
```

## Security Best Practices

### 1. Never Hardcode API Keys

```python
# ❌ WRONG - Never do this
stripe_api_key = "sk_live_1234567890"

# ✅ CORRECT - Use environment variables
import os
stripe_api_key = os.getenv("STRIPE_API_KEY")
```

### 2. Always Validate Webhook Signatures

```python
# ❌ WRONG - Never skip validation in production
tool = StripeHandleWebhooks(
    payload=payload,
    signature_header=sig_header,
    skip_signature_validation=True  # ONLY for testing!
)

# ✅ CORRECT - Always validate signatures
tool = StripeHandleWebhooks(
    payload=payload,
    signature_header=sig_header,
    skip_signature_validation=False  # Default
)
```

### 3. Use Test Mode for Development

```bash
# Development
export STRIPE_API_KEY=sk_test_...
export STRIPE_WEBHOOK_SECRET=whsec_test_...

# Production (only when ready)
export STRIPE_API_KEY=sk_live_...
export STRIPE_WEBHOOK_SECRET=whsec_...
```

### 4. Implement Idempotency

```python
# Use idempotency keys to prevent duplicate charges
tool = StripeCreatePayment(
    amount=2000,
    currency="usd",
    customer_email="customer@example.com",
    metadata={"idempotency_key": "unique_order_id_12345"}
)
```

### 5. Secure Webhook Endpoints

```python
# Add rate limiting
from flask_limiter import Limiter

limiter = Limiter(app, default_limits=["100 per minute"])

@app.route('/stripe/webhook', methods=['POST'])
@limiter.limit("10 per minute")
def stripe_webhook():
    # Process webhook
    pass
```

## Error Handling

All tools raise specific exceptions for different error types:

```python
from shared.errors import (
    ValidationError,
    APIError,
    AuthenticationError,
    SecurityError
)

try:
    tool = StripeCreatePayment(
        amount=2000,
        currency="usd",
        customer_email="customer@example.com"
    )
    result = tool.run()

except ValidationError as e:
    # Invalid input parameters
    print(f"Validation error: {e.message}")
    # Handle: Show user-friendly error

except AuthenticationError as e:
    # Missing or invalid API key
    print(f"Auth error: {e.message}")
    # Handle: Check configuration

except SecurityError as e:
    # Webhook signature validation failed
    print(f"Security error: {e.message}")
    # Handle: Log and reject request

except APIError as e:
    # Stripe API error
    print(f"API error: {e.message}")
    # Handle: Retry or show error to user
```

### Error Response Format

```python
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid currency code",
        "tool": "stripe_create_payment",
        "retry_after": None,
        "details": {...}
    }
}
```

## Testing

### Enable Mock Mode

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

# All tools will return mock data without calling Stripe API
tool = StripeCreatePayment(
    amount=2000,
    currency="usd",
    customer_email="test@example.com"
)
result = tool.run()

# Returns mock payment intent
print(result["payment_intent_id"])  # pi_mock_1234567890
```

### Run Tests

```bash
# Run all Stripe integration tests
pytest tests/integrations/stripe/ -v

# Run specific tool tests
pytest tests/integrations/stripe/test_stripe_create_payment.py -v

# Run with coverage
pytest tests/integrations/stripe/ --cov=tools.integrations.stripe --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Test Individual Tools

Each tool has a built-in test block:

```bash
# Test payment creation
python tools/integrations/stripe/stripe_create_payment.py

# Test subscription creation
python tools/integrations/stripe/stripe_create_subscription.py

# Test customer listing
python tools/integrations/stripe/stripe_list_customers.py

# Test invoice retrieval
python tools/integrations/stripe/stripe_get_invoices.py

# Test webhook handling
python tools/integrations/stripe/stripe_handle_webhooks.py
```

## API Reference

### Supported Currencies

All Stripe-supported currencies: `usd`, `eur`, `gbp`, `cad`, `aud`, `jpy`, `cny`, `inr`, `sgd`, `hkd`, and 135+ more.

### Payment Method Types

- `card` - Credit/debit cards
- `us_bank_account` - ACH direct debit
- `sepa_debit` - SEPA direct debit (Europe)
- `ideal` - iDEAL (Netherlands)
- `alipay` - Alipay (China)
- `wechat_pay` - WeChat Pay (China)

### Billing Intervals

- `daily` - Daily billing
- `weekly` - Weekly billing
- `monthly` - Monthly billing (most common)
- `yearly` - Yearly billing

### Invoice Statuses

- `draft` - Invoice not yet finalized
- `open` - Invoice sent but not paid
- `paid` - Invoice paid successfully
- `void` - Invoice voided
- `uncollectible` - Invoice marked as uncollectible

### Subscription Statuses

- `incomplete` - Payment method not attached
- `incomplete_expired` - Incomplete subscription expired
- `trialing` - In trial period
- `active` - Active subscription
- `past_due` - Payment failed
- `canceled` - Subscription cancelled
- `unpaid` - Multiple payment failures

## Contributing

Contributions are welcome! Please follow the Agency Swarm tool development standards:

1. All tools must be standalone with test blocks
2. Never hardcode secrets - use environment variables
3. Use Pydantic Field() with descriptions
4. Implement all 5 required BaseTool methods
5. 90%+ test coverage required

## Support

- **Documentation**: Individual tool READMEs in this directory
- **Stripe API**: https://stripe.com/docs/api
- **Stripe Support**: https://support.stripe.com
- **GitHub Issues**: [Report issues](https://github.com/your-repo/issues)

## License

MIT License - See LICENSE file for details.

---

Made with ❤️ for AgentSwarm Tools Framework
```
