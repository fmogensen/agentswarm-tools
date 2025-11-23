"""
GitHub Integration Tools for AgentSwarm Framework.

Provides 5 production-ready tools for GitHub automation using GraphQL API:
- GitHubCreatePR: Create pull requests with templates and auto-reviewers
- GitHubReviewCode: Submit PR reviews with line comments
- GitHubManageIssues: Create, update, close, and manage issues
- GitHubRunActions: Trigger and monitor GitHub Actions workflows
- GitHubRepoAnalytics: Fetch repository statistics and insights

All tools use GraphQL API for 10x faster performance vs REST API.
"""

from tools.integrations.github.github_create_pr import GitHubCreatePR
from tools.integrations.github.github_manage_issues import (
    GitHubManageIssues,
    IssueAction,
)
from tools.integrations.github.github_repo_analytics import GitHubRepoAnalytics
from tools.integrations.github.github_review_code import GitHubReviewCode, ReviewEvent
from tools.integrations.github.github_run_actions import GitHubRunActions

__all__ = [
    "GitHubCreatePR",
    "GitHubReviewCode",
    "ReviewEvent",
    "GitHubManageIssues",
    "IssueAction",
    "GitHubRunActions",
    "GitHubRepoAnalytics",
]

__version__ = "1.0.0"
__author__ = "AgentSwarm Team"
__description__ = "GitHub integration tools using GraphQL API"
