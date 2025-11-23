"""
Unit tests for VideoClipperTool
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from tools.media_processing.video_clipper.video_clipper import VideoClipperTool


class TestVideoClipperTool:
    """Test suite for VideoClipperTool"""

    def setup_method(self):
        """Setup test environment"""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup test environment"""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_basic_clipping(self):
        """Test basic video clipping with auto detection"""
        tool = VideoClipperTool(
            video_url="https://example.com/long_video.mp4",
            clip_duration=30,
            num_clips=3,
            detection_mode="auto",
            aspect_ratio="9:16",
        )
        result = tool.run()

        assert result.get("success") == True
        assert len(result["clips"]) == 3
        assert result["clips"][0]["duration"] == 30
        assert result["aspect_ratio"] == "9:16"

    def test_action_detection(self):
        """Test action detection mode"""
        tool = VideoClipperTool(
            video_url="https://example.com/sports_video.mp4",
            clip_duration=15,
            num_clips=5,
            detection_mode="action",
            aspect_ratio="16:9",
            add_captions=False,
        )
        result = tool.run()

        assert result.get("success") == True
        assert len(result["clips"]) == 5
        assert result["clips"][0]["highlight_type"] in [
            "fast_motion",
            "scene_change",
            "intense_moment",
        ]

    def test_dialogue_detection_with_captions(self):
        """Test dialogue detection with captions enabled"""
        tool = VideoClipperTool(
            video_url="https://example.com/podcast.mp4",
            clip_duration=45,
            num_clips=2,
            detection_mode="dialogue",
            aspect_ratio="1:1",
            add_captions=True,
            optimize_for="instagram",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result["metadata"]["transcription_available"] == True
        assert result["metadata"]["platform_optimized"] == "instagram"

    def test_tiktok_optimization(self):
        """Test TikTok platform optimization"""
        tool = VideoClipperTool(
            video_url="https://example.com/viral_video.mp4",
            clip_duration=30,
            num_clips=3,
            detection_mode="highlights",
            aspect_ratio="9:16",
            add_captions=True,
            add_transitions=True,
            optimize_for="tiktok",
            output_format="mp4",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result["clips"][0]["format"] == "mp4"

    def test_youtube_shorts(self):
        """Test YouTube Shorts optimization"""
        tool = VideoClipperTool(
            video_url="https://example.com/educational_video.mp4",
            clip_duration=60,
            num_clips=1,
            detection_mode="topics",
            aspect_ratio="9:16",
            optimize_for="youtube_shorts",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result["clips"][0]["duration"] == 60

    def test_all_aspect_ratios(self):
        """Test all supported aspect ratios"""
        for aspect_ratio in ["16:9", "9:16", "1:1", "4:5"]:
            tool = VideoClipperTool(
                video_url="https://example.com/video.mp4",
                clip_duration=20,
                num_clips=1,
                aspect_ratio=aspect_ratio,
            )
            result = tool.run()

            assert result.get("success") == True
            assert result["aspect_ratio"] == aspect_ratio

    def test_invalid_url_validation(self):
        """Test URL validation with invalid protocol"""
        with pytest.raises(Exception):
            tool = VideoClipperTool(
                video_url="ftp://invalid.url/video.mp4",
                clip_duration=30,
                num_clips=3,
            )

    def test_duration_exceeds_platform_limit(self):
        """Test validation when clip duration exceeds platform limit"""
        tool = VideoClipperTool(
            video_url="https://example.com/video.mp4",
            clip_duration=90,  # Exceeds TikTok 60s limit
            num_clips=2,
            optimize_for="tiktok",
        )
        result = tool.run()

        # Should return error response
        assert result.get("success") == False
        assert "error" in result

    def test_clip_scoring_order(self):
        """Test that clips are ordered by score descending"""
        tool = VideoClipperTool(
            video_url="https://example.com/video.mp4",
            clip_duration=30,
            num_clips=5,
            detection_mode="highlights",
        )
        result = tool.run()

        scores = [clip["score"] for clip in result["clips"]]
        assert scores == sorted(scores, reverse=True)

    def test_general_platform_long_clips(self):
        """Test general platform with longer clip duration"""
        tool = VideoClipperTool(
            video_url="https://example.com/documentary.mp4",
            clip_duration=120,
            num_clips=2,
            detection_mode="auto",
            optimize_for="general",
            add_transitions=False,
        )
        result = tool.run()

        assert result.get("success") == True
        assert result["clips"][0]["duration"] == 120

    def test_all_detection_modes(self):
        """Test all detection modes"""
        for mode in ["auto", "action", "dialogue", "highlights", "topics"]:
            tool = VideoClipperTool(
                video_url="https://example.com/video.mp4",
                clip_duration=30,
                num_clips=2,
                detection_mode=mode,
            )
            result = tool.run()

            assert result.get("success") == True
            assert result["metadata"]["detection_mode"] == mode

    def test_output_formats(self):
        """Test all output formats"""
        for format in ["mp4", "mov", "webm"]:
            tool = VideoClipperTool(
                video_url="https://example.com/video.mp4",
                clip_duration=30,
                num_clips=1,
                output_format=format,
            )
            result = tool.run()

            assert result.get("success") == True
            assert result["clips"][0]["format"] == format

    def test_parameter_boundaries(self):
        """Test parameter boundary conditions"""
        # Minimum clip duration
        tool_min = VideoClipperTool(
            video_url="https://example.com/video.mp4",
            clip_duration=10,
            num_clips=1,
        )
        result_min = tool_min.run()
        assert result_min.get("success") == True

        # Maximum clip duration (general platform)
        tool_max = VideoClipperTool(
            video_url="https://example.com/video.mp4",
            clip_duration=300,
            num_clips=1,
            optimize_for="general",
        )
        result_max = tool_max.run()
        assert result_max.get("success") == True

        # Minimum clips
        assert len(result_min["clips"]) >= 1

        # Maximum clips
        tool_clips = VideoClipperTool(
            video_url="https://example.com/video.mp4",
            clip_duration=20,
            num_clips=10,
        )
        result_clips = tool_clips.run()
        assert len(result_clips["clips"]) <= 10


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
