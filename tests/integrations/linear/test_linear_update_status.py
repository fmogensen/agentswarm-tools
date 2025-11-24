"""
Tests for LinearUpdateStatus tool

Test coverage:
- Status updates with state transitions
- Priority and estimate changes
- Label management
- Assignee updates
- Comment addition
- Validation and error handling
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from shared.errors import ValidationError
from tools.integrations.linear.linear_update_status import LinearUpdateStatus


class TestLinearUpdateStatus:
    """Test suite for LinearUpdateStatus tool."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Clean up after tests."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Basic functionality tests

    def test_update_state_by_name(self):
        """Test updating issue state by name."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", state_name="In Progress")
        result = tool.run()

        assert result["success"] is True
        assert result["new_state"] == "In Progress"
        assert result["previous_state"] == "Todo"

    def test_update_state_by_id(self):
        """Test updating issue state by ID."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", state_id="state_xyz789")
        result = tool.run()

        assert result["success"] is True
        assert result["transition_valid"] is True

    def test_update_priority(self):
        """Test updating issue priority."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", priority=1)  # Urgent
        result = tool.run()

        assert result["success"] is True
        assert "priority" in result["metadata"]["updates_applied"]

    def test_update_assignee(self):
        """Test updating issue assignee."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", assignee_id="user_xyz789")
        result = tool.run()

        assert result["success"] is True
        assert "assignee" in result["metadata"]["updates_applied"]

    def test_unassign_issue(self):
        """Test removing assignee from issue."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", assignee_id="unassign")
        result = tool.run()

        assert result["success"] is True

    def test_update_estimate(self):
        """Test updating issue estimate."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", estimate=5.0)
        result = tool.run()

        assert result["success"] is True
        assert "estimate" in result["metadata"]["updates_applied"]

    # Multiple field updates

    def test_update_multiple_fields(self):
        """Test updating multiple fields at once."""
        tool = LinearUpdateStatus(
            issue_id="issue_abc123",
            state_name="In Progress",
            priority=2,
            assignee_id="user_xyz789",
            estimate=3.0,
        )
        result = tool.run()

        assert result["success"] is True
        updates = result["metadata"]["updates_applied"]
        assert "state" in updates
        assert "priority" in updates
        assert "assignee" in updates
        assert "estimate" in updates

    def test_update_with_comment(self):
        """Test updating status with comment."""
        tool = LinearUpdateStatus(
            issue_id="issue_abc123",
            state_name="Done",
            comment="Completed implementation and testing",
        )
        result = tool.run()

        assert result["success"] is True
        assert "comment_added" in result["metadata"]["updates_applied"]

    # Label management

    def test_add_labels(self):
        """Test adding labels to issue."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", add_labels=["label_urgent", "label_bug"])
        result = tool.run()

        assert result["success"] is True
        assert "labels_added" in result["metadata"]["updates_applied"]

    def test_remove_labels(self):
        """Test removing labels from issue."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", remove_labels=["label_backlog"])
        result = tool.run()

        assert result["success"] is True
        assert "labels_removed" in result["metadata"]["updates_applied"]

    def test_add_and_remove_labels(self):
        """Test adding and removing labels simultaneously."""
        tool = LinearUpdateStatus(
            issue_id="issue_abc123", add_labels=["label_urgent"], remove_labels=["label_backlog"]
        )
        result = tool.run()

        assert result["success"] is True
        updates = result["metadata"]["updates_applied"]
        assert "labels_added" in updates
        assert "labels_removed" in updates

    # Validation tests

    def test_validation_empty_issue_id(self):
        """Test validation fails for empty issue ID."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearUpdateStatus(issue_id="", state_name="In Progress")
            tool.run()

        assert "issue" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_validation_no_updates(self):
        """Test validation fails when no updates specified."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearUpdateStatus(issue_id="issue_abc123")
            tool.run()

        assert "update" in str(exc_info.value).lower()

    def test_validation_both_state_id_and_name(self):
        """Test validation fails when both state_id and state_name provided."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearUpdateStatus(
                issue_id="issue_abc123", state_id="state_123", state_name="In Progress"
            )
            tool.run()

        assert "state" in str(exc_info.value).lower()

    def test_validation_invalid_priority(self):
        """Test validation fails for invalid priority."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearUpdateStatus(issue_id="issue_abc123", priority=10)
            tool.run()

        assert "priority" in str(exc_info.value).lower()

    def test_validation_negative_estimate(self):
        """Test validation fails for negative estimate."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearUpdateStatus(issue_id="issue_abc123", estimate=-1.0)
            tool.run()

        assert "estimate" in str(exc_info.value).lower()

    # Priority level tests

    def test_all_priority_levels(self):
        """Test all valid priority levels."""
        priorities = [0, 1, 2, 3, 4]  # None, Urgent, High, Normal, Low
        for priority in priorities:
            tool = LinearUpdateStatus(issue_id="issue_abc123", priority=priority)
            result = tool.run()
            assert result["success"] is True

    # State transition tests

    def test_state_transitions(self):
        """Test various state transitions."""
        states = ["Todo", "In Progress", "In Review", "Done", "Canceled"]
        for state in states:
            tool = LinearUpdateStatus(issue_id="issue_abc123", state_name=state)
            result = tool.run()
            assert result["success"] is True
            assert result["new_state"] == state

    # Estimate tests

    def test_fractional_estimate(self):
        """Test updating with fractional estimate."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", estimate=2.5)
        result = tool.run()

        assert result["success"] is True

    def test_zero_estimate(self):
        """Test updating with zero estimate."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", estimate=0.0)
        result = tool.run()

        assert result["success"] is True

    # Tool metadata tests

    def test_tool_metadata(self):
        """Test that tool metadata is correctly set."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", state_name="Done")

        assert tool.tool_name == "linear_update_status"
        assert tool.tool_category == "integrations"

    def test_updates_summary(self):
        """Test that updates summary is correctly generated."""
        tool = LinearUpdateStatus(
            issue_id="issue_abc123",
            state_name="In Progress",
            priority=1,
            estimate=5.0,
            add_labels=["label_bug"],
        )
        result = tool.run()

        updates = result["metadata"]["updates_applied"]
        assert updates["state"] == "In Progress"
        assert updates["priority"] == 1
        assert updates["estimate"] == 5.0
        assert updates["labels_added"] == 1

    # Comment tests

    def test_comment_only_update(self):
        """Test updating with only a comment."""
        tool = LinearUpdateStatus(issue_id="issue_abc123", comment="Status update comment")
        result = tool.run()

        assert result["success"] is True

    def test_long_comment(self):
        """Test updating with long comment."""
        long_comment = "A" * 5000
        tool = LinearUpdateStatus(issue_id="issue_abc123", comment=long_comment)
        result = tool.run()

        assert result["success"] is True

    # Integration tests

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false", "LINEAR_API_KEY": "test_key"})
    @patch("requests.post")
    def test_real_api_call_structure(self, mock_post):
        """Test that real API calls are structured correctly."""
        # Mock get current issue
        mock_get_response = MagicMock()
        mock_get_response.json.return_value = {
            "data": {
                "issue": {
                    "id": "issue_abc123",
                    "identifier": "ENG-123",
                    "state": {"id": "state_1", "name": "Todo"},
                    "team": {"id": "team_123"},
                    "labels": {"nodes": []},
                }
            }
        }
        mock_get_response.raise_for_status = MagicMock()

        # Mock resolve state name
        mock_state_response = MagicMock()
        mock_state_response.json.return_value = {
            "data": {
                "workflowStates": {
                    "nodes": [
                        {"id": "state_2", "name": "In Progress"},
                    ]
                }
            }
        }
        mock_state_response.raise_for_status = MagicMock()

        # Mock update issue
        mock_update_response = MagicMock()
        mock_update_response.json.return_value = {
            "data": {
                "issueUpdate": {
                    "success": True,
                    "issue": {
                        "id": "issue_abc123",
                        "identifier": "ENG-123",
                        "state": {"id": "state_2", "name": "In Progress"},
                        "priority": 1,
                        "estimate": 5.0,
                    },
                }
            }
        }
        mock_update_response.raise_for_status = MagicMock()

        # Mock responses: get issue, resolve state, update issue
        mock_post.side_effect = [mock_get_response, mock_state_response, mock_update_response]

        tool = LinearUpdateStatus(issue_id="issue_abc123", state_name="In Progress")
        result = tool.run()

        # Verify API was called and result is successful
        assert mock_post.call_count >= 2  # At least get + update calls
        assert result["success"] is True


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
