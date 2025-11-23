#!/usr/bin/env python3
"""
Dashboard Server - Web UI for Monitoring

Provides a web interface to monitor autonomous development progress.
Shows real-time metrics, tool status, and system health.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

from aiohttp import web

try:
    import redis.asyncio as redis
except ImportError:
    import redis

    redis.asyncio = redis

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DashboardServer:
    """Web dashboard for monitoring autonomous development."""

    def __init__(self):
        self.redis_client = None
        self.port = int(os.getenv("DASHBOARD_PORT", "8080"))
        self.refresh_interval = int(os.getenv("DASHBOARD_AUTO_REFRESH", "30"))

    async def connect(self):
        """Connect to Redis."""
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis_client = await redis.from_url(redis_url, decode_responses=True)
        logger.info("📊 Dashboard connected to Redis")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics from Redis."""
        try:
            total = int(os.getenv("TOOLS_TO_DEVELOP", "61"))
            completed = int(await self.redis_client.get("metrics:completed") or 0)
            tests_passed = int(await self.redis_client.get("metrics:tests_passed") or 0)
            tests_failed = int(await self.redis_client.get("metrics:tests_failed") or 0)
            documented = int(await self.redis_client.get("metrics:documented") or 0)

            return {
                "total_tools": total,
                "completed": completed,
                "in_progress": await self.count_tools_by_status("in_progress"),
                "needs_review": await self.count_tools_by_status("needs_review"),
                "tested": await self.count_tools_by_status("tested"),
                "failed": await self.count_tools_by_status("failed"),
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "documented": documented,
                "progress_percent": int((completed / total) * 100) if total > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}

    async def count_tools_by_status(self, status: str) -> int:
        """Count tools with given status."""
        try:
            count = 0
            cursor = 0

            while True:
                cursor, keys = await self.redis_client.scan(cursor, match="tool:*", count=100)

                for key in keys:
                    tool_status = await self.redis_client.hget(key, "status")
                    if tool_status == status:
                        count += 1

                if cursor == 0:
                    break

            return count
        except Exception as e:
            logger.error(f"Error counting tools: {e}")
            return 0

    async def get_recent_tools(self, status: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent tools with given status."""
        try:
            tools = []
            cursor = 0

            while True:
                cursor, keys = await self.redis_client.scan(cursor, match="tool:*", count=100)

                for key in keys:
                    tool_data = await self.redis_client.hgetall(key)
                    if tool_data.get("status") == status:
                        tool_name = key.replace("tool:", "")
                        tools.append(
                            {
                                "name": tool_name,
                                "category": tool_data.get("category", "unknown"),
                                "status": tool_data.get("status"),
                                "updated_at": tool_data.get("completed_at")
                                or tool_data.get("started_at"),
                            }
                        )

                if cursor == 0:
                    break

            # Sort by most recent
            tools.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            return tools[:limit]

        except Exception as e:
            logger.error(f"Error getting recent tools: {e}")
            return []

    async def handle_index(self, request):
        """Serve main dashboard page."""
        metrics = await self.get_metrics()
        recent_completed = await self.get_recent_tools("completed", 5)
        recent_in_progress = await self.get_recent_tools("in_progress", 5)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AgentSwarm Tools - Development Dashboard</title>
    <meta http-equiv="refresh" content="{self.refresh_interval}">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0d1117;
            color: #c9d1d9;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #58a6ff;
            border-bottom: 1px solid #21262d;
            padding-bottom: 10px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric-card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 20px;
        }}
        .metric-value {{
            font-size: 48px;
            font-weight: bold;
            color: #58a6ff;
        }}
        .metric-label {{
            font-size: 14px;
            color: #8b949e;
            margin-top: 5px;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #238636 0%, #2ea043 100%);
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .section {{
            margin: 40px 0;
        }}
        .section h2 {{
            color: #f0f6fc;
            font-size: 20px;
            margin-bottom: 15px;
        }}
        .tool-list {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 15px;
        }}
        .tool-item {{
            padding: 10px;
            border-bottom: 1px solid #21262d;
        }}
        .tool-item:last-child {{
            border-bottom: none;
        }}
        .tool-name {{
            font-weight: bold;
            color: #58a6ff;
        }}
        .tool-meta {{
            font-size: 12px;
            color: #8b949e;
            margin-top: 5px;
        }}
        .status {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status-completed {{
            background: #238636;
            color: white;
        }}
        .status-in-progress {{
            background: #1f6feb;
            color: white;
        }}
        .status-failed {{
            background: #da3633;
            color: white;
        }}
        .timestamp {{
            text-align: center;
            color: #8b949e;
            font-size: 12px;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AgentSwarm Tools - Development Dashboard</h1>

        <div class="progress-bar">
            <div class="progress-fill" style="width: {metrics.get('progress_percent', 0)}%">
                {metrics.get('progress_percent', 0)}% Complete
            </div>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{metrics.get('completed', 0)}</div>
                <div class="metric-label">Completed Tools</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('in_progress', 0)}</div>
                <div class="metric-label">In Progress</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('tests_passed', 0)}</div>
                <div class="metric-label">Tests Passed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('documented', 0)}</div>
                <div class="metric-label">Documented</div>
            </div>
        </div>

        <div class="section">
            <h2>✅ Recently Completed</h2>
            <div class="tool-list">
                {''.join([f'''
                <div class="tool-item">
                    <div class="tool-name">{tool['name']}</div>
                    <div class="tool-meta">
                        <span class="status status-completed">COMPLETED</span>
                        {tool['category']} • {tool.get('updated_at', 'N/A')}
                    </div>
                </div>
                ''' for tool in recent_completed]) if recent_completed else '<div class="tool-item">No completed tools yet</div>'}
            </div>
        </div>

        <div class="section">
            <h2>🔨 Currently In Progress</h2>
            <div class="tool-list">
                {''.join([f'''
                <div class="tool-item">
                    <div class="tool-name">{tool['name']}</div>
                    <div class="tool-meta">
                        <span class="status status-in-progress">IN PROGRESS</span>
                        {tool['category']} • {tool.get('updated_at', 'N/A')}
                    </div>
                </div>
                ''' for tool in recent_in_progress]) if recent_in_progress else '<div class="tool-item">No tools in progress</div>'}
            </div>
        </div>

        <div class="timestamp">
            Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • Auto-refresh every {self.refresh_interval}s
        </div>
    </div>
</body>
</html>
        """

        return web.Response(text=html, content_type="text/html")

    async def handle_api_metrics(self, request):
        """API endpoint for metrics."""
        metrics = await self.get_metrics()
        return web.json_response(metrics)

    async def handle_health(self, request):
        """Health check endpoint."""
        return web.json_response({"status": "healthy", "timestamp": datetime.now().isoformat()})

    async def start_server(self):
        """Start the web server."""
        await self.connect()

        app = web.Application()
        app.router.add_get("/", self.handle_index)
        app.router.add_get("/api/metrics", self.handle_api_metrics)
        app.router.add_get("/health", self.handle_health)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()

        logger.info(f"🚀 Dashboard server started on http://0.0.0.0:{self.port}")
        logger.info(f"   Auto-refresh: {self.refresh_interval}s")

        # Keep running
        while True:
            await asyncio.sleep(3600)

    async def cleanup(self):
        """Cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()


async def main():
    """Main entry point."""
    dashboard = DashboardServer()

    try:
        await dashboard.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Dashboard server shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await dashboard.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
