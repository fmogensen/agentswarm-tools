# MCP Integration Guide for AgentSwarm

**Version:** 1.0
**Date:** November 22, 2025
**Purpose:** Connect AI agents to external systems via Model Context Protocol

---

## Overview

Instead of building custom integrations for every database, API, and service (months of work, $100K+), AgentSwarm leverages **Model Context Protocol (MCP)** to connect agents to 100+ pre-built servers. This guide shows you how to integrate MCP servers with Agency Swarm agents.

### What is MCP?

**Model Context Protocol (MCP)** is an open-source standard for connecting AI applications to external systems. Think of it as **"USB-C for AI applications"** - a universal connector that lets AI agents access:

- **Data sources**: PostgreSQL, MySQL, MongoDB, Redis, S3, Google Drive
- **Tools**: GitHub, Docker, Kubernetes, Stripe, Salesforce
- **Workflows**: Specialized prompts, APIs, and custom integrations

### Why MCP?

| Approach | Time | Cost | Maintenance |
|----------|------|------|-------------|
| **Build custom integrations** | 6+ months | $100K+ | High complexity |
| **Use MCP servers** | 1 week | $0 | Zero maintenance |

**Decision:** Use MCP servers ✅

---

## Architecture

```
AI Agent (Agency Swarm)
    ↓
MCP Client (MCPServerStdio/MCPServerSse)
    ↓
MCP Server (PostgreSQL/GitHub/Docker/etc)
    ↓
External System (Database/API/Service)
    ↓
Data & Tools Available to Agent
```

### MCP Components

1. **MCP Client**: Built into Agency Swarm (MCPServerStdio, MCPServerSse, MCPServerStreamableHttp)
2. **MCP Server**: Standalone process that exposes tools/resources from external systems
3. **Transport Layer**: Communication protocol (stdio, SSE, HTTP)
4. **Resources**: Data sources agents can read (files, database records)
5. **Tools**: Actions agents can execute (queries, API calls, operations)
6. **Prompts**: Specialized workflows agents can use

---

## Agency Swarm Native MCP Support

Agency Swarm added native MCP support in **April 2025** with the following classes:

### 1. MCPServerStdio

For local MCP servers that run as subprocesses.

```python
from agency_swarm.mcp import MCPServerStdio

# Local PostgreSQL MCP server
postgres_server = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost:5432/db"
    }
)
```

### 2. MCPServerSse

For remote MCP servers using Server-Sent Events (SSE).

```python
from agency_swarm.mcp import MCPServerSse

# Remote MCP server
remote_server = MCPServerSse(
    url="https://mcp.example.com/events",
    headers={
        "Authorization": "Bearer token"
    }
)
```

### 3. MCPServerStreamableHttp

For MCP servers with HTTP streaming transport.

```python
from agency_swarm.mcp import MCPServerStreamableHttp

# HTTP-based MCP server
http_server = MCPServerStreamableHttp(
    base_url="https://api.example.com/mcp",
    api_key="your_api_key"
)
```

### 4. HostedMCPTool

For using individual tools from MCP servers.

```python
from agency_swarm.mcp import HostedMCPTool

# Use specific tool from MCP server
db_query_tool = HostedMCPTool(
    server=postgres_server,
    tool_name="query_database"
)
```

---

## Popular MCP Servers (20+)

### Databases

#### PostgreSQL
```bash
# Installation
uvx mcp-server-postgres

# Usage
from agency_swarm.mcp import MCPServerStdio

postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={
        "POSTGRES_CONNECTION_STRING": "postgresql://localhost/mydb"
    }
)
```

**Features:**
- Schema inspection
- SQL query execution
- Read-only by default (safe)
- Transaction support

#### MySQL
```bash
# Installation
npm install -g @modelcontextprotocol/server-mysql

# Usage
mysql = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-mysql"],
    env={
        "MYSQL_HOST": "localhost",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "password",
        "MYSQL_DATABASE": "mydb"
    }
)
```

**Features:**
- Database queries
- Schema exploration
- Table inspection
- Data retrieval

#### MongoDB
```bash
# Installation
npm install -g @mongodb/mcp-server

# Usage
mongodb = MCPServerStdio(
    command="npx",
    args=["-y", "@mongodb/mcp-server"],
    env={
        "MONGODB_URI": "mongodb://localhost:27017",
        "MONGODB_DATABASE": "mydb"
    }
)
```

**Features:**
- Collection queries
- Document CRUD operations
- Aggregation pipelines
- MongoDB Atlas support

#### Redis
```bash
# Installation
uvx mcp-server-redis

# Usage
redis = MCPServerStdio(
    command="uvx",
    args=["mcp-server-redis"],
    env={
        "REDIS_URL": "redis://localhost:6379"
    }
)
```

**Features:**
- Key-value operations
- Search capabilities
- Data management
- Cache operations

### DevOps & Infrastructure

#### Docker
```bash
# Installation
npm install -g @modelcontextprotocol/server-docker

# Usage
docker = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-docker"],
    env={
        "DOCKER_HOST": "unix:///var/run/docker.sock"
    }
)
```

**Features:**
- Container management
- Image operations
- Volume management
- Network configuration

#### Kubernetes
```bash
# Installation
npm install -g mcp-server-k8s

# Usage
k8s = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-k8s"],
    env={
        "KUBECONFIG": "/path/to/kubeconfig"
    }
)
```

**Features:**
- Pod management
- Deployment operations
- Service configuration
- Cluster monitoring

#### Terraform
```bash
# Installation
uvx mcp-server-terraform

# Usage
terraform = MCPServerStdio(
    command="uvx",
    args=["mcp-server-terraform"],
    env={
        "TF_WORKSPACE": "/path/to/terraform"
    }
)
```

**Features:**
- Infrastructure as Code
- Plan/apply operations
- State management
- Resource tracking

### APIs & Services

#### GitHub
```bash
# Installation
npm install -g @modelcontextprotocol/server-github

# Usage
github = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
    }
)
```

**Features:**
- Repository management
- Issue tracking
- Pull requests
- File operations
- Search capabilities

#### GitLab
```bash
# Installation
npm install -g mcp-server-gitlab

# Usage
gitlab = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-gitlab"],
    env={
        "GITLAB_TOKEN": "glpat-xxx",
        "GITLAB_URL": "https://gitlab.com"
    }
)
```

**Features:**
- Project management
- Merge requests
- CI/CD pipelines
- Issue tracking

#### Stripe
```bash
# Installation
npm install -g mcp-server-stripe

# Usage
stripe = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-stripe"],
    env={
        "STRIPE_SECRET_KEY": "sk_test_xxx"
    }
)
```

**Features:**
- Payment processing
- Customer management
- Subscription handling
- Invoice operations

#### Salesforce
```bash
# Installation
npm install -g mcp-server-salesforce

# Usage
salesforce = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-salesforce"],
    env={
        "SALESFORCE_USERNAME": "user@example.com",
        "SALESFORCE_PASSWORD": "password",
        "SALESFORCE_TOKEN": "token"
    }
)
```

**Features:**
- CRM operations
- Lead management
- Opportunity tracking
- Custom objects

### Development Tools

#### npm
```bash
# Installation
uvx mcp-server-npm

# Usage
npm_server = MCPServerStdio(
    command="uvx",
    args=["mcp-server-npm"]
)
```

**Features:**
- Package search
- Version lookup
- Dependency analysis
- Package information

#### pip
```bash
# Installation
uvx mcp-server-pypi

# Usage
pypi = MCPServerStdio(
    command="uvx",
    args=["mcp-server-pypi"]
)
```

**Features:**
- Python package search
- Version information
- Download statistics
- Package metadata

### Cloud Platforms

#### AWS S3
```bash
# Installation
npm install -g @modelcontextprotocol/server-aws-s3

# Usage
s3 = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-aws-s3"],
    env={
        "AWS_ACCESS_KEY_ID": "AKIAXXXX",
        "AWS_SECRET_ACCESS_KEY": "secret",
        "AWS_REGION": "us-east-1"
    }
)
```

**Features:**
- File upload/download
- Bucket management
- Object operations
- Presigned URLs

#### Google Cloud Storage
```bash
# Installation
npm install -g mcp-server-gcs

# Usage
gcs = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-gcs"],
    env={
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json"
    }
)
```

**Features:**
- Bucket operations
- File management
- Access control
- Storage analytics

### Productivity & Collaboration

#### Notion
```bash
# Installation
npm install -g @notionhq/mcp-server

# Usage
notion = MCPServerStdio(
    command="npx",
    args=["-y", "@notionhq/mcp-server"],
    env={
        "NOTION_API_KEY": "secret_xxx"
    }
)
```

**Features:**
- Page creation
- Database queries
- Content updates
- Search capabilities

#### Slack
```bash
# Installation
npm install -g mcp-server-slack

# Usage
slack = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-slack"],
    env={
        "SLACK_BOT_TOKEN": "xoxb-xxx",
        "SLACK_APP_TOKEN": "xapp-xxx"
    }
)
```

**Features:**
- Message sending
- Channel management
- User operations
- File sharing

#### Linear
```bash
# Installation
npm install -g mcp-server-linear

# Usage
linear = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-linear"],
    env={
        "LINEAR_API_KEY": "lin_api_xxx"
    }
)
```

**Features:**
- Issue creation
- Project management
- Team operations
- Search functionality

---

## Setup Instructions

### Step 1: Install MCP Dependencies

```bash
# Install Agency Swarm with MCP support
pip install agency-swarm>=0.3.0

# Install uvx for Python-based MCP servers
pip install uvx

# Install Node.js for JavaScript-based MCP servers
# (if not already installed)
# macOS: brew install node
# Ubuntu: apt install nodejs npm
```

### Step 2: Install MCP Servers

```bash
# Python-based servers (via uvx)
uvx mcp-server-postgres
uvx mcp-server-redis

# JavaScript-based servers (via npm/npx)
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-docker
```

### Step 3: Configure Environment Variables

```bash
# Create .env file
cat > .env << EOF
# Database connections
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/db
MONGODB_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379

# API tokens
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx
STRIPE_SECRET_KEY=sk_test_xxx
SALESFORCE_TOKEN=xxx

# Cloud credentials
AWS_ACCESS_KEY_ID=AKIAXXXX
AWS_SECRET_ACCESS_KEY=secret
GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json
EOF
```

### Step 4: Test MCP Server

```bash
# Test PostgreSQL MCP server
uvx mcp-server-postgres --help

# Test GitHub MCP server
npx -y @modelcontextprotocol/server-github --help
```

---

## Integration Tutorials

### Tutorial 1: Database Agent with PostgreSQL

```python
from agency_swarm import Agent, Agency
from agency_swarm.mcp import MCPServerStdio
import os

# Configure PostgreSQL MCP server
postgres_server = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={
        "POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_CONNECTION_STRING")
    }
)

# Create database agent
db_agent = Agent(
    name="DatabaseAgent",
    description="Agent with PostgreSQL database access",
    instructions="""You can query the PostgreSQL database.

    Available capabilities:
    - Execute SELECT queries
    - Inspect database schema
    - Analyze table structures
    - Retrieve data for analysis

    Always:
    - Use read-only queries
    - Validate query syntax
    - Return results in clear format
    - Handle errors gracefully
    """,
    mcp_servers=[postgres_server],  # Add MCP server
    model="gpt-4o"
)

# Create agency
agency = Agency(
    [db_agent],
    shared_instructions="Use database responsibly"
)

# Run query
response = agency.get_completion(
    "Show me the top 10 customers by revenue from the sales database"
)
print(response)
```

### Tutorial 2: DevOps Agent with Docker & Kubernetes

```python
from agency_swarm import Agent, Agency
from agency_swarm.mcp import MCPServerStdio
import os

# Configure Docker MCP server
docker_server = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-docker"],
    env={
        "DOCKER_HOST": "unix:///var/run/docker.sock"
    }
)

# Configure Kubernetes MCP server
k8s_server = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-k8s"],
    env={
        "KUBECONFIG": os.getenv("KUBECONFIG")
    }
)

# Create DevOps agent
devops_agent = Agent(
    name="DevOpsAgent",
    description="Manages containers and Kubernetes clusters",
    instructions="""You manage Docker containers and Kubernetes deployments.

    Docker capabilities:
    - List/start/stop containers
    - Manage images
    - Monitor resources

    Kubernetes capabilities:
    - Deploy applications
    - Scale deployments
    - Monitor pod health
    - Manage services

    Always verify operations before execution.
    """,
    mcp_servers=[docker_server, k8s_server],  # Multiple MCP servers
    model="gpt-4o"
)

# Create agency
agency = Agency([devops_agent])

# Execute DevOps task
response = agency.get_completion(
    "List all running Docker containers and their resource usage"
)
print(response)
```

### Tutorial 3: GitHub Integration Agent

```python
from agency_swarm import Agent, Agency
from agency_swarm.mcp import MCPServerStdio
import os

# Configure GitHub MCP server
github_server = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={
        "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")
    }
)

# Create GitHub agent
github_agent = Agent(
    name="GitHubAgent",
    description="Manages GitHub repositories and issues",
    instructions="""You interact with GitHub repositories.

    Capabilities:
    - Search repositories and code
    - Create/update issues
    - Manage pull requests
    - Read file contents
    - Track project activity

    Provide helpful summaries and actionable insights.
    """,
    mcp_servers=[github_server],
    model="gpt-4o"
)

# Create agency
agency = Agency([github_agent])

# GitHub operations
response = agency.get_completion(
    "Find all open issues in VRSEN/agency-swarm labeled 'bug' and summarize them"
)
print(response)
```

### Tutorial 4: Multi-Database Analytics Agent

```python
from agency_swarm import Agent, Agency
from agency_swarm.mcp import MCPServerStdio
import os

# Configure multiple database servers
postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
)

mongodb = MCPServerStdio(
    command="npx",
    args=["-y", "@mongodb/mcp-server"],
    env={
        "MONGODB_URI": os.getenv("MONGODB_URI"),
        "MONGODB_DATABASE": "analytics"
    }
)

redis = MCPServerStdio(
    command="uvx",
    args=["mcp-server-redis"],
    env={"REDIS_URL": os.getenv("REDIS_URL")}
)

# Create analytics agent
analytics_agent = Agent(
    name="AnalyticsAgent",
    description="Cross-database analytics specialist",
    instructions="""You analyze data across multiple databases.

    Data sources:
    - PostgreSQL: Transactional data (orders, customers)
    - MongoDB: User behavior logs
    - Redis: Real-time metrics

    Combine data from multiple sources to provide insights.
    """,
    mcp_servers=[postgres, mongodb, redis],
    model="gpt-4o"
)

# Create agency
agency = Agency([analytics_agent])

# Cross-database analysis
response = agency.get_completion(
    """Analyze today's sales performance:
    1. Get order count from PostgreSQL
    2. Get user activity from MongoDB
    3. Get current traffic from Redis
    Provide a comprehensive summary.
    """
)
print(response)
```

### Tutorial 5: E-commerce Agent with Stripe

```python
from agency_swarm import Agent, Agency
from agency_swarm.mcp import MCPServerStdio
import os

# Configure Stripe MCP server
stripe_server = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-stripe"],
    env={
        "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY")
    }
)

# Create e-commerce agent
ecommerce_agent = Agent(
    name="EcommerceAgent",
    description="Manages payments and subscriptions",
    instructions="""You handle Stripe payment operations.

    Capabilities:
    - Create/manage customers
    - Process payments
    - Handle subscriptions
    - Generate invoices
    - Track transactions

    Always verify amounts and customer details.
    """,
    mcp_servers=[stripe_server],
    model="gpt-4o"
)

# Create agency
agency = Agency([ecommerce_agent])

# Payment operations
response = agency.get_completion(
    "Show me all customers who subscribed in the last 7 days"
)
print(response)
```

---

## Real-World Use Cases

### 1. Automated Database Administration

```python
from agency_swarm import Agent, Agency
from agency_swarm.mcp import MCPServerStdio

# Setup
postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
)

dba_agent = Agent(
    name="DBA",
    instructions="""Database administration tasks:
    - Monitor slow queries
    - Analyze table statistics
    - Identify missing indexes
    - Generate optimization reports
    """,
    mcp_servers=[postgres],
    model="gpt-4o"
)

# Usage
agency = Agency([dba_agent])
report = agency.get_completion("Generate daily database health report")
```

### 2. CI/CD Pipeline Management

```python
github_server = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")}
)

cicd_agent = Agent(
    name="CICDManager",
    instructions="""Manage CI/CD pipelines:
    - Monitor build failures
    - Analyze test results
    - Track deployment status
    - Create bug reports
    """,
    mcp_servers=[github_server],
    model="gpt-4o"
)

# Auto-respond to failed builds
agency = Agency([cicd_agent])
response = agency.get_completion(
    "Check recent failed builds and create issues for failures"
)
```

### 3. Customer Support Automation

```python
salesforce = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-salesforce"],
    env={
        "SALESFORCE_USERNAME": os.getenv("SF_USERNAME"),
        "SALESFORCE_PASSWORD": os.getenv("SF_PASSWORD"),
        "SALESFORCE_TOKEN": os.getenv("SF_TOKEN")
    }
)

support_agent = Agent(
    name="SupportAgent",
    instructions="""Handle customer support:
    - Look up customer information
    - Track support tickets
    - Update case status
    - Escalate priority issues
    """,
    mcp_servers=[salesforce],
    model="gpt-4o"
)

# Auto-triage support tickets
agency = Agency([support_agent])
response = agency.get_completion(
    "Review all open support cases and prioritize by severity"
)
```

### 4. Infrastructure Monitoring

```python
docker = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-docker"],
    env={"DOCKER_HOST": "unix:///var/run/docker.sock"}
)

k8s = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-k8s"],
    env={"KUBECONFIG": os.getenv("KUBECONFIG")}
)

infra_agent = Agent(
    name="InfraMonitor",
    instructions="""Monitor infrastructure:
    - Check container health
    - Monitor resource usage
    - Detect anomalies
    - Auto-scale services
    """,
    mcp_servers=[docker, k8s],
    model="gpt-4o"
)

# Continuous monitoring
agency = Agency([infra_agent])
response = agency.get_completion(
    "Check all services and report any issues"
)
```

### 5. Multi-Cloud Storage Management

```python
s3 = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-aws-s3"],
    env={
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_KEY"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET"),
        "AWS_REGION": "us-east-1"
    }
)

gcs = MCPServerStdio(
    command="npx",
    args=["-y", "mcp-server-gcs"],
    env={
        "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GCS_CREDS")
    }
)

storage_agent = Agent(
    name="StorageManager",
    instructions="""Manage cloud storage:
    - Sync files between S3 and GCS
    - Optimize storage costs
    - Monitor usage patterns
    - Generate reports
    """,
    mcp_servers=[s3, gcs],
    model="gpt-4o"
)

# Storage optimization
agency = Agency([storage_agent])
response = agency.get_completion(
    "Analyze storage usage and suggest cost optimizations"
)
```

---

## Best Practices

### 1. Security

#### API Key Management

❌ **Bad:**
```python
github_server = MCPServerStdio(
    env={"GITHUB_TOKEN": "ghp_hardcoded_token"}  # Never!
)
```

✅ **Good:**
```python
import os

github_server = MCPServerStdio(
    env={"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")}  # Always use env vars
)
```

#### Read-Only Access

```python
# Grant minimum necessary permissions
postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres", "--read-only"],  # Read-only mode
    env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
)
```

### 2. Error Handling

```python
from agency_swarm import Agent, Agency
from agency_swarm.mcp import MCPServerStdio

try:
    # Configure MCP server
    postgres = MCPServerStdio(
        command="uvx",
        args=["mcp-server-postgres"],
        env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
    )

    # Create agent
    agent = Agent(
        name="DBAgent",
        mcp_servers=[postgres],
        model="gpt-4o"
    )

    # Run task
    response = agency.get_completion("Query database")

except Exception as e:
    print(f"Error: {e}")
    # Log error, send alert, etc.
```

### 3. Resource Management

```python
# Use context managers for proper cleanup
from agency_swarm.mcp import MCPServerStdio

with MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
) as postgres:
    agent = Agent(
        name="DBAgent",
        mcp_servers=[postgres],
        model="gpt-4o"
    )
    # MCP server automatically cleaned up when done
```

### 4. Testing

```python
import pytest
from agency_swarm import Agent
from agency_swarm.mcp import MCPServerStdio
import os

@pytest.fixture
def postgres_server():
    """Test fixture for PostgreSQL MCP server."""
    return MCPServerStdio(
        command="uvx",
        args=["mcp-server-postgres"],
        env={
            "POSTGRES_CONNECTION_STRING": os.getenv("TEST_POSTGRES_URL")
        }
    )

def test_db_agent(postgres_server):
    """Test database agent with MCP server."""
    agent = Agent(
        name="TestDBAgent",
        mcp_servers=[postgres_server],
        model="gpt-4o"
    )

    # Test agent can access database
    assert agent.mcp_servers
    assert len(agent.mcp_servers) == 1
```

### 5. Monitoring

```python
from agency_swarm import Agent, Agency
from agency_swarm.mcp import MCPServerStdio
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agency_swarm.mcp")
logger.setLevel(logging.DEBUG)

# Configure MCP server
postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
)

# Create agent with logging
agent = Agent(
    name="DBAgent",
    mcp_servers=[postgres],
    model="gpt-4o"
)

# All MCP operations will be logged
```

### 6. Performance Optimization

```python
# Reuse MCP server instances
postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
)

# Multiple agents can share the same MCP server
agent1 = Agent(name="Agent1", mcp_servers=[postgres], model="gpt-4o")
agent2 = Agent(name="Agent2", mcp_servers=[postgres], model="gpt-4o")

# Better than creating separate servers for each agent
```

### 7. Graceful Degradation

```python
from agency_swarm import Agent
from agency_swarm.mcp import MCPServerStdio

def create_agent_with_fallback():
    """Create agent with MCP fallback."""
    try:
        # Try to connect to primary database
        postgres = MCPServerStdio(
            command="uvx",
            args=["mcp-server-postgres"],
            env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
        )
        mcp_servers = [postgres]
    except Exception:
        # Fallback to no MCP servers
        print("Warning: PostgreSQL MCP server unavailable")
        mcp_servers = []

    return Agent(
        name="DBAgent",
        mcp_servers=mcp_servers,
        instructions="""Query database if available.
        If database unavailable, explain limitation to user.
        """,
        model="gpt-4o"
    )
```

---

## Configuration Examples

### Multi-Environment Setup

```python
import os
from agency_swarm.mcp import MCPServerStdio

# Environment-specific configuration
ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    db_url = os.getenv("PROD_POSTGRES_URL")
elif ENV == "staging":
    db_url = os.getenv("STAGING_POSTGRES_URL")
else:
    db_url = os.getenv("DEV_POSTGRES_URL")

postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={
        "POSTGRES_CONNECTION_STRING": db_url,
        "ENVIRONMENT": ENV
    }
)
```

### Docker Compose Integration

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  agent:
    build: .
    depends_on:
      - postgres
      - redis
    environment:
      POSTGRES_CONNECTION_STRING: postgresql://user:password@postgres:5432/mydb
      REDIS_URL: redis://redis:6379
```

### Kubernetes Deployment

```yaml
# agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-agent
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: agent
        image: my-agency-agent:latest
        env:
        - name: POSTGRES_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: postgres-url
        - name: GITHUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: api-tokens
              key: github-token
```

---

## Troubleshooting

### Issue 1: MCP Server Not Starting

**Symptoms:**
```
Error: MCP server failed to start
```

**Solutions:**

```bash
# Check server is installed
uvx mcp-server-postgres --version
npx -y @modelcontextprotocol/server-github --version

# Check environment variables
echo $POSTGRES_CONNECTION_STRING
echo $GITHUB_PERSONAL_ACCESS_TOKEN

# Test server manually
uvx mcp-server-postgres
# Should start without errors
```

### Issue 2: Connection Errors

**Symptoms:**
```
ConnectionError: Failed to connect to database
```

**Solutions:**

```python
# Verify connection string format
# PostgreSQL: postgresql://user:pass@host:port/database
# MongoDB: mongodb://host:port/database
# Redis: redis://host:port

# Test connection separately
import psycopg2
conn = psycopg2.connect(os.getenv("POSTGRES_CONNECTION_STRING"))
print("Connection successful!")
```

### Issue 3: Permission Denied

**Symptoms:**
```
PermissionError: Insufficient privileges
```

**Solutions:**

```python
# Check API token permissions
# GitHub: Needs repo, read:org scopes
# Stripe: Needs read/write permissions
# AWS: Needs appropriate IAM policies

# Use read-only mode for testing
postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres", "--read-only"],
    env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
)
```

### Issue 4: Slow Performance

**Symptoms:**
```
Queries taking 10+ seconds
```

**Solutions:**

```python
# Use connection pooling
postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres", "--pool-size=10"],
    env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
)

# Add query timeouts
agent = Agent(
    name="DBAgent",
    instructions="Use queries with LIMIT. Timeout after 30 seconds.",
    mcp_servers=[postgres],
    model="gpt-4o"
)
```

### Issue 5: Memory Leaks

**Symptoms:**
```
Memory usage growing over time
```

**Solutions:**

```python
# Properly close MCP servers
from contextlib import closing

with closing(MCPServerStdio(...)) as server:
    agent = Agent(mcp_servers=[server], ...)
    # Server closed automatically

# Or manually
server = MCPServerStdio(...)
try:
    agent = Agent(mcp_servers=[server], ...)
    # Use agent
finally:
    server.close()
```

---

## Advanced Patterns

### Pattern 1: Dynamic MCP Server Selection

```python
from agency_swarm import Agent
from agency_swarm.mcp import MCPServerStdio

def get_database_server(db_type: str):
    """Get MCP server based on database type."""
    servers = {
        "postgres": lambda: MCPServerStdio(
            command="uvx",
            args=["mcp-server-postgres"],
            env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
        ),
        "mongodb": lambda: MCPServerStdio(
            command="npx",
            args=["-y", "@mongodb/mcp-server"],
            env={"MONGODB_URI": os.getenv("MONGODB_URI")}
        ),
        "redis": lambda: MCPServerStdio(
            command="uvx",
            args=["mcp-server-redis"],
            env={"REDIS_URL": os.getenv("REDIS_URL")}
        )
    }
    return servers[db_type]()

# Use dynamically
db_agent = Agent(
    name="DBAgent",
    mcp_servers=[get_database_server("postgres")],
    model="gpt-4o"
)
```

### Pattern 2: MCP Server Health Checks

```python
from agency_swarm.mcp import MCPServerStdio
import time

def wait_for_server(server, timeout=30):
    """Wait for MCP server to be ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            # Try to list server capabilities
            if server.list_tools():
                return True
        except:
            time.sleep(1)
    raise TimeoutError("MCP server failed to start")

# Use with health check
postgres = MCPServerStdio(
    command="uvx",
    args=["mcp-server-postgres"],
    env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
)

wait_for_server(postgres)  # Ensure ready
agent = Agent(mcp_servers=[postgres], model="gpt-4o")
```

### Pattern 3: Conditional MCP Loading

```python
from agency_swarm import Agent
from agency_swarm.mcp import MCPServerStdio

def create_agent_with_optional_mcp(enable_db=True, enable_github=True):
    """Create agent with optional MCP servers."""
    mcp_servers = []

    if enable_db:
        mcp_servers.append(MCPServerStdio(
            command="uvx",
            args=["mcp-server-postgres"],
            env={"POSTGRES_CONNECTION_STRING": os.getenv("POSTGRES_URL")}
        ))

    if enable_github:
        mcp_servers.append(MCPServerStdio(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")}
        ))

    return Agent(
        name="FlexibleAgent",
        mcp_servers=mcp_servers,
        model="gpt-4o"
    )

# Create different agent configurations
basic_agent = create_agent_with_optional_mcp(enable_db=False, enable_github=False)
db_agent = create_agent_with_optional_mcp(enable_db=True, enable_github=False)
full_agent = create_agent_with_optional_mcp(enable_db=True, enable_github=True)
```

---

## Cost Analysis

### MCP Server Costs

Most MCP servers are **free and open-source**. Costs come from:

1. **Infrastructure**: Cloud databases, APIs
2. **API Usage**: GitHub, Stripe, AWS API calls
3. **Compute**: Running MCP server processes

### Cost Comparison

| Approach | Setup Cost | Monthly Cost | Maintenance |
|----------|------------|--------------|-------------|
| **Custom integrations** | $100K+ | $5K-20K | High |
| **MCP servers** | $0 | $0-500 | Minimal |

### Example Costs

**Scenario 1:** Small team using GitHub + PostgreSQL
```
GitHub API: Free (personal use)
PostgreSQL: $0 (self-hosted) or $20/mo (managed)
MCP servers: $0 (open source)
Total: $0-20/month
```

**Scenario 2:** Enterprise with multiple integrations
```
Databases: $200/mo (managed services)
APIs: $500/mo (Stripe, Salesforce, etc.)
Cloud storage: $100/mo
MCP servers: $0 (open source)
Total: $800/month

vs Custom Build: $15K/month (infrastructure + dev)
Savings: $14,200/month = $170K/year
```

---

## Resources

### Official Documentation

- **MCP Protocol**: https://modelcontextprotocol.io
- **MCP Servers**: https://github.com/modelcontextprotocol/servers
- **Agency Swarm**: https://agency-swarm.ai
- **Agency Swarm MCP PR**: https://github.com/VRSEN/agency-swarm/pull/264

### Community Resources

- **Awesome MCP Servers**: https://github.com/mctrinh/awesome-mcp-servers
- **MCP Examples**: https://modelcontextprotocol.io/examples
- **Agency Swarm Examples**: https://github.com/VRSEN/agency-swarm/tree/main/examples

### Server Catalogs

- **Official Registry**: https://github.com/modelcontextprotocol/servers
- **Community Servers**: https://github.com/mctrinh/awesome-mcp-servers
- **Docker Hub**: https://hub.docker.com/mcp

---

## Next Steps

1. ✅ Install Agency Swarm with MCP support
2. ✅ Choose MCP servers for your use case
3. ✅ Set up environment variables
4. ✅ Test individual MCP servers
5. ✅ Create agents with MCP integration
6. ✅ Build multi-agent workflows
7. ✅ Deploy to production
8. ✅ Monitor and optimize

---

## Summary

**MCP Integration Benefits:**

- ✅ 100+ pre-built servers (databases, APIs, DevOps)
- ✅ Zero integration cost vs $100K+ custom build
- ✅ 1-week setup vs 6-month development
- ✅ Native Agency Swarm support (MCPServerStdio, MCPServerSse)
- ✅ Open-source and community-driven
- ✅ Production-ready and scalable
- ✅ Minimal maintenance

**Result:** Connect AI agents to any system in hours, not months. 🎯

---

**Questions or issues?** Create an issue on GitHub or contact support@agentswarm.ai
