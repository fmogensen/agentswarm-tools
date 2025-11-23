"""
Linear Integration Tools for AgentSwarm Tools Framework

Comprehensive Linear integration with GraphQL API support for issue management,
team collaboration, roadmap tracking, and GitHub synchronization.

Available Tools:
    - LinearCreateIssue: Create issues with projects, labels, priorities
    - LinearUpdateStatus: Update issue status, transitions, workflows
    - LinearAssignTeam: Assign to teams/users, set estimates, cycles
    - LinearGetRoadmap: Retrieve roadmap, projects, milestones, progress
    - LinearSyncGitHub: Bi-directional sync with GitHub issues/PRs

Usage:
    from tools.integrations.linear import LinearCreateIssue

    tool = LinearCreateIssue(
        title="New feature",
        team_id="team_abc123",
        priority=2
    )
    result = tool.run()
"""

from .linear_assign_team import LinearAssignTeam
from .linear_create_issue import LinearCreateIssue
from .linear_get_roadmap import LinearGetRoadmap
from .linear_sync_github import LinearSyncGitHub
from .linear_update_status import LinearUpdateStatus

__all__ = [
    "LinearCreateIssue",
    "LinearUpdateStatus",
    "LinearAssignTeam",
    "LinearGetRoadmap",
    "LinearSyncGitHub",
]

# Tool metadata for discovery
LINEAR_TOOLS = {
    "linear_create_issue": {
        "class": LinearCreateIssue,
        "category": "integrations",
        "description": "Create Linear issues with full field support",
        "requires_auth": True,
        "api": "Linear GraphQL",
    },
    "linear_update_status": {
        "class": LinearUpdateStatus,
        "category": "integrations",
        "description": "Update Linear issue status and workflows",
        "requires_auth": True,
        "api": "Linear GraphQL",
    },
    "linear_assign_team": {
        "class": LinearAssignTeam,
        "category": "integrations",
        "description": "Assign issues to teams with capacity planning",
        "requires_auth": True,
        "api": "Linear GraphQL",
    },
    "linear_get_roadmap": {
        "class": LinearGetRoadmap,
        "category": "integrations",
        "description": "Retrieve roadmap and project tracking",
        "requires_auth": True,
        "api": "Linear GraphQL",
    },
    "linear_sync_github": {
        "class": LinearSyncGitHub,
        "category": "integrations",
        "description": "Bi-directional sync with GitHub",
        "requires_auth": True,
        "api": "Linear GraphQL + GitHub REST",
    },
}
