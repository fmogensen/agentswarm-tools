# LinearSyncGitHub Tool

Bi-directional synchronization between Linear and GitHub for issues, pull requests, and project management with conflict resolution.

## Overview

Comprehensive Linear ↔ GitHub sync with:
- Bi-directional issue synchronization
- Pull request linking
- Status and label syncing
- Comment synchronization
- Automatic branch creation
- Conflict detection and resolution
- Batch operations

## Quick Start

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
print(f"Synced: {result['synced_count']} items")
```

## Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `sync_direction` | str | Direction: linear_to_github, github_to_linear, bidirectional |
| `github_repo` | str | GitHub repository (format: owner/repo) |

### Optional (context-dependent)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `linear_issue_id` | str | None | Linear issue ID (for single sync) |
| `github_issue_number` | int | None | GitHub issue number |
| `github_pr_number` | int | None | GitHub PR to link |
| `sync_comments` | bool | True | Sync comments |
| `sync_labels` | bool | True | Sync labels |
| `sync_status` | bool | True | Sync status/state |
| `create_branch` | bool | False | Auto-create GitHub branch |
| `conflict_resolution` | str | "linear_wins" | Conflict strategy: linear_wins, github_wins, manual |
| `label_mapping` | Dict | None | Custom label mapping |
| `batch_sync` | bool | False | Sync multiple issues |
| `batch_filters` | Dict | None | Filters for batch sync |

## Return Value

```python
{
    "success": True,
    "synced_count": 1,
    "sync_details": [
        {
            "linear_issue_id": "issue_abc123",
            "linear_identifier": "ENG-123",
            "github_issue_number": 42,
            "github_url": "https://github.com/company/project/issues/42",
            "sync_direction": "bidirectional",
            "changes_synced": ["title", "description", "labels", "status"],
            "conflicts": []
        }
    ],
    "conflicts": [],
    "created_items": {
        "branch": "linear/ENG-123-issue-title",
        "pr_link": "https://github.com/company/project/pull/156"
    },
    "metadata": {
        "tool_name": "linear_sync_github",
        "sync_direction": "bidirectional",
        "github_repo": "company/project"
    }
}
```

## Setup

### Environment Variables

```bash
# Required for Linear
export LINEAR_API_KEY=lin_api_xxxxx

# Required for GitHub
export GITHUB_TOKEN=ghp_xxxxx
```

### GitHub Token Scopes

Required scopes:
- `repo` - Full repository access
- `read:org` - Read organization data

## Examples

### Linear to GitHub (One-Way)

```python
# Create GitHub issue from Linear
tool = LinearSyncGitHub(
    sync_direction="linear_to_github",
    linear_issue_id="issue_abc123",
    github_repo="company/project",
    sync_labels=True,
    sync_comments=True
)

result = tool.run()
print(f"Created GitHub issue #{result['sync_details'][0]['github_issue_number']}")
```

### GitHub to Linear (One-Way)

```python
# Create Linear issue from GitHub
tool = LinearSyncGitHub(
    sync_direction="github_to_linear",
    github_issue_number=42,
    github_repo="company/project"
)

result = tool.run()
print(f"Created Linear issue: {result['sync_details'][0]['linear_identifier']}")
```

### Bidirectional Sync

```python
# Sync both directions
tool = LinearSyncGitHub(
    sync_direction="bidirectional",
    linear_issue_id="issue_abc123",
    github_issue_number=42,
    github_repo="company/project",
    sync_comments=True,
    sync_labels=True,
    sync_status=True
)

result = tool.run()
if result['conflicts']:
    print(f"Conflicts detected: {len(result['conflicts'])}")
```

### Link Pull Request

```python
# Link GitHub PR to Linear issue
tool = LinearSyncGitHub(
    sync_direction="linear_to_github",
    linear_issue_id="issue_abc123",
    github_repo="company/project",
    github_pr_number=156
)

result = tool.run()
print(f"Linked PR: {result['created_items']['pr_link']}")
```

### Create Branch Automatically

```python
# Create feature branch from Linear issue
tool = LinearSyncGitHub(
    sync_direction="linear_to_github",
    linear_issue_id="issue_abc123",
    github_repo="company/project",
    create_branch=True
)

result = tool.run()
print(f"Created branch: {result['created_items']['branch']}")
```

### Batch Sync

```python
# Sync all in-progress issues for team
tool = LinearSyncGitHub(
    sync_direction="linear_to_github",
    github_repo="company/project",
    batch_sync=True,
    batch_filters={
        "team_id": "team_engineering",
        "state": "In Progress"
    }
)

result = tool.run()
print(f"Synced {result['synced_count']} issues")
```

## Conflict Resolution

When syncing bidirectionally, conflicts may occur if both systems have changes:

### Linear Wins

```python
tool = LinearSyncGitHub(
    sync_direction="bidirectional",
    linear_issue_id="issue_abc",
    github_issue_number=42,
    github_repo="company/project",
    conflict_resolution="linear_wins"  # Linear overwrites GitHub
)
```

### GitHub Wins

```python
tool = LinearSyncGitHub(
    sync_direction="bidirectional",
    linear_issue_id="issue_abc",
    github_issue_number=42,
    github_repo="company/project",
    conflict_resolution="github_wins"  # GitHub overwrites Linear
)
```

### Manual Resolution

```python
tool = LinearSyncGitHub(
    sync_direction="bidirectional",
    linear_issue_id="issue_abc",
    github_issue_number=42,
    github_repo="company/project",
    conflict_resolution="manual"
)

result = tool.run()

# Review conflicts
for conflict in result['conflicts']:
    print(f"Field: {conflict['field']}")
    print(f"  Linear: {conflict['linear_value']}")
    print(f"  GitHub: {conflict['github_value']}")
    # Decide which to keep and sync again
```

## Label Mapping

Map Linear labels to different GitHub labels:

```python
tool = LinearSyncGitHub(
    sync_direction="linear_to_github",
    linear_issue_id="issue_abc",
    github_repo="company/project",
    label_mapping={
        "bug": "type: bug",
        "feature": "type: enhancement",
        "urgent": "priority: high",
        "low-priority": "priority: low"
    }
)
```

## Workflows

### Development Workflow

```python
# 1. Create Linear issue
from tools.integrations.linear import LinearCreateIssue

create = LinearCreateIssue(
    title="Add email notifications",
    team_id="team_backend",
    priority=2
)
issue = create.run()

# 2. Sync to GitHub and create branch
sync = LinearSyncGitHub(
    sync_direction="linear_to_github",
    linear_issue_id=issue['issue_id'],
    github_repo="company/api",
    create_branch=True
)
sync_result = sync.run()

# 3. Developer works on feature branch
# ...code changes...

# 4. Link PR when created
sync_pr = LinearSyncGitHub(
    sync_direction="linear_to_github",
    linear_issue_id=issue['issue_id'],
    github_repo="company/api",
    github_pr_number=158
)
sync_pr.run()
```

### Release Sync

```python
def sync_release_issues(team_id, sprint_id, github_repo):
    """Sync all completed sprint issues to GitHub for release notes"""

    from tools.integrations.linear import LinearGetRoadmap

    # Get completed issues
    roadmap = LinearGetRoadmap(
        team_id=team_id,
        status_filter="completed"
    )
    result = roadmap.run()

    # Sync each to GitHub
    for project in result['projects']:
        sync = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id=project['id'],
            github_repo=github_repo,
            sync_labels=True
        )
        sync.run()

    print(f"Synced {len(result['projects'])} issues for release")

sync_release_issues("team_eng", "sprint_12", "company/product")
```

## Best Practices

1. **Choose Direction**: Understand which system is source of truth
2. **Map Labels**: Create consistent labeling schemes
3. **Handle Conflicts**: Define strategy before syncing
4. **Batch Carefully**: Use filters to sync relevant issues
5. **Monitor Results**: Check sync_details for errors
6. **Automate Selectively**: Don't sync everything automatically

## Common Patterns

### One-Way Sync (Linear → GitHub)

Best for teams that plan in Linear, execute in GitHub:
- Create issues in Linear
- Auto-sync to GitHub
- Link PRs back to Linear

### One-Way Sync (GitHub → Linear)

Best for open-source projects:
- Community creates GitHub issues
- Auto-sync to Linear for triage
- Update Linear, sync back

### Bi-Directional Sync

Best for integrated workflows:
- Sync bidirectionally
- Define conflict resolution
- Monitor for conflicts

## Error Handling

```python
result = tool.run()

if not result['success']:
    error = result['error']

    if error['code'] == 'AUTH_ERROR':
        print("Check LINEAR_API_KEY and GITHUB_TOKEN")
    elif error['code'] == 'VALIDATION_ERROR':
        print(f"Invalid params: {error['message']}")
    elif error['code'] == 'API_ERROR':
        print(f"API error: {error['message']}")
```

## See Also

- [LinearCreateIssue](./linear_create_issue_README.md) - Create Linear issues
- [LinearUpdateStatus](./linear_update_status_README.md) - Update status
- [Main README](./README.md) - Complete Linear integration guide
