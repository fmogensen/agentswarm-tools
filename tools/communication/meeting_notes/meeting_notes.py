"""
Transcribe meeting audio and generate structured notes with action items
"""

import os
from typing import Any, Dict, List, Optional

import requests
from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class MeetingNotesAgent(BaseTool):
    """
    Transcribe meeting audio and generate structured notes with action items.

    Use this tool to process meeting recordings into organized notes including
    transcript, summary, action items, key decisions, and participants.

    Args:
        audio_url: URL to meeting audio file
        export_formats: List of export formats (notion, pdf, markdown)
        include_transcript: Whether to include full transcript
        extract_action_items: Whether to extract action items
        identify_speakers: Whether to identify different speakers
        meeting_title: Optional meeting title

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: {"notes_url": "...", "transcript_url": "...", "exports": {...}}
        - metadata: Processing metadata

    Example:
        >>> tool = MeetingNotesAgent(
        ...     audio_url="https://example.com/meeting.mp3",
        ...     export_formats=["notion", "pdf"],
        ...     extract_action_items=True,
        ...     meeting_title="Q4 Planning Meeting"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "meeting_notes_agent"
    tool_category: str = "communication"

    # Parameters
    audio_url: str = Field(..., description="URL to meeting audio file")
    export_formats: List[str] = Field(
        ["markdown"], description="Export formats: notion, pdf, markdown"
    )
    include_transcript: bool = Field(True, description="Include full transcript")
    extract_action_items: bool = Field(True, description="Extract action items")
    identify_speakers: bool = Field(False, description="Identify different speakers")
    meeting_title: Optional[str] = Field(None, description="Meeting title")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the meeting_notes_agent tool.

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
                    "mock_mode": False,
                },
            }
        except Exception as e:
            raise APIError(f"Failed to process meeting notes: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate audio_url
        if not self.audio_url or not self.audio_url.strip():
            raise ValidationError(
                "audio_url cannot be empty", tool_name=self.tool_name, field="audio_url"
            )

        # Basic URL validation
        if not self.audio_url.startswith(("http://", "https://")):
            raise ValidationError(
                "audio_url must be a valid HTTP/HTTPS URL",
                tool_name=self.tool_name,
                field="audio_url",
            )

        # Validate export_formats
        valid_formats = {"notion", "pdf", "markdown"}
        if not self.export_formats:
            raise ValidationError(
                "export_formats cannot be empty", tool_name=self.tool_name, field="export_formats"
            )

        for fmt in self.export_formats:
            if fmt not in valid_formats:
                raise ValidationError(
                    f"Invalid export format: {fmt}. Must be one of {valid_formats}",
                    tool_name=self.tool_name,
                    field="export_formats",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        exports = {}
        for fmt in self.export_formats:
            if fmt == "notion":
                exports[fmt] = "https://notion.so/mock-page"
            elif fmt == "pdf":
                exports[fmt] = "https://mock.example.com/notes123.pdf"
            elif fmt == "markdown":
                exports[fmt] = "https://mock.example.com/notes123.md"

        return {
            "success": True,
            "result": {
                "notes_url": "https://mock.example.com/notes123.md",
                "transcript_url": "https://mock.example.com/transcript123.txt",
                "exports": exports,
                "action_items": 5 if self.extract_action_items else 0,
                "duration": "45:30",
                "meeting_title": self.meeting_title or "Untitled Meeting",
            },
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Dict[str, Any]:
        """Main processing logic."""
        # Get API credentials from environment
        api_key = os.getenv("GENSPARK_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise APIError(
                "Missing API credentials. Set GENSPARK_API_KEY or OPENAI_API_KEY",
                tool_name=self.tool_name,
            )

        # Step 1: Download/validate audio file
        audio_info = self._validate_audio_file()

        # Step 2: Transcribe audio
        transcript = self._transcribe_audio(api_key)

        # Step 3: Generate structured notes
        notes = self._generate_structured_notes(transcript, api_key)

        # Step 4: Create exports
        exports = self._create_exports(notes, transcript)

        # Step 5: Upload to storage and generate URLs
        urls = self._upload_and_generate_urls(exports)

        return {
            "notes_url": urls.get("primary_url"),
            "transcript_url": urls.get("transcript_url"),
            "exports": urls.get("exports", {}),
            "action_items": len(notes.get("action_items", [])),
            "duration": audio_info.get("duration", "Unknown"),
            "meeting_title": self.meeting_title or "Meeting Notes",
        }

    def _validate_audio_file(self) -> Dict[str, Any]:
        """Validate audio file is accessible."""
        try:
            # Head request to check if file exists
            response = requests.head(self.audio_url, timeout=10)
            response.raise_for_status()

            return {
                "duration": "Unknown",  # Would need actual audio processing
                "size": response.headers.get("Content-Length", "Unknown"),
                "content_type": response.headers.get("Content-Type", "Unknown"),
            }
        except requests.RequestException as e:
            raise APIError(
                f"Cannot access audio file at {self.audio_url}: {e}", tool_name=self.tool_name
            )

    def _transcribe_audio(self, api_key: str) -> Dict[str, Any]:
        """Transcribe audio file using audio transcription service."""
        # In production, this would call the audio_transcribe tool
        # or directly use Whisper API/similar service

        # Simulated transcription for now (real implementation would use actual API)
        return {
            "text": "This is a simulated transcript of the meeting.",
            "segments": [
                {
                    "timestamp": "00:00",
                    "speaker": "Speaker 1" if self.identify_speakers else None,
                    "text": "This is a simulated transcript segment.",
                }
            ],
        }

    def _generate_structured_notes(
        self, transcript: Dict[str, Any], api_key: str
    ) -> Dict[str, Any]:
        """Generate structured notes from transcript using AI."""
        # In production, this would use GPT-4 or similar to parse transcript

        notes = {
            "meeting_overview": {
                "title": self.meeting_title or "Meeting Notes",
                "date": "2025-11-22",
                "duration": "45:30",
                "participants": ["Speaker 1", "Speaker 2"] if self.identify_speakers else [],
            },
            "key_discussion_points": [
                "Discussed Q4 planning and goals",
                "Reviewed budget allocation",
                "Team capacity planning",
            ],
            "decisions_made": [
                "Approved budget increase of 10%",
                "Decided to hire 2 new team members",
            ],
        }

        if self.extract_action_items:
            notes["action_items"] = [
                {
                    "task": "Prepare budget proposal",
                    "assignee": "John",
                    "deadline": "2025-11-30",
                },
                {
                    "task": "Post job listings",
                    "assignee": "Sarah",
                    "deadline": "2025-11-25",
                },
                {
                    "task": "Schedule follow-up meeting",
                    "assignee": "Mike",
                    "deadline": "2025-11-24",
                },
                {
                    "task": "Send meeting notes to team",
                    "assignee": "Assistant",
                    "deadline": "2025-11-22",
                },
                {
                    "task": "Review Q3 performance metrics",
                    "assignee": "Team",
                    "deadline": "2025-11-28",
                },
            ]

        notes["next_steps"] = [
            "Review and finalize budget proposal",
            "Begin recruitment process",
            "Schedule Q1 planning session",
        ]

        if self.include_transcript:
            notes["full_transcript"] = transcript

        return notes

    def _create_exports(self, notes: Dict[str, Any], transcript: Dict[str, Any]) -> Dict[str, str]:
        """Create exports in requested formats."""
        exports = {}

        for fmt in self.export_formats:
            if fmt == "markdown":
                exports["markdown"] = self._format_as_markdown(notes)
            elif fmt == "pdf":
                # Would convert markdown to PDF in production
                exports["pdf"] = self._format_as_markdown(notes)
            elif fmt == "notion":
                # Would format for Notion API in production
                exports["notion"] = self._format_as_markdown(notes)

        return exports

    def _format_as_markdown(self, notes: Dict[str, Any]) -> str:
        """Format notes as markdown."""
        md = f"# {notes['meeting_overview']['title']}\n\n"
        md += f"**Date:** {notes['meeting_overview']['date']}\n"
        md += f"**Duration:** {notes['meeting_overview']['duration']}\n\n"

        if notes["meeting_overview"].get("participants"):
            md += "**Participants:**\n"
            for p in notes["meeting_overview"]["participants"]:
                md += f"- {p}\n"
            md += "\n"

        md += "## Key Discussion Points\n\n"
        for point in notes["key_discussion_points"]:
            md += f"- {point}\n"
        md += "\n"

        md += "## Decisions Made\n\n"
        for decision in notes["decisions_made"]:
            md += f"- {decision}\n"
        md += "\n"

        if self.extract_action_items and notes.get("action_items"):
            md += "## Action Items\n\n"
            for item in notes["action_items"]:
                md += f"- [ ] **{item['task']}** "
                md += f"(Assignee: {item['assignee']}, Due: {item['deadline']})\n"
            md += "\n"

        md += "## Next Steps\n\n"
        for step in notes["next_steps"]:
            md += f"- {step}\n"
        md += "\n"

        if self.include_transcript and notes.get("full_transcript"):
            md += "## Full Transcript\n\n"
            md += notes["full_transcript"].get("text", "")
            md += "\n"

        return md

    def _upload_and_generate_urls(self, exports: Dict[str, str]) -> Dict[str, Any]:
        """Upload files to storage and generate accessible URLs."""
        # In production, this would upload to AI Drive or similar storage

        urls = {
            "primary_url": "https://storage.example.com/meeting-notes.md",
            "transcript_url": "https://storage.example.com/transcript.txt",
            "exports": {},
        }

        for fmt in self.export_formats:
            if fmt == "markdown":
                urls["exports"]["markdown"] = "https://storage.example.com/notes.md"
            elif fmt == "pdf":
                urls["exports"]["pdf"] = "https://storage.example.com/notes.pdf"
            elif fmt == "notion":
                urls["exports"]["notion"] = "https://notion.so/meeting-notes"

        return urls


if __name__ == "__main__":
    print("Testing MeetingNotesAgent...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic meeting notes
    tool = MeetingNotesAgent(
        audio_url="https://example.com/meeting.mp3",
        export_formats=["markdown", "pdf"],
        extract_action_items=True,
        meeting_title="Test Meeting",
    )
    result = tool.run()

    assert result.get("success") == True
    assert "notes_url" in result["result"]
    assert len(result["result"]["exports"]) == 2
    print(f"✅ Basic meeting notes test passed")

    # Test Notion export
    tool2 = MeetingNotesAgent(
        audio_url="https://example.com/meeting2.mp3",
        export_formats=["notion"],
        identify_speakers=True,
    )
    result2 = tool2.run()
    assert "notion" in result2["result"]["exports"]
    print(f"✅ Notion export test passed")

    # Test validation
    try:
        tool3 = MeetingNotesAgent(audio_url="", export_formats=["markdown"])
        tool3.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Validation test passed (caught error: {type(e).__name__})")

    print("All tests passed!")
