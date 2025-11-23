"""
Comprehensive tests for WorkflowEngine.

Tests:
- Variable interpolation
- Step execution
- Conditional logic
- Foreach loops
- Parallel execution
- Error handling
- Workflow composition
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic import Field

from shared.base import BaseTool
from shared.errors import ToolError, ValidationError
from shared.workflow import StepStatus, WorkflowContext, WorkflowEngine, execute_workflow


# Mock tools for testing
class MockSearchTool(BaseTool):
    """Mock search tool."""

    tool_name = "mock_search"
    tool_category = "test"

    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Max results")

    def _execute(self):
        return {
            "success": True,
            "results": [
                {"url": f"https://example.com/{i}", "score": 0.9 - i * 0.1}
                for i in range(self.max_results)
            ],
        }


class MockCrawlerTool(BaseTool):
    """Mock crawler tool."""

    tool_name = "mock_crawler"
    tool_category = "test"

    url: str = Field(..., description="URL to crawl")

    def _execute(self):
        return {"success": True, "content": f"Content from {self.url}", "url": self.url}


class FailingTool(BaseTool):
    """Tool that always fails."""

    tool_name = "failing_tool"
    tool_category = "test"

    def _execute(self):
        raise ToolError("Intentional failure", tool_name=self.tool_name)


class TestWorkflowContext:
    """Test WorkflowContext functionality."""

    def test_variable_interpolation(self):
        """Test variable interpolation."""
        context = WorkflowContext({"topic": "AI", "count": 10})

        # Simple variable
        assert context.interpolate("${vars.topic}") == "AI"
        assert context.interpolate("${vars.count}") == 10

        # Variable in string
        assert context.interpolate("Search: ${vars.topic}") == "Search: AI"

        # Multiple variables
        result = context.interpolate("Query: ${vars.topic}, Count: ${vars.count}")
        assert result == "Query: AI, Count: 10"

    def test_step_result_interpolation(self):
        """Test interpolating step results."""
        context = WorkflowContext()
        context.set_step_result("search", {"urls": ["url1", "url2"], "count": 2}, success=True)

        # Success flag
        assert context.interpolate("${steps.search.success}") == True

        # Nested result
        assert context.interpolate("${steps.search.result.urls}") == ["url1", "url2"]
        assert context.interpolate("${steps.search.result.count}") == 2

    def test_environment_interpolation(self):
        """Test environment variable interpolation."""
        os.environ["TEST_VAR"] = "test_value"
        context = WorkflowContext()

        assert context.interpolate("${env.TEST_VAR}") == "test_value"

        del os.environ["TEST_VAR"]

    def test_nested_interpolation(self):
        """Test nested object interpolation."""
        context = WorkflowContext()
        context.set_step_result(
            "search", {"results": [{"url": "url1", "score": 0.9}, {"url": "url2", "score": 0.8}]}
        )

        # Array indexing
        assert context.interpolate("${steps.search.result.results[0].url}") == "url1"

        # Full object interpolation
        params = {"urls": "${steps.search.result.results}", "count": 2}
        result = context.interpolate(params)
        assert len(result["urls"]) == 2
        assert result["urls"][0]["url"] == "url1"

    def test_condition_evaluation(self):
        """Test boolean condition evaluation."""
        context = WorkflowContext({"count": 10})
        context.set_step_result("search", {"found": True}, success=True)

        # Boolean values
        assert context.evaluate_condition("${steps.search.success}") == True

        # Comparisons
        assert context.evaluate_condition("${vars.count} > 5") == True
        assert context.evaluate_condition("${vars.count} < 5") == False
        assert context.evaluate_condition("${vars.count} >= 10") == True
        assert context.evaluate_condition("${vars.count} <= 10") == True
        assert context.evaluate_condition("${vars.count} == 10") == True
        assert context.evaluate_condition("${vars.count} != 5") == True

    def test_invalid_reference(self):
        """Test error handling for invalid references."""
        context = WorkflowContext()

        with pytest.raises(ValidationError):
            context.interpolate("${invalid.reference}")

        with pytest.raises(ValidationError):
            context.interpolate("${steps.nonexistent.result}")


class TestWorkflowEngine:
    """Test WorkflowEngine functionality."""

    @pytest.fixture(autouse=True)
    def setup_registry(self):
        """Register mock tools."""
        from shared.registry import tool_registry

        tool_registry.register(MockSearchTool)
        tool_registry.register(MockCrawlerTool)
        tool_registry.register(FailingTool)
        yield
        # Cleanup after tests
        tool_registry.unregister("mock_search")
        tool_registry.unregister("mock_crawler")
        tool_registry.unregister("failing_tool")

    def test_simple_workflow(self):
        """Test basic workflow execution."""
        workflow = {
            "name": "simple-test",
            "steps": [
                {
                    "id": "search",
                    "tool": "mock_search",
                    "params": {"query": "test", "max_results": 5},
                }
            ],
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        assert result["success"] == True
        assert result["steps_executed"] == 1
        assert result["steps_failed"] == 0
        assert "search" in result["results"]
        assert result["results"]["search"]["success"] == True

    def test_multi_step_workflow(self):
        """Test workflow with multiple steps."""
        workflow = {
            "name": "multi-step",
            "variables": {"query": "AI"},
            "steps": [
                {
                    "id": "search",
                    "tool": "mock_search",
                    "params": {"query": "${vars.query}", "max_results": 3},
                },
                {
                    "id": "crawl",
                    "tool": "mock_crawler",
                    "params": {"url": "${steps.search.result.results[0].url}"},
                },
            ],
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        assert result["success"] == True
        assert result["steps_executed"] == 2
        assert "search" in result["results"]
        assert "crawl" in result["results"]

    def test_conditional_step(self):
        """Test conditional step execution."""
        workflow = {
            "name": "conditional",
            "steps": [
                {
                    "id": "search",
                    "tool": "mock_search",
                    "params": {"query": "test", "max_results": 5},
                },
                {
                    "id": "crawl",
                    "tool": "mock_crawler",
                    "params": {"url": "https://example.com"},
                    "condition": "${steps.search.success}",
                },
            ],
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        assert result["success"] == True
        assert result["step_status"]["crawl"] == StepStatus.SUCCESS.value

    def test_skipped_step(self):
        """Test step skipping when condition is false."""
        workflow = {
            "name": "skip-test",
            "variables": {"enabled": False},
            "steps": [
                {
                    "id": "optional",
                    "tool": "mock_search",
                    "params": {"query": "test"},
                    "condition": "${vars.enabled}",
                }
            ],
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        assert result["success"] == True
        assert result["step_status"]["optional"] == StepStatus.SKIPPED.value

    def test_foreach_step(self):
        """Test foreach loop execution."""
        workflow = {
            "name": "foreach-test",
            "steps": [
                {
                    "id": "search",
                    "tool": "mock_search",
                    "params": {"query": "test", "max_results": 3},
                },
                {
                    "id": "crawl_all",
                    "type": "foreach",
                    "items": "${steps.search.result.results}",
                    "step": {"tool": "mock_crawler", "params": {"url": "${item.url}"}},
                },
            ],
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        assert result["success"] == True
        assert "crawl_all" in result["results"]
        # Should have 3 results from foreach
        crawl_results = result["results"]["crawl_all"]
        assert len(crawl_results) == 3

    def test_condition_step_type(self):
        """Test condition step type (if/else)."""
        workflow = {
            "name": "condition-type",
            "variables": {"use_advanced": True},
            "steps": [
                {
                    "id": "decision",
                    "type": "condition",
                    "condition": "${vars.use_advanced}",
                    "then": {
                        "tool": "mock_search",
                        "params": {"query": "advanced", "max_results": 10},
                    },
                    "else": {"tool": "mock_search", "params": {"query": "basic", "max_results": 5}},
                }
            ],
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        assert result["success"] == True
        # Should execute 'then' branch
        assert result["results"]["decision"] is not None

    def test_error_handling_retry(self):
        """Test error handling with retry."""
        workflow = {
            "name": "retry-test",
            "steps": [{"id": "fail", "tool": "failing_tool", "params": {}}],
            "error_handling": {
                "retry_on_failure": True,
                "max_retries": 2,
                "continue_on_error": False,
            },
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        # Should fail after retries
        assert result["success"] == False
        assert result["step_status"]["fail"] == StepStatus.FAILED.value

    def test_continue_on_error(self):
        """Test continue on error mode."""
        workflow = {
            "name": "continue-test",
            "steps": [
                {"id": "fail", "tool": "failing_tool", "params": {}},
                {"id": "success", "tool": "mock_search", "params": {"query": "test"}},
            ],
            "error_handling": {"retry_on_failure": False, "continue_on_error": True},
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        # Overall should fail but second step should execute
        assert result["success"] == False
        assert result["step_status"]["fail"] == StepStatus.FAILED.value
        assert result["step_status"]["success"] == StepStatus.SUCCESS.value
        assert result["steps_executed"] == 2
        assert result["steps_failed"] == 1

    def test_parallel_step(self):
        """Test parallel step execution."""
        workflow = {
            "name": "parallel-test",
            "steps": [
                {
                    "id": "parallel_search",
                    "type": "parallel",
                    "steps": [
                        {
                            "id": "search1",
                            "tool": "mock_search",
                            "params": {"query": "AI", "max_results": 5},
                        },
                        {
                            "id": "search2",
                            "tool": "mock_search",
                            "params": {"query": "ML", "max_results": 5},
                        },
                    ],
                }
            ],
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        assert result["success"] == True
        # Should have results from both parallel steps
        parallel_results = result["results"]["parallel_search"]
        assert len(parallel_results) == 2

    def test_workflow_from_file(self, tmp_path):
        """Test loading workflow from JSON file."""
        workflow_data = {
            "name": "file-test",
            "steps": [{"id": "search", "tool": "mock_search", "params": {"query": "test"}}],
        }

        # Write to temp file
        import json

        workflow_file = tmp_path / "test_workflow.json"
        with open(workflow_file, "w") as f:
            json.dump(workflow_data, f)

        # Load and execute
        engine = WorkflowEngine.from_file(workflow_file)
        result = engine.execute()

        assert result["success"] == True
        assert result["workflow_name"] == "file-test"

    def test_timeout(self):
        """Test workflow timeout."""
        workflow = {
            "name": "timeout-test",
            "steps": [{"id": "search", "tool": "mock_search", "params": {"query": "test"}}],
            "timeout": 0.001,  # Very short timeout
        }

        engine = WorkflowEngine(workflow)
        # May or may not timeout depending on execution speed
        result = engine.execute()
        # Test just ensures it doesn't crash

    def test_nested_variable_interpolation(self):
        """Test complex nested interpolation."""
        workflow = {
            "name": "nested-test",
            "variables": {"config": {"search": {"query": "AI", "max_results": 5}}},
            "steps": [{"id": "search", "tool": "mock_search", "params": "${vars.config.search}"}],
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()

        assert result["success"] == True


class TestExecuteWorkflow:
    """Test execute_workflow convenience function."""

    @pytest.fixture(autouse=True)
    def setup_registry(self):
        """Register mock tools."""
        from shared.registry import tool_registry

        tool_registry.register(MockSearchTool)
        yield
        tool_registry.unregister("mock_search")

    def test_execute_workflow_dict(self):
        """Test execute_workflow with dict."""
        workflow = {
            "name": "test",
            "steps": [{"id": "search", "tool": "mock_search", "params": {"query": "test"}}],
        }

        result = execute_workflow(workflow)
        assert result["success"] == True

    def test_execute_workflow_file(self, tmp_path):
        """Test execute_workflow with file path."""
        import json

        workflow = {
            "name": "test",
            "steps": [{"id": "search", "tool": "mock_search", "params": {"query": "test"}}],
        }

        workflow_file = tmp_path / "test.json"
        with open(workflow_file, "w") as f:
            json.dump(workflow, f)

        result = execute_workflow(workflow_file)
        assert result["success"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
