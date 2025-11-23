# LinearUpdateStatus Tool

Update Linear issue status, transitions, priorities, assignees, and labels with workflow validation.

## Overview

Update existing Linear issues with support for:
- Workflow state transitions
- Status updates by name or ID
- Priority and estimate changes
- Assignee management
- Label additions and removals
- Comment addition with updates

## Quick Start

```python
from tools.integrations.linear import LinearUpdateStatus

tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    state_name="In Progress",
    assignee_id="user_xyz789",
    priority=2,
    comment="Starting work on this feature"
)

result = tool.run()
print(f"{result['previous_state']} → {result['new_state']}")
```

## Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `issue_id` | str | Linear issue ID |

### Optional (at least one required)

| Parameter | Type | Description |
|-----------|------|-------------|
| `state_id` | str | New workflow state ID |
| `state_name` | str | State name (alternative to state_id) |
| `priority` | int | New priority (0-4) |
| `assignee_id` | str | New assignee (use "unassign" to remove) |
| `estimate` | float | New estimate value |
| `add_labels` | List[str] | Label IDs to add |
| `remove_labels` | List[str] | Label IDs to remove |
| `comment` | str | Comment to add with update |

## Return Value

```python
{
    "success": True,
    "issue_id": "issue_abc123",
    "issue_identifier": "ENG-123",
    "previous_state": "Todo",
    "new_state": "In Progress",
    "transition_valid": True,
    "metadata": {
        "tool_name": "linear_update_status",
        "updates_applied": {
            "state": "In Progress",
            "priority": 2,
            "assignee": "user_xyz789"
        }
    }
}
```

## Examples

### Update State

```python
# By state name
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    state_name="In Progress"
)

# By state ID
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    state_id="state_xyz789"
)
```

### Change Priority

```python
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    priority=1,  # Urgent
    comment="Escalating to urgent due to customer impact"
)
```

### Reassign Issue

```python
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    assignee_id="user_bob",
    comment="Reassigning to Bob for backend expertise"
)

# Unassign
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    assignee_id="unassign"
)
```

### Update Estimate

```python
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    estimate=8.0,
    comment="Revised estimate after investigation"
)
```

### Manage Labels

```python
# Add labels
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    add_labels=["bug", "urgent"]
)

# Remove labels
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    remove_labels=["backlog"]
)

# Add and remove simultaneously
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    add_labels=["in-progress"],
    remove_labels=["todo", "backlog"]
)
```

### Multiple Updates

```python
tool = LinearUpdateStatus(
    issue_id="issue_abc123",
    state_name="In Progress",
    priority=2,
    assignee_id="user_alice",
    estimate=5.0,
    add_labels=["backend"],
    comment="Alice starting work this sprint"
)
```

## Common Workflow States

| State | Description |
|-------|-------------|
| Todo | Ready to start |
| In Progress | Actively being worked on |
| In Review | Under code review |
| Done | Completed |
| Canceled | Not proceeding with issue |

Note: Exact states depend on your team's workflow configuration.

## Best Practices

1. **Add Context**: Always include comments explaining status changes
2. **Update Estimates**: Revise estimates as work progresses
3. **Manage Assignees**: Update when handoffs occur
4. **Use Transitions**: Follow valid state transitions for your workflow
5. **Clean Labels**: Remove outdated labels when status changes

## Error Handling

```python
result = tool.run()

if not result['success']:
    error = result['error']
    if error['code'] == 'VALIDATION_ERROR':
        print(f"Invalid update: {error['message']}")
```

## State Resolution

The tool automatically resolves state names to IDs:

```python
# These are equivalent if "In Progress" exists
tool = LinearUpdateStatus(issue_id="id", state_name="In Progress")
# Internally resolves to:
# tool = LinearUpdateStatus(issue_id="id", state_id="state_resolved_id")
```

## See Also

- [LinearCreateIssue](./linear_create_issue_README.md) - Create new issues
- [LinearAssignTeam](./linear_assign_team_README.md) - Team assignment
- [Main README](./README.md) - Complete Linear integration guide
