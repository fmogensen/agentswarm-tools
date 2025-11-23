#!/usr/bin/env python3
"""
Accelerate Development - Push high-priority tools to agent teams

This script assigns priority tools to teams via Redis queue.
"""

import json
import os
from datetime import datetime, timezone

import redis

# Priority tools to develop next
PRIORITY_TOOLS = [
    # High-value tools not yet implemented
    ("financial_report", "team1", "search"),
    ("stock_price", "team1", "search"),
    ("crawler", "team2", "web_content"),
    ("summarize_large_document", "team2", "web_content"),
    ("url_metadata", "team2", "web_content"),
    ("webpage_capture_screen", "team2", "web_content"),
    ("understand_video", "team3", "media_analysis"),
    ("batch_understand_videos", "team3", "media_analysis"),
    ("analyze_media_content", "team3", "media_analysis"),
    ("audio_transcribe", "team3", "media_analysis"),
    ("merge_audio", "team3", "media_analysis"),
    ("extract_audio_from_video", "team3", "media_analysis"),
    ("aidrive_tool", "team4", "storage"),
    ("file_format_converter", "team4", "storage"),
    ("onedrive_search", "team4", "storage"),
    ("onedrive_file_read", "team4", "storage"),
]


def main():
    """Push priority tools to Redis queue."""
    redis_host = os.getenv("REDIS_HOST", "redis")
    r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

    print("🚀 Accelerating Tool Development")
    print(f"📋 Pushing {len(PRIORITY_TOOLS)} priority tools to queue...")

    for tool_name, team, category in PRIORITY_TOOLS:
        task = {
            "tool_name": tool_name,
            "team": team,
            "category": category,
            "status": "queued",
            "priority": "high",
            "assigned_at": datetime.now(timezone.utc).isoformat(),
        }

        # Push to team-specific queue
        queue_key = f"queue:{team}"
        r.lpush(queue_key, json.dumps(task))

        # Set tool status
        r.hset(f"tool:{tool_name}", "status", "queued")
        r.hset(f"tool:{tool_name}", "team", team)
        r.hset(f"tool:{tool_name}", "queued_at", task["assigned_at"])

        print(f"  ✅ {tool_name} → {team} ({category})")

    # Update metrics
    r.set("metrics:last_queue_push", datetime.now(timezone.utc).isoformat())
    r.incr("metrics:total_tasks_queued", len(PRIORITY_TOOLS))

    print(f"\n✅ Successfully queued {len(PRIORITY_TOOLS)} tools!")
    print("🔄 Agent teams will pick up tasks automatically...")

    # Show queue sizes
    print("\n📊 Queue Status:")
    for i in range(1, 8):
        team = f"team{i}"
        queue_size = r.llen(f"queue:{team}")
        print(f"   {team}: {queue_size} tasks")


if __name__ == "__main__":
    main()
