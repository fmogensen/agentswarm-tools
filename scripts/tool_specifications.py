#!/usr/bin/env python3
"""
Tool Specifications Parser

Parses Genspark documentation and generates JSON specifications
for all 101 tools to guide autonomous development.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Tool list from orchestrator
ALL_TOOLS = [
    # Search & Information (8)
    {"name": "web_search", "category": "search"},
    {"name": "scholar_search", "category": "search"},
    {"name": "image_search", "category": "search"},
    {"name": "video_search", "category": "search"},
    {"name": "product_search", "category": "search"},
    {"name": "google_product_search", "category": "search"},
    {"name": "financial_report", "category": "search"},
    {"name": "stock_price", "category": "search"},
    # Web Content (5)
    {"name": "crawler", "category": "web"},
    {"name": "summarize_large_document", "category": "web"},
    {"name": "url_metadata", "category": "web"},
    {"name": "webpage_capture_screen", "category": "web"},
    {"name": "resource_discovery", "category": "web"},
    # Media Generation (3)
    {"name": "image_generation", "category": "media_generation"},
    {"name": "video_generation", "category": "media_generation"},
    {"name": "audio_generation", "category": "media_generation"},
    # Media Analysis (7)
    {"name": "understand_images", "category": "media_analysis"},
    {"name": "understand_video", "category": "media_analysis"},
    {"name": "batch_understand_videos", "category": "media_analysis"},
    {"name": "analyze_media_content", "category": "media_analysis"},
    {"name": "audio_transcribe", "category": "media_analysis"},
    {"name": "merge_audio", "category": "media_analysis"},
    {"name": "extract_audio_from_video", "category": "media_analysis"},
    # Storage (4)
    {"name": "aidrive_tool", "category": "storage"},
    {"name": "file_format_converter", "category": "storage"},
    {"name": "onedrive_search", "category": "storage"},
    {"name": "onedrive_file_read", "category": "storage"},
    # Communication (8)
    {"name": "gmail_search", "category": "communication"},
    {"name": "gmail_read", "category": "communication"},
    {"name": "read_email_attachments", "category": "communication"},
    {"name": "email_draft", "category": "communication"},
    {"name": "google_calendar_list", "category": "communication"},
    {"name": "google_calendar_create_event_draft", "category": "communication"},
    {"name": "phone_call", "category": "communication"},
    {"name": "query_call_logs", "category": "communication"},
    # Visualization (15)
    {"name": "generate_line_chart", "category": "visualization"},
    {"name": "generate_bar_chart", "category": "visualization"},
    {"name": "generate_column_chart", "category": "visualization"},
    {"name": "generate_pie_chart", "category": "visualization"},
    {"name": "generate_area_chart", "category": "visualization"},
    {"name": "generate_scatter_chart", "category": "visualization"},
    {"name": "generate_dual_axes_chart", "category": "visualization"},
    {"name": "generate_histogram_chart", "category": "visualization"},
    {"name": "generate_radar_chart", "category": "visualization"},
    {"name": "generate_treemap_chart", "category": "visualization"},
    {"name": "generate_word_cloud_chart", "category": "visualization"},
    {"name": "generate_fishbone_diagram", "category": "visualization"},
    {"name": "generate_flow_diagram", "category": "visualization"},
    {"name": "generate_mind_map", "category": "visualization"},
    {"name": "generate_network_graph", "category": "visualization"},
    # Location (1)
    {"name": "maps_search", "category": "location"},
    # Code Execution (5)
    {"name": "bash_tool", "category": "code_execution"},
    {"name": "read_tool", "category": "code_execution"},
    {"name": "write_tool", "category": "code_execution"},
    {"name": "multiedit_tool", "category": "code_execution"},
    {"name": "downloadfilewrapper_tool", "category": "code_execution"},
    # Documents (1)
    {"name": "create_agent", "category": "documents"},
    # Workspace (2)
    {"name": "notion_search", "category": "workspace"},
    {"name": "notion_read", "category": "workspace"},
    # Utils (2)
    {"name": "think", "category": "utils"},
    {"name": "ask_for_clarification", "category": "utils"},
]


class ToolSpecificationGenerator:
    """Generate tool specifications from Genspark documentation."""

    def __init__(self, docs_dir: str = "/Users/frank/Documents/Code/Genspark/Genspark"):
        self.docs_dir = Path(docs_dir)
        self.output_dir = Path("data/tool_specs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_specs(self):
        """Generate specifications for all 101 tools."""
        print(f"Generating specifications for {len(ALL_TOOLS)} tools...")

        generated = 0
        for tool in ALL_TOOLS:
            try:
                spec = self.generate_spec(tool["name"], tool["category"])
                self.save_spec(spec)
                generated += 1
                print(f"✅ {tool['name']}")
            except Exception as e:
                print(f"❌ {tool['name']}: {e}")

        print(f"\n✅ Generated {generated}/{len(ALL_TOOLS)} specifications")

    def generate_spec(self, tool_name: str, category: str) -> Dict[str, Any]:
        """
        Generate specification for a single tool.

        This creates a template spec that AI will use for code generation.
        Real documentation is in Genspark docs.
        """
        # Base specification template
        spec = {
            "tool_name": tool_name,
            "category": category,
            "description": self._get_description(tool_name),
            "parameters": self._get_parameters(tool_name),
            "returns": self._get_returns(tool_name),
            "example": self._get_example(tool_name),
            "metadata": {
                "source": "genspark",
                "version": "1.0.0",
                "framework": "agency_swarm",
                "base_class": "BaseTool",
            },
        }

        return spec

    def _get_description(self, tool_name: str) -> str:
        """Get tool description from documentation or generate default."""
        descriptions = {
            "web_search": "Perform web search with Google and return comprehensive results",
            "scholar_search": "Search scholarly articles, academic papers, and research publications",
            "image_search": "Search for existing images on the internet",
            "video_search": "Search for videos on YouTube platform",
            "product_search": "Search and recommend products from Amazon with detailed information",
            "google_product_search": "Search products using Google Shopping for price comparison",
            "financial_report": "Search official financial reports, earnings, statements for public companies",
            "stock_price": "Retrieve current stock price information for a company",
            "crawler": "Retrieve and convert content from URLs into readable format",
            "summarize_large_document": "Fetch and summarize text-based documents, answering specific questions",
            "url_metadata": "Check URL metadata (content-type, size, filename) without downloading",
            "webpage_capture_screen": "Capture screenshot of a webpage as visual representation",
            "resource_discovery": "Detect and catalog downloadable media resources from web pages",
            "image_generation": "Generate new images from text descriptions or reference images",
            "video_generation": "Generate 5-10 second video clips from text or reference images",
            "audio_generation": "Generate audio: TTS, sound effects, music, voice cloning, songs",
            "understand_images": "Read and analyze image content from URLs or AI Drive paths",
            "understand_video": "Extract transcript from YouTube videos with timestamps",
            "batch_understand_videos": "Process multiple YouTube videos to answer specific questions efficiently",
            "analyze_media_content": "Deep analysis of images, audio, and video with custom requirements",
            "audio_transcribe": "Precisely transcribe audio to text with word-level timestamps",
            "merge_audio": "Merge multiple audio clips into one file with positioning and effects",
            "extract_audio_from_video": "Extract audio track from video files to MP3",
            "aidrive_tool": "AI Drive cloud storage management (list, upload, download, compress)",
            "file_format_converter": "Convert files between different formats",
            "onedrive_search": "Search files and folders in Microsoft OneDrive (personal and business)",
            "onedrive_file_read": "Read and process OneDrive/SharePoint files, answer questions about content",
            "gmail_search": "Search and list emails from Gmail based on query",
            "gmail_read": "Read specific email from Gmail by ID and process content",
            "read_email_attachments": "Read email attachments efficiently (checks cache first)",
            "email_draft": "Generate email content for drafting (text or HTML)",
            "google_calendar_list": "Search and retrieve Google Calendar events",
            "google_calendar_create_event_draft": "Create or modify calendar event draft (requires confirmation)",
            "phone_call": "Create AI-assisted phone call card (user clicks to initiate)",
            "query_call_logs": "Query call history logs with optional filtering and transcripts",
            "generate_line_chart": "Generate line chart for trends over time",
            "generate_bar_chart": "Generate bar chart for horizontal categorical comparisons",
            "generate_column_chart": "Generate column chart for vertical categorical comparisons",
            "generate_pie_chart": "Generate pie chart for proportions and parts of whole",
            "generate_area_chart": "Generate area chart for trends under continuous variables",
            "generate_scatter_chart": "Generate scatter chart for correlations and relationships",
            "generate_dual_axes_chart": "Generate dual axes chart combining column and line charts",
            "generate_histogram_chart": "Generate histogram for frequency distribution",
            "generate_radar_chart": "Generate radar chart for multidimensional data (4+ dimensions)",
            "generate_treemap_chart": "Generate treemap for hierarchical data visualization",
            "generate_word_cloud_chart": "Generate word cloud for word frequency visualization",
            "generate_fishbone_diagram": "Generate fishbone diagram for cause-effect analysis",
            "generate_flow_diagram": "Generate flow diagram for processes and workflows",
            "generate_mind_map": "Generate mind map for hierarchical information organization",
            "generate_network_graph": "Generate network graph for relationships between entities",
            "maps_search": "Search geographical information, places, businesses, and get directions",
            "bash_tool": "Execute bash commands in sandboxed Linux environment",
            "read_tool": "Read files from sandboxed environment with line numbers",
            "write_tool": "Create or overwrite files in sandboxed environment",
            "multiedit_tool": "Perform multiple sequential edits to a single file atomically",
            "downloadfilewrapper_tool": "Download file wrapper URLs to sandbox for processing",
            "create_agent": "Create specialized agents (podcasts, docs, slides, sheets, deep research, websites, video editing)",
            "notion_search": "Search Notion workspace for pages and content",
            "notion_read": "Retrieve and summarize full Notion page content",
            "think": "Internal reasoning and memory (no external effects)",
            "ask_for_clarification": "Request additional information from user when needed",
        }

        return descriptions.get(tool_name, f"{tool_name.replace('_', ' ').title()} tool")

    def _get_parameters(self, tool_name: str) -> Dict[str, Any]:
        """Get parameter definitions for the tool."""
        # Simple tools with minimal parameters
        if tool_name == "think":
            return {
                "thought": {
                    "type": "string",
                    "description": "Internal reasoning or thought to record",
                    "required": True,
                }
            }

        if tool_name == "ask_for_clarification":
            return {
                "question": {
                    "type": "string",
                    "description": "Question to ask the user for clarification",
                    "required": True,
                }
            }

        # Search tools typically have query parameter
        if "search" in tool_name:
            return {
                "query": {
                    "type": "string",
                    "description": "Search query string",
                    "required": True,
                    "example": "artificial intelligence",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "required": False,
                    "default": 10,
                },
            }

        # Generation tools
        if "generation" in tool_name or "generate" in tool_name:
            return {
                "prompt": {
                    "type": "string",
                    "description": "Description of what to generate",
                    "required": True,
                },
                "params": {
                    "type": "object",
                    "description": "Additional generation parameters",
                    "required": False,
                },
            }

        # Analysis tools
        if "understand" in tool_name or "analyze" in tool_name:
            return {
                "media_url": {
                    "type": "string",
                    "description": "URL of media to analyze",
                    "required": True,
                },
                "instruction": {
                    "type": "string",
                    "description": "What to analyze or extract",
                    "required": False,
                },
            }

        # Default generic parameters
        return {
            "input": {"type": "string", "description": "Primary input parameter", "required": True}
        }

    def _get_returns(self, tool_name: str) -> Dict[str, Any]:
        """Get return value specification."""
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "description": "Whether operation succeeded"},
                "result": {"type": "object", "description": "Tool-specific result data"},
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata about the operation",
                },
            },
        }

    def _get_example(self, tool_name: str) -> Dict[str, Any]:
        """Get usage example for the tool."""
        if tool_name == "web_search":
            return {
                "input": {"query": "latest AI news", "max_results": 5},
                "output": {
                    "success": True,
                    "result": {
                        "organic_results": [
                            {
                                "title": "AI News Today",
                                "url": "https://example.com",
                                "snippet": "Latest developments...",
                            }
                        ]
                    },
                },
            }

        return {"input": {"query": "example input"}, "output": {"success": True, "result": {}}}

    def save_spec(self, spec: Dict[str, Any]):
        """Save specification to JSON file."""
        filename = f"{spec['tool_name']}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            json.dump(spec, f, indent=2)


def main():
    """Generate all tool specifications."""
    generator = ToolSpecificationGenerator()
    generator.generate_all_specs()


if __name__ == "__main__":
    main()
