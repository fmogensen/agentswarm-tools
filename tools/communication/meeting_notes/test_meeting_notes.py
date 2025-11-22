"""
Unit tests for MeetingNotesAgent tool
"""

import pytest
import os
from unittest.mock import patch, MagicMock

from meeting_notes import MeetingNotesAgent
from shared.errors import ValidationError, APIError


class TestMeetingNotesAgent:
    """Test suite for MeetingNotesAgent"""

    def setup_method(self):
        """Setup test environment before each test"""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after each test"""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_basic_meeting_notes_creation(self):
        """Test basic meeting notes generation with default settings"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"],
            meeting_title="Test Meeting"
        )
        result = tool.run()

        assert result["success"] == True
        assert "notes_url" in result["result"]
        assert "transcript_url" in result["result"]
        assert "exports" in result["result"]
        assert "markdown" in result["result"]["exports"]
        assert result["result"]["meeting_title"] == "Test Meeting"

    def test_multiple_export_formats(self):
        """Test generating notes with multiple export formats"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown", "pdf", "notion"]
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["result"]["exports"]) == 3
        assert "markdown" in result["result"]["exports"]
        assert "pdf" in result["result"]["exports"]
        assert "notion" in result["result"]["exports"]

    def test_action_items_extraction(self):
        """Test action items extraction"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"],
            extract_action_items=True
        )
        result = tool.run()

        assert result["success"] == True
        assert "action_items" in result["result"]
        assert result["result"]["action_items"] > 0

    def test_action_items_disabled(self):
        """Test with action items disabled"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"],
            extract_action_items=False
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["action_items"] == 0

    def test_speaker_identification(self):
        """Test speaker identification feature"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"],
            identify_speakers=True
        )
        result = tool.run()

        assert result["success"] == True
        # In mock mode, this should still work

    def test_notion_export_only(self):
        """Test exporting to Notion only"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["notion"],
            meeting_title="Notion Meeting"
        )
        result = tool.run()

        assert result["success"] == True
        assert "notion" in result["result"]["exports"]
        assert result["result"]["exports"]["notion"].startswith("https://notion.so")

    def test_pdf_export_only(self):
        """Test PDF export only"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["pdf"]
        )
        result = tool.run()

        assert result["success"] == True
        assert "pdf" in result["result"]["exports"]

    def test_transcript_inclusion(self):
        """Test including full transcript"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"],
            include_transcript=True
        )
        result = tool.run()

        assert result["success"] == True
        assert "transcript_url" in result["result"]

    def test_transcript_exclusion(self):
        """Test excluding full transcript"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"],
            include_transcript=False
        )
        result = tool.run()

        assert result["success"] == True
        # Should still have transcript_url even if not included in notes

    def test_empty_audio_url_validation(self):
        """Test validation fails with empty audio URL"""
        with pytest.raises(ValidationError) as exc_info:
            tool = MeetingNotesAgent(
                audio_url="",
                export_formats=["markdown"]
            )
            tool.run()

        assert "audio_url cannot be empty" in str(exc_info.value)

    def test_invalid_audio_url_validation(self):
        """Test validation fails with invalid URL format"""
        with pytest.raises(ValidationError) as exc_info:
            tool = MeetingNotesAgent(
                audio_url="invalid-url",
                export_formats=["markdown"]
            )
            tool.run()

        assert "must be a valid HTTP/HTTPS URL" in str(exc_info.value)

    def test_empty_export_formats_validation(self):
        """Test validation fails with empty export formats"""
        with pytest.raises(ValidationError) as exc_info:
            tool = MeetingNotesAgent(
                audio_url="https://example.com/meeting.mp3",
                export_formats=[]
            )
            tool.run()

        assert "export_formats cannot be empty" in str(exc_info.value)

    def test_invalid_export_format_validation(self):
        """Test validation fails with invalid export format"""
        with pytest.raises(ValidationError) as exc_info:
            tool = MeetingNotesAgent(
                audio_url="https://example.com/meeting.mp3",
                export_formats=["invalid_format"]
            )
            tool.run()

        assert "Invalid export format" in str(exc_info.value)

    def test_mixed_valid_invalid_formats(self):
        """Test validation fails with mix of valid and invalid formats"""
        with pytest.raises(ValidationError) as exc_info:
            tool = MeetingNotesAgent(
                audio_url="https://example.com/meeting.mp3",
                export_formats=["markdown", "invalid", "pdf"]
            )
            tool.run()

        assert "Invalid export format" in str(exc_info.value)

    def test_default_meeting_title(self):
        """Test default meeting title when not provided"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"]
        )
        result = tool.run()

        assert result["success"] == True
        # Should have a default title

    def test_custom_meeting_title(self):
        """Test custom meeting title"""
        title = "Q4 2025 Planning Meeting"
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"],
            meeting_title=title
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["meeting_title"] == title

    def test_mock_mode_enabled(self):
        """Test that mock mode works correctly"""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"]
        )
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True

    def test_all_features_combined(self):
        """Test all features enabled together"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown", "pdf", "notion"],
            include_transcript=True,
            extract_action_items=True,
            identify_speakers=True,
            meeting_title="Complete Feature Test"
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["result"]["exports"]) == 3
        assert result["result"]["action_items"] > 0
        assert result["result"]["meeting_title"] == "Complete Feature Test"

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_missing_api_key_in_real_mode(self):
        """Test that missing API key raises error in real mode"""
        # Ensure no API keys are set
        env_backup = {}
        for key in ["GENSPARK_API_KEY", "OPENAI_API_KEY"]:
            if key in os.environ:
                env_backup[key] = os.environ[key]
                del os.environ[key]

        try:
            tool = MeetingNotesAgent(
                audio_url="https://example.com/meeting.mp3",
                export_formats=["markdown"]
            )

            with patch("requests.head") as mock_head:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.headers = {"Content-Length": "1000", "Content-Type": "audio/mpeg"}
                mock_head.return_value = mock_response

                with pytest.raises(APIError) as exc_info:
                    tool.run()

                assert "Missing API credentials" in str(exc_info.value)
        finally:
            # Restore environment
            for key, value in env_backup.items():
                os.environ[key] = value

    def test_duration_in_result(self):
        """Test that duration is included in result"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"]
        )
        result = tool.run()

        assert result["success"] == True
        assert "duration" in result["result"]

    def test_metadata_structure(self):
        """Test metadata structure in response"""
        tool = MeetingNotesAgent(
            audio_url="https://example.com/meeting.mp3",
            export_formats=["markdown"]
        )
        result = tool.run()

        assert "metadata" in result
        assert "tool_name" in result["metadata"]
        assert result["metadata"]["tool_name"] == "meeting_notes_agent"

    def test_whitespace_audio_url_validation(self):
        """Test validation fails with whitespace-only audio URL"""
        with pytest.raises(ValidationError) as exc_info:
            tool = MeetingNotesAgent(
                audio_url="   ",
                export_formats=["markdown"]
            )
            tool.run()

        assert "audio_url cannot be empty" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
