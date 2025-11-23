"""
Search for videos on YouTube platform and return comprehensive results
"""

import os
from typing import Any, Dict, List

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class VideoSearch(BaseTool):
    """
    Search for videos on YouTube platform

    Best for:
    - Tutorials and how-to guides
    - Educational content
    - Product reviews
    - Visual demonstrations

    Args:
        query: Video search query
        max_results: Maximum number of results to return (default: 10)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: List of video results with video_id, title, channel, views,
                 duration, upload_date, thumbnails, description
        - metadata: Additional information

    Example:
        >>> tool = VideoSearch(query="Python tutorial", max_results=5)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "video_search"
    tool_category: str = "data"

    # Parameters
    query: str = Field(..., description="Video search query", min_length=1)
    max_results: int = Field(10, description="Maximum number of results to return", ge=1, le=50)

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the video_search tool.

        Returns:
            Dict with results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.query.strip():
            raise ValidationError("Query cannot be empty", tool_name=self.tool_name)

        if self.max_results < 1 or self.max_results > 50:
            raise ValidationError("max_results must be between 1 and 50", tool_name=self.tool_name)

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_results = [
            {
                "video_id": f"mock_video_id_{i}",
                "title": f"Mock Video Title {i}: {self.query}",
                "channel": f"Mock Channel {i}",
                "views": 1000 * i,
                "duration": f"{i}:30",
                "upload_date": "2024-01-15",
                "thumbnails": {
                    "default": f"https://example.com/thumbnail_{i}_default.jpg",
                    "medium": f"https://example.com/thumbnail_{i}_medium.jpg",
                    "high": f"https://example.com/thumbnail_{i}_high.jpg",
                },
                "description": f"This is a mock description for video {i} about {self.query}.",
            }
            for i in range(1, min(self.max_results + 1, 11))
        ]

        return {
            "success": True,
            "result": mock_results,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "query": self.query,
                "max_results": self.max_results,
            },
        }

    def _process(self) -> List[Dict[str, Any]]:
        """Main processing logic."""
        try:
            # Get API key from environment
            api_key = os.getenv("YOUTUBE_API_KEY")
            if not api_key:
                raise ValidationError(
                    "YOUTUBE_API_KEY environment variable not set", tool_name=self.tool_name
                )

            # YouTube Data API v3 endpoint
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": self.query,
                    "maxResults": self.max_results,
                    "type": "video",
                    "key": api_key,
                },
                timeout=30,
            )
            response.raise_for_status()
            search_data = response.json()

            if "items" not in search_data:
                return []

            video_ids = [item["id"]["videoId"] for item in search_data["items"]]

            # Get additional video details (statistics, content details)
            video_details = self._get_video_details(video_ids, api_key)

            # Combine search results with video details
            results = []
            for item in search_data["items"]:
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                details = video_details.get(video_id, {})

                result = {
                    "video_id": video_id,
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "views": details.get("viewCount", 0),
                    "duration": details.get("duration", ""),
                    "upload_date": (
                        snippet.get("publishedAt", "").split("T")[0]
                        if snippet.get("publishedAt")
                        else ""
                    ),
                    "thumbnails": {
                        "default": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                        "medium": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                        "high": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    },
                    "description": snippet.get("description", ""),
                }
                results.append(result)

            return results

        except requests.RequestException as e:
            raise APIError(f"API request failed: {e}", tool_name=self.tool_name)

    def _get_video_details(self, video_ids: List[str], api_key: str) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed information for videos (views, duration, etc.)

        Args:
            video_ids: List of video IDs
            api_key: YouTube API key

        Returns:
            Dict mapping video_id to details
        """
        if not video_ids:
            return {}

        try:
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    "part": "statistics,contentDetails",
                    "id": ",".join(video_ids),
                    "key": api_key,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            details = {}
            for item in data.get("items", []):
                video_id = item.get("id")
                statistics = item.get("statistics", {})
                content_details = item.get("contentDetails", {})

                details[video_id] = {
                    "viewCount": int(statistics.get("viewCount", 0)),
                    "likeCount": int(statistics.get("likeCount", 0)),
                    "commentCount": int(statistics.get("commentCount", 0)),
                    "duration": self._parse_duration(content_details.get("duration", "")),
                }

            return details

        except Exception as e:
            # Log error but don't fail the whole request
            print(f"Warning: Failed to get video details: {e}")
            return {}

    def _parse_duration(self, duration: str) -> str:
        """
        Parse ISO 8601 duration to readable format (e.g., PT1H2M10S -> 1:02:10)

        Args:
            duration: ISO 8601 duration string

        Returns:
            Formatted duration string
        """
        if not duration or not duration.startswith("PT"):
            return "0:00"

        duration = duration[2:]  # Remove 'PT'
        hours = 0
        minutes = 0
        seconds = 0

        if "H" in duration:
            hours, duration = duration.split("H")
            hours = int(hours)

        if "M" in duration:
            minutes, duration = duration.split("M")
            minutes = int(minutes)

        if "S" in duration:
            seconds = int(duration.replace("S", ""))

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"


if __name__ == "__main__":
    # Test the video_search tool
    print("Testing VideoSearch tool...")

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    tool = VideoSearch(query="Python programming tutorial", max_results=5)
    result = tool.run()

    print(f"\nSuccess: {result.get('success')}")
    print(f"Results: {len(result.get('result', []))} items")

    if result.get("result"):
        first_result = result["result"][0]
        print(f"\nFirst result:")
        print(f"  Video ID: {first_result.get('video_id')}")
        print(f"  Title: {first_result.get('title')}")
        print(f"  Channel: {first_result.get('channel')}")
        print(f"  Views: {first_result.get('views')}")
        print(f"  Duration: {first_result.get('duration')}")
        print(f"  Upload Date: {first_result.get('upload_date')}")
        print(f"  Description: {first_result.get('description')[:100]}...")
