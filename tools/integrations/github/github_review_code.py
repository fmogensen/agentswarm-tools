"""
GitHub Review Code Tool

Submit pull request reviews using GitHub's GraphQL API.
Supports comments, approve/reject, line-specific feedback, and suggestions.
"""

import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class ReviewEvent(str, Enum):
    """Review event types."""

    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    COMMENT = "COMMENT"


class GitHubReviewCode(BaseTool):
    """
    Submit a code review on a GitHub pull request.

    This tool submits PR reviews with support for overall comments, line-specific
    feedback, code suggestions, and approve/request changes actions.

    Args:
        repo_owner: GitHub repository owner (username or organization)
        repo_name: Repository name
        pr_number: Pull request number to review
        event: Review action (APPROVE, REQUEST_CHANGES, COMMENT)
        body: Overall review comment (supports markdown)
        comments: List of line-specific comments with path, position, and body
        commit_id: Specific commit SHA to review (optional, defaults to latest)

    Returns:
        Dict containing:
            - success (bool): Whether the review was submitted successfully
            - review_id (str): Review ID
            - review_url (str): URL to the review
            - state (str): Review state (APPROVED, CHANGES_REQUESTED, COMMENTED)
            - submitted_at (str): Review submission timestamp
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = GitHubReviewCode(
        ...     repo_owner="myorg",
        ...     repo_name="myrepo",
        ...     pr_number=123,
        ...     event="APPROVE",
        ...     body="LGTM! Great work on this feature.",
        ...     comments=[
        ...         {
        ...             "path": "src/main.py",
        ...             "position": 10,
        ...             "body": "Consider adding error handling here"
        ...         }
        ...     ]
        ... )
        >>> result = tool.run()
        >>> print(result['state'])
        'APPROVED'
    """

    # Tool metadata
    tool_name: str = "github_review_code"
    tool_category: str = "integrations"

    # Required parameters
    repo_owner: str = Field(
        ...,
        description="Repository owner (username or organization)",
        min_length=1,
        max_length=100,
    )
    repo_name: str = Field(..., description="Repository name", min_length=1, max_length=100)
    pr_number: int = Field(..., description="Pull request number", ge=1)
    event: ReviewEvent = Field(..., description="Review action (APPROVE, REQUEST_CHANGES, COMMENT)")

    # Optional parameters
    body: Optional[str] = Field(None, description="Overall review comment (markdown supported)")
    comments: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Line-specific comments with path, position, and body",
    )
    commit_id: Optional[str] = Field(None, description="Specific commit SHA to review")

    def _execute(self) -> Dict[str, Any]:
        """Execute the code review."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            # Submit review using GraphQL
            review_data = self._submit_review_graphql()

            return {
                "success": True,
                "review_id": review_data["id"],
                "review_url": review_data["url"],
                "state": review_data["state"],
                "submitted_at": review_data["submitted_at"],
                "metadata": {
                    "tool_name": self.tool_name,
                    "repo": f"{self.repo_owner}/{self.repo_name}",
                    "pr_number": self.pr_number,
                    "event": self.event.value,
                },
            }
        except Exception as e:
            raise APIError(f"Failed to submit review: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate PR number
        if self.pr_number < 1:
            raise ValidationError("pr_number must be positive", tool_name=self.tool_name)

        # Validate body exists for APPROVE/REQUEST_CHANGES
        if self.event in [ReviewEvent.APPROVE, ReviewEvent.REQUEST_CHANGES]:
            if not self.body or not self.body.strip():
                raise ValidationError(
                    f"{self.event.value} requires a body comment",
                    tool_name=self.tool_name,
                )

        # Validate comments format
        if self.comments:
            for i, comment in enumerate(self.comments):
                if "path" not in comment:
                    raise ValidationError(
                        f"Comment {i} missing 'path' field", tool_name=self.tool_name
                    )
                if "body" not in comment:
                    raise ValidationError(
                        f"Comment {i} missing 'body' field", tool_name=self.tool_name
                    )
                # Either position (line) or start_line/end_line required
                if "position" not in comment and "line" not in comment:
                    raise ValidationError(
                        f"Comment {i} missing 'position' or 'line' field",
                        tool_name=self.tool_name,
                    )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        state_map = {
            ReviewEvent.APPROVE: "APPROVED",
            ReviewEvent.REQUEST_CHANGES: "CHANGES_REQUESTED",
            ReviewEvent.COMMENT: "COMMENTED",
        }

        return {
            "success": True,
            "review_id": "PRR_mock_1234567890",
            "review_url": f"https://github.com/{self.repo_owner}/{self.repo_name}/pull/{self.pr_number}#pullrequestreview-mock123",
            "state": state_map[self.event],
            "submitted_at": "2024-01-15T10:30:00Z",
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "pr_number": self.pr_number,
                "event": self.event.value,
                "mock_mode": True,
            },
        }

    def _submit_review_graphql(self) -> Dict[str, Any]:
        """Submit review using GitHub GraphQL API."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise AuthenticationError(
                "Missing GITHUB_TOKEN environment variable", tool_name=self.tool_name
            )

        # Get PR node ID
        pr_id = self._get_pr_node_id(token)

        # Get commit ID if not provided
        commit_oid = self.commit_id or self._get_latest_commit(token, pr_id)

        # Build review comments
        review_comments = []
        if self.comments:
            for comment in self.comments:
                review_comment = {
                    "path": comment["path"],
                    "body": comment["body"],
                }
                # Handle different position formats
                if "position" in comment:
                    review_comment["position"] = comment["position"]
                elif "line" in comment:
                    review_comment["position"] = comment["line"]

                review_comments.append(review_comment)

        # GraphQL mutation to submit review
        mutation = """
        mutation($input: AddPullRequestReviewInput!) {
            addPullRequestReview(input: $input) {
                pullRequestReview {
                    id
                    url
                    state
                    submittedAt
                    body
                    comments(first: 10) {
                        totalCount
                    }
                }
            }
        }
        """

        variables = {
            "input": {
                "pullRequestId": pr_id,
                "commitOID": commit_oid,
                "event": self.event.value,
                "body": self.body or "",
            }
        }

        # Add comments if provided
        if review_comments:
            variables["input"]["comments"] = review_comments

        response = self._execute_graphql(token, mutation, variables)

        if "errors" in response:
            error_msg = response["errors"][0].get("message", "Unknown error")
            raise APIError(f"GraphQL error: {error_msg}", tool_name=self.tool_name)

        review = response["data"]["addPullRequestReview"]["pullRequestReview"]
        return {
            "id": review["id"],
            "url": review["url"],
            "state": review["state"],
            "submitted_at": review["submittedAt"],
        }

    def _get_pr_node_id(self, token: str) -> str:
        """Get PR GraphQL node ID."""
        query = """
        query($owner: String!, $name: String!, $number: Int!) {
            repository(owner: $owner, name: $name) {
                pullRequest(number: $number) {
                    id
                }
            }
        }
        """

        variables = {
            "owner": self.repo_owner,
            "name": self.repo_name,
            "number": self.pr_number,
        }

        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            raise APIError(
                f"PR #{self.pr_number} not found in {self.repo_owner}/{self.repo_name}",
                tool_name=self.tool_name,
            )

        return response["data"]["repository"]["pullRequest"]["id"]

    def _get_latest_commit(self, token: str, pr_id: str) -> str:
        """Get latest commit SHA from PR."""
        query = """
        query($id: ID!) {
            node(id: $id) {
                ... on PullRequest {
                    commits(last: 1) {
                        nodes {
                            commit {
                                oid
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {"id": pr_id}
        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            raise APIError("Failed to get latest commit", tool_name=self.tool_name)

        commits = response["data"]["node"]["commits"]["nodes"]
        if not commits:
            raise APIError("PR has no commits", tool_name=self.tool_name)

        return commits[0]["commit"]["oid"]

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
    print("Testing GitHubReviewCode...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Approve PR
    print("\n1. Testing approve review...")
    tool = GitHubReviewCode(
        repo_owner="myorg",
        repo_name="myrepo",
        pr_number=123,
        event=ReviewEvent.APPROVE,
        body="LGTM! Great work on this feature.",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Review ID: {result.get('review_id')}")
    print(f"State: {result.get('state')}")
    print(f"URL: {result.get('review_url')}")
    assert result.get("success") == True
    assert result.get("state") == "APPROVED"

    # Test 2: Request changes with comments
    print("\n2. Testing request changes with comments...")
    tool = GitHubReviewCode(
        repo_owner="myorg",
        repo_name="myrepo",
        pr_number=123,
        event=ReviewEvent.REQUEST_CHANGES,
        body="Please address the following issues before merging.",
        comments=[
            {
                "path": "src/main.py",
                "position": 10,
                "body": "Add error handling here",
            },
            {
                "path": "src/utils.py",
                "line": 25,
                "body": "This function needs documentation",
            },
        ],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"State: {result.get('state')}")
    assert result.get("success") == True
    assert result.get("state") == "CHANGES_REQUESTED"

    # Test 3: Comment only (no approval)
    print("\n3. Testing comment-only review...")
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
                "body": "Consider adding more examples here",
            }
        ],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"State: {result.get('state')}")
    assert result.get("success") == True
    assert result.get("state") == "COMMENTED"

    # Test 4: Error handling - missing body for APPROVE
    print("\n4. Testing error handling (missing body for APPROVE)...")
    try:
        tool = GitHubReviewCode(
            repo_owner="myorg",
            repo_name="myrepo",
            pr_number=123,
            event=ReviewEvent.APPROVE,
            body="",
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if "error" in str(e):
            error_dict = eval(str(e))
            print(f"Correctly caught error: {error_dict['error']['message']}")
        else:
            print(f"Correctly caught error: {str(e)}")

    # Test 5: Review with specific commit
    print("\n5. Testing review with specific commit...")
    tool = GitHubReviewCode(
        repo_owner="myorg",
        repo_name="myrepo",
        pr_number=123,
        event=ReviewEvent.APPROVE,
        body="Approved commit abc123",
        commit_id="abc123def456",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    print("\n✅ All tests passed!")
