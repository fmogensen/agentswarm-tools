#!/usr/bin/env python3
"""Queue all remaining tools to appropriate teams."""

import json
import os
from datetime import datetime, timezone

import redis

# Additional tools for teams 5, 6, 7
MORE_TOOLS = [
    # Team 5 - Visualization (15 chart tools)
    ("generate_line_chart", "team5", "visualization"),
    ("generate_bar_chart", "team5", "visualization"),
    ("generate_column_chart", "team5", "visualization"),
    ("generate_pie_chart", "team5", "visualization"),
    ("generate_area_chart", "team5", "visualization"),
    ("generate_scatter_chart", "team5", "visualization"),
    ("generate_dual_axes_chart", "team5", "visualization"),
    ("generate_histogram_chart", "team5", "visualization"),
    ("generate_radar_chart", "team5", "visualization"),
    ("generate_treemap_chart", "team5", "visualization"),
    ("generate_word_cloud_chart", "team5", "visualization"),
    ("generate_fishbone_diagram", "team5", "visualization"),
    ("generate_flow_diagram", "team5", "visualization"),
    ("generate_mind_map", "team5", "visualization"),
    ("generate_network_graph", "team5", "visualization"),
    # Team 6 - Workspace & Documents
    ("notion_search", "team6", "workspace"),
    ("notion_read", "team6", "workspace"),
    ("create_agent", "team6", "document_creation"),
    # Team 4 - Communication (8 tools)
    ("gmail_search", "team4", "communication"),
    ("gmail_read", "team4", "communication"),
    ("read_email_attachments", "team4", "communication"),
    ("email_draft", "team4", "communication"),
    ("google_calendar_list", "team4", "communication"),
    ("google_calendar_create_event_draft", "team4", "communication"),
    ("phone_call", "team4", "communication"),
    ("query_call_logs", "team4", "communication"),
    # Team 7 - Utils & Code Execution
    ("think", "team7", "utils"),
    ("ask_for_clarification", "team7", "utils"),
    ("bash_tool", "team7", "code_execution"),
    ("read_tool", "team7", "code_execution"),
    ("write_tool", "team7", "code_execution"),
    ("multiedit_tool", "team7", "code_execution"),
    ("downloadfilewrapper_tool", "team7", "code_execution"),
    # Team 1 - Location
    ("maps_search", "team1", "location"),
]


def main():
    """Queue remaining tools."""
    redis_host = os.getenv("REDIS_HOST", "redis")
    r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

    print("🚀 Queueing Remaining Tools")
    print(f"📋 Pushing {len(MORE_TOOLS)} tools to queue...\n")

    for tool_name, team, category in MORE_TOOLS:
        task = {
            "tool_name": tool_name,
            "team": team,
            "category": category,
            "status": "queued",
            "priority": "normal",
            "assigned_at": datetime.now(timezone.utc).isoformat(),
        }

        queue_key = f"queue:{team}"
        r.lpush(queue_key, json.dumps(task))
        r.hset(f"tool:{tool_name}", "status", "queued")
        r.hset(f"tool:{tool_name}", "team", team)
        r.hset(f"tool:{tool_name}", "queued_at", task["assigned_at"])

        print(f"  ✅ {tool_name} → {team} ({category})")

    r.set("metrics:last_queue_push", datetime.now(timezone.utc).isoformat())
    r.incr("metrics:total_tasks_queued", len(MORE_TOOLS))

    print(f"\n✅ Successfully queued {len(MORE_TOOLS)} more tools!")
    print("\n📊 Final Queue Status:")
    total = 0
    for i in range(1, 8):
        team = f"team{i}"
        queue_size = r.llen(f"queue:{team}")
        total += queue_size
        print(f"   {team}: {queue_size} tasks")

    print(f"\n📈 Total tasks queued: {total}")
    print("🤖 All 7 agent teams are now working!")


if __name__ == "__main__":
    main()
