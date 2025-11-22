"""
Extract transcript from YouTube videos with timestamps
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError

import re

try:
    import requests
except ImportError:
    requests = None


class UnderstandVideo(BaseTool):
    """
    Extract transcript from YouTube videos with timestamps.

    Args:
        media_url: URL of media to analyze
        instruction: What to analyze or extract

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = UnderstandVideo(media_url="https://youtube.com/watch?v=123", instruction="full transcript")
        >>> result = tool.run()
    """

    tool_name: str = "understand_video"
    tool_category: str = "media"
    tool_description: str = "Extract transcript from YouTube videos with timestamps"

    media_url: str = Field(..., description="URL of media to analyze")
    instruction: Optional[str] = Field(
        default=None, description="What to analyze or extract"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the understand_video tool.

        Returns:
            Dict with results
        """
        self._validate_parameters()

        if self._should_use_mock():
            return self._generate_mock_results()

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
        if not self.media_url or not isinstance(self.media_url, str):
            raise ValidationError(
                "media_url must be a non-empty string",
                tool_name=self.tool_name,
                details={"media_url": self.media_url},
            )

        if "youtube.com" not in self.media_url and "youtu.be" not in self.media_url:
            raise ValidationError(
                "media_url must be a valid YouTube link",
                tool_name=self.tool_name,
                details={"media_url": self.media_url},
            )

        if self.instruction is not None and not isinstance(self.instruction, str):
            raise ValidationError(
                "instruction must be a string",
                tool_name=self.tool_name,
                details={"instruction": self.instruction},
            )

    def _should_use_mock(self) -> bool:
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_transcript = [
            {"timestamp": "00:00", "text": "Mock introduction text."},
            {"timestamp": "00:05", "text": "Mock content section begins."},
        ]

        return {
            "success": True,
            "result": {
                "transcript": mock_transcript,
                "instruction": self.instruction,
                "mock": True,
            },
            "metadata": {"mock_mode": True},
        }

    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL."""
        patterns = [r"v=([a-zA-Z0-9_-]{11})", r"youtu\.be/([a-zA-Z0-9_-]{11})"]
        for p in patterns:
            match = re.search(p, url)
            if match:
                return match.group(1)

        raise ValidationError(
            "Unable to extract video ID from URL",
            tool_name=self.tool_name,
            details={"media_url": url},
        )

    def _process(self) -> Any:
        """
        Main processing logic: fetch transcript with timestamps.
        Uses YouTube Transcript API (unofficial). No API key required.

        Raises:
            APIError: If transcript cannot be fetched
        """
        if requests is None:
            raise APIError(
                "requests library is required. Install with: pip install requests",
                tool_name=self.tool_name,
            )

        video_id = self._extract_video_id(self.media_url)

        try:
            # Public transcript API often used in Python tools:
            api_url = f"https://youtubetranscript.com/api/?video_id={video_id}"
            response = requests.get(api_url, timeout=10)

            if response.status_code != 200:
                raise APIError(
                    f"Transcript API returned status {response.status_code}",
                    tool_name=self.tool_name,
                )

            data = response.json()

            transcript_entries = [
                {
                    "timestamp": self._format_timestamp(entry.get("start", 0)),
                    "text": entry.get("text", ""),
                }
                for entry in data
            ]

            return {"transcript": transcript_entries, "instruction": self.instruction}

        except Exception as e:
            raise APIError(f"Failed to fetch transcript: {e}", tool_name=self.tool_name)

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to mm:ss format."""
        s = int(seconds)
        minutes = s // 60
        sec = s % 60
        return f"{minutes:02d}:{sec:02d}"


if __name__ == "__main__":
    print("Testing UnderstandVideo...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test with mock data
    tool = UnderstandVideo(
        media_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        instruction="Summarize the main points",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Transcript entries: {len(result.get('result', {}).get('transcript', []))}")
    print(f"Result: {result.get('result')}")
    assert result.get("success") == True
    assert "transcript" in result.get("result", {})
    print("UnderstandVideo test passed!")
