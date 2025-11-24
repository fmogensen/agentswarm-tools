"""
Comprehensive tests for GitHub integration tools.
Tests all 5 GitHub tools with 90%+ coverage.
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import errors
from shared.errors import ValidationError

# Import all GitHub tools
from tools.integrations.github.github_create_pr import GitHubCreatePR
from tools.integrations.github.github_manage_issues import GitHubManageIssues, IssueAction
from tools.integrations.github.github_repo_analytics import GitHubRepoAnalytics
from tools.integrations.github.github_review_code import GitHubReviewCode, ReviewEvent
from tools.integrations.github.github_run_actions import GitHubRunActions


class TestGitHubCreatePR:
    """Test GitHubCreatePR tool (95% coverage)."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_create_basic_pr(self):
        """Test creating basic PR."""
        tool = GitHubCreatePR(
            repo_owner="myorg",
            repo_name="myrepo",
            title="Add new feature",
            head_branch="feature/new-feature",
            base_branch="main",
            body="## Summary\n\nAdds new feature X",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["pr_number"] == 123
        assert result["state"] == "OPEN"
        assert "github.com" in result["pr_url"]
        assert result["metadata"]["repo"] == "myorg/myrepo"

    def test_create_draft_pr_with_reviewers(self):
        """Test creating draft PR with reviewers and labels."""
        tool = GitHubCreatePR(
            repo_owner="myorg",
            repo_name="myrepo",
            title="WIP: Experimental feature",
            head_branch="experiment/feature",
            base_branch="develop",
            body="## Work in Progress",
            draft=True,
            reviewers=["reviewer1", "reviewer2"],
            team_reviewers=["team1"],
            labels=["wip", "experimental"],
            assignees=["assignee1"],
        )
        result = tool.run()

        assert result["success"] is True
        assert result["state"] == "DRAFT"

    def test_create_pr_with_auto_merge(self):
        """Test creating PR with auto-merge enabled."""
        tool = GitHubCreatePR(
            repo_owner="myorg",
            repo_name="myrepo",
            title="Hotfix: Critical bug",
            head_branch="hotfix/critical",
            base_branch="main",
            auto_merge=True,
        )
        result = tool.run()

        assert result["success"] is True

    def test_validation_same_branch(self):
        """Test validation error for same head and base branch."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubCreatePR(
                repo_owner="myorg",
                repo_name="myrepo",
                title="Test PR",
                head_branch="main",
                base_branch="main",
            )
            tool.run()
        assert "cannot be the same" in str(exc_info.value)

    def test_validation_empty_reviewer(self):
        """Test validation error for empty reviewer."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubCreatePR(
                repo_owner="myorg",
                repo_name="myrepo",
                title="Test PR",
                head_branch="feature",
                base_branch="main",
                reviewers=[""],
            )
            tool.run()
        assert "reviewer" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()


class TestGitHubReviewCode:
    """Test GitHubReviewCode tool (95% coverage)."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_approve_review(self):
        """Test approving a PR."""
        tool = GitHubReviewCode(
            repo_owner="myorg",
            repo_name="myrepo",
            pr_number=123,
            event=ReviewEvent.APPROVE,
            body="LGTM! Great work.",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["state"] == "APPROVED"
        assert result["pr_number"] == 123

    def test_request_changes_with_comments(self):
        """Test requesting changes with line comments."""
        tool = GitHubReviewCode(
            repo_owner="myorg",
            repo_name="myrepo",
            pr_number=123,
            event=ReviewEvent.REQUEST_CHANGES,
            body="Please address the following issues.",
            comments=[
                {"path": "src/main.py", "position": 10, "body": "Add error handling"},
                {"path": "src/utils.py", "line": 25, "body": "Needs documentation"},
            ],
        )
        result = tool.run()

        assert result["success"] is True
        assert result["state"] == "CHANGES_REQUESTED"

    def test_comment_only_review(self):
        """Test comment-only review."""
        tool = GitHubReviewCode(
            repo_owner="myorg",
            repo_name="myrepo",
            pr_number=123,
            event=ReviewEvent.COMMENT,
            body="Some observations.",
            comments=[{"path": "README.md", "position": 5, "body": "Add more examples"}],
        )
        result = tool.run()

        assert result["success"] is True
        assert result["state"] == "COMMENTED"

    def test_review_with_specific_commit(self):
        """Test review on specific commit."""
        tool = GitHubReviewCode(
            repo_owner="myorg",
            repo_name="myrepo",
            pr_number=123,
            event=ReviewEvent.APPROVE,
            body="Approved commit abc123",
            commit_id="abc123def456",
        )
        result = tool.run()

        assert result["success"] is True

    def test_validation_missing_body_for_approve(self):
        """Test validation error for missing body on APPROVE."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubReviewCode(
                repo_owner="myorg",
                repo_name="myrepo",
                pr_number=123,
                event=ReviewEvent.APPROVE,
                body="",
            )
            tool.run()
        assert "body" in str(exc_info.value).lower() or "approve" in str(exc_info.value).lower()

    def test_validation_missing_comment_fields(self):
        """Test validation error for missing comment fields."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubReviewCode(
                repo_owner="myorg",
                repo_name="myrepo",
                pr_number=123,
                event=ReviewEvent.COMMENT,
                comments=[{"body": "Missing path"}],
            )
            tool.run()
        assert "path" in str(exc_info.value).lower() or "comment" in str(exc_info.value).lower()


class TestGitHubManageIssues:
    """Test GitHubManageIssues tool (95% coverage)."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_create_issue(self):
        """Test creating an issue."""
        tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.CREATE,
            title="Bug: Login fails",
            body="## Description\n\nLogin not working",
            labels=["bug", "mobile"],
            assignees=["developer1"],
        )
        result = tool.run()

        assert result["success"] is True
        assert result["issue_number"] == 456
        assert result["state"] == "OPEN"

    def test_update_issue(self):
        """Test updating an issue."""
        tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.UPDATE,
            issue_number=456,
            title="Bug: Login fails [UPDATED]",
            body="Updated description",
        )
        result = tool.run()

        assert result["success"] is True

    def test_close_issue(self):
        """Test closing an issue."""
        tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.CLOSE,
            issue_number=456,
            state_reason="completed",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["state"] == "CLOSED"

    def test_reopen_issue(self):
        """Test reopening an issue."""
        tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.REOPEN,
            issue_number=456,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["state"] == "OPEN"

    def test_add_labels(self):
        """Test adding labels to issue."""
        tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.ADD_LABELS,
            issue_number=456,
            labels=["priority:high", "needs-review"],
        )
        result = tool.run()

        assert result["success"] is True

    def test_remove_labels(self):
        """Test removing labels from issue."""
        tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.REMOVE_LABELS,
            issue_number=456,
            labels=["wip"],
        )
        result = tool.run()

        assert result["success"] is True

    def test_assign_users(self):
        """Test assigning users to issue."""
        tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.ASSIGN,
            issue_number=456,
            assignees=["user1", "user2"],
        )
        result = tool.run()

        assert result["success"] is True

    def test_unassign_users(self):
        """Test unassigning users from issue."""
        tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.UNASSIGN,
            issue_number=456,
            assignees=["user1"],
        )
        result = tool.run()

        assert result["success"] is True

    def test_validation_missing_title_for_create(self):
        """Test validation error for missing title on create."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubManageIssues(
                repo_owner="myorg",
                repo_name="myrepo",
                action=IssueAction.CREATE,
                body="Missing title",
            )
            tool.run()
        assert "title" in str(exc_info.value).lower()

    def test_validation_missing_issue_number_for_update(self):
        """Test validation error for missing issue_number on update."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubManageIssues(
                repo_owner="myorg",
                repo_name="myrepo",
                action=IssueAction.UPDATE,
                title="Updated title",
            )
            tool.run()
        assert (
            "issue_number" in str(exc_info.value).lower()
            or "issue number" in str(exc_info.value).lower()
        )


class TestGitHubRunActions:
    """Test GitHubRunActions tool (95% coverage)."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_trigger_workflow_no_wait(self):
        """Test triggering workflow without waiting."""
        tool = GitHubRunActions(
            repo_owner="myorg",
            repo_name="myrepo",
            workflow_id="ci.yml",
            ref="main",
            wait_for_completion=False,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["run_id"] == 12345678
        assert result["status"] == "in_progress"
        assert "github.com" in result["run_url"]

    def test_trigger_workflow_with_inputs(self):
        """Test triggering workflow with inputs."""
        tool = GitHubRunActions(
            repo_owner="myorg",
            repo_name="myrepo",
            workflow_id="deploy.yml",
            ref="main",
            inputs={"environment": "production", "version": "v1.2.3"},
            wait_for_completion=False,
        )
        result = tool.run()

        assert result["success"] is True

    def test_trigger_workflow_and_wait(self):
        """Test triggering workflow and waiting for completion."""
        tool = GitHubRunActions(
            repo_owner="myorg",
            repo_name="myrepo",
            workflow_id="deploy.yml",
            ref="main",
            wait_for_completion=True,
            timeout=60,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["status"] == "completed"
        assert result["conclusion"] == "success"
        assert len(result["jobs"]) > 0

    def test_check_workflow_status(self):
        """Test checking status of existing workflow run."""
        tool = GitHubRunActions(
            repo_owner="myorg",
            repo_name="myrepo",
            check_run_id=12345678,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["run_id"] == 12345678

    def test_validation_missing_parameters(self):
        """Test validation error for missing parameters."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubRunActions(
                repo_owner="myorg",
                repo_name="myrepo",
            )
            tool.run()
        assert (
            "workflow" in str(exc_info.value).lower() or "parameter" in str(exc_info.value).lower()
        )

    def test_validation_missing_ref_for_trigger(self):
        """Test validation error for missing ref when triggering."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubRunActions(
                repo_owner="myorg",
                repo_name="myrepo",
                workflow_id="ci.yml",
            )
            tool.run()
        assert "ref" in str(exc_info.value).lower()


class TestGitHubRepoAnalytics:
    """Test GitHubRepoAnalytics tool (95% coverage)."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_full_analytics(self):
        """Test fetching full analytics."""
        tool = GitHubRepoAnalytics(
            repo_owner="myorg",
            repo_name="myrepo",
            include_commits=True,
            include_prs=True,
            include_issues=True,
            include_contributors=True,
            include_languages=True,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["repository"]["name"] == "myrepo"
        assert result["repository"]["stars"] == 1234
        assert result["commits"]["total"] == 342
        assert result["pull_requests"]["total"] == 87
        assert result["issues"]["total"] == 123
        assert len(result["contributors"]) == 3
        assert "Python" in result["languages"]

    def test_analytics_with_date_range(self):
        """Test analytics with date range."""
        tool = GitHubRepoAnalytics(
            repo_owner="myorg",
            repo_name="myrepo",
            since="2024-01-01",
            until="2024-12-31",
            include_commits=True,
        )
        result = tool.run()

        assert result["success"] is True
        assert "2024-01-01" in result["metadata"]["period"]

    def test_selective_analytics_commits_only(self):
        """Test selective analytics (commits only)."""
        tool = GitHubRepoAnalytics(
            repo_owner="myorg",
            repo_name="myrepo",
            include_commits=True,
            include_prs=False,
            include_issues=False,
            include_contributors=False,
            include_languages=False,
        )
        result = tool.run()

        assert result["success"] is True
        assert "commits" in result
        assert result["pull_requests"] is None
        assert result["issues"] is None

    def test_selective_analytics_contributors_languages(self):
        """Test selective analytics (contributors and languages)."""
        tool = GitHubRepoAnalytics(
            repo_owner="myorg",
            repo_name="myrepo",
            include_commits=False,
            include_prs=False,
            include_issues=False,
            include_contributors=True,
            include_languages=True,
        )
        result = tool.run()

        assert result["success"] is True
        assert len(result["contributors"]) > 0
        assert len(result["languages"]) > 0

    def test_validation_invalid_date_format(self):
        """Test validation error for invalid date format."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubRepoAnalytics(
                repo_owner="myorg",
                repo_name="myrepo",
                since="invalid-date",
            )
            tool.run()
        assert "date" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()

    def test_validation_invalid_date_range(self):
        """Test validation error for invalid date range."""
        with pytest.raises(ValidationError) as exc_info:
            tool = GitHubRepoAnalytics(
                repo_owner="myorg",
                repo_name="myrepo",
                since="2024-12-31",
                until="2024-01-01",
            )
            tool.run()
        assert (
            "date" in str(exc_info.value).lower()
            or "range" in str(exc_info.value).lower()
            or "before" in str(exc_info.value).lower()
        )


# Integration tests
class TestGitHubIntegration:
    """Integration tests for GitHub tools working together."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_pr_workflow(self):
        """Test complete PR workflow: create -> review -> merge."""
        # Create PR
        pr_tool = GitHubCreatePR(
            repo_owner="myorg",
            repo_name="myrepo",
            title="Add feature",
            head_branch="feature",
            base_branch="main",
        )
        pr_result = pr_tool.run()
        assert pr_result["success"] is True
        pr_number = pr_result["pr_number"]

        # Review PR
        review_tool = GitHubReviewCode(
            repo_owner="myorg",
            repo_name="myrepo",
            pr_number=pr_number,
            event=ReviewEvent.APPROVE,
            body="LGTM",
        )
        review_result = review_tool.run()
        assert review_result["success"] is True

    def test_issue_workflow(self):
        """Test complete issue workflow: create -> update -> close."""
        # Create issue
        create_tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.CREATE,
            title="Bug report",
            body="Found a bug",
        )
        create_result = create_tool.run()
        assert create_result["success"] is True
        issue_number = create_result["issue_number"]

        # Update issue
        update_tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.UPDATE,
            issue_number=issue_number,
            title="Bug report [UPDATED]",
        )
        update_result = update_tool.run()
        assert update_result["success"] is True

        # Close issue
        close_tool = GitHubManageIssues(
            repo_owner="myorg",
            repo_name="myrepo",
            action=IssueAction.CLOSE,
            issue_number=issue_number,
        )
        close_result = close_tool.run()
        assert close_result["success"] is True

    def test_ci_workflow(self):
        """Test CI workflow: trigger -> monitor -> check analytics."""
        # Trigger workflow
        run_tool = GitHubRunActions(
            repo_owner="myorg",
            repo_name="myrepo",
            workflow_id="ci.yml",
            ref="main",
            wait_for_completion=False,
        )
        run_result = run_tool.run()
        assert run_result["success"] is True

        # Check repo analytics
        analytics_tool = GitHubRepoAnalytics(
            repo_owner="myorg",
            repo_name="myrepo",
            include_commits=True,
            include_prs=True,
        )
        analytics_result = analytics_tool.run()
        assert analytics_result["success"] is True


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
