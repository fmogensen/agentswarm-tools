"""
Tests for LinearSyncGitHub tool

Test coverage:
- Bi-directional sync operations
- Conflict detection and resolution
- Label mapping
- Comment syncing
- Branch creation
- PR linking
- Batch operations
- Validation and error handling
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from shared.errors import APIError
from tools.integrations.linear.linear_sync_github import LinearSyncGitHub


class TestLinearSyncGitHub:
    """Test suite for LinearSyncGitHub tool."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Clean up after tests."""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # Basic sync tests

    def test_linear_to_github_sync(self):
        """Test syncing from Linear to GitHub."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_repo="company/project",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["synced_count"] == 1
        assert result["sync_details"][0]["sync_direction"] == "linear_to_github"

    def test_github_to_linear_sync(self):
        """Test syncing from GitHub to Linear."""
        tool = LinearSyncGitHub(
            sync_direction="github_to_linear", github_issue_number=42, github_repo="company/project"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["synced_count"] == 1

    def test_bidirectional_sync(self):
        """Test bidirectional sync."""
        tool = LinearSyncGitHub(
            sync_direction="bidirectional",
            linear_issue_id="issue_abc123",
            github_issue_number=42,
            github_repo="company/project",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["sync_details"][0]["sync_direction"] == "bidirectional"

    # Sync options tests

    def test_sync_with_comments(self):
        """Test syncing with comments enabled."""
        tool = LinearSyncGitHub(
            sync_direction="bidirectional",
            linear_issue_id="issue_abc123",
            github_issue_number=42,
            github_repo="company/project",
            sync_comments=True,
        )
        result = tool.run()

        assert result["success"] is True
        changes = result["sync_details"][0]["changes_synced"]
        assert "comments" in changes

    def test_sync_with_labels(self):
        """Test syncing with labels enabled."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_repo="company/project",
            sync_labels=True,
        )
        result = tool.run()

        assert result["success"] is True
        changes = result["sync_details"][0]["changes_synced"]
        assert "labels" in changes

    def test_sync_with_status(self):
        """Test syncing with status enabled."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_repo="company/project",
            sync_status=True,
        )
        result = tool.run()

        assert result["success"] is True
        changes = result["sync_details"][0]["changes_synced"]
        assert "status" in changes

    def test_sync_all_options(self):
        """Test syncing with all options enabled."""
        tool = LinearSyncGitHub(
            sync_direction="bidirectional",
            linear_issue_id="issue_abc123",
            github_issue_number=42,
            github_repo="company/project",
            sync_comments=True,
            sync_labels=True,
            sync_status=True,
        )
        result = tool.run()

        assert result["success"] is True

    # Conflict resolution tests

    def test_conflict_linear_wins(self):
        """Test conflict resolution with linear_wins."""
        tool = LinearSyncGitHub(
            sync_direction="bidirectional",
            linear_issue_id="issue_abc123",
            github_issue_number=42,
            github_repo="company/project",
            conflict_resolution="linear_wins",
        )
        result = tool.run()

        assert result["success"] is True

    def test_conflict_github_wins(self):
        """Test conflict resolution with github_wins."""
        tool = LinearSyncGitHub(
            sync_direction="bidirectional",
            linear_issue_id="issue_abc123",
            github_issue_number=42,
            github_repo="company/project",
            conflict_resolution="github_wins",
        )
        result = tool.run()

        assert result["success"] is True

    def test_conflict_manual(self):
        """Test conflict resolution with manual mode."""
        tool = LinearSyncGitHub(
            sync_direction="bidirectional",
            linear_issue_id="issue_abc123",
            github_issue_number=42,
            github_repo="company/project",
            conflict_resolution="manual",
        )
        result = tool.run()

        assert result["success"] is True
        # Manual mode should return conflicts for user to resolve
        assert "conflicts" in result

    # Label mapping tests

    def test_label_mapping(self):
        """Test custom label mapping."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_repo="company/project",
            sync_labels=True,
            label_mapping={"bug": "type: bug", "urgent": "priority: high"},
        )
        result = tool.run()

        assert result["success"] is True

    # Branch creation tests

    def test_create_branch(self):
        """Test automatic branch creation."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_repo="company/project",
            create_branch=True,
        )
        result = tool.run()

        assert result["success"] is True
        assert "branch" in result["created_items"]
        assert result["created_items"]["branch"].startswith("linear/")

    # PR linking tests

    def test_link_pull_request(self):
        """Test linking GitHub PR to Linear issue."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_repo="company/project",
            github_pr_number=123,
        )
        result = tool.run()

        assert result["success"] is True
        assert "pr_link" in result["created_items"]

    # Batch sync tests

    def test_batch_sync(self):
        """Test batch sync with filters."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            github_repo="company/project",
            batch_sync=True,
            batch_filters={"team_id": "team_xyz", "state": "In Progress"},
        )
        result = tool.run()

        assert result["success"] is True
        assert result["synced_count"] > 1

    def test_batch_sync_multiple_issues(self):
        """Test batch sync processes multiple issues."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            github_repo="company/project",
            batch_sync=True,
            batch_filters={"team_id": "team_xyz"},
        )
        result = tool.run()

        assert result["success"] is True
        assert len(result["sync_details"]) > 1

    # Validation tests

    def test_validation_invalid_direction(self):
        """Test validation fails for invalid sync direction."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearSyncGitHub(
                sync_direction="invalid_direction",
                github_repo="company/project",
                linear_issue_id="issue_abc",
            )
            tool.run()

        assert "direction" in str(exc_info.value).lower()

    def test_validation_invalid_repo_format(self):
        """Test validation fails for invalid repo format."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearSyncGitHub(
                sync_direction="linear_to_github",
                github_repo="invalid-format",
                linear_issue_id="issue_abc",
            )
            tool.run()

        assert "repo" in str(exc_info.value).lower()

    def test_validation_no_issue_ids(self):
        """Test validation fails when no issue IDs provided."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearSyncGitHub(
                sync_direction="linear_to_github", github_repo="company/project"
            )
            tool.run()

        assert (
            "issue" in str(exc_info.value).lower()
            or "linear_issue_id" in str(exc_info.value).lower()
        )

    def test_validation_batch_without_filters(self):
        """Test validation fails for batch sync without filters."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearSyncGitHub(
                sync_direction="linear_to_github", github_repo="company/project", batch_sync=True
            )
            tool.run()

        assert "filter" in str(exc_info.value).lower()

    def test_validation_invalid_conflict_resolution(self):
        """Test validation fails for invalid conflict resolution."""
        with pytest.raises(Exception) as exc_info:
            tool = LinearSyncGitHub(
                sync_direction="bidirectional",
                linear_issue_id="issue_abc",
                github_repo="company/project",
                conflict_resolution="invalid_option",
            )
            tool.run()

        assert "conflict" in str(exc_info.value).lower()

    # Sync details tests

    def test_sync_details_structure(self):
        """Test sync details have correct structure."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_repo="company/project",
        )
        result = tool.run()

        detail = result["sync_details"][0]
        assert "linear_issue_id" in detail
        assert "linear_identifier" in detail
        assert "sync_direction" in detail
        assert "changes_synced" in detail

    def test_github_url_included(self):
        """Test GitHub URL is included in sync details."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_issue_number=42,
            github_repo="company/project",
        )
        result = tool.run()

        detail = result["sync_details"][0]
        assert "github_url" in detail
        assert "github.com" in detail["github_url"]

    # Created items tests

    def test_created_items_branch(self):
        """Test created items includes branch when created."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_repo="company/project",
            create_branch=True,
        )
        result = tool.run()

        assert "created_items" in result
        assert "branch" in result["created_items"]

    def test_created_items_pr_link(self):
        """Test created items includes PR link when provided."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc123",
            github_repo="company/project",
            github_pr_number=123,
        )
        result = tool.run()

        assert "created_items" in result
        assert "pr_link" in result["created_items"]

    # Tool metadata tests

    def test_tool_metadata(self):
        """Test that tool metadata is correctly set."""
        tool = LinearSyncGitHub(
            sync_direction="linear_to_github",
            linear_issue_id="issue_abc",
            github_repo="company/project",
        )

        assert tool.tool_name == "linear_sync_github"
        assert tool.tool_category == "integrations"

    def test_result_metadata(self):
        """Test that result includes proper metadata."""
        tool = LinearSyncGitHub(
            sync_direction="bidirectional",
            linear_issue_id="issue_abc",
            github_repo="company/project",
        )
        result = tool.run()

        metadata = result["metadata"]
        assert metadata["tool_name"] == "linear_sync_github"
        assert metadata["sync_direction"] == "bidirectional"
        assert metadata["github_repo"] == "company/project"

    # Repository format tests

    def test_valid_repo_formats(self):
        """Test various valid repository formats."""
        valid_repos = [
            "owner/repo",
            "org-name/repo-name",
            "user_123/project_456",
            "company.com/repo.name",
        ]
        for repo in valid_repos:
            tool = LinearSyncGitHub(
                sync_direction="linear_to_github", linear_issue_id="issue_abc", github_repo=repo
            )
            result = tool.run()
            assert result["success"] is True

    # Integration tests

    @patch.dict(
        os.environ,
        {"USE_MOCK_APIS": "false", "LINEAR_API_KEY": "test_key", "GITHUB_TOKEN": "gh_token"},
    )
    @patch("requests.post")
    @patch("requests.get")
    def test_real_api_call_structure(self, mock_get, mock_post):
        """Test that real API calls are structured correctly."""
        # Mock Linear API response
        mock_linear_response = MagicMock()
        mock_linear_response.json.return_value = {
            "data": {
                "issue": {
                    "id": "issue_abc",
                    "identifier": "ENG-123",
                    "title": "Test issue",
                    "description": "Description",
                    "state": {"name": "Todo"},
                    "labels": {"nodes": []},
                    "updatedAt": "2025-01-01T00:00:00Z",
                }
            }
        }

        # Mock GitHub API response
        mock_github_response = MagicMock()
        mock_github_response.json.return_value = {
            "number": 42,
            "title": "Test issue",
            "body": "Description",
            "state": "open",
            "labels": [],
        }

        mock_post.return_value = mock_linear_response
        mock_get.return_value = mock_github_response

        tool = LinearSyncGitHub(
            sync_direction="bidirectional",
            linear_issue_id="issue_abc",
            github_issue_number=42,
            github_repo="company/project",
        )
        result = tool.run()

        # Verify API calls were made
        assert mock_post.called or mock_get.called

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_missing_linear_api_key(self):
        """Test error when Linear API key is missing."""
        with pytest.raises(APIError) as exc_info:
            tool = LinearSyncGitHub(
                sync_direction="linear_to_github",
                linear_issue_id="issue_abc",
                github_repo="company/project",
            )
            tool.run()
        assert "api key" in str(exc_info.value).lower() or "linear" in str(exc_info.value).lower()

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false", "LINEAR_API_KEY": "test_key"})
    def test_missing_github_token(self):
        """Test error when GitHub token is missing."""
        with pytest.raises(APIError) as exc_info:
            tool = LinearSyncGitHub(
                sync_direction="linear_to_github",
                linear_issue_id="issue_abc",
                github_repo="company/project",
            )
            tool.run()
        assert "token" in str(exc_info.value).lower() or "github" in str(exc_info.value).lower()


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
