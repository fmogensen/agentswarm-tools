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

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any, List

from tools.media_analysis.understand_images.understand_images import UnderstandImages
from tools.media_analysis.understand_video.understand_video import UnderstandVideo
from tools.media_analysis.batch_understand_videos.batch_understand_videos import (
    BatchUnderstandVideos,
)
from tools.media_analysis.analyze_media_content.analyze_media_content import AnalyzeMediaContent
from tools.media_analysis.audio_transcribe.audio_transcribe import AudioTranscribe
from tools.media_analysis.merge_audio.merge_audio import MergeAudio
from tools.media_analysis.extract_audio_from_video.extract_audio_from_video import (
    ExtractAudioFromVideo,
)
from tools.media_analysis.audio_effects.audio_effects import AudioEffects
from tools.media_analysis.batch_video_analysis.batch_video_analysis import BatchVideoAnalysis
from tools.media_analysis.video_metadata_extractor.video_metadata_extractor import (
    VideoMetadataExtractor,
)

from shared.errors import ValidationError, APIError, MediaError


# ========== UnderstandImages Tests ==========


class TestUnderstandImages:
    """Comprehensive tests for UnderstandImages tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = UnderstandImages(
            media_urls=["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
            instruction="Describe what you see in these images",
        )
        assert len(tool.media_urls) == 2
        assert tool.instruction == "Describe what you see in these images"
        assert tool.tool_name == "understand_images"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = UnderstandImages(
            media_urls=["https://example.com/test.jpg"], instruction="Analyze this image"
        )
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_urls(self):
        """Test validation with empty media URLs"""
        tool = UnderstandImages(media_urls=[], instruction="test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_url(self):
        """Test validation with invalid URL"""
        tool = UnderstandImages(media_urls=["not-a-url"], instruction="test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_empty_instruction(self):
        """Test validation with empty instruction"""
        tool = UnderstandImages(media_urls=["https://example.com/image.jpg"], instruction="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.media_analysis.understand_images.understand_images.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked vision API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("OPENAI_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"analysis": "The image shows a sunset over mountains."}
        mock_post.return_value = mock_response

        tool = UnderstandImages(
            media_urls=["https://example.com/image.jpg"], instruction="What is in this image?"
        )
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_multiple_images(self, monkeypatch):
        """Test analyzing multiple images at once"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        urls = [f"https://example.com/image{i}.jpg" for i in range(10)]
        tool = UnderstandImages(media_urls=urls, instruction="Analyze all images")
        result = tool.run()

        assert result["success"] is True


# ========== UnderstandVideo Tests ==========


class TestUnderstandVideo:
    """Comprehensive tests for UnderstandVideo tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = UnderstandVideo(
            media_urls=["https://example.com/video.mp4"],
            instruction="Summarize the content of this video",
        )
        assert len(tool.media_urls) == 1
        assert tool.instruction == "Summarize the content of this video"
        assert tool.tool_name == "understand_video"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = UnderstandVideo(
            media_urls=["https://example.com/test.mp4"], instruction="What happens in this video?"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_urls(self):
        """Test validation with empty URLs"""
        tool = UnderstandVideo(media_urls=[], instruction="test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.media_analysis.understand_video.understand_video.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked video analysis API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("VIDEO_ANALYSIS_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "summary": "The video shows a tutorial on Python programming."
        }
        mock_post.return_value = mock_response

        tool = UnderstandVideo(
            media_urls=["https://example.com/video.mp4"], instruction="Summarize"
        )
        result = tool.run()

        assert result["success"] is True


# ========== BatchUnderstandVideos Tests ==========


class TestBatchUnderstandVideos:
    """Comprehensive tests for BatchUnderstandVideos tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = BatchUnderstandVideos(
            media_urls=["https://example.com/video1.mp4", "https://example.com/video2.mp4"],
            instruction="Analyze these videos",
        )
        assert len(tool.media_urls) == 2
        assert tool.tool_name == "batch_understand_videos"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = BatchUnderstandVideos(
            media_urls=["https://example.com/v1.mp4", "https://example.com/v2.mp4"],
            instruction="Compare these videos",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_edge_case_large_batch(self, monkeypatch):
        """Test processing large batch of videos"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        urls = [f"https://example.com/video{i}.mp4" for i in range(20)]
        tool = BatchUnderstandVideos(media_urls=urls, instruction="Analyze all")
        result = tool.run()

        assert result["success"] is True


# ========== AnalyzeMediaContent Tests ==========


class TestAnalyzeMediaContent:
    """Comprehensive tests for AnalyzeMediaContent tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = AnalyzeMediaContent(
            media_url="https://example.com/media.mp4", analysis_type="content"
        )
        assert tool.media_url == "https://example.com/media.mp4"
        assert tool.analysis_type == "content"
        assert tool.tool_name == "analyze_media_content"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AnalyzeMediaContent(
            media_url="https://example.com/test.mp4", analysis_type="sentiment"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_invalid_analysis_type(self):
        """Test validation with invalid analysis type"""
        tool = AnalyzeMediaContent(
            media_url="https://example.com/media.mp4", analysis_type="invalid"
        )
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== AudioTranscribe Tests ==========


class TestAudioTranscribe:
    """Comprehensive tests for AudioTranscribe tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = AudioTranscribe(audio_url="https://example.com/audio.mp3", language="en")
        assert tool.audio_url == "https://example.com/audio.mp3"
        assert tool.language == "en"
        assert tool.tool_name == "audio_transcribe"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AudioTranscribe(audio_url="https://example.com/speech.wav", language="en")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty audio URL"""
        tool = AudioTranscribe(audio_url="", language="en")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_language(self):
        """Test validation with invalid language code"""
        tool = AudioTranscribe(audio_url="https://example.com/audio.mp3", language="invalid")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.media_analysis.audio_transcribe.audio_transcribe.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked transcription API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("WHISPER_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"text": "This is the transcribed text from the audio."}
        mock_post.return_value = mock_response

        tool = AudioTranscribe(audio_url="https://example.com/audio.mp3", language="en")
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_multiple_languages(self, monkeypatch):
        """Test transcription in different languages"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        languages = ["en", "es", "fr", "de", "zh"]

        for lang in languages:
            tool = AudioTranscribe(audio_url="https://example.com/audio.mp3", language=lang)
            result = tool.run()
            assert result["success"] is True


# ========== MergeAudio Tests ==========


class TestMergeAudio:
    """Comprehensive tests for MergeAudio tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = MergeAudio(
            audio_urls=["https://example.com/audio1.mp3", "https://example.com/audio2.mp3"],
            task_summary="Merge audio files",
        )
        assert len(tool.audio_urls) == 2
        assert tool.tool_name == "merge_audio"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = MergeAudio(
            audio_urls=["https://example.com/a1.mp3", "https://example.com/a2.mp3"],
            task_summary="Test merge",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_insufficient_files(self):
        """Test validation with less than 2 audio files"""
        tool = MergeAudio(audio_urls=["https://example.com/audio1.mp3"], task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_edge_case_many_files(self, monkeypatch):
        """Test merging many audio files"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        urls = [f"https://example.com/audio{i}.mp3" for i in range(10)]
        tool = MergeAudio(audio_urls=urls, task_summary="Merge many")
        result = tool.run()

        assert result["success"] is True


# ========== ExtractAudioFromVideo Tests ==========


class TestExtractAudioFromVideo:
    """Comprehensive tests for ExtractAudioFromVideo tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ExtractAudioFromVideo(
            video_url="https://example.com/video.mp4", task_summary="Extract audio track"
        )
        assert tool.video_url == "https://example.com/video.mp4"
        assert tool.tool_name == "extract_audio_from_video"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ExtractAudioFromVideo(
            video_url="https://example.com/test.mp4", task_summary="Test extraction"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty video URL"""
        tool = ExtractAudioFromVideo(video_url="", task_summary="Test")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.media_analysis.extract_audio_from_video.extract_audio_from_video.requests.post")
    def test_execute_live_mode_success(self, mock_post, monkeypatch):
        """Test execution with mocked extraction API"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("FFMPEG_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {"audio_url": "https://example.com/extracted_audio.mp3"}
        mock_post.return_value = mock_response

        tool = ExtractAudioFromVideo(
            video_url="https://example.com/video.mp4", task_summary="Extract"
        )
        result = tool.run()

        assert result["success"] is True


# ========== AudioEffects Tests ==========


class TestAudioEffects:
    """Comprehensive tests for AudioEffects tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = AudioEffects(
            audio_url="https://example.com/audio.mp3",
            effect_type="reverb",
            intensity=0.5,
            task_summary="Apply reverb effect",
        )
        assert tool.audio_url == "https://example.com/audio.mp3"
        assert tool.effect_type == "reverb"
        assert tool.intensity == 0.5
        assert tool.tool_name == "audio_effects"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = AudioEffects(
            audio_url="https://example.com/test.mp3", effect_type="echo", task_summary="Test effect"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_invalid_intensity(self):
        """Test validation with invalid intensity"""
        with pytest.raises(ValidationError):
            AudioEffects(
                audio_url="https://example.com/audio.mp3",
                effect_type="reverb",
                intensity=2.0,  # Should be 0-1
                task_summary="Test",
            )

    def test_edge_case_different_effects(self, monkeypatch):
        """Test different audio effects"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        effects = ["reverb", "echo", "pitch", "speed", "normalize"]

        for effect in effects:
            tool = AudioEffects(
                audio_url="https://example.com/audio.mp3",
                effect_type=effect,
                task_summary=f"Test {effect}",
            )
            result = tool.run()
            assert result["success"] is True


# ========== BatchVideoAnalysis Tests ==========


class TestBatchVideoAnalysis:
    """Comprehensive tests for BatchVideoAnalysis tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = BatchVideoAnalysis(
            video_urls=["https://example.com/v1.mp4", "https://example.com/v2.mp4"],
            analysis_type="content",
        )
        assert len(tool.video_urls) == 2
        assert tool.analysis_type == "content"
        assert tool.tool_name == "batch_video_analysis"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = BatchVideoAnalysis(
            video_urls=["https://example.com/v1.mp4"], analysis_type="sentiment"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_urls(self):
        """Test validation with empty video URLs"""
        tool = BatchVideoAnalysis(video_urls=[], analysis_type="content")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== VideoMetadataExtractor Tests ==========


class TestVideoMetadataExtractor:
    """Comprehensive tests for VideoMetadataExtractor tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = VideoMetadataExtractor(video_url="https://example.com/video.mp4")
        assert tool.video_url == "https://example.com/video.mp4"
        assert tool.tool_name == "video_metadata_extractor"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = VideoMetadataExtractor(video_url="https://example.com/test.mp4")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_url(self):
        """Test validation with empty video URL"""
        tool = VideoMetadataExtractor(video_url="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.media_analysis.video_metadata_extractor.video_metadata_extractor.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked metadata extraction"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "duration": 120,
            "resolution": "1920x1080",
            "fps": 30,
            "codec": "h264",
        }
        mock_get.return_value = mock_response

        tool = VideoMetadataExtractor(video_url="https://example.com/video.mp4")
        result = tool.run()

        assert result["success"] is True

    def test_edge_case_various_video_formats(self, monkeypatch):
        """Test metadata extraction for different video formats"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        formats = [".mp4", ".avi", ".mkv", ".mov", ".webm"]

        for fmt in formats:
            tool = VideoMetadataExtractor(video_url=f"https://example.com/video{fmt}")
            result = tool.run()
            assert result["success"] is True
