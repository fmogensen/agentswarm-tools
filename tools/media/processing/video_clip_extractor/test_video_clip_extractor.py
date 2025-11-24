"""Tests for video_clip_extractor tool."""

import os
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import MediaError, ValidationError
from tools.media.processing.video_clip_extractor.video_clip_extractor import VideoClipExtractor


class TestVideoClipExtractor:
    """Test suite for VideoClipExtractor."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_video_url(self) -> str:
        return "https://example.com/video.mp4"

    @pytest.fixture
    def valid_clips(self) -> list:
        return [
            {"start_time": 10.0, "end_time": 30.0, "label": "intro"},
            {"start_time": 60.0, "end_time": 90.0, "label": "main"},
        ]

    @pytest.fixture
    def tool(self, valid_video_url, valid_clips) -> VideoClipExtractor:
        return VideoClipExtractor(video_url=valid_video_url, clips=valid_clips)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_video_url, valid_clips):
        tool = VideoClipExtractor(video_url=valid_video_url, clips=valid_clips)
        assert tool.video_url == valid_video_url
        assert tool.clips == valid_clips
        assert tool.tool_name == "video_clip_extractor"
        assert tool.tool_category == "media"
        assert tool.output_format == "mp4"
        assert tool.preserve_quality is True
        assert tool.add_fade is False
        assert tool.aspect_ratio is None

    def test_initialization_with_all_params(self, valid_video_url):
        clips = [{"start_time": 5.0, "end_time": 15.0, "label": "test"}]
        tool = VideoClipExtractor(
            video_url=valid_video_url,
            clips=clips,
            output_format="webm",
            preserve_quality=False,
            add_fade=True,
            aspect_ratio="16:9",
        )
        assert tool.output_format == "webm"
        assert tool.preserve_quality is False
        assert tool.add_fade is True
        assert tool.aspect_ratio == "16:9"

    # ========== HAPPY PATH TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_execute_success(self, tool: VideoClipExtractor):
        result = tool.run()

        assert result["success"] is True
        assert "clips" in result
        assert result["total_clips"] == 2
        assert "total_duration" in result
        assert "metadata" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_single_clip_extraction(self, valid_video_url):
        clips = [{"start_time": 10.5, "end_time": 25.75, "label": "highlight"}]
        tool = VideoClipExtractor(video_url=valid_video_url, clips=clips)
        result = tool.run()

        assert result["success"] is True
        assert result["total_clips"] == 1
        assert result["clips"][0]["duration_seconds"] == 15.25
        assert result["clips"][0]["label"] == "highlight"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_multiple_clips_extraction(self, valid_video_url):
        clips = [
            {"start_time": 0, "end_time": 10, "label": "clip1"},
            {"start_time": 20, "end_time": 35, "label": "clip2"},
            {"start_time": 50, "end_time": 70, "label": "clip3"},
        ]
        tool = VideoClipExtractor(video_url=valid_video_url, clips=clips)
        result = tool.run()

        assert result["success"] is True
        assert result["total_clips"] == 3
        assert len(result["clips"]) == 3

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: VideoClipExtractor):
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert all("mock.example.com" in clip["url"] for clip in result["clips"])

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_result_format(self, tool: VideoClipExtractor):
        result = tool.run()

        clip = result["clips"][0]
        assert "clip_id" in clip
        assert "label" in clip
        assert "url" in clip
        assert "start_time" in clip
        assert "end_time" in clip
        assert "duration" in clip
        assert "format" in clip
        assert "resolution" in clip
        assert "file_size" in clip

    # ========== VALIDATION TESTS ==========

    def test_invalid_video_url_scheme(self):
        with pytest.raises(PydanticValidationError):
            VideoClipExtractor(
                video_url="ftp://invalid.com/video.mp4",
                clips=[{"start_time": 0, "end_time": 10}],
            )

    def test_invalid_video_url_empty(self):
        with pytest.raises(PydanticValidationError):
            VideoClipExtractor(video_url="", clips=[{"start_time": 0, "end_time": 10}])

    def test_empty_clips_list(self):
        with pytest.raises(PydanticValidationError):
            VideoClipExtractor(video_url="https://example.com/video.mp4", clips=[])

    def test_invalid_clip_missing_start_time(self, valid_video_url):
        with pytest.raises(PydanticValidationError):
            VideoClipExtractor(
                video_url=valid_video_url, clips=[{"end_time": 10, "label": "test"}]
            )

    def test_invalid_clip_missing_end_time(self, valid_video_url):
        with pytest.raises(PydanticValidationError):
            VideoClipExtractor(
                video_url=valid_video_url, clips=[{"start_time": 0, "label": "test"}]
            )

    def test_invalid_clip_negative_start_time(self, valid_video_url):
        with pytest.raises(PydanticValidationError):
            VideoClipExtractor(
                video_url=valid_video_url, clips=[{"start_time": -10, "end_time": 20}]
            )

    def test_invalid_clip_end_before_start(self, valid_video_url):
        with pytest.raises(PydanticValidationError):
            VideoClipExtractor(
                video_url=valid_video_url, clips=[{"start_time": 60, "end_time": 30}]
            )

    def test_invalid_clip_equal_times(self, valid_video_url):
        with pytest.raises(PydanticValidationError):
            VideoClipExtractor(
                video_url=valid_video_url, clips=[{"start_time": 30, "end_time": 30}]
            )

    def test_invalid_aspect_ratio(self, valid_video_url, valid_clips):
        tool = VideoClipExtractor(
            video_url=valid_video_url, clips=valid_clips, aspect_ratio="21:9"
        )
        result = tool.run()
        assert result["success"] is False

    def test_invalid_output_format(self, valid_video_url, valid_clips):
        with pytest.raises(PydanticValidationError):
            VideoClipExtractor(
                video_url=valid_video_url, clips=valid_clips, output_format="avi"
            )

    # ========== API ERROR TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_api_error_propagation(self, tool: VideoClipExtractor):
        with patch.object(tool, "_process", side_effect=Exception("FFmpeg failed")):
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_precision_timestamps(self, valid_video_url):
        clips = [{"start_time": 12.345, "end_time": 23.678, "label": "precise"}]
        tool = VideoClipExtractor(video_url=valid_video_url, clips=clips)
        result = tool.run()

        assert result["success"] is True
        assert result["clips"][0]["start_seconds"] == 12.345
        assert result["clips"][0]["end_seconds"] == 23.678

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_file_url_protocol(self):
        tool = VideoClipExtractor(
            video_url="file:///path/to/video.mp4",
            clips=[{"start_time": 0, "end_time": 10, "label": "local"}],
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["source_url"] == "file:///path/to/video.mp4"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_clips_without_labels(self, valid_video_url):
        clips = [
            {"start_time": 0, "end_time": 10},
            {"start_time": 20, "end_time": 30},
        ]
        tool = VideoClipExtractor(video_url=valid_video_url, clips=clips)
        result = tool.run()

        assert result["success"] is True
        # Labels should be auto-generated
        assert "clip" in result["clips"][0]["label"].lower()

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_overlapping_clips_warning(self, valid_video_url):
        # Overlapping clips should work but log warning
        clips = [
            {"start_time": 10, "end_time": 30, "label": "clip1"},
            {"start_time": 25, "end_time": 45, "label": "clip2"},
        ]
        tool = VideoClipExtractor(video_url=valid_video_url, clips=clips)
        result = tool.run()

        assert result["success"] is True
        assert result["total_clips"] == 2

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "aspect_ratio,expected_resolution",
        [
            ("16:9", "1920x1080"),
            ("9:16", "1080x1920"),
            ("1:1", "1080x1080"),
            ("4:5", "1080x1350"),
            (None, "1920x1080"),  # Original/default
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_aspect_ratios(self, valid_video_url, aspect_ratio, expected_resolution):
        clips = [{"start_time": 0, "end_time": 10, "label": "test"}]
        tool = VideoClipExtractor(
            video_url=valid_video_url, clips=clips, aspect_ratio=aspect_ratio
        )
        result = tool.run()

        assert result["success"] is True
        assert expected_resolution in result["clips"][0]["resolution"]

    @pytest.mark.parametrize("output_format", ["mp4", "mov", "webm"])
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_output_formats(self, valid_video_url, output_format):
        clips = [{"start_time": 0, "end_time": 10, "label": "test"}]
        tool = VideoClipExtractor(
            video_url=valid_video_url, clips=clips, output_format=output_format
        )
        result = tool.run()

        assert result["success"] is True
        assert result["clips"][0]["format"] == output_format
        assert output_format in result["clips"][0]["url"]

    @pytest.mark.parametrize("preserve_quality", [True, False])
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_quality_settings(self, valid_video_url, preserve_quality):
        clips = [{"start_time": 0, "end_time": 10, "label": "test"}]
        tool = VideoClipExtractor(
            video_url=valid_video_url, clips=clips, preserve_quality=preserve_quality
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["preserve_quality"] == preserve_quality

    @pytest.mark.parametrize(
        "clips,expected_clips",
        [
            ([{"start_time": 0, "end_time": 10}], 1),
            (
                [
                    {"start_time": 0, "end_time": 10},
                    {"start_time": 20, "end_time": 30},
                ],
                2,
            ),
            (
                [
                    {"start_time": 0, "end_time": 5},
                    {"start_time": 10, "end_time": 15},
                    {"start_time": 20, "end_time": 25},
                    {"start_time": 30, "end_time": 35},
                ],
                4,
            ),
        ],
    )
    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_various_clip_counts(self, valid_video_url, clips, expected_clips):
        tool = VideoClipExtractor(video_url=valid_video_url, clips=clips)
        result = tool.run()

        assert result["success"] is True
        assert result["total_clips"] == expected_clips

    # ========== INTERNAL METHOD TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_generate_mock_results_format(self, tool):
        result = tool._generate_mock_results()

        assert result["success"] is True
        assert "clips" in result
        assert "total_clips" in result
        assert "total_duration" in result
        assert "metadata" in result
        assert result["metadata"]["mock_mode"] is True

    def test_should_use_mock(self, tool):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            assert tool._should_use_mock() is True
        with patch.dict("os.environ", {"USE_MOCK_APIS": "false"}):
            assert tool._should_use_mock() is False

    def test_format_timestamp(self, tool):
        assert tool._format_timestamp(0) == "00:00:00.000"
        assert tool._format_timestamp(65.5) == "00:01:05.500"
        assert tool._format_timestamp(3661.25) == "01:01:01.250"

    def test_format_file_size(self, tool):
        assert tool._format_file_size(512) == "512 B"
        assert tool._format_file_size(1536) == "1.5 KB"
        assert tool._format_file_size(2097152) == "2.0 MB"
        assert tool._format_file_size(1073741824) == "1.0 GB"

    # ========== INTEGRATION TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow_with_fade(self, valid_video_url):
        clips = [{"start_time": 0, "end_time": 30, "label": "intro"}]
        tool = VideoClipExtractor(
            video_url=valid_video_url,
            clips=clips,
            output_format="mp4",
            add_fade=True,
            aspect_ratio="16:9",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["fade_transitions"] is True
        assert result["metadata"]["aspect_ratio_applied"] == "16:9"

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_full_workflow_multiple_formats(self, valid_video_url):
        clips = [
            {"start_time": 10, "end_time": 20, "label": "clip1"},
            {"start_time": 30, "end_time": 50, "label": "clip2"},
        ]

        # Test with different formats
        for fmt in ["mp4", "mov", "webm"]:
            tool = VideoClipExtractor(
                video_url=valid_video_url, clips=clips, output_format=fmt
            )
            result = tool.run()

            assert result["success"] is True
            assert all(clip["format"] == fmt for clip in result["clips"])

    def test_error_formatting_integration(self, tool: VideoClipExtractor):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert result["success"] is False or "error" in result

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_total_duration_calculation(self, valid_video_url):
        clips = [
            {"start_time": 0, "end_time": 10, "label": "clip1"},  # 10s
            {"start_time": 20, "end_time": 35, "label": "clip2"},  # 15s
            {"start_time": 50, "end_time": 75, "label": "clip3"},  # 25s
        ]
        tool = VideoClipExtractor(video_url=valid_video_url, clips=clips)
        result = tool.run()

        assert result["success"] is True
        # Total should be 50s
        assert "50.0" in result["total_duration"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
