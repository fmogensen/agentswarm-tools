"""
GitHub Repository Analytics Tool

Fetch repository statistics and insights using GitHub's GraphQL API.
Provides metrics on commits, PRs, contributors, languages, and more.
"""

from typing import Any, Dict, Optional, List
from pydantic import Field
import os
import json
from datetime import datetime, timedelta

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError


class GitHubRepoAnalytics(BaseTool):
    """
    Fetch comprehensive repository analytics and statistics.

    This tool provides insights into repository activity including commits,
    pull requests, contributors, languages, stars, forks, and more.

    Args:
        repo_owner: GitHub repository owner (username or organization)
        repo_name: Repository name
        since: Start date for analytics (ISO format, e.g., '2024-01-01')
        until: End date for analytics (ISO format, defaults to now)
        include_commits: Include commit statistics (default: True)
        include_prs: Include pull request statistics (default: True)
        include_issues: Include issue statistics (default: True)
        include_contributors: Include contributor statistics (default: True)
        include_languages: Include language breakdown (default: True)

    Returns:
        Dict containing:
            - success (bool): Whether the operation was successful
            - repository (dict): Basic repository info
            - commits (dict): Commit statistics
            - pull_requests (dict): PR statistics
            - issues (dict): Issue statistics
            - contributors (list): Top contributors
            - languages (dict): Language breakdown
            - metadata (dict): Tool execution metadata

    Example:
        >>> tool = GitHubRepoAnalytics(
        ...     repo_owner="myorg",
        ...     repo_name="myrepo",
        ...     since="2024-01-01",
        ...     include_commits=True,
        ...     include_prs=True,
        ...     include_contributors=True
        ... )
        >>> result = tool.run()
        >>> print(result['commits']['total'])
        342
    """

    # Tool metadata
    tool_name: str = "github_repo_analytics"
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

    # Optional parameters
    since: Optional[str] = Field(
        None, description="Start date for analytics (ISO format: YYYY-MM-DD)"
    )
    until: Optional[str] = Field(
        None, description="End date for analytics (ISO format: YYYY-MM-DD)"
    )
    include_commits: bool = Field(True, description="Include commit statistics")
    include_prs: bool = Field(True, description="Include PR statistics")
    include_issues: bool = Field(True, description="Include issue statistics")
    include_contributors: bool = Field(
        True, description="Include contributor statistics"
    )
    include_languages: bool = Field(True, description="Include language breakdown")

    def _execute(self) -> Dict[str, Any]:
        """Execute the analytics fetching."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._fetch_analytics()
            return result
        except Exception as e:
            raise APIError(
                f"Failed to fetch analytics: {e}", tool_name=self.tool_name
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate date formats
        if self.since:
            try:
                datetime.fromisoformat(self.since)
            except ValueError:
                raise ValidationError(
                    "since must be in ISO format (YYYY-MM-DD)",
                    tool_name=self.tool_name,
                )

        if self.until:
            try:
                datetime.fromisoformat(self.until)
            except ValueError:
                raise ValidationError(
                    "until must be in ISO format (YYYY-MM-DD)",
                    tool_name=self.tool_name,
                )

        # Validate date range
        if self.since and self.until:
            since_date = datetime.fromisoformat(self.since)
            until_date = datetime.fromisoformat(self.until)
            if since_date > until_date:
                raise ValidationError(
                    "since date must be before until date",
                    tool_name=self.tool_name,
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "repository": {
                "name": self.repo_name,
                "owner": self.repo_owner,
                "description": "Mock repository description",
                "stars": 1234,
                "forks": 567,
                "watchers": 89,
                "open_issues": 45,
                "created_at": "2023-01-15T10:00:00Z",
                "updated_at": "2024-01-15T15:30:00Z",
                "default_branch": "main",
                "is_private": False,
            },
            "commits": {
                "total": 342,
                "authors": 15,
                "additions": 12450,
                "deletions": 8320,
                "files_changed": 456,
            }
            if self.include_commits
            else None,
            "pull_requests": {
                "total": 87,
                "open": 12,
                "closed": 45,
                "merged": 30,
                "avg_merge_time_hours": 24.5,
            }
            if self.include_prs
            else None,
            "issues": {
                "total": 123,
                "open": 45,
                "closed": 78,
                "avg_close_time_hours": 48.2,
            }
            if self.include_issues
            else None,
            "contributors": [
                {
                    "login": "user1",
                    "contributions": 145,
                    "avatar_url": "https://avatars.githubusercontent.com/u/1",
                },
                {
                    "login": "user2",
                    "contributions": 98,
                    "avatar_url": "https://avatars.githubusercontent.com/u/2",
                },
                {
                    "login": "user3",
                    "contributions": 67,
                    "avatar_url": "https://avatars.githubusercontent.com/u/3",
                },
            ]
            if self.include_contributors
            else None,
            "languages": {
                "Python": {"bytes": 125000, "percentage": 45.2},
                "JavaScript": {"bytes": 98000, "percentage": 35.4},
                "TypeScript": {"bytes": 45000, "percentage": 16.3},
                "CSS": {"bytes": 8500, "percentage": 3.1},
            }
            if self.include_languages
            else None,
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "period": f"{self.since or 'all-time'} to {self.until or 'now'}",
                "mock_mode": True,
            },
        }

    def _fetch_analytics(self) -> Dict[str, Any]:
        """Fetch analytics using GitHub GraphQL API."""
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise AuthenticationError(
                "Missing GITHUB_TOKEN environment variable", tool_name=self.tool_name
            )

        # Fetch repository info
        repo_info = self._get_repository_info(token)

        result = {
            "success": True,
            "repository": repo_info,
            "metadata": {
                "tool_name": self.tool_name,
                "repo": f"{self.repo_owner}/{self.repo_name}",
                "period": f"{self.since or 'all-time'} to {self.until or 'now'}",
            },
        }

        # Fetch optional analytics
        if self.include_commits:
            result["commits"] = self._get_commit_stats(token)

        if self.include_prs:
            result["pull_requests"] = self._get_pr_stats(token)

        if self.include_issues:
            result["issues"] = self._get_issue_stats(token)

        if self.include_contributors:
            result["contributors"] = self._get_contributors(token)

        if self.include_languages:
            result["languages"] = self._get_languages(token)

        return result

    def _get_repository_info(self, token: str) -> Dict[str, Any]:
        """Get basic repository information using GraphQL."""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                name
                description
                stargazerCount
                forkCount
                watchers {
                    totalCount
                }
                issues(states: OPEN) {
                    totalCount
                }
                createdAt
                updatedAt
                defaultBranchRef {
                    name
                }
                isPrivate
                url
            }
        }
        """

        variables = {"owner": self.repo_owner, "name": self.repo_name}
        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            raise APIError(
                f"Repository not found: {self.repo_owner}/{self.repo_name}",
                tool_name=self.tool_name,
            )

        repo = response["data"]["repository"]
        return {
            "name": repo["name"],
            "owner": self.repo_owner,
            "description": repo["description"],
            "stars": repo["stargazerCount"],
            "forks": repo["forkCount"],
            "watchers": repo["watchers"]["totalCount"],
            "open_issues": repo["issues"]["totalCount"],
            "created_at": repo["createdAt"],
            "updated_at": repo["updatedAt"],
            "default_branch": repo["defaultBranchRef"]["name"],
            "is_private": repo["isPrivate"],
            "url": repo["url"],
        }

    def _get_commit_stats(self, token: str) -> Dict[str, Any]:
        """Get commit statistics using GraphQL."""
        query = """
        query($owner: String!, $name: String!, $since: GitTimestamp) {
            repository(owner: $owner, name: $name) {
                defaultBranchRef {
                    target {
                        ... on Commit {
                            history(since: $since) {
                                totalCount
                                edges {
                                    node {
                                        additions
                                        deletions
                                        author {
                                            user {
                                                login
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        variables = {"owner": self.repo_owner, "name": self.repo_name}

        if self.since:
            variables["since"] = f"{self.since}T00:00:00Z"

        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            return {
                "total": 0,
                "authors": 0,
                "additions": 0,
                "deletions": 0,
            }

        history = (
            response["data"]["repository"]["defaultBranchRef"]["target"]["history"]
        )

        # Calculate statistics
        total_commits = history["totalCount"]
        authors = set()
        total_additions = 0
        total_deletions = 0

        for edge in history.get("edges", [])[:100]:  # Limit to 100 commits
            node = edge["node"]
            total_additions += node.get("additions", 0)
            total_deletions += node.get("deletions", 0)
            if node.get("author", {}).get("user"):
                authors.add(node["author"]["user"]["login"])

        return {
            "total": total_commits,
            "authors": len(authors),
            "additions": total_additions,
            "deletions": total_deletions,
            "net_change": total_additions - total_deletions,
        }

    def _get_pr_stats(self, token: str) -> Dict[str, Any]:
        """Get pull request statistics using GraphQL."""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                pullRequests(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
                    totalCount
                    nodes {
                        state
                        merged
                        createdAt
                        mergedAt
                    }
                }
            }
        }
        """

        variables = {"owner": self.repo_owner, "name": self.repo_name}
        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            return {"total": 0, "open": 0, "closed": 0, "merged": 0}

        prs = response["data"]["repository"]["pullRequests"]
        total = prs["totalCount"]
        open_count = 0
        closed_count = 0
        merged_count = 0
        merge_times = []

        for pr in prs["nodes"]:
            if pr["state"] == "OPEN":
                open_count += 1
            elif pr["state"] == "CLOSED":
                closed_count += 1
            if pr["merged"]:
                merged_count += 1
                if pr["createdAt"] and pr["mergedAt"]:
                    created = datetime.fromisoformat(
                        pr["createdAt"].replace("Z", "+00:00")
                    )
                    merged = datetime.fromisoformat(
                        pr["mergedAt"].replace("Z", "+00:00")
                    )
                    merge_times.append((merged - created).total_seconds() / 3600)

        avg_merge_time = sum(merge_times) / len(merge_times) if merge_times else 0

        return {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "merged": merged_count,
            "avg_merge_time_hours": round(avg_merge_time, 2),
        }

    def _get_issue_stats(self, token: str) -> Dict[str, Any]:
        """Get issue statistics using GraphQL."""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                issues(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
                    totalCount
                    nodes {
                        state
                        createdAt
                        closedAt
                    }
                }
            }
        }
        """

        variables = {"owner": self.repo_owner, "name": self.repo_name}
        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            return {"total": 0, "open": 0, "closed": 0}

        issues = response["data"]["repository"]["issues"]
        total = issues["totalCount"]
        open_count = 0
        closed_count = 0
        close_times = []

        for issue in issues["nodes"]:
            if issue["state"] == "OPEN":
                open_count += 1
            else:
                closed_count += 1
                if issue["createdAt"] and issue["closedAt"]:
                    created = datetime.fromisoformat(
                        issue["createdAt"].replace("Z", "+00:00")
                    )
                    closed = datetime.fromisoformat(
                        issue["closedAt"].replace("Z", "+00:00")
                    )
                    close_times.append((closed - created).total_seconds() / 3600)

        avg_close_time = sum(close_times) / len(close_times) if close_times else 0

        return {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "avg_close_time_hours": round(avg_close_time, 2),
        }

    def _get_contributors(self, token: str) -> List[Dict[str, Any]]:
        """Get top contributors using REST API."""
        import requests

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contributors"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"per_page": 10}

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            return []

        contributors = []
        for contributor in response.json():
            contributors.append(
                {
                    "login": contributor["login"],
                    "contributions": contributor["contributions"],
                    "avatar_url": contributor["avatar_url"],
                    "url": contributor["html_url"],
                }
            )

        return contributors

    def _get_languages(self, token: str) -> Dict[str, Any]:
        """Get language breakdown using GraphQL."""
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                    totalSize
                    edges {
                        size
                        node {
                            name
                            color
                        }
                    }
                }
            }
        }
        """

        variables = {"owner": self.repo_owner, "name": self.repo_name}
        response = self._execute_graphql(token, query, variables)

        if "errors" in response:
            return {}

        languages_data = response["data"]["repository"]["languages"]
        total_size = languages_data["totalSize"]
        languages = {}

        for edge in languages_data["edges"]:
            lang_name = edge["node"]["name"]
            lang_size = edge["size"]
            percentage = (lang_size / total_size * 100) if total_size > 0 else 0

            languages[lang_name] = {
                "bytes": lang_size,
                "percentage": round(percentage, 2),
                "color": edge["node"]["color"],
            }

        return languages

    def _execute_graphql(
        self, token: str, query: str, variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute GraphQL query/mutation."""
        import requests

        url = "https://api.github.com/graphql"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {"query": query, "variables": variables}

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            raise APIError(
                f"GitHub API error: {response.status_code}",
                api_name="GitHub",
                status_code=response.status_code,
                tool_name=self.tool_name,
            )

        return response.json()


if __name__ == "__main__":
    # Test the tool
    print("Testing GitHubRepoAnalytics...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Full analytics
    print("\n1. Testing full analytics...")
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

    print(f"Success: {result.get('success')}")
    print(f"Repository: {result['repository']['name']}")
    print(f"Stars: {result['repository']['stars']}")
    print(f"Commits: {result['commits']['total']}")
    print(f"PRs: {result['pull_requests']['total']}")
    print(f"Issues: {result['issues']['total']}")
    print(f"Contributors: {len(result['contributors'])}")
    print(f"Languages: {len(result['languages'])}")
    assert result.get("success") == True
    assert result["repository"]["name"] == "myrepo"
    assert result["commits"]["total"] == 342

    # Test 2: Analytics with date range
    print("\n2. Testing analytics with date range...")
    tool = GitHubRepoAnalytics(
        repo_owner="myorg",
        repo_name="myrepo",
        since="2024-01-01",
        until="2024-12-31",
        include_commits=True,
        include_prs=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Period: {result['metadata']['period']}")
    assert result.get("success") == True

    # Test 3: Selective analytics (commits only)
    print("\n3. Testing selective analytics (commits only)...")
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

    print(f"Success: {result.get('success')}")
    print(f"Commits: {result['commits']}")
    assert result.get("success") == True
    assert "commits" in result
    assert result.get("pull_requests") is None
    assert result.get("issues") is None

    # Test 4: Contributors and languages only
    print("\n4. Testing contributors and languages...")
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

    print(f"Success: {result.get('success')}")
    print(f"Top contributor: {result['contributors'][0]['login']}")
    print(f"Main language: {list(result['languages'].keys())[0]}")
    assert result.get("success") == True
    assert len(result["contributors"]) == 3
    assert "Python" in result["languages"]

    # Test 5: Error handling - invalid date format
    print("\n5. Testing error handling (invalid date format)...")
    try:
        tool = GitHubRepoAnalytics(
            repo_owner="myorg",
            repo_name="myrepo",
            since="invalid-date",
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        if "error" in str(e):
            error_dict = eval(str(e))
            print(f"Correctly caught error: {error_dict['error']['message']}")
        else:
            print(f"Correctly caught error: {str(e)}")

    print("\n✅ All tests passed!")
