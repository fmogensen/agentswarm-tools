"""
Tests for LinearCreateIssue tool

Comprehensive test suite covering:
- Issue creation with various field combinations
- Validation logic
- Error handling
- Mock mode functionality
- Edge cases
"""

import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from shared.errors import APIError, AuthenticationError, ValidationError
from tools.integrations.linear.linear_create_issue import LinearCreateIssue


class TestLinearCreateIssue:
    """Test suite for LinearCreateIssue tool."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Clean up after tests."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Basic functionality tests

    def test_basic_issue_creation(self):
        """Test creating a basic issue with minimal fields."""
        tool = LinearCreateIssue(title="Test issue", team_id="team_abc123")
        result = tool.run()

        assert result["success"] is True
        assert result["issue_id"] == "mock_issue_abc123def456"
        assert result["issue_identifier"] == "ENG-123"
        assert result["title"] == "Test issue"
        assert "issue_url" in result

    def test_full_issue_creation(self):
        """Test creating issue with all optional fields."""
        tool = LinearCreateIssue(
            title="Complete feature implementation",
            description="Detailed description of the feature",
            team_id="team_abc123",
            project_id="proj_def456",
            assignee_id="user_xyz789",
            priority=1,
            labels=["label_feature", "label_urgent"],
            estimate=5.0,
            due_date="2025-12-31",
            cycle_id="cycle_123",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["team_id"] == "team_abc123"
        assert result["metadata"]["project_id"] == "proj_def456"

    def test_sub_issue_creation(self):
        """Test creating a sub-issue with parent."""
        tool = LinearCreateIssue(
            title="Sub-task", team_id="team_abc123", parent_id="parent_issue_xyz"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["issue_id"] is not None

    # Validation tests

    def test_validation_empty_title(self):
        """Test validation fails for empty title."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearCreateIssue(title="", team_id="team_abc123")
            tool.run()

        # Error is caught and returned in run() or raised
        assert "title" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_validation_empty_team_id(self):
        """Test validation fails for empty team_id."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearCreateIssue(title="Test", team_id="")
            tool.run()

        assert "team" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_validation_invalid_priority(self):
        """Test validation fails for invalid priority."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearCreateIssue(title="Test", team_id="team_abc123", priority=10)
            tool.run()

        assert "priority" in str(exc_info.value).lower()

    def test_validation_negative_estimate(self):
        """Test validation fails for negative estimate."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearCreateIssue(title="Test", team_id="team_abc123", estimate=-5.0)
            tool.run()

        assert "estimate" in str(exc_info.value).lower()

    def test_validation_invalid_due_date(self):
        """Test validation fails for invalid due date format."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearCreateIssue(title="Test", team_id="team_abc123", due_date="invalid-date")
            tool.run()

        assert "date" in str(exc_info.value).lower()

    # Priority level tests

    def test_priority_urgent(self):
        """Test creating issue with urgent priority."""
        tool = LinearCreateIssue(title="Critical bug", team_id="team_abc123", priority=1)
        result = tool.run()

        assert result["success"] is True

    def test_priority_none(self):
        """Test creating issue with no priority."""
        tool = LinearCreateIssue(title="Backlog item", team_id="team_abc123", priority=0)
        result = tool.run()

        assert result["success"] is True

    # Label management tests

    def test_multiple_labels(self):
        """Test creating issue with multiple labels."""
        tool = LinearCreateIssue(
            title="Multi-label issue",
            team_id="team_abc123",
            labels=["label_bug", "label_urgent", "label_backend"],
        )
        result = tool.run()

        assert result["success"] is True

    def test_single_label(self):
        """Test creating issue with single label."""
        tool = LinearCreateIssue(
            title="Single-label issue", team_id="team_abc123", labels=["label_feature"]
        )
        result = tool.run()

        assert result["success"] is True

    # Description tests

    def test_markdown_description(self):
        """Test creating issue with Markdown description."""
        description = """
        # Feature Overview

        ## Requirements
        - Bullet 1
        - Bullet 2

        ## Technical Details
        ```python
        def example():
            pass
        ```
        """
        tool = LinearCreateIssue(
            title="Feature with docs", team_id="team_abc123", description=description
        )
        result = tool.run()

        assert result["success"] is True

    def test_long_description(self):
        """Test creating issue with very long description."""
        long_desc = "A" * 10000  # 10k characters
        tool = LinearCreateIssue(
            title="Issue with long description", team_id="team_abc123", description=long_desc
        )
        result = tool.run()

        assert result["success"] is True

    # Custom fields tests

    def test_custom_fields(self):
        """Test creating issue with custom field values."""
        tool = LinearCreateIssue(
            title="Issue with custom fields",
            team_id="team_abc123",
            custom_fields={"field1": "value1", "field2": 42},
        )
        result = tool.run()

        assert result["success"] is True

    # Subscriber tests

    def test_multiple_subscribers(self):
        """Test creating issue with multiple subscribers."""
        tool = LinearCreateIssue(
            title="Team collaboration issue",
            team_id="team_abc123",
            subscriber_ids=["user_1", "user_2", "user_3"],
        )
        result = tool.run()

        assert result["success"] is True

    # Estimate tests

    def test_fractional_estimate(self):
        """Test creating issue with fractional estimate."""
        tool = LinearCreateIssue(title="Half-day task", team_id="team_abc123", estimate=0.5)
        result = tool.run()

        assert result["success"] is True

    def test_large_estimate(self):
        """Test creating issue with large estimate."""
        tool = LinearCreateIssue(title="Long-term project", team_id="team_abc123", estimate=100.0)
        result = tool.run()

        assert result["success"] is True

    # Date tests

    def test_various_date_formats(self):
        """Test creating issues with various valid date formats."""
        dates = ["2025-12-31", "2025-01-01", "2026-06-15"]
        for date in dates:
            tool = LinearCreateIssue(
                title=f"Issue due {date}", team_id="team_abc123", due_date=date
            )
            result = tool.run()
            assert result["success"] is True

    # Tool metadata tests

    def test_tool_metadata(self):
        """Test that tool metadata is correctly set."""
        tool = LinearCreateIssue(title="Test", team_id="team_abc123")

        assert tool.tool_name == "linear_create_issue"
        assert tool.tool_category == "integrations"

    def test_result_metadata(self):
        """Test that result includes proper metadata."""
        tool = LinearCreateIssue(title="Test", team_id="team_abc123", project_id="proj_123")
        result = tool.run()

        assert "metadata" in result
        assert result["metadata"]["tool_name"] == "linear_create_issue"
        assert result["metadata"]["team_id"] == "team_abc123"
        assert result["metadata"]["project_id"] == "proj_123"

    # Mock mode tests

    def test_mock_mode_enabled(self):
        """Test that mock mode is properly enabled."""
        tool = LinearCreateIssue(title="Test", team_id="team_abc123")
        result = tool.run()

        assert result["metadata"]["mock_mode"] is True
        assert result["issue_identifier"] == "ENG-123"

    # Edge cases

    def test_very_long_title(self):
        """Test creating issue with maximum length title."""
        long_title = "A" * 255
        tool = LinearCreateIssue(title=long_title, team_id="team_abc123")
        result = tool.run()

        assert result["success"] is True

    def test_special_characters_in_title(self):
        """Test creating issue with special characters in title."""
        tool = LinearCreateIssue(
            title="Bug: User can't access @mentions & #hashtags", team_id="team_abc123"
        )
        result = tool.run()

        assert result["success"] is True

    def test_unicode_in_description(self):
        """Test creating issue with Unicode characters."""
        tool = LinearCreateIssue(
            title="International support",
            team_id="team_abc123",
            description="支持中文 • Поддержка русского • 日本語サポート",
        )
        result = tool.run()

        assert result["success"] is True

    # Integration tests

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false", "LINEAR_API_KEY": "test_key"})
    @patch("requests.post")
    def test_real_api_call_structure(self, mock_post):
        """Test that real API calls are structured correctly."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "issueCreate": {
                    "success": True,
                    "issue": {
                        "id": "issue_real_123",
                        "identifier": "ENG-456",
                        "title": "Test issue",
                        "url": "https://linear.app/workspace/issue/ENG-456",
                        "state": {"id": "state_123", "name": "Todo"},
                    },
                }
            }
        }
        mock_post.return_value = mock_response

        tool = LinearCreateIssue(title="Test issue", team_id="team_abc123")
        result = tool.run()

        # Verify API was called
        assert mock_post.called
        call_args = mock_post.call_args

        # Verify GraphQL structure
        assert "query" in call_args[1]["json"]
        assert "variables" in call_args[1]["json"]
        assert "input" in call_args[1]["json"]["variables"]

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false", "LINEAR_API_KEY": "test_key"})
    @patch("requests.post")
    def test_graphql_error_handling(self, mock_post):
        """Test handling of GraphQL errors."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"errors": [{"message": "Invalid team ID"}]}
        mock_post.return_value = mock_response

        with pytest.raises(APIError) as exc_info:
            tool = LinearCreateIssue(title="Test issue", team_id="invalid_team")
            tool.run()
        assert "invalid team" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_missing_api_key(self):
        """Test error when API key is missing."""
        with pytest.raises(APIError) as exc_info:
            tool = LinearCreateIssue(title="Test issue", team_id="team_abc123")
            tool.run()
        assert "api key" in str(exc_info.value).lower() or "linear_api_key" in str(exc_info.value).lower()


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
