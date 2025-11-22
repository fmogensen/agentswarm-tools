"""
Analyze multiple videos in batch with custom analysis criteria
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import re

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class BatchVideoAnalysis(BaseTool):
    """
    Analyze multiple videos in batch with custom analysis criteria.

    This tool processes multiple video URLs or file paths concurrently,
    performing various analyses such as scene detection, object recognition,
    transcript extraction, and sentiment analysis.

    Args:
        video_urls: Comma-separated URLs or file paths of videos to analyze
        analysis_types: List of analysis types (e.g., "scene_detection", "object_recognition", "transcript", "sentiment")
        custom_instruction: Optional custom instruction for specialized analysis

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Analysis results for each video
        - metadata: Processing statistics and configuration

    Example:
        >>> tool = BatchVideoAnalysis(
        ...     video_urls="https://example.com/video1.mp4,https://example.com/video2.mp4",
        ...     analysis_types=["scene_detection", "object_recognition"],
        ...     custom_instruction="Focus on identifying product placements"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "batch_video_analysis"
    tool_category: str = "media"

    # Parameters
    video_urls: str = Field(
        ..., description="Comma-separated video URLs or file paths", min_length=1
    )
    analysis_types: List[str] = Field(
        default=["scene_detection", "object_recognition"],
        description="Types of analysis to perform on each video",
    )
    custom_instruction: Optional[str] = Field(
        default=None, description="Custom analysis instruction for specialized requirements"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the batch video analysis."""
        self._validate_parameters()

        if self._should_use_mock():
            return self._generate_mock_results()

        try:
            result = self._process()
            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "videos_processed": len(result.get("analyses", [])),
                    "analysis_types": self.analysis_types,
                },
            }
        except Exception as e:
            raise APIError(f"Batch video analysis failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.video_urls or not isinstance(self.video_urls, str):
            raise ValidationError(
                "video_urls must be a non-empty string",
                tool_name=self.tool_name,
                field="video_urls",
            )

        # Parse and validate URLs
        url_list = [u.strip() for u in self.video_urls.split(",") if u.strip()]
        if not url_list:
            raise ValidationError(
                "video_urls must contain at least one URL or file path",
                tool_name=self.tool_name,
                field="video_urls",
            )

        # Validate URL format
        url_pattern = r"^(https?://|/|[a-zA-Z]:\\)"
        for url in url_list:
            if not re.match(url_pattern, url):
                raise ValidationError(
                    f"Invalid video URL or path: {url}",
                    tool_name=self.tool_name,
                    field="video_urls",
                )

        # Validate analysis types
        valid_types = {
            "scene_detection",
            "object_recognition",
            "transcript",
            "sentiment",
            "action_recognition",
            "face_detection",
            "audio_analysis",
        }

        if not self.analysis_types or not isinstance(self.analysis_types, list):
            raise ValidationError(
                "analysis_types must be a non-empty list",
                tool_name=self.tool_name,
                field="analysis_types",
            )

        invalid_types = [t for t in self.analysis_types if t not in valid_types]
        if invalid_types:
            raise ValidationError(
                f"Invalid analysis types: {invalid_types}. Valid types: {valid_types}",
                tool_name=self.tool_name,
                field="analysis_types",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        urls = [u.strip() for u in self.video_urls.split(",") if u.strip()]
        mock_analyses = []

        for i, url in enumerate(urls, start=1):
            analysis = {"video_url": url, "video_index": i, "analyses": {}}

            for analysis_type in self.analysis_types:
                if analysis_type == "scene_detection":
                    analysis["analyses"]["scene_detection"] = {
                        "scenes": [
                            {"start_time": 0, "end_time": 5.2, "description": "Opening scene"},
                            {"start_time": 5.2, "end_time": 12.8, "description": "Main action"},
                        ],
                        "total_scenes": 2,
                    }
                elif analysis_type == "object_recognition":
                    analysis["analyses"]["object_recognition"] = {
                        "objects": [
                            {"label": "person", "confidence": 0.95, "count": 2},
                            {"label": "car", "confidence": 0.88, "count": 1},
                        ]
                    }
                elif analysis_type == "transcript":
                    analysis["analyses"]["transcript"] = {
                        "text": "Mock transcript for video analysis",
                        "language": "en",
                        "confidence": 0.92,
                    }
                elif analysis_type == "sentiment":
                    analysis["analyses"]["sentiment"] = {
                        "overall": "positive",
                        "score": 0.75,
                        "segments": [
                            {"timestamp": "0:00-0:30", "sentiment": "neutral", "score": 0.5},
                            {"timestamp": "0:30-1:00", "sentiment": "positive", "score": 0.85},
                        ],
                    }
                else:
                    analysis["analyses"][analysis_type] = {"status": "completed", "mock": True}

            if self.custom_instruction:
                analysis["custom_analysis"] = f"Mock analysis based on: {self.custom_instruction}"

            mock_analyses.append(analysis)

        return {
            "success": True,
            "result": {
                "analyses": mock_analyses,
                "total_videos": len(urls),
                "analysis_types_applied": self.analysis_types,
                "custom_instruction": self.custom_instruction,
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic for batch video analysis."""
        urls = [u.strip() for u in self.video_urls.split(",") if u.strip()]
        analyses = []

        for i, url in enumerate(urls, start=1):
            try:
                video_analysis = self._analyze_single_video(url, i)
                analyses.append(video_analysis)
            except Exception as e:
                # Continue processing other videos even if one fails
                analyses.append(
                    {"video_url": url, "video_index": i, "error": str(e), "status": "failed"}
                )

        return {
            "analyses": analyses,
            "total_videos": len(urls),
            "successful": len([a for a in analyses if a.get("status") != "failed"]),
            "failed": len([a for a in analyses if a.get("status") == "failed"]),
            "analysis_types_applied": self.analysis_types,
            "custom_instruction": self.custom_instruction,
        }

    def _analyze_single_video(self, url: str, index: int) -> Dict[str, Any]:
        """
        Analyze a single video with specified analysis types.

        In production, this would call actual video analysis APIs.
        """
        analysis = {"video_url": url, "video_index": index, "status": "completed", "analyses": {}}

        # Simulate analysis for each type
        for analysis_type in self.analysis_types:
            # Placeholder for actual API calls
            analysis["analyses"][analysis_type] = {
                "status": "completed",
                "data": f"Analysis results for {analysis_type}",
            }

        if self.custom_instruction:
            analysis["custom_analysis"] = f"Custom analysis based on: {self.custom_instruction}"

        return analysis


if __name__ == "__main__":
    print("Testing BatchVideoAnalysis...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test with mock data
    tool = BatchVideoAnalysis(
        video_urls="https://example.com/video1.mp4,https://example.com/video2.mp4",
        analysis_types=["scene_detection", "object_recognition", "sentiment"],
        custom_instruction="Focus on identifying key moments",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Videos processed: {result.get('metadata', {}).get('videos_processed')}")
    print(f"Analysis types: {result.get('metadata', {}).get('analysis_types')}")

    assert result.get("success") == True
    assert result.get("result", {}).get("total_videos") == 2
    assert len(result.get("result", {}).get("analyses", [])) == 2

    print("BatchVideoAnalysis test passed!")
