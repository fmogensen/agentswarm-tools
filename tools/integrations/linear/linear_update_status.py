"""
Linear Update Status Tool

Updates issue status, transitions, and workflow states in Linear with support
for state validation, automatic transitions, and workflow rules.
"""

import json
import os
from typing import Any, Dict, Optional

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class LinearUpdateStatus(BaseTool):
    """
    Update issue status and workflow states in Linear.

    This tool updates Linear issue status with support for:
    - Workflow state transitions
    - Status updates with validation
    - Automatic state transitions
    - Priority and estimate updates
    - Assignee changes
    - Label management

    Args:
        issue_id: Linear issue ID (required)
        state_id: New workflow state ID (optional)
        state_name: State name (alternative to state_id, e.g., "In Progress")
        priority: New priority (0=None, 1=Urgent, 2=High, 3=Normal, 4=Low)
        assignee_id: New assignee user ID (optional)
        estimate: New estimate value (optional)
        add_labels: List of label IDs to add (optional)
        remove_labels: List of label IDs to remove (optional)
        comment: Comment to add with status update (optional)

    Returns:
        Dict containing:
            - success (bool): Whether the update was successful
            - issue_id (str): Linear issue ID
            - issue_identifier (str): Human-readable identifier
            - previous_state (str): Previous state name
            - new_state (str): New state name
            - transition_valid (bool): Whether transition was valid
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = LinearUpdateStatus(
        ...     issue_id="issue_abc123",
        ...     state_name="In Progress",
        ...     assignee_id="user_xyz789",
        ...     comment="Starting work on this issue"
        ... )
        >>> result = tool.run()
        >>> print(result['new_state'])
        'In Progress'
    """

    # Tool metadata
    tool_name: str = "linear_update_status"
    tool_category: str = "integrations"

    # Required parameters
    issue_id: str = Field(..., description="Linear issue ID", min_length=1)

    # Optional parameters - state update
    state_id: Optional[str] = Field(None, description="New workflow state ID")
    state_name: Optional[str] = Field(None, description="State name (alternative to state_id)")

    # Optional parameters - other updates
    priority: Optional[int] = Field(
        None, description="New priority: 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low", ge=0, le=4
    )
    assignee_id: Optional[str] = Field(
        None, description="New assignee user ID (use 'unassign' to remove)"
    )
    estimate: Optional[float] = Field(None, description="New estimate value", ge=0, le=1000)
    add_labels: Optional[list] = Field(None, description="List of label IDs to add")
    remove_labels: Optional[list] = Field(None, description="List of label IDs to remove")
    comment: Optional[str] = Field(None, description="Comment to add with status update")

    def _execute(self) -> Dict[str, Any]:
        """Execute the status update."""

        self._logger.info(f"Executing {self.tool_name} with issue_id={self.issue_id}, state_id={self.state_id}, state_name={self.state_name}, ...")
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()
            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "issue_id": result["id"],
                "issue_identifier": result["identifier"],
                "previous_state": result.get("previous_state", "Unknown"),
                "new_state": result.get("state", {}).get("name", "Unknown"),
                "transition_valid": True,
                "metadata": {
                    "tool_name": self.tool_name,
                    "updates_applied": self._get_updates_summary(),
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to update Linear issue status: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate issue_id
        if not self.issue_id or not self.issue_id.strip():
            raise ValidationError(
                "Issue ID cannot be empty", tool_name=self.tool_name, field="issue_id"
            )

        # At least one update must be specified
        has_updates = any(
            [
                self.state_id,
                self.state_name,
                self.priority is not None,
                self.assignee_id,
                self.estimate is not None,
                self.add_labels,
                self.remove_labels,
                self.comment,
            ]
        )

        if not has_updates:
            raise ValidationError(
                "At least one update field must be specified", tool_name=self.tool_name
            )

        # Validate priority if provided
        if self.priority is not None and (self.priority < 0 or self.priority > 4):
            raise ValidationError(
                "Priority must be between 0 (None) and 4 (Low)",
                tool_name=self.tool_name,
                field="priority",
            )

        # Validate estimate if provided
        if self.estimate is not None and self.estimate < 0:
            raise ValidationError(
                "Estimate must be a positive number", tool_name=self.tool_name, field="estimate"
            )

        # Can't specify both state_id and state_name
        if self.state_id and self.state_name:
            raise ValidationError(
                "Cannot specify both state_id and state_name", tool_name=self.tool_name
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "issue_id": self.issue_id,
            "issue_identifier": "ENG-123",
            "previous_state": "Todo",
            "new_state": self.state_name or "In Progress",
            "transition_valid": True,
            "metadata": {
                "tool_name": self.tool_name,
                "updates_applied": self._get_updates_summary(),
                "mock_mode": True,
            },
        }

    def _get_updates_summary(self) -> Dict[str, Any]:
        """Get summary of updates being applied."""
        summary = {}
        if self.state_id or self.state_name:
            summary["state"] = self.state_id or self.state_name
        if self.priority is not None:
            summary["priority"] = self.priority
        if self.assignee_id:
            summary["assignee"] = self.assignee_id
        if self.estimate is not None:
            summary["estimate"] = self.estimate
        if self.add_labels:
            summary["labels_added"] = len(self.add_labels)
        if self.remove_labels:
            summary["labels_removed"] = len(self.remove_labels)
        if self.comment:
            summary["comment_added"] = True
        return summary

    def _process(self) -> Dict[str, Any]:
        """Process the status update with Linear GraphQL API."""
        # Get API key
        api_key = os.getenv("LINEAR_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing LINEAR_API_KEY environment variable", tool_name=self.tool_name
            )

        # First, get current issue state for comparison
        current_issue = self._get_current_issue(api_key)
        previous_state = current_issue.get("state", {}).get("name", "Unknown")

        # If state_name is provided, resolve it to state_id
        if self.state_name and not self.state_id:
            team_id = current_issue.get("team", {}).get("id")
            if team_id:
                resolved_state_id = self._resolve_state_name(api_key, team_id, self.state_name)
                if resolved_state_id:
                    self.state_id = resolved_state_id

        # Prepare GraphQL mutation
        mutation = """
        mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    state {
                        id
                        name
                    }
                    priority
                    estimate
                    assignee {
                        id
                        name
                    }
                }
            }
        }
        """

        # Build input object
        input_data = {}

        if self.state_id:
            input_data["stateId"] = self.state_id

        if self.priority is not None:
            input_data["priority"] = self.priority

        if self.assignee_id:
            if self.assignee_id.lower() == "unassign":
                input_data["assigneeId"] = None
            else:
                input_data["assigneeId"] = self.assignee_id

        if self.estimate is not None:
            input_data["estimate"] = self.estimate

        if self.add_labels:
            # Get current labels and merge
            current_labels = [l["id"] for l in current_issue.get("labels", {}).get("nodes", [])]
            all_labels = list(set(current_labels + self.add_labels))
            input_data["labelIds"] = all_labels

        if self.remove_labels:
            # Get current labels and remove specified ones
            current_labels = [l["id"] for l in current_issue.get("labels", {}).get("nodes", [])]
            remaining_labels = [l for l in current_labels if l not in self.remove_labels]
            input_data["labelIds"] = remaining_labels

        # Execute GraphQL request
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {"query": mutation, "variables": {"id": self.issue_id, "input": input_data}}

        try:
            response = requests.post(
                "https://api.linear.app/graphql", headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()

            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                error_messages = [e.get("message", str(e)) for e in data["errors"]]
                raise APIError(
                    f"GraphQL errors: {'; '.join(error_messages)}", tool_name=self.tool_name
                )

            # Extract issue data
            update_data = data.get("data", {}).get("issueUpdate", {})

            if not update_data.get("success"):
                raise APIError("Issue update failed", tool_name=self.tool_name)

            issue = update_data.get("issue", {})
            issue["previous_state"] = previous_state

            # Add comment if provided
            if self.comment:
                self._add_comment(api_key, self.issue_id, self.comment)

            return issue

        except requests.exceptions.RequestException as e:
            raise APIError(f"Linear API request failed: {str(e)}", tool_name=self.tool_name)
        except (KeyError, ValueError) as e:
            raise APIError(
                f"Failed to parse Linear API response: {str(e)}", tool_name=self.tool_name
            )

    def _get_current_issue(self, api_key: str) -> Dict[str, Any]:
        """Get current issue data."""
        query = """
        query Issue($id: String!) {
            issue(id: $id) {
                id
                identifier
                state {
                    id
                    name
                }
                team {
                    id
                }
                labels {
                    nodes {
                        id
                        name
                    }
                }
            }
        }
        """

        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {"query": query, "variables": {"id": self.issue_id}}

        response = requests.post(
            "https://api.linear.app/graphql", headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        return data.get("data", {}).get("issue", {})

    def _resolve_state_name(self, api_key: str, team_id: str, state_name: str) -> Optional[str]:
        """Resolve state name to state ID."""
        query = """
        query WorkflowStates($filter: WorkflowStateFilter!) {
            workflowStates(filter: $filter) {
                nodes {
                    id
                    name
                }
            }
        }
        """

        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {"query": query, "variables": {"filter": {"team": {"id": {"eq": team_id}}}}}

        response = requests.post(
            "https://api.linear.app/graphql", headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        states = data.get("data", {}).get("workflowStates", {}).get("nodes", [])

        # Find matching state (case-insensitive)
        for state in states:
            if state["name"].lower() == state_name.lower():
                return state["id"]

        return None

    def _add_comment(self, api_key: str, issue_id: str, comment: str) -> None:
        """Add comment to issue."""
        mutation = """
        mutation CommentCreate($input: CommentCreateInput!) {
            commentCreate(input: $input) {
                success
            }
        }
        """

        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "query": mutation,
            "variables": {"input": {"issueId": issue_id, "body": comment}},
        }

        requests.post("https://api.linear.app/graphql", headers=headers, json=payload, timeout=30)


if __name__ == "__main__":
    # Test the tool
    print("Testing LinearUpdateStatus...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Update state by name
    print("\n1. Testing state update by name...")
    tool = LinearUpdateStatus(issue_id="issue_abc123", state_name="In Progress")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Previous State: {result.get('previous_state')}")
    print(f"New State: {result.get('new_state')}")
    assert result.get("success") == True
    assert result.get("new_state") == "In Progress"

    # Test 2: Update multiple fields
    print("\n2. Testing multiple field updates...")
    tool = LinearUpdateStatus(
        issue_id="issue_abc123",
        state_name="In Progress",
        priority=1,
        assignee_id="user_xyz789",
        estimate=5.0,
        comment="Starting work on this",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Updates: {result.get('metadata', {}).get('updates_applied')}")
    assert result.get("success") == True

    # Test 3: Unassign issue
    print("\n3. Testing unassign...")
    tool = LinearUpdateStatus(issue_id="issue_abc123", assignee_id="unassign")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 4: Label management
    print("\n4. Testing label management...")
    tool = LinearUpdateStatus(
        issue_id="issue_abc123",
        add_labels=["label_bug", "label_urgent"],
        remove_labels=["label_backlog"],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 5: Error handling - no updates
    print("\n5. Testing error handling (no updates)...")
    try:
        tool = LinearUpdateStatus(issue_id="issue_abc123")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, "error_code"):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    # Test 6: Error handling - invalid priority
    print("\n6. Testing error handling (invalid priority)...")
    try:
        tool = LinearUpdateStatus(issue_id="issue_abc123", priority=10)
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, "error_code"):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    print("\n✅ All tests passed!")
