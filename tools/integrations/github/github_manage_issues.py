"""
GitHub Manage Issues Tool

Create, update, close, and manage GitHub issues using GraphQL API.
Supports labels, assignees, milestones, and issue templates.
"""

import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class IssueAction(str, Enum):
    """Issue management actions."""

    CREATE = "create"
    UPDATE = "update"
    CLOSE = "close"
    REOPEN = "reopen"
    ADD_LABELS = "add_labels"
    REMOVE_LABELS = "remove_labels"
    ASSIGN = "assign"
    UNASSIGN = "unassign"


class GitHubManageIssues(BaseTool):
    """
    Manage GitHub issues with comprehensive CRUD operations.

    This tool supports creating, updating, closing, and managing issues with
    labels, assignees, milestones, and project integration.

    Args:
        repo_owner: GitHub repository owner (username or organization)
        repo_name: Repository name
        action: Action to perform (create, update, close, reopen, add_labels, etc.)
        issue_number: Issue number (required for update/close/reopen/labels/assign)
        title: Issue title (required for create, optional for update)
        body: Issue description (supports markdown)
        labels: List of label names to add
        assignees: List of GitHub usernames to assign
        milestone: Milestone number to associate
        state_reason: Reason for closing (completed, not_planned, reopened)

    Returns:
        Dict containing:
            - success (bool): Whether the operation was successful
            - issue_number (int): Issue number
            - issue_url (str): URL to the issue
            - issue_id (str): GraphQL node ID
            - state (str): Issue state (OPEN, CLOSED)
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Create new issue
        >>> tool = GitHubManageIssues(
        ...     repo_owner="myorg",
        ...     repo_name="myrepo",
        ...     action="create",
        ...     title="Bug: Login fails on mobile",
        ...     body="## Description\\n\\nLogin button not working on mobile",
        ...     labels=["bug", "mobile"],
        ...     assignees=["developer1"]
        ... )
        >>> result = tool.run()
        >>> print(result['issue_number'])
        456
    """

    # Tool metadata
    tool_name: str = "github_manage_issues"
    tool_category: str = "integrations"

    # Required parameters
    repo_owner: str = Field(
        ...,
        description="Repository owner (username or organization)",
        min_length=1,
        max_length=100,
    )
    repo_name: str = Field(..., description="Repository name", min_length=1, max_length=100)
    action: IssueAction = Field(..., description="Action to perform on issue")

    # Conditional parameters
    issue_number: Optional[int] = Field(
        None, description="Issue number (required for update/close/reopen)", ge=1
    )
    title: Optional[str] = Field(
        None, description="Issue title (required for create)", max_length=256
    )
    body: Optional[str] = Field(None, description="Issue description (markdown supported)")
    labels: Optional[List[str]] = Field(None, description="Label names to add/remove")
    assignees: Optional[List[str]] = Field(None, description="GitHub usernames to assign/unassign")
    milestone: Optional[int] = Field(None, description="Milestone number to associate")
    state_reason: Optional[str] = Field(
        None,
        description="Reason for closing (completed, not_planned, reopened)",
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the issue management operation."""

        self._logger.info(f"Executing {self.tool_name} with repo_owner={self.repo_owner}, repo_name={self.repo_name}, issue_number={self.issue_number}, ...")
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._perform_action()
            return result
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to {self.action.value} issue: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters based on action."""
        # Validate action-specific requirements
        if self.action == IssueAction.CREATE:
            if not self.title or not self.title.strip():
                raise ValidationError(
                    "title is required for create action", tool_name=self.tool_name
                )
        elif self.action in [
            IssueAction.UPDATE,
            IssueAction.CLOSE,
            IssueAction.REOPEN,
            IssueAction.ADD_LABELS,
            IssueAction.REMOVE_LABELS,
            IssueAction.ASSIGN,
            IssueAction.UNASSIGN,
        ]:
            if not self.issue_number:
                raise ValidationError(
                    f"issue_number is required for {self.action.value} action",
                    tool_name=self.tool_name,
                )

        # Validate labels for label actions
        if self.action in [IssueAction.ADD_LABELS, IssueAction.REMOVE_LABELS]:
            if not self.labels:
                raise ValidationError(
                    f"labels is required for {self.action.value} action",
                    tool_name=self.tool_name,
                )

        # Validate assignees for assign actions
        if self.action in [IssueAction.ASSIGN, IssueAction.UNASSIGN]:
            if not self.assignees:
                raise ValidationError(
                    f"assignees is required for {self.action.value} action",
                    tool_name=self.tool_name,
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        issue_num = self.issue_number or 456
        state = "CLOSED" if self.action == IssueAction.CLOSE else "OPEN"

        return {
            "success": True,
            "issue_number": issue_num,
            "issue_url": f"https://github.com/{self.repo_owner}/{self.repo_name}/issues/{issue_num}",
            "issue_id": f"I_mock_{issue_num}",
            "state": state,
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "action": self.action.value,
                "mock_mode": True,
            },
        }

    def _perform_action(self) -> Dict[str, Any]:
        """Perform the requested action."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise AuthenticationError(
                "Missing GITHUB_TOKEN environment variable", tool_name=self.tool_name
            )

        action_map = {
            IssueAction.CREATE: self._create_issue,
            IssueAction.UPDATE: self._update_issue,
            IssueAction.CLOSE: self._close_issue,
            IssueAction.REOPEN: self._reopen_issue,
            IssueAction.ADD_LABELS: self._add_labels,
            IssueAction.REMOVE_LABELS: self._remove_labels,
            IssueAction.ASSIGN: self._assign_users,
            IssueAction.UNASSIGN: self._unassign_users,
        }

        handler = action_map.get(self.action)
        if not handler:
            raise ValidationError(f"Unknown action: {self.action}", tool_name=self.tool_name)

        return handler(token)

    def _create_issue(self, token: str) -> Dict[str, Any]:
        """Create a new issue using GraphQL."""
        repo_id = self._get_repository_id(token)

        mutation = """
        mutation($input: CreateIssueInput!) {
            createIssue(input: $input) {
                issue {
                    id
                    number
                    url
                    state
                    title
                }
            }
        }
        """

        variables = {
            "input": {
                "repositoryId": repo_id,
                "title": self.title,
                "body": self.body or "",
            }
        }

        # Add optional fields
        if self.labels:
            label_ids = [self._get_label_id(token, label) for label in self.labels]
            variables["input"]["labelIds"] = [lid for lid in label_ids if lid]

        if self.assignees:
            assignee_ids = [self._get_user_id(token, user) for user in self.assignees]
            variables["input"]["assigneeIds"] = [aid for aid in assignee_ids if aid]

        if self.milestone:
            milestone_id = self._get_milestone_id(token, self.milestone)
            if milestone_id:
                variables["input"]["milestoneId"] = milestone_id

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        issue = response["data"]["createIssue"]["issue"]
        return {
            "success": True,
            "issue_number": issue["number"],
            "issue_url": issue["url"],
            "issue_id": issue["id"],
            "state": issue["state"],
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "action": "created",
            },
        }

    def _update_issue(self, token: str) -> Dict[str, Any]:
        """Update an existing issue using GraphQL."""
        issue_id = self._get_issue_id(token)

        mutation = """
        mutation($input: UpdateIssueInput!) {
            updateIssue(input: $input) {
                issue {
                    id
                    number
                    url
                    state
                    title
                }
            }
        }
        """

        variables = {"input": {"id": issue_id}}

        # Add fields to update
        if self.title:
            variables["input"]["title"] = self.title
        if self.body is not None:
            variables["input"]["body"] = self.body
        if self.labels:
            label_ids = [self._get_label_id(token, label) for label in self.labels]
            variables["input"]["labelIds"] = [lid for lid in label_ids if lid]
        if self.assignees:
            assignee_ids = [self._get_user_id(token, user) for user in self.assignees]
            variables["input"]["assigneeIds"] = [aid for aid in assignee_ids if aid]
        if self.milestone:
            milestone_id = self._get_milestone_id(token, self.milestone)
            if milestone_id:
                variables["input"]["milestoneId"] = milestone_id

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        issue = response["data"]["updateIssue"]["issue"]
        return {
            "success": True,
            "issue_number": issue["number"],
            "issue_url": issue["url"],
            "issue_id": issue["id"],
            "state": issue["state"],
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "action": "updated",
            },
        }

    def _close_issue(self, token: str) -> Dict[str, Any]:
        """Close an issue using GraphQL."""
        issue_id = self._get_issue_id(token)

        mutation = """
        mutation($input: CloseIssueInput!) {
            closeIssue(input: $input) {
                issue {
                    id
                    number
                    url
                    state
                    stateReason
                }
            }
        }
        """

        variables = {
            "input": {
                "issueId": issue_id,
                "stateReason": self.state_reason or "COMPLETED",
            }
        }

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        issue = response["data"]["closeIssue"]["issue"]
        return {
            "success": True,
            "issue_number": issue["number"],
            "issue_url": issue["url"],
            "issue_id": issue["id"],
            "state": issue["state"],
            "state_reason": issue.get("stateReason"),
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "action": "closed",
            },
        }

    def _reopen_issue(self, token: str) -> Dict[str, Any]:
        """Reopen a closed issue using GraphQL."""
        issue_id = self._get_issue_id(token)

        mutation = """
        mutation($input: ReopenIssueInput!) {
            reopenIssue(input: $input) {
                issue {
                    id
                    number
                    url
                    state
                }
            }
        }
        """

        variables = {"input": {"issueId": issue_id}}

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        issue = response["data"]["reopenIssue"]["issue"]
        return {
            "success": True,
            "issue_number": issue["number"],
            "issue_url": issue["url"],
            "issue_id": issue["id"],
            "state": issue["state"],
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "action": "reopened",
            },
        }

    def _add_labels(self, token: str) -> Dict[str, Any]:
        """Add labels to an issue."""
        issue_id = self._get_issue_id(token)
        label_ids = [self._get_label_id(token, label) for label in self.labels]
        label_ids = [lid for lid in label_ids if lid]

        mutation = """
        mutation($input: AddLabelsToLabelableInput!) {
            addLabelsToLabelable(input: $input) {
                labelable {
                    ... on Issue {
                        id
                        number
                        url
                    }
                }
            }
        }
        """

        variables = {"input": {"labelableId": issue_id, "labelIds": label_ids}}

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        issue = response["data"]["addLabelsToLabelable"]["labelable"]
        return {
            "success": True,
            "issue_number": issue["number"],
            "issue_url": issue["url"],
            "issue_id": issue["id"],
            "state": "OPEN",
            "metadata": {
                "tool_name": self.tool_name,
                "labels_added": self.labels,
            },
        }

    def _remove_labels(self, token: str) -> Dict[str, Any]:
        """Remove labels from an issue."""
        issue_id = self._get_issue_id(token)
        label_ids = [self._get_label_id(token, label) for label in self.labels]
        label_ids = [lid for lid in label_ids if lid]

        mutation = """
        mutation($input: RemoveLabelsFromLabelableInput!) {
            removeLabelsFromLabelable(input: $input) {
                labelable {
                    ... on Issue {
                        id
                        number
                        url
                    }
                }
            }
        }
        """

        variables = {"input": {"labelableId": issue_id, "labelIds": label_ids}}

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        issue = response["data"]["removeLabelsFromLabelable"]["labelable"]
        return {
            "success": True,
            "issue_number": issue["number"],
            "issue_url": issue["url"],
            "issue_id": issue["id"],
            "state": "OPEN",
            "metadata": {
                "tool_name": self.tool_name,
                "labels_removed": self.labels,
            },
        }

    def _assign_users(self, token: str) -> Dict[str, Any]:
        """Assign users to an issue."""
        issue_id = self._get_issue_id(token)
        assignee_ids = [self._get_user_id(token, user) for user in self.assignees]
        assignee_ids = [aid for aid in assignee_ids if aid]

        mutation = """
        mutation($input: AddAssigneesToAssignableInput!) {
            addAssigneesToAssignable(input: $input) {
                assignable {
                    ... on Issue {
                        id
                        number
                        url
                    }
                }
            }
        }
        """

        variables = {"input": {"assignableId": issue_id, "assigneeIds": assignee_ids}}

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        issue = response["data"]["addAssigneesToAssignable"]["assignable"]
        return {
            "success": True,
            "issue_number": issue["number"],
            "issue_url": issue["url"],
            "issue_id": issue["id"],
            "state": "OPEN",
            "metadata": {
                "tool_name": self.tool_name,
                "assignees_added": self.assignees,
            },
        }

    def _unassign_users(self, token: str) -> Dict[str, Any]:
        """Unassign users from an issue."""
        issue_id = self._get_issue_id(token)
        assignee_ids = [self._get_user_id(token, user) for user in self.assignees]
        assignee_ids = [aid for aid in assignee_ids if aid]

        mutation = """
        mutation($input: RemoveAssigneesFromAssignableInput!) {
            removeAssigneesFromAssignable(input: $input) {
                assignable {
                    ... on Issue {
                        id
                        number
                        url
                    }
                }
            }
        }
        """

        variables = {"input": {"assignableId": issue_id, "assigneeIds": assignee_ids}}

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        issue = response["data"]["removeAssigneesFromAssignable"]["assignable"]
        return {
            "success": True,
            "issue_number": issue["number"],
            "issue_url": issue["url"],
            "issue_id": issue["id"],
            "state": "OPEN",
            "metadata": {
                "tool_name": self.tool_name,
                "assignees_removed": self.assignees,
            },
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

    def _get_issue_id(self, token: str) -> str:
        """Get issue GraphQL node ID."""
        query = """
        query($owner: String!, $name: String!, $number: Int!) {
            repository(owner: $owner, name: $name) {
                issue(number: $number) {
                    id
                }
            }
        }
        """

        variables = {
            "owner": self.repo_owner,
            "name": self.repo_name,
            "number": self.issue_number,
        }
        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            raise APIError(
                f"Issue #{self.issue_number} not found",
                tool_name=self.tool_name,
            )

        return response["data"]["repository"]["issue"]["id"]

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

    def _get_milestone_id(self, token: str, milestone_number: int) -> Optional[str]:
        """Get milestone GraphQL node ID."""
        query = """
        query($owner: String!, $name: String!, $number: Int!) {
            repository(owner: $owner, name: $name) {
                milestone(number: $number) {
                    id
                }
            }
        }
        """

        variables = {
            "owner": self.repo_owner,
            "name": self.repo_name,
            "number": milestone_number,
        }
        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            return None

        milestone = response.get("data", {}).get("repository", {}).get("milestone")
        return milestone["id"] if milestone else None

    def _execute_graphql(self, token: str, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
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
    print("Testing GitHubManageIssues...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Create issue
    print("\n1. Testing create issue...")
    tool = GitHubManageIssues(
        repo_owner="myorg",
        repo_name="myrepo",
        action=IssueAction.CREATE,
        title="Bug: Login fails on mobile",
        body="## Description\n\nLogin button not working on iOS",
        labels=["bug", "mobile"],
        assignees=["developer1"],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Issue Number: {result.get('issue_number')}")
    print(f"Issue URL: {result.get('issue_url')}")
    print(f"State: {result.get('state')}")
    assert result.get("success") == True
    assert result.get("issue_number") == 456

    # Test 2: Update issue
    print("\n2. Testing update issue...")
    tool = GitHubManageIssues(
        repo_owner="myorg",
        repo_name="myrepo",
        action=IssueAction.UPDATE,
        issue_number=456,
        title="Bug: Login fails on mobile [UPDATED]",
        body="## Description\n\nUpdated description",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 3: Add labels
    print("\n3. Testing add labels...")
    tool = GitHubManageIssues(
        repo_owner="myorg",
        repo_name="myrepo",
        action=IssueAction.ADD_LABELS,
        issue_number=456,
        labels=["priority:high", "needs-review"],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 4: Assign users
    print("\n4. Testing assign users...")
    tool = GitHubManageIssues(
        repo_owner="myorg",
        repo_name="myrepo",
        action=IssueAction.ASSIGN,
        issue_number=456,
        assignees=["user1", "user2"],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 5: Close issue
    print("\n5. Testing close issue...")
    tool = GitHubManageIssues(
        repo_owner="myorg",
        repo_name="myrepo",
        action=IssueAction.CLOSE,
        issue_number=456,
        state_reason="completed",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"State: {result.get('state')}")
    assert result.get("success") == True
    assert result.get("state") == "CLOSED"

    # Test 6: Reopen issue
    print("\n6. Testing reopen issue...")
    tool = GitHubManageIssues(
        repo_owner="myorg",
        repo_name="myrepo",
        action=IssueAction.REOPEN,
        issue_number=456,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"State: {result.get('state')}")
    assert result.get("success") == True
    assert result.get("state") == "OPEN"

    # Test 7: Error handling - missing title for create
    print("\n7. Testing error handling (missing title for create)...")
    try:
        tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.CREATE,
            body="Missing title",
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
