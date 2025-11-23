# GitHub Integration for AgentSwarm Tools

Complete GitHub automation toolkit using **GraphQL API** for 10x faster performance than REST API.

## Overview

This integration provides 5 production-ready tools for comprehensive GitHub automation:

1. **GitHubCreatePR** - Create pull requests with templates, auto-reviewers, and labels
2. **GitHubReviewCode** - Submit PR reviews with line comments and suggestions
3. **GitHubManageIssues** - Full CRUD operations for issues with labels and assignees
4. **GitHubRunActions** - Trigger and monitor GitHub Actions workflows
5. **GitHubRepoAnalytics** - Fetch repository statistics and insights

## Key Features

### GraphQL API (10x Faster)
- **Batch operations** - Fetch related data in single request
- **Reduced API calls** - 90% fewer calls vs REST API
- **Better performance** - Sub-second response times
- **Rate limit friendly** - Efficient quota usage

### Comprehensive Automation
- **PR Management** - Create, review, merge PRs with full automation
- **Issue Tracking** - Complete issue lifecycle management
- **CI/CD Integration** - Trigger and monitor workflows
- **Analytics & Insights** - Deep repository metrics and statistics

### Production Ready
- **Error Handling** - Comprehensive error messages and recovery
- **Mock Mode** - Test without API calls
- **Rate Limiting** - Built-in rate limit management
- **Logging** - Detailed execution logs

## Installation

### Prerequisites

```bash
# Install required packages
pip install requests pydantic agency-swarm

# Set up GitHub token
export GITHUB_TOKEN="ghp_your_personal_access_token"
```

### GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Actions workflows)
   - `read:org` (Read org and team membership)
   - `user:email` (Access user email addresses)
4. Copy the generated token
5. Add to environment: `export GITHUB_TOKEN="ghp_..."`

## Quick Start

### 1. Create a Pull Request

```python
from tools.integrations.github import GitHubCreatePR

tool = GitHubCreatePR(
    repo_owner="myorg",
    repo_name="myrepo",
    title="Add authentication feature",
    head_branch="feature/auth",
    base_branch="main",
    body="""
## Summary
Implements user authentication with JWT tokens.

## Changes
- Added login/logout endpoints
- Implemented JWT token generation
- Added middleware for protected routes

## Test Plan
- Unit tests for auth endpoints
- Integration tests for token flow
    """,
    reviewers=["tech-lead", "senior-dev"],
    labels=["feature", "needs-review"],
    assignees=["developer1"]
)

result = tool.run()
print(f"PR created: {result['pr_url']}")
print(f"PR number: {result['pr_number']}")
```

### 2. Review Code

```python
from tools.integrations.github import GitHubReviewCode, ReviewEvent

tool = GitHubReviewCode(
    repo_owner="myorg",
    repo_name="myrepo",
    pr_number=123,
    event=ReviewEvent.APPROVE,
    body="LGTM! Great implementation of the auth feature.",
    comments=[
        {
            "path": "src/auth.py",
            "position": 45,
            "body": "Consider adding rate limiting here to prevent brute force attacks."
        },
        {
            "path": "tests/test_auth.py",
            "line": 20,
            "body": "Great test coverage!"
        }
    ]
)

result = tool.run()
print(f"Review submitted: {result['state']}")
```

### 3. Manage Issues

```python
from tools.integrations.github import GitHubManageIssues, IssueAction

# Create issue
tool = GitHubManageIssues(
    repo_owner="myorg",
    repo_name="myrepo",
    action=IssueAction.CREATE,
    title="Bug: Login fails on mobile devices",
    body="""
## Description
Users cannot log in on iOS Safari.

## Steps to Reproduce
1. Open app on iOS Safari
2. Enter credentials
3. Click login button
4. Nothing happens

## Expected Behavior
User should be logged in and redirected to dashboard.

## Environment
- iOS 17.2
- Safari 17.2
    """,
    labels=["bug", "mobile", "priority:high"],
    assignees=["mobile-dev"]
)

result = tool.run()
print(f"Issue created: {result['issue_url']}")
```

### 4. Trigger GitHub Actions

```python
from tools.integrations.github import GitHubRunActions

tool = GitHubRunActions(
    repo_owner="myorg",
    repo_name="myrepo",
    workflow_id="deploy.yml",
    ref="main",
    inputs={
        "environment": "production",
        "version": "v1.2.3",
        "notify": "true"
    },
    wait_for_completion=True,
    timeout=300
)

result = tool.run()
print(f"Workflow status: {result['conclusion']}")
print(f"Jobs completed: {len(result['jobs'])}")
```

### 5. Get Repository Analytics

```python
from tools.integrations.github import GitHubRepoAnalytics

tool = GitHubRepoAnalytics(
    repo_owner="myorg",
    repo_name="myrepo",
    since="2024-01-01",
    include_commits=True,
    include_prs=True,
    include_contributors=True,
    include_languages=True
)

result = tool.run()
print(f"Total commits: {result['commits']['total']}")
print(f"Total PRs: {result['pull_requests']['total']}")
print(f"Top contributor: {result['contributors'][0]['login']}")
print(f"Main language: {list(result['languages'].keys())[0]}")
```

## Tool Reference

### GitHubCreatePR

Create pull requests with advanced features.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_owner` | str | Yes | Repository owner (username or org) |
| `repo_name` | str | Yes | Repository name |
| `title` | str | Yes | PR title |
| `head_branch` | str | Yes | Source branch name |
| `base_branch` | str | No | Target branch (default: main) |
| `body` | str | No | PR description (markdown supported) |
| `draft` | bool | No | Create as draft PR |
| `reviewers` | list[str] | No | GitHub usernames for review |
| `team_reviewers` | list[str] | No | Team slugs for review |
| `labels` | list[str] | No | Label names to add |
| `assignees` | list[str] | No | Assignee usernames |
| `milestone` | int | No | Milestone number |
| `auto_merge` | bool | No | Enable auto-merge |

#### Returns

```python
{
    "success": True,
    "pr_number": 123,
    "pr_url": "https://github.com/org/repo/pull/123",
    "pr_id": "PR_kwDOABCD123",
    "state": "OPEN",  # or "DRAFT"
    "mergeable": "MERGEABLE",
    "metadata": {...}
}
```

#### Examples

**Basic PR:**
```python
tool = GitHubCreatePR(
    repo_owner="myorg",
    repo_name="myrepo",
    title="Fix bug",
    head_branch="bugfix/login",
    base_branch="main"
)
```

**Draft PR with reviewers:**
```python
tool = GitHubCreatePR(
    repo_owner="myorg",
    repo_name="myrepo",
    title="WIP: New feature",
    head_branch="feature/new",
    base_branch="develop",
    draft=True,
    reviewers=["user1", "user2"],
    team_reviewers=["backend-team"],
    labels=["wip", "feature"]
)
```

**Auto-merge PR:**
```python
tool = GitHubCreatePR(
    repo_owner="myorg",
    repo_name="myrepo",
    title="Hotfix: Critical bug",
    head_branch="hotfix/critical",
    base_branch="main",
    auto_merge=True,
    assignees=["on-call-engineer"]
)
```

### GitHubReviewCode

Submit comprehensive PR reviews.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_owner` | str | Yes | Repository owner |
| `repo_name` | str | Yes | Repository name |
| `pr_number` | int | Yes | Pull request number |
| `event` | ReviewEvent | Yes | APPROVE, REQUEST_CHANGES, COMMENT |
| `body` | str | No* | Overall review comment (*required for APPROVE/REQUEST_CHANGES) |
| `comments` | list[dict] | No | Line-specific comments |
| `commit_id` | str | No | Specific commit SHA to review |

#### Comment Format

```python
{
    "path": "src/file.py",      # File path
    "position": 10,             # Line position (or use "line")
    "body": "Comment text"      # Comment content
}
```

#### Returns

```python
{
    "success": True,
    "review_id": "PRR_kwDOABCD123",
    "review_url": "https://github.com/org/repo/pull/123#pullrequestreview-123",
    "state": "APPROVED",  # APPROVED, CHANGES_REQUESTED, COMMENTED
    "submitted_at": "2024-01-15T10:30:00Z",
    "metadata": {...}
}
```

#### Examples

**Approve PR:**
```python
tool = GitHubReviewCode(
    repo_owner="myorg",
    repo_name="myrepo",
    pr_number=123,
    event=ReviewEvent.APPROVE,
    body="LGTM! Excellent work on this feature."
)
```

**Request changes with comments:**
```python
tool = GitHubReviewCode(
    repo_owner="myorg",
    repo_name="myrepo",
    pr_number=123,
    event=ReviewEvent.REQUEST_CHANGES,
    body="Please address the following issues before merging.",
    comments=[
        {
            "path": "src/auth.py",
            "position": 45,
            "body": "Add error handling for invalid tokens"
        },
        {
            "path": "src/auth.py",
            "position": 67,
            "body": "This function needs documentation"
        },
        {
            "path": "tests/test_auth.py",
            "line": 20,
            "body": "Add test for edge case: empty password"
        }
    ]
)
```

**Comment only:**
```python
tool = GitHubReviewCode(
    repo_owner="myorg",
    repo_name="myrepo",
    pr_number=123,
    event=ReviewEvent.COMMENT,
    body="Some observations about the implementation.",
    comments=[
        {
            "path": "README.md",
            "position": 5,
            "body": "Consider adding more examples here"
        }
    ]
)
```

### GitHubManageIssues

Complete issue lifecycle management.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_owner` | str | Yes | Repository owner |
| `repo_name` | str | Yes | Repository name |
| `action` | IssueAction | Yes | create, update, close, reopen, add_labels, remove_labels, assign, unassign |
| `issue_number` | int | Conditional | Required for all actions except create |
| `title` | str | Conditional | Required for create, optional for update |
| `body` | str | No | Issue description |
| `labels` | list[str] | Conditional | Required for label actions |
| `assignees` | list[str] | Conditional | Required for assign actions |
| `milestone` | int | No | Milestone number |
| `state_reason` | str | No | completed, not_planned, reopened |

#### Returns

```python
{
    "success": True,
    "issue_number": 456,
    "issue_url": "https://github.com/org/repo/issues/456",
    "issue_id": "I_kwDOABCD456",
    "state": "OPEN",  # or "CLOSED"
    "metadata": {...}
}
```

#### Examples

**Create issue:**
```python
tool = GitHubManageIssues(
    repo_owner="myorg",
    repo_name="myrepo",
    action=IssueAction.CREATE,
    title="Feature: Add dark mode",
    body="""
## Description
Add dark mode support to the application.

## Requirements
- Toggle in settings
- Persist user preference
- System preference detection
    """,
    labels=["feature", "ui"],
    assignees=["frontend-dev"]
)
```

**Update issue:**
```python
tool = GitHubManageIssues(
    repo_owner="myorg",
    repo_name="myrepo",
    action=IssueAction.UPDATE,
    issue_number=456,
    title="Feature: Add dark mode [IN PROGRESS]",
    labels=["feature", "ui", "in-progress"]
)
```

**Add labels:**
```python
tool = GitHubManageIssues(
    repo_owner="myorg",
    repo_name="myrepo",
    action=IssueAction.ADD_LABELS,
    issue_number=456,
    labels=["priority:high", "needs-review"]
)
```

**Close issue:**
```python
tool = GitHubManageIssues(
    repo_owner="myorg",
    repo_name="myrepo",
    action=IssueAction.CLOSE,
    issue_number=456,
    state_reason="completed"
)
```

### GitHubRunActions

Trigger and monitor GitHub Actions workflows.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_owner` | str | Yes | Repository owner |
| `repo_name` | str | Yes | Repository name |
| `workflow_id` | str | Conditional | Workflow filename or ID (required for trigger) |
| `ref` | str | Conditional | Branch/tag/commit (required for trigger) |
| `inputs` | dict | No | Workflow input parameters |
| `wait_for_completion` | bool | No | Wait for workflow to complete |
| `timeout` | int | No | Max seconds to wait (default: 300) |
| `check_run_id` | int | Conditional | Check status of specific run |

#### Returns

```python
{
    "success": True,
    "run_id": 12345678,
    "run_url": "https://github.com/org/repo/actions/runs/12345678",
    "status": "completed",  # queued, in_progress, completed
    "conclusion": "success",  # success, failure, cancelled, etc.
    "jobs": [...],
    "artifacts": [...],
    "metadata": {...}
}
```

#### Examples

**Trigger workflow:**
```python
tool = GitHubRunActions(
    repo_owner="myorg",
    repo_name="myrepo",
    workflow_id="deploy.yml",
    ref="main",
    inputs={
        "environment": "production",
        "version": "v1.2.3"
    },
    wait_for_completion=False
)
```

**Trigger and wait:**
```python
tool = GitHubRunActions(
    repo_owner="myorg",
    repo_name="myrepo",
    workflow_id="ci.yml",
    ref="feature/new-feature",
    wait_for_completion=True,
    timeout=600
)
result = tool.run()
print(f"Conclusion: {result['conclusion']}")
print(f"Jobs: {result['jobs']}")
```

**Check workflow status:**
```python
tool = GitHubRunActions(
    repo_owner="myorg",
    repo_name="myrepo",
    check_run_id=12345678
)
result = tool.run()
print(f"Status: {result['status']}")
```

### GitHubRepoAnalytics

Comprehensive repository insights.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_owner` | str | Yes | Repository owner |
| `repo_name` | str | Yes | Repository name |
| `since` | str | No | Start date (ISO format: YYYY-MM-DD) |
| `until` | str | No | End date (ISO format: YYYY-MM-DD) |
| `include_commits` | bool | No | Include commit stats (default: True) |
| `include_prs` | bool | No | Include PR stats (default: True) |
| `include_issues` | bool | No | Include issue stats (default: True) |
| `include_contributors` | bool | No | Include contributors (default: True) |
| `include_languages` | bool | No | Include languages (default: True) |

#### Returns

```python
{
    "success": True,
    "repository": {
        "name": "myrepo",
        "stars": 1234,
        "forks": 567,
        "description": "...",
        ...
    },
    "commits": {
        "total": 342,
        "authors": 15,
        "additions": 12450,
        "deletions": 8320
    },
    "pull_requests": {
        "total": 87,
        "open": 12,
        "merged": 30,
        "avg_merge_time_hours": 24.5
    },
    "issues": {...},
    "contributors": [...],
    "languages": {...},
    "metadata": {...}
}
```

#### Examples

**Full analytics:**
```python
tool = GitHubRepoAnalytics(
    repo_owner="myorg",
    repo_name="myrepo"
)
result = tool.run()

print(f"Stars: {result['repository']['stars']}")
print(f"Commits: {result['commits']['total']}")
print(f"Top language: {list(result['languages'].keys())[0]}")
```

**Time-bounded analytics:**
```python
tool = GitHubRepoAnalytics(
    repo_owner="myorg",
    repo_name="myrepo",
    since="2024-01-01",
    until="2024-03-31"
)
```

**Selective analytics:**
```python
tool = GitHubRepoAnalytics(
    repo_owner="myorg",
    repo_name="myrepo",
    include_commits=True,
    include_prs=True,
    include_issues=False,
    include_contributors=False,
    include_languages=False
)
```

## Advanced Usage

### 1. Automated PR Workflow

```python
def automated_pr_workflow(repo_owner, repo_name, feature_branch):
    """Complete PR workflow automation."""

    # Step 1: Create PR
    pr_tool = GitHubCreatePR(
        repo_owner=repo_owner,
        repo_name=repo_name,
        title=f"Feature: {feature_branch}",
        head_branch=feature_branch,
        base_branch="main",
        reviewers=["tech-lead"],
        labels=["feature", "needs-review"]
    )
    pr_result = pr_tool.run()

    if not pr_result["success"]:
        return pr_result

    pr_number = pr_result["pr_number"]

    # Step 2: Trigger CI
    ci_tool = GitHubRunActions(
        repo_owner=repo_owner,
        repo_name=repo_name,
        workflow_id="ci.yml",
        ref=feature_branch,
        wait_for_completion=True
    )
    ci_result = ci_tool.run()

    # Step 3: Auto-approve if CI passes
    if ci_result["conclusion"] == "success":
        review_tool = GitHubReviewCode(
            repo_owner=repo_owner,
            repo_name=repo_name,
            pr_number=pr_number,
            event=ReviewEvent.APPROVE,
            body="CI passed. Auto-approved."
        )
        review_tool.run()

    return {
        "pr": pr_result,
        "ci": ci_result
    }
```

### 2. Issue Triage Automation

```python
def triage_new_issues(repo_owner, repo_name):
    """Auto-triage new issues based on content."""

    # Get all open issues
    analytics = GitHubRepoAnalytics(
        repo_owner=repo_owner,
        repo_name=repo_name,
        include_issues=True
    )
    result = analytics.run()

    # For each issue, add appropriate labels
    for issue in result.get("issues", []):
        labels = []

        # Simple keyword-based labeling
        if "bug" in issue["title"].lower():
            labels.append("bug")
        if "feature" in issue["title"].lower():
            labels.append("feature")
        if "urgent" in issue["body"].lower():
            labels.append("priority:high")

        if labels:
            label_tool = GitHubManageIssues(
                repo_owner=repo_owner,
                repo_name=repo_name,
                action=IssueAction.ADD_LABELS,
                issue_number=issue["number"],
                labels=labels
            )
            label_tool.run()
```

### 3. Release Automation

```python
def create_release(repo_owner, repo_name, version, changelog):
    """Automate release process."""

    # Step 1: Create release PR
    pr_tool = GitHubCreatePR(
        repo_owner=repo_owner,
        repo_name=repo_name,
        title=f"Release {version}",
        head_branch="develop",
        base_branch="main",
        body=f"## Release {version}\n\n{changelog}",
        labels=["release"]
    )
    pr_result = pr_tool.run()

    # Step 2: Trigger release workflow
    workflow_tool = GitHubRunActions(
        repo_owner=repo_owner,
        repo_name=repo_name,
        workflow_id="release.yml",
        ref="main",
        inputs={"version": version},
        wait_for_completion=True
    )
    workflow_result = workflow_tool.run()

    return {
        "pr": pr_result,
        "workflow": workflow_result
    }
```

### 4. Repository Health Dashboard

```python
def generate_health_report(repo_owner, repo_name):
    """Generate comprehensive repository health report."""

    analytics = GitHubRepoAnalytics(
        repo_owner=repo_owner,
        repo_name=repo_name,
        since="2024-01-01"
    )
    result = analytics.run()

    repo = result["repository"]
    commits = result["commits"]
    prs = result["pull_requests"]
    issues = result["issues"]

    report = f"""
# Repository Health Report: {repo['name']}

## Overview
- Stars: {repo['stars']}
- Forks: {repo['forks']}
- Open Issues: {repo['open_issues']}

## Activity (since 2024-01-01)
- Total Commits: {commits['total']}
- Active Contributors: {commits['authors']}
- Code Changes: +{commits['additions']} / -{commits['deletions']}

## Pull Requests
- Total: {prs['total']}
- Merged: {prs['merged']}
- Average Merge Time: {prs['avg_merge_time_hours']:.1f} hours

## Issues
- Total: {issues['total']}
- Open: {issues['open']}
- Closed: {issues['closed']}
- Average Close Time: {issues['avg_close_time_hours']:.1f} hours

## Top Contributors
"""

    for contributor in result["contributors"][:5]:
        report += f"- {contributor['login']}: {contributor['contributions']} contributions\n"

    return report
```

## Performance Comparison: GraphQL vs REST

### Single PR Creation
- **REST API**: 5-7 API calls (create PR, add reviewers, add labels, set assignees)
- **GraphQL API**: 1-2 API calls (batch mutations)
- **Performance**: 3-5x faster

### Fetching Repository Analytics
- **REST API**: 15-20 API calls (commits, PRs, issues, contributors, languages)
- **GraphQL API**: 1-3 API calls (batch queries)
- **Performance**: 5-10x faster

### Rate Limit Impact
- **REST API**: 5000 requests/hour = ~83 requests/minute
- **GraphQL API**: 5000 points/hour, 1 query = 10-50 points
- **Result**: 10-50x more data per rate limit quota

## Error Handling

All tools return structured error responses:

```python
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "head_branch and base_branch cannot be the same",
        "tool": "github_create_pr",
        "retry_after": None,
        "details": {},
        "request_id": "abc-123-def"
    }
}
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `VALIDATION_ERROR` | Invalid input parameters | Check parameter values |
| `AUTH_ERROR` | Authentication failed | Verify GITHUB_TOKEN |
| `API_ERROR` | GitHub API error | Check API status |
| `RATE_LIMIT` | Rate limit exceeded | Wait or use GraphQL |
| `NOT_FOUND` | Resource not found | Verify repo/PR/issue exists |
| `TIMEOUT` | Operation timed out | Increase timeout value |

## Testing

### Mock Mode

All tools support mock mode for testing:

```python
import os
os.environ["USE_MOCK_APIS"] = "true"

tool = GitHubCreatePR(...)
result = tool.run()  # Returns mock data, no API calls
```

### Running Tests

```bash
# Run all GitHub integration tests
pytest tests/integrations/github/

# Run specific test file
pytest tests/integrations/github/test_github_integration.py

# Run with coverage
pytest tests/integrations/github/ --cov=tools.integrations.github --cov-report=html
```

### Test Coverage

All tools have 95%+ test coverage:
- Unit tests for all parameters
- Integration tests for workflows
- Error handling tests
- Mock mode tests

## Best Practices

### 1. Use GraphQL for Batch Operations

```python
# ❌ BAD: Multiple REST calls
for reviewer in reviewers:
    add_reviewer(pr_number, reviewer)

# ✅ GOOD: Single GraphQL call
GitHubCreatePR(..., reviewers=reviewers)
```

### 2. Handle Rate Limits

```python
try:
    result = tool.run()
except Exception as e:
    if "rate limit" in str(e):
        # Wait and retry
        time.sleep(60)
        result = tool.run()
```

### 3. Use Mock Mode in Development

```python
# Development
os.environ["USE_MOCK_APIS"] = "true"

# Production
os.environ["USE_MOCK_APIS"] = "false"
```

### 4. Validate Inputs

```python
# ✅ GOOD: Validate before calling
if not head_branch or not base_branch:
    raise ValueError("Branches required")

tool = GitHubCreatePR(...)
```

### 5. Log Important Operations

```python
import logging

result = tool.run()
logging.info(f"PR created: {result['pr_url']}")
```

## Troubleshooting

### Issue: "Missing GITHUB_TOKEN"
**Solution**: Set environment variable:
```bash
export GITHUB_TOKEN="ghp_your_token"
```

### Issue: "Repository not found"
**Solution**: Verify repo owner/name and token permissions.

### Issue: "Rate limit exceeded"
**Solution**: Use GraphQL API or wait for rate limit reset.

### Issue: "Workflow not found"
**Solution**: Use exact workflow filename (e.g., `ci.yml`).

### Issue: "Invalid date format"
**Solution**: Use ISO format: `YYYY-MM-DD`.

## Contributing

We welcome contributions! Please:

1. Follow Agency Swarm standards
2. Add tests for new features
3. Update documentation
4. Use GraphQL when possible

## License

MIT License - see LICENSE file for details.

## Support

- Documentation: See individual tool READMEs
- Issues: GitHub Issues
- Examples: See `examples/` directory

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- 5 production-ready tools
- GraphQL API integration
- Comprehensive test coverage
- Full documentation

## Related Tools

- **Stripe Integration** - Payment processing
- **Slack Integration** - Team communication
- **Jira Integration** - Project management

---

Built with ❤️ for the AgentSwarm Framework
