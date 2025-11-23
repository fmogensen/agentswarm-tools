"""
Tests for workflow management functionality
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from cli.workflow import WorkflowManager


class TestWorkflowManager:
    """Test WorkflowManager class."""

    @pytest.fixture
    def temp_workflows_dir(self):
        """Create temporary workflows directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WorkflowManager()
            manager.workflows_dir = Path(tmpdir) / "workflows"
            manager.workflows_dir.mkdir(parents=True, exist_ok=True)
            yield manager

    def test_create_workflow(self, temp_workflows_dir):
        """Test workflow creation."""
        manager = temp_workflows_dir

        workflow = {
            "name": "test-workflow",
            "description": "Test workflow",
            "created_at": datetime.now().isoformat(),
            "steps": [
                {
                    "tool": "web_search",
                    "params": {"query": "test", "max_results": 10}
                }
            ]
        }

        # Save workflow
        workflow_file = manager.save_workflow(workflow)

        assert workflow_file.exists()
        assert workflow_file.name == "test-workflow.json"

    def test_load_workflow(self, temp_workflows_dir):
        """Test workflow loading."""
        manager = temp_workflows_dir

        # Create and save workflow
        workflow = {
            "name": "load-test",
            "description": "Load test workflow",
            "created_at": datetime.now().isoformat(),
            "steps": []
        }
        manager.save_workflow(workflow)

        # Load workflow
        loaded = manager.load_workflow("load-test")

        assert loaded is not None
        assert loaded["name"] == "load-test"
        assert loaded["description"] == "Load test workflow"

    def test_load_nonexistent_workflow(self, temp_workflows_dir):
        """Test loading non-existent workflow."""
        manager = temp_workflows_dir

        loaded = manager.load_workflow("nonexistent")

        assert loaded is None

    def test_list_workflows(self, temp_workflows_dir):
        """Test listing workflows."""
        manager = temp_workflows_dir

        # Create multiple workflows
        for i in range(3):
            workflow = {
                "name": f"workflow-{i}",
                "description": f"Workflow {i}",
                "created_at": datetime.now().isoformat(),
                "steps": []
            }
            manager.save_workflow(workflow)

        # List workflows
        workflows = manager.list_workflows()

        assert len(workflows) == 3
        assert all("name" in w for w in workflows)
        assert all("steps" in w for w in workflows)

    def test_delete_workflow(self, temp_workflows_dir):
        """Test workflow deletion."""
        manager = temp_workflows_dir

        # Create workflow
        workflow = {
            "name": "delete-test",
            "description": "Delete test",
            "created_at": datetime.now().isoformat(),
            "steps": []
        }
        manager.save_workflow(workflow)

        # Verify exists
        assert manager.load_workflow("delete-test") is not None

        # Delete
        result = manager.delete_workflow("delete-test")

        assert result is True
        assert manager.load_workflow("delete-test") is None

    def test_delete_nonexistent_workflow(self, temp_workflows_dir):
        """Test deleting non-existent workflow."""
        manager = temp_workflows_dir

        result = manager.delete_workflow("nonexistent")

        assert result is False

    def test_resolve_parameters(self, temp_workflows_dir):
        """Test parameter resolution with variables."""
        manager = temp_workflows_dir

        params = {
            "query": "${input.search_term}",
            "max_results": 10,
            "url": "${steps[0].result}"
        }

        context = {
            "input": {"search_term": "AI news"},
            "steps": [{"result": "https://example.com"}]
        }

        resolved = manager._resolve_parameters(params, context)

        assert resolved["query"] == "AI news"
        assert resolved["max_results"] == 10
        assert resolved["url"] == "https://example.com"

    def test_evaluate_condition(self, temp_workflows_dir):
        """Test condition evaluation."""
        manager = temp_workflows_dir

        context = {
            "steps": [
                {"success": True},
                {"success": False}
            ]
        }

        # Test successful condition
        result1 = manager._evaluate_condition("${steps[0].success}", context)
        assert result1 is True

        # Test failed condition
        result2 = manager._evaluate_condition("${steps[1].success}", context)
        assert result2 is False


def test_workflow_creation_interactive_mode():
    """Test interactive workflow creation (mocked)."""
    # This would require mocking user input
    # For now, just verify the function exists
    manager = WorkflowManager()
    assert hasattr(manager, "create_workflow")
    assert hasattr(manager, "_create_workflow_interactive")


def test_workflow_structure_validation():
    """Test that workflow structure is valid."""
    workflow = {
        "name": "test",
        "description": "Test workflow",
        "created_at": datetime.now().isoformat(),
        "variables": {
            "query": {
                "type": "string",
                "description": "Search query",
                "required": True
            }
        },
        "steps": [
            {
                "tool": "web_search",
                "params": {"query": "${input.query}"}
            }
        ]
    }

    # Verify structure
    assert "name" in workflow
    assert "steps" in workflow
    assert "variables" in workflow
    assert isinstance(workflow["steps"], list)
    assert len(workflow["steps"]) > 0
    assert "tool" in workflow["steps"][0]
    assert "params" in workflow["steps"][0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
