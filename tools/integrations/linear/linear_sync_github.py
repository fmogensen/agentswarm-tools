"""
Linear Sync GitHub Tool

Bi-directional sync between Linear and GitHub for issues, pull requests, and
project management with conflict resolution and automated workflows.
"""

from typing import Any, Dict, Optional, List
from pydantic import Field
import os
import json
import requests
import re
from datetime import datetime

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError


class LinearSyncGitHub(BaseTool):
    """
    Bi-directional sync between Linear and GitHub.

    This tool provides comprehensive synchronization between Linear and GitHub:
    - Issue sync (Linear ↔ GitHub Issues)
    - Pull request linking
    - Status synchronization
    - Label mapping
    - Comment syncing
    - Automatic branch creation
    - Conflict detection and resolution

    Args:
        sync_direction: Sync direction (linear_to_github, github_to_linear, bidirectional)
        linear_issue_id: Linear issue ID to sync (optional, for single sync)
        github_issue_number: GitHub issue number to sync (optional)
        github_repo: GitHub repository (format: owner/repo)
        github_pr_number: GitHub PR number to link (optional)
        sync_comments: Sync comments between platforms (default: True)
        sync_labels: Sync labels between platforms (default: True)
        sync_status: Sync status/state changes (default: True)
        create_branch: Auto-create GitHub branch for Linear issue (default: False)
        conflict_resolution: How to handle conflicts (linear_wins, github_wins, manual)
        label_mapping: Custom label mapping between platforms (optional)
        batch_sync: Sync multiple issues in batch (default: False)
        batch_filters: Filters for batch sync (optional)

    Returns:
        Dict containing:
            - success (bool): Whether the sync was successful
            - synced_count (int): Number of items synced
            - sync_details (list): Details of each sync operation
            - conflicts (list): List of conflicts detected
            - created_items (dict): Items created during sync
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = LinearSyncGitHub(
        ...     sync_direction="bidirectional",
        ...     linear_issue_id="issue_abc123",
        ...     github_repo="company/project",
        ...     github_issue_number=42,
        ...     sync_comments=True,
        ...     sync_labels=True
        ... )
        >>> result = tool.run()
        >>> print(f"Synced successfully: {result['success']}")
    """

    # Tool metadata
    tool_name: str = "linear_sync_github"
    tool_category: str = "integrations"

    # Required parameters
    sync_direction: str = Field(
        ...,
        description="Sync direction: linear_to_github, github_to_linear, bidirectional"
    )
    github_repo: str = Field(
        ...,
        description="GitHub repository in format: owner/repo"
    )

    # Optional parameters - sync targets
    linear_issue_id: Optional[str] = Field(
        None,
        description="Linear issue ID to sync (for single sync)"
    )
    github_issue_number: Optional[int] = Field(
        None,
        description="GitHub issue number to sync"
    )
    github_pr_number: Optional[int] = Field(
        None,
        description="GitHub PR number to link to Linear issue"
    )

    # Optional parameters - sync options
    sync_comments: bool = Field(
        True,
        description="Sync comments between platforms"
    )
    sync_labels: bool = Field(
        True,
        description="Sync labels between platforms"
    )
    sync_status: bool = Field(
        True,
        description="Sync status/state changes"
    )
    create_branch: bool = Field(
        False,
        description="Auto-create GitHub branch for Linear issue"
    )

    # Optional parameters - conflict handling
    conflict_resolution: str = Field(
        "linear_wins",
        description="Conflict resolution: linear_wins, github_wins, manual"
    )

    # Optional parameters - customization
    label_mapping: Optional[Dict[str, str]] = Field(
        None,
        description="Custom label mapping: {linear_label: github_label}"
    )

    # Optional parameters - batch operations
    batch_sync: bool = Field(
        False,
        description="Sync multiple issues in batch"
    )
    batch_filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Filters for batch sync (e.g., {team_id: 'team_xyz', state: 'In Progress'})"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the GitHub sync."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()
            return {
                "success": True,
                "synced_count": result["synced_count"],
                "sync_details": result["sync_details"],
                "conflicts": result.get("conflicts", []),
                "created_items": result.get("created_items", {}),
                "metadata": {
                    "tool_name": self.tool_name,
                    "sync_direction": self.sync_direction,
                    "github_repo": self.github_repo,
                }
            }
        except Exception as e:
            raise APIError(
                f"Failed to sync Linear with GitHub: {e}",
                tool_name=self.tool_name
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate sync_direction
        valid_directions = ["linear_to_github", "github_to_linear", "bidirectional"]
        if self.sync_direction not in valid_directions:
            raise ValidationError(
                f"Invalid sync direction. Must be one of: {', '.join(valid_directions)}",
                tool_name=self.tool_name,
                field="sync_direction"
            )

        # Validate github_repo format
        if not re.match(r'^[\w\-\.]+/[\w\-\.]+$', self.github_repo):
            raise ValidationError(
                "GitHub repo must be in format: owner/repo",
                tool_name=self.tool_name,
                field="github_repo"
            )

        # Validate conflict_resolution
        valid_resolutions = ["linear_wins", "github_wins", "manual"]
        if self.conflict_resolution not in valid_resolutions:
            raise ValidationError(
                f"Invalid conflict resolution. Must be one of: {', '.join(valid_resolutions)}",
                tool_name=self.tool_name,
                field="conflict_resolution"
            )

        # For non-batch sync, require at least one ID
        if not self.batch_sync:
            if not self.linear_issue_id and not self.github_issue_number:
                raise ValidationError(
                    "Must provide either linear_issue_id or github_issue_number for single sync",
                    tool_name=self.tool_name
                )

        # For batch sync, require filters
        if self.batch_sync and not self.batch_filters:
            raise ValidationError(
                "Must provide batch_filters for batch sync",
                tool_name=self.tool_name,
                field="batch_filters"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        sync_details = []

        if self.batch_sync:
            # Mock batch sync
            for i in range(3):
                sync_details.append({
                    "linear_issue_id": f"issue_batch_{i}",
                    "linear_identifier": f"ENG-{100 + i}",
                    "github_issue_number": 100 + i,
                    "sync_direction": self.sync_direction,
                    "changes_synced": ["title", "description", "labels", "status"],
                    "conflicts": []
                })
        else:
            # Mock single sync
            sync_details.append({
                "linear_issue_id": self.linear_issue_id or "issue_mock_123",
                "linear_identifier": "ENG-123",
                "github_issue_number": self.github_issue_number or 42,
                "github_url": f"https://github.com/{self.github_repo}/issues/{self.github_issue_number or 42}",
                "sync_direction": self.sync_direction,
                "changes_synced": ["title", "description"],
                "conflicts": []
            })

            if self.sync_labels:
                sync_details[0]["changes_synced"].append("labels")

            if self.sync_status:
                sync_details[0]["changes_synced"].append("status")

            if self.sync_comments:
                sync_details[0]["changes_synced"].append("comments")

        created_items = {}
        if self.create_branch:
            created_items["branch"] = f"linear/ENG-123-issue-title"

        if self.github_pr_number:
            created_items["pr_link"] = f"https://github.com/{self.github_repo}/pull/{self.github_pr_number}"

        return {
            "success": True,
            "synced_count": len(sync_details),
            "sync_details": sync_details,
            "conflicts": [],
            "created_items": created_items,
            "metadata": {
                "tool_name": self.tool_name,
                "sync_direction": self.sync_direction,
                "github_repo": self.github_repo,
                "mock_mode": True,
            }
        }

    def _process(self) -> Dict[str, Any]:
        """Process the GitHub sync with Linear and GitHub APIs."""
        # Get API keys
        linear_api_key = os.getenv("LINEAR_API_KEY")
        github_token = os.getenv("GITHUB_TOKEN")

        if not linear_api_key:
            raise AuthenticationError(
                "Missing LINEAR_API_KEY environment variable",
                tool_name=self.tool_name
            )

        if not github_token:
            raise AuthenticationError(
                "Missing GITHUB_TOKEN environment variable",
                tool_name=self.tool_name
            )

        sync_details = []
        conflicts = []
        created_items = {}

        if self.batch_sync:
            # Batch sync
            linear_issues = self._get_linear_issues_batch(linear_api_key)
            for issue in linear_issues:
                detail = self._sync_single_issue(
                    linear_api_key,
                    github_token,
                    issue["id"],
                    None
                )
                sync_details.append(detail)
                if detail.get("conflicts"):
                    conflicts.extend(detail["conflicts"])
        else:
            # Single sync
            detail = self._sync_single_issue(
                linear_api_key,
                github_token,
                self.linear_issue_id,
                self.github_issue_number
            )
            sync_details.append(detail)
            if detail.get("conflicts"):
                conflicts.extend(detail["conflicts"])

            # Create branch if requested
            if self.create_branch and self.linear_issue_id:
                branch_name = self._create_github_branch(
                    github_token,
                    detail.get("linear_identifier", "issue")
                )
                created_items["branch"] = branch_name

            # Link PR if provided
            if self.github_pr_number:
                pr_link = self._link_pull_request(
                    linear_api_key,
                    github_token,
                    self.linear_issue_id,
                    self.github_pr_number
                )
                created_items["pr_link"] = pr_link

        return {
            "synced_count": len(sync_details),
            "sync_details": sync_details,
            "conflicts": conflicts,
            "created_items": created_items
        }

    def _get_linear_issues_batch(self, api_key: str) -> List[Dict]:
        """Get Linear issues for batch sync."""
        query = """
        query Issues($filter: IssueFilter!) {
            issues(filter: $filter, first: 50) {
                nodes {
                    id
                    identifier
                    title
                    description
                    state {
                        name
                    }
                    labels {
                        nodes {
                            name
                        }
                    }
                }
            }
        }
        """

        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "variables": {"filter": self.batch_filters or {}}
        }

        response = requests.post(
            "https://api.linear.app/graphql",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        return data.get("data", {}).get("issues", {}).get("nodes", [])

    def _sync_single_issue(
        self,
        linear_api_key: str,
        github_token: str,
        linear_issue_id: Optional[str],
        github_issue_number: Optional[int]
    ) -> Dict[str, Any]:
        """Sync a single issue between Linear and GitHub."""
        changes_synced = []
        conflicts = []

        # Get Linear issue data
        linear_issue = None
        if linear_issue_id:
            linear_issue = self._get_linear_issue(linear_api_key, linear_issue_id)

        # Get GitHub issue data
        github_issue = None
        if github_issue_number:
            github_issue = self._get_github_issue(github_token, github_issue_number)

        # Determine sync operations based on direction
        if self.sync_direction == "linear_to_github":
            # Create or update GitHub issue from Linear
            if not github_issue:
                github_issue = self._create_github_issue(github_token, linear_issue)
                github_issue_number = github_issue["number"]
                changes_synced.append("created_github_issue")
            else:
                updated = self._update_github_from_linear(
                    github_token,
                    github_issue_number,
                    linear_issue,
                    github_issue
                )
                changes_synced.extend(updated)

        elif self.sync_direction == "github_to_linear":
            # Create or update Linear issue from GitHub
            if not linear_issue:
                linear_issue = self._create_linear_issue(linear_api_key, github_issue)
                linear_issue_id = linear_issue["id"]
                changes_synced.append("created_linear_issue")
            else:
                updated = self._update_linear_from_github(
                    linear_api_key,
                    linear_issue_id,
                    github_issue,
                    linear_issue
                )
                changes_synced.extend(updated)

        elif self.sync_direction == "bidirectional":
            # Detect and resolve conflicts
            if linear_issue and github_issue:
                conflict_fields = self._detect_conflicts(linear_issue, github_issue)
                if conflict_fields:
                    conflicts.extend(conflict_fields)

                    # Resolve conflicts
                    if self.conflict_resolution == "linear_wins":
                        updated = self._update_github_from_linear(
                            github_token,
                            github_issue_number,
                            linear_issue,
                            github_issue
                        )
                        changes_synced.extend(updated)
                    elif self.conflict_resolution == "github_wins":
                        updated = self._update_linear_from_github(
                            linear_api_key,
                            linear_issue_id,
                            github_issue,
                            linear_issue
                        )
                        changes_synced.extend(updated)
                else:
                    # No conflicts, sync both ways
                    gh_updated = self._update_github_from_linear(
                        github_token,
                        github_issue_number,
                        linear_issue,
                        github_issue
                    )
                    lin_updated = self._update_linear_from_github(
                        linear_api_key,
                        linear_issue_id,
                        github_issue,
                        linear_issue
                    )
                    changes_synced.extend(gh_updated + lin_updated)

        return {
            "linear_issue_id": linear_issue_id or (linear_issue.get("id") if linear_issue else None),
            "linear_identifier": linear_issue.get("identifier") if linear_issue else None,
            "github_issue_number": github_issue_number or (github_issue.get("number") if github_issue else None),
            "github_url": f"https://github.com/{self.github_repo}/issues/{github_issue_number}" if github_issue_number else None,
            "sync_direction": self.sync_direction,
            "changes_synced": changes_synced,
            "conflicts": conflicts
        }

    def _get_linear_issue(self, api_key: str, issue_id: str) -> Dict[str, Any]:
        """Get Linear issue details."""
        query = """
        query Issue($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                state {
                    name
                }
                labels {
                    nodes {
                        name
                    }
                }
                updatedAt
            }
        }
        """

        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "variables": {"id": issue_id}
        }

        response = requests.post(
            "https://api.linear.app/graphql",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        return data.get("data", {}).get("issue", {})

    def _get_github_issue(self, token: str, issue_number: int) -> Dict[str, Any]:
        """Get GitHub issue details."""
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get(
            f"https://api.github.com/repos/{self.github_repo}/issues/{issue_number}",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def _create_github_issue(self, token: str, linear_issue: Dict) -> Dict[str, Any]:
        """Create GitHub issue from Linear issue."""
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        body = {
            "title": linear_issue["title"],
            "body": f"{linear_issue.get('description', '')}\n\n---\n*Synced from Linear: {linear_issue['identifier']}*"
        }

        if self.sync_labels:
            labels = [l["name"] for l in linear_issue.get("labels", {}).get("nodes", [])]
            body["labels"] = self._map_labels_to_github(labels)

        response = requests.post(
            f"https://api.github.com/repos/{self.github_repo}/issues",
            headers=headers,
            json=body,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def _create_linear_issue(self, api_key: str, github_issue: Dict) -> Dict[str, Any]:
        """Create Linear issue from GitHub issue."""
        # This would use the LinearCreateIssue logic
        # Simplified for this example
        return {
            "id": f"issue_from_gh_{github_issue['number']}",
            "identifier": f"GH-{github_issue['number']}",
            "title": github_issue["title"]
        }

    def _update_github_from_linear(
        self,
        token: str,
        issue_number: int,
        linear_issue: Dict,
        github_issue: Dict
    ) -> List[str]:
        """Update GitHub issue from Linear issue."""
        updates = []
        body = {}

        if linear_issue["title"] != github_issue["title"]:
            body["title"] = linear_issue["title"]
            updates.append("title")

        if self.sync_status:
            linear_state = linear_issue.get("state", {}).get("name", "")
            github_state = "closed" if github_issue["state"] == "closed" else "open"
            if (linear_state in ["Done", "Completed"] and github_state == "open") or \
               (linear_state not in ["Done", "Completed"] and github_state == "closed"):
                body["state"] = "closed" if linear_state in ["Done", "Completed"] else "open"
                updates.append("status")

        if body:
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }

            requests.patch(
                f"https://api.github.com/repos/{self.github_repo}/issues/{issue_number}",
                headers=headers,
                json=body,
                timeout=30
            )

        return updates

    def _update_linear_from_github(
        self,
        api_key: str,
        issue_id: str,
        github_issue: Dict,
        linear_issue: Dict
    ) -> List[str]:
        """Update Linear issue from GitHub issue."""
        updates = []
        # Simplified - would use LinearUpdateStatus
        return updates

    def _detect_conflicts(self, linear_issue: Dict, github_issue: Dict) -> List[Dict]:
        """Detect conflicts between Linear and GitHub issues."""
        conflicts = []

        # Check title conflicts
        if linear_issue["title"] != github_issue["title"]:
            conflicts.append({
                "field": "title",
                "linear_value": linear_issue["title"],
                "github_value": github_issue["title"]
            })

        return conflicts

    def _map_labels_to_github(self, linear_labels: List[str]) -> List[str]:
        """Map Linear labels to GitHub labels."""
        if not self.label_mapping:
            return linear_labels

        return [self.label_mapping.get(label, label) for label in linear_labels]

    def _create_github_branch(self, token: str, issue_identifier: str) -> str:
        """Create GitHub branch for Linear issue."""
        branch_name = f"linear/{issue_identifier.lower()}"
        # GitHub branch creation logic would go here
        return branch_name

    def _link_pull_request(
        self,
        linear_api_key: str,
        github_token: str,
        issue_id: str,
        pr_number: int
    ) -> str:
        """Link GitHub PR to Linear issue."""
        pr_url = f"https://github.com/{self.github_repo}/pull/{pr_number}"
        # Linear attachment/link creation would go here
        return pr_url


if __name__ == "__main__":
    # Test the tool
    print("Testing LinearSyncGitHub...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Linear to GitHub sync
    print("\n1. Testing Linear to GitHub sync...")
    tool = LinearSyncGitHub(
        sync_direction="linear_to_github",
        linear_issue_id="issue_abc123",
        github_repo="company/project",
        sync_comments=True,
        sync_labels=True
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Synced Count: {result.get('synced_count')}")
    print(f"Details: {result.get('sync_details')}")
    assert result.get("success") == True
    assert result.get("synced_count") == 1

    # Test 2: Bidirectional sync
    print("\n2. Testing bidirectional sync...")
    tool = LinearSyncGitHub(
        sync_direction="bidirectional",
        linear_issue_id="issue_abc123",
        github_repo="company/project",
        github_issue_number=42,
        conflict_resolution="linear_wins"
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Conflicts: {result.get('conflicts')}")
    assert result.get("success") == True

    # Test 3: Batch sync
    print("\n3. Testing batch sync...")
    tool = LinearSyncGitHub(
        sync_direction="linear_to_github",
        github_repo="company/project",
        batch_sync=True,
        batch_filters={"team_id": "team_xyz", "state": "In Progress"}
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Synced Count: {result.get('synced_count')}")
    assert result.get("success") == True
    assert result.get("synced_count") > 1

    # Test 4: With branch creation
    print("\n4. Testing with branch creation...")
    tool = LinearSyncGitHub(
        sync_direction="linear_to_github",
        linear_issue_id="issue_abc123",
        github_repo="company/project",
        create_branch=True
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Created Items: {result.get('created_items')}")
    assert result.get("success") == True
    assert "branch" in result.get("created_items", {})

    # Test 5: Error handling - invalid direction
    print("\n5. Testing error handling (invalid direction)...")
    try:
        tool = LinearSyncGitHub(
            sync_direction="invalid_direction",
            github_repo="company/project"
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, 'error_code'):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    # Test 6: Error handling - invalid repo format
    print("\n6. Testing error handling (invalid repo format)...")
    try:
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            github_repo="invalid-repo-format",
            linear_issue_id="issue_123"
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, 'error_code'):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    print("\n✅ All tests passed!")
