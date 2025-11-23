"""
Tests for VideoEditorTool.
"""

import os

import pytest
from video_editor import VideoEditorTool


@pytest.fixture(autouse=True)
def setup_mock_mode():
    """Enable mock mode for all tests."""
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    os.environ.pop("USE_MOCK_APIS", None)


class TestVideoEditorTool:
    """Test cases for VideoEditorTool."""

    def test_trim_operation(self):
        """Test trim operation."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "trim", "start": "00:00:10", "end": "00:00:30"}],
            output_format="mp4",
        )
        result = tool.run()

        assert result["success"] is True
        assert "edited_video_url" in result["result"]
        assert result["result"]["operations_applied"] == 1
        assert result["result"]["format"] == "mp4"

    def test_resize_operation(self):
        """Test resize operation."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "resize", "width": 1920, "height": 1080}],
            output_format="mp4",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["operations_applied"] == 1

    def test_rotate_operation(self):
        """Test rotate operation."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "rotate", "degrees": 90}],
            output_format="mp4",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["operations_applied"] == 1

    def test_speed_operation(self):
        """Test speed adjustment operation."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "speed", "factor": 2.0}],
            output_format="mp4",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["operations_applied"] == 1

    def test_add_audio_operation(self):
        """Test add audio operation."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "add_audio", "audio_url": "https://example.com/audio.mp3"}],
            output_format="mp4",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["operations_applied"] == 1

    def test_add_subtitles_operation(self):
        """Test add subtitles operation."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[
                {"type": "add_subtitles", "subtitle_url": "https://example.com/subtitles.srt"}
            ],
            output_format="mp4",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["operations_applied"] == 1

    def test_merge_operation(self):
        """Test merge operation."""
        tool = VideoEditorTool(
            operations=[
                {
                    "type": "merge",
                    "videos": [
                        "https://example.com/video1.mp4",
                        "https://example.com/video2.mp4",
                        "https://example.com/video3.mp4",
                    ],
                }
            ],
            output_format="mp4",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["operations_applied"] == 1

    def test_transition_operation(self):
        """Test transition operation."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "transition", "effect": "fade"}],
            output_format="mp4",
        )
        result = tool.run()

        assert result["success"] is True

    def test_multiple_operations(self):
        """Test multiple operations in sequence."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[
                {"type": "trim", "start": "00:00:05", "end": "00:00:25"},
                {"type": "resize", "width": 1280, "height": 720},
                {"type": "rotate", "degrees": 90},
                {"type": "speed", "factor": 1.5},
            ],
            output_format="mp4",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["operations_applied"] == 4

    def test_different_output_formats(self):
        """Test different output formats."""
        formats = ["mp4", "avi", "mov", "webm"]

        for fmt in formats:
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "trim", "start": "00:00:00", "end": "00:00:10"}],
                output_format=fmt,
            )
            result = tool.run()

            assert result["success"] is True
            assert result["result"]["format"] == fmt

    def test_validation_missing_operation_type(self):
        """Test validation error when operation type is missing."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"start": "00:00:10", "end": "00:00:30"}],  # Missing 'type'
            )
            tool.run()

    def test_validation_invalid_operation_type(self):
        """Test validation error for invalid operation type."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "invalid_operation"}],
            )
            tool.run()

    def test_validation_invalid_output_format(self):
        """Test validation error for invalid output format."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "trim", "start": "00:00:00", "end": "00:00:10"}],
                output_format="invalid_format",
            )
            tool.run()

    def test_validation_trim_missing_end(self):
        """Test validation error when trim operation is missing end time."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "trim", "start": "00:00:10"}],  # Missing 'end'
            )
            tool.run()

    def test_validation_resize_missing_dimensions(self):
        """Test validation error when resize is missing dimensions."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "resize", "width": 1920}],  # Missing 'height'
            )
            tool.run()

    def test_validation_resize_negative_dimensions(self):
        """Test validation error for negative dimensions."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "resize", "width": -1920, "height": 1080}],
            )
            tool.run()

    def test_validation_rotate_invalid_degrees(self):
        """Test validation error for invalid rotation degrees."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "rotate", "degrees": 45}],  # Only 90, 180, 270 allowed
            )
            tool.run()

    def test_validation_speed_negative_factor(self):
        """Test validation error for negative speed factor."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "speed", "factor": -1.0}],
            )
            tool.run()

    def test_validation_merge_insufficient_videos(self):
        """Test validation error when merge has less than 2 videos."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                operations=[
                    {"type": "merge", "videos": ["https://example.com/video1.mp4"]}  # Only 1 video
                ],
            )
            tool.run()

    def test_validation_add_audio_missing_url(self):
        """Test validation error when add_audio is missing audio_url."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "add_audio"}],  # Missing 'audio_url'
            )
            tool.run()

    def test_validation_add_subtitles_missing_url(self):
        """Test validation error when add_subtitles is missing subtitle_url."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "add_subtitles"}],  # Missing 'subtitle_url'
            )
            tool.run()

    def test_validation_transition_invalid_effect(self):
        """Test validation error for invalid transition effect."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "transition", "effect": "invalid_effect"}],
            )
            tool.run()

    def test_time_format_hhmmss(self):
        """Test time format validation with HH:MM:SS."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "trim", "start": "00:01:30", "end": "00:02:45"}],
        )
        result = tool.run()
        assert result["success"] is True

    def test_time_format_numeric_seconds(self):
        """Test time format validation with numeric seconds."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "trim", "start": "10", "end": "30"}],
        )
        result = tool.run()
        assert result["success"] is True

    def test_time_format_decimal_seconds(self):
        """Test time format validation with decimal seconds."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "trim", "start": "10.5", "end": "30.75"}],
        )
        result = tool.run()
        assert result["success"] is True

    def test_rotate_all_valid_degrees(self):
        """Test all valid rotation degrees."""
        valid_degrees = [0, 90, 180, 270, -90, -180, -270]

        for degrees in valid_degrees:
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "rotate", "degrees": degrees}],
            )
            result = tool.run()
            assert result["success"] is True

    def test_speed_various_factors(self):
        """Test various speed factors."""
        speed_factors = [0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0]

        for factor in speed_factors:
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "speed", "factor": factor}],
            )
            result = tool.run()
            assert result["success"] is True

    def test_transition_all_effects(self):
        """Test all transition effects."""
        effects = ["fade", "wipeleft", "wiperight", "wipeup", "wipedown", "dissolve"]

        for effect in effects:
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[{"type": "transition", "effect": effect}],
            )
            result = tool.run()
            assert result["success"] is True

    def test_mock_mode_result_structure(self):
        """Test that mock mode returns proper result structure."""
        tool = VideoEditorTool(
            video_url="https://example.com/video.mp4",
            operations=[{"type": "trim", "start": "00:00:00", "end": "00:00:10"}],
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert "edited_video_url" in result["result"]
        assert "format" in result["result"]
        assert "duration" in result["result"]
        assert "resolution" in result["result"]
        assert "file_size" in result["result"]
        assert "operations_applied" in result["result"]
        assert "fps" in result["result"]
        assert "metadata" in result

    def test_empty_operations_list(self):
        """Test validation error for empty operations list."""
        with pytest.raises(Exception):
            tool = VideoEditorTool(
                video_url="https://example.com/video.mp4",
                operations=[],
            )
            tool.run()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
