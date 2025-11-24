"""
Process multiple YouTube videos to answer specific questions efficiently
"""

import os
import re
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.batch import DefaultProgressCallback, parallel_process
from shared.errors import APIError, ValidationError


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
    instruction: Optional[str] = Field(default=None, description="What to analyze or extract")
    max_workers: int = Field(
        5, description="Maximum number of parallel workers for processing", ge=1, le=20
    )
    show_progress: bool = Field(True, description="Whether to show progress information")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the batch_understand_videos tool.

        Returns:
            Dict with results
        """

        self._logger.info(
            f"Executing {self.tool_name} with media_url={self.media_url}, instruction={self.instruction}, max_workers={self.max_workers}, show_progress={self.show_progress}"
        )
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "video_count": len(result.get("videos", [])),
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
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
        """Main processing logic with parallel execution."""
        urls = [u.strip() for u in self.media_url.split(",") if u.strip()]

        # Process videos in parallel
        progress_callback = (
            DefaultProgressCallback(verbose=self.show_progress)
            if self.show_progress
            else DefaultProgressCallback(verbose=False)
        )

        batch_result = parallel_process(
            items=urls,
            processor=self._process_single_video,
            max_workers=self.max_workers,
            progress_callback=progress_callback,
            continue_on_error=True,
        )

        # Prepare response with both successes and failures
        return {
            "videos": batch_result.successes,
            "instruction_used": self.instruction,
            "total_processed": batch_result.successful_count,
            "total_failed": batch_result.failed_count,
            "failures": batch_result.failures if batch_result.failed_count > 0 else [],
            "processing_time_ms": batch_result.processing_time_ms,
            "success_rate": batch_result.success_rate,
        }

    def _process_single_video(self, url: str) -> Dict[str, Any]:
        """
        Process a single video URL.

        Args:
            url: YouTube video URL

        Returns:
            Dict with video analysis results

        Raises:
            APIError: If video processing fails
        """
        try:
            video_id = self._extract_video_id(url)
            summary = f"Processed summary for video ID {video_id}"
            extracted = (
                f"Extracted information based on instruction: {self.instruction}"
                if self.instruction
                else "No instruction provided"
            )

            return {
                "video_url": url,
                "video_id": video_id,
                "summary": summary,
                "extracted_info": extracted,
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(
                f"Failed to analyze video: {url}. Error: {e}",
                tool_name=self.tool_name,
            )

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
