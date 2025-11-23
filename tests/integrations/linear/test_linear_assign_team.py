"""
Tests for LinearAssignTeam tool

Test coverage:
- Team and user assignment
- Cycle/sprint management
- Capacity planning
- Auto-assignment strategies
- Batch operations
- Validation and error handling
"""

import pytest
import os
from unittest.mock import patch, MagicMock

from tools.integrations.linear.linear_assign_team import LinearAssignTeam


class TestLinearAssignTeam:
    """Test suite for LinearAssignTeam tool."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Clean up after tests."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Basic functionality tests

    def test_basic_team_assignment(self):
        """Test assigning single issue to team."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc123"],
            team_id="team_xyz"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["assigned_count"] == 1
        assert len(result["assignments"]) == 1

    def test_assign_to_user(self):
        """Test assigning issue to specific user."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc123"],
            assignee_id="user_xyz789"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["assignments"][0]["assigned_to"] == "user_xyz789"

    def test_assign_to_cycle(self):
        """Test assigning issue to cycle/sprint."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc123"],
            team_id="team_xyz",
            cycle_id="cycle_123"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["cycle_info"]["cycle_id"] == "cycle_123"

    def test_assign_with_estimate(self):
        """Test assigning issue with estimate."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc123"],
            team_id="team_xyz",
            estimate=5.0
        )
        result = tool.run()

        assert result["success"] is True
        assert result["assignments"][0]["estimate"] == 5.0

    # Multiple issue assignment

    def test_assign_multiple_issues(self):
        """Test assigning multiple issues at once."""
        tool = LinearAssignTeam(
            issue_ids=["issue_1", "issue_2", "issue_3"],
            team_id="team_xyz",
            assignee_id="user_abc"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["assigned_count"] == 3
        assert len(result["assignments"]) == 3

    def test_bulk_assignment(self):
        """Test bulk assignment to team."""
        tool = LinearAssignTeam(
            issue_ids=[f"issue_{i}" for i in range(10)],
            team_id="team_xyz",
            cycle_id="cycle_123"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["assigned_count"] == 10

    # Auto-assignment tests

    def test_auto_assign_lowest_workload(self):
        """Test auto-assigning to member with lowest workload."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc123"],
            team_id="team_xyz",
            auto_assign=True,
            estimate=3.0
        )
        result = tool.run()

        assert result["success"] is True
        assert "capacity_summary" in result
        assert result["capacity_summary"]["utilization"] >= 0

    def test_distribute_evenly(self):
        """Test distributing issues evenly across team."""
        tool = LinearAssignTeam(
            issue_ids=[f"issue_{i}" for i in range(6)],
            team_id="team_xyz",
            distribute_evenly=True,
            estimate=2.0
        )
        result = tool.run()

        assert result["success"] is True
        assert result["assigned_count"] == 6
        # Issues should be distributed across team members

    # Capacity planning tests

    def test_capacity_summary(self):
        """Test capacity summary is generated."""
        tool = LinearAssignTeam(
            issue_ids=["issue_1", "issue_2"],
            team_id="team_xyz",
            auto_assign=True,
            estimate=5.0
        )
        result = tool.run()

        assert result["success"] is True
        capacity = result["capacity_summary"]
        assert "total_capacity" in capacity
        assert "allocated" in capacity
        assert "remaining" in capacity
        assert "utilization" in capacity

    def test_capacity_utilization(self):
        """Test capacity utilization calculation."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc"],
            team_id="team_xyz",
            estimate=5.0
        )
        result = tool.run()

        capacity = result["capacity_summary"]
        assert 0 <= capacity["utilization"] <= 1.0

    # Date planning tests

    def test_assignment_with_dates(self):
        """Test assigning with start and due dates."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc123"],
            team_id="team_xyz",
            start_date="2025-12-01",
            due_date="2025-12-14"
        )
        result = tool.run()

        assert result["success"] is True

    def test_cycle_with_dates(self):
        """Test cycle assignment includes date info."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc123"],
            cycle_id="cycle_123"
        )
        result = tool.run()

        assert result["success"] is True
        if result["cycle_info"]:
            assert "start_date" in result["cycle_info"]
            assert "end_date" in result["cycle_info"]

    # Team info tests

    def test_team_info_included(self):
        """Test team information is included in result."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc123"],
            team_id="team_xyz"
        )
        result = tool.run()

        assert result["success"] is True
        team_info = result["team_info"]
        assert "team_id" in team_info
        assert "team_name" in team_info
        assert "member_count" in team_info

    # Validation tests

    def test_validation_empty_issue_ids(self):
        """Test validation fails for empty issue list."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearAssignTeam(
                issue_ids=[],
                team_id="team_xyz"
            )
            tool.run()

        assert "issue" in str(exc_info.value).lower()

    def test_validation_negative_estimate(self):
        """Test validation fails for negative estimate."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearAssignTeam(
                issue_ids=["issue_abc"],
                estimate=-5.0
            )
            tool.run()

        assert "estimate" in str(exc_info.value).lower()

    def test_validation_conflicting_assignee_options(self):
        """Test validation fails when assignee_id conflicts with auto_assign."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearAssignTeam(
                issue_ids=["issue_abc"],
                assignee_id="user_123",
                auto_assign=True
            )
            tool.run()

        assert "assignee" in str(exc_info.value).lower() or "auto" in str(exc_info.value).lower()

    def test_validation_both_auto_and_distribute(self):
        """Test validation fails when both auto_assign and distribute_evenly are True."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearAssignTeam(
                issue_ids=["issue_abc"],
                auto_assign=True,
                distribute_evenly=True
            )
            tool.run()

        assert "auto" in str(exc_info.value).lower() or "distribute" in str(exc_info.value).lower()

    def test_validation_invalid_date_format(self):
        """Test validation fails for invalid date format."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearAssignTeam(
                issue_ids=["issue_abc"],
                start_date="invalid-date"
            )
            tool.run()

        assert "date" in str(exc_info.value).lower()

    # Estimate tests

    def test_various_estimates(self):
        """Test various estimate values."""
        estimates = [0.5, 1.0, 2.0, 5.0, 8.0, 13.0]
        for estimate in estimates:
            tool = LinearAssignTeam(
                issue_ids=["issue_abc"],
                team_id="team_xyz",
                estimate=estimate
            )
            result = tool.run()
            assert result["success"] is True

    # Cycle info tests

    def test_cycle_progress(self):
        """Test cycle includes progress information."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc"],
            cycle_id="cycle_123"
        )
        result = tool.run()

        if result["cycle_info"]:
            assert "cycle_name" in result["cycle_info"]
            assert "progress" in result["cycle_info"]

    # Tool metadata tests

    def test_tool_metadata(self):
        """Test that tool metadata is correctly set."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc"],
            team_id="team_xyz"
        )

        assert tool.tool_name == "linear_assign_team"
        assert tool.tool_category == "integrations"

    def test_result_metadata(self):
        """Test that result includes proper metadata."""
        tool = LinearAssignTeam(
            issue_ids=["issue_abc"],
            team_id="team_xyz",
            cycle_id="cycle_123"
        )
        result = tool.run()

        metadata = result["metadata"]
        assert metadata["tool_name"] == "linear_assign_team"
        assert metadata["team_id"] == "team_xyz"
        assert metadata["cycle_id"] == "cycle_123"

    # Assignment details tests

    def test_assignment_details_structure(self):
        """Test that assignment details have correct structure."""
        tool = LinearAssignTeam(
            issue_ids=["issue_1", "issue_2"],
            team_id="team_xyz",
            assignee_id="user_abc"
        )
        result = tool.run()

        for assignment in result["assignments"]:
            assert "issue_id" in assignment
            assert "issue_identifier" in assignment
            assert "assigned_to" in assignment
            assert "team" in assignment

    # Integration tests

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false", "LINEAR_API_KEY": "test_key"})
    @patch('requests.post')
    def test_real_api_call_structure(self, mock_post):
        """Test that real API calls are structured correctly."""
        # Mock team info
        mock_team_response = MagicMock()
        mock_team_response.json.return_value = {
            "data": {
                "team": {
                    "id": "team_xyz",
                    "name": "Engineering",
                    "key": "ENG",
                    "members": {"nodes": []}
                }
            }
        }

        # Mock issue update
        mock_update_response = MagicMock()
        mock_update_response.json.return_value = {
            "data": {
                "issueUpdate": {
                    "success": True,
                    "issue": {
                        "id": "issue_abc",
                        "identifier": "ENG-123",
                        "assignee": {"id": "user_123", "name": "Alice"},
                        "estimate": 5.0
                    }
                }
            }
        }

        mock_post.side_effect = [mock_team_response, mock_update_response]

        tool = LinearAssignTeam(
            issue_ids=["issue_abc"],
            team_id="team_xyz",
            assignee_id="user_123"
        )
        result = tool.run()

        assert mock_post.call_count >= 1


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
