# Integrations Directory

## MCP-First Integration Strategy

**AgentSwarm Tools has adopted an MCP-first approach for enterprise integrations.**

This directory previously contained 25 integration tools for GitHub, HubSpot, Linear, Stripe, and Supabase. These integrations have been **removed** because official Model Context Protocol (MCP) servers now exist for all these services.

## Why MCP-First?

### Benefits of Using MCP Servers

- ✅ **No Duplication** - Avoid maintaining redundant integration code
- ✅ **Always Up-to-Date** - Official MCP servers maintained by vendors
- ✅ **Standardized Interface** - Consistent tool patterns across platforms
- ✅ **Better Security** - Official authentication and permissions
- ✅ **Community Support** - Leverage 100+ existing MCP servers
- ✅ **Reduced Maintenance** - No need to track API changes and updates

### Official MCP Servers

Instead of custom integrations, use these official MCP servers:

#### **Stripe** - Payment Processing
- **MCP Server:** https://mcp.stripe.com/
- **Documentation:** https://docs.stripe.com/mcp
- **Capabilities:** Customer management, payments, subscriptions, invoices, webhooks

#### **GitHub** - Developer Tools
- **MCP Server:** Official MCP server available
- **Capabilities:** Pull requests, code review, issues, actions, repository analytics

#### **Linear** - Project Management
- **MCP Server:** Official MCP server available
- **Capabilities:** Issue tracking, team assignment, roadmap, GitHub sync

#### **HubSpot** - CRM & Marketing
- **MCP Server:** @hubspot/mcp-server
- **Documentation:** https://developers.hubspot.com/mcp
- **Capabilities:** Contacts, deals, email campaigns, analytics, calendar sync

#### **Supabase** - Database & Backend
- **MCP Server:** https://mcp.supabase.com/mcp
- **Documentation:** https://supabase.com/docs/guides/getting-started/mcp
- **Capabilities:** Vector search, embeddings, authentication, realtime, storage

## Future Integration Guidelines

### When to Add Custom Integrations

Only add custom integrations to this directory when:

1. **No MCP Server Exists** - The service has no official or community MCP server
2. **Unique Functionality** - Your integration provides capabilities beyond what MCP offers
3. **Specialized Workflows** - Custom business logic that can't be achieved with MCP alone

### Services WITHOUT MCP Servers (Good Candidates)

Consider adding integrations for these services:

**Payment & Commerce:**
- Mailchimp - Email marketing
- SendGrid - Transactional email
- Square - Point of sale and payments
- PayPal - Alternative payment processing

**Customer Support:**
- Zendesk - Support ticket system
- Intercom - Customer messaging
- Freshdesk - Help desk software

**Productivity:**
- Airtable - No-code database
- ClickUp - Project management
- Monday.com - Work operating system
- Calendly - Meeting scheduling

**Authentication:**
- Auth0 - Authentication platform
- Okta - Identity management

### Services WITH MCP Servers (Avoid Duplication)

**Do NOT** add integrations for:
- GitHub, GitLab (developer tools)
- Slack, Discord (messaging)
- Notion, Google Drive (document management)
- Jira, Asana, Trello (project management with MCP)
- Salesforce, HubSpot (CRM with MCP)
- Stripe, Supabase (payment/backend with MCP)

## Migration Notes

If you were using the previous integration tools:

1. **Install MCP Servers** - Follow official documentation for each service
2. **Update Tool Calls** - Use MCP tool syntax instead of custom tool calls
3. **Configure Authentication** - Set up API keys/tokens in MCP configuration
4. **Test Workflows** - Verify all functionality works with MCP servers

## AgentSwarm Tools Focus

With MCP handling enterprise integrations, AgentSwarm Tools focuses on:

- **Specialized Media Processing** (image, video, audio generation and analysis)
- **Advanced Analytics** (business intelligence, trend analysis, reporting)
- **Custom Workflows** (pipeline orchestration, batch processing)
- **Domain-Specific Tools** (search, visualization, content creation)
- **Infrastructure Tools** (code execution, file management, storage)

These capabilities are **not available via MCP** and represent the unique value of AgentSwarm Tools.

---

**Last Updated:** 2025-11-24
**Status:** MCP-first strategy adopted
**Integration Count:** 0 (use MCP servers instead)
