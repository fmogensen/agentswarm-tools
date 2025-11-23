"""
Tests for LinearGetRoadmap tool

Test coverage:
- Roadmap retrieval with various filters
- Project listing and sorting
- Milestone extraction
- Progress analytics
- Timeline generation
- Validation and error handling
"""

import pytest
import os
from unittest.mock import patch, MagicMock

from tools.integrations.linear.linear_get_roadmap import LinearGetRoadmap


class TestLinearGetRoadmap:
    """Test suite for LinearGetRoadmap tool."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Clean up after tests."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Basic functionality tests

    def test_get_all_projects(self):
        """Test retrieving all projects."""
        tool = LinearGetRoadmap()
        result = tool.run()

        assert result["success"] is True
        assert "projects" in result
        assert len(result["projects"]) > 0
        assert "roadmap_summary" in result

    def test_filter_by_team(self):
        """Test filtering projects by team."""
        tool = LinearGetRoadmap(team_id="team_xyz")
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["team_id"] == "team_xyz"

    def test_filter_by_status(self):
        """Test filtering projects by status."""
        tool = LinearGetRoadmap(status_filter="started")
        result = tool.run()

        assert result["success"] is True
        # All returned projects should have 'started' status
        for project in result["projects"]:
            assert project["status"] == "started"

    # Status filter tests

    def test_all_status_filters(self):
        """Test all valid status filters."""
        statuses = ["planned", "started", "paused", "completed", "canceled"]
        for status in statuses:
            tool = LinearGetRoadmap(status_filter=status)
            result = tool.run()
            assert result["success"] is True

    # Milestone tests

    def test_include_milestones(self):
        """Test including milestone information."""
        tool = LinearGetRoadmap(include_milestones=True)
        result = tool.run()

        assert result["success"] is True
        assert "milestones" in result
        if result["projects"]:
            assert len(result["milestones"]) >= 0

    def test_exclude_milestones(self):
        """Test excluding milestone information."""
        tool = LinearGetRoadmap(include_milestones=False)
        result = tool.run()

        assert result["success"] is True
        assert result["milestones"] == []

    def test_milestone_structure(self):
        """Test milestone data structure."""
        tool = LinearGetRoadmap(include_milestones=True)
        result = tool.run()

        if result["milestones"]:
            milestone = result["milestones"][0]
            assert "id" in milestone
            assert "name" in milestone
            assert "date" in milestone
            assert "project_id" in milestone

    # Progress tests

    def test_include_progress(self):
        """Test including progress metrics."""
        tool = LinearGetRoadmap(include_progress=True)
        result = tool.run()

        assert result["success"] is True
        if result["projects"]:
            project = result["projects"][0]
            assert "progress" in project
            assert 0 <= project["progress"] <= 1.0

    def test_exclude_progress(self):
        """Test excluding progress metrics."""
        tool = LinearGetRoadmap(include_progress=False)
        result = tool.run()

        assert result["success"] is True

    # Sorting tests

    def test_sort_by_name(self):
        """Test sorting projects by name."""
        tool = LinearGetRoadmap(sort_by="name")
        result = tool.run()

        assert result["success"] is True
        # Verify sorted order
        names = [p["name"] for p in result["projects"]]
        assert names == sorted(names)

    def test_sort_by_start_date(self):
        """Test sorting projects by start date."""
        tool = LinearGetRoadmap(sort_by="startDate")
        result = tool.run()

        assert result["success"] is True

    def test_sort_by_target_date(self):
        """Test sorting projects by target date."""
        tool = LinearGetRoadmap(sort_by="targetDate")
        result = tool.run()

        assert result["success"] is True

    def test_sort_by_progress(self):
        """Test sorting projects by progress."""
        tool = LinearGetRoadmap(sort_by="progress", include_progress=True)
        result = tool.run()

        assert result["success"] is True

    # Pagination tests

    def test_limit_results(self):
        """Test limiting number of results."""
        tool = LinearGetRoadmap(limit=10)
        result = tool.run()

        assert result["success"] is True
        assert len(result["projects"]) <= 10

    def test_minimum_limit(self):
        """Test minimum limit of 1."""
        tool = LinearGetRoadmap(limit=1)
        result = tool.run()

        assert result["success"] is True
        assert len(result["projects"]) <= 1

    def test_maximum_limit(self):
        """Test maximum limit of 100."""
        tool = LinearGetRoadmap(limit=100)
        result = tool.run()

        assert result["success"] is True

    # Date filtering tests

    def test_filter_by_start_date(self):
        """Test filtering by start date range."""
        tool = LinearGetRoadmap(date_range_start="2025-01-01")
        result = tool.run()

        assert result["success"] is True

    def test_filter_by_end_date(self):
        """Test filtering by end date range."""
        tool = LinearGetRoadmap(date_range_end="2025-12-31")
        result = tool.run()

        assert result["success"] is True

    def test_filter_by_date_range(self):
        """Test filtering by both start and end dates."""
        tool = LinearGetRoadmap(
            date_range_start="2025-01-01",
            date_range_end="2025-12-31"
        )
        result = tool.run()

        assert result["success"] is True

    # Archived projects tests

    def test_exclude_archived(self):
        """Test excluding archived projects (default)."""
        tool = LinearGetRoadmap(include_archived=False)
        result = tool.run()

        assert result["success"] is True

    def test_include_archived(self):
        """Test including archived projects."""
        tool = LinearGetRoadmap(include_archived=True)
        result = tool.run()

        assert result["success"] is True

    # Roadmap summary tests

    def test_roadmap_summary_structure(self):
        """Test roadmap summary has correct structure."""
        tool = LinearGetRoadmap()
        result = tool.run()

        summary = result["roadmap_summary"]
        assert "total_projects" in summary
        assert "by_status" in summary
        assert "by_health" in summary
        assert "average_progress" in summary

    def test_roadmap_statistics(self):
        """Test roadmap statistics calculation."""
        tool = LinearGetRoadmap(include_progress=True)
        result = tool.run()

        summary = result["roadmap_summary"]
        assert summary["total_projects"] >= 0
        assert 0 <= summary["average_progress"] <= 1.0

    # Timeline tests

    def test_timeline_generation(self):
        """Test timeline data is generated."""
        tool = LinearGetRoadmap()
        result = tool.run()

        assert "timeline" in result
        timeline = result["timeline"]
        assert "start_date" in timeline
        assert "end_date" in timeline

    # Project data structure tests

    def test_project_structure(self):
        """Test project data has correct structure."""
        tool = LinearGetRoadmap()
        result = tool.run()

        if result["projects"]:
            project = result["projects"][0]
            assert "id" in project
            assert "name" in project
            assert "status" in project
            assert "progress" in project
            assert "start_date" in project
            assert "target_date" in project

    def test_project_team_info(self):
        """Test project includes team information."""
        tool = LinearGetRoadmap()
        result = tool.run()

        if result["projects"]:
            project = result["projects"][0]
            if project.get("team"):
                assert "id" in project["team"]
                assert "name" in project["team"]

    def test_project_health_status(self):
        """Test project includes health status."""
        tool = LinearGetRoadmap()
        result = tool.run()

        if result["projects"]:
            project = result["projects"][0]
            assert "health" in project

    # Validation tests

    def test_validation_invalid_status(self):
        """Test validation fails for invalid status."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearGetRoadmap(status_filter="invalid_status")
            tool.run()

        assert "status" in str(exc_info.value).lower()

    def test_validation_invalid_sort_by(self):
        """Test validation fails for invalid sort_by."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearGetRoadmap(sort_by="invalid_field")
            tool.run()

        assert "sort" in str(exc_info.value).lower()

    def test_validation_invalid_limit(self):
        """Test validation fails for invalid limit."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearGetRoadmap(limit=0)
            tool.run()

        assert "limit" in str(exc_info.value).lower()

    def test_validation_limit_too_high(self):
        """Test validation fails for limit > 100."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearGetRoadmap(limit=150)
            tool.run()

        assert "limit" in str(exc_info.value).lower()

    def test_validation_invalid_start_date(self):
        """Test validation fails for invalid start date."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearGetRoadmap(date_range_start="invalid-date")
            tool.run()

        assert "date" in str(exc_info.value).lower()

    def test_validation_invalid_end_date(self):
        """Test validation fails for invalid end date."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearGetRoadmap(date_range_end="not-a-date")
            tool.run()

        assert "date" in str(exc_info.value).lower()

    # Tool metadata tests

    def test_tool_metadata(self):
        """Test that tool metadata is correctly set."""
        tool = LinearGetRoadmap()

        assert tool.tool_name == "linear_get_roadmap"
        assert tool.tool_category == "integrations"

    def test_result_metadata(self):
        """Test that result includes proper metadata."""
        tool = LinearGetRoadmap(
            team_id="team_xyz",
            status_filter="started"
        )
        result = tool.run()

        metadata = result["metadata"]
        assert metadata["tool_name"] == "linear_get_roadmap"
        assert metadata["team_id"] == "team_xyz"
        assert metadata["status_filter"] == "started"
        assert "project_count" in metadata

    # Complex filter combinations

    def test_complex_filter_combination(self):
        """Test combining multiple filters."""
        tool = LinearGetRoadmap(
            team_id="team_xyz",
            status_filter="started",
            include_milestones=True,
            include_progress=True,
            sort_by="progress",
            limit=20
        )
        result = tool.run()

        assert result["success"] is True

    # Integration tests

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false", "LINEAR_API_KEY": "test_key"})
    @patch('requests.post')
    def test_real_api_call_structure(self, mock_post):
        """Test that real API calls are structured correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "projects": {
                    "nodes": [{
                        "id": "proj_123",
                        "name": "Test Project",
                        "state": "started",
                        "progress": 0.5,
                        "startDate": "2025-01-01",
                        "targetDate": "2025-12-31",
                        "teams": {"nodes": []},
                        "projectMilestones": {"nodes": []},
                        "issues": {"nodes": []},
                        "health": "onTrack"
                    }]
                }
            }
        }
        mock_post.return_value = mock_response

        tool = LinearGetRoadmap()
        result = tool.run()

        assert mock_post.called


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
