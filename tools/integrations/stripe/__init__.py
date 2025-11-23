"""
Stripe Integration Tools for AgentSwarm

This module provides comprehensive Stripe payment integration tools for
creating payments, managing subscriptions, listing customers, retrieving
invoices, and handling webhooks.

Tools:
    - StripeCreatePayment: Create one-time payments
    - StripeCreateSubscription: Create recurring subscriptions
    - StripeListCustomers: List and search customers
    - StripeGetInvoices: Retrieve customer invoices
    - StripeHandleWebhooks: Process Stripe webhook events

Example:
    >>> from tools.integrations.stripe import StripeCreatePayment
    >>>
    >>> tool = StripeCreatePayment(
    ...     amount=2000,  # $20.00
    ...     currency="usd",
    ...     customer_email="customer@example.com"
    ... )
    >>> result = tool.run()
"""

from .stripe_create_payment import StripeCreatePayment
from .stripe_create_subscription import StripeCreateSubscription
from .stripe_get_invoices import StripeGetInvoices
from .stripe_handle_webhooks import STRIPE_EVENT_TYPES, StripeHandleWebhooks
from .stripe_list_customers import StripeListCustomers

__all__ = [
    "StripeCreatePayment",
    "StripeCreateSubscription",
    "StripeListCustomers",
    "StripeGetInvoices",
    "StripeHandleWebhooks",
    "STRIPE_EVENT_TYPES",
]

__version__ = "1.0.0"
__author__ = "AgentSwarm Tools"
__description__ = "Stripe payment integration tools for AgentSwarm"
