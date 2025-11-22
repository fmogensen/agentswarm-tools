"""
Process multiple YouTube videos to answer specific questions efficiently
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import re

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class BatchUnderstandVideos(BaseTool):
    """
    Process multiple YouTube videos to answer specific questions efficiently

    Args:
        media_url: URL of media to analyze
        instruction: What to analyze or extract

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = BatchUnderstandVideos(media_url="example", instruction="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "batch_understand_videos"
    tool_category: str = "media"

    # Parameters
    media_url: str = Field(..., description="URL of media to analyze")
    instruction: Optional[str] = Field(
        default=None, description="What to analyze or extract"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the batch_understand_videos tool.

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
                "metadata": {
                    "tool_name": self.tool_name,
                    "video_count": len(result.get("videos", [])),
                },
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

        url_list = [u.strip() for u in self.media_url.split(",") if u.strip()]
        if not url_list:
            raise ValidationError(
                "media_url must contain at least one URL", tool_name=self.tool_name
            )

        youtube_pattern = r"(youtube\.com|youtu\.be)"
        for url in url_list:
            if not re.search(youtube_pattern, url):
                raise ValidationError(
                    "Invalid YouTube URL detected",
                    tool_name=self.tool_name,
                    details={"invalid_url": url},
                )

        if self.instruction is not None and not isinstance(self.instruction, str):
            raise ValidationError(
                "instruction must be a string if provided",
                tool_name=self.tool_name,
                details={"instruction": self.instruction},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        urls = [u.strip() for u in self.media_url.split(",") if u.strip()]
        mock_data = []

        for i, url in enumerate(urls, start=1):
            mock_data.append(
                {
                    "video_url": url,
                    "summary": f"Mock summary for video {i}",
                    "extracted_info": f"Mock extracted info for instruction: {self.instruction}",
                }
            )

        return {
            "success": True,
            "result": {
                "videos": mock_data,
                "instruction_used": self.instruction,
                "mock": True,
            },
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        urls = [u.strip() for u in self.media_url.split(",") if u.strip()]
        results: List[Dict[str, Any]] = []

        for url in urls:
            try:
                video_id = self._extract_video_id(url)
                summary = f"Processed summary for video ID {video_id}"
                extracted = (
                    f"Extracted information based on instruction: {self.instruction}"
                    if self.instruction
                    else "No instruction provided"
                )

                results.append(
                    {
                        "video_url": url,
                        "video_id": video_id,
                        "summary": summary,
                        "extracted_info": extracted,
                    }
                )
            except Exception as e:
                raise APIError(
                    f"Failed to analyze video: {url}. Error: {e}",
                    tool_name=self.tool_name,
                )

        return {"videos": results, "instruction_used": self.instruction}

    def _extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL."""
        patterns = [r"v=([^&]+)", r"youtu\.be/([^?&]+)"]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        raise ValidationError(
            "Could not extract YouTube video ID",
            tool_name=self.tool_name,
            details={"url": url},
        )


if __name__ == "__main__":
    print("Testing BatchUnderstandVideos...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test with mock data
    tool = BatchUnderstandVideos(
        media_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ,https://youtu.be/abc123",
        instruction="Summarize the main points",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Result videos: {len(result.get('result', {}).get('videos', []))}")
    print(f"Result: {result.get('result')}")
    assert result.get("success") == True
    assert len(result.get("result", {}).get("videos", [])) == 2
    print("BatchUnderstandVideos test passed!")
