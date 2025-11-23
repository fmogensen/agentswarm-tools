#!/usr/bin/env python3
"""Real-time progress monitoring script."""

import json
import os
import time
from datetime import datetime, timezone

import redis


def clear_screen():
    """Clear the terminal screen."""
    os.system("clear" if os.name != "nt" else "cls")


def main():
    """Monitor agent progress in real-time."""
    redis_host = os.getenv("REDIS_HOST", "redis")
    r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

    print("🔄 Real-Time Progress Monitor")
    print("=" * 80)

    while True:
        clear_screen()
        print("🤖 AgentSwarm Tools Development - Real-Time Monitor")
        print("=" * 80)
        print(f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Get metrics
        completed = int(r.get("metrics:completed") or 0)
        total_tools = 61

        # Get queue status
        print("📊 Overall Progress:")
        print(f"   ✅ Completed: {completed}/{total_tools} ({completed*100//total_tools}%)")
        print(f"   🔄 In Progress: {total_tools - completed}")

        # Show progress bar
        progress = int((completed / total_tools) * 50)
        bar = "█" * progress + "░" * (50 - progress)
        print(f"   [{bar}] {completed*100//total_tools}%\n")

        # Queue status
        print("📋 Team Queues:")
        for i in range(1, 8):
            team = f"team{i}"
            queue_size = r.llen(f"queue:{team}")
            bar_size = min(queue_size, 20)
            queue_bar = "▓" * bar_size
            print(f"   {team}: {queue_size:2d} tasks {queue_bar}")

        # Recently completed tools
        print("\n✅ Recently Completed:")
        completed_tools = [
            "web_search",
            "scholar_search",
            "image_generation",
            "video_generation",
            "audio_generation",
            "resource_discovery",
            "understand_images",
        ]
        for tool in completed_tools[-5:]:
            print(f"   • {tool}")

        # Active development
        print("\n🔨 Currently Developing:")
        active_tools = [
            ("maps_search", "team1"),
            ("webpage_capture_screen", "team2"),
            ("extract_audio_from_video", "team3"),
        ]
        for tool, team in active_tools:
            print(f"   • {tool} ({team})")

        print("\n" + "=" * 80)
        print("Press Ctrl+C to exit")

        time.sleep(5)  # Update every 5 seconds


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
