# Documentation Navigation Guide

## 📚 Complete Documentation Structure

This repository contains **77 documentation files** organized in 3 tiers for easy navigation.

---

## 🎯 Quick Start

### Looking for a specific tool?
→ Start with **[TOOLS_INDEX.md](TOOLS_INDEX.md)** - Alphabetical listing with one-line descriptions

### Need technical details?
→ Read **[TOOLS_DOCUMENTATION.md](TOOLS_DOCUMENTATION.md)** - Complete reference (36KB)

### Want usage examples?
→ Check **[TOOL_EXAMPLES.md](TOOL_EXAMPLES.md)** - Real-world samples (23KB)

---

## 📂 Documentation Hierarchy

```
agentswarm-tools/
│
├── 📄 TOOLS_INDEX.md              ← START HERE for quick lookup
├── 📄 TOOLS_DOCUMENTATION.md      ← Complete technical reference
├── 📄 TOOL_EXAMPLES.md            ← Real-world usage examples
│
└── tools/
    ├── search/
    │   ├── 📄 README.md           ← Category overview (8 tools)
    │   ├── web_search/
    │   │   └── 📄 README.md       ← Individual tool docs
    │   ├── scholar_search/
    │   │   └── 📄 README.md
    │   └── ...
    │
    ├── visualization/
    │   ├── 📄 README.md           ← Category overview (15 tools)
    │   ├── generate_line_chart/
    │   │   └── 📄 README.md
    │   └── ...
    │
    └── ... (13 categories total)
```

---

## 🗂️ All 13 Categories

1. **[Search & Information](tools/search/README.md)** (8 tools)
   - web_search, scholar_search, image_search, video_search, product_search, google_product_search, financial_report, stock_price

2. **[Web Content & Data](tools/web_content/README.md)** (4 tools) + **[Web](tools/web/README.md)** (1 tool)
   - crawler, summarize_large_document, url_metadata, webpage_capture_screen, resource_discovery

3. **[Media Generation](tools/media_generation/README.md)** (3 tools)
   - image_generation, video_generation, audio_generation

4. **[Media Analysis](tools/media_analysis/README.md)** (7 tools)
   - understand_images, understand_video, batch_understand_videos, analyze_media_content, audio_transcribe, merge_audio, extract_audio_from_video

5. **[Storage & Files](tools/storage/README.md)** (4 tools)
   - aidrive_tool, file_format_converter, onedrive_search, onedrive_file_read

6. **[Communication](tools/communication/README.md)** (8 tools)
   - gmail_search, gmail_read, read_email_attachments, email_draft, google_calendar_list, google_calendar_create_event_draft, phone_call, query_call_logs

7. **[Visualization](tools/visualization/README.md)** (15 tools)
   - All chart generation tools (line, bar, pie, scatter, area, column, dual_axes, fishbone, flow, histogram, mind_map, network_graph, radar, treemap, word_cloud)

8. **[Location Services](tools/location/README.md)** (1 tool)
   - maps_search

9. **[Code Execution](tools/code_execution/README.md)** (5 tools)
   - bash_tool, read_tool, write_tool, multiedit_tool, downloadfilewrapper_tool

10. **[Document Creation](tools/document_creation/README.md)** (1 tool)
    - create_agent

11. **[Workspace Integration](tools/workspace/README.md)** (2 tools)
    - notion_search, notion_read

12. **[Utilities](tools/utils/README.md)** (2 tools)
    - think, ask_for_clarification

---

## 🔍 Finding Documentation

### By Tool Name
1. Check **TOOLS_INDEX.md** for alphabetical listing
2. Navigate to `tools/{category}/{tool_name}/README.md`

### By Category
1. Browse category list above
2. Read category README for overview
3. Explore individual tool READMEs

### By Use Case
1. Read **TOOLS_DOCUMENTATION.md** - organized by category with use cases
2. Check **TOOL_EXAMPLES.md** - real-world scenarios

---

## 📊 Documentation Statistics

- **Root Files**: 3 comprehensive references (48KB total)
- **Category Overviews**: 13 category READMEs
- **Tool Documentation**: 61 individual tool READMEs
- **Total Documentation**: 77 files covering all 101 production tools
- **Lines of Documentation**: 1,539 (technical) + 1,207 (examples) = 2,746+ lines

---

## 🚀 Common Workflows

### "I want to search for something"
→ [tools/search/README.md](tools/search/README.md) → Choose appropriate search tool

### "I need to generate media"
→ [tools/media_generation/README.md](tools/media_generation/README.md) → Image, video, or audio

### "I want to create charts"
→ [tools/visualization/README.md](tools/visualization/README.md) → 15 chart types available

### "I need to analyze media"
→ [tools/media_analysis/README.md](tools/media_analysis/README.md) → Images, video, or audio analysis

### "I want to access storage"
→ [tools/storage/README.md](tools/storage/README.md) → AI Drive or OneDrive

---

## ✅ Documentation Quality

Each tool README includes:
- ✅ Clear description and purpose
- ✅ Parameter documentation
- ✅ Return value structure  
- ✅ Usage examples with code
- ✅ Testing instructions
- ✅ Links to comprehensive docs

---

**Last Updated**: 2025-11-20  
**Documentation Version**: 1.0.0  
**Tools Covered**: 61/61 (100%)
