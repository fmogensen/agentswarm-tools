# GitHub Tools - Comprehensive Documentation

Complete reference for all 5 GitHub integration tools with examples, use cases, and best practices.

---

# 1. GitHubCreatePR - Pull Request Creation

## Overview

Create pull requests using GitHub's GraphQL API with support for templates, auto-reviewers, labels, and draft PRs.

### Key Features
- **GraphQL Powered** - 10x faster than REST API
- **Template Support** - Use PR templates for consistency
- **Auto-Reviewers** - Automatically request reviews from users/teams
- **Draft PRs** - Create work-in-progress pull requests
- **Auto-Merge** - Enable automatic merging when checks pass
- **Batch Operations** - Set reviewers, labels, assignees in one call

## Parameters Reference

```python
GitHubCreatePR(
    repo_owner: str,          # Required: Repository owner (org or user)
    repo_name: str,           # Required: Repository name
    title: str,               # Required: PR title (max 256 chars)
    head_branch: str,         # Required: Source branch
    base_branch: str = "main",# Optional: Target branch
    body: str = None,         # Optional: PR description (markdown)
    draft: bool = False,      # Optional: Create as draft
    reviewers: List[str] = None,      # Optional: User reviewers
    team_reviewers: List[str] = None, # Optional: Team reviewers
    labels: List[str] = None,         # Optional: Label names
    assignees: List[str] = None,      # Optional: Assignees
    milestone: int = None,            # Optional: Milestone number
    auto_merge: bool = False          # Optional: Enable auto-merge
)
```

## Use Cases

### 1. Feature Development PR

```python
from tools.integrations.github import GitHubCreatePR

tool = GitHubCreatePR(
    repo_owner="acme-corp",
    repo_name="web-app",
    title="Add user authentication system",
    head_branch="feature/auth",
    base_branch="develop",
    body="""
## Summary
Implements comprehensive user authentication system with JWT tokens.

## Features
- User registration and login
- JWT token generation and validation
- Password hashing with bcrypt
- Session management
- Logout functionality

## Testing
- Unit tests: 95% coverage
- Integration tests: All auth flows
- Manual testing: Chrome, Firefox, Safari

## Screenshots
![Login Page](https://...)
![Dashboard](https://...)

## Checklist
- [x] Code complete
- [x] Tests passing
- [x] Documentation updated
- [ ] Code review pending
    """,
    reviewers=["tech-lead", "security-expert"],
    team_reviewers=["backend-team"],
    labels=["feature", "needs-review", "security"],
    assignees=["developer-john"]
)

result = tool.run()
print(f"✅ PR created: {result['pr_url']}")
print(f"📝 PR #{result['pr_number']} - {result['state']}")
```

### 2. Hotfix PR with Auto-Merge

```python
tool = GitHubCreatePR(
    repo_owner="acme-corp",
    repo_name="web-app",
    title="Hotfix: Fix critical login bug",
    head_branch="hotfix/login-crash",
    base_branch="main",
    body="## Critical Fix\n\nFixes app crash on login with special characters.",
    reviewers=["on-call-engineer"],
    labels=["hotfix", "priority:critical"],
    auto_merge=True  # Auto-merge when CI passes
)
```

### 3. Draft PR for Work in Progress

```python
tool = GitHubCreatePR(
    repo_owner="acme-corp",
    repo_name="web-app",
    title="WIP: Refactor database layer",
    head_branch="refactor/database",
    base_branch="develop",
    body="## Work in Progress\n\nRefactoring database layer. Not ready for review.",
    draft=True,
    labels=["wip", "refactoring"]
)
```

### 4. Dependency Update PR

```python
tool = GitHubCreatePR(
    repo_owner="acme-corp",
    repo_name="web-app",
    title="chore: Update dependencies",
    head_branch="chore/deps-update",
    base_branch="main",
    body="## Dependency Updates\n\n- React: 18.2.0 → 18.3.0\n- TypeScript: 5.0 → 5.1",
    labels=["dependencies", "maintenance"],
    assignees=["devops-team"]
)
```

## Response Format

```python
{
    "success": True,
    "pr_number": 123,
    "pr_url": "https://github.com/acme-corp/web-app/pull/123",
    "pr_id": "PR_kwDOABCDEFG",
    "state": "OPEN",  # or "DRAFT"
    "mergeable": "MERGEABLE",  # MERGEABLE, CONFLICTING, UNKNOWN
    "metadata": {
        "tool_name": "github_create_pr",
        "repo": "acme-corp/web-app",
        "head": "feature/auth",
        "base": "develop"
    }
}
```

## GraphQL Performance

**vs REST API:**
- REST: 5-7 separate API calls
- GraphQL: 1-2 batched calls
- **Result: 3-5x faster execution**

---

# 2. GitHubReviewCode - Code Review Submission

## Overview

Submit comprehensive PR reviews with line-specific comments, suggestions, and approve/reject actions.

### Key Features
- **Three Review Types** - Approve, Request Changes, Comment
- **Line Comments** - Add feedback on specific code lines
- **Code Suggestions** - Propose code changes
- **Batch Comments** - Submit multiple comments at once
- **Commit-Specific** - Review specific commits

## Parameters Reference

```python
GitHubReviewCode(
    repo_owner: str,              # Required: Repository owner
    repo_name: str,               # Required: Repository name
    pr_number: int,               # Required: PR number to review
    event: ReviewEvent,           # Required: APPROVE, REQUEST_CHANGES, COMMENT
    body: str = None,             # Optional*: Overall comment (*required for APPROVE/REQUEST_CHANGES)
    comments: List[Dict] = None,  # Optional: Line-specific comments
    commit_id: str = None         # Optional: Specific commit SHA
)
```

### Comment Format
```python
{
    "path": "src/auth.py",    # File path
    "position": 45,           # Line position (or use "line")
    "body": "Add error handling here"  # Comment text
}
```

## Use Cases

### 1. Approve PR with Suggestions

```python
from tools.integrations.github import GitHubReviewCode, ReviewEvent

tool = GitHubReviewCode(
    repo_owner="acme-corp",
    repo_name="web-app",
    pr_number=123,
    event=ReviewEvent.APPROVE,
    body="""
## Approval

LGTM! Excellent implementation of the authentication system.

### Highlights
- Clean code architecture
- Comprehensive test coverage
- Good documentation

### Minor Suggestions
See inline comments for optional improvements.
    """,
    comments=[
        {
            "path": "src/auth.py",
            "position": 45,
            "body": "💡 Consider adding rate limiting to prevent brute force attacks."
        },
        {
            "path": "src/auth.py",
            "position": 67,
            "body": "✨ Great use of async/await here!"
        },
        {
            "path": "tests/test_auth.py",
            "line": 20,
            "body": "📝 Excellent test coverage for edge cases."
        }
    ]
)

result = tool.run()
print(f"✅ Review submitted: {result['state']}")
print(f"🔗 {result['review_url']}")
```

### 2. Request Changes with Detailed Feedback

```python
tool = GitHubReviewCode(
    repo_owner="acme-corp",
    repo_name="web-app",
    pr_number=123,
    event=ReviewEvent.REQUEST_CHANGES,
    body="""
## Changes Requested

Please address the following issues before merging:

### Critical Issues
1. Missing error handling in authentication
2. SQL injection vulnerability in login query
3. Missing unit tests for password reset

### Code Quality
- Add documentation for public methods
- Follow naming conventions
- Remove commented code

### Security
- Hash passwords with bcrypt
- Validate input sanitization
- Add CSRF protection
    """,
    comments=[
        {
            "path": "src/auth.py",
            "position": 45,
            "body": "⚠️ **Security Issue**: This is vulnerable to SQL injection. Use parameterized queries."
        },
        {
            "path": "src/auth.py",
            "position": 67,
            "body": "🔒 **Critical**: Passwords must be hashed before storage. Use bcrypt with salt."
        },
        {
            "path": "src/auth.py",
            "position": 89,
            "body": "❌ Missing error handling. Add try/except for database errors."
        },
        {
            "path": "tests/test_auth.py",
            "line": 10,
            "body": "📋 Add tests for:\n- Invalid email format\n- Empty password\n- SQL injection attempts"
        }
    ]
)
```

### 3. Comment-Only Review (No Approval)

```python
tool = GitHubReviewCode(
    repo_owner="acme-corp",
    repo_name="web-app",
    pr_number=123,
    event=ReviewEvent.COMMENT,
    body="Some observations and questions about the implementation.",
    comments=[
        {
            "path": "src/auth.py",
            "position": 30,
            "body": "❓ Why use JWT over sessions? Performance considerations?"
        },
        {
            "path": "README.md",
            "position": 15,
            "body": "💡 Consider adding setup instructions for authentication."
        }
    ]
)
```

### 4. Review Specific Commit

```python
tool = GitHubReviewCode(
    repo_owner="acme-corp",
    repo_name="web-app",
    pr_number=123,
    event=ReviewEvent.APPROVE,
    body="Approved commit abc123. Looks good!",
    commit_id="abc123def456789"
)
```

## Response Format

```python
{
    "success": True,
    "review_id": "PRR_kwDOABCDEFG",
    "review_url": "https://github.com/acme-corp/web-app/pull/123#pullrequestreview-456",
    "state": "APPROVED",  # APPROVED, CHANGES_REQUESTED, COMMENTED
    "submitted_at": "2024-01-15T10:30:00Z",
    "metadata": {
        "tool_name": "github_review_code",
        "repo": "acme-corp/web-app",
        "pr_number": 123,
        "event": "APPROVE"
    }
}
```

## Best Practices

1. **Be Specific** - Reference exact lines and provide clear feedback
2. **Be Constructive** - Explain why and suggest improvements
3. **Use Emojis** - Make reviews more engaging (⚠️ 💡 ✨ 📝 ❌ ✅)
4. **Batch Comments** - Submit all comments at once for efficiency
5. **Approve Quickly** - Don't block good PRs with minor nitpicks

---

# 3. GitHubManageIssues - Issue Management

## Overview

Complete issue lifecycle management with CRUD operations, labels, assignees, and milestones.

### Key Features
- **8 Actions** - create, update, close, reopen, add_labels, remove_labels, assign, unassign
- **Rich Formatting** - Markdown support in descriptions
- **Batch Operations** - Multiple labels/assignees at once
- **State Management** - Track issue state and reasons

## Parameters Reference

```python
GitHubManageIssues(
    repo_owner: str,              # Required: Repository owner
    repo_name: str,               # Required: Repository name
    action: IssueAction,          # Required: Action to perform
    issue_number: int = None,     # Conditional: Required for all except create
    title: str = None,            # Conditional: Required for create
    body: str = None,             # Optional: Issue description
    labels: List[str] = None,     # Conditional: Required for label actions
    assignees: List[str] = None,  # Conditional: Required for assign actions
    milestone: int = None,        # Optional: Milestone number
    state_reason: str = None      # Optional: completed, not_planned, reopened
)
```

## Use Cases

### 1. Create Bug Report

```python
from tools.integrations.github import GitHubManageIssues, IssueAction

tool = GitHubManageIssues(
    repo_owner="acme-corp",
    repo_name="web-app",
    action=IssueAction.CREATE,
    title="Bug: Login fails on iOS Safari",
    body="""
## Description
Users cannot log in using iOS Safari browser. The login button appears unresponsive.

## Steps to Reproduce
1. Open app on iPhone (iOS 17.2)
2. Navigate to login page
3. Enter valid credentials
4. Tap login button
5. Nothing happens - no error, no redirect

## Expected Behavior
User should be logged in and redirected to dashboard.

## Actual Behavior
Login button appears to do nothing. Console shows CORS error.

## Environment
- Device: iPhone 14 Pro
- OS: iOS 17.2
- Browser: Safari 17.2
- App Version: 1.2.3

## Screenshots
![Login Error](https://...)

## Additional Context
- Works fine on Chrome/Firefox
- Works on Android Safari
- Started after v1.2.3 deploy
    """,
    labels=["bug", "mobile", "ios", "priority:high"],
    assignees=["mobile-dev", "backend-dev"],
    milestone=5
)

result = tool.run()
print(f"🐛 Issue created: {result['issue_url']}")
print(f"📝 Issue #{result['issue_number']}")
```

### 2. Create Feature Request

```python
tool = GitHubManageIssues(
    repo_owner="acme-corp",
    repo_name="web-app",
    action=IssueAction.CREATE,
    title="Feature: Add dark mode support",
    body="""
## Feature Request

### Description
Add dark mode theme to improve user experience in low-light conditions.

### Motivation
- Reduce eye strain for night-time users
- Match system preferences
- Industry standard feature
- 65% of users requested this in survey

### Proposed Solution
1. Add theme toggle in settings
2. Implement dark color scheme
3. Persist user preference in localStorage
4. Auto-detect system preference
5. Smooth theme transitions

### Alternatives Considered
- Browser extension (rejected - not all browsers)
- Third-party theme (rejected - maintenance)

### Acceptance Criteria
- [ ] Toggle in user settings
- [ ] Dark theme for all pages
- [ ] Preference persistence
- [ ] System preference detection
- [ ] Smooth transitions (no flash)

### Design Mockups
![Dark Mode Dashboard](https://...)
    """,
    labels=["feature", "enhancement", "ui"],
    assignees=["frontend-lead"]
)
```

### 3. Update Issue Status

```python
# Update title and add label
tool = GitHubManageIssues(
    repo_owner="acme-corp",
    repo_name="web-app",
    action=IssueAction.UPDATE,
    issue_number=456,
    title="Bug: Login fails on iOS Safari [IN PROGRESS]",
    body="## Update\n\nInvestigating CORS configuration issue."
)
```

### 4. Add Labels to Issue

```python
tool = GitHubManageIssues(
    repo_owner="acme-corp",
    repo_name="web-app",
    action=IssueAction.ADD_LABELS,
    issue_number=456,
    labels=["priority:critical", "needs-review", "security"]
)
```

### 5. Assign Developers

```python
tool = GitHubManageIssues(
    repo_owner="acme-corp",
    repo_name="web-app",
    action=IssueAction.ASSIGN,
    issue_number=456,
    assignees=["senior-dev", "security-expert"]
)
```

### 6. Close Issue as Completed

```python
tool = GitHubManageIssues(
    repo_owner="acme-corp",
    repo_name="web-app",
    action=IssueAction.CLOSE,
    issue_number=456,
    state_reason="completed"
)

result = tool.run()
print(f"✅ Issue closed: {result['state']}")
```

### 7. Close Issue as Not Planned

```python
tool = GitHubManageIssues(
    repo_owner="acme-corp",
    repo_name="web-app",
    action=IssueAction.CLOSE,
    issue_number=789,
    state_reason="not_planned"
)
```

### 8. Reopen Issue

```python
tool = GitHubManageIssues(
    repo_owner="acme-corp",
    repo_name="web-app",
    action=IssueAction.REOPEN,
    issue_number=456
)
```

## Response Format

```python
{
    "success": True,
    "issue_number": 456,
    "issue_url": "https://github.com/acme-corp/web-app/issues/456",
    "issue_id": "I_kwDOABCDEFG",
    "state": "OPEN",  # or "CLOSED"
    "metadata": {
        "tool_name": "github_manage_issues",
        "repo": "acme-corp/web-app",
        "action": "created"
    }
}
```

## Issue Templates

Use consistent templates for better organization:

### Bug Template
```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. Step 1
2. Step 2

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS:
- Browser:
- Version:
```

### Feature Template
```markdown
## Feature Request
[Description]

## Motivation
[Why this is needed]

## Proposed Solution
[How to implement]

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
```

---

# 4. GitHubRunActions - Workflow Automation

## Overview

Trigger and monitor GitHub Actions workflows with support for manual dispatch, status checking, and artifact tracking.

### Key Features
- **Trigger Workflows** - Manual workflow dispatch
- **Monitor Execution** - Wait for completion with timeout
- **Check Status** - Get workflow run details
- **Job Tracking** - Monitor individual jobs
- **Artifact Access** - List available artifacts

## Parameters Reference

```python
GitHubRunActions(
    repo_owner: str,                    # Required: Repository owner
    repo_name: str,                     # Required: Repository name
    workflow_id: str = None,            # Conditional: Required for trigger
    ref: str = None,                    # Conditional: Required for trigger
    inputs: Dict[str, str] = None,      # Optional: Workflow inputs
    wait_for_completion: bool = False,  # Optional: Wait for completion
    timeout: int = 300,                 # Optional: Wait timeout (seconds)
    check_run_id: int = None            # Conditional: Check existing run
)
```

## Use Cases

### 1. Deploy to Production

```python
from tools.integrations.github import GitHubRunActions

tool = GitHubRunActions(
    repo_owner="acme-corp",
    repo_name="web-app",
    workflow_id="deploy.yml",
    ref="main",
    inputs={
        "environment": "production",
        "version": "v1.2.3",
        "region": "us-east-1",
        "notify_slack": "true"
    },
    wait_for_completion=True,
    timeout=600  # 10 minutes
)

result = tool.run()
if result["conclusion"] == "success":
    print(f"✅ Deployed successfully to production!")
    print(f"🔗 {result['run_url']}")
    for job in result["jobs"]:
        print(f"  ✓ {job['name']}: {job['conclusion']}")
else:
    print(f"❌ Deployment failed: {result['conclusion']}")
```

### 2. Run CI Tests

```python
tool = GitHubRunActions(
    repo_owner="acme-corp",
    repo_name="web-app",
    workflow_id="ci.yml",
    ref="feature/new-feature",
    inputs={
        "test_suite": "integration",
        "coverage": "true"
    },
    wait_for_completion=True,
    timeout=300
)

result = tool.run()
print(f"Tests: {result['conclusion']}")
print(f"Jobs: {len(result['jobs'])}")
```

### 3. Trigger Without Waiting

```python
# Fire and forget
tool = GitHubRunActions(
    repo_owner="acme-corp",
    repo_name="web-app",
    workflow_id="nightly-build.yml",
    ref="develop",
    wait_for_completion=False
)

result = tool.run()
print(f"🚀 Workflow triggered: {result['run_url']}")
print(f"📊 Status: {result['status']}")
```

### 4. Check Workflow Status

```python
# Check existing workflow run
tool = GitHubRunActions(
    repo_owner="acme-corp",
    repo_name="web-app",
    check_run_id=12345678
)

result = tool.run()
print(f"Status: {result['status']}")
print(f"Conclusion: {result['conclusion']}")

if result["status"] == "completed":
    print(f"Jobs:")
    for job in result["jobs"]:
        print(f"  - {job['name']}: {job['conclusion']}")

    print(f"\nArtifacts:")
    for artifact in result["artifacts"]:
        print(f"  - {artifact['name']} ({artifact['size_in_bytes']} bytes)")
```

### 5. Scheduled Release

```python
tool = GitHubRunActions(
    repo_owner="acme-corp",
    repo_name="web-app",
    workflow_id="release.yml",
    ref="main",
    inputs={
        "version": "v2.0.0",
        "changelog": "Major release with new features",
        "create_github_release": "true",
        "publish_npm": "true"
    },
    wait_for_completion=True,
    timeout=900  # 15 minutes
)

result = tool.run()
if result["conclusion"] == "success":
    # Extract artifacts
    for artifact in result["artifacts"]:
        if artifact["name"] == "release-notes":
            print(f"📄 Release notes ready: {artifact['id']}")
```

## Response Format

```python
{
    "success": True,
    "run_id": 12345678,
    "run_url": "https://github.com/acme-corp/web-app/actions/runs/12345678",
    "status": "completed",  # queued, in_progress, completed
    "conclusion": "success",  # success, failure, cancelled, skipped
    "jobs": [
        {
            "id": 11111,
            "name": "build",
            "status": "completed",
            "conclusion": "success",
            "started_at": "2024-01-15T10:00:00Z",
            "completed_at": "2024-01-15T10:05:00Z",
            "steps": 12
        }
    ],
    "artifacts": [
        {
            "id": 22222,
            "name": "build-output",
            "size_in_bytes": 1024000,
            "created_at": "2024-01-15T10:05:00Z"
        }
    ],
    "metadata": {
        "tool_name": "github_run_actions",
        "repo": "acme-corp/web-app",
        "workflow": "deploy.yml"
    }
}
```

## Workflow Examples

See workflow files in `.github/workflows/` for examples.

---

# 5. GitHubRepoAnalytics - Repository Insights

## Overview

Fetch comprehensive repository statistics including commits, PRs, issues, contributors, and language breakdown.

### Key Features
- **Repository Info** - Stars, forks, watchers
- **Commit Stats** - Total commits, authors, code changes
- **PR Analytics** - Open, merged, average merge time
- **Issue Tracking** - Open, closed, average close time
- **Contributors** - Top contributors by commits
- **Languages** - Language breakdown by bytes

## Parameters Reference

```python
GitHubRepoAnalytics(
    repo_owner: str,                      # Required: Repository owner
    repo_name: str,                       # Required: Repository name
    since: str = None,                    # Optional: Start date (YYYY-MM-DD)
    until: str = None,                    # Optional: End date (YYYY-MM-DD)
    include_commits: bool = True,         # Optional: Include commit stats
    include_prs: bool = True,             # Optional: Include PR stats
    include_issues: bool = True,          # Optional: Include issue stats
    include_contributors: bool = True,    # Optional: Include contributors
    include_languages: bool = True        # Optional: Include languages
)
```

## Use Cases

### 1. Monthly Report

```python
from tools.integrations.github import GitHubRepoAnalytics

tool = GitHubRepoAnalytics(
    repo_owner="acme-corp",
    repo_name="web-app",
    since="2024-01-01",
    until="2024-01-31"
)

result = tool.run()

print(f"📊 Monthly Report: {result['repository']['name']}")
print(f"\n⭐ Stars: {result['repository']['stars']}")
print(f"🍴 Forks: {result['repository']['forks']}")
print(f"\n📝 Commits: {result['commits']['total']}")
print(f"👥 Active Contributors: {result['commits']['authors']}")
print(f"📈 Code Changes: +{result['commits']['additions']} / -{result['commits']['deletions']}")
print(f"\n🔀 Pull Requests:")
print(f"  Total: {result['pull_requests']['total']}")
print(f"  Merged: {result['pull_requests']['merged']}")
print(f"  Avg Merge Time: {result['pull_requests']['avg_merge_time_hours']:.1f} hours")
print(f"\n🐛 Issues:")
print(f"  Open: {result['issues']['open']}")
print(f"  Closed: {result['issues']['closed']}")
print(f"  Avg Close Time: {result['issues']['avg_close_time_hours']:.1f} hours")
```

### 2. Contributor Dashboard

```python
tool = GitHubRepoAnalytics(
    repo_owner="acme-corp",
    repo_name="web-app",
    include_commits=False,
    include_prs=False,
    include_issues=False,
    include_contributors=True,
    include_languages=True
)

result = tool.run()

print(f"🏆 Top Contributors:")
for i, contributor in enumerate(result['contributors'][:10], 1):
    print(f"{i}. {contributor['login']}: {contributor['contributions']} contributions")

print(f"\n💻 Languages:")
for lang, stats in result['languages'].items():
    print(f"  {lang}: {stats['percentage']}%")
```

### 3. Health Check

```python
tool = GitHubRepoAnalytics(
    repo_owner="acme-corp",
    repo_name="web-app"
)

result = tool.run()

repo = result["repository"]
prs = result["pull_requests"]
issues = result["issues"]

# Calculate health score
health_score = 0
if prs["avg_merge_time_hours"] < 48:
    health_score += 25
if issues["avg_close_time_hours"] < 72:
    health_score += 25
if issues["open"] < issues["closed"]:
    health_score += 25
if repo["stars"] > 100:
    health_score += 25

print(f"🏥 Repository Health: {health_score}/100")
```

### 4. Language Analysis

```python
tool = GitHubRepoAnalytics(
    repo_owner="acme-corp",
    repo_name="web-app",
    include_commits=False,
    include_prs=False,
    include_issues=False,
    include_contributors=False,
    include_languages=True
)

result = tool.run()

print(f"📊 Language Breakdown:")
for lang, stats in result['languages'].items():
    bar = "█" * int(stats['percentage'] / 2)
    print(f"{lang:15} {bar} {stats['percentage']:.1f}%")
```

## Response Format

```python
{
    "success": True,
    "repository": {
        "name": "web-app",
        "owner": "acme-corp",
        "description": "Our awesome web application",
        "stars": 1234,
        "forks": 567,
        "watchers": 89,
        "open_issues": 45,
        "created_at": "2023-01-15T10:00:00Z",
        "updated_at": "2024-01-15T15:30:00Z",
        "default_branch": "main",
        "is_private": False,
        "url": "https://github.com/acme-corp/web-app"
    },
    "commits": {
        "total": 342,
        "authors": 15,
        "additions": 12450,
        "deletions": 8320,
        "net_change": 4130
    },
    "pull_requests": {
        "total": 87,
        "open": 12,
        "closed": 45,
        "merged": 30,
        "avg_merge_time_hours": 24.5
    },
    "issues": {
        "total": 123,
        "open": 45,
        "closed": 78,
        "avg_close_time_hours": 48.2
    },
    "contributors": [
        {
            "login": "senior-dev",
            "contributions": 145,
            "avatar_url": "https://...",
            "url": "https://github.com/senior-dev"
        }
    ],
    "languages": {
        "Python": {
            "bytes": 125000,
            "percentage": 45.2,
            "color": "#3572A5"
        },
        "JavaScript": {
            "bytes": 98000,
            "percentage": 35.4,
            "color": "#f1e05a"
        }
    },
    "metadata": {
        "tool_name": "github_repo_analytics",
        "repo": "acme-corp/web-app",
        "period": "2024-01-01 to 2024-01-31"
    }
}
```

---

## Common Patterns

### 1. Complete CI/CD Pipeline

```python
# Step 1: Create PR
pr = GitHubCreatePR(...)
pr_result = pr.run()

# Step 2: Trigger CI
ci = GitHubRunActions(..., workflow_id="ci.yml")
ci_result = ci.run()

# Step 3: Auto-approve if CI passes
if ci_result["conclusion"] == "success":
    review = GitHubReviewCode(..., event=ReviewEvent.APPROVE)
    review.run()
```

### 2. Issue Triage

```python
# Get analytics
analytics = GitHubRepoAnalytics(...)
result = analytics.run()

# Auto-label based on patterns
for issue in get_open_issues():
    if "bug" in issue["title"].lower():
        GitHubManageIssues(..., action=IssueAction.ADD_LABELS, labels=["bug"])
```

### 3. Release Process

```python
# Create release PR
pr = GitHubCreatePR(..., title="Release v1.2.3")

# Run release workflow
workflow = GitHubRunActions(..., workflow_id="release.yml")

# Get analytics for release notes
analytics = GitHubRepoAnalytics(...)
```

---

Built for the AgentSwarm Framework | MIT License
