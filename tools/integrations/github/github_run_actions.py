"""
GitHub Run Actions Tool

Trigger GitHub Actions workflows and check their status using GitHub API.
Supports manual workflow dispatch, status monitoring, and artifact downloads.
"""

from typing import Any, Dict, Optional, List
from pydantic import Field
import os
import json
import time

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError, TimeoutError


class GitHubRunActions(BaseTool):
    """
    Trigger and monitor GitHub Actions workflows.

    This tool triggers workflow runs via manual dispatch and monitors their
    execution status, including job details and artifact information.

    Args:
        repo_owner: GitHub repository owner (username or organization)
        repo_name: Repository name
        workflow_id: Workflow filename (e.g., 'ci.yml') or ID
        ref: Git reference (branch, tag, or commit SHA) to run workflow on
        inputs: Workflow input parameters (key-value pairs)
        wait_for_completion: Wait for workflow to complete (default: False)
        timeout: Maximum seconds to wait for completion (default: 300)
        check_run_id: Check status of specific workflow run ID

    Returns:
        Dict containing:
            - success (bool): Whether the operation was successful
            - run_id (int): Workflow run ID
            - run_url (str): URL to the workflow run
            - status (str): Workflow status (queued, in_progress, completed)
            - conclusion (str): Workflow conclusion (success, failure, cancelled, etc.)
            - jobs (list): Job details if completed
            - artifacts (list): Artifact information if available
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Trigger workflow
        >>> tool = GitHubRunActions(
        ...     repo_owner="myorg",
        ...     repo_name="myrepo",
        ...     workflow_id="deploy.yml",
        ...     ref="main",
        ...     inputs={"environment": "production", "version": "v1.2.3"},
        ...     wait_for_completion=True
        ... )
        >>> result = tool.run()
        >>> print(result['conclusion'])
        'success'
    """

    # Tool metadata
    tool_name: str = "github_run_actions"
    tool_category: str = "integrations"

    # Required parameters
    repo_owner: str = Field(
        ...,
        description="Repository owner (username or organization)",
        min_length=1,
        max_length=100,
    )
    repo_name: str = Field(
        ..., description="Repository name", min_length=1, max_length=100
    )

    # Conditional parameters
    workflow_id: Optional[str] = Field(
        None, description="Workflow filename or ID (required for trigger)"
    )
    ref: Optional[str] = Field(
        None, description="Git reference (branch/tag/commit) for workflow"
    )
    inputs: Optional[Dict[str, str]] = Field(
        None, description="Workflow input parameters"
    )
    wait_for_completion: bool = Field(
        False, description="Wait for workflow to complete"
    )
    timeout: int = Field(
        300, description="Maximum seconds to wait for completion", ge=10, le=3600
    )
    check_run_id: Optional[int] = Field(
        None, description="Check status of specific workflow run ID"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the workflow operation."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            if self.check_run_id:
                # Check status of existing run
                return self._check_workflow_status()
            else:
                # Trigger new workflow
                return self._trigger_workflow()
        except Exception as e:
            raise APIError(
                f"Failed to run workflow: {e}", tool_name=self.tool_name
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Either workflow_id or check_run_id must be provided
        if not self.workflow_id and not self.check_run_id:
            raise ValidationError(
                "Either workflow_id or check_run_id must be provided",
                tool_name=self.tool_name,
            )

        # For triggering workflow, ref is required
        if self.workflow_id and not self.check_run_id:
            if not self.ref:
                raise ValidationError(
                    "ref is required when triggering workflow",
                    tool_name=self.tool_name,
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        run_id = self.check_run_id or 12345678
        status = "completed" if self.wait_for_completion else "in_progress"
        conclusion = "success" if self.wait_for_completion else None

        return {
            "success": True,
            "run_id": run_id,
            "run_url": f"https://github.com/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}",
            "status": status,
            "conclusion": conclusion,
            "jobs": [
                {
                    "id": 11111,
                    "name": "build",
                    "status": "completed",
                    "conclusion": "success",
                    "started_at": "2024-01-15T10:00:00Z",
                    "completed_at": "2024-01-15T10:05:00Z",
                }
            ]
            if self.wait_for_completion
            else [],
            "artifacts": [
                {
                    "id": 22222,
                    "name": "build-output",
                    "size_in_bytes": 1024000,
                }
            ]
            if self.wait_for_completion
            else [],
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "workflow": self.workflow_id or "check",
                "mock_mode": True,
            },
        }

    def _trigger_workflow(self) -> Dict[str, Any]:
        """Trigger a workflow using REST API."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise AuthenticationError(
                "Missing GITHUB_TOKEN environment variable", tool_name=self.tool_name
            )

        import requests

        # Trigger workflow dispatch
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{self.workflow_id}/dispatches"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        payload = {"ref": self.ref}

        if self.inputs:
            payload["inputs"] = self.inputs

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 204:
            raise APIError(
                f"Failed to trigger workflow: {response.status_code}",
                api_name="GitHub",
                status_code=response.status_code,
                tool_name=self.tool_name,
            )

        # Get the run ID of the triggered workflow
        run_id = self._get_latest_run_id(token)

        if self.wait_for_completion:
            return self._wait_for_workflow_completion(token, run_id)
        else:
            # Return immediate status
            run_data = self._get_workflow_run(token, run_id)
            return {
                "success": True,
                "run_id": run_data["id"],
                "run_url": run_data["html_url"],
                "status": run_data["status"],
                "conclusion": run_data["conclusion"],
                "jobs": [],
                "artifacts": [],
                "metadata": {
                    "tool_name": self.tool_name,
                    "repo": f"{self.repo_owner}/{self.repo_name}",
                    "workflow": self.workflow_id,
                    "ref": self.ref,
                },
            }

    def _check_workflow_status(self) -> Dict[str, Any]:
        """Check status of an existing workflow run."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise AuthenticationError(
                "Missing GITHUB_TOKEN environment variable", tool_name=self.tool_name
            )

        run_data = self._get_workflow_run(token, self.check_run_id)

        # Get jobs and artifacts if completed
        jobs = []
        artifacts = []

        if run_data["status"] == "completed":
            jobs = self._get_workflow_jobs(token, self.check_run_id)
            artifacts = self._get_workflow_artifacts(token, self.check_run_id)

        return {
            "success": True,
            "run_id": run_data["id"],
            "run_url": run_data["html_url"],
            "status": run_data["status"],
            "conclusion": run_data["conclusion"],
            "jobs": jobs,
            "artifacts": artifacts,
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "run_id": self.check_run_id,
            },
        }

    def _wait_for_workflow_completion(
        self, token: str, run_id: int
    ) -> Dict[str, Any]:
        """Wait for workflow to complete with timeout."""
        start_time = time.time()
        poll_interval = 5  # seconds

        while True:
            # Check if timeout exceeded
            if time.time() - start_time > self.timeout:
                raise TimeoutError(
                    f"Workflow did not complete within {self.timeout} seconds",
                    timeout=self.timeout,
                    tool_name=self.tool_name,
                )

            # Get current status
            run_data = self._get_workflow_run(token, run_id)

            if run_data["status"] == "completed":
                # Workflow completed, get jobs and artifacts
                jobs = self._get_workflow_jobs(token, run_id)
                artifacts = self._get_workflow_artifacts(token, run_id)

                return {
                    "success": True,
                    "run_id": run_data["id"],
                    "run_url": run_data["html_url"],
                    "status": run_data["status"],
                    "conclusion": run_data["conclusion"],
                    "jobs": jobs,
                    "artifacts": artifacts,
                    "metadata": {
                        "tool_name": self.tool_name,
                        "repo": f"{self.repo_owner}/{self.repo_name}",
                        "workflow": self.workflow_id,
                        "wait_time_seconds": int(time.time() - start_time),
                    },
                }

            # Wait before next poll
            time.sleep(poll_interval)

    def _get_latest_run_id(self, token: str) -> int:
        """Get the most recent workflow run ID."""
        import requests

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/{self.workflow_id}/runs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"per_page": 1, "branch": self.ref}

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            raise APIError(
                f"Failed to get workflow runs: {response.status_code}",
                api_name="GitHub",
                status_code=response.status_code,
                tool_name=self.tool_name,
            )

        data = response.json()
        if not data.get("workflow_runs"):
            raise APIError(
                "No workflow runs found", tool_name=self.tool_name
            )

        return data["workflow_runs"][0]["id"]

    def _get_workflow_run(self, token: str, run_id: int) -> Dict[str, Any]:
        """Get workflow run details."""
        import requests

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            raise APIError(
                f"Failed to get workflow run: {response.status_code}",
                api_name="GitHub",
                status_code=response.status_code,
                tool_name=self.tool_name,
            )

        return response.json()

    def _get_workflow_jobs(self, token: str, run_id: int) -> List[Dict[str, Any]]:
        """Get jobs for a workflow run."""
        import requests

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}/jobs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            return []

        data = response.json()
        jobs = []

        for job in data.get("jobs", []):
            jobs.append(
                {
                    "id": job["id"],
                    "name": job["name"],
                    "status": job["status"],
                    "conclusion": job["conclusion"],
                    "started_at": job.get("started_at"),
                    "completed_at": job.get("completed_at"),
                    "steps": len(job.get("steps", [])),
                }
            )

        return jobs

    def _get_workflow_artifacts(
        self, token: str, run_id: int
    ) -> List[Dict[str, Any]]:
        """Get artifacts for a workflow run."""
        import requests

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs/{run_id}/artifacts"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            return []

        data = response.json()
        artifacts = []

        for artifact in data.get("artifacts", []):
            artifacts.append(
                {
                    "id": artifact["id"],
                    "name": artifact["name"],
                    "size_in_bytes": artifact["size_in_bytes"],
                    "created_at": artifact["created_at"],
                    "expires_at": artifact.get("expires_at"),
                }
            )

        return artifacts


if __name__ == "__main__":
    # Test the tool
    print("Testing GitHubRunActions...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Trigger workflow without waiting
    print("\n1. Testing trigger workflow (no wait)...")
    tool = GitHubRunActions(
        repo_owner="myorg",
        repo_name="myrepo",
        workflow_id="ci.yml",
        ref="main",
        wait_for_completion=False,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Run ID: {result.get('run_id')}")
    print(f"Run URL: {result.get('run_url')}")
    print(f"Status: {result.get('status')}")
    assert result.get("success") == True
    assert result.get("run_id") == 12345678
    assert result.get("status") == "in_progress"

    # Test 2: Trigger workflow with inputs and wait
    print("\n2. Testing trigger workflow with inputs (wait for completion)...")
    tool = GitHubRunActions(
        repo_owner="myorg",
        repo_name="myrepo",
        workflow_id="deploy.yml",
        ref="main",
        inputs={"environment": "production", "version": "v1.2.3"},
        wait_for_completion=True,
        timeout=60,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    print(f"Conclusion: {result.get('conclusion')}")
    print(f"Jobs: {len(result.get('jobs', []))}")
    print(f"Artifacts: {len(result.get('artifacts', []))}")
    assert result.get("success") == True
    assert result.get("status") == "completed"
    assert result.get("conclusion") == "success"
    assert len(result.get("jobs", [])) > 0

    # Test 3: Check status of existing run
    print("\n3. Testing check workflow status...")
    tool = GitHubRunActions(
        repo_owner="myorg",
        repo_name="myrepo",
        check_run_id=12345678,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Run ID: {result.get('run_id')}")
    print(f"Status: {result.get('status')}")
    assert result.get("success") == True
    assert result.get("run_id") == 12345678

    # Test 4: Error handling - missing parameters
    print("\n4. Testing error handling (missing workflow_id and check_run_id)...")
    try:
        tool = GitHubRunActions(
            repo_owner="myorg",
            repo_name="myrepo",
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if "error" in str(e):
            error_dict = eval(str(e))
            print(f"Correctly caught error: {error_dict['error']['message']}")
        else:
            print(f"Correctly caught error: {str(e)}")

    # Test 5: Workflow with specific branch
    print("\n5. Testing workflow on feature branch...")
    tool = GitHubRunActions(
        repo_owner="myorg",
        repo_name="myrepo",
        workflow_id="test.yml",
        ref="feature/new-feature",
        inputs={"test_suite": "integration"},
        wait_for_completion=False,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Run URL: {result.get('run_url')}")
    assert result.get("success") == True

    print("\n✅ All tests passed!")
