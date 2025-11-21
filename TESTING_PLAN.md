# Comprehensive Tool Testing Plan

## Overview
Testing all 61 tools in the AgentSwarm Tools Framework with live API keys where required.

## API Keys Required

### ✅ Already Have
- **NOTION_API_KEY** - Tested and working
  - notion_search ✅
  - notion_read ✅

### 🔑 Need to Provide

#### Search Tools (4 keys)
1. **SERPAPI_KEY** - For image_search
2. **YOUTUBE_API_KEY** - For video_search
3. **GOOGLE_SHOPPING_API_KEY** + **GOOGLE_SHOPPING_ENGINE_ID** - For google_product_search
4. **AMAZON_API_KEY** - For product_search

#### Communication Tools (2-3 keys)
5. **GOOGLE_SERVICE_ACCOUNT_FILE** or **GOOGLE_SERVICE_ACCOUNT_JSON** - For gmail_search, gmail_read
6. **GOOGLE_CALENDAR_SERVICE_ACCOUNT_FILE** - For google_calendar_list, google_calendar_create_event_draft

#### Storage Tools (1 key)
7. **MS_GRAPH_TOKEN** - For onedrive_search, onedrive_file_read

## Testing Categories

### Category 1: Search & Information (8 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| web_search | None (uses mock) | 🟡 Ready to test |
| scholar_search | None (uses mock) | 🟡 Ready to test |
| image_search | SERPAPI_KEY | 🔴 Need key |
| video_search | YOUTUBE_API_KEY | 🔴 Need key |
| product_search | AMAZON_API_KEY | 🔴 Need key |
| google_product_search | GOOGLE_SHOPPING_API_KEY | 🔴 Need key |
| financial_report | None (uses mock) | 🟡 Ready to test |
| stock_price | None (uses mock) | 🟡 Ready to test |

### Category 2: Web Content & Data (5 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| crawler | None | 🟢 Ready to test |
| summarize_large_document | None | 🟢 Ready to test |
| url_metadata | None | 🟢 Ready to test |
| webpage_capture_screen | None | 🟢 Ready to test |
| resource_discovery | None | 🟢 Ready to test |

### Category 3: Media Generation (3 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| image_generation | Platform API | 🟠 Platform test |
| video_generation | Platform API | 🟠 Platform test |
| audio_generation | Platform API | 🟠 Platform test |

### Category 4: Media Analysis (7 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| understand_images | Platform API | 🟠 Platform test |
| understand_video | Platform API | 🟠 Platform test |
| batch_understand_videos | Platform API | 🟠 Platform test |
| analyze_media_content | Platform API | 🟠 Platform test |
| audio_transcribe | Platform API | 🟠 Platform test |
| merge_audio | Platform API | 🟠 Platform test |
| extract_audio_from_video | Platform API | 🟠 Platform test |

### Category 5: Storage & Files (4 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| aidrive_tool | Platform storage | 🟠 Platform test |
| file_format_converter | Platform API | 🟠 Platform test |
| onedrive_search | MS_GRAPH_TOKEN | 🔴 Need key |
| onedrive_file_read | MS_GRAPH_TOKEN | 🔴 Need key |

### Category 6: Communication (8 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| gmail_search | GOOGLE_SERVICE_ACCOUNT | 🔴 Need key |
| gmail_read | GOOGLE_SERVICE_ACCOUNT | 🔴 Need key |
| read_email_attachments | GOOGLE_SERVICE_ACCOUNT | 🔴 Need key |
| email_draft | GOOGLE_SERVICE_ACCOUNT | 🔴 Need key |
| google_calendar_list | GOOGLE_CALENDAR_SA | 🔴 Need key |
| google_calendar_create_event_draft | GOOGLE_CALENDAR_SA | 🔴 Need key |
| phone_call | Platform API | 🟠 Platform test |
| query_call_logs | Platform API | 🟠 Platform test |

### Category 7: Visualization (15 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| generate_line_chart | Chart Server MCP | 🟢 Ready to test |
| generate_bar_chart | Chart Server MCP | 🟢 Ready to test |
| generate_pie_chart | Chart Server MCP | 🟢 Ready to test |
| generate_scatter_chart | Chart Server MCP | 🟢 Ready to test |
| generate_area_chart | Chart Server MCP | 🟢 Ready to test |
| generate_column_chart | Chart Server MCP | 🟢 Ready to test |
| generate_dual_axes_chart | Chart Server MCP | 🟢 Ready to test |
| generate_fishbone_diagram | Chart Server MCP | 🟢 Ready to test |
| generate_flow_diagram | Chart Server MCP | 🟢 Ready to test |
| generate_histogram_chart | Chart Server MCP | 🟢 Ready to test |
| generate_mind_map | Chart Server MCP | 🟢 Ready to test |
| generate_network_graph | Chart Server MCP | 🟢 Ready to test |
| generate_radar_chart | Chart Server MCP | 🟢 Ready to test |
| generate_treemap_chart | Chart Server MCP | 🟢 Ready to test |
| generate_word_cloud_chart | Chart Server MCP | 🟢 Ready to test |

### Category 8: Location Services (1 tool)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| maps_search | Platform API | 🟠 Platform test |

### Category 9: Code Execution (5 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| bash_tool | None | 🟢 Ready to test |
| read_tool | None | 🟢 Ready to test |
| write_tool | None | 🟢 Ready to test |
| multiedit_tool | None | 🟢 Ready to test |
| downloadfilewrapper_tool | None | 🟢 Ready to test |

### Category 10: Document Creation (1 tool)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| create_agent | Platform API | 🟠 Platform test |

### Category 11: Workspace Integration (2 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| notion_search | NOTION_API_KEY | ✅ TESTED |
| notion_read | NOTION_API_KEY | ✅ TESTED |

### Category 12: Utilities (2 tools)
| Tool | API Key Required | Status |
|------|-----------------|--------|
| think | None | 🟢 Ready to test |
| ask_for_clarification | None | 🟢 Ready to test |

## Testing Summary

### By Key Requirement:
- **✅ Already Tested**: 2 tools (Notion)
- **🟢 No API Key Needed**: 32 tools (can test immediately)
- **🔴 Need External API Key**: 12 tools (need user to provide keys)
- **🟠 Platform API**: 15 tools (need Genspark platform access)

### Total: 61 tools

## Recommended Testing Order

### Phase 1: No API Keys Required (32 tools)
Test these immediately with mock mode or no external dependencies:
1. Web Content tools (5)
2. Visualization tools (15)
3. Code Execution tools (5)
4. Utilities (2)
5. Some Search tools (3: web_search, scholar_search, financial_report, stock_price)

### Phase 2: With User-Provided API Keys (12 tools)
Once keys are provided:
1. Search tools with keys (4)
2. Communication tools (6)
3. Storage tools (2)

### Phase 3: Platform-Dependent (15 tools)
These require Genspark platform integration:
1. Media Generation (3)
2. Media Analysis (7)
3. Document Creation (1)
4. Some Communication tools (2)
5. Location Services (1)
6. Some Storage tools (2)

## API Key Priority

Based on number of tools affected:

1. **HIGH PRIORITY**:
   - GOOGLE_SERVICE_ACCOUNT_FILE (6 communication tools)
   - SERPAPI_KEY (1 tool but commonly available)

2. **MEDIUM PRIORITY**:
   - MS_GRAPH_TOKEN (2 OneDrive tools)
   - YOUTUBE_API_KEY (1 tool)

3. **LOW PRIORITY**:
   - AMAZON_API_KEY (1 tool)
   - GOOGLE_SHOPPING_API_KEY + ENGINE_ID (1 tool)
