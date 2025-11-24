"""
Linear Get Roadmap Tool

Retrieves roadmap, projects, milestones, and progress tracking from Linear
with comprehensive filtering and analytics capabilities.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class LinearGetRoadmap(BaseTool):
    """
    Retrieve roadmap, projects, milestones, and progress from Linear.

    This tool retrieves Linear roadmap data with support for:
    - Project listing and filtering
    - Milestone tracking
    - Progress analytics
    - Timeline visualization data
    - Status and health metrics
    - Team and cycle associations

    Args:
        team_id: Filter projects by team ID (optional)
        status_filter: Filter by project status (planned, started, paused, completed, canceled)
        include_archived: Include archived projects (default: False)
        include_milestones: Include milestone information (default: True)
        include_progress: Include progress metrics (default: True)
        date_range_start: Filter projects by start date (ISO 8601 format)
        date_range_end: Filter projects by end date (ISO 8601 format)
        sort_by: Sort results by field (name, startDate, targetDate, progress)
        limit: Maximum number of projects to return (default: 50)

    Returns:
        Dict containing:
            - success (bool): Whether the retrieval was successful
            - projects (list): List of projects with details
            - milestones (list): List of milestones across projects
            - roadmap_summary (dict): Overall roadmap statistics
            - timeline (dict): Timeline data for visualization
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = LinearGetRoadmap(
        ...     team_id="team_abc123",
        ...     status_filter="started",
        ...     include_milestones=True,
        ...     include_progress=True
        ... )
        >>> result = tool.run()
        >>> print(f"Found {len(result['projects'])} active projects")
    """

    # Tool metadata
    tool_name: str = "linear_get_roadmap"
    tool_category: str = "integrations"

    # Optional parameters - filtering
    team_id: Optional[str] = Field(None, description="Filter projects by team ID")
    status_filter: Optional[str] = Field(
        None, description="Filter by status: planned, started, paused, completed, canceled"
    )
    include_archived: bool = Field(False, description="Include archived projects")

    # Optional parameters - data inclusion
    include_milestones: bool = Field(True, description="Include milestone information")
    include_progress: bool = Field(True, description="Include progress metrics")

    # Optional parameters - date filtering
    date_range_start: Optional[str] = Field(
        None, description="Filter by start date (ISO 8601 format)"
    )
    date_range_end: Optional[str] = Field(None, description="Filter by end date (ISO 8601 format)")

    # Optional parameters - sorting and pagination
    sort_by: str = Field("startDate", description="Sort by: name, startDate, targetDate, progress")
    limit: int = Field(50, description="Maximum number of projects to return", ge=1, le=100)

    def _execute(self) -> Dict[str, Any]:
        """Execute the roadmap retrieval."""
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
                "projects": result["projects"],
                "milestones": result.get("milestones", []),
                "roadmap_summary": result.get("roadmap_summary", {}),
                "timeline": result.get("timeline", {}),
                "metadata": {
                    "tool_name": self.tool_name,
                    "team_id": self.team_id,
                    "status_filter": self.status_filter,
                    "project_count": len(result["projects"]),
                },
            }
        except Exception as e:
            raise APIError(f"Failed to retrieve Linear roadmap: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate status_filter
        valid_statuses = ["planned", "started", "paused", "completed", "canceled"]
        if self.status_filter and self.status_filter.lower() not in valid_statuses:
            raise ValidationError(
                f"Invalid status filter. Must be one of: {', '.join(valid_statuses)}",
                tool_name=self.tool_name,
                field="status_filter",
            )

        # Validate sort_by
        valid_sorts = ["name", "startDate", "targetDate", "progress"]
        if self.sort_by not in valid_sorts:
            raise ValidationError(
                f"Invalid sort_by. Must be one of: {', '.join(valid_sorts)}",
                tool_name=self.tool_name,
                field="sort_by",
            )

        # Validate limit
        if self.limit < 1 or self.limit > 100:
            raise ValidationError(
                "Limit must be between 1 and 100", tool_name=self.tool_name, field="limit"
            )

        # Validate dates
        if self.date_range_start:
            try:
                datetime.fromisoformat(self.date_range_start.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                raise ValidationError(
                    "Start date must be in ISO 8601 format",
                    tool_name=self.tool_name,
                    field="date_range_start",
                )

        if self.date_range_end:
            try:
                datetime.fromisoformat(self.date_range_end.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                raise ValidationError(
                    "End date must be in ISO 8601 format",
                    tool_name=self.tool_name,
                    field="date_range_end",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        projects = [
            {
                "id": "proj_abc123",
                "name": "Q4 Platform Improvements",
                "description": "Major platform enhancements for Q4",
                "status": "started",
                "progress": 0.65,
                "start_date": "2025-10-01",
                "target_date": "2025-12-31",
                "lead": {"id": "user_123", "name": "Alice Smith"},
                "team": {"id": self.team_id or "team_xyz", "name": "Engineering"},
                "health": "onTrack",
                "issue_count": 23,
                "completed_issues": 15,
                "milestones": [
                    {
                        "id": "milestone_1",
                        "name": "Alpha Release",
                        "date": "2025-11-15",
                        "completed": True,
                    },
                    {
                        "id": "milestone_2",
                        "name": "Beta Release",
                        "date": "2025-12-15",
                        "completed": False,
                    },
                ],
            },
            {
                "id": "proj_def456",
                "name": "Mobile App Redesign",
                "description": "Complete redesign of mobile applications",
                "status": "planned",
                "progress": 0.15,
                "start_date": "2026-01-01",
                "target_date": "2026-03-31",
                "lead": {"id": "user_456", "name": "Bob Johnson"},
                "team": {"id": self.team_id or "team_xyz", "name": "Design"},
                "health": "atRisk",
                "issue_count": 45,
                "completed_issues": 7,
                "milestones": [
                    {
                        "id": "milestone_3",
                        "name": "Design Complete",
                        "date": "2026-02-01",
                        "completed": False,
                    }
                ],
            },
        ]

        # Filter by status if specified
        if self.status_filter:
            projects = [p for p in projects if p["status"] == self.status_filter.lower()]

        # Sort projects by specified field
        if self.sort_by == "name":
            projects = sorted(projects, key=lambda p: p["name"])
        elif self.sort_by == "startDate":
            projects = sorted(projects, key=lambda p: p["start_date"])
        elif self.sort_by == "targetDate":
            projects = sorted(projects, key=lambda p: p["target_date"])
        elif self.sort_by == "progress":
            projects = sorted(projects, key=lambda p: p.get("progress", 0), reverse=True)

        milestones = []
        for project in projects:
            if self.include_milestones and "milestones" in project:
                for milestone in project["milestones"]:
                    milestones.append(
                        {**milestone, "project_id": project["id"], "project_name": project["name"]}
                    )

        roadmap_summary = {
            "total_projects": len(projects),
            "by_status": {
                "started": sum(1 for p in projects if p["status"] == "started"),
                "planned": sum(1 for p in projects if p["status"] == "planned"),
                "completed": sum(1 for p in projects if p["status"] == "completed"),
            },
            "by_health": {
                "onTrack": sum(1 for p in projects if p.get("health") == "onTrack"),
                "atRisk": sum(1 for p in projects if p.get("health") == "atRisk"),
                "offTrack": sum(1 for p in projects if p.get("health") == "offTrack"),
            },
            "average_progress": (
                sum(p.get("progress", 0) for p in projects) / len(projects) if projects else 0
            ),
            "total_issues": sum(p.get("issue_count", 0) for p in projects),
            "completed_issues": sum(p.get("completed_issues", 0) for p in projects),
        }

        timeline = {
            "start_date": min((p["start_date"] for p in projects), default="2025-01-01"),
            "end_date": max((p["target_date"] for p in projects), default="2026-12-31"),
            "quarters": self._generate_timeline_quarters(projects),
        }

        return {
            "success": True,
            "projects": projects[: self.limit] if self.limit else projects,
            "milestones": milestones if self.include_milestones else [],
            "roadmap_summary": roadmap_summary,
            "timeline": timeline,
            "metadata": {
                "tool_name": self.tool_name,
                "team_id": self.team_id,
                "status_filter": self.status_filter,
                "project_count": len(projects),
                "mock_mode": True,
            },
        }

    def _generate_timeline_quarters(self, projects: List[Dict]) -> List[Dict]:
        """Generate timeline data by quarters."""
        quarters = []
        for q in range(1, 5):
            quarter_projects = [
                p
                for p in projects
                if f"Q{q}" in p.get("name", "")
                or (
                    p.get("start_date", "").startswith(f"2025-{q*3-2:02d}")
                    or p.get("start_date", "").startswith(f"2025-{q*3-1:02d}")
                    or p.get("start_date", "").startswith(f"2025-{q*3:02d}")
                )
            ]
            quarters.append(
                {
                    "quarter": f"Q{q} 2025",
                    "project_count": len(quarter_projects),
                    "projects": [p["name"] for p in quarter_projects],
                }
            )
        return quarters

    def _process(self) -> Dict[str, Any]:
        """Process the roadmap retrieval with Linear GraphQL API."""
        # Get API key
        api_key = os.getenv("LINEAR_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing LINEAR_API_KEY environment variable", tool_name=self.tool_name
            )

        # Prepare GraphQL query
        query = """
        query Projects($filter: ProjectFilter, $first: Int!) {
            projects(filter: $filter, first: $first) {
                nodes {
                    id
                    name
                    description
                    state
                    progress
                    startDate
                    targetDate
                    lead {
                        id
                        name
                    }
                    teams {
                        nodes {
                            id
                            name
                        }
                    }
                    projectMilestones {
                        nodes {
                            id
                            name
                            targetDate
                            sortOrder
                        }
                    }
                    issues {
                        nodes {
                            id
                            state {
                                type
                            }
                        }
                    }
                    health
                    createdAt
                    updatedAt
                }
            }
        }
        """

        # Build filter
        filter_obj = {}

        if self.team_id:
            filter_obj["teams"] = {"some": {"id": {"eq": self.team_id}}}

        if self.status_filter:
            filter_obj["state"] = {"eq": self.status_filter}

        if not self.include_archived:
            filter_obj["archived"] = {"eq": False}

        if self.date_range_start:
            filter_obj["startDate"] = {"gte": self.date_range_start}

        if self.date_range_end:
            filter_obj["targetDate"] = {"lte": self.date_range_end}

        # Execute GraphQL request
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "variables": {"filter": filter_obj if filter_obj else None, "first": self.limit},
        }

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

            # Extract and process projects
            projects_raw = data.get("data", {}).get("projects", {}).get("nodes", [])
            projects = self._process_projects(projects_raw)

            # Sort projects
            projects = self._sort_projects(projects)

            # Extract milestones
            milestones = []
            if self.include_milestones:
                milestones = self._extract_milestones(projects)

            # Calculate roadmap summary
            roadmap_summary = self._calculate_roadmap_summary(projects)

            # Generate timeline
            timeline = self._generate_timeline(projects)

            return {
                "projects": projects,
                "milestones": milestones,
                "roadmap_summary": roadmap_summary,
                "timeline": timeline,
            }

        except requests.exceptions.RequestException as e:
            raise APIError(f"Linear API request failed: {str(e)}", tool_name=self.tool_name)
        except (KeyError, ValueError) as e:
            raise APIError(
                f"Failed to parse Linear API response: {str(e)}", tool_name=self.tool_name
            )

    def _process_projects(self, projects_raw: List[Dict]) -> List[Dict]:
        """Process raw project data."""
        processed = []

        for project in projects_raw:
            # Calculate progress if needed
            if self.include_progress:
                issues = project.get("issues", {}).get("nodes", [])
                total_issues = len(issues)
                completed_issues = sum(
                    1 for issue in issues if issue.get("state", {}).get("type") == "completed"
                )
                progress = completed_issues / total_issues if total_issues > 0 else 0
            else:
                progress = project.get("progress", 0)
                total_issues = 0
                completed_issues = 0

            # Get first team (projects can have multiple teams)
            teams = project.get("teams", {}).get("nodes", [])
            team = teams[0] if teams else None

            processed_project = {
                "id": project.get("id"),
                "name": project.get("name"),
                "description": project.get("description"),
                "status": project.get("state"),
                "progress": progress,
                "start_date": project.get("startDate"),
                "target_date": project.get("targetDate"),
                "lead": (
                    {
                        "id": project.get("lead", {}).get("id"),
                        "name": project.get("lead", {}).get("name"),
                    }
                    if project.get("lead")
                    else None
                ),
                "team": {"id": team.get("id"), "name": team.get("name")} if team else None,
                "health": project.get("health"),
                "issue_count": total_issues,
                "completed_issues": completed_issues,
            }

            # Add milestones if requested
            if self.include_milestones:
                milestones = project.get("projectMilestones", {}).get("nodes", [])
                processed_project["milestones"] = [
                    {
                        "id": m.get("id"),
                        "name": m.get("name"),
                        "date": m.get("targetDate"),
                        "sort_order": m.get("sortOrder"),
                    }
                    for m in milestones
                ]

            processed.append(processed_project)

        return processed

    def _sort_projects(self, projects: List[Dict]) -> List[Dict]:
        """Sort projects by specified field."""
        sort_key_map = {
            "name": lambda p: p.get("name", ""),
            "startDate": lambda p: p.get("start_date", ""),
            "targetDate": lambda p: p.get("target_date", ""),
            "progress": lambda p: p.get("progress", 0),
        }

        sort_key = sort_key_map.get(self.sort_by, lambda p: p.get("start_date", ""))
        return sorted(projects, key=sort_key)

    def _extract_milestones(self, projects: List[Dict]) -> List[Dict]:
        """Extract all milestones from projects."""
        milestones = []
        for project in projects:
            project_milestones = project.get("milestones", [])
            for milestone in project_milestones:
                milestones.append(
                    {**milestone, "project_id": project["id"], "project_name": project["name"]}
                )
        return sorted(milestones, key=lambda m: m.get("date", ""))

    def _calculate_roadmap_summary(self, projects: List[Dict]) -> Dict[str, Any]:
        """Calculate roadmap summary statistics."""
        if not projects:
            return {}

        status_counts = {}
        health_counts = {}

        for project in projects:
            status = project.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            health = project.get("health", "unknown")
            health_counts[health] = health_counts.get(health, 0) + 1

        total_issues = sum(p.get("issue_count", 0) for p in projects)
        completed_issues = sum(p.get("completed_issues", 0) for p in projects)
        avg_progress = sum(p.get("progress", 0) for p in projects) / len(projects)

        return {
            "total_projects": len(projects),
            "by_status": status_counts,
            "by_health": health_counts,
            "average_progress": round(avg_progress, 2),
            "total_issues": total_issues,
            "completed_issues": completed_issues,
            "completion_rate": round(completed_issues / total_issues, 2) if total_issues > 0 else 0,
        }

    def _generate_timeline(self, projects: List[Dict]) -> Dict[str, Any]:
        """Generate timeline visualization data."""
        if not projects:
            return {}

        dates = []
        for project in projects:
            if project.get("start_date"):
                dates.append(project["start_date"])
            if project.get("target_date"):
                dates.append(project["target_date"])

        if not dates:
            return {}

        return {
            "start_date": min(dates),
            "end_date": max(dates),
            "project_count": len(projects),
            "milestones_count": sum(len(p.get("milestones", [])) for p in projects),
        }


if __name__ == "__main__":
    # Test the tool
    print("Testing LinearGetRoadmap...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Get all projects
    print("\n1. Testing get all projects...")
    tool = LinearGetRoadmap()
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Projects: {len(result.get('projects', []))}")
    print(f"Summary: {result.get('roadmap_summary')}")
    assert result.get("success") == True
    assert len(result.get("projects", [])) > 0

    # Test 2: Filter by status
    print("\n2. Testing status filter...")
    tool = LinearGetRoadmap(status_filter="started", include_milestones=True, include_progress=True)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Projects: {len(result.get('projects', []))}")
    print(f"Milestones: {len(result.get('milestones', []))}")
    assert result.get("success") == True

    # Test 3: Team-specific roadmap
    print("\n3. Testing team-specific roadmap...")
    tool = LinearGetRoadmap(team_id="team_xyz", sort_by="progress")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Timeline: {result.get('timeline')}")
    assert result.get("success") == True

    # Test 4: Limited results
    print("\n4. Testing limited results...")
    tool = LinearGetRoadmap(limit=10, sort_by="name")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Projects returned: {len(result.get('projects', []))}")
    assert result.get("success") == True

    # Test 5: Error handling - invalid status
    print("\n5. Testing error handling (invalid status)...")
    try:
        tool = LinearGetRoadmap(status_filter="invalid_status")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, "error_code"):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    # Test 6: Error handling - invalid sort
    print("\n6. Testing error handling (invalid sort)...")
    try:
        tool = LinearGetRoadmap(sort_by="invalid_sort")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if hasattr(e, "error_code"):
            print(f"Correctly caught error: {e.message}")
        else:
            print(f"Caught error in run(): {e}")

    print("\n✅ All tests passed!")
