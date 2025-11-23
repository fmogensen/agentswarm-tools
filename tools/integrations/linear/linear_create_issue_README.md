# LinearCreateIssue Tool

Create Linear issues with comprehensive field support including projects, labels, assignees, priorities, estimates, and custom fields.

## Overview

The `LinearCreateIssue` tool provides full-featured issue creation in Linear with support for:
- Project and team assignment
- Priority levels and labels
- Story point estimates
- Due dates and cycles
- Parent-child relationships (sub-issues)
- Custom field values
- Subscriber management

## Quick Start

```python
from tools.integrations.linear import LinearCreateIssue

tool = LinearCreateIssue(
    title="Implement user authentication",
    description="Add OAuth2 support for Google login",
    team_id="team_abc123",
    priority=2,
    labels=["feature", "auth"],
    estimate=5.0
)

result = tool.run()
print(f"Created: {result['issue_identifier']}")  # ENG-123
print(f"URL: {result['issue_url']}")
```

## Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | str | Issue title (1-255 characters) |
| `team_id` | str | Linear team ID (e.g., 'team_abc123') |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | str | None | Markdown description (max 50,000 chars) |
| `project_id` | str | None | Project ID to associate issue with |
| `assignee_id` | str | None | User ID to assign issue to |
| `priority` | int | 0 | Priority: 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low |
| `labels` | List[str] | None | List of label IDs |
| `state_id` | str | None | Workflow state ID (defaults to team default) |
| `estimate` | float | None | Story points/time estimate |
| `due_date` | str | None | Due date (ISO 8601: YYYY-MM-DD) |
| `parent_id` | str | None | Parent issue ID for sub-issues |
| `cycle_id` | str | None | Cycle/sprint ID |
| `subscriber_ids` | List[str] | None | User IDs to subscribe |
| `custom_fields` | Dict | None | Custom field values |

## Return Value

```python
{
    "success": True,
    "issue_id": "issue_abc123def456",
    "issue_identifier": "ENG-123",
    "issue_url": "https://linear.app/workspace/issue/ENG-123",
    "title": "Issue title",
    "state": "Todo",
    "metadata": {
        "tool_name": "linear_create_issue",
        "team_id": "team_abc123",
        "project_id": "proj_def456"
    }
}
```

## Examples

### Basic Issue

```python
tool = LinearCreateIssue(
    title="Fix login bug",
    team_id="team_eng"
)
result = tool.run()
```

### Feature with Full Details

```python
tool = LinearCreateIssue(
    title="Add dark mode support",
    description="""
    # Requirements
    - Toggle in settings
    - Persist user preference
    - Support system preference

    # Acceptance Criteria
    - [ ] Toggle added to settings
    - [ ] Dark theme applied globally
    - [ ] Preference saved to localStorage
    """,
    team_id="team_frontend",
    project_id="proj_q4_features",
    assignee_id="user_alice",
    priority=2,  # High
    labels=["feature", "ui", "accessibility"],
    estimate=8.0,
    due_date="2025-12-31",
    cycle_id="cycle_sprint_12"
)
```

### Sub-Issue Creation

```python
# Create parent epic
parent = LinearCreateIssue(
    title="Epic: User Management System",
    team_id="team_backend",
    estimate=40.0
)
parent_result = parent.run()

# Create sub-tasks
subtasks = [
    "Implement user registration",
    "Add email verification",
    "Create password reset flow",
    "Build user profile page"
]

for task in subtasks:
    child = LinearCreateIssue(
        title=task,
        team_id="team_backend",
        parent_id=parent_result['issue_id'],
        estimate=10.0
    )
    child.run()
```

### Bug Report

```python
tool = LinearCreateIssue(
    title="Mobile app crashes on iOS 15",
    description="""
    ## Steps to Reproduce
    1. Open app on iPhone 12 (iOS 15.0)
    2. Navigate to Settings
    3. Tap 'About'
    4. App crashes

    ## Expected
    About page should display

    ## Actual
    App crashes with error code 502

    ## Environment
    - iOS 15.0
    - App version 2.1.0
    """,
    team_id="team_mobile",
    priority=1,  # Urgent
    labels=["bug", "ios", "crash"],
    assignee_id="oncall_engineer",
    subscriber_ids=["team_lead", "qa_lead"]
)
```

## Priority Levels

| Value | Level | When to Use |
|-------|-------|-------------|
| 0 | None | Backlog items, no urgency |
| 1 | Urgent | Production issues, blockers |
| 2 | High | Important features, significant bugs |
| 3 | Normal | Standard work items |
| 4 | Low | Nice-to-haves, minor improvements |

## Date Formats

All dates use ISO 8601 format:

```python
# Valid formats
due_date="2025-12-31"
due_date="2025-01-15"
due_date="2026-06-30"
```

## Finding IDs

### Team ID
1. Navigate to Linear → Team Settings
2. URL shows team ID: `linear.app/team-abc123/settings`
3. Or use GraphQL: `query { teams { nodes { id name } } }`

### Project ID
1. Go to project in Linear
2. Check URL: `linear.app/team-abc/project/proj-def456`
3. Or GraphQL: `query { projects { nodes { id name } } }`

### Label IDs
```graphql
query {
  issueLabels {
    nodes {
      id
      name
      color
    }
  }
}
```

### User IDs
```graphql
query {
  users {
    nodes {
      id
      name
      email
    }
  }
}
```

## Error Handling

```python
result = tool.run()

if not result['success']:
    error = result['error']

    if error['code'] == 'VALIDATION_ERROR':
        print(f"Invalid input: {error['message']}")
    elif error['code'] == 'AUTH_ERROR':
        print("Check LINEAR_API_KEY")
    elif error['code'] == 'API_ERROR':
        print(f"Linear API error: {error['message']}")
```

## Best Practices

1. **Descriptive Titles**: Use clear, actionable titles
   - Good: "Add email validation to signup form"
   - Bad: "Fix thing"

2. **Detailed Descriptions**: Include context, requirements, acceptance criteria
   - Use Markdown for formatting
   - Add checklists for multi-step work
   - Include reproduction steps for bugs

3. **Appropriate Priority**: Reserve urgent for actual emergencies

4. **Accurate Estimates**: Help with capacity planning

5. **Meaningful Labels**: Use consistent labeling scheme

6. **Link Related Work**: Use parent_id for epics and sub-tasks

## Templates

### Feature Template

```python
def create_feature(title, requirements, acceptance_criteria):
    description = f"""
    # Requirements
    {chr(10).join(f'- {r}' for r in requirements)}

    # Acceptance Criteria
    {chr(10).join(f'- [ ] {c}' for c in acceptance_criteria)}
    """

    return LinearCreateIssue(
        title=title,
        description=description,
        team_id="team_id",
        labels=["feature"],
        priority=3
    )
```

### Bug Template

```python
def create_bug(title, steps, expected, actual, environment):
    description = f"""
    ## Steps to Reproduce
    {chr(10).join(f'{i+1}. {s}' for i, s in enumerate(steps))}

    ## Expected
    {expected}

    ## Actual
    {actual}

    ## Environment
    {environment}
    """

    return LinearCreateIssue(
        title=title,
        description=description,
        team_id="team_id",
        priority=2,
        labels=["bug"]
    )
```

## Testing

```bash
# Run tests
pytest tests/integrations/linear/test_linear_create_issue.py -v

# With coverage
pytest tests/integrations/linear/test_linear_create_issue.py --cov
```

## GraphQL Query

The tool uses this GraphQL mutation:

```graphql
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue {
      id
      identifier
      title
      url
      state { id name }
      team { id name }
      assignee { id name }
      priority
      estimate
      dueDate
      labels { nodes { id name } }
    }
  }
}
```

## See Also

- [LinearUpdateStatus](./linear_update_status_README.md) - Update existing issues
- [LinearAssignTeam](./linear_assign_team_README.md) - Assign issues to teams
- [Main README](./README.md) - Complete Linear integration guide
