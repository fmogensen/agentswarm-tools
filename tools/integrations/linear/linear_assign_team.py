"""
Linear Assign Team Tool

Manages team assignments, cycles, and estimates for Linear issues with support
for sprint planning, capacity management, and team workflows.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class LinearAssignTeam(BaseTool):
    """
    Assign issues to teams, users, cycles with estimates and capacity planning.

    This tool manages team assignments in Linear with support for:
    - Team and user assignment
    - Cycle/sprint management
    - Story point estimation
    - Capacity planning
    - Bulk assignment operations
    - Team workflow integration

    Args:
        issue_ids: List of issue IDs to assign (single or multiple)
        team_id: Team ID to assign issues to (optional)
        assignee_id: User ID to assign issues to (optional)
        cycle_id: Cycle/sprint ID (optional)
        estimate: Story points estimate (optional)
        auto_assign: Automatically assign to team member with lowest workload
        start_date: Start date for cycle planning (ISO 8601 format)
        due_date: Due date for cycle planning (ISO 8601 format)
        distribute_evenly: Distribute work evenly across team members

    Returns:
        Dict containing:
            - success (bool): Whether the assignment was successful
            - assigned_count (int): Number of issues assigned
            - assignments (list): Details of each assignment
            - team_info (dict): Team information
            - cycle_info (dict): Cycle information if applicable
            - capacity_summary (dict): Team capacity summary
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = LinearAssignTeam(
        ...     issue_ids=["issue_abc", "issue_def"],
        ...     team_id="team_xyz",
        ...     cycle_id="cycle_123",
        ...     auto_assign=True,
        ...     distribute_evenly=True
        ... )
        >>> result = tool.run()
        >>> print(f"Assigned {result['assigned_count']} issues")
    """

    # Tool metadata
    tool_name: str = "linear_assign_team"
    tool_category: str = "integrations"

    # Required parameters
    issue_ids: List[str] = Field(
        ..., description="List of issue IDs to assign (can be single issue)", min_items=1
    )

    # Optional parameters - assignment targets
    team_id: Optional[str] = Field(None, description="Team ID to assign issues to")
    assignee_id: Optional[str] = Field(None, description="User ID to assign issues to")
    cycle_id: Optional[str] = Field(None, description="Cycle/sprint ID")

    # Optional parameters - estimation and planning
    estimate: Optional[float] = Field(
        None, description="Story points estimate to apply to all issues", ge=0, le=100
    )
    auto_assign: bool = Field(False, description="Auto-assign to team member with lowest workload")
    distribute_evenly: bool = Field(
        False, description="Distribute issues evenly across team members"
    )

    # Optional parameters - dates
    start_date: Optional[str] = Field(
        None, description="Start date for cycle planning (ISO 8601 format)"
    )
    due_date: Optional[str] = Field(
        None, description="Due date for cycle planning (ISO 8601 format)"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the team assignment."""
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
                "assigned_count": result["assigned_count"],
                "assignments": result["assignments"],
                "team_info": result.get("team_info", {}),
                "cycle_info": result.get("cycle_info", {}),
                "capacity_summary": result.get("capacity_summary", {}),
                "metadata": {
                    "tool_name": self.tool_name,
                    "team_id": self.team_id,
                    "cycle_id": self.cycle_id,
                },
            }
        except Exception as e:
            raise APIError(f"Failed to assign team in Linear: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate issue_ids
        if not self.issue_ids or len(self.issue_ids) == 0:
            raise ValidationError(
                "At least one issue ID must be provided",
                tool_name=self.tool_name,
                field="issue_ids",
            )

        # Validate estimate
        if self.estimate is not None and self.estimate < 0:
            raise ValidationError(
                "Estimate must be a positive number", tool_name=self.tool_name, field="estimate"
            )

        # Can't use both assignee_id and auto_assign/distribute_evenly
        if self.assignee_id and (self.auto_assign or self.distribute_evenly):
            raise ValidationError(
                "Cannot specify assignee_id with auto_assign or distribute_evenly",
                tool_name=self.tool_name,
            )

        # auto_assign and distribute_evenly are mutually exclusive
        if self.auto_assign and self.distribute_evenly:
            raise ValidationError(
                "Cannot use both auto_assign and distribute_evenly", tool_name=self.tool_name
            )

        # Validate dates
        if self.start_date:
            try:
                datetime.fromisoformat(self.start_date.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                raise ValidationError(
                    "Start date must be in ISO 8601 format",
                    tool_name=self.tool_name,
                    field="start_date",
                )

        if self.due_date:
            try:
                datetime.fromisoformat(self.due_date.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                raise ValidationError(
                    "Due date must be in ISO 8601 format",
                    tool_name=self.tool_name,
                    field="due_date",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        assignments = []
        for i, issue_id in enumerate(self.issue_ids):
            assignments.append(
                {
                    "issue_id": issue_id,
                    "issue_identifier": f"ENG-{100 + i}",
                    "assigned_to": self.assignee_id or f"user_mock_{i % 3}",
                    "team": self.team_id or "team_mock",
                    "cycle": self.cycle_id,
                    "estimate": self.estimate or 3.0,
                }
            )

        return {
            "success": True,
            "assigned_count": len(self.issue_ids),
            "assignments": assignments,
            "team_info": {
                "team_id": self.team_id or "team_mock",
                "team_name": "Engineering",
                "member_count": 5,
            },
            "cycle_info": (
                {
                    "cycle_id": self.cycle_id,
                    "cycle_name": "Sprint 12",
                    "start_date": self.start_date or "2025-12-01",
                    "end_date": self.due_date or "2025-12-14",
                }
                if self.cycle_id
                else {}
            ),
            "capacity_summary": {
                "total_capacity": 50.0,
                "allocated": 25.0,
                "remaining": 25.0,
                "utilization": 0.5,
            },
            "metadata": {
                "tool_name": self.tool_name,
                "team_id": self.team_id,
                "cycle_id": self.cycle_id,
                "mock_mode": True,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Process the team assignment with Linear GraphQL API."""
        # Get API key
        api_key = os.getenv("LINEAR_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing LINEAR_API_KEY environment variable", tool_name=self.tool_name
            )

        # Get team info if team_id provided
        team_info = {}
        if self.team_id:
            team_info = self._get_team_info(api_key, self.team_id)

        # Get cycle info if cycle_id provided
        cycle_info = {}
        if self.cycle_id:
            cycle_info = self._get_cycle_info(api_key, self.cycle_id)

        # Determine assignment strategy
        if self.auto_assign or self.distribute_evenly:
            # Get team members and their workloads
            team_members = self._get_team_members_workload(api_key, self.team_id)
        else:
            team_members = []

        # Process assignments
        assignments = []
        for i, issue_id in enumerate(self.issue_ids):
            # Determine assignee
            assignee = self.assignee_id
            if self.auto_assign:
                # Assign to member with lowest workload
                assignee = self._get_lowest_workload_member(team_members)
            elif self.distribute_evenly:
                # Round-robin distribution
                assignee = team_members[i % len(team_members)]["id"] if team_members else None

            # Update issue
            assignment = self._update_issue_assignment(
                api_key,
                issue_id,
                assignee,
                self.cycle_id,
                self.estimate,
                self.start_date,
                self.due_date,
            )

            assignments.append(assignment)

            # Update workload tracking for distribution
            if assignee and team_members:
                for member in team_members:
                    if member["id"] == assignee:
                        member["workload"] += self.estimate or 0

        # Calculate capacity summary
        capacity_summary = self._calculate_capacity_summary(
            team_members if team_members else [], cycle_info
        )

        return {
            "assigned_count": len(assignments),
            "assignments": assignments,
            "team_info": team_info,
            "cycle_info": cycle_info,
            "capacity_summary": capacity_summary,
        }

    def _get_team_info(self, api_key: str, team_id: str) -> Dict[str, Any]:
        """Get team information."""
        query = """
        query Team($id: String!) {
            team(id: $id) {
                id
                name
                key
                members {
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

        payload = {"query": query, "variables": {"id": team_id}}

        response = requests.post(
            "https://api.linear.app/graphql", headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        team = data.get("data", {}).get("team", {})

        return {
            "team_id": team.get("id"),
            "team_name": team.get("name"),
            "team_key": team.get("key"),
            "member_count": len(team.get("members", {}).get("nodes", [])),
        }

    def _get_cycle_info(self, api_key: str, cycle_id: str) -> Dict[str, Any]:
        """Get cycle/sprint information."""
        query = """
        query Cycle($id: String!) {
            cycle(id: $id) {
                id
                name
                number
                startsAt
                endsAt
                completedAt
                progress
            }
        }
        """

        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {"query": query, "variables": {"id": cycle_id}}

        response = requests.post(
            "https://api.linear.app/graphql", headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        cycle = data.get("data", {}).get("cycle", {})

        return {
            "cycle_id": cycle.get("id"),
            "cycle_name": cycle.get("name"),
            "cycle_number": cycle.get("number"),
            "start_date": cycle.get("startsAt"),
            "end_date": cycle.get("endsAt"),
            "progress": cycle.get("progress", 0),
        }

    def _get_team_members_workload(self, api_key: str, team_id: str) -> List[Dict[str, Any]]:
        """Get team members and their current workload."""
        query = """
        query Team($id: String!) {
            team(id: $id) {
                members {
                    nodes {
                        id
                        name
                        assignedIssues {
                            nodes {
                                estimate
                            }
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

        payload = {"query": query, "variables": {"id": team_id}}

        response = requests.post(
            "https://api.linear.app/graphql", headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        members = data.get("data", {}).get("team", {}).get("members", {}).get("nodes", [])

        # Calculate workload for each member
        workload_list = []
        for member in members:
            issues = member.get("assignedIssues", {}).get("nodes", [])
            workload = sum(issue.get("estimate", 0) for issue in issues)
            workload_list.append({"id": member["id"], "name": member["name"], "workload": workload})

        return workload_list

    def _get_lowest_workload_member(self, team_members: List[Dict[str, Any]]) -> Optional[str]:
        """Get team member with lowest current workload."""
        if not team_members:
            return None

        lowest = min(team_members, key=lambda m: m["workload"])
        return lowest["id"]

    def _update_issue_assignment(
        self,
        api_key: str,
        issue_id: str,
        assignee_id: Optional[str],
        cycle_id: Optional[str],
        estimate: Optional[float],
        start_date: Optional[str],
        due_date: Optional[str],
    ) -> Dict[str, Any]:
        """Update issue with assignment details."""
        mutation = """
        mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
                issue {
                    id
                    identifier
                    assignee {
                        id
                        name
                    }
                    cycle {
                        id
                        name
                    }
                    estimate
                }
            }
        }
        """

        input_data = {}
        if assignee_id:
            input_data["assigneeId"] = assignee_id
        if cycle_id:
            input_data["cycleId"] = cycle_id
        if estimate is not None:
            input_data["estimate"] = estimate
        if start_date:
            input_data["startedAt"] = start_date
        if due_date:
            input_data["dueDate"] = due_date

        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {"query": mutation, "variables": {"id": issue_id, "input": input_data}}

        response = requests.post(
            "https://api.linear.app/graphql", headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        issue = data.get("data", {}).get("issueUpdate", {}).get("issue", {})

        return {
            "issue_id": issue.get("id"),
            "issue_identifier": issue.get("identifier"),
            "assigned_to": issue.get("assignee", {}).get("name"),
            "assignee_id": issue.get("assignee", {}).get("id"),
            "cycle": issue.get("cycle", {}).get("name"),
            "estimate": issue.get("estimate"),
        }

    def _calculate_capacity_summary(
        self, team_members: List[Dict[str, Any]], cycle_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate team capacity summary."""
        if not team_members:
            return {}

        total_workload = sum(m["workload"] for m in team_members)
        # Assume each member has capacity of 10 points per sprint
        total_capacity = len(team_members) * 10

        return {
            "total_capacity": total_capacity,
            "allocated": total_workload,
            "remaining": max(0, total_capacity - total_workload),
            "utilization": min(1.0, total_workload / total_capacity if total_capacity > 0 else 0),
            "team_size": len(team_members),
            "average_workload": total_workload / len(team_members) if team_members else 0,
        }


if __name__ == "__main__":
    # Test the tool
    print("Testing LinearAssignTeam...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic assignment
    print("\n1. Testing basic team assignment...")
    tool = LinearAssignTeam(issue_ids=["issue_abc123"], team_id="team_xyz", assignee_id="user_123")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Assigned Count: {result.get('assigned_count')}")
    print(f"Team: {result.get('team_info', {}).get('team_name')}")
    assert result.get("success") == True
    assert result.get("assigned_count") == 1

    # Test 2: Cycle assignment with estimates
    print("\n2. Testing cycle assignment with estimates...")
    tool = LinearAssignTeam(
        issue_ids=["issue_1", "issue_2", "issue_3"],
        team_id="team_xyz",
        cycle_id="cycle_123",
        estimate=5.0,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Assigned Count: {result.get('assigned_count')}")
    print(f"Cycle: {result.get('cycle_info', {}).get('cycle_name')}")
    assert result.get("success") == True
    assert result.get("assigned_count") == 3

    # Test 3: Auto-assign (lowest workload)
    print("\n3. Testing auto-assign...")
    tool = LinearAssignTeam(
        issue_ids=["issue_1", "issue_2"], team_id="team_xyz", auto_assign=True, estimate=3.0
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Capacity Summary: {result.get('capacity_summary')}")
    assert result.get("success") == True

    # Test 4: Distribute evenly
    print("\n4. Testing distribute evenly...")
    tool = LinearAssignTeam(
        issue_ids=["issue_1", "issue_2", "issue_3", "issue_4", "issue_5"],
        team_id="team_xyz",
        distribute_evenly=True,
        estimate=2.0,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Assignments: {len(result.get('assignments', []))}")
    assert result.get("success") == True
    assert result.get("assigned_count") == 5

    # Test 5: Error handling - no issues
    print("\n5. Testing error handling (no issues)...")
    try:
        tool = LinearAssignTeam(issue_ids=[], team_id="team_xyz")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, "error_code"):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    # Test 6: Error handling - conflicting options
    print("\n6. Testing error handling (conflicting options)...")
    try:
        tool = LinearAssignTeam(issue_ids=["issue_1"], assignee_id="user_123", auto_assign=True)
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, "error_code"):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    print("\n✅ All tests passed!")
