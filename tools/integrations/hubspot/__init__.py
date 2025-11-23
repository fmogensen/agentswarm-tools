"""
HubSpot Integration Tools

Complete HubSpot CRM and marketing automation integration for AgentSwarm Tools Framework.
Provides tools for contact management, deal tracking, email campaigns, analytics, and calendar sync.

Available Tools:
    - HubSpotCreateContact: Create/update contacts with custom properties and list management
    - HubSpotTrackDeal: Manage deals, pipelines, and sales forecasting
    - HubSpotSendEmail: Send marketing emails with templates and personalization
    - HubSpotGetAnalytics: Retrieve CRM and marketing analytics
    - HubSpotSyncCalendar: Sync meetings with Google Calendar

Example:
    >>> from tools.integrations.hubspot import HubSpotCreateContact
    >>> tool = HubSpotCreateContact(
    ...     email="john@example.com",
    ...     firstname="John",
    ...     lastname="Doe",
    ...     company="Acme Corp"
    ... )
    >>> result = tool.run()
"""

from .hubspot_create_contact import HubSpotCreateContact
from .hubspot_track_deal import HubSpotTrackDeal
from .hubspot_send_email import HubSpotSendEmail
from .hubspot_get_analytics import HubSpotGetAnalytics
from .hubspot_sync_calendar import HubSpotSyncCalendar

__all__ = [
    "HubSpotCreateContact",
    "HubSpotTrackDeal",
    "HubSpotSendEmail",
    "HubSpotGetAnalytics",
    "HubSpotSyncCalendar",
]

__version__ = "1.0.0"
__author__ = "AgentSwarm Tools Framework"
__description__ = "HubSpot CRM and Marketing Automation Integration"
