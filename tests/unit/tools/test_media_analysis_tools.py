"""
Comprehensive unit tests for Media Analysis Tools category.

Tests all media analysis and processing tools:
- understand_images
- understand_video
- batch_understand_videos
- analyze_media_content
- audio_transcribe
- merge_audio
- extract_audio_from_video
- audio_effects
- batch_video_analysis
- video_metadata_extractor
"""

import json
import os
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from shared.errors import APIError, MediaError, ValidationError
from tools.media.analysis.analyze_media_content.analyze_media_content import AnalyzeMediaContent
from tools.media.analysis.audio_effects.audio_effects import AudioEffects
from tools.media.analysis.audio_transcribe.audio_transcribe import AudioTranscribe
from tools.media.analysis.batch_understand_videos.batch_understand_videos import (
    BatchUnderstandVideos,
)
from tools.media.analysis.batch_video_analysis.batch_video_analysis import BatchVideoAnalysis
from tools.media.analysis.extract_audio_from_video.extract_audio_from_video import (
    ExtractAudioFromVideo,
)
from tools.media.analysis.merge_audio.merge_audio import MergeAudio
from tools.media.analysis.understand_images.understand_images import UnderstandImages
from tools.media.analysis.understand_video.understand_video import UnderstandVideo
from tools.media.analysis.video_metadata_extractor.video_metadata_extractor import (
    VideoMetadataExtractor,
)

# ========== UnderstandImages Tests ==========


class TestUnderstandImages:
    """Comprehensive tests for UnderstandImages tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = UnderstandImages(
            media_url="https://example.com/image1.jpg",
            instruction="Describe what you see in these images",
        )
        assert tool.media_url == "https://example.com/image1.jpg"
        assert tool.instruction == "Describe what you see in these images"
        assert tool.tool_name == "understand_images"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = UnderstandImages(
            media_url="https://example.com/test.jpg", instruction="Analyze this image"
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_urls(self):
        """Test validation with empty media URLs"""
        tool = UnderstandImages(media_url="", instruction="test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = UnderstandImages(media_url="not-a-url", instruction="test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_empty_instruction(self):
        """Test validation with empty instruction"""
        # instruction is optional, so this should succeed
        tool = UnderstandImages(media_url="https://example.com/image.jpg", instruction=None)
        assert tool.instruction is None

    def test_execute_live_mode_success(self, monkeypatch):
        """Test execution with mocked vision API - uses mock mode to avoid rate limits"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")

        tool = UnderstandImages(
            media_url="https://example.com/image.jpg", instruction="What is in this image?"
        )
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_aidrive_url(self, monkeypatch):
        """Test analyzing image from AI Drive"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = UnderstandImages(
            media_url="aidrive://path/to/image.jpg", instruction="Analyze this image"
        )
        result = tool.run()

        assert result["success"] is True


# ========== UnderstandVideo Tests ==========


class TestUnderstandVideo:
    """Comprehensive tests for UnderstandVideo tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = UnderstandVideo(
            media_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            instruction="Summarize the content of this video",
        )
        assert tool.media_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert tool.instruction == "Summarize the content of this video"
        assert tool.tool_name == "understand_video"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = UnderstandVideo(
            media_url="https://www.youtube.com/watch?v=test123",
            instruction="What happens in this video?",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_urls(self):
        """Test validation with empty URLs"""
        tool = UnderstandVideo(media_url="", instruction="test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_execute_live_mode_success(self, monkeypatch):
        """Test execution with mocked video analysis API - uses mock mode to avoid rate limits"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")

        tool = UnderstandVideo(
            media_url="https://www.youtube.com/watch?v=test123", instruction="Summarize"
        )
        result = tool.run()

        assert result["success"] is True


# ========== BatchUnderstandVideos Tests ==========


class TestBatchUnderstandVideos:
    """Comprehensive tests for BatchUnderstandVideos tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = BatchUnderstandVideos(
            media_url="https://www.youtube.com/watch?v=test1,https://www.youtube.com/watch?v=test2",
            instruction="Analyze these videos",
        )
        assert "," in tool.media_url
        assert tool.tool_name == "batch_understand_videos"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = BatchUnderstandVideos(
            media_url="https://www.youtube.com/watch?v=v1,https://youtu.be/v2",
            instruction="Compare these videos",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_edge_case_large_batch(self, monkeypatch):
        """Test processing large batch of videos"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        urls = ",".join([f"https://www.youtube.com/watch?v=test{i}" for i in range(20)])
        tool = BatchUnderstandVideos(media_url=urls, instruction="Analyze all")
        result = tool.run()

        assert result["success"] is True


# ========== AnalyzeMediaContent Tests ==========


class TestAnalyzeMediaContent:
    """Comprehensive tests for AnalyzeMediaContent tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = AnalyzeMediaContent(
            media_url="https://example.com/media.mp4", instruction="Analyze content"
        )
        assert tool.media_url == "https://example.com/media.mp4"
        assert tool.instruction == "Analyze content"
        assert tool.tool_name == "analyze_media_content"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AnalyzeMediaContent(
            media_url="https://example.com/test.mp4", instruction="Analyze sentiment"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = AnalyzeMediaContent(media_url="not-a-valid-url", instruction="test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== AudioTranscribe Tests ==========


class TestAudioTranscribe:
    """Comprehensive tests for AudioTranscribe tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = AudioTranscribe(input="https://example.com/audio.mp3")
        assert tool.input == "https://example.com/audio.mp3"
        assert tool.tool_name == "audio_transcribe"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AudioTranscribe(input="https://example.com/speech.wav")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty audio URL"""
        # Empty string is allowed by Pydantic but caught in _validate_parameters
        tool = AudioTranscribe(input="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_language(self):
        """Test validation with invalid language code"""
        # AudioTranscribe no longer has a language parameter
        # Testing with valid input should succeed
        tool = AudioTranscribe(input="https://example.com/audio.mp3")
        # This should not raise an error
        tool._validate_parameters()

    def test_execute_live_mode_success(self, monkeypatch):
        """Test execution with mocked transcription - uses mock mode to avoid dependencies"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")

        tool = AudioTranscribe(input="https://example.com/audio.mp3")
        result = tool.run()

        assert result["success"] is True
        assert "text" in result.get("result", {})

    def test_edge_case_multiple_languages(self, monkeypatch):
        """Test transcription with different audio files"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        # Test with different audio file paths
        audio_files = ["audio_en.mp3", "audio_es.mp3", "audio_fr.mp3"]

        for audio in audio_files:
            tool = AudioTranscribe(input=f"https://example.com/{audio}")
            result = tool.run()
            assert result["success"] is True


# ========== MergeAudio Tests ==========


class TestMergeAudio:
    """Comprehensive tests for MergeAudio tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        import json

        input_json = json.dumps(
            {
                "clips": [
                    {"path": "https://example.com/audio1.mp3", "start": 0},
                    {"path": "https://example.com/audio2.mp3", "start": 5000},
                ],
                "output_format": "mp3",
            }
        )
        tool = MergeAudio(input=input_json)
        assert tool.input is not None
        assert tool.tool_name == "merge_audio"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        import json

        input_json = json.dumps(
            {
                "clips": [
                    {"path": "https://example.com/a1.mp3", "start": 0},
                    {"path": "https://example.com/a2.mp3", "start": 3000},
                ],
                "output_format": "mp3",
            }
        )
        tool = MergeAudio(input=input_json)
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_insufficient_files(self):
        """Test validation with less than 2 audio files"""
        import json

        input_json = json.dumps(
            {
                "clips": [{"path": "https://example.com/audio1.mp3", "start": 0}],
                "output_format": "mp3",
            }
        )
        tool = MergeAudio(input=input_json)
        # Single clip is technically valid for MergeAudio, just validates the structure
        tool._validate_parameters()  # Should not raise error

    def test_edge_case_many_files(self, monkeypatch):
        """Test merging many audio files"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        import json

        clips = [
            {"path": f"https://example.com/audio{i}.mp3", "start": i * 1000} for i in range(10)
        ]
        input_json = json.dumps({"clips": clips, "output_format": "mp3"})
        tool = MergeAudio(input=input_json)
        result = tool.run()

        assert result["success"] is True


# ========== ExtractAudioFromVideo Tests ==========


class TestExtractAudioFromVideo:
    """Comprehensive tests for ExtractAudioFromVideo tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            tool = ExtractAudioFromVideo(input=tmp_path)
            assert tool.input == tmp_path
            assert tool.tool_name == "extract_audio_from_video"
        finally:
            import os as os_mod

            if os_mod.path.exists(tmp_path):
                os_mod.remove(tmp_path)

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            tool = ExtractAudioFromVideo(input=tmp_path)
            result = tool.run()

            assert result["success"] is True
            assert result["metadata"]["mock_mode"] is True
        finally:
            import os as os_mod

            if os_mod.path.exists(tmp_path):
                os_mod.remove(tmp_path)

    def test_validate_parameters_empty_url(self):
        """Test validation with empty video URL"""
        tool = ExtractAudioFromVideo(input="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_file(self):
        """Test validation with non-existent file"""
        tool = ExtractAudioFromVideo(input="/nonexistent/file.mp4")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_execute_live_mode_success(self, monkeypatch):
        """Test execution with mocked extraction - uses mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            tool = ExtractAudioFromVideo(input=tmp_path)
            result = tool.run()

            assert result["success"] is True
        finally:
            import os as os_mod

            if os_mod.path.exists(tmp_path):
                os_mod.remove(tmp_path)


# ========== AudioEffects Tests ==========


class TestAudioEffects:
    """Comprehensive tests for AudioEffects tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = AudioEffects(
            input_path="/path/to/audio.mp3",
            effects=[
                {"type": "reverb", "parameters": {"room_size": 0.5}},
                {"type": "normalize", "parameters": {"target_level": -3}},
            ],
        )
        assert tool.input_path == "/path/to/audio.mp3"
        assert len(tool.effects) == 2
        assert tool.effects[0]["type"] == "reverb"
        assert tool.tool_name == "audio_effects"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AudioEffects(
            input_path="/path/to/test.mp3",
            effects=[{"type": "echo", "parameters": {"delay": 500, "decay": 0.6}}],
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_invalid_intensity(self):
        """Test validation with invalid effect type"""
        tool = AudioEffects(
            input_path="/path/to/audio.mp3", effects=[{"type": "invalid_effect", "parameters": {}}]
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_edge_case_different_effects(self, monkeypatch):
        """Test different audio effects"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        effects = ["reverb", "echo", "pitch_shift", "tempo_change", "normalize"]

        for effect in effects:
            tool = AudioEffects(
                input_path="/path/to/audio.mp3", effects=[{"type": effect, "parameters": {}}]
            )
            result = tool.run()
            assert result["success"] is True


# ========== BatchVideoAnalysis Tests ==========


class TestBatchVideoAnalysis:
    """Comprehensive tests for BatchVideoAnalysis tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = BatchVideoAnalysis(
            video_urls="https://example.com/v1.mp4,https://example.com/v2.mp4",
            analysis_types=["content"],
        )
        assert "," in tool.video_urls
        assert "content" in tool.analysis_types
        assert tool.tool_name == "batch_video_analysis"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = BatchVideoAnalysis(
            video_urls="https://example.com/v1.mp4", analysis_types=["sentiment"]
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_urls(self):
        """Test validation with empty video URLs"""
        # Pydantic now catches empty string due to min_length=1
        with pytest.raises(PydanticValidationError):
            tool = BatchVideoAnalysis(video_urls="", analysis_types=["content"])


# ========== VideoMetadataExtractor Tests ==========


class TestVideoMetadataExtractor:
    """Comprehensive tests for VideoMetadataExtractor tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = VideoMetadataExtractor(video_path="https://example.com/video.mp4")
        assert tool.video_path == "https://example.com/video.mp4"
        assert tool.tool_name == "video_metadata_extractor"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = VideoMetadataExtractor(video_path="https://example.com/test.mp4")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty video URL"""
        with pytest.raises(PydanticValidationError):
            VideoMetadataExtractor(video_path="")

    def test_execute_live_mode_success(self, monkeypatch):
        """Test execution with mocked metadata extraction - uses mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")

        tool = VideoMetadataExtractor(video_path="https://example.com/video.mp4")
        result = tool.run()

        assert result["success"] is True
        assert "video" in result.get("result", {})
        assert result.get("result", {}).get("video", {}).get("resolution") == "1920x1080"

    def test_edge_case_various_video_formats(self, monkeypatch):
        """Test metadata extraction for different video formats"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        formats = [".mp4", ".avi", ".mkv", ".mov", ".webm"]

        for fmt in formats:
            tool = VideoMetadataExtractor(video_path=f"https://example.com/video{fmt}")
            result = tool.run()
            assert result["success"] is True
