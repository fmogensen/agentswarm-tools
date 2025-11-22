# AgentSwarm Tools - Development User Stories

**Version**: 1.0
**Date**: November 22, 2025
**Purpose**: Detailed specifications for 100% AI-driven development

---

## Story 1: Office Document Generator (Word .docx)

### Story ID: TOOL-001
### Priority: CRITICAL
### Category: Document Creation
### Estimated Effort: 8 hours

### User Story
As an AI agent, I need to generate professional Word documents (.docx) from structured content so that users can create reports, proposals, memos, and other formatted documents programmatically.

### Acceptance Criteria
- [ ] Tool accepts content, template type, and formatting options
- [ ] Generates .docx files with proper formatting (fonts, spacing, styles)
- [ ] Supports headings, paragraphs, bullet points, tables
- [ ] Optional table of contents generation
- [ ] Export to both .docx and .pdf formats
- [ ] Returns accessible URL to generated document
- [ ] Follows AgentSwarm BaseTool pattern with all 5 required methods
- [ ] Includes test block with USE_MOCK_APIS=true
- [ ] 100% test coverage for core logic
- [ ] No hardcoded secrets (uses environment variables)
- [ ] Comprehensive docstring with examples

### Technical Specifications

**File Location**: `tools/document_creation/office_docs/office_docs.py`

**Dependencies**:
```python
python-docx==1.1.0
PyPDF2==3.0.1
```

**Class Definition**:
```python
class OfficeDocsTool(BaseTool):
    """
    Generate professional Word documents (.docx) from structured content.

    Use this tool to create formatted documents including reports, proposals,
    memos, letters, and other business documents with proper styling.

    Args:
        content: Document content as text or structured data
        template: Template type (report, proposal, memo, letter, blank)
        title: Document title
        include_toc: Whether to include table of contents
        font_name: Font family (Calibri, Arial, Times New Roman)
        font_size: Base font size in points (default: 11)
        output_format: Output format (docx, pdf, both)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: {"document_url": "...", "format": "...", "pages": N}
        - metadata: Tool execution metadata

    Example:
        >>> tool = OfficeDocsTool(
        ...     content="# Report\\n\\nThis is the content...",
        ...     template="report",
        ...     title="Q4 Sales Report",
        ...     include_toc=True
        ... )
        >>> result = tool.run()
        >>> print(result['result']['document_url'])
    """

    # Tool metadata
    tool_name: str = "office_docs"
    tool_category: str = "document_creation"

    # Parameters
    content: str = Field(..., description="Document content (supports markdown)", min_length=1)
    template: str = Field("blank", description="Template type: report, proposal, memo, letter, blank")
    title: str = Field("Untitled Document", description="Document title")
    include_toc: bool = Field(False, description="Include table of contents")
    font_name: str = Field("Calibri", description="Font family")
    font_size: int = Field(11, description="Base font size in points", ge=8, le=24)
    output_format: str = Field("docx", description="Output format: docx, pdf, both")
```

**Required Methods Implementation**:

1. **`_execute()`**: Orchestrate validation, mock check, and processing
2. **`_validate_parameters()`**:
   - Validate template is in allowed list
   - Validate output_format is valid
   - Validate content is not empty
   - Validate font_name is supported

3. **`_should_use_mock()`**: Check USE_MOCK_APIS environment variable

4. **`_generate_mock_results()`**:
   ```python
   return {
       "success": True,
       "result": {
           "document_url": "https://mock.example.com/doc123.docx",
           "format": self.output_format,
           "pages": 5,
           "file_size": "245 KB"
       },
       "metadata": {"mock_mode": True}
   }
   ```

5. **`_process()`**:
   - Parse content (support markdown)
   - Create Document object
   - Apply template styles
   - Add title, headings, paragraphs
   - Add table of contents if requested
   - Save to temporary file
   - Upload to AI Drive or persistent storage
   - Generate accessible URL
   - Return result dict

**Test Block**:
```python
if __name__ == "__main__":
    print("Testing OfficeDocsTool...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic document
    tool = OfficeDocsTool(
        content="# Test Report\n\nThis is a test document.",
        template="report",
        title="Test Document"
    )
    result = tool.run()

    assert result.get('success') == True
    assert 'document_url' in result['result']
    print(f"✅ Basic test passed")

    # Test with table of contents
    tool2 = OfficeDocsTool(
        content="# Chapter 1\n\nContent...\n\n# Chapter 2\n\nMore content...",
        include_toc=True,
        output_format="pdf"
    )
    result2 = tool2.run()
    assert result2.get('success') == True
    print(f"✅ TOC test passed")

    print("All tests passed!")
```

**Environment Variables**:
- `USE_MOCK_APIS`: Enable mock mode for testing
- `AIDRIVE_API_KEY`: For file upload (optional, falls back to temp storage)

**Error Handling**:
- Raise `ValidationError` for invalid templates, formats, or empty content
- Raise `APIError` for file upload failures
- Raise `ConfigurationError` for missing required libraries

**Documentation**:
- Add entry to TOOLS_CATALOG.md
- Add example to TOOL_EXAMPLES.md
- Update TOOLS_INDEX.md

---

## Story 2: Office Presentation Generator (PowerPoint .pptx)

### Story ID: TOOL-002
### Priority: CRITICAL
### Category: Document Creation
### Estimated Effort: 10 hours

### User Story
As an AI agent, I need to generate professional PowerPoint presentations (.pptx) from structured content so that users can create slide decks for business, education, or personal use.

### Acceptance Criteria
- [ ] Tool accepts slides content, theme, and formatting options
- [ ] Generates .pptx files with proper themes and layouts
- [ ] Supports title slides, content slides, bullet points
- [ ] Supports embedding charts and images
- [ ] Export to both .pptx and .pdf formats
- [ ] Returns accessible URL to generated presentation
- [ ] Follows AgentSwarm BaseTool pattern with all 5 required methods
- [ ] Includes test block with USE_MOCK_APIS=true
- [ ] 100% test coverage for core logic
- [ ] No hardcoded secrets
- [ ] Comprehensive docstring

### Technical Specifications

**File Location**: `tools/document_creation/office_slides/office_slides.py`

**Dependencies**:
```python
python-pptx==0.6.21
Pillow==10.1.0
```

**Class Definition**:
```python
class OfficeSlidesTool(BaseTool):
    """
    Generate professional PowerPoint presentations (.pptx) from structured content.

    Use this tool to create formatted slide decks including business presentations,
    educational materials, pitch decks, and reports with proper themes and layouts.

    Args:
        slides: List of slide definitions (each with title, content, layout)
        theme: Presentation theme (modern, classic, minimal, corporate)
        title_slide: Title slide configuration (title, subtitle, author)
        charts: Optional list of chart definitions to embed
        output_format: Output format (pptx, pdf, both)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: {"presentation_url": "...", "format": "...", "slides": N}
        - metadata: Tool execution metadata

    Example:
        >>> tool = OfficeSlidesTool(
        ...     slides=[
        ...         {"title": "Introduction", "content": ["Point 1", "Point 2"], "layout": "title_content"},
        ...         {"title": "Data", "content": ["Analysis"], "layout": "content"}
        ...     ],
        ...     theme="modern",
        ...     title_slide={"title": "Q4 Report", "subtitle": "2025", "author": "John Doe"}
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "office_slides"
    tool_category: str = "document_creation"

    # Parameters
    slides: List[Dict[str, Any]] = Field(..., description="List of slide definitions", min_items=1)
    theme: str = Field("modern", description="Theme: modern, classic, minimal, corporate")
    title_slide: Optional[Dict[str, str]] = Field(None, description="Title slide config")
    charts: Optional[List[Dict[str, Any]]] = Field(None, description="Chart definitions")
    output_format: str = Field("pptx", description="Output format: pptx, pdf, both")
```

**Required Methods**: Same pattern as Story 1

**Mock Results**:
```python
{
    "success": True,
    "result": {
        "presentation_url": "https://mock.example.com/pres123.pptx",
        "format": "pptx",
        "slides": len(self.slides) + (1 if self.title_slide else 0),
        "file_size": "1.2 MB"
    },
    "metadata": {"mock_mode": True}
}
```

**Test Block**:
```python
if __name__ == "__main__":
    print("Testing OfficeSlidesTool...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic presentation
    tool = OfficeSlidesTool(
        slides=[
            {"title": "Slide 1", "content": ["Point A", "Point B"], "layout": "title_content"},
            {"title": "Slide 2", "content": ["Data"], "layout": "content"}
        ],
        theme="modern",
        title_slide={"title": "Test Presentation", "subtitle": "2025"}
    )
    result = tool.run()

    assert result.get('success') == True
    assert result['result']['slides'] == 3  # title + 2 content
    print(f"✅ Basic presentation test passed")

    # Test PDF export
    tool2 = OfficeSlidesTool(
        slides=[{"title": "Test", "content": ["Content"], "layout": "content"}],
        output_format="pdf"
    )
    result2 = tool2.run()
    assert result2['result']['format'] == "pdf"
    print(f"✅ PDF export test passed")

    print("All tests passed!")
```

---

## Story 3: Office Spreadsheet Generator (Excel .xlsx)

### Story ID: TOOL-003
### Priority: CRITICAL
### Category: Document Creation
### Estimated Effort: 10 hours

### User Story
As an AI agent, I need to generate Excel spreadsheets (.xlsx) from structured data so that users can create data tables, reports, and calculations programmatically.

### Acceptance Criteria
- [ ] Tool accepts data, formulas, and formatting options
- [ ] Generates .xlsx files with proper formatting
- [ ] Supports formulas, charts, and cell formatting
- [ ] Multiple worksheet support
- [ ] Export to .xlsx and .csv formats
- [ ] Returns accessible URL
- [ ] Follows AgentSwarm BaseTool pattern
- [ ] Includes test block with mock mode
- [ ] 100% test coverage
- [ ] No hardcoded secrets
- [ ] Comprehensive docstring

### Technical Specifications

**File Location**: `tools/document_creation/office_sheets/office_sheets.py`

**Dependencies**:
```python
openpyxl==3.1.2
pandas==2.1.3
```

**Class Definition**:
```python
class OfficeSheetsTool(BaseTool):
    """
    Generate Excel spreadsheets (.xlsx) from structured data.

    Use this tool to create formatted spreadsheets including data tables,
    financial reports, budgets, and calculations with formulas and charts.

    Args:
        data: List of lists representing rows and columns
        headers: Optional list of column headers
        formulas: Optional dict mapping cell references to formulas
        charts: Optional list of chart definitions
        formatting: Optional dict with cell formatting rules
        worksheets: Optional dict for multiple worksheets
        output_format: Output format (xlsx, csv, both)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: {"spreadsheet_url": "...", "format": "...", "rows": N, "cols": M}
        - metadata: Tool execution metadata

    Example:
        >>> tool = OfficeSheetsTool(
        ...     data=[
        ...         [100, 200, 300],
        ...         [150, 250, 350]
        ...     ],
        ...     headers=["Q1", "Q2", "Q3"],
        ...     formulas={"D1": "=SUM(A1:C1)", "D2": "=SUM(A2:C2)"}
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "office_sheets"
    tool_category: str = "document_creation"

    # Parameters
    data: List[List[Any]] = Field(..., description="Data as list of rows", min_items=1)
    headers: Optional[List[str]] = Field(None, description="Column headers")
    formulas: Optional[Dict[str, str]] = Field(None, description="Cell formulas (e.g., {'A1': '=SUM(B1:B10)'})")
    charts: Optional[List[Dict[str, Any]]] = Field(None, description="Chart definitions")
    formatting: Optional[Dict[str, Any]] = Field(None, description="Cell formatting rules")
    worksheets: Optional[Dict[str, List[List[Any]]]] = Field(None, description="Multiple worksheets")
    output_format: str = Field("xlsx", description="Output format: xlsx, csv, both")
```

**Test Block**:
```python
if __name__ == "__main__":
    print("Testing OfficeSheetsTool...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic spreadsheet
    tool = OfficeSheetsTool(
        data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        headers=["A", "B", "C"],
        formulas={"D1": "=SUM(A1:C1)"}
    )
    result = tool.run()

    assert result.get('success') == True
    assert result['result']['rows'] == 3
    assert result['result']['cols'] == 3
    print(f"✅ Basic spreadsheet test passed")

    # Test CSV export
    tool2 = OfficeSheetsTool(
        data=[[1, 2], [3, 4]],
        output_format="csv"
    )
    result2 = tool2.run()
    assert result2['result']['format'] == "csv"
    print(f"✅ CSV export test passed")

    print("All tests passed!")
```

---

## Story 4: Meeting Notes Agent

### Story ID: TOOL-004
### Priority: HIGH
### Category: Communication
### Estimated Effort: 12 hours

### User Story
As an AI agent, I need to transcribe meeting recordings and generate structured notes so that users can capture meeting content, action items, and key decisions efficiently.

### Acceptance Criteria
- [ ] Tool accepts audio URL and processing options
- [ ] Transcribes audio with timestamps
- [ ] Generates structured notes with sections
- [ ] Extracts action items and key points
- [ ] Identifies speakers (if enabled)
- [ ] Exports to Notion, PDF, and Markdown
- [ ] Follows AgentSwarm BaseTool pattern
- [ ] Includes test block with mock mode
- [ ] 100% test coverage
- [ ] No hardcoded secrets

### Technical Specifications

**File Location**: `tools/communication/meeting_notes/meeting_notes.py`

**Dependencies**:
```python
requests==2.31.0
notion-client==2.2.1  # For Notion export
```

**Class Definition**:
```python
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
    export_formats: List[str] = Field(["markdown"], description="Export formats: notion, pdf, markdown")
    include_transcript: bool = Field(True, description="Include full transcript")
    extract_action_items: bool = Field(True, description="Extract action items")
    identify_speakers: bool = Field(False, description="Identify different speakers")
    meeting_title: Optional[str] = Field(None, description="Meeting title")
```

**Processing Logic**:
1. Download/access audio file
2. Call existing `audio_transcribe` tool for transcription
3. Use AI to parse transcript into structured sections:
   - Meeting Overview
   - Key Discussion Points
   - Decisions Made
   - Action Items (who, what, when)
   - Next Steps
4. Generate exports in requested formats
5. Upload to AI Drive
6. Return URLs

**Mock Results**:
```python
{
    "success": True,
    "result": {
        "notes_url": "https://mock.example.com/notes123.md",
        "transcript_url": "https://mock.example.com/transcript123.txt",
        "exports": {
            "notion": "https://notion.so/mock-page",
            "pdf": "https://mock.example.com/notes123.pdf",
            "markdown": "https://mock.example.com/notes123.md"
        },
        "action_items": 5,
        "duration": "45:30"
    },
    "metadata": {"mock_mode": True}
}
```

**Test Block**:
```python
if __name__ == "__main__":
    print("Testing MeetingNotesAgent...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic meeting notes
    tool = MeetingNotesAgent(
        audio_url="https://example.com/meeting.mp3",
        export_formats=["markdown", "pdf"],
        extract_action_items=True,
        meeting_title="Test Meeting"
    )
    result = tool.run()

    assert result.get('success') == True
    assert 'notes_url' in result['result']
    assert len(result['result']['exports']) == 2
    print(f"✅ Basic meeting notes test passed")

    # Test Notion export
    tool2 = MeetingNotesAgent(
        audio_url="https://example.com/meeting2.mp3",
        export_formats=["notion"],
        identify_speakers=True
    )
    result2 = tool2.run()
    assert 'notion' in result2['result']['exports']
    print(f"✅ Notion export test passed")

    print("All tests passed!")
```

---

## Story 5: Photo Editor Tool

### Story ID: TOOL-005
### Priority: MEDIUM
### Category: Media Processing
### Estimated Effort: 8 hours

### User Story
As an AI agent, I need to perform advanced photo editing operations (not just generation) so that users can enhance, modify, and process existing images.

### Acceptance Criteria
- [ ] Tool accepts image URL and editing operations
- [ ] Supports resize, crop, rotate, flip
- [ ] Supports filters (brightness, contrast, saturation, blur, sharpen)
- [ ] Supports background removal
- [ ] Supports overlays and watermarks
- [ ] Returns edited image URL
- [ ] Follows AgentSwarm BaseTool pattern
- [ ] Includes test block
- [ ] 100% test coverage
- [ ] No hardcoded secrets

### Technical Specifications

**File Location**: `tools/media_processing/photo_editor/photo_editor.py`

**Dependencies**:
```python
Pillow==10.1.0
opencv-python==4.8.1.78
```

**Class Definition**:
```python
class PhotoEditorTool(BaseTool):
    """
    Perform advanced photo editing operations on existing images.

    Use this tool to enhance, modify, and process images including resize,
    crop, filters, background removal, and overlays.

    Args:
        image_url: URL to source image
        operations: List of editing operations to apply
        output_format: Output format (png, jpg, webp)
        quality: Output quality 1-100 (for jpg)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: {"edited_image_url": "...", "format": "...", "size": "..."}
        - metadata: Processing metadata

    Example:
        >>> tool = PhotoEditorTool(
        ...     image_url="https://example.com/photo.jpg",
        ...     operations=[
        ...         {"type": "resize", "width": 800, "height": 600},
        ...         {"type": "filter", "name": "brightness", "value": 1.2},
        ...         {"type": "filter", "name": "contrast", "value": 1.1}
        ...     ],
        ...     output_format="jpg",
        ...     quality=90
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "photo_editor"
    tool_category: str = "media_processing"

    # Parameters
    image_url: str = Field(..., description="URL to source image")
    operations: List[Dict[str, Any]] = Field(..., description="List of editing operations", min_items=1)
    output_format: str = Field("png", description="Output format: png, jpg, webp")
    quality: int = Field(90, description="Output quality 1-100 (jpg only)", ge=1, le=100)
```

**Supported Operations**:
- resize: `{"type": "resize", "width": 800, "height": 600}`
- crop: `{"type": "crop", "x": 0, "y": 0, "width": 500, "height": 500}`
- rotate: `{"type": "rotate", "degrees": 90}`
- flip: `{"type": "flip", "direction": "horizontal"}`
- brightness: `{"type": "filter", "name": "brightness", "value": 1.2}`
- contrast: `{"type": "filter", "name": "contrast", "value": 1.1}`
- saturation: `{"type": "filter", "name": "saturation", "value": 1.3}`
- blur: `{"type": "filter", "name": "blur", "radius": 5}`
- sharpen: `{"type": "filter", "name": "sharpen", "amount": 1.5}`
- background_remove: `{"type": "background_remove"}`

---

## Development Guidelines for AI Agents

### Code Quality Checklist
- [ ] Inherits from `BaseTool` (from `shared.base`)
- [ ] All 5 required methods implemented (`_execute`, `_validate_parameters`, `_should_use_mock`, `_generate_mock_results`, `_process`)
- [ ] Pydantic `Field()` with descriptions for all parameters
- [ ] Comprehensive docstring with Args, Returns, Example
- [ ] No hardcoded secrets - use `os.getenv()`
- [ ] Custom exceptions from `shared.errors` (ValidationError, APIError, etc.)
- [ ] Test block at end with `if __name__ == "__main__":`
- [ ] Mock mode support via `USE_MOCK_APIS=true`
- [ ] Type hints on all methods
- [ ] Error handling with try/except blocks

### Testing Checklist
- [ ] Test file created: `test_{tool_name}.py`
- [ ] Test basic functionality with mock mode
- [ ] Test parameter validation (invalid inputs should raise ValidationError)
- [ ] Test error handling (API failures, timeouts)
- [ ] Test mock mode explicitly
- [ ] All tests pass with `pytest`
- [ ] Coverage >90% with `pytest --cov`

### Documentation Checklist
- [ ] Tool added to `TOOLS_CATALOG.md`
- [ ] Example added to `TOOL_EXAMPLES.md`
- [ ] Tool indexed in `TOOLS_INDEX.md`
- [ ] Environment variables documented (if any)
- [ ] Integration examples provided

### Security Checklist
- [ ] No `.env` file committed
- [ ] No hardcoded API keys or secrets
- [ ] All secrets via `os.getenv()`
- [ ] Validate API keys exist before use
- [ ] Input validation prevents injection attacks
- [ ] File paths validated (no directory traversal)

### File Structure
```
tools/
└── {category}/
    └── {tool_name}/
        ├── __init__.py
        ├── {tool_name}.py       # Main tool implementation
        └── test_{tool_name}.py  # Unit tests
```

### Environment Variables Pattern
```python
# CORRECT - Always use this pattern
api_key = os.getenv("MY_API_KEY")
if not api_key:
    raise APIError(
        "Missing MY_API_KEY environment variable",
        tool_name=self.tool_name
    )

# WRONG - Never do this
api_key = "hardcoded_secret_here"  # ❌ Will fail security audit
```

### Mock Mode Pattern
```python
def _should_use_mock(self) -> bool:
    """Check if mock mode enabled."""
    return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

def _generate_mock_results(self) -> Dict[str, Any]:
    """Generate realistic mock results."""
    return {
        "success": True,
        "result": {
            # Return realistic sample data
            "data": "mock_value"
        },
        "metadata": {"mock_mode": True}
    }
```

---

## Remaining Stories (Brief Outline)

### Story 6: Video Editor Tool (TOOL-006)
- **Category**: Media Processing
- **Priority**: MEDIUM
- **Effort**: 10 hours
- **Dependencies**: FFmpeg wrapper, moviepy
- **Operations**: trim, merge, add_audio, add_subtitles, transitions, effects

### Story 7: Fact Checker Tool (TOOL-007)
- **Category**: Utilities
- **Priority**: MEDIUM
- **Effort**: 8 hours
- **Dependencies**: web_search, scholar_search
- **Features**: Verify claims, find sources, confidence scoring

### Story 8: Translation Tool (TOOL-008)
- **Category**: Utilities
- **Priority**: LOW
- **Effort**: 6 hours
- **Dependencies**: Google Translate API or DeepL
- **Features**: Multi-language support, batch translation, format preservation

---

## Success Criteria for All Stories

Each story is complete when:
1. ✅ Code passes all tests (`pytest`)
2. ✅ Test coverage >90% (`pytest --cov`)
3. ✅ Security audit passes (no hardcoded secrets)
4. ✅ Documentation complete (catalog, examples, index)
5. ✅ Mock mode works (`USE_MOCK_APIS=true`)
6. ✅ Follows AgentSwarm BaseTool pattern 100%
7. ✅ Code review approved
8. ✅ Integration test passes

---

**End of User Stories**
