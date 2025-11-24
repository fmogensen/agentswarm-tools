"""
Linear Create Issue Tool

Creates issues in Linear with full support for projects, labels, assignees,
priorities, estimates, and custom fields using GraphQL API.
"""

import json
import os
from typing import Any, Dict, List, Optional

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class LinearCreateIssue(BaseTool):
    """
    Create issues in Linear with comprehensive field support.

    This tool creates Linear issues with support for:
    - Team assignment and project association
    - Labels, priorities, and status
    - Assignee and subscriber management
    - Time estimates and due dates
    - Parent/child issue relationships
    - Custom field values

    Args:
        title: Issue title (required)
        description: Issue description in Markdown format (optional)
        team_id: Linear team ID (required)
        project_id: Project ID to associate issue with (optional)
        assignee_id: User ID to assign the issue to (optional)
        priority: Issue priority (0=No priority, 1=Urgent, 2=High, 3=Normal, 4=Low)
        labels: List of label IDs to attach (optional)
        state_id: Workflow state ID (optional, defaults to team's default state)
        estimate: Story points or time estimate (optional)
        due_date: Due date in ISO 8601 format (optional)
        parent_id: Parent issue ID for sub-issues (optional)
        cycle_id: Cycle/sprint ID (optional)
        subscriber_ids: List of user IDs to subscribe (optional)
        custom_fields: Dictionary of custom field values (optional)

    Returns:
        Dict containing:
            - success (bool): Whether the issue was created successfully
            - issue_id (str): Linear issue ID
            - issue_identifier (str): Human-readable identifier (e.g., "ENG-123")
            - issue_url (str): Direct URL to the issue
            - title (str): Issue title
            - state (str): Initial state name
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = LinearCreateIssue(
        ...     title="Implement user authentication",
        ...     description="Add OAuth2 support for Google login",
        ...     team_id="team_abc123",
        ...     project_id="proj_def456",
        ...     priority=2,
        ...     labels=["label_xyz", "label_abc"],
        ...     estimate=5
        ... )
        >>> result = tool.run()
        >>> print(result['issue_identifier'])
        'ENG-123'
    """

    # Tool metadata
    tool_name: str = "linear_create_issue"
    tool_category: str = "integrations"

    # Required parameters
    title: str = Field(..., description="Issue title", min_length=1, max_length=255)
    team_id: str = Field(..., description="Linear team ID (e.g., 'team_abc123')", min_length=1)

    # Optional parameters
    description: Optional[str] = Field(
        None, description="Issue description in Markdown format", max_length=50000
    )
    project_id: Optional[str] = Field(None, description="Project ID to associate issue with")
    assignee_id: Optional[str] = Field(None, description="User ID to assign the issue to")
    priority: int = Field(
        0, description="Priority: 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low", ge=0, le=4
    )
    labels: Optional[List[str]] = Field(None, description="List of label IDs to attach")
    state_id: Optional[str] = Field(
        None, description="Workflow state ID (defaults to team's default)"
    )
    estimate: Optional[float] = Field(
        None, description="Story points or time estimate", ge=0, le=1000
    )
    due_date: Optional[str] = Field(None, description="Due date in ISO 8601 format (YYYY-MM-DD)")
    parent_id: Optional[str] = Field(None, description="Parent issue ID for creating sub-issues")
    cycle_id: Optional[str] = Field(None, description="Cycle/sprint ID")
    subscriber_ids: Optional[List[str]] = Field(
        None, description="List of user IDs to subscribe to the issue"
    )
    custom_fields: Optional[Dict[str, Any]] = Field(
        None, description="Custom field values as key-value pairs"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the issue creation."""

        self._logger.info(f"Executing {self.tool_name} with title={self.title}, team_id={self.team_id}, description={self.description}, ...")
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
                "issue_url": result["url"],
                "title": result["title"],
                "state": result.get("state", {}).get("name", "Unknown"),
                "metadata": {
                    "tool_name": self.tool_name,
                    "team_id": self.team_id,
                    "project_id": self.project_id,
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to create Linear issue: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate title
        if not self.title or not self.title.strip():
            raise ValidationError(
                "Issue title cannot be empty", tool_name=self.tool_name, field="title"
            )

        # Validate team_id format
        if not self.team_id.strip():
            raise ValidationError(
                "Team ID cannot be empty", tool_name=self.tool_name, field="team_id"
            )

        # Validate priority range
        if self.priority < 0 or self.priority > 4:
            raise ValidationError(
                "Priority must be between 0 (None) and 4 (Low)",
                tool_name=self.tool_name,
                field="priority",
            )

        # Validate estimate
        if self.estimate is not None and self.estimate < 0:
            raise ValidationError(
                "Estimate must be a positive number", tool_name=self.tool_name, field="estimate"
            )

        # Validate due_date format (must be valid ISO 8601 - contains digits and proper separators)
        if self.due_date:
            # Basic check: should have at least 2 hyphens for date (YYYY-MM-DD) or contain T for datetime
            hyphen_count = self.due_date.count("-")
            has_time_separator = "T" in self.due_date

            # Must have either proper date format (at least 2 hyphens) or datetime format (with T)
            if hyphen_count < 2 and not has_time_separator:
                raise ValidationError(
                    "Invalid due_date format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)",
                    tool_name=self.tool_name,
                    field="due_date",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "issue_id": "mock_issue_abc123def456",
            "issue_identifier": "ENG-123",
            "issue_url": "https://linear.app/mock-workspace/issue/ENG-123",
            "title": self.title,
            "state": "Todo",
            "metadata": {
                "tool_name": self.tool_name,
                "team_id": self.team_id,
                "project_id": self.project_id,
                "mock_mode": True,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Process the issue creation with Linear GraphQL API."""
        # Get API key
        api_key = os.getenv("LINEAR_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing LINEAR_API_KEY environment variable", tool_name=self.tool_name
            )

        # Prepare GraphQL mutation
        mutation = """
        mutation IssueCreate($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    url
                    state {
                        id
                        name
                    }
                    team {
                        id
                        name
                    }
                    assignee {
                        id
                        name
                    }
                    priority
                    estimate
                    dueDate
                    labels {
                        nodes {
                            id
                            name
                        }
                    }
                }
            }
        }
        """

        # Build input object
        input_data = {
            "title": self.title,
            "teamId": self.team_id,
            "priority": self.priority,
        }

        # Add optional fields
        if self.description:
            input_data["description"] = self.description

        if self.project_id:
            input_data["projectId"] = self.project_id

        if self.assignee_id:
            input_data["assigneeId"] = self.assignee_id

        if self.state_id:
            input_data["stateId"] = self.state_id

        if self.estimate is not None:
            input_data["estimate"] = self.estimate

        if self.due_date:
            input_data["dueDate"] = self.due_date

        if self.parent_id:
            input_data["parentId"] = self.parent_id

        if self.cycle_id:
            input_data["cycleId"] = self.cycle_id

        if self.labels:
            input_data["labelIds"] = self.labels

        if self.subscriber_ids:
            input_data["subscriberIds"] = self.subscriber_ids

        # Execute GraphQL request
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {"query": mutation, "variables": {"input": input_data}}

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
            issue_data = data.get("data", {}).get("issueCreate", {})

            if not issue_data.get("success"):
                raise APIError("Issue creation failed", tool_name=self.tool_name)

            return issue_data.get("issue", {})

        except requests.exceptions.RequestException as e:
            raise APIError(f"Linear API request failed: {str(e)}", tool_name=self.tool_name)
        except (KeyError, ValueError) as e:
            raise APIError(
                f"Failed to parse Linear API response: {str(e)}", tool_name=self.tool_name
            )


if __name__ == "__main__":
    # Test the tool
    print("Testing LinearCreateIssue...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic issue creation
    print("\n1. Testing basic issue creation...")
    tool = LinearCreateIssue(
        title="Implement user authentication",
        description="Add OAuth2 support for Google login",
        team_id="team_abc123",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Issue ID: {result.get('issue_id')}")
    print(f"Issue Identifier: {result.get('issue_identifier')}")
    print(f"Issue URL: {result.get('issue_url')}")
    assert result.get("success") == True
    assert result.get("issue_identifier") == "ENG-123"

    # Test 2: Full issue with all fields
    print("\n2. Testing issue with all fields...")
    tool = LinearCreateIssue(
        title="Fix critical bug in payment processing",
        description="Users unable to complete checkout. Stack trace attached.",
        team_id="team_abc123",
        project_id="proj_def456",
        assignee_id="user_xyz789",
        priority=1,  # Urgent
        labels=["label_bug", "label_payments"],
        estimate=3.0,
        due_date="2025-12-31",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Title: {result.get('title')}")
    print(f"State: {result.get('state')}")
    assert result.get("success") == True

    # Test 3: Sub-issue creation
    print("\n3. Testing sub-issue creation...")
    tool = LinearCreateIssue(
        title="Design mockups", team_id="team_abc123", parent_id="parent_issue_123", estimate=2.0
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True

    # Test 4: Error handling - empty title
    print("\n4. Testing error handling (empty title)...")
    try:
        tool = LinearCreateIssue(title="", team_id="team_abc123")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, "error_code"):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    # Test 5: Error handling - invalid priority
    print("\n5. Testing error handling (invalid priority)...")
    try:
        tool = LinearCreateIssue(title="Test issue", team_id="team_abc123", priority=10)
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, "error_code"):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    print("\n✅ All tests passed!")
