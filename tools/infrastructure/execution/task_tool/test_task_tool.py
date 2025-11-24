"""
Comprehensive test suite for TaskTool.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from tools.infrastructure.execution.task_tool.task_tool import TaskTool
from shared.errors import ValidationError, APIError


class TestTaskToolValidation:
    """Test parameter validation."""

    def test_prompt_too_short(self):
        """Test that prompt shorter than 50 characters raises ValidationError."""
        os.environ["USE_MOCK_APIS"] = "true"

        with pytest.raises((ValidationError, Exception)) as exc_info:
            tool = TaskTool(
                prompt="Short prompt", description="Test task", subagent_type="general-purpose"
            )
            tool.run()

        error_msg = str(exc_info.value)
        assert (
            "at least 50 characters" in error_msg
            or "at least 50 characters" in error_msg.lower()
            or "String should have at least 50 characters" in error_msg
        )

    def test_prompt_empty(self):
        """Test that empty prompt raises ValidationError."""
        os.environ["USE_MOCK_APIS"] = "true"

        with pytest.raises(Exception) as exc_info:
            tool = TaskTool(prompt="", description="Test task", subagent_type="general-purpose")
            tool.run()

        error_msg = str(exc_info.value)
        assert (
            "cannot be empty" in error_msg.lower()
            or "at least 50 characters" in error_msg.lower()
            or "string_too_short" in error_msg.lower()
        )

    def test_prompt_whitespace_only(self):
        """Test that whitespace-only prompt raises ValidationError."""
        os.environ["USE_MOCK_APIS"] = "true"

        with pytest.raises(Exception) as exc_info:
            tool = TaskTool(
                prompt="   \n\t   ", description="Test task", subagent_type="general-purpose"
            )
            tool.run()

        error_msg = str(exc_info.value)
        assert (
            "cannot be empty" in error_msg.lower()
            or "at least 50 characters" in error_msg.lower()
            or "string_too_short" in error_msg.lower()
        )

    def test_description_too_long(self):
        """Test that description longer than 50 characters raises ValidationError."""
        os.environ["USE_MOCK_APIS"] = "true"

        with pytest.raises(Exception) as exc_info:
            tool = TaskTool(
                prompt="This is a detailed task prompt for testing purposes that is long enough to pass validation requirements.",
                description="This is a very long description that exceeds the maximum allowed length of fifty characters",
                subagent_type="general-purpose",
            )
            tool.run()

        error_msg = str(exc_info.value)
        assert "50 characters" in error_msg.lower() or "string_too_long" in error_msg.lower()

    def test_description_empty(self):
        """Test that empty description raises ValidationError."""
        os.environ["USE_MOCK_APIS"] = "true"

        with pytest.raises(Exception) as exc_info:
            tool = TaskTool(
                prompt="This is a detailed task prompt for testing purposes that is long enough to pass validation requirements.",
                description="",
                subagent_type="general-purpose",
            )
            tool.run()

        error_msg = str(exc_info.value)
        assert (
            "cannot be empty" in error_msg.lower()
            or "at least 1 character" in error_msg.lower()
            or "string_too_short" in error_msg.lower()
        )

    def test_invalid_subagent_type(self):
        """Test that invalid subagent_type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = TaskTool(
                prompt="This is a detailed task prompt for testing purposes that is long enough to pass validation requirements.",
                description="Test task",
                subagent_type="invalid-agent-type",
            )
            tool.run()

        assert "Invalid subagent_type" in str(exc_info.value)
        assert "invalid-agent-type" in str(exc_info.value)
        assert exc_info.value.error_code == "VALIDATION_ERROR"

    def test_valid_parameters(self):
        """Test that valid parameters pass validation."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = TaskTool(
            prompt="This is a detailed task prompt for testing purposes that is long enough to pass validation requirements.",
            description="Valid test task",
            subagent_type="general-purpose",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("status") == "completed"


class TestTaskToolSubagentTypes:
    """Test different subagent types."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_general_purpose_agent(self):
        """Test general-purpose subagent execution."""
        tool = TaskTool(
            prompt="Execute a comprehensive analysis of the system architecture. "
            "Identify bottlenecks, security issues, and optimization opportunities. "
            "Provide detailed recommendations for improvements.",
            description="System analysis",
            subagent_type="general-purpose",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("subagent_type") == "general-purpose"
        assert result.get("result", {}).get("status") == "completed"
        assert "completion_report" in result.get("result", {})

    def test_code_reviewer_agent(self):
        """Test code-reviewer subagent execution."""
        tool = TaskTool(
            prompt="Review the authentication module for security vulnerabilities. "
            "Check for SQL injection, XSS, CSRF issues, and insecure session management. "
            "Analyze password hashing and provide recommendations.",
            description="Security code review",
            subagent_type="code-reviewer",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("subagent_type") == "code-reviewer"
        assert result.get("result", {}).get("status") == "completed"
        assert "actions_taken" in result.get("result", {})

    def test_test_runner_agent(self):
        """Test test-runner subagent execution."""
        tool = TaskTool(
            prompt="Execute the complete test suite for the payment processing module. "
            "Run unit tests, integration tests, and end-to-end tests. "
            "Collect coverage metrics and identify any failing tests.",
            description="Run test suite",
            subagent_type="test-runner",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("subagent_type") == "test-runner"
        assert result.get("result", {}).get("status") == "completed"

    def test_doc_writer_agent(self):
        """Test doc-writer subagent execution."""
        tool = TaskTool(
            prompt="Create comprehensive documentation for the REST API endpoints. "
            "Include detailed descriptions, parameter specifications, request/response examples. "
            "Add authentication requirements and rate limiting information.",
            description="API documentation",
            subagent_type="doc-writer",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("subagent_type") == "doc-writer"
        assert result.get("result", {}).get("status") == "completed"


class TestTaskToolExecution:
    """Test task execution functionality."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_task_id_generation(self):
        """Test that each task gets a unique ID."""
        tool1 = TaskTool(
            prompt="First task with detailed instructions for the agent to execute properly and meet requirements.",
            description="First task",
            subagent_type="general-purpose",
        )
        result1 = tool1.run()

        tool2 = TaskTool(
            prompt="Second task with different instructions for the agent to execute properly and meet requirements.",
            description="Second task",
            subagent_type="general-purpose",
        )
        result2 = tool2.run()

        task_id1 = result1.get("result", {}).get("task_id")
        task_id2 = result2.get("result", {}).get("task_id")

        assert task_id1 != task_id2
        # In mock mode, task IDs start with 'mock_task_', in normal mode they start with 'task_'
        assert "task_" in task_id1
        assert "task_" in task_id2

    def test_execution_time_tracking(self):
        """Test that execution time is tracked and returned."""
        tool = TaskTool(
            prompt="Execute a task that requires detailed analysis and comprehensive reporting of all findings.",
            description="Timed task",
            subagent_type="general-purpose",
        )
        result = tool.run()

        assert "execution_time_ms" in result.get("result", {})
        assert result.get("result", {}).get("execution_time_ms") > 0

    def test_actions_extraction(self):
        """Test that actions are extracted from prompt."""
        tool = TaskTool(
            prompt="Analyze the database schema for optimization opportunities. "
            "Identify slow queries and missing indexes. "
            "Review the data normalization and suggest improvements.",
            description="Database analysis",
            subagent_type="general-purpose",
        )
        result = tool.run()

        actions = result.get("result", {}).get("actions_taken", [])
        assert len(actions) > 0
        assert isinstance(actions, list)

    def test_completion_report_structure(self):
        """Test that completion report has proper structure."""
        tool = TaskTool(
            prompt="Perform comprehensive security audit of the web application including authentication checks.",
            description="Security audit",
            subagent_type="code-reviewer",
        )
        result = tool.run()

        report = result.get("result", {}).get("completion_report")
        assert isinstance(report, str)
        assert len(report) > 0
        assert "Task Overview" in report or "completed" in report

    def test_metadata_returned(self):
        """Test that proper metadata is returned."""
        tool = TaskTool(
            prompt="Create detailed technical documentation for the microservices architecture implementation.",
            description="Documentation",
            subagent_type="doc-writer",
        )
        result = tool.run()

        assert "metadata" in result
        metadata = result.get("metadata", {})
        assert metadata.get("tool_name") == "task_tool"
        assert metadata.get("subagent_type") == "doc-writer"
        assert "task_description" in metadata


class TestTaskToolComplexScenarios:
    """Test complex task scenarios."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_multi_step_task(self):
        """Test task with multiple steps in prompt."""
        tool = TaskTool(
            prompt="Step 1: Analyze the codebase structure and identify modules. "
            "Step 2: Review each module for code quality issues. "
            "Step 3: Check test coverage for all modules. "
            "Step 4: Generate a comprehensive report with recommendations.",
            description="Multi-step analysis",
            subagent_type="code-reviewer",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("status") == "completed"

    def test_code_generation_task(self):
        """Test task that involves code generation."""
        tool = TaskTool(
            prompt="Generate unit tests for the UserController class. "
            "Include tests for all CRUD operations: create, read, update, delete. "
            "Add edge case tests for validation errors and authentication failures. "
            "Ensure test coverage exceeds 90 percent.",
            description="Generate unit tests",
            subagent_type="test-runner",
        )
        result = tool.run()

        assert result.get("success") == True
        assert "test" in result.get("result", {}).get("task_description", "").lower()

    def test_file_operations_task(self):
        """Test task involving file operations."""
        tool = TaskTool(
            prompt="Read all markdown files in the docs directory. "
            "Check for broken links and outdated information. "
            "Update the table of contents and ensure consistent formatting. "
            "Generate a summary report of changes made.",
            description="Update documentation",
            subagent_type="doc-writer",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("subagent_type") == "doc-writer"

    def test_unicode_in_prompt(self):
        """Test that unicode characters in prompt are handled correctly."""
        tool = TaskTool(
            prompt="Analyze the internationalization support: Check UTF-8 encoding, "
            "test with special characters like é, ñ, ü, 中文, 日本語, العربية. "
            "Ensure all text rendering works correctly across different locales.",
            description="i18n testing",
            subagent_type="test-runner",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("status") == "completed"

    def test_special_characters_in_description(self):
        """Test special characters in description."""
        tool = TaskTool(
            prompt="Perform comprehensive analysis of the system with detailed examination of all components.",
            description="Test (special) chars: @#$%",
            subagent_type="general-purpose",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("task_description") == "Test (special) chars: @#$%"

    def test_long_detailed_prompt(self):
        """Test with a very detailed, long prompt."""
        long_prompt = """
        Perform a comprehensive security audit of the entire application stack:

        1. Frontend Security:
           - Check for XSS vulnerabilities in all input fields
           - Verify CSRF token implementation
           - Audit third-party library versions for known vulnerabilities

        2. Backend Security:
           - Review authentication and authorization logic
           - Check for SQL injection vulnerabilities
           - Verify password hashing algorithms meet current standards
           - Audit API endpoint security and rate limiting

        3. Infrastructure Security:
           - Review server configurations
           - Check SSL/TLS certificate validity
           - Audit firewall rules and network segmentation
           - Verify backup and disaster recovery procedures

        4. Generate comprehensive report with:
           - Executive summary
           - Detailed findings for each category
           - Risk assessment and prioritization
           - Remediation recommendations with timeline
        """

        tool = TaskTool(
            prompt=long_prompt, description="Full security audit", subagent_type="code-reviewer"
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("status") == "completed"
        assert len(result.get("result", {}).get("actions_taken", [])) > 0


class TestTaskToolMockMode:
    """Test mock mode functionality."""

    def test_mock_mode_enabled(self):
        """Test that mock mode returns mock results."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = TaskTool(
            prompt="This is a test prompt that should trigger mock mode execution with proper formatting.",
            description="Mock mode test",
            subagent_type="general-purpose",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result.get("result", {}).get("mock") == True
        assert "mock_task_" in result.get("result", {}).get("task_id", "")

    def test_mock_mode_disabled(self):
        """Test normal execution when mock mode is disabled."""
        os.environ["USE_MOCK_APIS"] = "false"

        tool = TaskTool(
            prompt="This is a test prompt for normal execution mode without mocking enabled for testing.",
            description="Normal mode test",
            subagent_type="general-purpose",
        )
        result = tool.run()

        assert result.get("success") == True
        # In normal mode, mock field should not be present or be False
        assert result.get("result", {}).get("mock") != True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
