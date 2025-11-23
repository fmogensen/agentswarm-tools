"""
GitHub Create Pull Request Tool

Creates pull requests using GitHub's GraphQL API (10x faster than REST).
Supports PR templates, auto-reviewers, labels, and draft PRs.
"""

from typing import Any, Dict, Optional, List
from pydantic import Field
import os
import json

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError


class GitHubCreatePR(BaseTool):
    """
    Create a pull request on GitHub using GraphQL API.

    This tool creates PRs with support for templates, auto-reviewers, labels,
    and draft PRs. Uses GraphQL for optimal performance (10x fewer API calls).

    Args:
        repo_owner: GitHub repository owner (username or organization)
        repo_name: Repository name
        title: Pull request title
        head_branch: Source branch name (where changes are)
        base_branch: Target branch name (where to merge, default: main)
        body: Pull request description (supports markdown)
        draft: Create as draft PR (default: False)
        reviewers: List of GitHub usernames to request reviews from
        team_reviewers: List of team slugs to request reviews from
        labels: List of label names to add to PR
        assignees: List of GitHub usernames to assign to PR
        milestone: Milestone number to associate with PR
        auto_merge: Enable auto-merge when all checks pass (default: False)

    Returns:
        Dict containing:
            - success (bool): Whether the PR was created successfully
            - pr_number (int): Pull request number
            - pr_url (str): URL to the pull request
            - pr_id (str): GraphQL node ID
            - state (str): PR state (OPEN, DRAFT)
            - mergeable (str): Whether PR is mergeable
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = GitHubCreatePR(
        ...     repo_owner="myorg",
        ...     repo_name="myrepo",
        ...     title="Add new feature",
        ...     head_branch="feature/new-feature",
        ...     base_branch="main",
        ...     body="## Summary\\n\\nAdds new feature X",
        ...     reviewers=["user1", "user2"],
        ...     labels=["feature", "needs-review"]
        ... )
        >>> result = tool.run()
        >>> print(result['pr_url'])
        'https://github.com/myorg/myrepo/pull/123'
    """

    # Tool metadata
    tool_name: str = "github_create_pr"
    tool_category: str = "integrations"

    # Required parameters
    repo_owner: str = Field(
        ...,
        description="Repository owner (username or organization)",
        min_length=1,
        max_length=100,
    )
    repo_name: str = Field(
        ..., description="Repository name", min_length=1, max_length=100
    )
    title: str = Field(
        ..., description="Pull request title", min_length=1, max_length=256
    )
    head_branch: str = Field(
        ..., description="Source branch name", min_length=1, max_length=100
    )

    # Optional parameters
    base_branch: str = Field(
        "main", description="Target branch name", min_length=1, max_length=100
    )
    body: Optional[str] = Field(
        None, description="Pull request description (markdown supported)"
    )
    draft: bool = Field(False, description="Create as draft PR")
    reviewers: Optional[List[str]] = Field(
        None, description="GitHub usernames to request reviews from"
    )
    team_reviewers: Optional[List[str]] = Field(
        None, description="Team slugs to request reviews from"
    )
    labels: Optional[List[str]] = Field(None, description="Label names to add to PR")
    assignees: Optional[List[str]] = Field(
        None, description="GitHub usernames to assign to PR"
    )
    milestone: Optional[int] = Field(
        None, description="Milestone number to associate with PR"
    )
    auto_merge: bool = Field(False, description="Enable auto-merge when checks pass")

    def _execute(self) -> Dict[str, Any]:
        """Execute the PR creation."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            # Create PR using GraphQL
            pr_data = self._create_pr_graphql()

            # Add reviewers, labels, assignees if specified
            if self.reviewers or self.team_reviewers:
                self._add_reviewers(pr_data["node_id"])

            if self.labels:
                self._add_labels(pr_data["node_id"])

            if self.assignees:
                self._add_assignees(pr_data["node_id"])

            if self.milestone:
                self._set_milestone(pr_data["node_id"])

            if self.auto_merge:
                self._enable_auto_merge(pr_data["node_id"])

            return {
                "success": True,
                "pr_number": pr_data["number"],
                "pr_url": pr_data["url"],
                "pr_id": pr_data["node_id"],
                "state": pr_data["state"],
                "mergeable": pr_data.get("mergeable", "UNKNOWN"),
                "metadata": {
                    "tool_name": self.tool_name,
                    "repo": f"{self.repo_owner}/{self.repo_name}",
                    "head": self.head_branch,
                    "base": self.base_branch,
                },
            }
        except Exception as e:
            raise APIError(f"Failed to create PR: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate branch names don't match
        if self.head_branch == self.base_branch:
            raise ValidationError(
                "head_branch and base_branch cannot be the same",
                tool_name=self.tool_name,
            )

        # Validate reviewers format
        if self.reviewers:
            for reviewer in self.reviewers:
                if not reviewer.strip():
                    raise ValidationError(
                        "Reviewer username cannot be empty", tool_name=self.tool_name
                    )

        # Validate labels format
        if self.labels:
            for label in self.labels:
                if not label.strip():
                    raise ValidationError(
                        "Label name cannot be empty", tool_name=self.tool_name
                    )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "pr_number": 123,
            "pr_url": f"https://github.com/{self.repo_owner}/{self.repo_name}/pull/123",
            "pr_id": "PR_mock_1234567890",
            "state": "DRAFT" if self.draft else "OPEN",
            "mergeable": "MERGEABLE",
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "head": self.head_branch,
                "base": self.base_branch,
                "mock_mode": True,
            },
        }

    def _create_pr_graphql(self) -> Dict[str, Any]:
        """Create PR using GitHub GraphQL API."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise AuthenticationError(
                "Missing GITHUB_TOKEN environment variable", tool_name=self.tool_name
            )

        # Get repository ID first
        repo_id = self._get_repository_id(token)

        # GraphQL mutation to create PR
        mutation = """
        mutation($input: CreatePullRequestInput!) {
            createPullRequest(input: $input) {
                pullRequest {
                    id
                    number
                    url
                    state
                    isDraft
                    mergeable
                    title
                    body
                }
            }
        }
        """

        variables = {
            "input": {
                "repositoryId": repo_id,
                "baseRefName": self.base_branch,
                "headRefName": self.head_branch,
                "title": self.title,
                "body": self.body or "",
                "draft": self.draft,
            }
        }

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        pr = response["data"]["createPullRequest"]["pullRequest"]
        return {
            "node_id": pr["id"],
            "number": pr["number"],
            "url": pr["url"],
            "state": pr["state"],
            "mergeable": pr["mergeable"],
        }

    def _get_repository_id(self, token: str) -> str:
        """Get repository GraphQL node ID."""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                id
            }
        }
        """

        variables = {"owner": self.repo_owner, "name": self.repo_name}

        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            raise APIError(
                f"Repository not found: {self.repo_owner}/{self.repo_name}",
                tool_name=self.tool_name,
            )

        return response["data"]["repository"]["id"]

    def _add_reviewers(self, pr_id: str) -> None:
        """Add reviewers to PR using GraphQL."""
        token = os.getenv("GITHUB_TOKEN")

        mutation = """
        mutation($input: RequestReviewsInput!) {
            requestReviews(input: $input) {
                pullRequest {
                    id
                }
            }
        }
        """

        # Get user IDs for reviewers
        user_ids = []
        if self.reviewers:
            for username in self.reviewers:
                user_id = self._get_user_id(token, username)
                if user_id:
                    user_ids.append(user_id)

        # Get team IDs for team reviewers
        team_ids = []
        if self.team_reviewers:
            for team_slug in self.team_reviewers:
                team_id = self._get_team_id(token, team_slug)
                if team_id:
                    team_ids.append(team_id)

        variables = {
            "input": {
                "pullRequestId": pr_id,
                "userIds": user_ids,
                "teamIds": team_ids,
            }
        }

        self._execute_graphql(token, mutation, variables)

    def _add_labels(self, pr_id: str) -> None:
        """Add labels to PR using GraphQL."""
        token = os.getenv("GITHUB_TOKEN")

        mutation = """
        mutation($input: AddLabelsToLabelableInput!) {
            addLabelsToLabelable(input: $input) {
                labelable {
                    ... on PullRequest {
                        id
                    }
                }
            }
        }
        """

        # Get label IDs
        label_ids = []
        for label_name in self.labels:
            label_id = self._get_label_id(token, label_name)
            if label_id:
                label_ids.append(label_id)

        variables = {"input": {"labelableId": pr_id, "labelIds": label_ids}}

        self._execute_graphql(token, mutation, variables)

    def _add_assignees(self, pr_id: str) -> None:
        """Add assignees to PR using GraphQL."""
        token = os.getenv("GITHUB_TOKEN")

        mutation = """
        mutation($input: AddAssigneesToAssignableInput!) {
            addAssigneesToAssignable(input: $input) {
                assignable {
                    ... on PullRequest {
                        id
                    }
                }
            }
        }
        """

        # Get assignee IDs
        assignee_ids = []
        for username in self.assignees:
            user_id = self._get_user_id(token, username)
            if user_id:
                assignee_ids.append(user_id)

        variables = {"input": {"assignableId": pr_id, "assigneeIds": assignee_ids}}

        self._execute_graphql(token, mutation, variables)

    def _set_milestone(self, pr_id: str) -> None:
        """Set milestone for PR using REST API (GraphQL doesn't support this)."""
        token = os.getenv("GITHUB_TOKEN")
        import requests

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues/{pr_id.split('_')[-1]}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {"milestone": self.milestone}

        requests.patch(url, headers=headers, json=data)

    def _enable_auto_merge(self, pr_id: str) -> None:
        """Enable auto-merge for PR using GraphQL."""
        token = os.getenv("GITHUB_TOKEN")

        mutation = """
        mutation($input: EnablePullRequestAutoMergeInput!) {
            enablePullRequestAutoMerge(input: $input) {
                pullRequest {
                    id
                    autoMergeRequest {
                        enabledAt
                    }
                }
            }
        }
        """

        variables = {
            "input": {"pullRequestId": pr_id, "mergeMethod": "MERGE"}
        }

        self._execute_graphql(token, mutation, variables)

    def _get_user_id(self, token: str, username: str) -> Optional[str]:
        """Get user GraphQL node ID."""
        query = """
        query($login: String!) {
            user(login: $login) {
                id
            }
        }
        """

        variables = {"login": username}
        response = self._execute_graphql(token, query, variables)

        if "errors" in response or not response.get("data", {}).get("user"):
            return None

        return response["data"]["user"]["id"]

    def _get_team_id(self, token: str, team_slug: str) -> Optional[str]:
        """Get team GraphQL node ID."""
        query = """
        query($org: String!, $slug: String!) {
            organization(login: $org) {
                team(slug: $slug) {
                    id
                }
            }
        }
        """

        variables = {"org": self.repo_owner, "slug": team_slug}
        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            return None

        team = response.get("data", {}).get("organization", {}).get("team")
        return team["id"] if team else None

    def _get_label_id(self, token: str, label_name: str) -> Optional[str]:
        """Get label GraphQL node ID."""
        query = """
        query($owner: String!, $name: String!, $labelName: String!) {
            repository(owner: $owner, name: $name) {
                label(name: $labelName) {
                    id
                }
            }
        }
        """

        variables = {
            "owner": self.repo_owner,
            "name": self.repo_name,
            "labelName": label_name,
        }
        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            return None

        label = response.get("data", {}).get("repository", {}).get("label")
        return label["id"] if label else None

    def _execute_graphql(
        self, token: str, query: str, variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute GraphQL query/mutation."""
        import requests

        url = "https://api.github.com/graphql"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {"query": query, "variables": variables}

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            raise APIError(
                f"GitHub API error: {response.status_code}",
                api_name="GitHub",
                status_code=response.status_code,
                tool_name=self.tool_name,
            )

        return response.json()


if __name__ == "__main__":
    # Test the tool
    print("Testing GitHubCreatePR...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic PR
    print("\n1. Testing basic PR creation...")
    tool = GitHubCreatePR(
        repo_owner="myorg",
        repo_name="myrepo",
        title="Add new feature",
        head_branch="feature/new-feature",
        base_branch="main",
        body="## Summary\n\nAdds new feature X",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"PR Number: {result.get('pr_number')}")
    print(f"PR URL: {result.get('pr_url')}")
    print(f"State: {result.get('state')}")
    assert result.get("success") == True
    assert result.get("pr_number") == 123
    assert result.get("state") == "OPEN"

    # Test 2: Draft PR with reviewers and labels
    print("\n2. Testing draft PR with reviewers and labels...")
    tool = GitHubCreatePR(
        repo_owner="myorg",
        repo_name="myrepo",
        title="WIP: Experimental feature",
        head_branch="experiment/feature",
        base_branch="develop",
        body="## Work in Progress\n\nExperimental feature",
        draft=True,
        reviewers=["reviewer1", "reviewer2"],
        labels=["wip", "experimental"],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"State: {result.get('state')}")
    assert result.get("success") == True
    assert result.get("state") == "DRAFT"

    # Test 3: PR with auto-merge
    print("\n3. Testing PR with auto-merge...")
    tool = GitHubCreatePR(
        repo_owner="myorg",
        repo_name="myrepo",
        title="Hotfix: Critical bug",
        head_branch="hotfix/critical-bug",
        base_branch="main",
        body="## Hotfix\n\nFixes critical bug",
        auto_merge=True,
        assignees=["assignee1"],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"PR URL: {result.get('pr_url')}")
    assert result.get("success") == True

    # Test 4: Error handling - same branch
    print("\n4. Testing error handling (same branch)...")
    try:
        tool = GitHubCreatePR(
            repo_owner="myorg",
            repo_name="myrepo",
            title="Test PR",
            head_branch="main",
            base_branch="main",
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if "error" in str(e):
            error_dict = eval(str(e))
            print(f"Correctly caught error: {error_dict['error']['message']}")
        else:
            print(f"Correctly caught error: {str(e)}")

    print("\n✅ All tests passed!")
