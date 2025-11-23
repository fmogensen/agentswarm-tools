# Linear Integration for AgentSwarm Tools Framework

Complete Linear integration with GraphQL API support for issue management, team collaboration, roadmap tracking, and GitHub synchronization.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [GitHub Sync Guide](#github-sync-guide)
- [Best Practices](#best-practices)
- [Error Handling](#error-handling)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

The Linear integration provides comprehensive tools for managing Linear issues, teams, cycles, and roadmaps programmatically through the AgentSwarm Tools Framework. Built on Linear's GraphQL API, these tools enable automated workflows, team capacity planning, and seamless GitHub synchronization.

### Key Capabilities

- **Issue Management**: Create and update issues with full field support
- **Team Collaboration**: Assign work with capacity planning and workload distribution
- **Roadmap Tracking**: Retrieve project status, milestones, and progress analytics
- **GitHub Integration**: Bi-directional sync with conflict resolution
- **Workflow Automation**: Status transitions, state management, and automated assignments

## Features

### LinearCreateIssue
- Create issues with projects, labels, priorities
- Support for estimates, due dates, and cycles
- Custom field values
- Sub-issue creation
- Subscriber management

### LinearUpdateStatus
- Update issue status with state transitions
- Workflow state validation
- Priority and estimate updates
- Assignee changes
- Label management
- Comment addition

### LinearAssignTeam
- Assign to teams and users
- Cycle/sprint management
- Story point estimation
- Auto-assignment to lowest workload
- Even distribution across team
- Capacity planning and utilization

### LinearGetRoadmap
- Retrieve projects and milestones
- Progress tracking and analytics
- Timeline visualization data
- Status and health metrics
- Filtering by team, status, dates

### LinearSyncGitHub
- Bi-directional Linear ↔ GitHub sync
- Issue and PR linking
- Status synchronization
- Label mapping
- Comment syncing
- Automatic branch creation
- Conflict detection and resolution

## Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# Install AgentSwarm Tools Framework
pip install agentswarm-tools

# Or install in development mode
git clone https://github.com/your-org/agentswarm-tools.git
cd agentswarm-tools
pip install -e .
```

### Dependencies

The Linear integration requires:

```bash
pip install requests>=2.31.0
pip install pydantic>=2.0.0
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required
LINEAR_API_KEY=lin_api_xxxxxxxxxxxxxxxxxxxxx

# For GitHub sync (optional)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx

# For testing
USE_MOCK_APIS=false
```

### Getting Linear API Key

1. Go to [Linear Settings → API](https://linear.app/settings/api)
2. Click "Create new API key"
3. Give it a descriptive name
4. Copy the key (starts with `lin_api_`)
5. Set as environment variable

### Getting GitHub Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Generate new token (classic)
3. Select scopes: `repo`, `read:org`
4. Copy token
5. Set as `GITHUB_TOKEN` environment variable

## Available Tools

| Tool | Purpose | Key Features |
|------|---------|--------------|
| `LinearCreateIssue` | Create issues | Projects, labels, priorities, estimates, sub-issues |
| `LinearUpdateStatus` | Update issues | Status transitions, assignee, priority, labels |
| `LinearAssignTeam` | Team assignment | Auto-assign, capacity planning, cycle management |
| `LinearGetRoadmap` | Roadmap retrieval | Projects, milestones, progress, timeline |
| `LinearSyncGitHub` | GitHub sync | Bi-directional sync, conflict resolution, PR linking |

## Quick Start

### Creating an Issue

```python
from tools.integrations.linear import LinearCreateIssue

tool = LinearCreateIssue(
    title="Implement user authentication",
    description="Add OAuth2 support for Google and GitHub login",
    team_id="team_abc123",
    priority=2,  # High priority
    labels=["feature", "auth"],
    estimate=5.0
)

result = tool.run()
print(f"Created issue: {result['issue_identifier']}")
print(f"URL: {result['issue_url']}")
```

### Updating Issue Status

```python
from tools.integrations.linear import LinearUpdateStatus

tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    state_name="In Progress",
    assignee_id="user_xyz789",
    comment="Starting work on this feature"
)

result = tool.run()
print(f"Updated to: {result['new_state']}")
```

### Assigning to Team

```python
from tools.integrations.linear import LinearAssignTeam

tool = LinearAssignTeam(
    issue_ids=["issue_1", "issue_2", "issue_3"],
    team_id="team_xyz",
    cycle_id="cycle_123",
    auto_assign=True,  # Distribute based on workload
    estimate=3.0
)

result = tool.run()
print(f"Assigned {result['assigned_count']} issues")
print(f"Capacity utilization: {result['capacity_summary']['utilization']:.1%}")
```

### Getting Roadmap

```python
from tools.integrations.linear import LinearGetRoadmap

tool = LinearGetRoadmap(
    team_id="team_xyz",
    status_filter="started",
    include_milestones=True,
    include_progress=True
)

result = tool.run()
print(f"Active projects: {result['roadmap_summary']['total_projects']}")
for project in result['projects']:
    print(f"  {project['name']}: {project['progress']:.0%} complete")
```

### Syncing with GitHub

```python
from tools.integrations.linear import LinearSyncGitHub

tool = LinearSyncGitHub(
    sync_direction="bidirectional",
    linear_issue_id="issue_abc123",
    github_repo="company/project",
    github_issue_number=42,
    sync_comments=True,
    sync_labels=True,
    conflict_resolution="linear_wins"
)

result = tool.run()
print(f"Synced {result['synced_count']} items")
if result['conflicts']:
    print(f"Conflicts detected: {len(result['conflicts'])}")
```

## Detailed Usage

### Priority Levels

Linear uses numeric priority levels:

- `0`: No priority (default)
- `1`: Urgent
- `2`: High
- `3`: Normal
- `4`: Low

```python
tool = LinearCreateIssue(
    title="Critical bug",
    team_id="team_xyz",
    priority=1  # Urgent
)
```

### Working with Cycles

Cycles (sprints) organize work into time-boxed iterations:

```python
# Assign multiple issues to current cycle
tool = LinearAssignTeam(
    issue_ids=["issue_1", "issue_2", "issue_3"],
    team_id="team_xyz",
    cycle_id="cycle_current_sprint",
    distribute_evenly=True
)
```

### Auto-Assignment Strategies

#### Lowest Workload

Assigns to team member with least current work:

```python
tool = LinearAssignTeam(
    issue_ids=["issue_abc"],
    team_id="team_xyz",
    auto_assign=True
)
```

#### Even Distribution

Round-robin distribution across team:

```python
tool = LinearAssignTeam(
    issue_ids=[f"issue_{i}" for i in range(10)],
    team_id="team_xyz",
    distribute_evenly=True
)
```

### State Transitions

Update issue state by name or ID:

```python
# By state name
tool = LinearUpdateStatus(
    issue_id="issue_abc",
    state_name="In Progress"
)

# Or by state ID
tool = LinearUpdateStatus(
    issue_id="issue_abc",
    state_id="state_xyz789"
)
```

### Label Management

Add or remove labels from issues:

```python
tool = LinearUpdateStatus(
    issue_id="issue_abc",
    add_labels=["bug", "urgent"],
    remove_labels=["backlog"]
)
```

### Estimates

Set story points or time estimates:

```python
tool = LinearCreateIssue(
    title="Medium task",
    team_id="team_xyz",
    estimate=3.0  # Story points
)
```

### Sub-Issues

Create hierarchical issue relationships:

```python
# Create parent issue
parent = LinearCreateIssue(
    title="Epic: User Management",
    team_id="team_xyz"
)

# Create sub-issue
child = LinearCreateIssue(
    title="Implement login",
    team_id="team_xyz",
    parent_id=parent.run()['issue_id']
)
```

## GitHub Sync Guide

### Setup

1. **Configure API Keys**:
   ```bash
   export LINEAR_API_KEY=lin_api_xxx
   export GITHUB_TOKEN=ghp_xxx
   ```

2. **Choose Sync Direction**:
   - `linear_to_github`: Linear → GitHub only
   - `github_to_linear`: GitHub → Linear only
   - `bidirectional`: Two-way sync

### Sync Scenarios

#### Create GitHub Issue from Linear

```python
tool = LinearSyncGitHub(
    sync_direction="linear_to_github",
    linear_issue_id="issue_abc123",
    github_repo="company/project",
    sync_labels=True,
    create_branch=True  # Auto-create feature branch
)
result = tool.run()
```

#### Link Existing Issues

```python
tool = LinearSyncGitHub(
    sync_direction="bidirectional",
    linear_issue_id="issue_abc123",
    github_issue_number=42,
    github_repo="company/project"
)
```

#### Batch Sync Team Issues

```python
tool = LinearSyncGitHub(
    sync_direction="linear_to_github",
    github_repo="company/project",
    batch_sync=True,
    batch_filters={
        "team_id": "team_xyz",
        "state": "In Progress"
    }
)
result = tool.run()
print(f"Synced {result['synced_count']} issues")
```

### Conflict Resolution

When syncing bidirectionally, conflicts may occur:

```python
tool = LinearSyncGitHub(
    sync_direction="bidirectional",
    linear_issue_id="issue_abc",
    github_issue_number=42,
    github_repo="company/project",
    conflict_resolution="linear_wins"  # or "github_wins" or "manual"
)

result = tool.run()
if result['conflicts']:
    for conflict in result['conflicts']:
        print(f"Conflict in {conflict['field']}")
        print(f"  Linear: {conflict['linear_value']}")
        print(f"  GitHub: {conflict['github_value']}")
```

### Label Mapping

Map Linear labels to GitHub labels:

```python
tool = LinearSyncGitHub(
    sync_direction="linear_to_github",
    linear_issue_id="issue_abc",
    github_repo="company/project",
    label_mapping={
        "bug": "type: bug",
        "urgent": "priority: high",
        "feature": "type: enhancement"
    }
)
```

### PR Linking

Link GitHub Pull Requests to Linear issues:

```python
tool = LinearSyncGitHub(
    sync_direction="linear_to_github",
    linear_issue_id="issue_abc123",
    github_repo="company/project",
    github_pr_number=156
)
```

## Best Practices

### Issue Creation

1. **Use descriptive titles**: Clear, actionable titles help team understanding
2. **Add context**: Include description with requirements, acceptance criteria
3. **Set appropriate priority**: Reserve urgent (1) for actual emergencies
4. **Estimate work**: Help with sprint planning and capacity management
5. **Use labels**: Categorize issues for filtering and organization

### Team Assignment

1. **Balance workload**: Use `auto_assign` for fair distribution
2. **Plan capacity**: Monitor capacity utilization to avoid overallocation
3. **Set deadlines**: Use cycles and due dates for time-bound work
4. **Track estimates**: Update estimates as work progresses

### Status Management

1. **Follow workflows**: Use valid state transitions for your team
2. **Add comments**: Document status changes with context
3. **Update assignees**: Reassign when handoffs occur
4. **Manage labels**: Keep labels current and relevant

### GitHub Sync

1. **Choose direction carefully**: Understand which system is source of truth
2. **Map labels thoughtfully**: Create consistent labeling across platforms
3. **Handle conflicts**: Define conflict resolution strategy upfront
4. **Batch wisely**: Use filters to sync relevant issues only
5. **Monitor sync**: Review sync results for errors or conflicts

## Error Handling

All tools return structured error responses:

```python
result = tool.run()

if not result['success']:
    error = result['error']
    print(f"Error: {error['message']}")
    print(f"Code: {error['code']}")

    if error['retry_after']:
        print(f"Retry after: {error['retry_after']}s")
```

### Common Errors

| Error Code | Cause | Solution |
|------------|-------|----------|
| `AUTH_ERROR` | Invalid API key | Check LINEAR_API_KEY environment variable |
| `VALIDATION_ERROR` | Invalid parameters | Review parameter values and types |
| `API_ERROR` | Linear API failure | Check Linear status, retry request |
| `RATE_LIMIT` | Too many requests | Wait and retry, implement backoff |
| `NOT_FOUND` | Resource doesn't exist | Verify IDs are correct |

## API Reference

### LinearCreateIssue

```python
LinearCreateIssue(
    title: str,                          # Required
    team_id: str,                        # Required
    description: Optional[str] = None,
    project_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    priority: int = 0,                   # 0-4
    labels: Optional[List[str]] = None,
    state_id: Optional[str] = None,
    estimate: Optional[float] = None,
    due_date: Optional[str] = None,      # ISO 8601
    parent_id: Optional[str] = None,
    cycle_id: Optional[str] = None,
    subscriber_ids: Optional[List[str]] = None,
    custom_fields: Optional[Dict] = None
)
```

### LinearUpdateStatus

```python
LinearUpdateStatus(
    issue_id: str,                       # Required
    state_id: Optional[str] = None,
    state_name: Optional[str] = None,
    priority: Optional[int] = None,
    assignee_id: Optional[str] = None,
    estimate: Optional[float] = None,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
    comment: Optional[str] = None
)
```

### LinearAssignTeam

```python
LinearAssignTeam(
    issue_ids: List[str],                # Required
    team_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    cycle_id: Optional[str] = None,
    estimate: Optional[float] = None,
    auto_assign: bool = False,
    distribute_evenly: bool = False,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None
)
```

### LinearGetRoadmap

```python
LinearGetRoadmap(
    team_id: Optional[str] = None,
    status_filter: Optional[str] = None, # planned, started, paused, completed, canceled
    include_archived: bool = False,
    include_milestones: bool = True,
    include_progress: bool = True,
    date_range_start: Optional[str] = None,
    date_range_end: Optional[str] = None,
    sort_by: str = "startDate",          # name, startDate, targetDate, progress
    limit: int = 50                      # 1-100
)
```

### LinearSyncGitHub

```python
LinearSyncGitHub(
    sync_direction: str,                 # linear_to_github, github_to_linear, bidirectional
    github_repo: str,                    # owner/repo format
    linear_issue_id: Optional[str] = None,
    github_issue_number: Optional[int] = None,
    github_pr_number: Optional[int] = None,
    sync_comments: bool = True,
    sync_labels: bool = True,
    sync_status: bool = True,
    create_branch: bool = False,
    conflict_resolution: str = "linear_wins",
    label_mapping: Optional[Dict[str, str]] = None,
    batch_sync: bool = False,
    batch_filters: Optional[Dict] = None
)
```

## Examples

### Sprint Planning Workflow

```python
from tools.integrations.linear import LinearGetRoadmap, LinearAssignTeam

# 1. Get backlog items
roadmap = LinearGetRoadmap(
    team_id="team_xyz",
    status_filter="planned",
    sort_by="priority"
)
backlog_result = roadmap.run()

# 2. Select top priority items
top_items = [p['id'] for p in backlog_result['projects'][:10]]

# 3. Assign to current sprint with even distribution
assign = LinearAssignTeam(
    issue_ids=top_items,
    team_id="team_xyz",
    cycle_id="current_sprint",
    distribute_evenly=True,
    estimate=5.0
)
assign_result = assign.run()

print(f"Sprint capacity: {assign_result['capacity_summary']['utilization']:.0%}")
```

### Bug Triage Automation

```python
from tools.integrations.linear import LinearCreateIssue, LinearUpdateStatus

# Create bug report
bug = LinearCreateIssue(
    title="User reported: Login fails on mobile",
    description="Users cannot login on iOS app",
    team_id="team_eng",
    priority=1,  # Urgent
    labels=["bug", "mobile", "auth"]
)
bug_result = bug.run()

# Auto-assign to on-call engineer
update = LinearUpdateStatus(
    issue_id=bug_result['issue_id'],
    assignee_id="oncall_engineer_id",
    state_name="In Progress",
    comment="Assigned to on-call engineer for immediate investigation"
)
```

### Release Management

```python
from tools.integrations.linear import LinearGetRoadmap, LinearSyncGitHub

# Get all completed issues for release
roadmap = LinearGetRoadmap(
    team_id="team_xyz",
    status_filter="completed",
    date_range_start="2025-12-01",
    date_range_end="2025-12-14"
)
release_issues = roadmap.run()

# Sync to GitHub for release notes
for issue in release_issues['projects']:
    sync = LinearSyncGitHub(
        sync_direction="linear_to_github",
        linear_issue_id=issue['id'],
        github_repo="company/product",
        sync_labels=True
    )
    sync.run()
```

## Testing

### Run All Tests

```bash
pytest tests/integrations/linear/ -v
```

### Run Specific Tool Tests

```bash
pytest tests/integrations/linear/test_linear_create_issue.py -v
pytest tests/integrations/linear/test_linear_sync_github.py -v
```

### Run with Coverage

```bash
pytest tests/integrations/linear/ --cov=tools.integrations.linear --cov-report=html
```

### Mock Mode

Enable mock mode for testing without API calls:

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = LinearCreateIssue(title="Test", team_id="team_xyz")
result = tool.run()  # Returns mock data
```

## Troubleshooting

### API Key Issues

**Problem**: `AUTH_ERROR: Missing LINEAR_API_KEY`

**Solution**:
```bash
export LINEAR_API_KEY=lin_api_your_key_here
```

### Invalid Team ID

**Problem**: `GraphQL errors: Team not found`

**Solution**: Get team ID from Linear:
```python
# Navigate to Linear → Team Settings → API
# Team ID is visible in URL: linear.app/team-abc123/settings
```

### Rate Limiting

**Problem**: `RATE_LIMIT: Too many requests`

**Solution**: Implement backoff:
```python
import time

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        result = func()
        if result['success']:
            return result
        if result.get('error', {}).get('code') == 'RATE_LIMIT':
            wait = result['error']['retry_after'] or 60
            time.sleep(wait)
    return result
```

### GitHub Sync Conflicts

**Problem**: Bidirectional sync shows conflicts

**Solution**: Choose conflict resolution strategy:
```python
# Option 1: Linear always wins
conflict_resolution="linear_wins"

# Option 2: GitHub always wins
conflict_resolution="github_wins"

# Option 3: Manual resolution
conflict_resolution="manual"
# Then review result['conflicts'] and resolve manually
```

## Support

- **Documentation**: See individual tool READMEs for detailed guides
- **Examples**: Check `examples/` directory for complete workflows
- **Issues**: Report bugs at GitHub repository
- **Linear API Docs**: https://developers.linear.app/docs

## License

Copyright © 2025. See LICENSE file for details.
